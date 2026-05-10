"""
Memory Integration - Memory OSとの統合
Project_036: P2 - iPhone Companion Implementation

Memory OSとの統合を提供します。
"""

from typing import Dict, List, Optional


class MemoryIntegration:
    """Memory OSとの統合"""
    
    def __init__(self, memory_os):
        """
        MemoryIntegrationを初期化
        
        Args:
            memory_os: Memory OSインスタンス
        """
        self.memory_os = memory_os
    
    def get_usage_stats(self) -> dict:
        """
        メモリ使用率を取得
        
        Returns:
            dict: メモリ使用率統計
        """
        return self.memory_os.get_stats()
    
    def get_recent_entries(self, limit: int = 5) -> List[Dict]:
        """
        最近のメモリエントリを取得
        
        Args:
            limit: 取得するエントリの最大数
            
        Returns:
            List[Dict]: 最近のメモリエントリ
        """
        return self.memory_os.get_recent_entries(limit=limit)
    
    def get_compression_ratio(self) -> float:
        """
        圧縮率を取得
        
        Returns:
            float: 圧縮率
        """
        return self.memory_os.get_compression_ratio()
    
    def get_last_compression_time(self) -> float:
        """
        最後の圧縮時刻を取得
        
        Returns:
            float: 最後の圧縮時刻（timestamp）
        """
        return self.memory_os.get_last_compression_time()
    
    def get_growth_rate(self) -> float:
        """
        メモリの成長率を取得
        
        Returns:
            float: 成長率
        """
        return self.memory_os.get_growth_rate()
    
    def get_health_status(self) -> str:
        """
        メモリの健全性を取得
        
        Returns:
            str: 健全性ステータス
        """
        return self.memory_os.get_health_status()
    
    def get_memory_trend(self) -> dict:
        """
        メモリの傾向を取得
        
        Returns:
            dict: メモリの傾向
        """
        return {
            "growth_rate": self.memory_os.get_growth_rate(),
            "compression_rate": self.memory_os.get_compression_ratio(),
            "health": self.memory_os.get_health_status()
        }
