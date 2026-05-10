"""
Status View - 状態表示ビュー
Project_036: P2 - iPhone Companion Implementation

最小限の状態表示を提供します。
"""

from typing import Dict, Optional


class StatusView:
    """状態表示ビュー（最小限）"""
    
    def __init__(self):
        """StatusViewを初期化"""
        self.displayed_state = None
    
    def render(self, status: dict) -> str:
        """
        最小限のステータスをレンダリング
        
        Args:
            status: ステータス情報
            
        Returns:
            str: レンダリングされたステータス（例: "● RUNNING"）
        """
        state = status.get("state", "UNKNOWN")
        
        # 状態アイコン
        icons = {
            "RUNNING": "●",
            "WAITING": "○",
            "COMPLETE": "✓",
            "INTERRUPTED": "!",
            "TIMEOUT": "⏱"
        }
        icon = icons.get(state, "?")
        
        # 1行ステータス
        return f"{icon} {state}"
    
    def should_update(self, status: dict) -> bool:
        """
        表示更新が必要か判定
        
        Args:
            status: 新しいステータス
            
        Returns:
            bool: 更新が必要か
        """
        return self.displayed_state != status.get("state")
    
    def update_displayed_state(self, status: dict):
        """
        表示された状態を更新
        
        Args:
            status: 新しいステータス
        """
        self.displayed_state = status.get("state")
    
    def clear(self):
        """表示状態をクリア"""
        self.displayed_state = None
