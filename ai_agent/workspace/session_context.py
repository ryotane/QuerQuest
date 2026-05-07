# ai_agent/workspace/session_context.py

from ai_agent.workspace.session_registry import SessionRegistry


def build_session_context(registry: SessionRegistry, limit: int = 3) -> str:
    """
    セッションコンテキストを生成
    
    直近のセッション情報を system prompt 用にテキスト化
    
    Args:
        registry: SessionRegistry インスタンス
        limit: 含めるセッション数
    
    Returns:
        生成されたコンテキストテキスト
    """
    sessions = registry.get_recent_sessions(limit=limit)
    
    if not sessions:
        return ""
    
    context_parts = []
    
    for i, session in enumerate(sessions, 1):
        section = []
        
        # タイトル
        title = session.get("title", "Untitled")
        section.append(f"【セッション {i}: {title}】")
        
        # サマリー
        summary = session.get("summary", "")
        if summary:
            section.append(f"  要約: {summary}")
        
        # 最近のトピック
        topics = session.get("recent_topics", [])
        if topics:
            section.append(f"  トピック: {', '.join(topics[:5])}")
        
        # アクティブゴール
        goals = session.get("active_goals", [])
        if goals:
            section.append(f"  目標: {'; '.join(goals[:3])}")
        
        # 最後のユーザー意図
        intent = session.get("last_user_intent", "")
        if intent:
            section.append(f"  意図: {intent}")
        
        # 更新日時
        updated = session.get("updated_at", "")
        if updated:
            section.append(f"  更新: {updated}")
        
        context_parts.append("\n".join(section))
    
    return "\n\n".join(context_parts)


def inject_session_context(system_prompt: str, registry: SessionRegistry, 
                           limit: int = 3) -> str:
    """
    セッションコンテキストを system prompt へ prepend
    
    Args:
        system_prompt: 元のシステムプロンプト
        registry: SessionRegistry インスタンス
        limit: 含めるセッション数
    
    Returns:
        セッションコンテキストを prepend したシステムプロンプト
    """
    session_context = build_session_context(registry, limit)
    
    if not session_context:
        return system_prompt
    
    # セッションコンテキストを system prompt の先頭に追加
    return f"""【直近のセッション】
{session_context}

---

{system_prompt}"""
