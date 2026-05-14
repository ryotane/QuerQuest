"""
Automatic Continuation Orchestrator

新規チャット移行時の継続状態復元オーケストレーター。

構成:
- orchestrator.py: メインオーケストレーター
  - 継続意図検出
  - ターゲット検索
  - コンテキスト復元
  - 復元プロンプト生成
  - 曖昧さ解決
  - 起動時継続ローダー
"""

from .orchestrator import (
    ContinuationOrchestrator,
    ContinuationTarget,
    ContinuationContext,
    ContinuationResult,
    HydrationMode,
    create_continuation_orchestrator,
)

__all__ = [
    "ContinuationOrchestrator",
    "ContinuationTarget",
    "ContinuationContext",
    "ContinuationResult",
    "HydrationMode",
    "create_continuation_orchestrator",
]
