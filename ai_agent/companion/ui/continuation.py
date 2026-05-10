"""
Continuation Handler - 継続ハンドラー
Project_036: P2 - iPhone Companion Implementation

セッションの継続と復元を提供します。
"""

from typing import Dict, List, Optional


class ContinuationHandler:
    """継続ハンドラー"""
    
    def __init__(self, runtime, memory_os):
        """
        ContinuationHandlerを初期化
        
        Args:
            runtime: Runtime Coreインスタンス
            memory_os: Memory OSインスタンス
        """
        self.runtime = runtime
        self.memory_os = memory_os
    
    def get_continuation_context(self) -> dict:
        """
        継続のためのコンテキストを取得
        
        Returns:
            dict: 継続コンテキスト
                - last_session: 最後のセッション情報
                - recent_memory: 最近のメモリエントリ（最大5件）
        """
        return {
            "last_session": self.runtime.get_last_session(),
            "recent_memory": self.memory_os.get_recent_entries(limit=5)
        }
    
    def restore_session(self, session_id: str) -> bool:
        """
        セッションを再開
        
        Args:
            session_id: セッションID
            
        Returns:
            bool: 再開に成功したか
        """
        return self.runtime.restore_session(session_id)
    
    def get_available_sessions(self) -> List[Dict]:
        """
        利用可能なセッション一覧を取得
        
        Returns:
            List[Dict]: セッション一覧
        """
        return self.runtime.get_session_list()
    
    def get_last_session_id(self) -> Optional[str]:
        """
        最後のセッションIDを取得
        
        Returns:
            Optional[str]: 最後のセッションID（存在しない場合はNone）
        """
        last_session = self.runtime.get_last_session()
        if last_session:
            return last_session.get("id")
        return None
