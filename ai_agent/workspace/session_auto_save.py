# ai_agent/workspace/session_auto_save.py

"""
セッション自動保存モジュール

チャット終了時に会話から情報を抽出し、
session_registry.json に自動保存する。
"""

import re
from datetime import datetime
from ai_agent.llm.lmstudio import LMStudioClient


llm = LMStudioClient()


def extract_topics(text: str) -> list:
    """
    テキストから技術キーワードを抽出
    
    MVP 段階ではルールベースで抽出。
    将来的に LLM に任せることも可能。
    """
    # 技術キーワードの例（必要に応じて拡張）
    tech_keywords = [
        "Python", "MVP", "JSON", "API", "LLM", "LM Studio",
        "MCP", "Vector DB", "Embedding", "Memory", "Workspace",
        "Session", "Continuity", "Orchestrator", "Intent",
        "System Prompt", "Chat", "Thread", "Goal", "Registry",
        "Phase", "Architecture", "Design", "Implementation",
        "テスト", "実装", "設計", "確認", "動作"
    ]
    
    found = []
    for keyword in tech_keywords:
        if keyword in text:
            found.append(keyword)
    
    return found[:10]  # 最大10件


def generate_summary(query: str, answer: str) -> str:
    """
    会話から要約を生成
    
    LLM に要約を依頼する。
    """
    try:
        prompt = f"""
以下の会話から、核心的な要約を150文字程度で生成してください。

【ユーザーの質問】
{query[:500]}

【AI の回答】
{answer[:500]}

出力形式:
要約: <150文字程度の要約>

要約のみを返してください。
"""
        result = llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        # 「要約:」以降を抽出
        match = re.search(r"要約:\s*(.+)", result, re.IGNORECASE)
        if match:
            return match.group(1).strip()[:150]
        
        return result[:150]
    
    except Exception as e:
        print(f"❌ 要約生成エラー: {e}")
        return ""


def extract_next_actions(query: str, answer: str) -> list:
    """
    次回やるべきことを抽出
    
    LLM に抽出を依頼する。
    """
    try:
        prompt = f"""
以下の会話から、次回やるべきことを3つまで抽出してください。

【ユーザーの質問】
{query[:500]}

【AI の回答】
{answer[:500]}

出力形式:
1. <アクション1>
2. <アクション2>
3. <アクション3>

アクションがない場合は空を返してください。
"""
        result = llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        # 番号付きリストを抽出
        actions = []
        for line in result.split('\n'):
            line = line.strip()
            if re.match(r'^\d+\.', line):
                action = re.sub(r'^\d+\.\s*', '', line)
                if action:
                    actions.append(action)
        
        return actions[:3]
    
    except Exception as e:
        print(f"❌ next_actions 抽出エラー: {e}")
        return []


def auto_save_session(
    chat_id: str,
    title: str,
    query: str,
    answer: str,
    existing_summary: str = "",
    existing_topics: list = None,
    existing_goals: list = None
) -> dict:
    """
    セッション情報を自動抽出して保存
    
    Args:
        chat_id: セッション ID
        title: タイトル
        query: ユーザーの質問
        answer: AI の回答
        existing_summary: 既存のサマリー（あれば）
        existing_topics: 既存のトピック（あれば）
        existing_goals: 既存のゴール（あれば）
    
    Returns:
        保存されたセッションデータ
    """
    from ai_agent.workspace.session_registry import SessionRegistry
    
    registry = SessionRegistry()
    
    # 既存セッションを取得
    existing = registry.get_session(chat_id)
    
    # 要約の生成（既存があれば更新、なければ新規）
    if existing_summary:
        summary = existing_summary
    else:
        summary = generate_summary(query, answer)
    
    # トピックの抽出（既存があればマージ）
    new_topics = extract_topics(query + " " + answer)
    if existing_topics:
        # マージ（重複除去）
        all_topics = list(set(existing_topics + new_topics))
    else:
        all_topics = new_topics
    
    # next_actions の抽出
    next_actions = extract_next_actions(query, answer)
    
    # ゴールの更新（既存があれば維持）
    goals = existing_goals or []
    
    # セッションの更新
    updated = registry.update_session(
        chat_id=chat_id,
        title=title,
        summary=summary,
        recent_topics=all_topics,
        active_goals=goals,
        last_user_intent=query[:100]  # 意図は質問の先頭100文字
    )
    
    # next_actions を直接追加（update_session に含まれていないため）
    if next_actions:
        # session_registry.json に直接追記
        import json
        import os
        
        path = registry.path
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        # 該当セッションを検索
        for session in data.get("sessions", []):
            if session.get("chat_id") == chat_id:
                session["next_actions"] = next_actions
                break
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    return updated


