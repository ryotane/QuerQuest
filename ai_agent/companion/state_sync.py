"""
State Sync - Runtimeとの状態同期
Project_036: P2 - iPhone Companion Implementation

Runtimeの状態を同期し、変更時のみ通知を提供します。
"""

import time
from typing import Dict, List, Optional


class StateSync:
    """Runtimeとの状態同期"""
    
    def __init__(self, runtime):
        """
        StateSyncを初期化
        
        Args:
            runtime: Runtime Coreインスタンス
        """
        self.runtime = runtime
        self.last_state = None
        self.state_history: List[Dict] = []
        self._max_history = 10  # 履歴の最大件数
    
    def sync_state(self) -> str:
        """
        現在の状態を取得（変更時のみ履歴に追加）
        
        Returns:
            str: 現在の状態 (RUNNING/WAITING/COMPLETE/INTERRUPTED/TIMEOUT)
        """
        current_state = self.runtime.get_state()
        
        if current_state != self.last_state:
            self._add_state_transition(current_state)
            self.last_state = current_state
        
        return current_state
    
    def _add_state_transition(self, state: str):
        """
        状態遷移を履歴に追加
        
        Args:
            state: 遷移先の状態
        """
        transition = {
            "state": state,
            "timestamp": time.time()
        }
        self.state_history.append(transition)
        
        # 履歴の最大件数を保持
        if len(self.state_history) > self._max_history:
            self.state_history = self.state_history[-self._max_history:]
    
    def get_state_transition(self) -> dict:
        """
        状態遷移情報を取得
        
        Returns:
            dict: 状態遷移情報
                - current: 現在の状態
                - transitions: 直近の状態遷移履歴（最大3件）
        """
        return {
            "current": self.last_state,
            "transitions": self.state_history[-3:] if self.state_history else []
        }
    
    def get_state_history(self) -> List[Dict]:
        """
        状態履歴を全部取得
        
        Returns:
            List[Dict]: 状態履歴
        """
        return self.state_history.copy()
    
    def is_state_changed(self) -> bool:
        """
        状態が変更されたか判定
        
        Returns:
            bool: 変更されたか
        """
        current_state = self.runtime.get_state()
        return current_state != self.last_state
    
    def reset(self):
        """同期状態をリセット"""
        self.last_state = None
        self.state_history = []
