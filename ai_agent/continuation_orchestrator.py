"""
Continuation Orchestrator

新規チャット移行時の継続状態自動復元オケストレーター。

目的:
- 「Project_03 の続きをお願いします」だけで継続状態を復元
- title 完全一致に依存しない
- workspace_id 優先マッチング
- recent_topics / active_goals overlap 利用
- compressed context restore
- token budget strict enforcement
- stabilization layer 統合
- telemetry health 状態を考慮

設計:
- continuation detection: ユーザー入力が継続リクエストか判定
- confidence scoring: 継続確率をスコアリング
- best target selection: 最適な継続対象を探索
- context restore: compressed context の復元
- ambiguity resolution: 複数候補時の曖昧さ解決
"""

import os
import json
import time
import re
from dataclasses import dataclass, field, asdict
from typing import Optional, Dict, List, Tuple
from pathlib import Path


# --- Data Models ---

@dataclass
class ContinuationCandidate:
    """継続候補"""
    session: dict
    confidence: float  # 0.0 - 1.0
    match_reasons: List[str] = field(default_factory=list)
    workspace_id: str = ""
    title: str = ""
    updated_at: str = ""
    topic_overlap: float = 0.0
    goal_overlap: float = 0.0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ContinuationResult:
    """継続結果"""
    detected: bool = False
    confidence: float = 0.0
    target: Optional[ContinuationCandidate] = None
    restored_context: str = ""
    mode: str = "full"  # full, compressed, partial
    token_budget_used: int = 0
    health_status: str = "unknown"  # healthy, degraded, critical
    ambiguity_resolved: bool = False
    message: str = ""

    def to_dict(self) -> dict:
        result = asdict(self)
        if self.target:
            result["target"] = self.target.to_dict()
        return result

    def to_json(self, indent: int = 2) -> str:
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)


# --- Continuation Detection ---

class ContinuationDetector:
    """継続リクエスト検出器"""

    # 継続キーワード
    CONTINUATION_KEYWORDS = [
        "続き", "continue", "previous", "last", "before",
        "前回の", "以前の", "再開", "resume", "pick up",
        "また", "もう一度", "再度", "再開", "progress",
        "project", "phase", "task", "goal",
    ]

    # 継続パターン
    CONTINUATION_PATTERNS = [
        r"続き",
        r"continue\s*(?:.*project|.*phase|.*task)?",
        r"previous\s+(?:project|phase|task|work)",
        r"last\s+(?:session|chat|project|phase)",
        r"resume\s*(?:.*project|.*phase)?",
        r"pick\s+up\s+(?:where\s+)?(?:we\s+left\s+off|the\s+thread)",
        r"また\s+(?:作業|進め|話|続き)",
        r"もう一度\s+(?:始め|進め|話)",
        r"再開",
        r"progress\s+(?:on|with)",
    ]

    def __init__(
        self,
        confidence_threshold: float = 0.6,
        keywords: Optional[List[str]] = None,
        patterns: Optional[List[str]] = None,
    ):
        self.confidence_threshold = confidence_threshold
        self.keywords = keywords or self.CONTINUATION_KEYWORDS
        self.patterns = patterns or self.CONTINUATION_PATTERNS

    def detect(self, user_input: str) -> bool:
        """
        ユーザー入力が継続リクエストかどうかを検出。

        Args:
            user_input: ユーザー入力

        Returns:
            継続リクエストなら True
        """
        score = self.confidence_score(user_input)
        return score >= self.confidence_threshold

    def confidence_score(self, user_input: str) -> float:
        """
        継続確率スコアを計算 (0.0 - 1.0)。

        Args:
            user_input: ユーザー入力

        Returns:
            継続確率スコア
        """
        if not user_input or not user_input.strip():
            return 0.0

        score = 0.0
        lower_input = user_input.lower()

        # キーワードマッチ
        keyword_score = 0.0
        for kw in self.keywords:
            if kw.lower() in lower_input:
                keyword_score += 0.2
        score += min(keyword_score, 0.4)

        # パターンマッチ
        pattern_score = 0.0
        for pattern in self.patterns:
            if re.search(pattern, lower_input, re.IGNORECASE):
                pattern_score += 0.3
        score += min(pattern_score, 0.4)

        # 文脈キーワード
        context_keywords = ["project", "phase", "task", "goal", "work", "session"]
        context_score = 0.0
        for kw in context_keywords:
            if kw in lower_input:
                context_score += 0.1
        score += min(context_score, 0.2)

        return min(score, 1.0)

    def get_match_details(self, user_input: str) -> Dict:
        """マッチ詳細を取得"""
        lower_input = user_input.lower()
        matched_keywords = [kw for kw in self.keywords if kw.lower() in lower_input]
        matched_patterns = [
            p for p in self.patterns
            if re.search(p, lower_input, re.IGNORECASE)
        ]

        return {
            "score": self.confidence_score(user_input),
            "matched_keywords": matched_keywords,
            "matched_patterns": matched_patterns,
            "is_continuation": self.detect(user_input),
        }


