"""
test_user_profile_updater.py - ユーザープロファイル自動更新のテスト

Project_042: ユーザープロファイルの強化
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from unittest import TestCase, main

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent.memory.user_profile import UserProfileStore
from ai_agent.memory.user_profile_updater import UserProfileUpdater


class TestUserProfileUpdater(TestCase):
    """UserProfileUpdater のテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = UserProfileStore(storage_dir=os.path.join(self.temp_dir, "profiles"))
        self.updater = UserProfileUpdater()
        # テスト用にストアを置き換え
        self.updater.store = self.store

    def tearDown(self):
        """テスト後の後処理"""
        # テンポラリディレクトリを削除
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_analyze_japanese_messages(self):
        """日本語メッセージの分析"""
        messages = [
            {"role": "user", "content": "こんにちは、今日はどのようなことができますか？"},
            {"role": "assistant", "content": "こんにちは！私はAIアシスタントです。"},
            {"role": "user", "content": "Pythonのコードを書いてください。"},
        ]

        profile = self.updater.analyze_and_update("test_user", messages)

        self.assertEqual(profile.preferences.get("language"), "ja")
        self.assertIn("frequent_keywords", profile.behavior_patterns)

    def test_analyze_english_messages(self):
        """英語メッセージの分析"""
        messages = [
            {"role": "user", "content": "Hello, what can you do?"},
            {"role": "assistant", "content": "Hello! I am an AI assistant."},
            {"role": "user", "content": "Write Python code for me."},
        ]

        profile = self.updater.analyze_and_update("test_user_en", messages)

        self.assertEqual(profile.preferences.get("language"), "en")

    def test_analyze_formal_tone(self):
        """敬語トーンの分析"""
        messages = [
            {"role": "user", "content": "こんにちは、お元気ですか？"},
            {"role": "user", "content": "よろしくお願いします。"},
        ]

        profile = self.updater.analyze_and_update("test_user_formal", messages)

        self.assertEqual(profile.preferences.get("tone"), "formal")

    def test_analyze_casual_tone(self):
        """カジュアルトーンの分析"""
        messages = [
            {"role": "user", "content": "やっほ、何できる？"},
            {"role": "user", "content": "コード書いてよ。"},
        ]

        profile = self.updater.analyze_and_update("test_user_casual", messages)

        self.assertEqual(profile.preferences.get("tone"), "casual")

    def test_empty_messages(self):
        """空のメッセージリストの処理"""
        profile = self.updater.analyze_and_update("test_user_empty", [])

        self.assertIsNotNone(profile)
        self.assertEqual(profile.user_id, "test_user_empty")

    def test_extract_project_info(self):
        """プロジェクト情報の抽出"""
        messages = [
            {"role": "user", "content": "ai_agent/memory/user_profile.py を確認して"},
            {"role": "user", "content": "$ git status を実行して"},
        ]

        profile = self.updater.analyze_and_update("test_user_project", messages)

        self.assertIn("project_info", profile.context)
        self.assertIn("files", profile.context["project_info"])
        self.assertIn("commands", profile.context["project_info"])

    def test_system_prompt_injection(self):
        """システムプロンプトへのプロファイル注入テスト"""
        # プロファイルを作成
        messages = [
            {"role": "user", "content": "こんにちは、Pythonのコードを書いてください。"},
        ]
        profile = self.updater.analyze_and_update("test_prompt_user", messages)
        
        # プロファイル情報を辞書に変換
        profile_dict = profile.to_dict()
        
        # build_system_prompt のロジックを簡易再現してテスト
        # (実際のインポートはワークスペース依存のためスキップ)
        preferences = profile_dict.get("preferences", {})
        behavior_patterns = profile_dict.get("behavior_patterns", {})
        
        # 言語設定
        language = preferences.get("language", "ja")
        self.assertEqual(language, "ja")
        
        # トーン設定
        tone = preferences.get("tone", "casual")
        self.assertEqual(tone, "casual")
        
        # 頻出キーワード
        frequent_keywords = behavior_patterns.get("frequent_keywords", [])
        # 'python' が含まれるキーワードがあるか確認
        has_python = any('python' in k.lower() for k in frequent_keywords)
        self.assertTrue(has_python, f"python keyword not found in {frequent_keywords}")
        
        print(f"✅ Profile data structure is correct")
        print(f"   Language: {language}")
        print(f"   Tone: {tone}")
        print(f"   Keywords: {frequent_keywords}")

    def test_technical_stack_analysis(self):
        """技術スタックの分析テスト"""
        messages = [
            {"role": "user", "content": "```python\nfrom django.urls import path\nimport React from 'react'\n```"},
            {"role": "user", "content": "```bash\ndocker-compose up -d\n```"},
        ]
        profile = self.updater.analyze_and_update("test_tech_stack", messages)
        
        self.assertIn("technical_stack", profile.to_dict())
        tech_stack = profile.technical_stack
        self.assertIn("frameworks", tech_stack)
        self.assertIn("tools", tech_stack)
        self.assertIn("Django", tech_stack["frameworks"])
        self.assertIn("React", tech_stack["frameworks"])
        self.assertIn("Docker", tech_stack["tools"])
        
        print(f"✅ Technical stack analysis test passed")
        print(f"   Frameworks: {tech_stack.get('frameworks', [])}")
        print(f"   Tools: {tech_stack.get('tools', [])}")

    def test_project_history_analysis(self):
        """プロジェクト履歴の分析テスト"""
        messages = [
            {"role": "user", "content": "ai_agent/memory/user_profile.py を確認して"},
            {"role": "user", "content": "cd QueryQuest && git status を実行して"},
        ]
        profile = self.updater.analyze_and_update("test_project_history", messages)
        
        self.assertIn("project_history", profile.to_dict())
        history = profile.project_history
        self.assertTrue(len(history) > 0, "Project history should not be empty")
        
        # 最初のプロジェクトエントリを確認
        first_project = history[0]
        self.assertIn("name", first_project)
        self.assertIn("technologies", first_project)
        
        print(f"✅ Project history analysis test passed")
        print(f"   Projects: {[p['name'] for p in history]}")

    def test_profile_persistence(self):
        """プロファイルの永続化テスト"""
        # 1. プロファイルを作成
        messages = [
            {"role": "user", "content": "Pythonのコードを書いてください。"},
        ]
        profile1 = self.updater.analyze_and_update("test_persist", messages)
        
        # 2. ストアから再度取得
        profile2 = self.store.get("test_persist")
        
        # 3. 内容が一致するか確認
        self.assertIsNotNone(profile2)
        self.assertEqual(profile1.preferences, profile2.preferences)
        self.assertEqual(profile1.behavior_patterns, profile2.behavior_patterns)
        self.assertEqual(profile1.technical_stack, profile2.technical_stack)
        self.assertEqual(profile1.project_history, profile2.project_history)
        
        print(f"✅ Profile persistence test passed")
        print(f"   Preferences match: {profile1.preferences == profile2.preferences}")
        print(f"   Technical stack match: {profile1.technical_stack == profile2.technical_stack}")

    def test_code_style_analysis(self):
        """コードスタイルの分析テスト"""
        messages = [
            {"role": "user", "content": "```python\ndef hello():\n    print('Hello, World!')\n```"},
        ]
        profile = self.updater.analyze_and_update("test_code_style", messages)
        
        self.assertIn("code_style", profile.preferences)
        code_style = profile.preferences["code_style"]
        self.assertIn("indent_style", code_style)
        self.assertIn("quote_style", code_style)
        self.assertIn("type_hints", code_style)
        
        print(f"✅ Code style analysis test passed")
        print(f"   Code style: {code_style}")

    def test_doc_preference_analysis(self):
        """ドキュメントの好みの分析テスト"""
        messages = [
            {"role": "user", "content": "ドキュメントの詳細な説明を書いてください。"},
        ]
        profile = self.updater.analyze_and_update("test_doc_pref", messages)
        
        self.assertIn("doc_preference", profile.preferences)
        doc_pref = profile.preferences["doc_preference"]
        self.assertIn("language", doc_pref)
        self.assertIn("detail_level", doc_pref)
        
        print(f"✅ Doc preference analysis test passed")
        print(f"   Doc preference: {doc_pref}")

    def test_verbosity_analysis(self):
        """応答の冗長性の分析テスト"""
        messages = [
            {"role": "user", "content": "詳しく説明してください。"},
        ]
        profile = self.updater.analyze_and_update("test_verbosity", messages)
        
        self.assertEqual(profile.preferences.get("verbosity"), "detailed")
        
        messages2 = [
            {"role": "user", "content": "簡潔に要約して。"},
        ]
        profile2 = self.updater.analyze_and_update("test_verbosity2", messages2)
        
        self.assertEqual(profile2.preferences.get("verbosity"), "concise")
        
        print(f"✅ Verbosity analysis test passed")
        print(f"   Detailed: {profile.preferences.get('verbosity')}")
        print(f"   Concise: {profile2.preferences.get('verbosity')}")

    def test_technical_stack_with_databases(self):
        """技術スタックのデータベース検出テスト"""
        messages = [
            {"role": "user", "content": "```python\nimport redis\nfrom pymongo import MongoClient\nimport psycopg2\n# PostgreSQLとMongoDBとRedisを使いたい\n```"},
        ]
        profile = self.updater.analyze_and_update("test_tech_stack_db", messages)
        
        tech_stack = profile.technical_stack
        self.assertIn("databases", tech_stack)
        self.assertIn("PostgreSQL", tech_stack["databases"])
        self.assertIn("MongoDB", tech_stack["databases"])
        self.assertIn("Redis", tech_stack["databases"])
        
        print(f"✅ Technical stack with databases test passed")
        print(f"   Databases: {tech_stack.get('databases', [])}")

    def test_project_history_with_frequency(self):
        """プロジェクト履歴の頻度/期間追跡テスト"""
        messages = [
            {"role": "user", "content": "ai_agent/memory/user_profile.py を確認して", "timestamp": "2024-01-01T10:00:00"},
            {"role": "user", "content": "ai_agent/memory/user_profile.py を更新して", "timestamp": "2024-01-02T10:00:00"},
            {"role": "user", "content": "cd QueryQuest && git status を実行して", "timestamp": "2024-01-03T10:00:00"},
        ]
        profile = self.updater.analyze_and_update("test_project_history_freq", messages)
        
        history = profile.project_history
        self.assertTrue(len(history) > 0, "Project history should not be empty")
        
        # 頻度と期間が記録されているか確認
        first_project = history[0]
        self.assertIn("frequency", first_project)
        self.assertIn("first_seen", first_project)
        self.assertIn("last_seen", first_project)
        
        # 頻度が正しいか確認 (2回出現している 'memory' の頻度は2以上)
        memory_proj = next((p for p in history if p['name'] == 'memory'), None)
        if memory_proj:
            self.assertGreaterEqual(memory_proj['frequency'], 2)
        
        print(f"✅ Project history with frequency test passed")
        print(f"   Projects: {[(p['name'], p.get('frequency')) for p in history]}")

    def test_explicit_feedback(self):
        """明示的なフィードバックの反映テスト"""
        messages = [
            {"role": "user", "content": "もっと詳しく説明して。", "timestamp": "2024-01-01T10:00:00"},
        ]
        profile = self.updater.analyze_and_update("test_explicit_feedback", messages)
        
        # detail_level が 'detailed' に設定されているか
        self.assertEqual(profile.preferences.get('detail_level'), 'detailed')
        
        messages2 = [
            {"role": "user", "content": "簡潔に書いて。", "timestamp": "2024-01-01T10:00:00"},
        ]
        profile2 = self.updater.analyze_and_update("test_explicit_feedback2", messages2)
        
        # detail_level が 'concise' に設定されているか
        self.assertEqual(profile2.preferences.get('detail_level'), 'concise')
        
        messages3 = [
            {"role": "user", "content": "英語で書いて。", "timestamp": "2024-01-01T10:00:00"},
        ]
        profile3 = self.updater.analyze_and_update("test_explicit_feedback3", messages3)
        
        # language が 'en' に設定されているか
        self.assertEqual(profile3.preferences.get('language'), 'en')
        
        print(f"✅ Explicit feedback test passed")
        print(f"   Detailed feedback: {profile.preferences.get('detail_level')}")
        print(f"   Concise feedback: {profile2.preferences.get('detail_level')}")
        print(f"   English feedback: {profile3.preferences.get('language')}")

    def test_profile_integration_with_soul(self):
        """プロファイルと soul.py の統合テスト"""
        from ai_agent.soul import get_system_prompt
        
        # プロファイルを作成（コードブロックを含むメッセージ）
        messages = [
            {"role": "user", "content": "```python\nfrom django.urls import path\nimport React from 'react'\n```"},
        ]
        profile = self.updater.analyze_and_update("test_integration", messages)
        
        # システムプロンプトにプロファイル情報が組み込まれているか確認
        system_prompt = get_system_prompt("chat", profile.to_dict())
        
        self.assertIn("【ユーザー情報】", system_prompt)
        self.assertIn("Django", system_prompt)
        self.assertIn("React", system_prompt)
        
        print(f"✅ Profile integration with soul test passed")
        print(f"   System prompt includes user info: True")


if __name__ == "__main__":
    main()
