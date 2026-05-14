"""
test_user_profile.py - ユーザープロファイルのテスト

Project_044: ユーザープロファイル管理機能のテスト
"""

import pytest
import json
import os
import sys
import tempfile
from pathlib import Path
from unittest.mock import MagicMock, patch

# ai_agent パスを追加
sys.path.insert(0, str(Path(__file__).parent.parent))

from ai_agent.memory.user_profile import UserProfile, UserProfileStore, get_user_profile_store
from ai_agent.memory.user_profile_updater import UserProfileUpdater


class TestUserProfile:
    """UserProfile クラスのテスト"""

    def test_to_dict(self):
        """to_dict メソッドのテスト"""
        profile = UserProfile(user_id="test_user")
        data = profile.to_dict()
        assert data["user_id"] == "test_user"
        assert "preferences" in data
        assert "behavior_patterns" in data
        assert "context" in data
        assert "technical_stack" in data
        assert "project_history" in data
        assert "skill_level" in data
        assert "preferred_theme" in data
        assert "learning_goals" in data
        assert "communication_style" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_from_dict(self):
        """from_dict メソッドのテスト"""
        data = {
            "user_id": "test_user",
            "preferences": {"language": "ja"},
            "behavior_patterns": {"frequent_keywords": ["test"]},
            "context": {"recent_topics": ["test"]},
            "technical_stack": {"frameworks": ["FastAPI"]},
            "project_history": [{"name": "test_project"}],
            "skill_level": "intermediate",
            "preferred_theme": "dark",
            "learning_goals": ["learn_fastapi"],
            "communication_style": "direct",
            "created_at": 1234567890.0,
            "updated_at": 1234567890.0,
        }
        profile = UserProfile.from_dict(data)
        assert profile.user_id == "test_user"
        assert profile.preferences["language"] == "ja"
        assert profile.behavior_patterns["frequent_keywords"] == ["test"]
        assert profile.context["recent_topics"] == ["test"]
        assert profile.technical_stack["frameworks"] == ["FastAPI"]
        assert profile.project_history[0]["name"] == "test_project"
        assert profile.skill_level == "intermediate"
        assert profile.preferred_theme == "dark"
        assert profile.learning_goals == ["learn_fastapi"]
        assert profile.communication_style == "direct"
        assert profile.created_at == 1234567890.0
        assert profile.updated_at == 1234567890.0

    def test_update(self):
        """update メソッドのテスト"""
        profile = UserProfile(user_id="test_user")
        original_updated_at = profile.updated_at
        import time
        time.sleep(0.1)  # updated_at が更新されることを確認するため
        profile.update(preferences={"language": "en"}, skill_level="advanced")
        assert profile.preferences["language"] == "en"
        assert profile.skill_level == "advanced"
        assert profile.updated_at > original_updated_at

    def test_limit_size(self):
        """_limit_size メソッドのテスト"""
        profile = UserProfile(user_id="test_user")
        # 技術スタックの制限
        profile.technical_stack["frameworks"] = [f"framework_{i}" for i in range(15)]
        profile.technical_stack["languages"] = [f"language_{i}" for i in range(15)]
        # プロジェクト履歴の制限
        profile.project_history = [{"name": f"project_{i}"} for i in range(15)]
        
        profile._limit_size()
        
        assert len(profile.technical_stack["frameworks"]) <= 10
        assert len(profile.technical_stack["languages"]) <= 10
        assert len(profile.project_history) <= 10


class TestUserProfileStore:
    """UserProfileStore クラスのテスト"""

    def setup_method(self):
        """各テスト前に一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()
        self.store = UserProfileStore(storage_dir=self.temp_dir)

    def teardown_method(self):
        """各テスト後に一時ディレクトリを削除"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_create_or_update(self):
        """create_or_update メソッドのテスト"""
        profile = self.store.create_or_update("test_user", preferences={"language": "ja"})
        assert profile.user_id == "test_user"
        assert profile.preferences["language"] == "ja"
        
        # 既存のプロファイルを更新
        profile = self.store.create_or_update("test_user", preferences={"language": "en"})
        assert profile.preferences["language"] == "en"

    def test_save_and_get(self):
        """save と get メソッドのテスト"""
        profile = UserProfile(user_id="test_user", preferences={"language": "ja"})
        self.store.save(profile)
        
        retrieved_profile = self.store.get("test_user")
        assert retrieved_profile is not None
        assert retrieved_profile.preferences["language"] == "ja"

    def test_update_preference(self):
        """update_preference メソッドのテスト"""
        profile = UserProfile(user_id="test_user", preferences={"language": "ja"})
        self.store.save(profile)
        
        self.store.update_preference("test_user", "tone", "formal")
        retrieved_profile = self.store.get("test_user")
        assert retrieved_profile.preferences["tone"] == "formal"

    def test_update_behavior_pattern(self):
        """update_behavior_pattern メソッドのテスト"""
        profile = UserProfile(user_id="test_user", behavior_patterns={})
        self.store.save(profile)
        
        self.store.update_behavior_pattern("test_user", "frequent_keywords", ["test"])
        retrieved_profile = self.store.get("test_user")
        assert retrieved_profile.behavior_patterns["frequent_keywords"] == ["test"]

    def test_update_context(self):
        """update_context メソッドのテスト"""
        profile = UserProfile(user_id="test_user", context={})
        self.store.save(profile)
        
        self.store.update_context("test_user", "recent_topics", ["test"])
        retrieved_profile = self.store.get("test_user")
        assert retrieved_profile.context["recent_topics"] == ["test"]

    def test_get_related_memories(self):
        """get_related_memories メソッドのテスト"""
        profile = self.store.create_or_update("test_user")
        
        # memory_os が None の場合
        assert self.store.get_related_memories("test_user", None) == []
        
        # memory_os が get_memories_by_profile メソッドを持つ場合
        mock_memory_os = MagicMock()
        mock_memory_os.get_memories_by_profile.return_value = ["memory1", "memory2"]
        assert self.store.get_related_memories("test_user", mock_memory_os) == ["memory1", "memory2"]


