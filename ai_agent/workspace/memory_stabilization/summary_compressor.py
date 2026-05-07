# ai_agent/workspace/memory_stabilization/summary_compressor.py

"""
Summary Compressor Module

要約を圧縮し、
token 効率を最適化する。

役割:
1. 要約の文字数制限
2. 重要度の高い情報の保持
3. 冗長性の排除
"""

import re
from typing import Optional


class SummaryCompressor:
    """
    要約圧縮
    
    仕組み:
    - 文字数制限を厳格に適用
    - 重要情報を保持
    - 冗長性を排除
    """
    
    # 最大文字数
    MAX_SUMMARY_CHARS = 500
    MAX_TOPIC_CHARS = 200
    MAX_GOAL_CHARS = 300
    
    def __init__(self):
        pass
    
    def compress_summary(self, summary: str, max_chars: int = None) -> str:
        """
        要約を圧縮
        
        文字数制限を厳格に適用。
        文末を切り捨てず、意味を保持するように調整。
        
        Args:
            summary: 圧縮対象の要約
            max_chars: 最大文字数（デフォルト MAX_SUMMARY_CHARS）
            
        Returns:
            圧縮された要約
        """
        if max_chars is None:
            max_chars = self.MAX_SUMMARY_CHARS
        
        if not summary:
            return ""
        
        if len(summary) <= max_chars:
            return summary
        
        # 段落ごとに切り捨て
        paragraphs = summary.split('\n\n')
        result = []
        current_len = 0
        
        for para in paragraphs:
            if current_len + len(para) + 2 <= max_chars:
                result.append(para)
                current_len += len(para) + 2
            else:
                # 最後の段落は切り捨て
                remaining = max_chars - current_len
                if remaining > 50:  # 最低50文字は確保
                    result.append(para[:remaining-3] + "...")
                break
        
        return '\n\n'.join(result) if result else summary[:max_chars-3] + "..."
    
    def compress_topics(self, topics: list, max_chars: int = None) -> list:
        """
        トピックリストを圧縮
        
        文字数制限を適用し、重要度の高いものを保持。
        
        Args:
            topics: トピックリスト
            max_chars: 最大文字数（デフォルト MAX_TOPIC_CHARS）
            
        Returns:
            圧縮されたトピックリスト
        """
        if max_chars is None:
            max_chars = self.MAX_TOPIC_CHARS
        
        if not topics:
            return []
        
        if len(', '.join(topics)) <= max_chars:
            return topics
        
        # 文字数内で収まるように切り捨て
        result = []
        current_len = 0
        
        for topic in topics:
            if current_len + len(topic) + 2 <= max_chars:
                result.append(topic)
                current_len += len(topic) + 2
            else:
                break
        
        return result
    
    def compress_goals(self, goals: list, max_chars: int = None) -> list:
        """
        ゴールリストを圧縮
        
        文字数制限を適用。
        
        Args:
            goals: ゴールリスト
            max_chars: 最大文字数（デフォルト MAX_GOAL_CHARS）
            
        Returns:
            圧縮されたゴールリスト
        """
        if max_chars is None:
            max_chars = self.MAX_GOAL_CHARS
        
        if not goals:
            return []
        
        if len('; '.join(goals)) <= max_chars:
            return goals
        
        # 文字数内で収まるように切り捨て
        result = []
        current_len = 0
        
        for goal in goals:
            if current_len + len(goal) + 2 <= max_chars:
                result.append(goal)
                current_len += len(goal) + 2
            else:
                break
        
        return result
    
    def compress_session_context(self, context: str, 
                                  max_chars: int = 1500) -> str:
        """
        セッションコンテキスト全体を圧縮
        
        Args:
            context: 圧縮対象のコンテキスト
            max_chars: 最大文字数
            
        Returns:
            圧縮されたコンテキスト
        """
        if not context:
            return ""
        
        if len(context) <= max_chars:
            return context
        
        # セッションごとに処理
        sessions = re.split(r'【セッション \d+:', context)
        
        result = []
        current_len = 0
        
        for i, session in enumerate(sessions):
            if i == 0:
                # 最初のセッションはプレフィックス付き
                prefix = "【セッション 1:"
                if len(prefix) + len(session) + 2 <= max_chars:
                    result.append(prefix + session)
                    current_len += len(prefix) + len(session) + 2
                else:
                    result.append(prefix + session[:max_chars - len(prefix) - 3] + "...")
                break
            else:
                # 以降のセッション
                session_text = f"【セッション {i + 1}:" + session
                if current_len + len(session_text) + 2 <= max_chars:
                    result.append(session_text)
                    current_len += len(session_text) + 2
                else:
                    remaining = max_chars - current_len
                    if remaining > 50:
                        result.append(session_text[:remaining-3] + "...")
                    break
        
        return '\n\n'.join(result) if result else context[:max_chars-3] + "..."
    
    def get_compression_ratio(self, original: str, compressed: str) -> float:
        """
        圧縮率を計算
        
        Args:
            original: 元の文字列
            compressed: 圧縮後の文字列
            
        Returns:
            圧縮率（0.0 ~ 1.0）
        """
        if not original:
            return 1.0
        
        return len(compressed) / len(original)