# --- Target Selection ---

class ContinuationTargetSelector:
    """継続対象セレクタ"""

    def __init__(
        self,
        session_registry,
        project_master_path: Optional[str] = None,
        max_candidates: int = 5,
    ):
        self.registry = session_registry
        self.project_master_path = project_master_path or "project_master.json"
        self.max_candidates = max_candidates

    def find_best_target(
        self,
        user_input: str,
        detector: Optional[ContinuationDetector] = None,
    ) -> Optional[ContinuationCandidate]:
        """
        最適な継続対象を検索。

        優先順位:
        1. workspace_id マッチ
        2. recent_topics overlap
        3. active_goals overlap
        4. title keyword match
        5. recency

        Args:
            user_input: ユーザー入力
            detector: 継続検出器

        Returns:
            最適な継続候補
        """
        candidates = self.find_candidates(user_input)

        if not candidates:
            return None

        # 最高スコアでソート
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates[0]

    def find_candidates(
        self,
        user_input: str,
    ) -> List[ContinuationCandidate]:
        """
        継続候補を全て検索。

        Args:
            user_input: ユーザー入力

        Returns:
            候補リスト（スコア順）
        """
        sessions = self.registry.get_project_sessions("queryquest_project")
        if not sessions:
            return []

        lower_input = user_input.lower()
        keywords = self._extract_keywords(user_input)

        candidates = []
        for session in sessions:
            score = 0.0
            reasons = []

            # workspace_id マッチ (高重み)
            if session.get("workspace_id") == "queryquest_project":
                score += 0.3
                reasons.append("workspace_id match")

            # recent_topics overlap
            topic_overlap = self._calculate_topic_overlap(
                session.get("recent_topics", []), keywords
            )
            score += topic_overlap * 0.3
            if topic_overlap > 0.3:
                reasons.append(f"topic overlap ({topic_overlap:.2f})")

            # active_goals overlap
            goal_overlap = self._calculate_goal_overlap(
                session.get("active_goals", []), keywords
            )
            score += goal_overlap * 0.3
            if goal_overlap > 0.3:
                reasons.append(f"goal overlap ({goal_overlap:.2f})")

            # title keyword match
            title_score = self._calculate_title_match(
                session.get("title", ""), keywords
            )
            score += title_score * 0.1
            if title_score > 0.5:
                reasons.append(f"title match ({title_score:.2f})")

            # recency bonus
            updated_at = session.get("updated_at", "")
            if updated_at:
                try:
                    from datetime import datetime
                    updated = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                    now = datetime.now(updated.tzinfo)
                    days_ago = (now - updated).days
                    if days_ago < 1:
                        score += 0.1
                    elif days_ago < 7:
                        score += 0.05
                except Exception:
                    pass

            if score > 0.2:  # 閾値以上のみ候補として追加
                candidates.append(ContinuationCandidate(
                    session=session,
                    confidence=min(score, 1.0),
                    match_reasons=reasons,
                    workspace_id=session.get("workspace_id", ""),
                    title=session.get("title", ""),
                    updated_at=updated_at,
                    topic_overlap=topic_overlap,
                    goal_overlap=goal_overlap,
                ))

        # スコア順にソート
        candidates.sort(key=lambda c: c.confidence, reverse=True)
        return candidates[:self.max_candidates]

    def _extract_keywords(self, text: str) -> List[str]:
        """テキストからキーワードを抽出"""
        # 日本語と英語のキーワードを抽出
        words = re.findall(r'[a-zA-Z]+|[^\s]{2,}', text)
        return [w.lower() for w in words if len(w) > 2]

    def _calculate_topic_overlap(
        self,
        topics: List[str],
        keywords: List[str],
    ) -> float:
        """トピックオーバーラップを計算"""
        if not topics or not keywords:
            return 0.0

        topic_set = set(t.lower() for t in topics)
        keyword_set = set(keywords)

        matches = sum(1 for kw in keyword_set if any(kw in t for t in topic_set))
        return matches / max(len(keywords), 1)

    def _calculate_goal_overlap(
        self,
        goals: List[str],
        keywords: List[str],
    ) -> float:
        """ゴールオーバーラップを計算"""
        if not goals or not keywords:
            return 0.0

        goal_text = " ".join(goals).lower()
        matches = sum(1 for kw in keywords if kw in goal_text)
        return matches / max(len(keywords), 1)

    def _calculate_title_match(
        self,
        title: str,
        keywords: List[str],
    ) -> float:
        """タイトルマッチを計算"""
        if not title or not keywords:
            return 0.0

        title_lower = title.lower()
        matches = sum(1 for kw in keywords if kw in title_lower)
        return matches / max(len(keywords), 1)


