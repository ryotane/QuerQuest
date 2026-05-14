"""
Archive Ratio Monitor

Active Memory と Archive Memory の比率を監視する。

使用例:
    monitor = ArchiveRatioMonitor()
    monitor.update(active_size=5000, archive_size=15000)
    status = monitor.get_status()
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class ArchiveRatioStatus:
    """Archive Ratio ステータス"""
    active_size: int
    archive_size: int
    total_size: int
    archive_ratio: float  # archive 比率 (%)
    ratio_status: str  # balanced, archive_heavy, active_heavy
    timestamp: float


class ArchiveRatioMonitor:
    """Archive Ratio モニタリング"""

    def __init__(
        self,
        thresholds: Optional[dict] = None,
    ):
        """
        Args:
            thresholds: 比率閾値 (%)
                - archive_heavy: archive 比率 > この値
                - active_heavy: archive 比率 < この値
        """
        self.thresholds = thresholds or {
            "archive_heavy": 70.0,
            "active_heavy": 30.0,
        }
        self._history: list[ArchiveRatioStatus] = []

    def update(self, active_size: int, archive_size: int) -> ArchiveRatioStatus:
        """
        Archive Ratio を更新。

        Args:
            active_size: Active Memory サイズ
            archive_size: Archive Memory サイズ

        Returns:
            ArchiveRatioStatus
        """
        total = max(active_size + archive_size, 1)
        ratio = (archive_size / total) * 100

        if ratio > self.thresholds["archive_heavy"]:
            status = "archive_heavy"
        elif ratio < self.thresholds["active_heavy"]:
            status = "active_heavy"
        else:
            status = "balanced"

        archive_status = ArchiveRatioStatus(
            active_size=active_size,
            archive_size=archive_size,
            total_size=total,
            archive_ratio=round(ratio, 2),
            ratio_status=status,
            timestamp=time.time(),
        )

        self._history.append(archive_status)

        # 履歴制限 (直近 20 件)
        if len(self._history) > 20:
            self._history = self._history[-20:]

        return archive_status

    def get_status(self) -> ArchiveRatioStatus:
        """最新の Archive Ratio ステータスを取得"""
        if not self._history:
            return ArchiveRatioStatus(
                active_size=0,
                archive_size=0,
                total_size=0,
                archive_ratio=0.0,
                ratio_status="unknown",
                timestamp=time.time(),
            )
        return self._history[-1]

    def get_trend(self) -> str:
        """Archive Ratio のトレンドを判定"""
        if len(self._history) < 2:
            return "unknown"

        recent = self._history[-3:]  # 直近 3 件
        ratios = [r.archive_ratio for r in recent]

        if ratios[-1] > ratios[0] + 5:
            return "increasing"
        elif ratios[-1] < ratios[0] - 5:
            return "decreasing"
        return "stable"

    def get_alerts(self) -> list:
        """比率異常アラートを取得"""
        alerts = []
        status = self.get_status()

        if status.ratio_status == "archive_heavy":
            alerts.append({
                "type": "archive_heavy",
                "ratio": status.archive_ratio,
                "message": f"Archive ratio too high: {status.archive_ratio:.1f}%",
            })
        elif status.ratio_status == "active_heavy":
            alerts.append({
                "type": "active_heavy",
                "ratio": status.archive_ratio,
                "message": f"Archive ratio too low: {status.archive_ratio:.1f}%",
            })

        return alerts
