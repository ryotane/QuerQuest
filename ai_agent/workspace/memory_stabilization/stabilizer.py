# ai_agent/workspace/memory_stabilization/stabilizer.py

"""
Memory Stabilizer Module

recursive context amplification を防止する
統合安定化モジュール。

他の全モジュールを統合し、
memory flow の安定化を担当。

役割:
1. injected context exclusion
2. recursive injection detection
3. context deduplication
4. token budget hard limit
5. summary compression
6. active/archive memory separation
"""

from typing import Optional

from .injection_guard import InjectionGuard
from .context_deduplicator import ContextDeduplicator
from .summary_compressor import SummaryCompressor
from .memory_separation import MemorySeparation


class MemoryStabilizer:
    """
    Memory Stabilization 統合クラス
    
    全安定化機能を統合し、
    memory flow の安定化を担当。
    
    使用例:
        stabilizer = MemoryStabilizer()
        
        # セッションコンテキスト生成時
        context = stabilizer.build_safe_context(registry, limit=3)
        
        # セッション保存時
        stabilizer.validate_session_data(session_data)
        
        # 循環参照検出
        if stabilizer.detect_recursion(context):
            # 循環参照あり → 対策
            pass
    """
    
    # 文字数制限
    MAX_INJECTED_CONTEXT_CHARS = 1500
    MAX_SUMMARY_CHARS = 500
    MAX_TOPICS_CHARS = 200
    MAX_GOALS_CHARS = 300
    
    def __init__(self):
        self.injection_guard = InjectionGuard()
        self.deduplicator = ContextDeduplicator()
        self.compressor = SummaryCompressor()
        self.separation = MemorySeparation()
    
    def build_safe_context(self, registry, limit: int = 3) -> str:
        """
        安全なセッションコンテキストを生成
        
        安定化機能を適用した上でコンテキストを生成。
        
        Args:
            registry: SessionRegistry インスタンス
            limit: 含めるセッション数
            
        Returns:
            安全なコンテキストテキスト
        """
        # active sessions のみを取得
        all_sessions = registry.get_recent_sessions(limit=limit * 2)
        active_sessions = self.separation.get_recent_active_sessions(
            all_sessions, limit=limit
        )
        
        if not active_sessions:
            return ""
        
        # コンテキストを生成
        context_parts = []
        
        for i, session in enumerate(active_sessions, 1):
            section = []
            
            # タイトル
            title = session.get("title", "Untitled")
            section.append(f"【セッション {i}: {title}】")
            
            # サマリー（圧縮）
            summary = session.get("summary", "")
            if summary:
                compressed_summary = self.compressor.compress_summary(
                    summary, self.MAX_SUMMARY_CHARS
                )
                section.append(f"  要約: {compressed_summary}")
            
            # トピック（圧縮・重複排除）
            topics = session.get("recent_topics", [])
            if topics:
                deduped_topics = self.deduplicator.deduplicate_topics(topics)
                compressed_topics = self.compressor.compress_topics(
                    deduped_topics, self.MAX_TOPICS_CHARS
                )
                section.append(f"  トピック: {', '.join(compressed_topics[:5])}")
            
            # ゴール（圧縮）
            goals = session.get("active_goals", [])
            if goals:
                compressed_goals = self.compressor.compress_goals(
                    goals, self.MAX_GOALS_CHARS
                )
                section.append(f"  目標: {'; '.join(compressed_goals[:3])}")
            
            # 最後のユーザー意図
            intent = session.get("last_user_intent", "")
            if intent:
                section.append(f"  意図: {intent[:100]}")
            
            # 更新日時
            updated = session.get("updated_at", "")
            if updated:
                section.append(f"  更新: {updated}")
            
            context_parts.append("\n".join(section))
        
        context = "\n\n".join(context_parts)
        
        # 最終的な文字数制限
        context = self.compressor.compress_session_context(
            context, self.MAX_INJECTED_CONTEXT_CHARS
        )
        
        # 注入済みとしてマーク
        self.injection_guard.mark_injected(context)
        
        return context
    
    def validate_session_data(self, session_data: dict) -> dict:
        """
        セッションデータを検証・修正
        
        安定化ルールを適用。
        
        Args:
            session_data: セッションデータ
            
        Returns:
            修正されたセッションデータ
        """
        validated = session_data.copy()
        
        # サマリー圧縮
        if validated.get("summary"):
            validated["summary"] = self.compressor.compress_summary(
                validated["summary"], self.MAX_SUMMARY_CHARS
            )
        
        # トピック重複排除
        if validated.get("recent_topics"):
            validated["recent_topics"] = self.deduplicator.deduplicate_topics(
                validated["recent_topics"]
            )
        
        # ゴール圧縮
        if validated.get("active_goals"):
            validated["active_goals"] = self.compressor.compress_goals(
                validated["active_goals"], self.MAX_GOALS_CHARS
            )
        
        return validated
    
    def detect_recursion(self, context: str) -> bool:
        """
        循環参照を検出
        
        Args:
            context: チェック対象のcontext
            
        Returns:
            循環参照があれば True
        """
        return self.injection_guard.detect_recursive_injection(context)
    
    def is_context_safe(self, context: str) -> bool:
        """
        context が安全かチェック
        
        文字数制限と重複チェックを適用。
        
        Args:
            context: チェック対象のcontext
            
        Returns:
            安全なら True
        """
        # 文字数チェック
        if len(context) > self.MAX_INJECTED_CONTEXT_CHARS * 2:
            return False
        
        # 重複チェック
        if self.injection_guard.is_already_injected(context):
            return False
        
        return True
    
    def get_stats(self) -> dict:
        """統計情報を取得"""
        return {
            "injection_guard": self.injection_guard.get_stats(),
            "deduplicator": self.deduplicator.get_stats(),
            "memory_separation": self.separation.get_stats(),
            "limits": {
                "max_injected_context_chars": self.MAX_INJECTED_CONTEXT_CHARS,
                "max_summary_chars": self.MAX_SUMMARY_CHARS,
                "max_topics_chars": self.MAX_TOPICS_CHARS,
                "max_goals_chars": self.MAX_GOALS_CHARS,
            }
        }
    
    def reset(self):
        """全状態をリセット"""
        self.injection_guard.reset_chain()
        self.deduplicator.clear()
