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
        "best_practices": _load_best_practices(),  # 教訓・ベストプラクティス
        "tech_stack": _extract_tech_stack(),  # テックスタック
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


def _load_best_practices() -> list:
    """
    ベストプラクティスファイルを読み込み
    
    Returns:
        ベストプラクティスのリスト
    """
    best_practices_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "best_practices.json"
    )
    
    if os.path.exists(best_practices_path):
        with open(best_practices_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("best_practices", [])
    
    return []


def add_best_practice(workspace_id: str = "queryquest_project", lesson: str = "", category: str = "general") -> dict:
    """
    ベストプラクティスを追加
    
    Args:
        workspace_id: ワークスペース ID
        lesson: 教訓
        category: カテゴリ
    
    Returns:
        更新されたベストプラクティス
    """
    best_practices_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "best_practices.json"
    )
    
    # 既存データを読み込み
    if os.path.exists(best_practices_path):
        with open(best_practices_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"best_practices": []}
    
    # 重複チェック
    existing = data.get("best_practices", [])
    for item in existing:
        if item.get("lesson") == lesson:
            return data  # 重複時はそのまま返す
    
    # 新規追加
    new_practice = {
        "id": f"bp_{len(existing) + 1:03d}",
        "lesson": lesson,
        "category": category,
        "workspace_id": workspace_id,
        "added_at": datetime.now().isoformat()
    }
    
    existing.append(new_practice)
    data["best_practices"] = existing
    
    # 保存
    with open(best_practices_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    return data


def _extract_tech_stack() -> dict:
    """
    テックスタックを抽出
    
    Returns:
        テックスタック辞書
    """
    import re
    
    tech_stack = {
        "python_version": "3.12",
        "libraries": {},
        "tools": [],
        "frameworks": []
    }
    
    # requirements.txt を探す
    requirements_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
        "requirements.txt"
    )
    
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # パッケージ名とバージョンを抽出
                        match = re.match(r'^([a-zA-Z0-9_-]+)==(.+)
, line)
                        if match:
                            tech_stack["libraries"][match.group(1)] = match.group(2)
                        else:
                            # バージョンなしの場合
                            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                            if match:
                                tech_stack["libraries"][match.group(1)] = "latest"
        except Exception as e:
            print(f"⚠️ requirements.txt 読み込みエラー: {e}")
    
    return tech_stack
