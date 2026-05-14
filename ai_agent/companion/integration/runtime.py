"""
Runtime Integration - Runtimeとの統合
Project_036: P2 - iPhone Companion Implementation

Runtime Coreとの統合を提供します。
"""

from typing import Dict, List, Optional


class RuntimeIntegration:
    """Runtimeとの統合"""
    
    def __init__(self, runtime_core):
        """
        RuntimeIntegrationを初期化
        
        Args:
            runtime_core: Runtime Coreインスタンス
        """
        self.runtime = runtime_core
    
    def get_state(self) -> str:
        """
        現在のRuntime状態を取得
        
        Returns:
            str: 現在の状態 (RUNNING/WAITING/COMPLETE/INTERRUPTED/TIMEOUT)
        """
        return self.runtime.get_state()
    
    def get_last_session(self) -> dict:
        """
        最後のセッション情報を取得
        
        Returns:
            dict: 最後のセッション情報
        """
        return self.runtime.get_last_session()
    
    def restore_session(self, session_id: str) -> bool:
        """
        セッションを再開
        
        Args:
            session_id: セッションID
            
        Returns:
            bool: 再開に成功したか
        """
        return self.runtime.restore_session(session_id)
    
    def get_session_list(self) -> List[Dict]:
        """
        セッション一覧を取得
        
        Returns:
            List[Dict]: セッション一覧
        """
        return self.runtime.get_session_list()
    
    def get_state_transition(self) -> dict:
        """
        状態遷移情報を取得
        
        Returns:
            dict: 状態遷移情報
        """
        if hasattr(self.runtime, 'get_state_transition'):
            return self.runtime.get_state_transition()
        return {
            "current": self.runtime.get_state(),
            "transitions": []
        }
    
    def is_running(self) -> bool:
        """
        実行中か判定
        
        Returns:
            bool: 実行中か
        """
        return self.runtime.get_state() == "RUNNING"
    
    def is_complete(self) -> bool:
        """
        完了か判定
        
        Returns:
            bool: 完了か
        """
        return self.runtime.get_state() == "COMPLETE"
    
    def is_interrupted(self) -> bool:
        """
        中断中か判定
        
        Returns:
            bool: 中断中か
        """
        return self.runtime.get_state() == "INTERRUPTED"
    
    def is_timeout(self) -> bool:
        """
        タイアウトか判定
        
        Returns:
            bool: タイアウトか
        """
        return self.runtime.get_state() == "TIMEOUT"
