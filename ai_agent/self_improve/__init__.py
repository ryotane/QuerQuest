"""
Self-Improvement Module - Project_039

自律的学習のためのモジュール群
- loop_logger: ループ失敗ログ記録
- loop_analyzer: ループパターン分析
- loop_avoidance: ループ回避プロンプト注入
"""

from ai_agent.self_improve.loop_logger import LoopFailureLogger
from ai_agent.self_improve.loop_analyzer import LoopPatternAnalyzer
from ai_agent.self_improve.loop_avoidance import LoopAvoidancePromptInjector

__all__ = [
    "LoopFailureLogger",
    "LoopPatternAnalyzer",
    "LoopAvoidancePromptInjector",
]
