"""
session_logger.py - セッション履歴ロガー

Project_040: 記憶の継承機能
新規チャット開始時に履歴ファイルを作成し、メッセージを追記。
"""

import os
import json
import time
from pathlib import Path
from typing import List, Dict, Any, Optional


class SessionLogger:
    """
    セッション履歴ロガー

    新規チャット開始時に履歴ファイルを作成し、メッセージを追記。
    セッション終了時にメタデータ（要約、タグ）を生成。
    """

    def __init__(self, storage_dir: str = "memory/sessions"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.current_session_id: Optional[str] = None
        self.current_session_file: Optional[Path] = None
        self.messages: List[Dict[str, Any]] = []

    def start_session(self, project_id: str = "default") -> str:
        """
        セッションを開始

        Args:
            project_id: プロジェクトID

        Returns:
            セッションID
        """
        self.current_session_id = f"session_{int(time.time())}_{project_id}"
        self.current_session_file = self.storage_dir / f"{self.current_session_id}.json"
        self.messages = []

        # 空のセッションファイルを作成
        session_data = {
            "session_id": self.current_session_id,
            "project_id": project_id,
            "created_at": time.time(),
            "updated_at": time.time(),
            "messages": [],
            "metadata": {
                "summary": "",
                "tags": [],
            }
        }
        with open(self.current_session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

        return self.current_session_id

    def add_message(self, role: str, content: str):
        """
        メッセージを追加

        Args:
            role: メッセージの役割 (user, assistant, system)
            content: メッセージの内容
        """
        if not self.current_session_id:
            raise RuntimeError("Session not started. Call start_session() first.")

        message = {
            "role": role,
            "content": content,
            "timestamp": time.time(),
        }
        self.messages.append(message)

        # ファイルに追記
        with open(self.current_session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)
        
        session_data["messages"].append(message)
        session_data["updated_at"] = time.time()

        with open(self.current_session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def end_session(self):
        """
        セッションを終了し、メタデータを生成
        """
        if not self.current_session_id:
            return

        # メタデータを生成（簡易版）
        summary = self._generate_summary()
        tags = self._generate_tags()

        with open(self.current_session_file, "r", encoding="utf-8") as f:
            session_data = json.load(f)

        session_data["metadata"]["summary"] = summary
        session_data["metadata"]["tags"] = tags
        session_data["metadata"]["completed_at"] = time.time()

        with open(self.current_session_file, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)

    def _generate_summary(self) -> str:
        """要約を生成（簡易版）"""
        if not self.messages:
            return ""
        
        # 最初の数メッセージを要約として使用
        return "\n".join([msg["content"] for msg in self.messages[:3]])

    def _generate_tags(self) -> List[str]:
        """タグを生成（簡易版）"""
        tags = []
        if not self.messages:
            return tags
        
        # キーワードに基づいてタグを生成
        content = " ".join([msg["content"] for msg in self.messages])
        
        if "ループ" in content:
            tags.append("loop")
        if "エラー" in content:
            tags.append("error")
        if "メモリ" in content:
            tags.append("memory")
        
        return tags

    def get_current_session_id(self) -> Optional[str]:
        """現在のセッションIDを取得"""
        return self.current_session_id


# グローバルインスタンス
_session_logger = None


def get_session_logger() -> SessionLogger:
    """セッションロガーのインスタンスを取得"""
    global _session_logger
    if _session_logger is None:
        _session_logger = SessionLogger()
    return _session_logger
