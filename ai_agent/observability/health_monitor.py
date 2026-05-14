"""
Observability Layer - Core Health Monitor

AI Workspace の内部状態を可視化する統合モニタリングコア。

構成:
- token_growth_tracker: context/token 成長率追跡
- loop_risk_score: recursive loop 危険度スコア
- compression_efficiency: compression 効率モニタリング
- archive_ratio: archive/active ratio 監視

出力:
- JSON status export (ファイル + stdout)
- SwiftBar telemetry integration
"""

import json
import time
import os
from dataclasses import dataclass, field, asdict
from typing import Optional
from pathlib import Path


@dataclass
class TokenGrowthData:
    """Token 成長データ"""
    current_tokens: int = 0
    previous_tokens: int = 0
    growth_rate: float = 0.0  # 成長率 (%)
    growth_trend: str = "stable"  # stable, growing, exploding
    last_updated: float = 0.0


@dataclass
class LoopRiskData:
    """Loop 危険度データ"""
    injection_count: int = 0
    recursion_depth: int = 0
    context_amplification_count: int = 0
    risk_score: float = 0.0  # 0.0 - 1.0
    risk_level: str = "low"  # low, medium, high, critical
    last_updated: float = 0.0


@dataclass
class CompressionEfficiencyData:
    """Compression 効率データ"""
    original_size: int = 0
    compressed_size: int = 0
    compression_ratio: float = 0.0  # 圧縮率 (%)
    compression_count: int = 0
    efficiency: str = "normal"  # normal, good, excellent, poor
    last_updated: float = 0.0


@dataclass
class ArchiveRatioData:
    """Archive Ratio データ"""
    active_memory_size: int = 0
    archive_memory_size: int = 0
    archive_ratio: float = 0.0  # archive 比率 (%)
    ratio_status: str = "balanced"  # balanced, archive_heavy, active_heavy
    last_updated: float = 0.0


@dataclass
class HealthStatus:
    """全体ヘルスステータス"""
    timestamp: float = 0.0
    status: str = "healthy"  # healthy, degraded, critical
    token_growth: TokenGrowthData = field(default_factory=TokenGrowthData)
    loop_risk: LoopRiskData = field(default_factory=LoopRiskData)
    compression: CompressionEfficiencyData = field(default_factory=CompressionEfficiencyData)
    archive_ratio: ArchiveRatioData = field(default_factory=ArchiveRatioData)
    memory_stabilization: dict = field(default_factory=dict)
    system_info: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


