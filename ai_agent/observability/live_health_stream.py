"""
Live Health Stream

イベント駆動型リアルタイムヘルスストリーム。

目的:
- 状態変化をイベントとして通知
- low overhead なストリーミング
- cache-first アクセス
- 不要な収集を防止

設計:
- 状態変化時のみイベント発生 (polling しない)
- 前回の値と比較して差分のみ通知
- 同一状態の連続発生は抑制
"""

import time
import json
import threading
from dataclasses import dataclass, field, asdict
from typing import Optional, Callable, Dict, List, Any
from enum import Enum

from .telemetry_scheduler import TelemetryScheduler, TelemetryState


class HealthEventType(Enum):
    """ヘルスイベント種類"""
    STATE_CHANGE = "state_change"
    METRIC_UPDATE = "metric_update"
    ALERT = "alert"
    THRESHOLD_EXCEEDED = "threshold_exceeded"


@dataclass
class HealthEvent:
    """ヘルスイベント"""
    event_type: HealthEventType
    timestamp: float = 0.0
    source: str = ""
    data: Dict = field(default_factory=dict)
    severity: str = "info"  # info, warning, critical

    def to_dict(self) -> dict:
        return {
            "event_type": self.event_type.value,
            "timestamp": self.timestamp,
            "source": self.source,
            "data": self.data,
            "severity": self.severity,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), ensure_ascii=False)


@dataclass
class MetricHistory:
    """メトリクス履歴 (直近のみ保持)"""
    values: List[float] = field(default_factory=list)
    max_history: int = 10
    last_value: float = 0.0
    trend: str = "stable"  # stable, increasing, decreasing

    def add(self, value: float) -> None:
        self.values.append(value)
        if len(self.values) > self.max_history:
            self.values.pop(0)
        self.last_value = value
        self._update_trend()

    def _update_trend(self) -> None:
        if len(self.values) < 3:
            self.trend = "stable"
            return

        # 単純な傾き判定
        recent = self.values[-3:]
        diffs = [recent[i+1] - recent[i] for i in range(len(recent)-1)]
        avg_diff = sum(diffs) / len(diffs)

        if avg_diff > 0.01:
            self.trend = "increasing"
        elif avg_diff < -0.01:
            self.trend = "decreasing"
        else:
            self.trend = "stable"

    @property
    def is_significant_change(self) -> bool:
        """有意な変化かどうか"""
        if len(self.values) < 3:
            return False
        return abs(self.values[-1] - self.values[0]) > 0.05


