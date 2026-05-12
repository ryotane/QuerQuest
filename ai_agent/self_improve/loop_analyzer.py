"""
LoopPatternAnalyzer - ループパターン分析モジュール

目的:
- 記録されたループ失敗ログから、ループしやすいパターンを分析
- 単純なキーワード頻度分析から始め、必要に応じて高度な分析へ拡張

設計原則:
- 分析は必要に応じて実行（リアルタイムではない）
- 結果はキャッシュ可能
- 既存のloop_logger.pyと連携
"""

import json
import os
from collections import Counter
from typing import Dict, List, Optional, Tuple


class LoopPatternAnalyzer:
    """ループパターン分析クラス"""

    def __init__(self, log_path: str = "logs/loop_failures.jsonl"):
        """
        Args:
            log_path: ループ失敗ログファイルのパス
        """
        self.log_path = log_path
        self._cache: Optional[Dict] = None
        self._cache_timestamp: float = 0

    def analyze(self, force: bool = False) -> Dict:
        """
        ループパターンを分析

        Args:
            force: キャッシュを無視して再分析するか

        Returns:
            分析結果（パターンごとの頻度、関連キーワード等）
        """
        # キャッシュチェック（簡易実装）
        if not force and self._cache and self._cache_timestamp > 0:
            # 簡易キャッシュ（ファイル更新時刻チェックは省略）
            pass

        if not os.path.exists(self.log_path):
            return {
                "total_failures": 0,
                "loop_types": {},
                "top_keywords": [],
                "patterns": {},
            }

        # ログ読み込み
        failures = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    failures.append(json.loads(line))

        # 分析
        loop_types = Counter(f.get("loop_type", "unknown") for f in failures)
        keywords = self._extract_keywords(failures)
        top_keywords = keywords.most_common(10)

        # パターン分析（簡易版：loop_typeごとのクエリ類似度）
        patterns = self._analyze_patterns(failures)

        result = {
            "total_failures": len(failures),
            "loop_types": dict(loop_types),
            "top_keywords": top_keywords,
            "patterns": patterns,
        }

        # キャッシュ更新
        self._cache = result
        self._cache_timestamp = 1  # 簡易実装

        return result

    def _extract_keywords(self, failures: List[Dict]) -> Counter:
        """
        失敗ログからキーワードを抽出

        Args:
            failures: 失敗ログのリスト

        Returns:
            キーワードの頻度カウンター
        """
        keywords = Counter()
        for failure in failures:
            query = failure.get("query", "")
            # 簡易キーワード抽出（空白区切り、長さが2以上の単語）
            words = [w for w in query.split() if len(w) >= 2]
            keywords.update(words)
        return keywords

    def _analyze_patterns(self, failures: List[Dict]) -> Dict:
        """
        パターン分析（簡易版）

        Args:
            failures: 失敗ログのリスト

        Returns:
            パターンごとの分析結果
        """
        patterns = {}
        for failure in failures:
            loop_type = failure.get("loop_type", "unknown")
            if loop_type not in patterns:
                patterns[loop_type] = {
                    "count": 0,
                    "examples": [],
                }
            patterns[loop_type]["count"] += 1
            if len(patterns[loop_type]["examples"]) < 3:
                patterns[loop_type]["examples"].append(failure.get("query", ""))

        return patterns

    def get_loop_avoidance_instructions(self) -> List[str]:
        """
        ループ回避指示を生成

        Returns:
            ループ回避指示のリスト
        """
        analysis = self.analyze()
        instructions = []

        # 頻度の高いloop_typeに基づく指示
        loop_types = analysis.get("loop_types", {})
        if "infinite_loop" in loop_types and loop_types["infinite_loop"] > 3:
            instructions.append(
                "注意: 過去に無限ループが発生しました。推論は簡潔に行い、必要以上に深く考えないでください。"
            )

        if "recursive_file_read" in loop_types and loop_types["recursive_file_read"] > 2:
            instructions.append(
                "注意: 過去に同一ファイルの再読取ループが発生しました。ファイル読取後は必ず結果を活用してください。"
            )

        # 頻度の高いキーワードに基づく指示
        top_keywords = analysis.get("top_keywords", [])
        if top_keywords:
            # 上位3キーワードを特定
            top_3 = [kw for kw, count in top_keywords[:3] if count >= 2]
            if top_3:
                instructions.append(
                    f"注意: '{'、'.join(top_3)}' に関連する質問では、簡潔に答えてください。"
                )

        return instructions
