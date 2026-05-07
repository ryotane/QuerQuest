# ai_agent/workspace/session_context.py

from ai_agent.workspace.session_registry import SessionRegistry
from ai_agent.workspace.memory_stabilization import MemoryStabilizer

# グローバル安定化インスタンス
_stabilizer = MemoryStabilizer()


def get_stabilizer() -> MemoryStabilizer:
    """安定化インスタンスを取得"""
    return _stabilizer


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
    # 安定化モジュールを使用
    return _stabilizer.build_safe_context(registry, limit)


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


def build_multi_session_context(registry: SessionRegistry, 
                                 sessions: list, 
                                 max_total_chars: int = 2000) -> str:
    """
    複数のセッションからコンテキストを結合生成
    
    ガードレール: 総文字数制限
    
    Args:
        registry: SessionRegistry インスタンス
        sessions: [(session, score), ...] 検索結果
        max_total_chars: 総文字数制限（デフォルト 2000 文字）
    
    Returns:
        結合されたコンテキストテキスト
    """
    if not sessions:
        return ""
    
    context_parts = []
    total_chars = 0
    
    for i, (session, score) in enumerate(sessions, 1):
        # 各セッションのセクションを生成
        section = []
        
        # タイトル
        title = session.get("title", "Untitled")
        section.append(f"【セッション {i}: {title}】")
        
        # サマリー（重要）
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
        
        # next_actions（あれば）
        next_actions = session.get("next_actions", [])
        if next_actions:
            section.append(f"  次回アクション: {'; '.join(next_actions[:3])}")
        
        # 最後のユーザー意図
        intent = session.get("last_user_intent", "")
        if intent:
            section.append(f"  意図: {intent}")
        
        # 関連度スコア
        section.append(f"  関連度: {score}")
        
        section_text = "\n".join(section)
        
        # ガードレール: 総文字数制限
        if total_chars + len(section_text) > max_total_chars:
            # 残りで収まるように要約を切り詰める
            if summary:
                remaining = max_total_chars - total_chars
                truncated_summary = summary[:remaining-10] + "..."
                section = [s for s in section if not s.startswith("  要約:")]
                section.insert(1, f"  要約: {truncated_summary}")
                section_text = "\n".join(section)
            else:
                break  # これ以上追加できない
        
        context_parts.append(section_text)
        total_chars += len(section_text)
        
        # 制限に達したら終了
        if total_chars >= max_total_chars:
            break
    
    return "\n\n".join(context_parts)


def build_combined_context(registry: SessionRegistry, 
                            chat_ids: list, 
                            max_total_chars: int = 2000) -> str:
    """
    特定のセッション ID からコンテキストを結合
    
    Args:
        registry: SessionRegistry インスタンス
        chat_ids: 対象の chat_id リスト
        max_total_chars: 総文字数制限
    
    Returns:
        結合されたコンテキストテキスト
    """
    sessions = []
    for chat_id in chat_ids:
        session = registry.get_session(chat_id)
        if session:
            sessions.append((session, 1))  # スコアは均一
    
    return build_multi_session_context(registry, sessions, max_total_chars)