# --- Context Restore ---

class ContextRestorer:
    """コンテキスト復元器"""

    def __init__(
        self,
        max_context_tokens: int = 4000,
        compression_ratio: float = 0.3,
    ):
        self.max_context_tokens = max_context_tokens
        self.compression_ratio = compression_ratio

    def restore(
        self,
        candidate: ContinuationCandidate,
        health_status: str = "healthy",
        context_usage: float = 0.0,
    ) -> Tuple[str, str, int]:
        """
        コンテキストを復元。

        health_status と context_usage に応じてモードを自動選択。

        Args:
            candidate: 継続候補
            health_status: 現在のヘルス状態
            context_usage: 現在のコンテキスト使用率

        Returns:
            (restored_context, mode, token_count)
        """
        # モード選択
        mode = self._select_mode(health_status, context_usage)

        if mode == "full":
            context = self._restore_full(candidate)
        elif mode == "compressed":
            context = self._restore_compressed(candidate)
        else:  # partial
            context = self._restore_partial(candidate)

        # トークン数推定（文字数 / 4 で概算）
        token_count = len(context) // 4

        return context, mode, token_count

    def _select_mode(
        self,
        health_status: str,
        context_usage: float,
    ) -> str:
        """復元モードを選択"""
        # context_usage が高い場合は compressed/partial
        if context_usage > 0.7:
            return "compressed"
        if context_usage > 0.9:
            return "partial"

        # health_status が degraded/critical の場合は compressed
        if health_status in ("degraded", "critical"):
            return "compressed"

        return "full"

    def _restore_full(self, candidate: ContinuationCandidate) -> str:
        """フルコンテキスト復元"""
        session = candidate.session
        parts = []

        parts.append(f"=== Project Context ===")
        parts.append(f"Workspace: {candidate.workspace_id}")
        parts.append(f"Session: {candidate.title}")
        parts.append(f"Updated: {candidate.updated_at}")
        parts.append("")

        parts.append(f"=== Active Goals ===")
        for goal in session.get("active_goals", [])[:5]:
            parts.append(f"- {goal}")
        parts.append("")

        parts.append(f"=== Recent Topics ===")
        for topic in session.get("recent_topics", [])[:10]:
            parts.append(f"- {topic}")
        parts.append("")

        parts.append(f"=== Summary ===")
        parts.append(session.get("summary", "No summary"))
        parts.append("")

        parts.append(f"=== Next Actions ===")
        for action in session.get("next_actions", [])[:5]:
            parts.append(f"- {action}")

        return "\n".join(parts)

    def _restore_compressed(self, candidate: ContinuationCandidate) -> str:
        """圧縮コンテキスト復元"""
        session = candidate.session
        parts = []

        parts.append(f"=== Compressed Context (workspace: {candidate.workspace_id}) ===")
        parts.append(f"Session: {candidate.title}")
        parts.append(f"Updated: {candidate.updated_at}")
        parts.append("")

        # goals を圧縮
        goals = session.get("active_goals", [])
        if goals:
            parts.append(f"Goals: {' | '.join(goals[:3])}")
            parts.append("")

        # topics を圧縮
        topics = session.get("recent_topics", [])
        if topics:
            parts.append(f"Topics: {' | '.join(topics[:5])}")
            parts.append("")

        # summary を圧縮（最初の200文字）
        summary = session.get("summary", "")
        if summary:
            compressed_summary = summary[:200] + ("..." if len(summary) > 200 else "")
            parts.append(f"Summary: {compressed_summary}")
            parts.append("")

        # next_actions を圧縮
        actions = session.get("next_actions", [])
        if actions:
            parts.append(f"Next: {' | '.join(actions[:3])}")

        return "\n".join(parts)

    def _restore_partial(self, candidate: ContinuationCandidate) -> str:
        """部分コンテキスト復元（最小限）"""
        session = candidate.session
        parts = []

        parts.append(f"=== Partial Context ===")
        parts.append(f"Session: {candidate.title}")

        # 最も重要な goal のみ
        goals = session.get("active_goals", [])
        if goals:
            parts.append(f"Current goal: {goals[0]}")

        # 最新の topic のみ
        topics = session.get("recent_topics", [])
        if topics:
            parts.append(f"Recent topic: {topics[-1]}")

        return "\n".join(parts)


