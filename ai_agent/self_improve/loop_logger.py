"""
LoopFailureLogger - ループ失敗ログ記録モジュール

目的:
- ループ発生時のコンテキストを記録し、後続の分析・回避に活用する
- JSONL形式で軽量に記録

設計原則:
- 記録は非同期ではなく同期（オーバーヘッド最小）
- 失敗コンテキストのみ記録（個人情報除外）
- 既存logsディレクトリを活用
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Optional


class LoopFailureLogger:
    """ループ失敗ログ記録クラス"""

    def __init__(self, log_path: str = "logs/loop_failures.jsonl"):
        """
        Args:
            log_path: ログファイルのパス
        """
        self.log_path = log_path
        # logsディレクトリが存在することを確認
        os.makedirs(os.path.dirname(log_path), exist_ok=True)

    def log_loop_failure(
        self,
        query: str,
        loop_type: str,
        reasoning_history: List[str],
        detected_pattern: Optional[str] = None,
        metadata: Optional[Dict] = None,
    ) -> Dict:
        """
        ループ失敗を記録

        Args:
            query: ユーザーの質問（ループの原因となった入力）
            loop_type: ループの種類（例: "infinite_loop", "recursive_file_read", "hypothesis_limit"）
            reasoning_history: ループ検知時の推論履歴
            detected_pattern: 検知されたパターン（任意）
            metadata: 追加メタデータ（任意）

        Returns:
            記録したレコード
        """
        record = {
            "timestamp": datetime.utcnow().isoformat(),
            "query": query,
            "loop_type": loop_type,
            "reasoning_history": reasoning_history[-5:],  # 直近5件のみ記録（容量抑制）
            "detected_pattern": detected_pattern,
            "metadata": metadata or {},
        }

        # JSONL形式で追記
        with open(self.log_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

        return record

    def get_recent_failures(self, count: int = 10) -> List[Dict]:
        """
        最近の失敗ログを取得

        Args:
            count: 取得件数

        Returns:
            失敗ログのリスト
        """
        if not os.path.exists(self.log_path):
            return []

        failures = []
        with open(self.log_path, "r", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    failures.append(json.loads(line))

        # 最近の順にソート（timestampベース）
        failures.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
        return failures[:count]

    def clear_logs(self):
        """ログをクリア（開発用）"""
        if os.path.exists(self.log_path):
            os.remove(self.log_path)
