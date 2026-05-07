# ai_agent/workspace/memory_stabilization/__init__.py

"""
Memory Stabilization Module

recursive context amplification を防止する機能を提供。

機能:
- injected context exclusion: 注入済みcontextの再保存防止
- recursive injection detection: 循環参照検出
- context deduplication: 重複content排除
- token budget hard limit: 厳格な文字数制限
- summary compression: 要約圧縮
- active/archive memory separation: 状態分離
"""

from .stabilizer import MemoryStabilizer
from .injection_guard import InjectionGuard
from .context_deduplicator import ContextDeduplicator
from .summary_compressor import SummaryCompressor
from .memory_separation import MemorySeparation

__all__ = [
    "MemoryStabilizer",
    "InjectionGuard",
    "ContextDeduplicator",
    "SummaryCompressor",
    "MemorySeparation",
]
