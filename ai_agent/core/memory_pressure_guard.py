"""
Memory Pressure Guard - Swap Prevention + OOM Protection

Project_09: Runtime Hardening
- swap detection + proactive compression
- memory cap enforcement
- graceful degradation trigger
"""

import os
import time
import psutil
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from enum import Enum


class MemoryAction(Enum):
    """Memory pressure action"""
    NONE = "none"
    COMPRESS_ARCHIVE = "compress_archive"
    DISABLE_VECTOR = "disable_vector"
    TRUNCATE_CONTEXT = "truncate_context"
    FORCE_SHUTDOWN = "force_shutdown"


@dataclass
class MemoryStatus:
    """Memory status snapshot"""
    timestamp: float = 0.0
    rss_mb: float = 0.0
    vms_mb: float = 0.0
    swap_used_mb: float = 0.0
    swap_total_mb: float = 0.0
    swap_percent: float = 0.0
    memory_percent: float = 0.0
    pressure_level: str = "normal"  # normal, warning, critical
    action_taken: MemoryAction = MemoryAction.NONE
    last_check: float = 0.0


class MemoryPressureGuard:
    """Memory pressure guard - swap prevention + OOM protection"""

    def __init__(
        self,
        swap_threshold_mb: float = 100.0,
        memory_percent_threshold: float = 85.0,
        rss_limit_mb: float = 2048.0,  # 2GB per process
        check_interval_seconds: float = 30.0,
        on_pressure: Optional[Callable[[MemoryStatus], None]] = None,
    ):
        self.swap_threshold_mb = swap_threshold_mb
        self.memory_percent_threshold = memory_percent_threshold
        self.rss_limit_mb = rss_limit_mb
        self.check_interval_seconds = check_interval_seconds
        self.on_pressure = on_pressure
        
        self.last_check_time: float = 0
        self.last_action: MemoryAction = MemoryAction.NONE
        self.action_cooldown: float = 60.0  # 1分間隔でアクション
        
        self._status = MemoryStatus(timestamp=time.time())

    def check(self) -> MemoryStatus:
        """Memory pressureをチェックし、必要に応じてアクションを実行"""
        # チェック間隔確認
        if time.time() - self.last_check_time < self.check_interval_seconds:
            return self._status
        
        self.last_check_time = time.time()
        
        # Memory stats取得
        process = psutil.Process(os.getpid())
        mem_info = process.memory_info()
        
        self._status.timestamp = time.time()
        self._status.rss_mb = mem_info.rss / (1024 * 1024)
        self._status.vms_mb = mem_info.vms / (1024 * 1024)
        
        # Swap stats
        swap = psutil.swap_memory()
        self._status.swap_used_mb = swap.used / (1024 * 1024)
        self._status.swap_total_mb = swap.total / (1024 * 1024)
        self._status.swap_percent = swap.percent
        
        # System memory
        self._status.memory_percent = psutil.virtual_memory().percent
        
        # Pressure level判定
        self._status.pressure_level = self._assess_pressure()
        
        # アクション実行
        action = self._take_action()
        self._status.action_taken = action
        
        # Pressure callback
        if self.on_pressure and action != MemoryAction.NONE:
            self.on_pressure(self._status)
        
        return self._status

    def _assess_pressure(self) -> str:
        """Memory pressure levelを判定"""
        # Swap使用量が閾値を超えたらcritical
        if self._status.swap_used_mb > self.swap_threshold_mb:
            return "critical"
        
        # RSSが制限を超えたらcritical
        if self._status.rss_mb > self.rss_limit_mb:
            return "critical"
        
        # システムメモリ使用率が閾値を超えたらwarning
        if self._status.memory_percent > self.memory_percent_threshold:
            return "warning"
        
        return "normal"

    def _take_action(self) -> MemoryAction:
        """Pressureに応じたアクションを実行"""
        # アクションクールダウン
        if time.time() - self.last_check_time < self.action_cooldown:
            return self.last_action
        
        action = MemoryAction.NONE
        
        if self._status.pressure_level == "critical":
            if self._status.swap_used_mb > self.swap_threshold_mb:
                action = MemoryAction.FORCE_SHUTDOWN
            elif self._status.rss_mb > self.rss_limit_mb:
                action = MemoryAction.TRUNCATE_CONTEXT
        elif self._status.pressure_level == "warning":
            action = MemoryAction.COMPRESS_ARCHIVE
        
        if action != MemoryAction.NONE:
            self.last_action = action
        
        return action

    def get_status(self) -> MemoryStatus:
        """Current memory status"""
        return self._status

    def is_safe(self) -> bool:
        """Memory pressureが安全か"""
        return self._status.pressure_level == "normal"

    def should_compress(self) -> bool:
        """Compressionが必要か"""
        return self._status.pressure_level in ("warning", "critical")

    def should_disable_vector(self) -> bool:
        """Vector search無効化が必要か"""
        return self._status.pressure_level == "critical"


# Singleton
_guard_instance: Optional[MemoryPressureGuard] = None


def get_memory_guard(
    swap_threshold_mb: float = 100.0,
    memory_percent_threshold: float = 85.0,
    rss_limit_mb: float = 2048.0,
) -> MemoryPressureGuard:
    """Get memory pressure guard (singleton)"""
    global _guard_instance
    if _guard_instance is None:
        _guard_instance = MemoryPressureGuard(
            swap_threshold_mb=swap_threshold_mb,
            memory_percent_threshold=memory_percent_threshold,
            rss_limit_mb=rss_limit_mb,
        )
    return _guard_instance


def reset_memory_guard():
    """Reset singleton (testing)"""
    global _guard_instance
    _guard_instance = None