class LiveHealthStream:
    """
    イベント駆動型リアルタイムヘルスストリーム。

    使用例:
        stream = LiveHealthStream()

        # イベントハンドラ登録
        @stream.on_event
        def handle_event(event: HealthEvent):
            print(f"Event: {event.event_type}")

        # メトリクス更新 (状態変化時のみイベント発生)
        stream.update_metric("cpu_usage", 15.0)
        stream.update_metric("loop_risk", 0.3)

        # 手動で状態遷移トリガー
        stream.trigger_state_change(TelemetryState.ACTIVE)

        # イベント取得
        events = stream.get_events()
    """

    def __init__(
        self,
        scheduler: Optional[TelemetryScheduler] = None,
        max_events: int = 100,
        debounce_seconds: float = 2.0,
    ):
        self.scheduler = scheduler or TelemetryScheduler()
        self.max_events = max_events
        self.debounce_seconds = debounce_seconds
        self._events: List[HealthEvent] = []
        self._event_handlers: List[Callable[[HealthEvent], None]] = []
        self._metric_history: Dict[str, MetricHistory] = {}
        self._last_event_time: float = 0.0
        self._lock = threading.Lock()

    @property
    def event_count(self) -> int:
        return len(self._events)

    def on_event(self, handler: Callable[[HealthEvent], None]) -> Callable:
        """イベントハンドラ登録デコレータ"""
        self._event_handlers.append(handler)
        return handler

    def register_handler(self, handler: Callable[[HealthEvent], None]) -> None:
        """イベントハンドラ登録"""
        self._event_handlers.append(handler)

    def unregister_handler(self, handler: Callable[[HealthEvent], None]) -> None:
        """イベントハンドラ解除"""
        if handler in self._event_handlers:
            self._event_handlers.remove(handler)

    def update_metric(self, name: str, value: float) -> Optional[HealthEvent]:
        """
        メトリクス値を更新。
        有意な変化時のみイベントを生成。

        Args:
            name: メトリクス名
            value: 値

        Returns:
            生成されたイベント (変化なしなら None)
        """
        # デバウンス
        now = time.time()
        if now - self._last_event_time < self.debounce_seconds:
            return None

        # 履歴管理
        if name not in self._metric_history:
            self._metric_history[name] = MetricHistory()

        history = self._metric_history[name]
        history.add(value)

        # 有意な変化のみイベント生成
        if history.is_significant_change:
            event = HealthEvent(
                event_type=HealthEventType.METRIC_UPDATE,
                timestamp=now,
                source=name,
                data={
                    "name": name,
                    "value": value,
                    "trend": history.trend,
                    "previous_values": list(history.values),
                },
                severity="warning" if history.trend == "increasing" else "info",
            )
            self._emit_event(event)
            self._last_event_time = now
            return event

        return None

    def trigger_state_change(self, new_state: TelemetryState) -> Optional[HealthEvent]:
        """
        状態遷移をトリガー。

        Args:
            new_state: 新しい状態

        Returns:
            生成されたイベント
        """
        current_state = self.scheduler.state

        if current_state == new_state:
            return None

        event = HealthEvent(
            event_type=HealthEventType.STATE_CHANGE,
            timestamp=time.time(),
            source="scheduler",
            data={
                "from": current_state.value,
                "to": new_state.value,
                "interval": self.scheduler.interval,
            },
            severity="warning" if new_state in (TelemetryState.ACTIVE, TelemetryState.ALERT) else "info",
        )
        self._emit_event(event)
        self._last_event_time = time.time()
        return event

    def trigger_alert(self, alert_data: Dict) -> HealthEvent:
        """
        アラート発生をトリガー。

        Args:
            alert_data: アラートデータ

        Returns:
            生成されたイベント
        """
        event = HealthEvent(
            event_type=HealthEventType.ALERT,
            timestamp=time.time(),
            source="health_stream",
            data=alert_data,
            severity="critical",
        )
        self._emit_event(event)
        self._last_event_time = time.time()
        return event

    def _emit_event(self, event: HealthEvent) -> None:
        """イベントを発火"""
        with self._lock:
            self._events.append(event)
            if len(self._events) > self.max_events:
                self._events.pop(0)

        # ハンドラ実行
        for handler in self._event_handlers:
            try:
                handler(event)
            except Exception:
                pass  # ハンドラ失敗はイベントを停止しない

    def get_events(self, limit: Optional[int] = None) -> List[HealthEvent]:
        """イベントを取得"""
        with self._lock:
            events = list(self._events)
        if limit:
            events = events[-limit:]
        return events

    def get_events_json(self, limit: Optional[int] = None) -> str:
        """イベントを JSON で取得"""
        events = self.get_events(limit)
        return json.dumps(
            [e.to_dict() for e in events],
            ensure_ascii=False,
            indent=2,
        )

    def get_summary(self) -> Dict:
        """ストリームの要約を取得"""
        return {
            "event_count": self.event_count,
            "current_state": self.scheduler.state.value,
            "current_interval": self.scheduler.interval,
            "tracked_metrics": list(self._metric_history.keys()),
            "last_event_at": self._last_event_time,
        }

    def get_summary_json(self) -> str:
        """要約を JSON で取得"""
        return json.dumps(self.get_summary(), ensure_ascii=False, indent=2)


# --- Convenience ---

def create_health_stream(
    scheduler: Optional[TelemetryScheduler] = None,
    max_events: int = 100,
) -> LiveHealthStream:
    """LiveHealthStream のファクトリ"""
    return LiveHealthStream(scheduler=scheduler, max_events=max_events)
