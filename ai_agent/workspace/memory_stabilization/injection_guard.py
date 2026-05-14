# ai_agent/workspace/memory_stabilization/injection_guard.py

"""
Injection Guard Module

injected context の再保存を防止し、
recursive injection を検出・防止する。

役割:
1. system prompt に注入済みの context を追跡
2. 同一 context の再保存をブロック
3. 循環参照を検出
"""

import hashlib
from typing import Optional


class InjectionGuard:
    """
    injected context の追跡・防止
    
    仕組み:
    - context のハッシュ値を記録
    - 同一ハッシュの再保存をブロック
    - 循環参照を検出
    """
    
    # 最大再帰深度
    MAX_RECURSION_DEPTH = 3
    
    def __init__(self):
        self._injected_hashes: set = set()
        self._context_chain: list = []
    
    def hash_context(self, context: str) -> str:
        """context のハッシュ値を生成"""
        return hashlib.sha256(context.encode('utf-8')).hexdigest()[:16]
    
    def is_already_injected(self, context: str) -> bool:
        """
        context が既に注入済みかチェック
        
        Args:
            context: チェック対象のcontext
            
        Returns:
            注入済みなら True
        """
        h = self.hash_context(context)
        return h in self._injected_hashes
    
    def mark_injected(self, context: str):
        """context を注入済みとしてマーク"""
        h = self.hash_context(context)
        self._injected_hashes.add(h)
    
    def detect_recursive_injection(self, current_context: str, 
                                    max_depth: int = None) -> bool:
        """
        recursive injection を検出
        
        context が既に chain に存在するかチェック。
        同一 context が繰り返される = 循環参照。
        
        Args:
            current_context: 現在のcontext
            max_depth: 最大深度（デフォルト MAX_RECURSION_DEPTH）
            
        Returns:
            循環参照があれば True
        """
        if max_depth is None:
            max_depth = self.MAX_RECURSION_DEPTH
        
        h = self.hash_context(current_context)
        
        # 同一ハッシュが chain に存在
        if h in [self.hash_context(c) for c in self._context_chain]:
            return True
        
        # chain に追加
        self._context_chain.append(current_context)
        
        # 深度超過
        if len(self._context_chain) > max_depth:
            return True
        
        return False
    
    def reset_chain(self):
        """context chain をリセット（各リクエスト単位で）"""
        self._context_chain.clear()
    
    def clear(self):
        """全状態をクリア"""
        self._injected_hashes.clear()
        self._context_chain.clear()
    
    def get_stats(self) -> dict:
        """統計情報を取得"""
        return {
            "injected_count": len(self._injected_hashes),
            "chain_length": len(self._context_chain),
            "max_recursion_depth": self.MAX_RECURSION_DEPTH
        }
