# ai_agent/workspace/session_registry.py

import json
import os
from datetime import datetime
from typing import Optional


class SessionRegistry:
    """
    セッション状態を管理するレジストリ
    
    役割:
    - セッションのサマリー管理
    - 最近のセッション一覧
    - ユーザー意図の追跡
    - アクティブゴールの管理
    """
    
    def __init__(self, path: str = "session_registry.json"):
        self.path = path
        self.data = self._load()
    
    def _load(self) -> dict:
        """レジストリファイルを読み込み"""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                return json.load(f)
        return self._default_data()
    
    def _default_data(self) -> dict:
        """デフォルトのデータ構造"""
        return {
            "sessions": []
        }
    
    def save(self):
        """レジストリを保存"""
        self.data["last_updated"] = datetime.now().isoformat()
        with open(self.path, "w", encoding="utf-8") as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
    
    def get_session(self, chat_id: str) -> Optional[dict]:
        """chat_id でセッションを取得"""
        for session in self.data.get("sessions", []):
            if session.get("chat_id") == chat_id:
                return session
        return None
    
    def get_recent_sessions(self, limit: int = 5) -> list:
        """最近のセッションを取得（updated_at 降順）"""
        sessions = self.data.get("sessions", [])
        sorted_sessions = sorted(
            sessions,
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )
        return sorted_sessions[:limit]
    
    def update_session(self, chat_id: str, title: str, summary: str, 
                       recent_topics: list, active_goals: list, 
                       last_user_intent: str) -> dict:
        """セッションを更新（存在すれば更新、なければ新規作成）"""
        # 既存セッションを検索
        existing = None
        for session in self.data.get("sessions", []):
            if session.get("chat_id") == chat_id:
                existing = session
                break
        
        if existing:
            # 更新
            existing["title"] = title
            existing["summary"] = summary
            existing["recent_topics"] = recent_topics[-10:]  # 最大10件
            existing["active_goals"] = active_goals
            existing["last_user_intent"] = last_user_intent
            existing["updated_at"] = datetime.now().isoformat()
        else:
            # 新規作成
            new_session = {
                "chat_id": chat_id,
                "title": title,
                "workspace_id": "queryquest_project",
                "summary": summary,
                "recent_topics": recent_topics[-10:],
                "active_goals": active_goals,
                "last_user_intent": last_user_intent,
                "updated_at": datetime.now().isoformat()
            }
            self.data["sessions"].append(new_session)
        
        self.save()
        return existing or new_session
    
    def find_session_by_title(self, title_keyword: str) -> Optional[dict]:
        """タイトルでセッションを検索（部分一致）"""
        sessions = self.get_recent_sessions(limit=20)
        for session in sessions:
            if title_keyword.lower() in session.get("title", "").lower():
                return session
        return None
    
    def add_session(self, chat_id: str, title: str, summary: str = "",
                    recent_topics: list = None, active_goals: list = None,
                    last_user_intent: str = "") -> dict:
        """セッションを新規追加"""
        new_session = {
            "chat_id": chat_id,
            "title": title,
            "workspace_id": "queryquest_project",
            "summary": summary,
            "recent_topics": recent_topics or [],
            "active_goals": active_goals or [],
            "last_user_intent": last_user_intent,
            "updated_at": datetime.now().isoformat()
        }
        self.data["sessions"].append(new_session)
        self.save()
        return new_session
