"""
iPhone Companion Core
Project_036: P2 - iPhone Companion Implementation

Companion Coreは、Runtime, Memory OS, Observabilityを統合し、
iPhone Companionとしてのコアロジックを提供します。

基本方針:
- chat app ではない
- 「静かな remote runtime window」である
- 生活の邪魔をしない存在
"""

import time
from typing import Dict, Optional
from ai_agent.companion.notification_policy import NotificationPolicy, List


class CompanionCore:
    """iPhone Companionのコアロジック"""
    
    def __init__(self, runtime, memory_os, observability):
        """
        Companion Coreを初期化
        
        Args:
            runtime: Runtime Coreインスタンス
            memory_os: Memory OSインスタンス
            observability: Observability Managerインスタンス
        """
        self.runtime = runtime
        self.memory_os = memory_os
        self.observability = observability
        self.notification_policy = NotificationPolicy()
        self._last_status = None
        self._status_timestamp = 0
    
    def get_status(self) -> dict:
        """
        最小限のステータスを取得
        
        Returns:
            dict: ステータス情報
                - state: Runtimeの状態 (RUNNING/WAITING/COMPLETE/INTERRUPTED/TIMEOUT)
                - memory_usage: メモリ使用率統計
                - health: ヘルスステータス
        """
        # キャッシュ活用（1秒以内は同じデータを返す）
        current_time = time.time()
        if (self._last_status and 
            current_time - self._status_timestamp < 1.0):
            return self._last_status
        
        status = {
            "state": self.runtime.get_state(),
            "memory_usage": self.memory_os.get_usage_stats(),
            "health": self.observability.get_health_status()
        }
        
        self._last_status = status
        self._status_timestamp = current_time
        
        return status
    
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
    
    def should_notify(self, category: str) -> bool:
        """
        通知が必要か判定（冷却時間考慮）
        
        Args:
            category: 通知カテゴリ
                - critical_issue: 緊急問題
                - active_assistance: 明示的リクエスト時
                - idle_notification: アイドル通知（禁止）
                - passive_notification: 受動通知（禁止）
                - recovery_notification: リカバリ通知（禁止）
        
        Returns:
            bool: 通知が必要か
        """
        return self.notification_policy.should_notify(category)
    
    def record_notification(self, category: str):
        """
        通知を記録
        
        Args:
            category: 通知カテゴリ
        """
        self.notification_policy.record_notification(category)
    
    def get_notification_status(self) -> dict:
        """
        通知ステータスを取得
        
        Returns:
            dict: 通知ステータス
        """
        return self.notification_policy.get_status()
    
    def get_state_transition(self) -> dict:
        """
        状態遷移情報を取得
        
        Returns:
            dict: 状態遷移情報
                - current: 現在の状態
                - transitions: 直近の状態遷移履歴
        """
        if hasattr(self.runtime, 'get_state_transition'):
            return self.runtime.get_state_transition()
        return {
            "current": self.runtime.get_state(),
            "transitions": []
        }
    
    def get_memory_compression_status(self) -> dict:
        """
        メモリ圧縮ステータスを取得
        
        Returns:
            dict: 圧縮ステータス
        """
        return {
            "ratio": self.memory_os.get_compression_ratio(),
            "last_compression": self.memory_os.get_last_compression_time()
        }
    
    def get_metrics_summary(self) -> dict:
        """
        メトリクスサマリーを取得
        
        Returns:
            dict: メトリクスサマリー
        """
        return self.observability.get_metrics_summary()
    
    def reset_status_cache(self):
        """ステータスキャッシュをリセット"""
        self._last_status = None
        self._status_timestamp = 0
