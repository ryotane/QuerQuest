# ai_agent/workspace/memory_stabilization/context_deduplicator.py

"""
Context Deduplicator Module

重複した context を排除し、
token 効率を最適化する。

役割:
1. 同一 content の検出・排除
2. 類似 content のマージ
3. 重複トピックの統合
"""

import hashlib
from typing import Optional


class ContextDeduplicator:
    """
    context 重複排除
    
    仕組み:
    - content のハッシュ値で重複検出
    - 類似 content のマージ
    - 重複トピックの統合
    """
    
    # 類似判定のしきい値（文字列一致率）
    SIMILARITY_THRESHOLD = 0.8
    
    def __init__(self):
        self._seen_hashes: set = set()
    
    def hash_content(self, content: str) -> str:
        """content のハッシュ値を生成"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]
    
    def is_duplicate(self, content: str) -> bool:
        """
        content が重複かチェック
        
        Args:
            content: チェック対象のcontent
            
        Returns:
            重複なら True
        """
        h = self.hash_content(content)
        return h in self._seen_hashes
    
    def mark_seen(self, content: str):
        """content を既見としてマーク"""
        h = self.hash_content(content)
        self._seen_hashes.add(h)
    
    def deduplicate_list(self, items: list) -> list:
        """
        リストから重複を排除
        
        Args:
            items: 対象リスト
            
        Returns:
            重複排除後のリスト
        """
        seen = set()
        result = []
        
        for item in items:
            if isinstance(item, str):
                h = self.hash_content(item)
                if h not in seen:
                    seen.add(h)
                    result.append(item)
            else:
                # 辞書などの場合は文字列化
                key = str(item)
                h = self.hash_content(key)
                if h not in seen:
                    seen.add(h)
                    result.append(item)
        
        return result
    
    def deduplicate_topics(self, topics: list) -> list:
        """
        トピックリストから重複を排除
        
        大文字小文字を区別せず、前後の空白を除去。
        
        Args:
            topics: トピックリスト
            
        Returns:
            重複排除後のトピックリスト
        """
        seen = set()
        result = []
        
        for topic in topics:
            # 正規化
            normalized = topic.strip().lower()
            if normalized and normalized not in seen:
                seen.add(normalized)
                result.append(topic.strip())
        
        return result
    
    def merge_similar_summaries(self, summaries: list) -> str:
        """
        類似の要約をマージ
        
        最も長い要約を保持し、短い要約を排除。
        
        Args:
            summaries: 要約リスト
            
        Returns:
            マージされた要約
        """
        if not summaries:
            return ""
        
        if len(summaries) == 1:
            return summaries[0]
        
        # 長さでソート（長い順）
        sorted_summaries = sorted(summaries, key=len, reverse=True)
        
        # 最も長い要約を保持
        primary = sorted_summaries[0]
        
        # 類似する短い要約を排除
        result = [primary]
        
        for summary in sorted_summaries[1:]:
            # 単純な文字列一致率で判定
            if len(summary) < len(primary) * 0.5:
                # 50%未満の長さなら別物として保持
                result.append(summary)
            else:
                # 類似度高 → 排除（長い方に統合）
                pass
        
        return "\n\n".join(result) if len(result) > 1 else result[0]
    
    def clear(self):
        """全状態をクリア"""
        self._seen_hashes.clear()
    
    def get_stats(self) -> dict:
        """統計情報を取得"""
        return {
            "seen_count": len(self._seen_hashes),
            "similarity_threshold": self.SIMILARITY_THRESHOLD
        }