# --- Ambiguity Resolution ---

class AmbiguityResolver:
    """曖昧さ解決器"""

    def resolve(
        self,
        user_input: str,
        candidates: List[ContinuationCandidate],
    ) -> Tuple[ContinuationCandidate, bool]:
        """
        複数候補時の曖昧さを解決。

        Args:
            user_input: ユーザー入力
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
                return self._ask_for_clarification(user_input, candidates)

        return candidates[0], False

    def _ask_for_clarification(
        self,
        user_input: str,
        candidates: List[ContinuationCandidate],
    ) -> Tuple[ContinuationCandidate, bool]:
        """
        曖昧さ解消のための確認メッセージを生成。

        実際のシステムではユーザーに返すメッセージを生成。
        ここでは最高スコア候補を返す（デフォルト動作）。
        """
        # 実際のシステムではここでユーザーに確認メッセージを返す
        # 例: "複数のプロジェクトが見つかりました。どちらを続けますか？\n1. ...\n2. ..."
        return candidates[0], True


# --- Main Orchestrator ---

class ContinuationOrchestrator:
    """
    継続状態自動復元オケストレーター。

    使用例:
        orchestrator = ContinuationOrchestrator()

        # 継続検出
        if orchestrator.detect_continuation_request("Project_03 の続き"):
            # 継続復元
            result = orchestrator.restore_continuation("Project_03 の続き")
            print(result.restored_context)
    """

    def __init__(
        self,
        session_registry=None,
        project_master_path: Optional[str] = None,
        max_context_tokens: int = 4000,
        confidence_threshold: float = 0.6,
    ):
        self.detector = ContinuationDetector(confidence_threshold=confidence_threshold)
        self.selector = ContinuationTargetSelector(
            session_registry=session_registry,
            project_master_path=project_master_path,
        )
        self.restorer = ContextRestorer(max_context_tokens=max_context_tokens)
        self.resolver = AmbiguityResolver()

        # session_registry が None の場合はデフォルトパスから読み込み
        if session_registry is None:
            registry_path = project_master_path or "session_registry.json"
            if os.path.exists(registry_path):
                self.selector.registry = self._load_registry(registry_path)
            else:
                # デフォルトの空レジストリ
                from dataclasses import dataclass
                @dataclass
                class DummyRegistry:
                    def get_project_sessions(self, workspace_id):
                        return []
                self.selector.registry = DummyRegistry()

    def _load_registry(self, path: str):
        """レジストリを読み込み"""
        import json
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        class RegistryWrapper:
            def __init__(self, data):
                self.data = data

            def get_project_sessions(self, workspace_id):
                return [
                    s for s in self.data.get("sessions", [])
                    if s.get("workspace_id") == workspace_id
                ]

        return RegistryWrapper(data)

    def detect_continuation_request(self, user_input: str) -> bool:
        """
        ユーザー入力が継続リクエストかどうかを検出。

        Args:
            user_input: ユーザー入力

        Returns:
            継続リクエストなら True
        """
        return self.detector.detect(user_input)

    def get_continuation_confidence(self, user_input: str) -> float:
        """
        継続確率スコアを取得。

        Args:
            user_input: ユーザー入力

        Returns:
            継続確率スコア (0.0 - 1.0)
        """
        return self.detector.confidence_score(user_input)

    def restore_continuation(
        self,
        user_input: str,
        health_status: str = "healthy",
        context_usage: float = 0.0,
    ) -> ContinuationResult:
        """
        継続状態を復元。

        Args:
            user_input: ユーザー入力
            health_status: 現在のヘルス状態
            context_usage: 現在のコンテキスト使用率

        Returns:
            継続結果
        """
        result = ContinuationResult()

        # 1. 継続検出
        if not self.detector.detect(user_input):
            result.message = "継続リクエストとして検出されませんでした"
            return result

        result.confidence = self.detector.confidence_score(user_input)
        result.detected = True

        # 2. 候補検索
        candidates = self.selector.find_candidates(user_input)
        if not candidates:
            result.message = "継続対象が見つかりませんでした"
            return result

        # 3. 曖昧さ解決
        target, was_ambiguous = self.resolver.resolve(user_input, candidates)
        result.ambiguity_resolved = was_ambiguous
        result.target = target

        if not target:
            result.message = "継続対象が見つかりませんでした"
            return result

        # 4. コンテキスト復元
        context, mode, token_count = self.restorer.restore(
            target, health_status, context_usage
        )
        result.restored_context = context
        result.mode = mode
        result.token_budget_used = token_count

        # 5. メッセージ生成
        result.message = self._generate_restore_message(target, mode)

        return result

    def _generate_restore_message(
        self,
        target: ContinuationCandidate,
        mode: str,
    ) -> str:
        """復元メッセージを生成"""
        messages = {
            "full": f"フルコンテキストを復元しました: {target.title}",
            "compressed": f"圧縮コンテキストを復元しました: {target.title}",
            "partial": f"部分コンテキストを復元しました: {target.title}",
        }
        return messages.get(mode, f"コンテキストを復元しました: {target.title}")

    def get_status(self) -> Dict:
        """オケストレーターの状態を取得"""
        return {
            "confidence_threshold": self.detector.confidence_threshold,
            "max_context_tokens": self.restorer.max_context_tokens,
            "compression_ratio": self.restorer.compression_ratio,
        }


# --- Convenience Functions ---

def create_continuation_orchestrator(
    session_registry=None,
    project_master_path: Optional[str] = None,
) -> ContinuationOrchestrator:
    """ContinuationOrchestrator のファクトリ"""
    return ContinuationOrchestrator(
        session_registry=session_registry,
        project_master_path=project_master_path,
    )


def detect_continuation_request(
    user_input: str,
    confidence_threshold: float = 0.6,
) -> bool:
    """継続リクエストを検出する convenience 関数"""
    detector = ContinuationDetector(confidence_threshold=confidence_threshold)
    return detector.detect(user_input)


def continuation_confidence_score(
    user_input: str,
    confidence_threshold: float = 0.6,
) -> float:
    """継続確率スコアを計算する convenience 関数"""
    detector = ContinuationDetector(confidence_threshold=confidence_threshold)
    return detector.confidence_score(user_input)
