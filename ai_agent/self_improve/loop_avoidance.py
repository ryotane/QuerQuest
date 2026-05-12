"""
LoopAvoidancePromptInjector - ループ回避プロンプト注入モジュール

目的:
- 分析結果に基づき、システムプロンプトにループ回避指示を追加
- 既存のプロンプトを破壊せず、追記形式で適用

設計原則:
- 既存プロンプトを尊重
- 必要最小限の指示のみ追加
- 注入はオプション（無効化可能）
"""

from typing import List, Optional
from ai_agent.self_improve.loop_analyzer import LoopPatternAnalyzer


class LoopAvoidancePromptInjector:
    """ループ回避プロンプト注入クラス"""

    def __init__(
        self,
        analyzer: Optional[LoopPatternAnalyzer] = None,
        enabled: bool = True,
    ):
        """
        Args:
            analyzer: ループパターン分析クラス（任意）
            enabled: 注入の有効化フラグ
        """
        self.analyzer = analyzer or LoopPatternAnalyzer()
        self.enabled = enabled
        self.injection_prefix = "【ループ回避指示】"

    def inject(self, system_prompt: str) -> str:
        """
        システムプロンプトにループ回避指示を注入

        Args:
            system_prompt: 元のシステムプロンプト

        Returns:
            ループ回避指示が追加されたシステムプロンプト
        """
        if not self.enabled:
            return system_prompt

        # 分析結果に基づく指示を取得
        instructions = self.analyzer.get_loop_avoidance_instructions()

        if not instructions:
            return system_prompt

        # 指示を結合
        instruction_text = "\n".join(instructions)
        injection = f"\n\n{self.injection_prefix}\n{instruction_text}\n"

        # 既存プロンプトの末尾に追加
        return system_prompt + injection

    def disable(self):
        """注入を無効化"""
        self.enabled = False

    def enable(self):
        """注入を有効化"""
        self.enabled = True
