"""
iPhone Companion Test
Project_036: P2 - iPhone Companion Implementation

Companion Core, State Sync, Memory Status, Notification Policyのテスト。
"""

import unittest
import time
from unittest.mock import MagicMock, Mock


class TestCompanionCore(unittest.TestCase):
    """Companion Coreのテスト"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        # Mockオブジェクトの作成
        self.mock_runtime = MagicMock()
        self.mock_runtime.get_state.return_value = "RUNNING"
        self.mock_runtime.get_last_session.return_value = {"id": "test_session"}
        
        self.mock_memory_os = MagicMock()
        self.mock_memory_os.get_usage_stats.return_value = {"total": 100}
        self.mock_memory_os.get_recent_entries.return_value = []
        self.mock_memory_os.get_compression_ratio.return_value = 0.5
        self.mock_memory_os.get_last_compression_time.return_value = time.time()
        
        self.mock_observability = MagicMock()
        self.mock_observability.get_health_status.return_value = {"status": "healthy"}
        self.mock_observability.get_metrics_summary.return_value = {}
        
        # Companion Coreの初期化
        from ai_agent.companion.core import CompanionCore
        self.companion = CompanionCore(
            self.mock_runtime,
            self.mock_memory_os,
            self.mock_observability
        )
    
    def test_get_status(self):
        """ステータス取得のテスト"""
        status = self.companion.get_status()
        
        self.assertIn("state", status)
        self.assertIn("memory_usage", status)
        self.assertIn("health", status)
        self.assertEqual(status["state"], "RUNNING")
    
    def test_get_continuation_context(self):
        """継続コンテキスト取得のテスト"""
        context = self.companion.get_continuation_context()
        
        self.assertIn("last_session", context)
        self.assertIn("recent_memory", context)
        self.assertEqual(context["last_session"]["id"], "test_session")
    
    def test_should_notify(self):
        """通知判定のテスト"""
        # critical_issueは通知可能
        self.assertTrue(self.companion.should_notify("critical_issue"))
        
        # idle_notificationは通知不可
        self.assertFalse(self.companion.should_notify("idle_notification"))
        
        # passive_notificationは通知不可
        self.assertFalse(self.companion.should_notify("passive_notification"))
    
    def test_record_notification(self):
        """通知記録のテスト"""
        self.companion.record_notification("critical_issue")
        
        notification_status = self.companion.get_notification_status()
        self.assertEqual(notification_status["daily_count"], 1)
    
    def test_get_state_transition(self):
        """状態遷移情報のテスト"""
        # mockのget_state_transitionを設定
        self.mock_runtime.get_state_transition.return_value = {
            "current": "RUNNING",
            "transitions": []
        }
        
        transition = self.companion.get_state_transition()
        
        self.assertIn("current", transition)
        self.assertIn("transitions", transition)
    
    def test_get_memory_compression_status(self):
        """メモリ圧縮ステータスのテスト"""
        compression_status = self.companion.get_memory_compression_status()
        
        self.assertIn("ratio", compression_status)
        self.assertIn("last_compression", compression_status)
    
    def test_get_metrics_summary(self):
        """メトリクスサマリーのテスト"""
        metrics = self.companion.get_metrics_summary()
        
        self.assertIsInstance(metrics, dict)
    
    def test_reset_status_cache(self):
        """ステータスキャッシュのリセットのテスト"""
        # 最初にステータスを取得
        self.companion.get_status()
        
        # キャッシュをリセット
        self.companion.reset_status_cache()
        
        # キャッシュがクリアされたことを確認
        self.assertIsNone(self.companion._last_status)


class TestStateSync(unittest.TestCase):
    """State Syncのテスト"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        self.mock_runtime = MagicMock()
        self.mock_runtime.get_state.return_value = "RUNNING"
        
        from ai_agent.companion.state_sync import StateSync
        self.state_sync = StateSync(self.mock_runtime)
    
    def test_sync_state(self):
        """状態同期のテスト"""
        state = self.state_sync.sync_state()
        
        self.assertEqual(state, "RUNNING")
        self.assertEqual(self.state_sync.last_state, "RUNNING")
    
    def test_state_history(self):
        """状態履歴のテスト"""
        # 状態を変更して履歴に追加
        self.mock_runtime.get_state.side_effect = ["RUNNING", "WAITING", "COMPLETE"]
        
        self.state_sync.sync_state()
        self.state_sync.sync_state()
        self.state_sync.sync_state()
        
        history = self.state_sync.get_state_history()
        self.assertEqual(len(history), 3)
    
    def test_get_state_transition(self):
        """状態遷移情報のテスト"""
        self.state_sync.sync_state()
        
        transition = self.state_sync.get_state_transition()
        
        self.assertIn("current", transition)
        self.assertIn("transitions", transition)
    
    def test_is_state_changed(self):
        """状態変更判定のテスト"""
        # 初回はlast_stateがNoneなので変更あり
        self.assertTrue(self.state_sync.is_state_changed())
        
        # sync_state()でlast_stateを更新
        self.state_sync.sync_state()
        
        # 2回目は変更なし（同じ状態）
        self.assertFalse(self.state_sync.is_state_changed())
    
    def test_reset(self):
        """リセットのテスト"""
        self.state_sync.sync_state()
        self.state_sync.reset()
        
        self.assertIsNone(self.state_sync.last_state)
        self.assertEqual(len(self.state_sync.state_history), 0)


