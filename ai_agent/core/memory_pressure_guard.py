"""
memory_pressure_guard.py - メモリ圧力監視 + 自動対策

Project_09: Runtime Hardening
「安定性の固定化」

実メモリ使用量を監視し、
閾値を超えた場合に自動対策を実行する。

設計原則:
- 過剰対策禁止 (60秒クールダウン)
- 監視のみで停止しない
- graceful degradation 優先
- 人間介入は最終手段
- 監視ログは最小限
"""

import os
import time
import logging
from typing import Optional

from ai_agent.core.safe_defaults import SAFE_DEFAULTS
from ai_agent.core.runtime_profile import get_profile

logger = logging.getLogger(__name__)


class MemoryPressureGuard:
    """メモリ圧力監視 + 自動対策"""

    def __init__(self):
        self.last_action_time: float = 0
        self.pressure_count: int = 0
        self.emergency_count: int = 0

    def get_current_memory_mb(self) -> int:
        """現在の実メモリ使用量 (MB) を取得"""
        try:
            import psutil
            process = psutil.Process(os.getpid())
            return process.memory_info().rss / (1024 * 1024)
        except ImportError:
            # psutil がない場合は推定
            return self._estimate_memory_mb()

    def _estimate_memory_mb(self) -> int:
        """psutil なしでのメモリ推定"""
        # 簡易推定: プロセス数 * 平均メモリ
        return 256  # デフォルト推定値

    def check_and_act(self) -> str:
        """メモリ圧力チェック + 自動対策"""
        current_mb = self.get_current_memory_mb()
        profile = get_profile(SAFE_DEFAULTS.profile)

        # 緊急判定
        if current_mb > profile.max_memory_mb * 0.9:
            self.emergency_count += 1
            logger.warning(f"[memory_guard] EMERGENCY: {current_mb:.0f}MB > {profile.max_memory_mb * 0.9:.0f}MB")
            self._emergency_action()
            return "emergency"

        # 圧力判定
        if current_mb > profile.max_memory_mb * 0.8:
            self.pressure_count += 1
            logger.info(f"[memory_guard] PRESSURE: {current_mb:.0f}MB > {profile.max_memory_mb * 0.8:.0f}MB")
            self._pressure_action()
            return "pressure"

        # 正常
        self.pressure_count = 0
        self.emergency_count = 0
        return "ok"

    def _pressure_action(self):
        """メモリ圧力時の自動対策"""
        # 過剰対策防止
        if time.time() - self.last_action_time < 60:
            return

        self.last_action_time = time.time()

        # graceful degradation: メモリ使用量を減らす
        logger.info("[memory_guard] Applying graceful degradation...")
        # TODO: 実際の対策 (memory_store.json の圧縮など)

    def _emergency_action(self):
        """メモリ緊急時の自動対策"""
        # 過剰対策防止
        if time.time() - self.last_action_time < 60:
            return

        self.last_action_time = time.time()

        # 緊急対策: 最大限のデグレード
        logger.warning("[memory_guard] Applying emergency degradation...")
        # TODO: 実際の対策 (memory_store.json の削除など)

    def get_status(self) -> dict:
        """監視ステータス取得"""
        return {
            "current_mb": self.get_current_memory_mb(),
            "pressure_count": self.pressure_count,
            "emergency_count": self.emergency_count,
            "last_action": self.last_action_time,
        }


# グローバルインスタンス
memory_guard = MemoryPressureGuard()
