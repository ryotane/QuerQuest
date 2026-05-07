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
    
    def find_sessions_by_keywords(self, keywords: list, limit: int = 10) -> list:
        """
        キーワードでセッションを検索（複数キーワード対応）
        
        recent_topics と summary から部分一致で検索。
        関連度スコア付きで返す。
        
        Args:
            keywords: 検索キーワードのリスト
            limit: 返す最大件数
        
        Returns:
            [(session, score), ...] 関連度順にソート
        """
        sessions = self.data.get("sessions", [])
        results = []
        
        for session in sessions:
            score = 0
            
            # タイトルでの検索（重み高）
            title = session.get("title", "").lower()
            for kw in keywords:
                if kw.lower() in title:
                    score += 3
            
            # トピックでの検索（重み中）
            topics = session.get("recent_topics", [])
            for topic in topics:
                for kw in keywords:
                    if kw.lower() in topic.lower():
                        score += 2
            
            # サマリーでの検索（重み低）
            summary = session.get("summary", "").lower()
            for kw in keywords:
                if kw.lower() in summary:
                    score += 1
            
            if score > 0:
                results.append((session, score))
        
        # 関連度でソート（降順）、同点なら更新日でソート
        results.sort(key=lambda x: (x[1], x[0].get("updated_at", "")), 
                     reverse=True)
        
        return results[:limit]
    
    def merge_sessions(self, target_chat_id: str, source_sessions: list) -> dict:
        """
        複数のセッションを 1 つにマージ（知見の統合）
        
        既存セッションに上書きではなく、知見をマージ。
        マージ前のセッションは archive フォルダへ移動。
        安定化ルールを適用。
        
        Args:
            target_chat_id: 対象となる既存セッションの chat_id
            source_sessions: マージするセッションのリスト
        
        Returns:
            マージ後のセッションデータ
        """
        import shutil
        import os
        from ai_agent.workspace.memory_stabilization import SummaryCompressor, ContextDeduplicator
        
        # 対象セッションを検索
        target = None
        target_idx = None
        for i, session in enumerate(self.data.get("sessions", [])):
            if session.get("chat_id") == target_chat_id:
                target = session
                target_idx = i
                break
        
        if not target:
            raise ValueError(f"Target session not found: {target_chat_id}")
        
        # マージ前のセッションを archive へ移動
        archive_dir = os.path.join(os.path.dirname(self.path), "archive")
        os.makedirs(archive_dir, exist_ok=True)
        
        archived_ids = []
        for session in source_sessions:
            chat_id = session.get("chat_id")
            if chat_id != target_chat_id:
                # archive ファイルへ保存
                archive_path = os.path.join(archive_dir, f"{chat_id}.json")
                with open(archive_path, "w", encoding="utf-8") as f:
                    json.dump(session, f, indent=2, ensure_ascii=False)
                archived_ids.append(chat_id)
        
        # 安定化モジュール
        compressor = SummaryCompressor()
        deduplicator = ContextDeduplicator()
        
        # 知見のマージ
        merged_summary = target.get("summary", "")
        merged_topics = list(set(target.get("recent_topics", [])))
        merged_goals = target.get("active_goals", [])
        merged_next_actions = target.get("next_actions", [])
        
        for session in source_sessions:
            if session.get("chat_id") == target_chat_id:
                continue
            
            # サマリーを結合（重複除去）
            if session.get("summary"):
                merged_summary += f"\n\n[元セッション {session.get('title', 'Untitled')}] {session['summary']}"
            
            # トピックをマージ
            for topic in session.get("recent_topics", []):
                if topic not in merged_topics:
                    merged_topics.append(topic)
            
            # ゴールをマージ
            for goal in session.get("active_goals", []):
                if goal not in merged_goals:
                    merged_goals.append(goal)
            
            # next_actions をマージ
            for action in session.get("next_actions", []):
                if action not in merged_next_actions:
                    merged_next_actions.append(action)
        
        # 安定化ルールを適用
        merged_summary = compressor.compress_summary(merged_summary, 500)
        merged_topics = deduplicator.deduplicate_topics(merged_topics)
        merged_goals = compressor.compress_goals(merged_goals, 300)
        
        # 更新
        target["summary"] = merged_summary
        target["recent_topics"] = merged_topics[-20:]  # 最大 20 件
        target["active_goals"] = merged_goals
        target["next_actions"] = merged_next_actions
        target["merged_from"] = archived_ids
        target["merged_at"] = datetime.now().isoformat()
        target["updated_at"] = datetime.now().isoformat()
        
        self.save()
        
        return target
    
    def get_project_sessions(self, workspace_id: str) -> list:
        """
        特定のワークスペースに属する全セッションを取得
        
        Args:
            workspace_id: ワークスペース ID
        
        Returns:
            該当する全セッションのリスト
        """
        return [
            session for session in self.data.get("sessions", [])
            if session.get("workspace_id") == workspace_id
        ]
    
    def get_all_next_actions(self, workspace_id: str = None) -> list:
        """
        全セッションの next_actions を集約
        
        Args:
            workspace_id: ワークスペース ID（指定時はそのワークスペースのみ）
        
        Returns:
            集約された next_actions のリスト
        """
        sessions = self.data.get("sessions", [])
        
        if workspace_id:
            sessions = [
                s for s in sessions if s.get("workspace_id") == workspace_id
            ]
        
        all_actions = []
        for session in sessions:
            for action in session.get("next_actions", []):
                if action not in all_actions:
                    all_actions.append(action)
        
        return all_actions