class TestMemoryStatus(unittest.TestCase):
    """Memory Statusのテスト"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        self.mock_memory_os = MagicMock()
        self.mock_memory_os.get_stats.return_value = {
            "working": {"count": 10},
            "short_term": {"count": 20},
            "long_term": {"count": 30},
            "semantic": {"count": 40},
            "total_count": 100
        }
        self.mock_memory_os.get_compression_ratio.return_value = 0.5
        self.mock_memory_os.get_last_compression_time.return_value = time.time()
        self.mock_memory_os.get_recent_entries.return_value = []
        self.mock_memory_os.get_growth_rate.return_value = 0.1
        self.mock_memory_os.get_health_status.return_value = "healthy"
        
        from ai_agent.companion.memory_status import MemoryStatus
        self.memory_status = MemoryStatus(self.mock_memory_os)
    
    def test_get_usage_stats(self):
        """使用率統計のテスト"""
        stats = self.memory_status.get_usage_stats()
        
        self.assertIn("working", stats)
        self.assertIn("short_term", stats)
        self.assertIn("long_term", stats)
        self.assertIn("semantic", stats)
        self.assertIn("total", stats)
        self.assertEqual(stats["total"], 100)
    
    def test_get_compression_status(self):
        """圧縮ステータスのテスト"""
        compression_status = self.memory_status.get_compression_status()
        
        self.assertIn("ratio", compression_status)
        self.assertIn("last_compression", compression_status)
        self.assertEqual(compression_status["ratio"], 0.5)
    
    def test_get_recent_entries(self):
        """最近のエントリ取得のテスト"""
        entries = self.memory_status.get_recent_entries(limit=5)
        
        self.assertIsInstance(entries, list)
    
    def test_get_memory_trend(self):
        """メモリ傾向のテスト"""
        trend = self.memory_status.get_memory_trend()
        
        self.assertIn("growth_rate", trend)
        self.assertIn("compression_rate", trend)
        self.assertIn("health", trend)
    
    def test_reset_cache(self):
        """キャッシュリセットのテスト"""
        self.memory_status.get_usage_stats()
        self.memory_status.reset_cache()
        
        self.assertIsNone(self.memory_status._last_export)


class TestNotificationPolicy(unittest.TestCase):
    """Notification Policyのテスト"""
    
    def setUp(self):
        """テスト前のセットアップ"""
        from ai_agent.companion.notification_policy import NotificationPolicy
        self.policy = NotificationPolicy()
    
    def test_should_notify_critical_issue(self):
        """緊急問題の通知判定のテスト"""
        self.assertTrue(self.policy.should_notify("critical_issue"))
    
    def test_should_notify_active_assistance(self):
        """明示的リクエスト時の通知判定のテスト"""
        self.assertTrue(self.policy.should_notify("active_assistance"))
    
    def test_should_not_notify_idle(self):
        """アイドル通知の判定のテスト"""
        self.assertFalse(self.policy.should_notify("idle_notification"))
    
    def test_should_not_notify_passive(self):
        """受動通知の判定のテスト"""
        self.assertFalse(self.policy.should_notify("passive_notification"))
    
    def test_daily_limit(self):
        """1日あたりの上限のテスト"""
        # 5回通知を記録
        for _ in range(5):
            self.policy.record_notification("critical_issue")
        
        # 6回目は通知不可
        self.assertFalse(self.policy.should_notify("critical_issue"))
    
    def test_cooldown(self):
        """冷却時間のテスト"""
        # 冷却時間を0秒に設定
        self.policy.cooldown_seconds = 0
        
        # 通知を記録
        self.policy.record_notification("critical_issue")
        
        # 冷却時間中は通知不可
        self.policy.cooldown_seconds = 999999
        self.assertFalse(self.policy.should_notify("critical_issue"))
        
        # 冷却時間が経過したら通知可能
        self.policy.cooldown_seconds = 0
        self.assertTrue(self.policy.should_notify("critical_issue"))
    
    def test_get_status(self):
        """通知ステータスのテスト"""
        status = self.policy.get_status()
        
        self.assertIn("daily_count", status)
        self.assertIn("max_daily", status)
        self.assertIn("remaining", status)
        self.assertIn("cooldown_remaining", status)
    
    def test_reset_daily_count(self):
        """1日カウントリセットのテスト"""
        # 通知を記録
        self.policy.record_notification("critical_issue")
        
        # リセット
        self.policy.reset_daily_count()
        
        status = self.policy.get_status()
        self.assertEqual(status["daily_count"], 0)
    
    def test_get_recent_notifications(self):
        """最近の通知履歴のテスト"""
        # 通知を記録
        for _ in range(3):
            self.policy.record_notification("critical_issue")
        
        recent = self.policy.get_recent_notifications(limit=2)
        self.assertEqual(len(recent), 2)


if __name__ == "__main__":
    unittest.main()
