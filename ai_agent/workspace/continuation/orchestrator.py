"""
Automatic Continuation Orchestrator

新規チャット移行時の継続状態復元オーケストレーター。

目的:
- 「Project_03の続きをお願いします」だけで継続状態を復元
- 状況説明コストの削減
- 正確なコンテキスト復元

設計原則:
- workspace_id 優先検索
- recent_topics / active_goals overlap スコアリング
- context_usageに応じた適応的復元戦略
- token budget 厳格 enforcement
- stabilization layer 統合
- telemetry health 状態考慮
"""

import json
import os
import time
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple
from enum import Enum

from ..session_registry import SessionRegistry
from ..project_master import load_project_master
from ...observability.health_monitor import HealthMonitor
from ...observability.telemetry_scheduler import TelemetryState


class HydrationMode(Enum):
    """復元モード"""
    FULL = "full"           # 完全復元 (context_usage < 0.3)
    COMPRESSED = "compressed"  # 圧縮復元 (0.3 <= context_usage < 0.6)
    PARTIAL = "partial"     # 部分復元 (context_usage >= 0.6)


@dataclass
class ContinuationTarget:
    """継続ターゲット"""
    session_id: str
    title: str
    workspace_id: str
    confidence: float  # 0.0 - 1.0
    match_reasons: List[str] = field(default_factory=list)
    summary: str = ""
    active_goals: List[str] = field(default_factory=list)
    recent_topics: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)
    updated_at: str = ""


