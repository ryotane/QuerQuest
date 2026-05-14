"""
Token Growth Tracker

context/token の成長率を追跡し、異常成長を検出する。

使用例:
    tracker = TokenGrowthTracker()
    tracker.record("active_memory", 1000)
    tracker.record("active_memory", 1500)
    status = tracker.get_status()
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Optional


@dataclass
class MemorySegment:
    """メモリセグメントの成長データ"""
    name: str
    current_size: int = 0
    previous_size: int = 0
    growth_rate: float = 0.0
    history: list = field(default_factory=list)  # [(timestamp, size), ...]
    trend: str = "stable"  # stable, growing, exploding


class TokenGrowthTracker:
    """Token/Context 成長トラッカー"""

    def __init__(self, thresholds: Optional[Dict[str, float]] = None):
        """
        Args:
            thresholds: 閾値設定
                - growing: 成長率閾値 (%)
                - exploding: 爆発成長閾値 (%)
        """
        self.thresholds = thresholds or {
            "growing": 10.0,
            "exploding": 50.0,
        }
        self._segments: Dict[str, MemorySegment] = {}

    def record(self, segment_name: str, current_size: int) -> MemorySegment:
        """
        メモリセグメントのサイズを記録。

        Args:
            segment_name: セグメント名 (例: "active_memory", "context_window")
            current_size: 現在のサイズ (bytes または tokens)

        Returns:
            更新された MemorySegment
        """
        if segment_name not in self._segments:
            self._segments[segment_name] = MemorySegment(
                name=segment_name,
                current_size=current_size,
                previous_size=current_size,
            )

        segment = self._segments[segment_name]
        segment.previous_size = segment.current_size
        segment.current_size = current_size

        # 成長率計算
        if segment.previous_size > 0:
            growth_rate = ((current_size - segment.previous_size) / segment.previous_size) * 100
        else:
            growth_rate = 0.0
        segment.growth_rate = round(growth_rate, 2)

        # トレンド判定
        if growth_rate > self.thresholds.get("exploding", 50.0):
            segment.trend = "exploding"
        elif growth_rate > self.thresholds.get("growing", 10.0):
            segment.trend = "growing"
        else:
            segment.trend = "stable"

        # 履歴記録
        segment.history.append((time.time(), current_size))

        # 履歴サイズ制限 (直近 100 件)
        if len(segment.history) > 100:
            segment.history = segment.history[-100:]

        return segment

    def get_status(self) -> Dict[str, MemorySegment]:
        """全セグメントのステータスを取得"""
        return dict(self._segments)

    def get_overall_trend(self) -> str:
        """全体のトレンドを判定"""
        trends = [s.trend for s in self._segments.values()]
        if "exploding" in trends:
            return "exploding"
        if "growing" in trends:
            return "growing"
        return "stable"

    def get_alerts(self) -> list:
        """成長異常アラートを取得"""
        alerts = []
        for name, segment in self._segments.items():
            if segment.trend == "exploding":
                alerts.append({
                    "type": "token_exploding",
                    "segment": name,
                    "growth_rate": segment.growth_rate,
                    "current_size": segment.current_size,
                    "message": f"Token explosion detected in {name}: {segment.growth_rate:+.1f}%",
                })
            elif segment.trend == "growing":
                alerts.append({
                    "type": "token_growing",
                    "segment": name,
                    "growth_rate": segment.growth_rate,
                    "current_size": segment.current_size,
                    "message": f"Token growth detected in {name}: {segment.growth_rate:+.1f}%",
                })
        return alerts
