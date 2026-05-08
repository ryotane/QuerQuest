"""
Safety Guard - 統合ランタイム安全ゲート

全チェックを1関数で実行。
ブロック時は強制観測モードへ遷移。

設計原則:
- 1関数で全チェック (オーバーヘッド最小)
- observation-first (観測→実行の強制)
- low overhead (< 1ms)
- lightweight debug
"""

import time
import hashlib
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Set
from enum import Enum


class SafetyAction(Enum):
    """安全アクション"""
    ALLOW = "allow"           # 許可
    BLOCK = "block"           # 強制停止
    FORCE_OBSERVE = "force_observe"  # 強制観測モード


@dataclass
class SafetyResult:
    """安全チェック結果"""
    action: SafetyAction
    reason: str = ""
    blocked: bool = False
    force_observe: bool = False
    remaining_budget: int = 0
    debug_info: Dict = field(default_factory=dict)
    
    def __bool__(self):
        return not self.blocked


class SafetyGuard:
    """
    統合ランタイム安全ゲート。
    
    推論暴走を防止するための全チェックを1関数で実行。
    
    使用例:
        guard = SafetyGuard()
        
        # 推論ステップ前にチェック
        result = guard.check(
            step_type="reasoning",
            content="このコードを修正する必要がある",
            target="ai_agent/core/engine.py",
        )
        
        if result.blocked:
            # 観測を実行してから再試行
            ...
        
        # 観測ステップ前にチェック
        result = guard.check(
            step_type="observation",
            content="file_read",
            target="ai_agent/core/engine.py",
        )
        
        if result.action == SafetyAction.FORCE_OBSERVE:
            # 観測を強制
            ...
    """
    
    def __init__(
        self,
        max_reasoning_steps: int = 10,
        max_hypothesis_repeats: int = 3,
        max_same_file_reads: int = 3,
        observation_cooldown_ms: float = 500,
        debug: bool = False,
    ):
        """
        Args:
            max_reasoning_steps: 最大推論ステップ数
            max_hypothesis_repeats: 同一仮説の最大反復数
            max_same_file_reads: 同一ファイルの最大読取数
            observation_cooldown_ms: 観測間の最小間隔 (ms)
            debug: デバッグ出力有効化
        """
        self.max_reasoning_steps = max_reasoning_steps
        self.max_hypothesis_repeats = max_hypothesis_repeats
        self.max_same_file_reads = max_same_file_reads
        self.observation_cooldown_ms = observation_cooldown_ms
        self.debug = debug
        
        # 状態
        self.reasoning_steps: List[Dict] = []
        self.hypothesis_counts: Dict[str, int] = {}
        self.file_read_counts: Dict[str, int] = {}
        self.last_observation_time: float = 0
        self.total_checks: int = 0
        self.total_blocks: int = 0
        self.total_force_observe: int = 0
        
        # 推論暴走検出
        self.reasoning_history: List[str] = []
        self.max_history_size: int = 20
    
    def check(
        self,
        step_type: str,
        content: str,
        target: str = "",
        hypothesis: str = "",
    ) -> SafetyResult:
        """
        全安全チェックを1関数で実行。
        
        Args:
            step_type: "reasoning" or "observation"
            content: 推論/観測の内容
            target: ターゲット (ファイルパス等)
            hypothesis: 仮説 (推論時のみ)
            
        Returns:
            SafetyResult
        """
        self.total_checks += 1
        
        # 1. Reasoning Budgetチェック
        if step_type == "reasoning":
            result = self._check_reasoning_budget(content, hypothesis)
            if result.blocked:
                return result
        
        # 2. Hypothesis Limitチェック
        if hypothesis:
            result = self._check_hypothesis_limit(hypothesis)
            if result.blocked:
                return result
        
        # 3. Observation Enforcementチェック
        if step_type == "reasoning" and not self._has_recent_observation():
            result = self._force_observation()
            if result.force_observe:
                return result
        
        # 4. Recursive Detectionチェック
        if target:
            result = self._check_recursion(content, target)
            if result.blocked:
                return result
        
        # 5. Loop Controlチェック
        result = self._check_loop(content)
        if result.blocked:
            return result
        
        # 6. 成功 - 状態更新
        self._record_step(step_type, content, target, hypothesis)
        
        return SafetyResult(
            action=SafetyAction.ALLOW,
            remaining_budget=self.max_reasoning_steps - len(self.reasoning_steps),
            debug_info={
                "total_checks": self.total_checks,
                "reasoning_steps": len(self.reasoning_steps),
            }
        )
    
    def _check_reasoning_budget(
        self, content: str, hypothesis: str
    ) -> SafetyResult:
        """Reasoning Budgetチェック"""
        if len(self.reasoning_steps) >= self.max_reasoning_steps:
            self.total_blocks += 1
            return SafetyResult(
                action=SafetyAction.BLOCK,
                reason=f"reasoning_budget_exceeded ({len(self.reasoning_steps)}/{self.max_reasoning_steps})",
                blocked=True,
                remaining_budget=0,
                debug_info={"step_count": len(self.reasoning_steps)},
            )
        return SafetyResult(action=SafetyAction.ALLOW)
    
    def _check_hypothesis_limit(self, hypothesis: str) -> SafetyResult:
        """Hypothesis Limitチェック"""
        # 仮説をハッシュ化
        hyp_hash = hashlib.md5(hypothesis.encode()).hexdigest()[:8]
        
        # 類似仮説を検出
        similar_hyps = [
            h for h in self.hypothesis_counts.keys()
            if self._similarity(h, hyp_hash) > 0.7
        ]
        
        if similar_hyps:
            max_count = max(self.hypothesis_counts[h] for h in similar_hyps)
            if max_count >= self.max_hypothesis_repeats:
                self.total_blocks += 1
                return SafetyResult(
                    action=SafetyAction.BLOCK,
                    reason=f"hypothesis_limit_exceeded ({max_count}/{self.max_hypothesis_repeats})",
                    blocked=True,
                    debug_info={"hypothesis_hash": hyp_hash, "count": max_count},
                )
        
        return SafetyResult(action=SafetyAction.ALLOW)
    
    def _force_observation(self) -> SafetyResult:
        """強制観測モード"""
        self.total_force_observe += 1
        return SafetyResult(
            action=SafetyAction.FORCE_OBSERVE,
            reason="observation_required_before_reasoning",
            force_observe=True,
            debug_info={"force_observe_count": self.total_force_observe},
        )
    
    def _check_recursion(self, content: str, target: str) -> SafetyResult:
        """Recursive Detectionチェック"""
        # 同一ファイルの再読取検出
        read_count = self.file_read_counts.get(target, 0)
        if read_count >= self.max_same_file_reads:
            # 直近の推論が同一ファイルの読取のみなら暴走と判断
            recent_reasoning = self.reasoning_history[-3:] if self.reasoning_history else []
            if all(target in r for r in recent_reasoning):
                self.total_blocks += 1
                return SafetyResult(
                    action=SafetyAction.BLOCK,
                    reason=f"recursive_file_read ({target} x{read_count})",
                    blocked=True,
                    debug_info={"target": target, "read_count": read_count},
                )
        
        return SafetyResult(action=SafetyAction.ALLOW)
    
    def _check_loop(self, content: str) -> SafetyResult:
        """Loop Controlチェック"""
        # 推論履歴に同一内容が繰り返されているかチェック
        if len(self.reasoning_history) >= 3:
            recent = self.reasoning_history[-3:]
            # 簡易類似度チェック
            if self._similarity(content, recent[0]) > 0.8 and \
               self._similarity(content, recent[1]) > 0.8:
                self.total_blocks += 1
                return SafetyResult(
                    action=SafetyAction.BLOCK,
                    reason="infinite_loop_detected",
                    blocked=True,
                    debug_info={"recent_reasoning": recent},
                )
        
        return SafetyResult(action=SafetyAction.ALLOW)
    
    def _has_recent_observation(self) -> bool:
        """直近に観測が行われたか"""
        if self.last_observation_time == 0:
            return False
        elapsed_ms = (time.time() - self.last_observation_time) * 1000
        return elapsed_ms >= self.observation_cooldown_ms
    
    def _record_step(
        self,
        step_type: str,
        content: str,
        target: str,
        hypothesis: str,
    ):
        """ステップ記録"""
        if step_type == "reasoning":
            self.reasoning_steps.append({
                "content": content,
                "target": target,
                "hypothesis": hypothesis,
                "timestamp": time.time(),
            })
            
            # 推論履歴に追加
            self.reasoning_history.append(content)
            if len(self.reasoning_history) > self.max_history_size:
                self.reasoning_history.pop(0)
        
        elif step_type == "observation":
            self.last_observation_time = time.time()
        
        # 仮説カウント更新
        if hypothesis:
            hyp_hash = hashlib.md5(hypothesis.encode()).hexdigest()[:8]
            self.hypothesis_counts[hyp_hash] = self.hypothesis_counts.get(hyp_hash, 0) + 1
        
        # ファイル読取カウント更新
        if target:
            self.file_read_counts[target] = self.file_read_counts.get(target, 0) + 1
    
    def reset(self):
        """状態をリセット"""
        self.reasoning_steps.clear()
        self.hypothesis_counts.clear()
        self.file_read_counts.clear()
        self.reasoning_history.clear()
        self.last_observation_time = 0
    
    def get_status(self) -> Dict:
        """現在の状態を出力"""
        return {
            "total_checks": self.total_checks,
            "total_blocks": self.total_blocks,
            "total_force_observe": self.total_force_observe,
            "reasoning_steps": len(self.reasoning_steps),
            "remaining_budget": self.max_reasoning_steps - len(self.reasoning_steps),
            "hypothesis_count": len(self.hypothesis_counts),
            "file_read_targets": len(self.file_read_counts),
        }
    
    @staticmethod
    def _similarity(a: str, b: str) -> float:
        """簡易類似度 (0.0 - 1.0)"""
        if not a or not b:
            return 0.0
        
        # 共通単語数 / 総単語数
        words_a = set(a.lower().split())
        words_b = set(b.lower().split())
        
        if not words_a or not words_b:
            return 0.0
        
        intersection = words_a & words_b
        union = words_a | words_b
        
        return len(intersection) / len(union) if union else 0.0


