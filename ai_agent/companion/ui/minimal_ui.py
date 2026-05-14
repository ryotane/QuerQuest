"""
Minimal UI - 最小限のUIコンポーネント
Project_036: P2 - iPhone Companion Implementation

最小限のUIを提供し、詳細は必要時のみ表示します。
"""

from typing import Dict, Optional
from ai_agent.companion.ui.status_view import StatusView


class MinimalUI:
    """最小限のUIコンポーネント"""
    
    def __init__(self):
        """MinimalUIを初期化"""
        self.status_view = StatusView()
        self.is_detail_visible = False
    
    def get_main_display(self, status: dict) -> str:
        """
        メイン表示（状態のみ）
        
        Args:
            status: ステータス情報
            
        Returns:
            str: メイン表示テキスト（変更時のみ）
        """
        if self.status_view.should_update(status):
            rendered = self.status_view.render(status)
            self.status_view.update_displayed_state(status)
            return rendered
        return ""  # 変更なし
    
    def get_detail_display(self, status: dict) -> str:
        """
        詳細表示（オプション）
        
        Args:
            status: ステータス情報
            
        Returns:
            str: 詳細表示テキスト（詳細が表示中のみのみ）
        """
        if not self.is_detail_visible:
            return ""
        
        memory_usage = status.get("memory_usage", {})
        health = status.get("health", {})
        
        lines = [
            f"メモリ: {memory_usage.get('total', 0)} エントリ",
            f"ヘルス: {health.get('status', 'UNKNOWN')}"
        ]
        return "\n".join(lines)
    
    def toggle_detail(self):
        """詳細表示の切り替え"""
        self.is_detail_visible = not self.is_detail_visible
    
    def set_detail_visible(self, visible: bool):
        """
        詳細表示の状態を設定
        
        Args:
            visible: 詳細表示の有無
        """
        self.is_detail_visible = visible
    
    def is_visible(self) -> bool:
        """
        UIが表示中か判定
        
        Returns:
            bool: 表示中か
        """
        return self.is_detail_visible
    
    def reset(self):
        """UI状態をリセット"""
        self.is_detail_visible = False
        self.status_view.clear()