def distill_knowledge(sessions: list) -> dict:
    """
    複数のセッションから知識を蒸留（統合サマリー生成）
    
    LLM に重複を削ぎ、抽象度の高い情報だけを抽出させる。
    
    Args:
        sessions: マージ対象のセッションリスト
    
    Returns:
        蒸留された知識（統合サマリー、重要トピック、未完了タスク）
    """
    try:
        # セッション情報をテキスト化
        session_texts = []
        for session in sessions:
            text = f"""
【セッション: {session.get('title', 'Untitled')}】
要約: {session.get('summary', '')}
トピック: {', '.join(session.get('recent_topics', []))}
ゴール: {', '.join(session.get('active_goals', []))}
next_actions: {', '.join(session.get('next_actions', []))}
"""
            session_texts.append(text)
        
        combined_text = "\n".join(session_texts)
        
        prompt = f"""
以下の複数のセッションから、以下の情報を抽出してください。

【セッション一覧】
{combined_text[:3000]}

【出力形式】
統合サマリー: <350 文字程度の統合サマリー>
重要トピック: <重複を除いた重要トピックのリスト>
未完了タスク: <next_actions から重複を除いたタスクリスト>

出力形式例:
統合サマリー: ...
重要トピック:
- トピック 1
- トピック 2
未完了タスク:
1. タスク 1
2. タスク 2

重要トピックと未完了タスクのみを抽出してください。
"""
        
        result = llm.chat([
            {"role": "user", "content": prompt}
        ])
        
        # 結果をパース
        distilled = {
            "integrated_summary": "",
            "important_topics": [],
            "unfinished_tasks": []
        }
        
        # 統合サマリー抽出
        match = re.search(r"統合サマリー:\s*(.+?)(?=重要トピック|$)", result, re.IGNORECASE | re.DOTALL)
        if match:
            distilled["integrated_summary"] = match.group(1).strip()[:350]
        
        # 重要トピック抽出
        topics_section = re.search(r"重要トピック:\s*(.+?)(?=未完了タスク|$)", result, re.IGNORECASE | re.DOTALL)
        if topics_section:
            for line in topics_section.group(1).split('\n'):
                line = line.strip().lstrip('-•').strip()
                if line:
                    distilled["important_topics"].append(line)
        
        # 未完了タスク抽出
        tasks_section = re.search(r"未完了タスク:\s*(.+)", result, re.IGNORECASE | re.DOTALL)
        if tasks_section:
            for line in tasks_section.group(1).split('\n'):
                line = line.strip()
                if re.match(r'^\d+\.', line):
                    task = re.sub(r'^\d+\.\s*', '', line)
                    if task:
                        distilled["unfinished_tasks"].append(task)
        
        return distilled
    
    except Exception as e:
        print(f"❌ 知識蒸留エラー: {e}")
        return {
            "integrated_summary": "",
            "important_topics": [],
            "unfinished_tasks": []
        }


def auto_merge_sessions(
    registry,
    target_chat_id: str,
    source_sessions: list,
    use_distillation: bool = True
) -> dict:
    """
    セッションの自動マージ（知識蒸留付き）
    
    Args:
        registry: SessionRegistry インスタンス
        target_chat_id: 対象セッションの chat_id
        source_sessions: マージするセッションリスト
        use_distillation: 知識蒸留を使用するかどうか
    
    Returns:
        マージ後のセッションデータ
    """
    # 既存のマージ
    merged = registry.merge_sessions(target_chat_id, source_sessions)
    
    # 知識蒸留
    if use_distillation:
        distilled = distill_knowledge(source_sessions)
        
        # 統合サマリーで更新
        if distilled["integrated_summary"]:
            merged["summary"] = distilled["integrated_summary"]
        
        # 重要トピックで更新
        if distilled["important_topics"]:
            merged["recent_topics"] = distilled["important_topics"]
        
        # 未完了タスクで更新
        if distilled["unfinished_tasks"]:
            merged["next_actions"] = distilled["unfinished_tasks"]
        
        # 蒸留メタデータを追加
        merged["distilled_at"] = datetime.now().isoformat()
        merged["distilled_from_count"] = len(source_sessions)
        
        registry.save()
    
    return merged