@dataclass
class ContinuationContext:
    """復元されたコンテキスト"""
    target: ContinuationTarget
    hydration_mode: HydrationMode
    restored_tokens: int = 0
    token_budget_remaining: int = 0
    stabilization_status: str = "pending"  # pending, stabilizing, stable
    telemetry_status: str = "healthy"  # healthy, degraded, critical
    restore_timestamp: float = 0.0
    compressed_summary: str = ""
    active_goals: List[str] = field(default_factory=list)
    recent_topics: List[str] = field(default_factory=list)
    key_decisions: List[str] = field(default_factory=list)
    immediate_next_actions: List[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


@dataclass
class ContinuationResult:
    """継続処理結果"""
    success: bool
    target: Optional[ContinuationTarget]
    context: Optional[ContinuationContext]
    confidence: float
    hydration_mode: HydrationMode
    message: str
    tokens_used: int = 0
    processing_time: float = 0.0


class ContinuationOrchestrator:
    """
    自動継続オーケストレーター。

    使用例:
        orchestrator = ContinuationOrchestrator()
        
        # 継続意図を検出
        intent = orchestrator.detect_continuation_intent("Project_03の続きをお願いします")
        
        if intent.is_continuation:
            # ターゲットを検索
            target = orchestrator.find_best_continuation_target("Project_03")
            
            if target.confidence > 0.7:
                # コンテキストを復元
                context = orchestrator.restore_context(target)
                
                # LLM に渡す
                print(context.compressed_summary)
    """

    def __init__(
        self,
        workspace_root: Optional[str] = None,
        token_budget: int = 1000,
        confidence_threshold: float = 0.6,
    ):
        self.workspace_root = workspace_root or os.getcwd()
        self.token_budget = token_budget
        self.confidence_threshold = confidence_threshold
        self.registry = SessionRegistry()
        self.health_monitor = HealthMonitor(workspace_root=self.workspace_root)
        self._last_restore_time = 0.0
        self._restore_cooldown = 5.0  # 5秒間の再復元防止

    def detect_continuation_intent(self, query: str) -> Dict:
        """
        継続意図を検出。

        Args:
            query: ユーザー入力

        Returns:
            {
                "is_continuation": bool,
                "confidence": float,
                "project_keyword": str,
                "workspace_id": str,
                "reason": str
            }
        """
        query_lower = query.lower()

        # 継続キーワード検出
        continuity_keywords = [
            "続き", "継続", "resume", "continue",
            "前の話", "あの話", "先ほど", "before",
            "このプロジェクト", "この作業", "this task",
            "また", "もう一度", "再開", "再開",
            "またやりましょう", "続けて", "progress"
        ]

        is_continuation = any(kw in query_lower for kw in continuity_keywords)

        if not is_continuation:
            return {
                "is_continuation": False,
                "confidence": 0.0,
                "project_keyword": "",
                "workspace_id": "",
                "reason": "continuity keywords not detected",
            }

        # プロジェクトキーワード抽出
        project_keyword = self._extract_project_keyword(query)

        # workspace_id 推定
        workspace_id = self._infer_workspace_id(query, project_keyword)

        # 信頼度スコアリング
        confidence = self._score_continuation_confidence(query, project_keyword, workspace_id)

        return {
            "is_continuation": True,
            "confidence": confidence,
            "project_keyword": project_keyword,
            "workspace_id": workspace_id,
            "reason": self._get_continuation_reason(query, project_keyword),
        }

    def find_best_continuation_target(
        self,
        keyword: str,
        workspace_id: str = "",
        limit: int = 5,
    ) -> List[ContinuationTarget]:
        """
        最適な継続ターゲットを検索。

        workspace_id 優先 → title 一致 → topic overlap → goal overlap

        Args:
            keyword: プロジェクト/セッションキーワード
            workspace_id: ワークスペース ID (優先)
            limit: 返す最大件数

        Returns:
            信頼度順にソートされたターゲットリスト
        """
        candidates = []

        # workspace_id でフィルタ
        if workspace_id:
            sessions = self.registry.get_project_sessions(workspace_id)
        else:
            sessions = self.registry.data.get("sessions", [])

        # スコアリング
        for session in sessions:
            score, reasons = self._score_session_match(session, keyword)

            if score >= 0.3:  # 最低閾値
                target = ContinuationTarget(
                    session_id=session.get("chat_id", ""),
                    title=session.get("title", ""),
                    workspace_id=session.get("workspace_id", ""),
                    confidence=score,
                    match_reasons=reasons,
                    summary=session.get("summary", ""),
                    active_goals=session.get("active_goals", []),
                    recent_topics=session.get("recent_topics", []),
                    next_actions=session.get("next_actions", []),
                    updated_at=session.get("updated_at", ""),
                )
                candidates.append(target)

        # 信頼度でソート
        candidates.sort(key=lambda x: x.confidence, reverse=True)

        return candidates[:limit]

    def restore_context(
        self,
        target: ContinuationTarget,
        current_context_usage: float = 0.0,
    ) -> ContinuationContext:
        """
        ターゲットのコンテキストを復元。

        context_usage に応じて復元戦略を適応。

        Args:
            target: 継続ターゲット
            current_context_usage: 現在のコンテキスト使用率 (0.0 - 1.0)

        Returns:
            復元されたコンテキスト
        """
        # 復元クールダウン
        now = time.time()
        if now - self._last_restore_time < self._restore_cooldown:
            return self._get_cached_restore_result()

        # 復元モード決定
        hydration_mode = self._decide_hydration_mode(current_context_usage)

        # コンテキスト復元
        context = self._hydrate_context(target, hydration_mode)
        context.restore_timestamp = now

        # 安定化
        context = self._stabilize_restored_context(context)

        # テレメトリ更新
        self._update_telemetry_for_restore(context)

        self._last_restore_time = now

        return context

    def generate_continuation_prompt(
        self,
        context: ContinuationContext,
    ) -> str:
        """
        継続用プロンプトを生成。

        Args:
            context: 復元されたコンテキスト

        Returns:
            LLM に渡す継続用プロンプト
        """
        parts = []

        # ヘッダー
        parts.append(f"【QueryQuest 継続コンテキスト】")
        parts.append(f"プロジェクト: {context.target.title}")
        parts.append(f"復元モード: {context.hydration_mode.value}")
        parts.append(f"信頼度: {context.target.confidence:.2f}")
        parts.append("")

        # 圧縮サマリー
        if context.compressed_summary:
            parts.append(f"【圧縮サマリー】")
            parts.append(context.compressed_summary)
            parts.append("")

        # アクティブゴール
        if context.active_goals:
            parts.append(f"【アクティブゴール】")
            for goal in context.active_goals[:5]:
                parts.append(f"- {goal}")
            parts.append("")

        # 最近のトピック
        if context.recent_topics:
            parts.append(f"【最近のトピック】")
            parts.append(", ".join(context.recent_topics[:10]))
            parts.append("")

        # 即時アクション
        if context.immediate_next_actions:
            parts.append(f"【次のアクション】")
            for action in context.immediate_next_actions[:3]:
                parts.append(f"- {action}")
            parts.append("")

        # 意思決定
        if context.key_decisions:
            parts.append(f"【重要な意思決定】")
            for decision in context.key_decisions[:3]:
                parts.append(f"- {decision}")
            parts.append("")

        # フッター
        parts.append(f"---")
        parts.append(f"このコンテキストを基に、前の作業を継続してください。")

        return "\n".join(parts)

    # --- Private Methods ---

    def _extract_project_keyword(self, query: str) -> str:
        """プロジェクトキーワードを抽出"""
        # "Project_XX" パターン
        import re
        match = re.search(r"Project[_\s]?(\d+)", query, re.IGNORECASE)
        if match:
            return f"Project_{match.group(1)}"

        # "Phase XX" パターン
        match = re.search(r"Phase[_\s]?(\d+)", query, re.IGNORECASE)
        if match:
            return f"Phase_{match.group(1)}"

        # キーワード抽出 (簡易)
        words = query.split()
        for word in words:
            if len(word) > 3 and word[0].isupper():
                return word

        return ""

    def _infer_workspace_id(self, query: str, keyword: str) -> str:
        """workspace_id を推定"""
        # キーワードに workspace_id が含まれる場合
        if "queryquest" in query.lower():
            return "queryquest_project"

        # デフォルト
        return "queryquest_project"

    def _score_continuation_confidence(
        self,
        query: str,
        keyword: str,
        workspace_id: str,
    ) -> float:
        """継続信頼度をスコアリング"""
        score = 0.0

        # キーワード長 (長いほど特定性が高い)
        if len(keyword) > 5:
            score += 0.2
        elif len(keyword) > 0:
            score += 0.1

        # workspace_id 一致
        if workspace_id:
            score += 0.1

        # 継続キーワードの密度
        continuity_keywords = ["続き", "継続", "resume", "continue"]
        density = sum(1 for kw in continuity_keywords if kw in query.lower())
        score += min(density * 0.1, 0.3)

        return min(score, 1.0)

    def _get_continuation_reason(
        self,
        query: str,
        keyword: str,
    ) -> str:
        """継続理由を生成"""
        if keyword:
            return f"keyword match: {keyword}"
        return "continuity keywords detected"

    def _score_session_match(
        self,
        session: dict,
        keyword: str,
    ) -> Tuple[float, List[str]]:
        """セッションの一致度をスコアリング"""
        score = 0.0
        reasons = []

        # workspace_id 一致 (重み高)
        if session.get("workspace_id") == "queryquest_project":
            score += 0.3
            reasons.append("workspace_id match")

        # title 完全一致 (重み高)
        title = session.get("title", "").lower()
        if keyword.lower() in title:
            score += 0.3
            reasons.append(f"title match: {keyword}")

        # topic overlap (重み中)
        topics = session.get("recent_topics", [])
        topic_matches = sum(1 for t in topics if keyword.lower() in t.lower())
        if topic_matches > 0:
            score += min(topic_matches * 0.05, 0.2)
            reasons.append(f"topic overlap: {topic_matches}")

        # goal overlap (重み中)
        goals = session.get("active_goals", [])
        goal_matches = sum(1 for g in goals if keyword.lower() in g.lower())
        if goal_matches > 0:
            score += min(goal_matches * 0.05, 0.15)
            reasons.append(f"goal overlap: {goal_matches}")

        # recency (重み低)
        updated_at = session.get("updated_at", "")
        if updated_at:
            try:
                from datetime import datetime
                updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                days_ago = (datetime.now(updated.tzinfo) - updated).days
                if days_ago < 1:
                    score += 0.1
                    reasons.append("updated today")
                elif days_ago < 7:
                    score += 0.05
                    reasons.append("updated this week")
            except Exception:
                pass

        return min(score, 1.0), reasons

    def _decide_hydration_mode(self, context_usage: float) -> HydrationMode:
        """context_usage に応じて復元モードを決定"""
        if context_usage < 0.3:
            return HydrationMode.FULL
        elif context_usage < 0.6:
            return HydrationMode.COMPRESSED
        else:
            return HydrationMode.PARTIAL

    def _hydrate_context(
        self,
        target: ContinuationTarget,
        mode: HydrationMode,
    ) -> ContinuationContext:
        """ターゲットのコンテキストを復元"""
        context = ContinuationContext(
            target=target,
            hydration_mode=mode,
            token_budget_remaining=self.token_budget,
        )

        if mode == HydrationMode.FULL:
            # 完全復元
            context.compressed_summary = target.summary
            context.active_goals = target.active_goals
            context.recent_topics = target.recent_topics
            context.key_decisions = self._extract_key_decisions(target.summary)
            context.immediate_next_actions = target.next_actions
            context.restored_tokens = self._estimate_tokens(target.summary)

        elif mode == HydrationMode.COMPRESSED:
            # 圧縮復元
            context.compressed_summary = self._compress_summary(target.summary, 300)
            context.active_goals = target.active_goals[:3]
            context.recent_topics = target.recent_topics[:5]
            context.key_decisions = self._extract_key_decisions(target.summary)[:2]
            context.immediate_next_actions = target.next_actions[:2]
            context.restored_tokens = self._estimate_tokens(context.compressed_summary)

        else:  # PARTIAL
            # 部分復元 (最小限)
            context.compressed_summary = self._compress_summary(target.summary, 100)
            context.active_goals = target.active_goals[:1]
            context.recent_topics = target.recent_topics[:2]
            context.key_decisions = []
            context.immediate_next_actions = target.next_actions[:1]
            context.restored_tokens = self._estimate_tokens(context.compressed_summary)

        context.token_budget_remaining = max(
            0,
            self.token_budget - context.restored_tokens,
        )

        return context

    def _compress_summary(self, summary: str, max_tokens: int) -> str:
        """サマリーを圧縮"""
        if not summary:
            return ""

        # 簡易圧縮 (改行で分割して制限)
        sentences = summary.split("\n")
        compressed = []
        token_count = 0

        for sentence in sentences:
            sentence_tokens = len(sentence.split())
            if token_count + sentence_tokens > max_tokens:
                break
            compressed.append(sentence)
            token_count += sentence_tokens

        return "\n".join(compressed) if compressed else summary[:max_tokens * 4]

    def _extract_key_decisions(self, summary: str) -> List[str]:
        """重要な意思決定を抽出"""
        if not summary:
            return []

        decisions = []
        lines = summary.split("\n")

        for line in lines:
            line = line.strip()
            if any(kw in line.lower() for kw in ["decision", "決定", "選択", "adopt", "adopted"]):
                decisions.append(line)

        return decisions[:3]

    def _estimate_tokens(self, text: str) -> int:
        """テキストのトークン数を推定 (簡易)"""
        if not text:
            return 0
        # 日本語は 1 文字 ≈ 0.5 トークン、英語は 4 文字 ≈ 1 トークン
        japanese_chars = sum(1 for c in text if ord(c) > 0x2E80)
        english_chars = len(text) - japanese_chars
        return int(japanese_chars * 0.5 + english_chars * 0.25)

    def _stabilize_restored_context(self, context: ContinuationContext) -> ContinuationContext:
        """復元されたコンテキストを安定化"""
        # 重複除去
        context.active_goals = self._deduplicate_list(context.active_goals)
        context.recent_topics = self._deduplicate_list(context.recent_topics)

        context.stabilization_status = "stable"
        return context

    def _deduplicate_list(self, items: List[str]) -> List[str]:
        """リストの重複を除去 (順序保持)"""
        seen = set()
        result = []
        for item in items:
            if item not in seen:
                seen.add(item)
                result.append(item)
        return result

    def _update_telemetry_for_restore(self, context: ContinuationContext) -> None:
        """復元後のテレメトリ更新"""
        try:
            self.health_monitor.update_token_growth(
                current_tokens=context.restored_tokens,
                previous_tokens=0,
            )
            self.health_monitor.update_loop_risk(
                injection_count=0,
                recursion_depth=0,
            )
        except Exception:
            pass  # テレメトリ失敗は継続を停止しない

    def _get_cached_restore_result(self) -> ContinuationContext:
        """キャッシュされた復元結果を返す"""
        return ContinuationContext(
            target=ContinuationTarget(
                session_id="",
                title="",
                workspace_id="",
                confidence=0.0,
            ),
            hydration_mode=HydrationMode.FULL,
            stabilization_status="cooldown",
            telemetry_status="healthy",
        )

    def get_status_json(self) -> str:
        """現在の状態を JSON で出力"""
        return json.dumps({
            "token_budget": self.token_budget,
            "confidence_threshold": self.confidence_threshold,
            "last_restore_time": self._last_restore_time,
            "restore_cooldown": self._restore_cooldown,
        }, ensure_ascii=False, indent=2)

    # --- Ambiguity Resolution ---

    def resolve_ambiguity(
        self,
        query: str,
        candidates: List[ContinuationTarget],
    ) -> Tuple[ContinuationTarget, bool]:
        """
        複数候補時の曖昧さを解決。

        Args:
            query: ユーザー入力
            candidates: 候補リスト

        Returns:
            (resolved_candidate, was_ambiguous)
        """
        if len(candidates) <= 1:
            return candidates[0] if candidates else None, False

        # 最高スコアと2位との差が小さい場合は曖昧
        if len(candidates) >= 2:
            score_diff = candidates[0].confidence - candidates[1].confidence
            if score_diff < 0.15:
                # 曖昧性あり - ユーザーに確認が必要
                return self._ask_for_clarification(query, candidates)

        return candidates[0], False

    def _ask_for_clarification(
        self,
        query: str,
        candidates: List[ContinuationTarget],
    ) -> Tuple[ContinuationTarget, bool]:
        """
        曖昧さ解消のための確認メッセージを生成。

        実際のシステムではユーザーに返すメッセージを生成。
        ここでは最高スコア候補を返す（デフォルト動作）。
        """
        # 実際のシステムではここでユーザーに確認メッセージを返す
        # 例: "複数のプロジェクトが見つかりました。どちらを続けますか？\n1. ...\n2. ..."
        return candidates[0], True

    # --- Startup Continuation Loader ---

    def startup_continuation_loader(
        self,
        default_query: str = "",
        health_status: str = "healthy",
        context_usage: float = 0.0,
    ) -> Optional[ContinuationContext]:
        """
        起動時継続ローダー。

        起動時に自動的に継続状態を復元。

        Args:
            default_query: デフォルトのクエリ（ユーザー入力が無い場合）
            health_status: 現在のヘルス状態
            context_usage: 現在のコンテキスト使用率

        Returns:
            復元されたコンテキスト（継続対象が無い場合は None）
        """
        # ユーザー入力が無い場合はデフォルトクエリを使用
        query = default_query or ""

        # 継続意図を検出
        intent = self.detect_continuation_intent(query)

        if not intent.get("is_continuation"):
            return None

        # 信頼度が閾値未満の場合は継続しない
        if intent.get("confidence", 0.0) < self.confidence_threshold:
            return None

        # ターゲットを検索
        keyword = intent.get("project_keyword", "")
        workspace_id = intent.get("workspace_id", "")
        candidates = self.find_best_continuation_target(
            keyword, workspace_id, limit=5
        )

        if not candidates:
            return None

        # 曖昧さ解決
        target, was_ambiguous = self.resolve_ambiguity(query, candidates)

        if not target:
            return None

        # context_usage が高い場合は compressed/partial モードに強制
        if context_usage > 0.7:
            mode = HydrationMode.COMPRESSED
        elif context_usage > 0.9:
            mode = HydrationMode.PARTIAL
        else:
            mode = self._decide_hydration_mode(context_usage)

        # コンテキストを復元
        context = self.restore_context(target, context_usage)
        context.hydration_mode = mode  # モードを上書き

        return context


# --- Convenience ---

def create_continuation_orchestrator(
    workspace_root: Optional[str] = None,
    token_budget: int = 1000,
) -> ContinuationOrchestrator:
    """ContinuationOrchestrator のファクトリ"""
    return ContinuationOrchestrator(
        workspace_root=workspace_root,
        token_budget=token_budget,
    )
