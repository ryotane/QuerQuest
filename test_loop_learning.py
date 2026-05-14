"""
Project_039: Loop Learning Test

自律的学習（Self-Reflection）のテスト
- LoopFailureLogger: ループ失敗ログ記録
- LoopPatternAnalyzer: ループパターン分析
- LoopAvoidancePromptInjector: ループ回避プロンプト注入
"""

import os
import sys
import json
import tempfile
import unittest

# ai_agentディレクトリをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from ai_agent.self_improve.loop_logger import LoopFailureLogger
from ai_agent.self_improve.loop_analyzer import LoopPatternAnalyzer
from ai_agent.self_improve.loop_avoidance import LoopAvoidancePromptInjector


class TestLoopFailureLogger(unittest.TestCase):
    """LoopFailureLoggerのテスト"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.temp_dir, "loop_failures.jsonl")
        self.logger = LoopFailureLogger(log_path=self.log_path)

    def tearDown(self):
        # テスト後のクリーンアップ
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        os.rmdir(self.temp_dir)

    def test_log_loop_failure(self):
        """ループ失敗の記録テスト"""
        record = self.logger.log_loop_failure(
            query="今日の天気は？",
            loop_type="infinite_loop",
            reasoning_history=["推論1", "推論2", "推論3"],
            detected_pattern="high_similarity",
        )
        
        self.assertEqual(record["query"], "今日の天気は？")
        self.assertEqual(record["loop_type"], "infinite_loop")
        self.assertEqual(len(record["reasoning_history"]), 3)
        self.assertEqual(record["detected_pattern"], "high_similarity")
        
        # ファイルに記録されているか確認
        self.assertTrue(os.path.exists(self.log_path))
        with open(self.log_path, "r", encoding="utf-8") as f:
            lines = f.readlines()
        self.assertEqual(len(lines), 1)

    def test_get_recent_failures(self):
        """最近の失敗ログ取得テスト"""
        # 複数の失敗を記録
        for i in range(5):
            self.logger.log_loop_failure(
                query=f"テスト{i}",
                loop_type="infinite_loop",
                reasoning_history=["推論"],
            )
        
        # 最近の3件を取得
        recent = self.logger.get_recent_failures(count=3)
        self.assertEqual(len(recent), 3)
        
        # 最近の順にソートされているか確認
        for i in range(len(recent) - 1):
            self.assertGreaterEqual(
                recent[i]["timestamp"],
                recent[i + 1]["timestamp"],
            )


class TestLoopPatternAnalyzer(unittest.TestCase):
    """LoopPatternAnalyzerのテスト"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.temp_dir, "loop_failures.jsonl")
        self.analyzer = LoopPatternAnalyzer(log_path=self.log_path)
        
        # テスト用のログを作成
        self._create_test_logs()

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        os.rmdir(self.temp_dir)

    def _create_test_logs(self):
        """テスト用のログを作成"""
        logger = LoopFailureLogger(log_path=self.log_path)
        
        # infinite_loopの失敗を複数記録
        for i in range(5):
            logger.log_loop_failure(
                query="今日の天気は？",
                loop_type="infinite_loop",
                reasoning_history=["推論"],
            )
        
        # recursive_file_readの失敗を記録
        for i in range(3):
            logger.log_loop_failure(
                query="コードレビューして",
                loop_type="recursive_file_read",
                reasoning_history=["推論"],
            )

    def test_analyze(self):
        """パターン分析テスト"""
        result = self.analyzer.analyze()
        
        self.assertEqual(result["total_failures"], 8)
        self.assertIn("infinite_loop", result["loop_types"])
        self.assertIn("recursive_file_read", result["loop_types"])
        self.assertEqual(result["loop_types"]["infinite_loop"], 5)
        self.assertEqual(result["loop_types"]["recursive_file_read"], 3)

    def test_get_loop_avoidance_instructions(self):
        """ループ回避指示生成テスト"""
        instructions = self.analyzer.get_loop_avoidance_instructions()
        
        # infinite_loopが3回以上発生しているため、指示が生成される
        self.assertTrue(len(instructions) > 0)
        
        # 指示に「無限ループ」が含まれているか確認
        infinite_loop_instruction = [
            inst for inst in instructions if "無限ループ" in inst
        ]
        self.assertTrue(len(infinite_loop_instruction) > 0)


class TestLoopAvoidancePromptInjector(unittest.TestCase):
    """LoopAvoidancePromptInjectorのテスト"""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.log_path = os.path.join(self.temp_dir, "loop_failures.jsonl")
        self.analyzer = LoopPatternAnalyzer(log_path=self.log_path)
        self.injector = LoopAvoidancePromptInjector(
            analyzer=self.analyzer,
            enabled=True,
        )
        
        # テスト用のログを作成
        self._create_test_logs()

    def tearDown(self):
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
        os.rmdir(self.temp_dir)

    def _create_test_logs(self):
        """テスト用のログを作成"""
        logger = LoopFailureLogger(log_path=self.log_path)
        
        # infinite_loopの失敗を複数記録
        for i in range(5):
            logger.log_loop_failure(
                query="今日の天気は？",
                loop_type="infinite_loop",
                reasoning_history=["推論"],
            )

    def test_inject(self):
        """プロンプト注入テスト"""
        original_prompt = "あなたは便利なアシスタントです。"
        injected_prompt = self.injector.inject(original_prompt)
        
        # 注入された指示が含まれているか確認
        self.assertIn("【ループ回避指示】", injected_prompt)
        self.assertIn("無限ループ", injected_prompt)
        
        # 元のプロンプトが含まれているか確認
        self.assertIn(original_prompt, injected_prompt)

    def test_disable(self):
        """無効化テスト"""
        self.injector.disable()
        original_prompt = "あなたは便利なアシスタントです。"
        injected_prompt = self.injector.inject(original_prompt)
        
        # 無効化されているため、プロンプトは変更されていない
        self.assertEqual(injected_prompt, original_prompt)


if __name__ == "__main__":
    unittest.main()
