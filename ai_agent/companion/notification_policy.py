"""
Notification Policy - 通知ポリシー
Project_036: P2 - iPhone Companion Implementation

Project_17の通知ポリシーに基づき、最小限の通知を提供します。

基本ルール:
- 1日5回まで
- バッチ配信（リアルタイム同期無効）
- 緊急時以外: none
"""

import time
from typing import Dict, List, Optional


class NotificationPolicy:
    """通知ポリシー（Project_17準拠）"""
    
    def __init__(self):
        """
        NotificationPolicyを初期化
        
        設定値（runtime_config.yaml準拠）:
            max_daily_notifications: 5（1日あたりの通知上限）
            cooldown_seconds: 3600（1時間、緊急時以外）
        """
        self.max_daily_notifications = 5
        self.cooldown_seconds = 3600  # 1時間
        self.daily_count = 0
        self.last_notification_time = 0
        self.notification_history: List[Dict] = []
        
        # カテゴリ別の通知レベル
        self._notification_levels = {
            "critical_issue": "high",      # 緊急問題：高
            "active_assistance": "low",     # 明示的リクエスト時：低
            "idle_notification": "none",    # アイドル通知：禁止
            "passive_notification": "none", # 受動通知：禁止
            "recovery_notification": "none" # リカバリ通知：禁止
        }
    
    def should_notify(self, category: str) -> bool:
        """
        通知が必要か判定
        
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
        # カテゴリ別のレベルチェック
        level = self.get_notification_level(category)
        if level == "none":
            return False
        
        # 1日あたりの上限チェック
        if self.daily_count >= self.max_daily_notifications:
            return False
        
        # 冷却時間チェック
        if time.time() - self.last_notification_time < self.cooldown_seconds:
            return False
        
        return True
    
    def record_notification(self, category: str):
        """
        通知を記録
        
        Args:
            category: 通知カテゴリ
        """
        self.daily_count += 1
        self.last_notification_time = time.time()
        self.notification_history.append({
            "category": category,
            "timestamp": time.time()
        })
        
        # 履歴の最大件数を保持（100件）
        if len(self.notification_history) > 100:
            self.notification_history = self.notification_history[-100:]
    
    def get_notification_level(self, category: str) -> str:
        """
        カテゴリ別の通知レベルを取得
        
        Args:
            category: 通知カテゴリ
        
        Returns:
            str: 通知レベル (high/low/none)
        """
        return self._notification_levels.get(category, "none")
    
    def get_status(self) -> dict:
        """
        通知ステータスを取得
        
        Returns:
            dict: 通知ステータス
                - daily_count: 1日あたりの通知数
                - max_daily: 1日あたりの上限
                - remaining: 残り通知可能数
                - last_notification: 最後の通知時刻
                - cooldown_remaining: 冷却時間残り（秒）
        """
        cooldown_remaining = max(0, self.cooldown_seconds - (time.time() - self.last_notification_time))
        
        return {
            "daily_count": self.daily_count,
            "max_daily": self.max_daily_notifications,
            "remaining": max(0, self.max_daily_notifications - self.daily_count),
            "last_notification": self.last_notification_time,
            "cooldown_remaining": cooldown_remaining
        }
    
    def reset_daily_count(self):
        """1日あたりの通知カウントをリセット（日付変更時）"""
        self.daily_count = 0
        self.last_notification_time = 0
        self.notification_history = []
    
    def get_recent_notifications(self, limit: int = 5) -> List[Dict]:
        """
        最近の通知履歴を取得
        
        Args:
            limit: 取得する履歴の数
        
        Returns:
            List[Dict]: 最近の通知履歴
        """
        return self.notification_history[-limit:] if self.notification_history else []
