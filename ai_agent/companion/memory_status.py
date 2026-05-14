"""
Memory Status - Memory OSのステータスエクスポート
Project_036: P2 - iPhone Companion Implementation

Memory OSのステータスを最小限の形式でエクスポートします。
"""

import time
from typing import Dict, List, Optional


class MemoryStatus:
    """Memory OSのステータスエクスポート"""
    
    def __init__(self, memory_os):
        """
        MemoryStatusを初期化
        
        Args:
            memory_os: Memory OSインスタンス
        """
        self.memory_os = memory_os
        self._last_export_time = 0
        self._export_interval = 5.0  # 5秒以内はキャッシュ
    
    def get_usage_stats(self) -> dict:
        """
        メモリ使用率を取得（最小限）
        
        Returns:
            dict: メモリ使用率統計
                - working: Working Memoryのエントリ数
                - short_term: Short-term Memoryのエントリ数
                - long_term: Long-term Memoryのエントリ数
                - semantic: Semantic Memoryのエントリ数
                - total: 総エントリ数
        """
        # キャッシュ活用
        current_time = time.time()
        if (self._last_export_time and 
            current_time - self._last_export_time < self._export_interval):
            return self._last_export
        
        stats = self.memory_os.get_stats()
        
        self._last_export = {
            "working": stats.get("working", {}).get("count", 0),
            "short_term": stats.get("short_term", {}).get("count", 0),
            "long_term": stats.get("long_term", {}).get("count", 0),
            "semantic": stats.get("semantic", {}).get("count", 0),
            "total": stats.get("total_count", 0)
        }
        
        self._last_export_time = current_time
        
        return self._last_export
    
    def get_compression_status(self) -> dict:
        """
        圧縮ステータスを取得（オプション）
        
        Returns:
            dict: 圧縮ステータス
                - ratio: 圧縮率
                - last_compression: 最後の圧縮時刻
        """
        return {
            "ratio": self.memory_os.get_compression_ratio(),
            "last_compression": self.memory_os.get_last_compression_time()
        }
    
    def get_recent_entries(self, limit: int = 5) -> List[Dict]:
        """
        最近のメモリエントリを取得
        
        Args:
            limit: 取得するエントリの最大数
        
        Returns:
            List[Dict]: 最近のメモリエントリ
        """
        return self.memory_os.get_recent_entries(limit=limit)
    
    def get_memory_trend(self) -> dict:
        """
        メモリの傾向を取得
        
        Returns:
            dict: メモリの傾向
                - growth_rate: 成長率
                - compression_rate: 圧縮率
                - health: メモリの健全性
        """
        return {
            "growth_rate": self.memory_os.get_growth_rate(),
            "compression_rate": self.memory_os.get_compression_ratio(),
            "health": self.memory_os.get_health_status()
        }
    
    def reset_cache(self):
        """キャッシュをリセット"""
        self._last_export_time = 0
        self._last_export = None
