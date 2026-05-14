"""
test_profile_lifecycle.py - プロファイルライフサイクルテスト

Project_042: ユーザープロファイルの強化
プロファイルの作成→更新→応答生成→連携の全フローを検証
"""

import sys
import os
import tempfile
from pathlib import Path
from unittest import TestCase, main

# モジュールパスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent.memory.user_profile import UserProfileStore, get_user_profile_store
from ai_agent.memory.user_profile_updater import UserProfileUpdater
from ai_agent.memory.memory_os import MemoryOS, MemoryEntry, MemoryLayer


class TestProfileLifecycle(TestCase):
    """プロファイルライフサイクルテスト"""

    def setUp(self):
        """テスト前の準備"""
        self.temp_dir = tempfile.mkdtemp()
        self.profile_store = UserProfileStore(storage_dir=os.path.join(self.temp_dir, "profiles"))
        self.updater = UserProfileUpdater()
        self.updater.store = self.profile_store
        self.memory_os = MemoryOS()

    def tearDown(self):
        """テスト後の後処理"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_lifecycle(self):
        """全フローテスト"""
        # 1. プロファイル作成
        messages = [
            {"role": "user", "content": "こんにちは、Pythonのコードを書いてください。"},
            {"role": "assistant", "content": "はい、Pythonのコードを書きます。"},
            {"role": "user", "content": "ありがとうございます。"},
        ]
        profile = self.updater.analyze_and_update("test_user", messages)
        
        # 2. プロファイル情報確認
        self.assertEqual(profile.preferences.get("language"), "ja")
        self.assertEqual(profile.preferences.get("tone"), "casual")
        self.assertIn("frequent_keywords", profile.behavior_patterns)
        
        # 3. MemoryOS にプロファイル関連のエントリを保存
        entry = MemoryEntry(
            id="mem_profile_test",
            content="ユーザーはPythonを好む",
            metadata={"source": "conversation", "type": "preference"},
            importance=0.8,
            layer=MemoryLayer.WORKING,
            tags=["preference", "python"],
            user_profile_id="test_user",
        )
        self.memory_os.store(entry)
        
        # 4. MemoryOS からプロファイル関連のメモリを取得
        results = self.memory_os.get_memories_by_profile("test_user")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].content, "ユーザーはPythonを好む")
        
        # 5. システムプロンプトにプロファイル情報を注入
        profile_dict = profile.to_dict()
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
        has_python = any('python' in k.lower() for k in frequent_keywords)
        self.assertTrue(has_python)
        
        print(f"✅ Full lifecycle test passed")
        print(f"   Language: {language}")
        print(f"   Tone: {tone}")
        print(f"   Keywords: {frequent_keywords}")
        print(f"   Memory entries: {len(results)}")
    
    def test_memory_update_on_profile_change(self):
        """プロファイル更新時のメモリ更新テスト"""
        # 1. プロファイル作成
        messages = [
            {"role": "user", "content": "こんにちは、Pythonのコードを書いてください。"},
        ]
        profile = self.updater.analyze_and_update("test_user", messages)
        
        # 2. MemoryOS にプロファイル関連のエントリを保存
        entry = MemoryEntry(
            id="mem_profile_test",
            content="ユーザーはPythonを好む",
            metadata={"source": "conversation", "type": "preference"},
            importance=0.8,
            layer=MemoryLayer.WORKING,
            tags=["preference", "python"],
            user_profile_id="test_user",
        )
        self.memory_os.store(entry)
        
        # 3. プロファイル更新時にメモリも更新
        updated_count = self.updater.update_memory("test_user", self.memory_os)
        self.assertEqual(updated_count, 1)
        
        # 4. メモリが更新されたか確認
        results = self.memory_os.get_memories_by_profile("test_user")
        self.assertEqual(len(results), 1)
        self.assertIn("language", results[0].metadata)
        self.assertIn("tone", results[0].metadata)
        self.assertIn("frequent_keywords", results[0].metadata)
        
        print(f"✅ Memory update on profile change test passed")
        print(f"   Updated count: {updated_count}")
        print(f"   Metadata: {results[0].metadata}")

    def test_profile_effectiveness_in_chat(self):
        """実際のチャットでプロファイルが効いているか確認するテスト"""
        # シミュレーション: ユーザーが特定の技術スタックと好みを示すチャット
        messages = [
            {"role": "user", "content": "```typescript\n// TypeScriptでReactを書く\nimport React from 'react'\nimport { useState } from 'react'\n```"},
            {"role": "assistant", "content": "はい、ReactとTypeScriptのプロジェクトを作成します。"},
            {"role": "user", "content": "コードは簡潔に書いてください。"},
            {"role": "assistant", "content": "はい、簡潔なコードを提供します。"},
            {"role": "user", "content": "ドキュメントは日本語でお願いします。"},
        ]
        
        # プロファイルを分析
        profile = self.updater.analyze_and_update("chat_test_user", messages)
        
        # プロファイルが正しく抽出されているか確認
        self.assertEqual(profile.preferences.get("language"), "ja")
        self.assertIn("frameworks", profile.technical_stack)
        self.assertIn("React", profile.technical_stack["frameworks"])
        self.assertIn("languages", profile.technical_stack)
        self.assertIn("TypeScript", profile.technical_stack["languages"])
        self.assertEqual(profile.preferences.get("verbosity"), "concise")
        self.assertEqual(profile.preferences.get("doc_preference", {}).get("language"), "ja")
        
        # MemoryOS にプロファイル関連のエントリを保存
        entry = MemoryEntry(
            id="mem_chat_test",
            content="ユーザーはReactとTypeScriptを好み、簡潔なコードを好む",
            metadata={"source": "conversation", "type": "preference"},
            importance=0.9,
            layer=MemoryLayer.WORKING,
            tags=["react", "typescript", "concise"],
            user_profile_id="chat_test_user",
        )
        self.memory_os.store(entry)
        
        # MemoryOS からプロファイル関連のメモリを取得
        results = self.memory_os.get_memories_by_profile("chat_test_user")
        self.assertEqual(len(results), 1)
        
        print(f"✅ Profile effectiveness in chat test passed")
        print(f"   Language: {profile.preferences.get('language')}")
        print(f"   Frameworks: {profile.technical_stack.get('frameworks', [])}")
        print(f"   Verbosity: {profile.preferences.get('verbosity')}")
        print(f"   Doc Language: {profile.preferences.get('doc_preference', {}).get('language')}")
        print(f"   Memory entries: {len(results)}")


if __name__ == "__main__":
    main()