class TestUserProfileUpdater:
    """UserProfileUpdater クラスのテスト"""

    def setup_method(self):
        """各テスト前に一時ディレクトリを作成"""
        self.temp_dir = tempfile.mkdtemp()
        # グローバルな UserProfileStore を一時ディレクトリに置き換え
        self.original_store = get_user_profile_store.__globals__['_user_profile_store']
        get_user_profile_store.__globals__['_user_profile_store'] = UserProfileStore(storage_dir=self.temp_dir)
        self.updater = UserProfileUpdater()

    def teardown_method(self):
        """各テスト後に一時ディレクトリを削除"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        # グローバルな UserProfileStore を元に戻す
        get_user_profile_store.__globals__['_user_profile_store'] = self.original_store

    def test_analyze_and_update(self):
        """analyze_and_update メソッドのテスト"""
        messages = [
            {"role": "user", "content": "```python\nimport fastapi\n```\nPython で FastAPI のプロジェクトを作りたいです。"},
            {"role": "assistant", "content": "FastAPI は素晴らしい選択です。"},
            {"role": "user", "content": "```javascript\nconst express = require('express');\n```\nReact も使いたいです。"},
        ]
        
        profile = self.updater.analyze_and_update("test_user", messages)
        assert profile.user_id == "test_user"
        # technical_stack はコードブロック内のみを検出するため、languages は空の場合がある
        # frameworks は正しく検出されることを確認
        assert "FastAPI" in profile.technical_stack.get("frameworks", [])
        assert "Express" in profile.technical_stack.get("frameworks", [])

    def test_analyze_technical_stack_from_code_blocks(self):
        """_analyze_technical_stack メソッドのテスト（コードブロック内のみ検出）"""
        messages = [
            {"role": "user", "content": "```python\nimport fastapi\nfrom fastapi import FastAPI\n```\n\nこのコードについて教えてください。"},
            {"role": "assistant", "content": "FastAPI のコードですね。"},
            {"role": "user", "content": "```javascript\nconst express = require('express');\n```\n\nExpress についても教えてください。"},
        ]
        
        profile = self.updater.analyze_and_update("test_user", messages)
        assert "FastAPI" in profile.technical_stack.get("frameworks", [])
        assert "Express" in profile.technical_stack.get("frameworks", [])

    def test_analyze_project_history(self):
        """_analyze_project_history メソッドのテスト"""
        messages = [
            {"role": "user", "content": "/path/to/my_project/file.py"},
            {"role": "assistant", "content": "my_project についてのコードですね。"},
            {"role": "user", "content": "cd my_project"},
        ]
        
        profile = self.updater.analyze_and_update("test_user", messages)
        assert len(profile.project_history) > 0
        assert any(p.get("name") == "my_project" for p in profile.project_history)

    def test_apply_feedback(self):
        """_apply_feedback メソッドのテスト"""
        messages = [
            {"role": "user", "content": "詳しく説明してください。"},
            {"role": "user", "content": "英語で書いてください。"},
            {"role": "user", "content": "もっと詳しく。"},
        ]
        
        feedback_prefs = self.updater._apply_feedback(messages)
        assert feedback_prefs.get("detail_level") == "detailed"
        assert feedback_prefs.get("language") == "en"

    def test_recent_messages_weight(self):
        """直近のメッセージの重みが正しく適用されるテスト"""
        messages = [
            {"role": "user", "content": "詳しく説明してください。"},  # 古いメッセージ
            {"role": "user", "content": "簡潔に書いてください。"},  # 古いメッセージ
            {"role": "user", "content": "詳しく説明してください。"},  # 直近のメッセージ
        ]
        
        feedback_prefs = self.updater._apply_feedback(messages)
        # 直近のメッセージが「詳しく」なので、detailed が優先されるはず
        assert feedback_prefs.get("detail_level") == "detailed"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
