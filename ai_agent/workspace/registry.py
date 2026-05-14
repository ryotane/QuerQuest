# ai_agent/workspace/registry.py

import json
import os
from datetime import datetime

class WorkspaceRegistry:
    """
    ワークスペースの状態を管理するレジストリ
    
    役割:
    - workspace_registry.json の読み書き
    - ワークスペースコンテキストの生成
    """
    
    def __init__(self, path: str = "workspace_registry.json"):
        self.path = path
        self.registry = self._load()
    
    def _load(self) -> dict:
        """レジストリファイルを読み込み"""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_registry()
    
    def _default_registry(self) -> dict:
        """デフォルトのレジストリ構造"""
        return {
            "workspace_id": "default",
            "last_updated": datetime.now().isoformat(),
            "summary": "",
            "recent_topics": [],
            "active_goals": [],
            "recent_decisions": [],
            "related_chats": []
        }
    
    def save(self):
        """レジストリを保存"""
        self.registry["last_updated"] = datetime.now().isoformat()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.registry, f, indent=2, ensure_ascii=False)
    
    def get_context(self) -> str:
        """ワークスペースコンテキストを生成"""
        from ai_agent.workspace.context import generate_workspace_context
        # Project_08: workspace hydration時にplan compression適用
        if self.registry.get("active_goals"):
            self.registry["active_goals"] = self.registry["active_goals"][:1]
        return generate_workspace_context(self.registry)
    
    def update_summary(self, summary: str):
        """サマリーを更新"""
        self.registry["summary"] = summary
        self.save()
    
    def add_topic(self, topic: str):
        """トピックを追加"""
        if topic not in self.registry["recent_topics"]:
            self.registry["recent_topics"].append(topic)
            # 最大10件に制限
            self.registry["recent_topics"] = self.registry["recent_topics"][-10:]
        self.save()
