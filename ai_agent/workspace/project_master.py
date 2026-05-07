# ai_agent/workspace/project_master.py

"""
プロジェクトマスタードキュメント生成モジュール

セッションの next_actions を集約し、
プロジェクト全体の「未完了タスクリスト」を生成する。
"""

import json
import os
from datetime import datetime
from ai_agent.workspace.session_registry import SessionRegistry


def generate_project_master(workspace_id: str = "queryquest_project") -> dict:
    """
    プロジェクトマスタードキュメントを生成
    
    全セッションの next_actions を集約し、
    現在のプロジェクト全体の「未完了タスクリスト」を生成。
    
    Args:
        workspace_id: ワークスペース ID
    
    Returns:
        プロジェクトマスタードキュメント
    """
    registry = SessionRegistry()
    
    # 全セッションの next_actions を集約
    all_actions = registry.get_all_next_actions(workspace_id)
    
    # プロジェクトセッションを取得
    project_sessions = registry.get_project_sessions(workspace_id)
    
    # 重要トピックを集約
    all_topics = []
    for session in project_sessions:
        for topic in session.get("recent_topics", []):
            if topic not in all_topics:
                all_topics.append(topic)
    
    # アクティブゴールを集約
    active_goals = []
    for session in project_sessions:
        for goal in session.get("active_goals", []):
            if goal not in active_goals:
                active_goals.append(goal)
    
    # プロジェクトマスタードキュメントを生成
    master_doc = {
        "workspace_id": workspace_id,
        "generated_at": datetime.now().isoformat(),
        "project_summary": _generate_project_summary(project_sessions),
        "important_topics": all_topics[:20],
        "active_goals": active_goals,
        "unfinished_tasks": all_actions[:50],  # 最大 50 件
        "session_count": len(project_sessions),
        "last_updated": datetime.now().isoformat()
    }
    
    # プロジェクトマスタードキュメントを保存
    _save_project_master(master_doc)
    
    return master_doc


def _generate_project_summary(sessions: list) -> str:
    """
    プロジェクト全体のサマリーを生成
    
    Args:
        sessions: プロジェクトセッションリスト
    
    Returns:
        プロジェクトサマリー
    """
    if not sessions:
        return ""
    
    # 最新のセッションのサマリーを使用
    sorted_sessions = sorted(
        sessions,
        key=lambda x: x.get("updated_at", ""),
        reverse=True
    )
    
    if sorted_sessions:
        return sorted_sessions[0].get("summary", "")
    
    return ""


def _save_project_master(master_doc: dict):
    """
    プロジェクトマスタードキュメントを保存
    
    Args:
        master_doc: プロジェクトマスタードキュメント
    """
    # プロジェクトマスターファイルのパス
    project_master_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "project_master.json"
    )
    
    with open(project_master_path, "w", encoding="utf-8") as f:
        json.dump(master_doc, f, indent=2, ensure_ascii=False)


def load_project_master(workspace_id: str = "queryquest_project") -> dict:
    """
    プロジェクトマスタードキュメントを読み込み
    
    Args:
        workspace_id: ワークスペース ID
    
    Returns:
        プロジェクトマスタードキュメント
    """
    project_master_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "project_master.json"
    )
    
    if os.path.exists(project_master_path):
        with open(project_master_path, "r", encoding="utf-8") as f:
            return json.load(f)
    
    # なければ新規生成
    return generate_project_master(workspace_id)
