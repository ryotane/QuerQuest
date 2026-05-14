"""
memory_entry.py - メモリエントリ定義

Project_035: P1 - Memory OS
"""

import time
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional
from enum import Enum


class MemoryLayer(Enum):
    """メモリ層"""
    WORKING = "working"           # 作業メモリ
    SHORT_TERM = "short_term"     # 短期メモリ
    LONG_TERM = "long_term"       # 長期メモリ
    SEMANTIC = "semantic"         # 意味メモリ


@dataclass
class MemoryEntry:
    """
    メモリエントリ
    
    Attributes:
        id: エントリ固有ID
        content: コンテンツ
        metadata: メタデータ
        importance: 重要度 (0.0 - 1.0)
        created_at: 作成時刻
        accessed_at: 最終アクセス時刻
        access_count: アクセス回数
        layer: 層
        tags: タグ
        embedding: 埋め込みベクトル
    """
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    importance: float = 0.5
    created_at: float = field(default_factory=time.time)
    accessed_at: float = field(default_factory=time.time)
    access_count: int = 0
    layer: MemoryLayer = MemoryLayer.WORKING
    tags: List[str] = field(default_factory=list)
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict:
        """辞書へ変換"""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "importance": self.importance,
            "created_at": self.created_at,
            "accessed_at": self.accessed_at,
            "access_count": self.access_count,
            "layer": self.layer.value,
            "tags": self.tags,
            "embedding": self.embedding,
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        """辞書からエントリを作成"""
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            importance=data.get("importance", 0.5),
            created_at=data.get("created_at", time.time()),
            accessed_at=data.get("accessed_at", time.time()),
            access_count=data.get("access_count", 0),
            layer=MemoryLayer(data.get("layer", "working")),
            tags=data.get("tags", []),
            embedding=data.get("embedding"),
        )
    
    def touch(self):
        """最終アクセス時刻を更新"""
        self.accessed_at = time.time()
        self.access_count += 1
    
    def is_expired(self, lifetime: float) -> bool:
        """期限切れかどうか"""
        return (time.time() - self.created_at) > lifetime
    
    def similarity(self, other: "MemoryEntry") -> float:
        """他エントリとの類似度（簡易版）"""
        if not self.tags or not other.tags:
            return 0.0
        
        # タグの重複率
        intersection = set(self.tags) & set(other.tags)
        union = set(self.tags) | set(other.tags)
        
        return len(intersection) / len(union) if union else 0.0
