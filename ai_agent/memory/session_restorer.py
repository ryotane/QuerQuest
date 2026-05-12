"""
session_restorer.py - セッション履歴復元器

Project_040: 記憶の継承機能
新規チャット開始時に、関連する過去のセッション履歴を検索して復元。
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional

from .project_history import ProjectHistoryStore


class SessionRestorer:
    """
    セッション履歴復元器

    新規チャット開始時に、関連する過去のセッション履歴を検索して復元。
    """

    def __init__(self, storage_dir: str = "memory/sessions", project_history_dir: str = "memory/project_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.project_history_store = ProjectHistoryStore(project_history_dir)
        self.restored_sessions: List[Dict[str, Any]] = []

    def restore(self, query: str, k: int = 3) -> List[Dict[str, Any]]:
        """
        関連する過去のセッション履歴を復元

        Args:
            query: 検索クエリ
            k: 返す結果数

        Returns:
            復元されたセッション履歴のリスト
        """
        self.restored_sessions = []

        # プロジェクト履歴から関連するプロジェクトを検索
        related_projects = self.project_history_store.search(query, k=k)

        # 各プロジェクトのセッション履歴を検索
        for project in related_projects:
            project_id = project.project_id
            sessions = self._find_sessions_by_project(project_id)

            for session_file in sessions:
                session_data = self._load_session(session_file)
                if session_data:
                    self.restored_sessions.append(session_data)

        return self.restored_sessions

    def _find_sessions_by_project(self, project_id: str) -> List[Path]:
        """プロジェクトIDに関連するセッションファイルを検索"""
        sessions = []
        if not self.storage_dir.exists():
            return sessions

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    session_data = json.load(f)
                    if session_data.get("project_id") == project_id:
                        sessions.append(file_path)
            except (json.JSONDecodeError, KeyError):
                continue

        return sessions

    def _load_session(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """セッションファイルを読み込む"""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_restored_sessions(self) -> List[Dict[str, Any]]:
        """復元されたセッション履歴を取得"""
        return self.restored_sessions


# グローバルインスタンス
_session_restorer = None


def get_session_restorer() -> SessionRestorer:
    """セッション復元器のインスタンスを取得"""
    global _session_restorer
    if _session_restorer is None:
        _session_restorer = SessionRestorer()
    return _session_restorer
