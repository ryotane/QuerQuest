"""
Runtime Safety Layer

推論暴走防止のためのランタイム安全層。

設計原則:
- observation-first (観測→実行の強制)
- low overhead (Mac-friendly)
- minimal token usage
- no recursive reasoning
- lightweight debug

使用例:
    from ai_agent.runtime_safety import SafetyGuard
    
    guard = SafetyGuard()
    
    # 推論ステップ前にチェック
    result = guard.check(
        step_type="reasoning",
        content="このコードを修正する必要がある",
        target="ai_agent/core/engine.py",
    )
    
    if result.blocked:
        # 観測を実行してから再試行
        ...
    
    # 観測ステップ前にチェック
    result = guard.check(
        step_type="observation",
        content="file_read",
        target="ai_agent/core/engine.py",
    )
    
    if result.action == SafetyAction.FORCE_OBSERVE:
        # 観測を強制
        ...
"""

from .safety_guard import SafetyGuard, SafetyResult, SafetyAction
from .safety_guard import CollapsePreventionLayer

__all__ = [
    "SafetyGuard",
    "SafetyResult",
    "SafetyAction",
    "CollapsePreventionLayer",
]
