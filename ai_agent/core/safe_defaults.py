"""
safe_defaults.py - 安全なデフォルト値定義

Project_09: Runtime Hardening
「安定性の固定化」

すべてのデフォルト値は
「過剰なリソース消費をしない」方向に固定する。
"""

from dataclasses import dataclass, field
from typing import Optional


@dataclass(frozen=True)
class SafeDefaults:
    """安全なデフォルト値の固定セット"""

    # === LLM ===
    # 最大トークン数 (lightweight)
    max_tokens: int = 1024

    # 温度 (推論安定性)
    temperature: float = 0.3

    # 最大再試行回数
    max_retries: int = 2

    # 再試行間隔 (秒)
    retry_delay: float = 1.0

    # === Memory ===
    # 最大メモリ使用量 (MB)
    max_memory_mb: int = 512

    # メモリ圧力閾値 (%)
    memory_pressure_threshold: float = 80.0

    # メモリ緊急閾値 (%)
    memory_emergency_threshold: float = 90.0

    # 最大メモリ保持件数
    max_memory_entries: int = 256

    # メモリ圧迫時の保持件数
    memory_pressure_entries: int = 128

    # === Token ===
    # 最大トークン数 (context window)
    max_context_tokens: int = 50_000

    # トークン緊急閾値
    token_emergency_threshold: int = 40_000

    # === Planning ===
    # 最大プランステップ数
    max_plan_steps: int = 3

    # 計画タイムアウト (秒)
    plan_timeout: int = 30

    # 最小間隔 (秒) - runaway防止
    min_step_interval: float = 2.0

    # === Reflection ===
    # 最大リフレクション回数
    max_reflections: int = 1

    # リフレクションタイムアウト (秒)
    reflection_timeout: int = 15

    # === Swap ===
    # スワップ使用量閾値 (MB)
    swap_threshold_mb: int = 100

    # スワップ緊急閾値 (MB)
    swap_emergency_threshold_mb: int = 500

    # === Monitoring ===
    # 監視クールダウン (秒) - 過剰対策防止
    monitor_cooldown: int = 60

    # 監視ログ間隔 (秒)
    monitor_log_interval: int = 300

    # === Graceful Degradation ===
    # 監視のみで停止しない
    # 人間介入は最終手段
    # 監視ログは最小限

    # === Config ===
    # 設定変更検知
    config_hash: Optional[str] = None
    config_changed: bool = False

    # === Runtime Profile ===
    # lightweight/balanced/full
    profile: str = "lightweight"

    def is_memory_pressure(self, current_mb: int) -> bool:
        """メモリ圧力判定"""
        return current_mb > self.max_memory_mb * (self.memory_pressure_threshold / 100.0)

    def is_memory_emergency(self, current_mb: int) -> bool:
        """メモリ緊急判定"""
        return current_mb > self.max_memory_mb * (self.memory_emergency_threshold / 100.0)

    def is_swap_emergency(self, current_swap_mb: int) -> bool:
        """スワップ緊急判定"""
        return current_swap_mb > self.swap_emergency_threshold_mb

    def is_token_pressure(self, current_tokens: int) -> bool:
        """トークン圧力判定"""
        return current_tokens > self.max_context_tokens * 0.8

    def is_token_emergency(self, current_tokens: int) -> bool:
        """トークン緊急判定"""
        return current_tokens > self.token_emergency_threshold


# グローバルインスタンス
SAFE_DEFAULTS = SafeDefaults()
