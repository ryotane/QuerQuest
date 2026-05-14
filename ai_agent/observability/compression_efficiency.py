"""
Compression Efficiency Monitor

Memory compression の効率をモニタリングする。

使用例:
    monitor = CompressionEfficiencyMonitor()
    monitor.record(original=10000, compressed=3000)
    status = monitor.get_status()
"""

import time
from dataclasses import dataclass
from typing import Optional


@dataclass
class CompressionRecord:
    """Compression 記録"""
    timestamp: float
    original_size: int
    compressed_size: int
    ratio: float  # compressed/original * 100
    efficiency: str  # excellent, good, normal, poor


class CompressionEfficiencyMonitor:
    """Compression 効率モニタリング"""

    def __init__(
        self,
        thresholds: Optional[dict] = None,
    ):
        """
        Args:
            thresholds: 効率閾値 (%)
                - excellent: 圧縮率 < この値
                - good: 圧縮率 < この値
                - normal: 圧縮率 < この値
        """
        self.thresholds = thresholds or {
            "excellent": 30.0,
            "good": 50.0,
            "normal": 80.0,
        }
        self._records: list[CompressionRecord] = []
        self._total_original = 0
        self._total_compressed = 0
        self._compression_count = 0

    def record(self, original_size: int, compressed_size: int) -> CompressionRecord:
        """
        Compression 結果を記録。

        Args:
            original_size: 圧縮前サイズ
            compressed_size: 圧縮後サイズ

        Returns:
            CompressionRecord
        """
        ratio = (compressed_size / max(original_size, 1)) * 100

        if ratio < self.thresholds["excellent"]:
            efficiency = "excellent"
        elif ratio < self.thresholds["good"]:
            efficiency = "good"
        elif ratio < self.thresholds["normal"]:
            efficiency = "normal"
        else:
            efficiency = "poor"

        record = CompressionRecord(
            timestamp=time.time(),
            original_size=original_size,
            compressed_size=compressed_size,
            ratio=round(ratio, 2),
            efficiency=efficiency,
        )

        self._records.append(record)
        self._total_original += original_size
        self._total_compressed += compressed_size
        self._compression_count += 1

        # 履歴制限 (直近 50 件)
        if len(self._records) > 50:
            self._records = self._records[-50:]

        return record

    def get_status(self) -> dict:
        """現在の効率ステータスを取得"""
        if self._total_original == 0:
            return {
                "overall_ratio": 0.0,
                "overall_efficiency": "unknown",
                "compression_count": 0,
                "latest_efficiency": "unknown",
            }

        overall_ratio = (self._total_compressed / self._total_original) * 100

        if overall_ratio < self.thresholds["excellent"]:
            overall_efficiency = "excellent"
        elif overall_ratio < self.thresholds["good"]:
            overall_efficiency = "good"
        elif overall_ratio < self.thresholds["normal"]:
            overall_efficiency = "normal"
        else:
            overall_efficiency = "poor"

        latest = self._records[-1] if self._records else None

        return {
            "overall_ratio": round(overall_ratio, 2),
            "overall_efficiency": overall_efficiency,
            "compression_count": self._compression_count,
            "total_original": self._total_original,
            "total_compressed": self._total_compressed,
            "latest_efficiency": latest.efficiency if latest else "unknown",
            "latest_ratio": latest.ratio if latest else 0.0,
        }

    def get_alerts(self) -> list:
        """効率異常アラートを取得"""
        alerts = []
        status = self.get_status()

        if status["overall_efficiency"] == "poor":
            alerts.append({
                "type": "compression_poor",
                "ratio": status["overall_ratio"],
                "message": f"Compression efficiency is poor: {status['overall_ratio']:.1f}%",
            })

        # 最新記録が poor の場合
        if self._records and self._records[-1].efficiency == "poor":
            alerts.append({
                "type": "compression_poor_latest",
                "ratio": self._records[-1].ratio,
                "message": f"Latest compression was poor: {self._records[-1].ratio:.1f}%",
            })

        return alerts
