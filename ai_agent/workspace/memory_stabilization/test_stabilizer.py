# ai_agent/workspace/memory_stabilization/test_stabilizer.py

"""
Memory Stabilization Module のテスト
"""

import unittest
from .stabilizer import MemoryStabilizer
from .injection_guard import InjectionGuard
from .context_deduplicator import ContextDeduplicator
from .summary_compressor import SummaryCompressor
from .memory_separation import MemorySeparation


class TestInjectionGuard(unittest.TestCase):
    """InjectionGuard のテスト"""
    
    def setUp(self):
        self.guard = InjectionGuard()
    
    def test_hash_context(self):
        """context のハッシュ値が生成される"""
        context = "test context"
        h1 = self.guard.hash_context(context)
        h2 = self.guard.hash_context(context)
        self.assertEqual(h1, h2)
    
    def test_is_already_injected(self):
        """注入済み context が検出される"""
        context = "test context"
        self.assertFalse(self.guard.is_already_injected(context))
        self.guard.mark_injected(context)
        self.assertTrue(self.guard.is_already_injected(context))
    
    def test_detect_recursive_injection(self):
        """循環参照が検出される"""
        context = "test context"
        self.guard._context_chain.append(context)
        self.assertTrue(self.guard.detect_recursive_injection(context))


class TestContextDeduplicator(unittest.TestCase):
    """ContextDeduplicator のテスト"""
    
    def setUp(self):
        self.dedup = ContextDeduplicator()
    
    def test_is_duplicate(self):
        """重複が検出される"""
        content = "test content"
        self.assertFalse(self.dedup.is_duplicate(content))
        self.dedup.mark_seen(content)
        self.assertTrue(self.dedup.is_duplicate(content))
    
    def test_deduplicate_list(self):
        """リストの重複が排除される"""
        items = ["a", "b", "a", "c", "b"]
        result = self.dedup.deduplicate_list(items)
        self.assertEqual(result, ["a", "b", "c"])
    
    def test_deduplicate_topics(self):
        """トピックの重複が排除される（大文字小文字区別なし）"""
        topics = ["Python", "python", "Python", "Java"]
        result = self.dedup.deduplicate_topics(topics)
        self.assertEqual(len(result), 2)  # Python, Java


class TestSummaryCompressor(unittest.TestCase):
    """SummaryCompressor のテスト"""
    
    def setUp(self):
        self.compressor = SummaryCompressor()
    
    def test_compress_summary_short(self):
        """短い要約はそのまま返される"""
        summary = "short"
        result = self.compressor.compress_summary(summary, 100)
        self.assertEqual(result, summary)
    
    def test_compress_summary_long(self):
        """長い要約は圧縮される"""
        summary = "a" * 1000
        result = self.compressor.compress_summary(summary, 500)
        self.assertLessEqual(len(result), 500)
    
    def test_compress_topics(self):
        """トピックが圧縮される"""
        topics = [f"topic_{i}" for i in range(50)]
        result = self.compressor.compress_topics(topics, 100)
        self.assertLessEqual(len(', '.join(result)), 100)


class TestMemorySeparation(unittest.TestCase):
    """MemorySeparation のテスト"""
    
    def setUp(self):
        self.separation = MemorySeparation()
    
    def test_is_active_session_recent(self):
        """最近のセッションは active とみなされる"""
        from datetime import datetime, timedelta
        session = {
            "updated_at": (datetime.now() - timedelta(days=1)).isoformat()
        }
        self.assertTrue(self.separation.is_active_session(session))
    
    def test_is_active_session_old(self):
        """古いセッションは active でない"""
        from datetime import datetime, timedelta
        session = {
            "updated_at": (datetime.now() - timedelta(days=10)).isoformat()
        }
        self.assertFalse(self.separation.is_active_session(session))


class TestMemoryStabilizer(unittest.TestCase):
    """MemoryStabilizer のテスト"""
    
    def setUp(self):
        self.stabilizer = MemoryStabilizer()
    
    def test_is_context_safe(self):
        """安全な context が判定される"""
        context = "safe context"
        self.assertTrue(self.stabilizer.is_context_safe(context))
    
    def test_is_context_too_long(self):
        """長すぎる context は安全でないと判定される"""
        context = "a" * 10000
        self.assertFalse(self.stabilizer.is_context_safe(context))
    
    def test_validate_session_data(self):
        """セッションデータが検証される"""
        session_data = {
            "summary": "a" * 1000,
            "recent_topics": ["topic"] * 50,
            "active_goals": ["goal"] * 50
        }
        result = self.stabilizer.validate_session_data(session_data)
        self.assertLessEqual(len(result["summary"]), 500)
        self.assertLessEqual(len(result["recent_topics"]), 10)


if __name__ == "__main__":
    unittest.main()
