"""
Runtime Metrics Collector

AI Workspace の生データを取得する軽量コレクタ。

特徴:
- 重いスキャンは避ける（ファイルサイズキャッシュ等）
- OSレベルの軽量メトリクスを優先
- telemetry loop を防止するため独立したロジック
"""

import os
import sys
import time
import resource
from typing import Dict, Optional


class RuntimeMetricsCollector:
    """
    Runtime メトリクス収集クラス。

    使用例:
        collector = RuntimeMetricsCollector(workspace_path="/path/to/workspace")
        metrics = collector.collect()
    """

    def __init__(self, workspace_path: str, cache_ttl: float = 10.0):
        """
        Args:
            workspace_path: 監視対象のワークスペースパス
            cache_ttl: ディレクトリサイズキャッシュの TTL (秒)
        """
        self.workspace_path = workspace_path
        self.cache_ttl = cache_ttl
        self._dir_size_cache = 0.0
        self._dir_size_timestamp = 0.0

    def collect(self) -> Dict:
        """
        全メトリクスを収集。

        Returns:
            lightweight metrics dict
        """
        return {
            "timestamp": time.time(),
            "context_usage": self._get_context_usage(),
            "memory_pressure": self._get_memory_pressure(),
            "loop_risk": self._get_loop_risk(),
            "token_growth": self._get_token_growth_trend(),
            "compression_efficiency": self._get_compression_efficiency(),
            "process_info": self._get_process_info(),
        }

    def _get_context_usage(self) -> float:
        """
        コンテキスト使用率を推定 (0.0 - 1.0)。

        workspace ディレクトリのサイズと最大許容サイズから計算。
        キャッシュを使用してオーバーヘッドを最小化。
        """
        now = time.time()
        if (now - self._dir_size_timestamp) < self.cache_ttl:
            return self._normalize_context_size(self._dir_size_cache)

        # ディレクトリサイズの軽量計算
        total_size = self._get_directory_size(self.workspace_path)
        self._dir_size_cache = total_size
        self._dir_size_timestamp = now

        return self._normalize_context_size(total_size)

    def _get_directory_size(self, path: str) -> float:
        """
        ディレクトリサイズの軽量計算。

        os.scanditer を使い、再帰的だが軽量に計算。
        """
        total_size = 0
        try:
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    # シンボリックリンク等を除く
                    if os.path.isfile(fp) and not os.path.islink(fp):
                        try:
                            total_size += os.path.getsize(fp)
                        except OSError:
                            pass
        except Exception:
            pass
        return total_size

    def _normalize_context_size(self, size_bytes: float) -> float:
        """
        コンテキストサイズを 0.0-1.0 に正規化。

        最大許容サイズを 1GB (1024^3 bytes) と仮定。
        """
        max_size = 1024 ** 3  # 1GB
        ratio = size_bytes / max_size
        return min(ratio, 1.0)

    def _get_memory_pressure(self) -> float:
        """
        メモリ圧力を取得 (0.0 - 1.0)。

        自身の RSS メモリ使用率を基準に計算。
        """
        try:
            # RSS (Resident Set Size) in bytes
            usage = resource.getrusage(resource.RUSAGE_SELF)
            rss_mb = usage.ru_maxrss / 1024  # macOS is in KB, Linux in KB too usually but check docs

            # 48GB Unified Memory の 10% を許容範囲の中心とする
            # 実際には RSS が増えるほど圧力が高まるとみなす
            # 例: 100MB -> 0.0, 10GB -> ~0.2, 20GB -> ~0.4
            # 単純に RSS / 48GB とする
            max_memory = 48 * 1024 * 1024 * 1024  # 48GB
            pressure = rss_mb * 1024 * 1024 / max_memory
            return min(pressure, 1.0)
        except Exception:
            return 0.0

    def _get_loop_risk(self) -> float:
        """
        Loop 危険度を簡易推定 (0.0 - 1.0)。

        直近の log.jsonl の更新頻度や深さから推定。
        実際の再帰深さは計測できないため、ファイルサイズの変化率等で代替。
        """
        log_path = os.path.join(self.workspace_path, "logs", "log.jsonl")
        if not os.path.exists(log_path):
            return 0.0

        try:
            size = os.path.getsize(log_path)
            # ログファイルが急激に大きくなっている場合は loop 危険度高め
            # 例: 1MB -> 0.0, 10MB -> 0.1, 100MB -> 0.5
            risk = min(size / (100 * 1024 * 1024), 1.0)  # 100MB を max とする
            return round(risk, 2)
        except Exception:
            return 0.0

    def _get_token_growth_trend(self) -> str:
        """
        Token 成長トレンドを推定。

        ログファイルのサイズ変化から推定（簡易版）。
        """
        log_path = os.path.join(self.workspace_path, "logs", "log.jsonl")
        if not os.path.exists(log_path):
            return "stable"

        try:
            size = os.path.getsize(log_path)
            if size > 50 * 1024 * 1024:  # 50MB 以上
                return "growing"
            return "stable"
        except Exception:
            return "stable"

    def _get_compression_efficiency(self) -> float:
        """
        Compression 効率を推定。

        実際の圧縮率は計測できないため、archive ディレクトリの比率等で代替。
        """
        archive_path = os.path.join(self.workspace_path, "archive")
        if not os.path.exists(archive_path):
            return 0.5  # デフォルト

        try:
            archive_size = self._get_directory_size(archive_path)
            workspace_size = self._dir_size_cache if self._dir_size_cache > 0 else self._get_directory_size(self.workspace_path)
            if workspace_size == 0:
                return 0.5
            ratio = archive_size / workspace_size
            return round(min(ratio, 1.0), 2)
        except Exception:
            return 0.5

    def _get_process_info(self) -> Dict:
        """
        自身のプロセス情報を取得。
        """
        try:
            return {
                "pid": os.getpid(),
                "rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
            }
        except Exception:
            return {}
