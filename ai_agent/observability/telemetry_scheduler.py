"""
Telemetry Scheduler

適応的テレメトリ頻度スケジューラ。

目的:
- 監視自体が負荷源にならない
- 状態変化に応じて収集頻度を動的調整
- idle 時は低頻度、active 時は高頻度

設計原則:
- CPU 使用率 < 5%: 60s interval (idle)
- CPU 使用率 5-20%: 30s interval (normal)
- CPU 使用率 > 20%: 10s interval (active)
- loop_risk > 0.5: 5s interval (alert)
"""

import time
import threading
from dataclasses import dataclass, field
from typing import Optional, Callable, Dict
from enum import Enum


class TelemetryState(Enum):
    """テレメトリ状態"""
    IDLE = "idle"
    NORMAL = "normal"
    ACTIVE = "active"
    ALERT = "alert"


@dataclass
class TelemetryConfig:
    """テレメトリ設定"""
    # 各状態の収集 interval (秒)
    idle_interval: float = 60.0
    normal_interval: float = 30.0
    active_interval: float = 10.0
    alert_interval: float = 5.0

    # 状態遷移閾値
    cpu_active_threshold: float = 20.0  # CPU > 20% で active
    cpu_normal_threshold: float = 5.0   # CPU > 5% で normal
    loop_risk_alert_threshold: float = 0.5  # loop_risk > 0.5 で alert

    # 状態遷移ヒステリシス (フラッター防止)
    hysteresis_margin: float = 2.0


@dataclass
class TelemetrySnapshot:
    """テレメトリスナップショット"""
    timestamp: float = 0.0
    state: TelemetryState = TelemetryState.IDLE
    interval: float = 60.0
    next_collect_at: float = 0.0
    metrics: Dict = field(default_factory=dict)
    reason: str = ""


