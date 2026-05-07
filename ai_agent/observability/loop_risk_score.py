"""
Loop Risk Score Calculator

recursive context amplification の危険度をスコアリングする。

使用例:
    calculator = LoopRiskCalculator()
    score = calculator.calculate(
        injection_count=5,
        recursion_depth=3,
        context_amplification_count=2,
    )
    if score.is_critical:
        # 対策実行
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class LoopRiskScore:
    """Loop 危険度スコア"""
    score: float  # 0.0 - 1.0
    level: str  # low, medium, high, critical
    injection_count: int = 0
    recursion_depth: int = 0
    context_amplification_count: int = 0
    details: list = None  # 詳細情報

    def __post_init__(self):
        if self.details is None:
            self.details = []

    @property
    def is_critical(self) -> bool:
        return self.level in ("critical", "high")

    @property
    def is_warning(self) -> bool:
        return self.level in ("high", "medium")

    def to_dict(self) -> dict:
        return {
            "score": self.score,
            "level": self.level,
            "injection_count": self.injection_count,
            "recursion_depth": self.recursion_depth,
            "context_amplification_count": self.context_amplification_count,
            "details": self.details,
        }


class LoopRiskCalculator:
    """Loop 危険度スコア計算器"""

    def __init__(
        self,
        thresholds: Optional[dict] = None,
    ):
        """
        Args:
            thresholds: スコア閾値
                - high: 高危険度閾値
                - critical: 致命閾値
        """
        self.thresholds = thresholds or {
            "high": 0.5,
            "critical": 0.8,
        }

    def calculate(
        self,
        injection_count: int = 0,
        recursion_depth: int = 0,
        context_amplification_count: int = 0,
        duplicate_context_count: int = 0,
    ) -> LoopRiskScore:
        """
        Loop 危険度スコアを計算。

        Args:
            injection_count: context injection 回数
            recursion_depth: 再帰深さ
            context_amplification_count: context amplification 回数
            duplicate_context_count: 重複 context 数

        Returns:
            LoopRiskScore
        """
        score = 0.0
        details = []

        # 1. Injection Count (最大 0.3)
        injection_score = min(injection_count * 0.06, 0.3)
        score += injection_score
        if injection_count > 0:
            details.append(f"injection_count={injection_count} (+{injection_score:.2f})")

        # 2. Recursion Depth (最大 0.3)
        recursion_score = min(recursion_depth * 0.15, 0.3)
        score += recursion_score
        if recursion_depth > 0:
            details.append(f"recursion_depth={recursion_depth} (+{recursion_score:.2f})")

        # 3. Context Amplification (最大 0.2)
        amplification_score = min(context_amplification_count * 0.1, 0.2)
        score += amplification_score
        if context_amplification_count > 0:
            details.append(f"amplification_count={context_amplification_count} (+{amplification_score:.2f})")

        # 4. Duplicate Context (最大 0.2)
        duplicate_score = min(duplicate_context_count * 0.05, 0.2)
        score += duplicate_score
        if duplicate_context_count > 0:
            details.append(f"duplicate_count={duplicate_context_count} (+{duplicate_score:.2f})")

        # スコア正規化 (0.0 - 1.0)
        score = min(score, 1.0)

        # レベル判定
        if score >= self.thresholds["critical"]:
            level = "critical"
        elif score >= self.thresholds["high"]:
            level = "high"
        elif score >= 0.2:
            level = "medium"
        else:
            level = "low"

        return LoopRiskScore(
            score=round(score, 2),
            level=level,
            injection_count=injection_count,
            recursion_depth=recursion_depth,
            context_amplification_count=context_amplification_count,
            details=details,
        )

    def check_and_alert(
        self,
        injection_count: int = 0,
        recursion_depth: int = 0,
        context_amplification_count: int = 0,
    ) -> Optional[str]:
        """
        危険度チェック + アラート出力。

        Returns:
            アラートメッセージ (危険な場合) または None
        """
        score = self.calculate(
            injection_count=injection_count,
            recursion_depth=recursion_depth,
            context_amplification_count=context_amplification_count,
        )

        if score.is_critical:
            return (
                f"🚨 CRITICAL LOOP RISK: score={score.score:.2f}\n"
                f"   Details: {', '.join(score.details)}\n"
                f"   Action: Immediate context deduplication required!"
            )
        elif score.is_warning:
            return (
                f"⚠️ WARNING LOOP RISK: score={score.score:.2f}\n"
                f"   Details: {', '.join(score.details)}"
            )
        return None
