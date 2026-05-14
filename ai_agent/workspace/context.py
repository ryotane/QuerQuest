# ai_agent/workspace/context.py

def generate_workspace_context(registry: dict) -> str:
    """ワークスペースレジストリからコンテキストテキストを生成"""
    
    context_parts = []
    
    # サマリー
    if registry.get("summary"):
        context_parts.append(f"【プロジェクト概要】{registry['summary']}")
    
    # 最近のトピック
    if registry.get("recent_topics"):
        topics = ", ".join(registry["recent_topics"][:5])
        context_parts.append(f"【最近のトピック】{topics}")
    
    # アクティブゴール
    active_goals = [g for g in registry.get("active_goals", []) if g.get("status") == "in_progress"]
    if active_goals:
        goals = "\n".join([f"- {g['description']}" for g in active_goals[:3]])
        context_parts.append(f"【アクティブな目標】\n{goals}")
    
    # 最近の意思決定
    if registry.get("recent_decisions"):
        decisions = registry["recent_decisions"][:2]
        dec_text = "\n".join([f"- {d['description']}" for d in decisions])
        context_parts.append(f"【最近の意思決定】\n{dec_text}")
    
    return "\n\n".join(context_parts)
