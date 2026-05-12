"""
memory_os.py - Memory OS コア

Project_035: P1 - Memory OS
階層型メモリ管理 + 自動スケジューリング

設計原則:
- human_memory_simulation (人間の記憶を模倣)
- automatic_management (自動管理)
- lightweight (軽量)
"""

import time
import uuid
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field

from .memory_entry import MemoryEntry, MemoryLayer
from .project_history import ProjectHistoryStore


class MemoryOS:
    """
    Memory OS - メモリオペレーティングシステム
    
    階層型メモリ管理 + 自動スケジューリング
    
    使用例:
        memory_os = MemoryOS()
        
        # メモリ保存
        entry = MemoryEntry(
            id="mem_001",
            content="ユーザーはPythonを好む",
            metadata={"source": "conversation", "type": "preference"},
            importance=0.8,
            layer=MemoryLayer.WORKING,
            tags=["preference", "python"],
        )
        memory_os.store(entry)
        
        # メモリ検索
        results = memory_os.retrieve("Python", k=5)
        
        # 統合
        count = memory_os.consolidate()
        
        # 忘却
        count = memory_os.forget(policy="lru")
    """
    
    # 容量制限
    MAX_WORKING_MEMORY = 50
    MAX_SHORT_TERM_MEMORY = 500
    
    # 寿命（秒）
    SHORT_TERM_LIFETIME = 86400  # 24時間
    LONG_TERM_LIFETIME = float('inf')  # 恒久的
    
    # 統合閾値（短期メモリの使用率）
    CONSOLIDATION_THRESHOLD = 0.8
    
    def __init__(self, project_history_dir: str = "memory/project_history"):
        # メモリ層
        self.working_memory: Dict[str, MemoryEntry] = {}
        self.short_term_memory: Dict[str, MemoryEntry] = {}
        self.long_term_memory: Dict[str, MemoryEntry] = {}
        self.semantic_memory: Dict[str, MemoryEntry] = {}
        
        # プロジェクト履歴ストレージ
        self.project_history_store = ProjectHistoryStore(project_history_dir)
        
        # 統計
        self.stats = {
            "total_stored": 0,
            "total_retrieved": 0,
            "total_consolidated": 0,
            "total_forgotten": 0,
            "total_compressed": 0,
        }
    
    # ========================================
    # メモリ保存
    # ========================================
    
    def store(self, entry: MemoryEntry) -> str:
        """
        メモリを保存。
        
        Args:
            entry: 保存するメモリエントリ
            
        Returns:
            エントリID
        """
        # IDが未設定なら自動生成
        if not entry.id:
            entry.id = f"mem_{int(time.time())}_{uuid.uuid4().hex[:8]}"
        
        # 層に応じて保存
        if entry.layer == MemoryLayer.WORKING:
            self._store_working(entry)
        elif entry.layer == MemoryLayer.SHORT_TERM:
            self._store_short_term(entry)
        elif entry.layer == MemoryLayer.LONG_TERM:
            self._store_long_term(entry)
        elif entry.layer == MemoryLayer.SEMANTIC:
            self._store_semantic(entry)
        
        self.stats["total_stored"] += 1
        return entry.id
    
    def _store_working(self, entry: MemoryEntry):
        """作業メモリへ保存"""
        if len(self.working_memory) >= self.MAX_WORKING_MEMORY:
            # 容量超過時は自動で短期メモリへ移動
            self._promote_to_short_term(entry)
            return
        
        self.working_memory[entry.id] = entry
    
    def _store_short_term(self, entry: MemoryEntry):
        """短期メモリへ保存"""
        if len(self.short_term_memory) >= self.MAX_SHORT_TERM_MEMORY:
            # 容量超過時は自動で長期メモリへ移動
            self._promote_to_long_term(entry)
            return
        
        self.short_term_memory[entry.id] = entry
    
    def _store_long_term(self, entry: MemoryEntry):
        """長期メモリへ保存"""
        self.long_term_memory[entry.id] = entry
    
    def _store_semantic(self, entry: MemoryEntry):
        """意味メモリへ保存"""
        self.semantic_memory[entry.id] = entry
    
    def _promote_to_short_term(self, entry: MemoryEntry):
        """作業メモリから短期メモリへ移動"""
        entry.layer = MemoryLayer.SHORT_TERM
        self.short_term_memory[entry.id] = entry
        if entry.id in self.working_memory:
            del self.working_memory[entry.id]
    
    def _promote_to_long_term(self, entry: MemoryEntry):
        """短期メモリから長期メモリへ移動"""
        entry.layer = MemoryLayer.LONG_TERM
        self.long_term_memory[entry.id] = entry
        if entry.id in self.short_term_memory:
            del self.short_term_memory[entry.id]
    
    # ========================================
    # メモリ検索
    # ========================================
    
    def retrieve(self, query: str, k: int = 5, layer: Optional[MemoryLayer] = None) -> List[MemoryEntry]:
        """
        メモリを検索。
        
        Args:
            query: 検索クエリ
            k: 返す結果数
            layer: 検索層（Noneで全層）
            
        Returns:
            検索結果（重要度降順）
        """
        results = []
        
        # 指定層または全層から検索
        if layer:
            memories = self._get_memories_by_layer(layer)
        else:
            memories = self._get_all_memories()
        
        # クエリとの関連度でスコアリング
        for entry_id, entry in memories.items():
            score = self._score_relevance(entry, query)
            if score > 0:
                results.append((score, entry))
        
        # スコア降順にソート
        results.sort(key=lambda x: x[0], reverse=True)
        
        # 上位k件を返す
        top_k = [entry for _, entry in results[:k]]
        
        # アクセス統計更新
        for entry in top_k:
            entry.touch()
        
        self.stats["total_retrieved"] += len(top_k)
        return top_k
    
    def _get_memories_by_layer(self, layer: MemoryLayer) -> Dict[str, MemoryEntry]:
        """指定層のメモリを取得"""
        layer_map = {
            MemoryLayer.WORKING: self.working_memory,
            MemoryLayer.SHORT_TERM: self.short_term_memory,
            MemoryLayer.LONG_TERM: self.long_term_memory,
            MemoryLayer.SEMANTIC: self.semantic_memory,
        }
        return layer_map.get(layer, {})
    
    def _get_all_memories(self) -> Dict[str, MemoryEntry]:
        """全層のメモリを取得"""
        all_memories = {}
        all_memories.update(self.working_memory)
        all_memories.update(self.short_term_memory)
        all_memories.update(self.long_term_memory)
        all_memories.update(self.semantic_memory)
        return all_memories
    
    def _score_relevance(self, entry: MemoryEntry, query: str) -> float:
        """エントリとクエリの関連度をスコアリング"""
        score = 0.0
        
        # タグの一致
        query_tags = query.lower().split()
        for tag in entry.tags:
            if tag.lower() in query_tags:
                score += 0.3
        
        # コンテンツの一致
        if query.lower() in entry.content.lower():
            score += 0.5
        
        # メタデータの一致
        for value in entry.metadata.values():
            if isinstance(value, str) and query.lower() in value.lower():
                score += 0.2
        
        # 重要度の加重
        score *= (1.0 + entry.importance)
        
        # アクセス回数の加重（頻繁にアクセスされるほど重要）
        score *= (1.0 + 0.1 * entry.access_count)
        
        return score
    
    # ========================================
    # メモリ更新・削除
    # ========================================
    
    def update(self, id: str, data: Dict[str, Any]) -> bool:
        """
        メモリを更新。
        
        Args:
            id: エントリID
            data: 更新データ
            
        Returns:
            更新成功時 True
        """
        entry = self._find_entry(id)
        if not entry:
            return False
        
        for key, value in data.items():
            if hasattr(entry, key):
                setattr(entry, key, value)
        
        entry.touch()
        return True
    
    def delete(self, id: str) -> bool:
        """
        メモリを削除。
        
        Args:
            id: エントリID
            
        Returns:
            削除成功時 True
        """
        entry = self._find_entry(id)
        if not entry:
            return False
        
        # 層に応じて削除
        if entry.id in self.working_memory:
            del self.working_memory[entry.id]
        elif entry.id in self.short_term_memory:
            del self.short_term_memory[entry.id]
        elif entry.id in self.long_term_memory:
            del self.long_term_memory[entry.id]
        elif entry.id in self.semantic_memory:
            del self.semantic_memory[entry.id]
        
        return True
    
    def _find_entry(self, id: str) -> Optional[MemoryEntry]:
        """エントリを検索"""
        for memories in [self.working_memory, self.short_term_memory, 
                         self.long_term_memory, self.semantic_memory]:
            if id in memories:
                return memories[id]
        return None
    
    # ========================================
    # 自動統合
    # ========================================
    
    def consolidate(self) -> int:
        """
        短期メモリから長期メモリへ統合。
        
        Returns:
            統合されたエントリ数
        """
        count = 0
        
        # 短期メモリが閾値に達しているかチェック
        short_term_usage = len(self.short_term_memory) / self.MAX_SHORT_TERM_MEMORY if self.MAX_SHORT_TERM_MEMORY > 0 else 0
        
        if short_term_usage < self.CONSOLIDATION_THRESHOLD:
            return 0  # 閾値に達していない
        
        # 重要度が高いものから長期メモリへ移動
        entries = sorted(
            self.short_term_memory.values(),
            key=lambda e: e.importance,
            reverse=True,
        )
        
        for entry in entries:
            if len(self.short_term_memory) <= self.MAX_SHORT_TERM_MEMORY * (1 - self.CONSOLIDATION_THRESHOLD):
                break
            
            # 長期メモリへ移動
            entry.layer = MemoryLayer.LONG_TERM
            self.long_term_memory[entry.id] = entry
            del self.short_term_memory[entry.id]
            count += 1
        
        self.stats["total_consolidated"] += count
        return count
    
    def consolidate_high_importance(self, threshold: float = 0.8) -> int:
        """
        重要度が高い記憶を強制的に長期メモリへ移動。
        
        Args:
            threshold: 重要度の閾値
            
        Returns:
            移動されたエントリ数
        """
        count = 0
        
        # 重要度が高いエントリを検索
        high_importance_entries = [
            entry for entry in self.short_term_memory.values()
            if entry.importance >= threshold
        ]
        
        # 長期メモリへ移動
        for entry in high_importance_entries:
            entry.layer = MemoryLayer.LONG_TERM
            self.long_term_memory[entry.id] = entry
            del self.short_term_memory[entry.id]
            count += 1
        
        self.stats["total_consolidated"] += count
        return count
    
    # ========================================
    # 忘却
    # ========================================
    
    def forget(self, policy: str = "lru") -> int:
        """
        メモリを忘却。
        
        Args:
            policy: 忘却ポリシー (lru, importance, time)
            
        Returns:
            忘却されたエントリ数
        """
        count = 0
        
        if policy == "lru":
            count = self._forget_lru()
        elif policy == "importance":
            count = self._forget_by_importance()
        elif policy == "time":
            count = self._forget_by_time()
        
        self.stats["total_forgotten"] += count
        return count
    
    def _forget_lru(self) -> int:
        """LRU (Least Recently Used) による忘却"""
        count = 0
        
        # 短期メモリから忘却
        if self.short_term_memory:
            entries = sorted(
                self.short_term_memory.values(),
                key=lambda e: e.accessed_at,
            )
            
            # 古いものから50%を忘却
            forget_count = max(1, len(entries) // 2)
            for entry in entries[:forget_count]:
                if entry.is_expired(self.SHORT_TERM_LIFETIME):
                    del self.short_term_memory[entry.id]
                    count += 1
        
        return count
    
    def _forget_by_importance(self) -> int:
        """重要度ベースの忘却"""
        count = 0
        
        # 短期メモリから忘却
        if self.short_term_memory:
            entries = sorted(
                self.short_term_memory.values(),
                key=lambda e: e.importance,
            )
            
            # 重要度が低いものから忘却
            for entry in entries:
                if entry.importance < 0.2:
                    del self.short_term_memory[entry.id]
                    count += 1
        
        return count
    
    def _forget_by_time(self) -> int:
        """時間ベースの忘却"""
        count = 0
        
        # 短期メモリから忘却
        if self.short_term_memory:
            expired_entries = [
                entry for entry in self.short_term_memory.values()
                if entry.is_expired(self.SHORT_TERM_LIFETIME)
            ]
            
            for entry in expired_entries:
                del self.short_term_memory[entry.id]
                count += 1
        
        return count
    
    # ========================================
    # 圧縮
    # ========================================
    
    def compress(self) -> int:
        """
        メモリを圧縮（類似エントリのマージ）。
        
        Returns:
            圧縮されたエントリ数
        """
        count = 0
        
        # 短期メモリ内で圧縮
        if len(self.short_term_memory) < 2:
            return 0
        
        entries = list(self.short_term_memory.values())
        merged_ids = set()
        
        for i, entry1 in enumerate(entries):
            if entry1.id in merged_ids:
                continue
            
            for j, entry2 in enumerate(entries):
                if i >= j or entry2.id in merged_ids:
                    continue
                
                # 類似度チェック
                similarity = entry1.similarity(entry2)
                if similarity > 0.5:
                    # 類似エントリをマージ
                    merged_content = f"{entry1.content}\n{entry2.content}"
                    merged_tags = list(set(entry1.tags + entry2.tags))
                    merged_importance = max(entry1.importance, entry2.importance)
                    
                    # entry1を保持し、entry2を削除
                    entry1.content = merged_content
                    entry1.tags = merged_tags
                    entry1.importance = merged_importance
                    entry1.touch()
                    
                    del self.short_term_memory[entry2.id]
                    merged_ids.add(entry2.id)
                    count += 1
        
        self.stats["total_compressed"] += count
        return count
    
    # ========================================
    # 統計
    # ========================================
    
    def get_stats(self) -> Dict:
        """メモリ統計を取得"""
        return {
            "working_memory_count": len(self.working_memory),
            "short_term_memory_count": len(self.short_term_memory),
            "long_term_memory_count": len(self.long_term_memory),
            "semantic_memory_count": len(self.semantic_memory),
            "total_entries": (len(self.working_memory) + len(self.short_term_memory) +
                            len(self.long_term_memory) + len(self.semantic_memory)),
            "stats": self.stats.copy(),
        }
    
    def get_status(self) -> Dict:
        """メモリステータス"""
        stats = self.get_stats()
        stats["short_term_usage"] = (
            len(self.short_term_memory) / self.MAX_SHORT_TERM_MEMORY
            if self.MAX_SHORT_TERM_MEMORY > 0 else 0
        )
        return stats
    
    def reset(self):
        """メモリをリセット"""
        self.working_memory.clear()
        self.short_term_memory.clear()
        self.long_term_memory.clear()
        self.semantic_memory.clear()
        self.stats = {
            "total_stored": 0,
            "total_retrieved": 0,
            "total_consolidated": 0,
            "total_forgotten": 0,
            "total_compressed": 0,
        }


# ========================================
# ファクトリ関数
# ========================================

def create_memory_os() -> MemoryOS:
    """MemoryOSの作成（ファクトリ関数）"""
    return MemoryOS()