# =========================================
# Project_08: Recursive Collapse Prevention Layer
# =========================================

class CollapsePreventionLayer:
    """
    Recursive Collapse Prevention Layer (Project_08)
    
    目的: 「考え続ける前に小さく実行する」を強制
    
    重点方針:
    - next-action-only (1アクションのみ)
    - single-step execution (単一ステップ実行)
    - forced execution transition (実行遷移の強制)
    - plan compression (計画圧縮)
    - anti-meta-reasoning (メタ推論抑制)
    - planning TTL (計画の有効期限)
    - lightweight orchestration (軽量オーケストレーション)
    - observation-first (観測→実行)
    - execution-first (実行最優先)
    
    設計原則:
    - low overhead (< 1ms)
    - low token usage
    - no recursive debug
    - no heavy runtime
    """
    
    def __init__(
        self,
        planning_ttl_seconds: float = 5.0,
        planning_ttl_steps: int = 10,
        max_plan_length: int = 3,
        anti_meta_threshold: int = 2,
        debug: bool = False,
    ):
        """
        Args:
            planning_ttl_seconds: 計画の有効期限 (秒)
            planning_ttl_steps: 計画の有効期限 (ステップ数)
            max_plan_length: 最大計画アクション数 (next-action-only)
            anti_meta_threshold: メタ推論検出閾値
            debug: デバッグ出力有効化
        """
        self.planning_ttl_seconds = planning_ttl_seconds
        self.planning_ttl_steps = planning_ttl_steps
        self.max_plan_length = max_plan_length
        self.anti_meta_threshold = anti_meta_threshold
        self.debug = debug
        
        # 状態
        self.plan_start_time: float = 0
        self.plan_step_count: int = 0
        self.current_plan: List[str] = []
        self.last_action_type: str = ""
        self.meta_reasoning_count: int = 0
        self.total_execution_transitions: int = 0
        self.total_plan_compressions: int = 0
        self.total_meta_blocks: int = 0
        
        # メタ推論検出用キーワード
        self.meta_keywords = [
            "設計", "アーキテクチャ", "再検討", "見直し",
            "比較", "検討", "評価", "判断",
            "なぜ", "どうして", "根本原因",
            "戦略", "方針", "原則"
        ]
    
    def check_planning_ttl(self) -> tuple[bool, str]:
        """
        計画の有効期限をチェック
        
        Returns:
            (is_valid, reason)
        """
        if self.plan_start_time == 0:
            return True, ""
        
        # 時間TTLチェック
        elapsed = time.time() - self.plan_start_time
        if elapsed > self.planning_ttl_seconds:
            self.total_plan_compressions += 1
            return False, f"planning_ttl_exceeded (time:{elapsed:.1f}s)"
        
        # ステップTTLチェック
        if self.plan_step_count >= self.planning_ttl_steps:
            self.total_plan_compressions += 1
            return False, f"planning_ttl_exceeded (steps:{self.plan_step_count}/{self.planning_ttl_steps})"
        
        return True, ""
    
    def enforce_next_action_only(self, plan: List[str]) -> List[str]:
        """
        計画をnext-action-onlyに圧縮
        
        Args:
            plan: 元の計画アクションリスト
            
        Returns:
            圧縮された計画 (最大1アクション)
        """
        if len(plan) <= 1:
            return plan
        
        self.total_plan_compressions += 1
        compressed = [plan[0]]
        
        if self.debug:
            print(f"📦 PLAN COMPRESSED: {len(plan)} -> {len(compressed)} action(s)")
        
        return compressed
    
    def detect_meta_reasoning(self, content: str) -> bool:
        """
        メタ推論を検出
        
        Args:
            content: 推論内容
            
        Returns:
            メタ推論 detected
        """
        content_lower = content.lower()
        meta_count = sum(1 for kw in self.meta_keywords if kw in content_lower)
        
        if meta_count >= self.anti_meta_threshold:
            self.meta_reasoning_count += 1
            return True
        
        return False
    
    def force_execution_transition(
        self,
        step_type: str,
        content: str,
        plan: List[str]
    ) -> tuple[bool, str]:
        """
        実行遷移を強制
        
        Args:
            step_type: "reasoning" or "observation" or "execution"
            content: 内容
            plan: 現在の計画
            
        Returns:
            (is_allowed, reason)
        """
        # 計画TTLチェック
        is_valid, reason = self.check_planning_ttl()
        if not is_valid:
            return False, reason
        
        # メタ推論検出
        if self.detect_meta_reasoning(content):
            self.total_meta_blocks += 1
            return False, f"meta_reasoning_detected (count:{self.meta_reasoning_count})"
        
        # next-action-only強制
        if step_type == "reasoning" and len(plan) > self.max_plan_length:
            compressed = self.enforce_next_action_only(plan)
            return False, f"plan_compressed ({len(plan)} -> {len(compressed)})"
        
        # 実行遷移カウント
        if step_type == "execution":
            self.total_execution_transitions += 1
            self.plan_step_count = 0  # リセット
            self.plan_start_time = time.time()  # 更新
        
        # 観測→実行の強制
        if step_type == "reasoning" and self.last_action_type != "execution":
            if self.plan_step_count == 0:
                return False, "forced_observation_before_execution"
        
        self.last_action_type = step_type
        self.plan_step_count += 1
        
        return True, ""
    
    def reset_plan(self):
        """計画をリセット"""
        self.plan_start_time = 0
        self.plan_step_count = 0
        self.current_plan.clear()
        self.last_action_type = ""
        self.meta_reasoning_count = 0
    
    def get_status(self) -> Dict:
        """現在の状態を出力"""
        elapsed = time.time() - self.plan_start_time if self.plan_start_time > 0 else 0
        return {
            "total_execution_transitions": self.total_execution_transitions,
            "total_plan_compressions": self.total_plan_compressions,
            "total_meta_blocks": self.total_meta_blocks,
            "plan_ttl_remaining": max(0, self.planning_ttl_seconds - elapsed),
            "plan_steps_remaining": max(0, self.planning_ttl_steps - self.plan_step_count),
            "current_plan_length": len(self.current_plan),
            "meta_reasoning_count": self.meta_reasoning_count,
        }
