# ai_agent/workspace/memory_stabilization/memory_separation.py

"""
Memory Separation Module

active memory と archive memory を分離し、
context injection の対象を制限する。

役割:
1. active memory のみ injection 対象
2. archive memory は参照専用
3. 自動アーカイブ
"""

import os
import json
from datetime import datetime, timedelta
from typing import Optional


class MemorySeparation:
    """
    active/archive memory 分離
    
    仕組み:
    - active sessions のみ context injection 対象
    - archive sessions は参照専用
    - 一定期間経過で自動アーカイブ
    """
    
    # アーカイブ期間（日数）
    ARCHIVE_AFTER_DAYS = 7
    
    # 最大 active sessions 数
    MAX_ACTIVE_SESSIONS = 5
    
    def __init__(self, archive_dir: str = None):
        if archive_dir is None:
            # session_registry.json の親ディレクトリ
            import os
            self.archive_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.abspath(__file__)))),
                "archive", "sessions"
            )
        else:
            self.archive_dir = archive_dir
        
        os.makedirs(self.archive_dir, exist_ok=True)
    
    def is_active_session(self, session: dict) -> bool:
        """
        セッションが active かチェック
        
        更新日から一定期間以内なら active。
        
        Args:
            session: セッションデータ
            
        Returns:
            active なら True
        """
        updated_at = session.get("updated_at", "")
        if not updated_at:
            return True  # 日付なしは active とみなす
        
        try:
            updated = datetime.fromisoformat(updated_at.replace('Z', '+00:00'))
            now = datetime.now(updated.tzinfo)
            delta = now - updated
            
            return delta.days < self.ARCHIVE_AFTER_DAYS
        except (ValueError, TypeError):
            return True  # パース失敗時は active とみなす
    
    def archive_session(self, session: dict, registry_path: str) -> str:
        """
        セッションを archive へ移動
        
        Args:
            session: アーカイブ対象セッション
            registry_path: session_registry.json のパス
            
        Returns:
            アーカイブ先のパス
        """
        chat_id = session.get("chat_id", "unknown")
        archive_path = os.path.join(self.archive_dir, f"{chat_id}.json")
        
        # archive データを作成
        archive_data = {
            "session": session,
            "archived_at": datetime.now().isoformat(),
            "archived_reason": "active_period_expired"
        }
        
        with open(archive_path, "w", encoding="utf-8") as f:
            json.dump(archive_data, f, indent=2, ensure_ascii=False)
        
        return archive_path
    
    def get_active_sessions(self, sessions: list) -> list:
        """
        active sessions のみを抽出
        
        Args:
            sessions: 全セッションリスト
            
        Returns:
            active sessions のみ
        """
        return [s for s in sessions if self.is_active_session(s)]
    
    def get_recent_active_sessions(self, sessions: list, 
                                    limit: int = None) -> list:
        """
        最新の active sessions を取得
        
        Args:
            sessions: 全セッションリスト
            limit: 最大件数（デフォルト MAX_ACTIVE_SESSIONS）
            
        Returns:
            最新の active sessions
        """
        if limit is None:
            limit = self.MAX_ACTIVE_SESSIONS
        
        active = self.get_active_sessions(sessions)
        
        # 更新日でソート（降順）
        sorted_sessions = sorted(
            active,
            key=lambda x: x.get("updated_at", ""),
            reverse=True
        )
        
        return sorted_sessions[:limit]
    
    def clean_old_archives(self, max_age_days: int = 30) -> int:
        """
        古い archive ファイルを削除
        
        Args:
            max_age_days: 最大保存期間（日数）
            
        Returns:
            削除したファイル数
        """
        import os
        
        deleted_count = 0
        
        if not os.path.exists(self.archive_dir):
            return 0
        
        for filename in os.listdir(self.archive_dir):
            if not filename.endswith('.json'):
                continue
            
            filepath = os.path.join(self.archive_dir, filename)
            file_time = datetime.fromtimestamp(os.path.getmtime(filepath))
            age = datetime.now() - file_time
            
            if age.days > max_age_days:
                os.remove(filepath)
                deleted_count += 1
        
        return deleted_count
    
    def get_stats(self) -> dict:
        """統計情報を取得"""
        archive_count = 0
        if os.path.exists(self.archive_dir):
            archive_count = len([
                f for f in os.listdir(self.archive_dir)
                if f.endswith('.json')
            ])
        
        return {
            "archive_dir": self.archive_dir,
            "archive_count": archive_count,
            "max_active_sessions": self.MAX_ACTIVE_SESSIONS,
            "archive_after_days": self.ARCHIVE_AFTER_DAYS
        }