class TelemetryScheduler:
    """
    適応的テレメトリ頻度スケジューラ。

    使用例:
        scheduler = TelemetryScheduler()
        
        # コールバック登録
        def on_collect(metrics: dict):
            print(metrics)
        
        scheduler.register_callback(on_collect)
        
        # 状態更新 (外部から呼び出し)
        scheduler.update_state(
            cpu_usage=15.0,
            loop_risk=0.3,
            memory_pressure=0.1
        )
        
        # 収集判定
        if scheduler.should_collect():
            metrics = collector.collect()
            scheduler.record_collection(metrics)
    """

    def __init__(
        self,
        config: Optional[TelemetryConfig] = None,
        initial_state: TelemetryState = TelemetryState.IDLE,
    ):
        self.config = config or TelemetryConfig()
        self._state = initial_state
        self._last_collect_time = 0.0
        self._callbacks = []
        self._lock = threading.Lock()
        self._snapshot = TelemetrySnapshot()

    @property
    def state(self) -> TelemetryState:
        return self._state

    @property
    def interval(self) -> float:
        """現在の収集 interval"""
        return {
            TelemetryState.IDLE: self.config.idle_interval,
            TelemetryState.NORMAL: self.config.normal_interval,
            TelemetryState.ACTIVE: self.config.active_interval,
            TelemetryState.ALERT: self.config.alert_interval,
        }[self._state]

    def register_callback(self, callback: Callable[[Dict], None]) -> None:
        """収集コールバックを登録"""
        self._callbacks.append(callback)

    def unregister_callback(self, callback: Callable[[Dict], None]) -> None:
        """収集コールバックを解除"""
        if callback in self._callbacks:
            self._callbacks.remove(callback)

    def update_state(
        self,
        cpu_usage: float = 0.0,
        loop_risk: float = 0.0,
        memory_pressure: float = 0.0,
    ) -> TelemetryState:
        """
        外部メトリクスから状態を計算・更新。

        Args:
            cpu_usage: CPU 使用率 (%)
            loop_risk: Loop 危険度 (0.0 - 1.0)
            memory_pressure: メモリ圧力 (0.0 - 1.0)

        Returns:
            更新された状態
        """
        new_state = self._compute_state(cpu_usage, loop_risk, memory_pressure)

        if new_state != self._state:
            reason = self._state_transition_reason(self._state, new_state)
            self._state = new_state
            self._snapshot = TelemetrySnapshot(
                timestamp=time.time(),
                state=new_state,
                interval=self.interval,
                next_collect_at=time.time() + self.interval,
                reason=reason,
            )

        return self._state

    def _compute_state(
        self,
        cpu_usage: float,
        loop_risk: float,
        memory_pressure: float,
    ) -> TelemetryState:
        """メトリクスから状態を計算"""
        # loop_risk が閾値超え → alert
        if loop_risk >= self.config.loop_risk_alert_threshold:
            return TelemetryState.ALERT

        # memory_pressure が高い → active
        if memory_pressure > 0.3:
            return TelemetryState.ACTIVE

        # CPU 使用率で判定 (ヒステリシス付き)
        if cpu_usage > self.config.cpu_active_threshold + self.config.hysteresis_margin:
            return TelemetryState.ACTIVE
        elif cpu_usage > self.config.cpu_normal_threshold:
            return TelemetryState.NORMAL
        else:
            return TelemetryState.IDLE

    def _state_transition_reason(
        self,
        old: TelemetryState,
        new: TelemetryState,
    ) -> str:
        """状態遷移理由を生成"""
        if new == TelemetryState.ALERT:
            return "Loop risk threshold exceeded"
        if old == TelemetryState.ALERT and new in (TelemetryState.NORMAL, TelemetryState.IDLE):
            return "Loop risk decreased"

        reasons = {
            (TelemetryState.IDLE, TelemetryState.NORMAL): "CPU activity detected",
            (TelemetryState.IDLE, TelemetryState.ACTIVE): "High memory pressure",
            (TelemetryState.NORMAL, TelemetryState.ACTIVE): "CPU spike detected",
            (TelemetryState.NORMAL, TelemetryState.IDLE): "Activity decreased",
            (TelemetryState.ACTIVE, TelemetryState.NORMAL): "Load normalized",
            (TelemetryState.ACTIVE, TelemetryState.IDLE): "System idle",
        }
        return reasons.get((old, new), "state update")

    def should_collect(self) -> bool:
        """
        現在収集すべきか判定。

        Returns:
            収集すべきなら True
        """
        now = time.time()
        return now >= self._last_collect_time + self.interval

    def record_collection(self, metrics: Dict) -> TelemetrySnapshot:
        """
        収集を記録。

        Args:
            metrics: 収集したメトリクス

        Returns:
            スナップショット
        """
        with self._lock:
            self._last_collect_time = time.time()
            self._snapshot = TelemetrySnapshot(
                timestamp=time.time(),
                state=self._state,
                interval=self.interval,
                next_collect_at=time.time() + self.interval,
                metrics=metrics,
            )

            # コールバック実行
            for cb in self._callbacks:
                try:
                    cb(metrics)
                except Exception:
                    pass  # コールバック失敗は監視を停止しない

        return self._snapshot

    def get_snapshot(self) -> TelemetrySnapshot:
        """現在のスナップショットを取得"""
        return TelemetrySnapshot(
            timestamp=time.time(),
            state=self._state,
            interval=self.interval,
            next_collect_at=self._last_collect_time + self.interval,
            metrics=self._snapshot.metrics,
            reason=self._snapshot.reason,
        )

    def get_status_json(self) -> str:
        """現在の状態を JSON で出力"""
        import json
        snapshot = self.get_snapshot()
        return json.dumps({
            "state": snapshot.state.value,
            "interval": snapshot.interval,
            "next_collect_at": snapshot.next_collect_at,
            "reason": snapshot.reason,
        }, ensure_ascii=False)


# --- Convenience ---

def create_scheduler(initial_state: TelemetryState = TelemetryState.IDLE) -> TelemetryScheduler:
    """TelemetryScheduler のファクトリ"""
    return TelemetryScheduler(initial_state=initial_state)