class HealthMonitor:
    """
    AI Workspace のヘルスモニタリング統合クラス。

    使用例:
        monitor = HealthMonitor()
        monitor.update_token_growth(current=1000, previous=800)
        monitor.update_loop_risk(injection_count=5, recursion_depth=3)
        status = monitor.get_status()
        monitor.export_json("/path/to/status.json")
    """

    def __init__(self, workspace_root: Optional[str] = None):
        self.workspace_root = workspace_root or os.getcwd()
        self._status = HealthStatus(timestamp=time.time())
        self._status.system_info = self._get_system_info()

    def _get_system_info(self) -> dict:
        """システム情報を取得"""
        import platform
        return {
            "platform": platform.system(),
            "platform_release": platform.release(),
            "platform_machine": platform.machine(),
            "python_version": platform.python_version(),
            "hostname": platform.node(),
        }

    # --- Token Growth ---

    def update_token_growth(self, current_tokens: int, previous_tokens: int) -> TokenGrowthData:
        """Token 成長データを更新"""
        growth_rate = ((current_tokens - previous_tokens) / max(previous_tokens, 1)) * 100

        if growth_rate > 50:
            trend = "exploding"
        elif growth_rate > 10:
            trend = "growing"
        else:
            trend = "stable"

        self._status.token_growth = TokenGrowthData(
            current_tokens=current_tokens,
            previous_tokens=previous_tokens,
            growth_rate=round(growth_rate, 2),
            growth_trend=trend,
            last_updated=time.time(),
        )
        return self._status.token_growth

    # --- Loop Risk ---

    def update_loop_risk(
        self,
        injection_count: int = 0,
        recursion_depth: int = 0,
        context_amplification_count: int = 0,
    ) -> LoopRiskData:
        """Loop 危険度スコアを更新"""
        # スコア計算 (0.0 - 1.0)
        score = 0.0
        score += min(injection_count * 0.1, 0.4)  # 最大 0.4
        score += min(recursion_depth * 0.15, 0.3)  # 最大 0.3
        score += min(context_amplification_count * 0.1, 0.3)  # 最大 0.3
        score = min(score, 1.0)

        if score >= 0.8:
            level = "critical"
        elif score >= 0.5:
            level = "high"
        elif score >= 0.2:
            level = "medium"
        else:
            level = "low"

        self._status.loop_risk = LoopRiskData(
            injection_count=injection_count,
            recursion_depth=recursion_depth,
            context_amplification_count=context_amplification_count,
            risk_score=round(score, 2),
            risk_level=level,
            last_updated=time.time(),
        )
        return self._status.loop_risk

    # --- Compression Efficiency ---

    def update_compression_efficiency(
        self,
        original_size: int,
        compressed_size: int,
        compression_count: int = 0,
    ) -> CompressionEfficiencyData:
        """Compression 効率データを更新"""
        ratio = (compressed_size / max(original_size, 1)) * 100

        if ratio < 30:
            efficiency = "excellent"
        elif ratio < 50:
            efficiency = "good"
        elif ratio < 80:
            efficiency = "normal"
        else:
            efficiency = "poor"

        self._status.compression = CompressionEfficiencyData(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=round(ratio, 2),
            compression_count=compression_count,
            efficiency=efficiency,
            last_updated=time.time(),
        )
        return self._status.compression

    # --- Archive Ratio ---

    def update_archive_ratio(
        self,
        active_size: int,
        archive_size: int,
    ) -> ArchiveRatioData:
        """Archive Ratio データを更新"""
        total = max(active_size + archive_size, 1)
        ratio = (archive_size / total) * 100

        if 30 <= ratio <= 70:
            status = "balanced"
        elif ratio > 70:
            status = "archive_heavy"
        else:
            status = "active_heavy"

        self._status.archive_ratio = ArchiveRatioData(
            active_memory_size=active_size,
            archive_memory_size=archive_size,
            archive_ratio=round(ratio, 2),
            ratio_status=status,
            last_updated=time.time(),
        )
        return self._status.archive_ratio

    # --- Memory Stabilization ---

    def update_memory_stabilization(self, data: dict) -> None:
        """Memory Stabilization 結果を更新"""
        self._status.memory_stabilization = {
            **data,
            "updated_at": time.time(),
        }

    # --- Overall Status ---

    def get_status(self) -> HealthStatus:
        """現在のヘルスステータスを取得"""
        self._status.timestamp = time.time()

        # 全体ステータス判定
        if self._status.loop_risk.risk_level in ("critical", "high"):
            self._status.status = "critical"
        elif self._status.token_growth.growth_trend == "exploding":
            self._status.status = "degraded"
        else:
            self._status.status = "healthy"

        return self._status

    # --- Export ---

    def export_json(self, filepath: Optional[str] = None) -> str:
        """JSON 形式でエクスポート"""
        status = self.get_status()
        json_str = status.to_json()

        if filepath:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(json_str)

        return json_str

    def export_swiftbar(self) -> str:
        """SwiftBar 用テキスト形式で出力"""
        status = self.get_status()
        lines = []

        # ヘッダー
        status_icon = {
            "healthy": "✅",
            "degraded": "⚠️",
            "critical": "🚨",
        }.get(status.status, "❓")

        lines.append(f"{status_icon} QueryQuest Health")
        lines.append("---")

        # Token 成長
        tg = status.token_growth
        lines.append(f"Tokens: {tg.current_tokens:,} ({tg.growth_rate:+.1f}%)")

        # Loop Risk
        lr = status.loop_risk
        risk_icon = {
            "low": "🟢",
            "medium": "🟡",
            "high": "🟠",
            "critical": "🔴",
        }.get(lr.risk_level, "⚪")
        lines.append(f"Loop Risk: {risk_icon} {lr.risk_score:.2f}")

        # Compression
        ce = status.compression
        lines.append(f"Compression: {ce.efficiency} ({ce.compression_ratio:.1f}%)")

        # Archive Ratio
        ar = status.archive_ratio
        lines.append(f"Archive: {ar.archive_ratio:.1f}% ({ar.ratio_status})")

        return "\n".join(lines)


# --- Convenience Functions ---

def create_health_monitor(workspace_root: Optional[str] = None) -> HealthMonitor:
    """HealthMonitor のファクトリ関数"""
    return HealthMonitor(workspace_root=workspace_root)


def quick_health_check(workspace_root: Optional[str] = None) -> str:
    """クイックヘルスチェック (SwiftBar 用)"""
    monitor = create_health_monitor(workspace_root)
    return monitor.export_swiftbar()
