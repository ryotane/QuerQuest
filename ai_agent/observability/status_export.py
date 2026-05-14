"""
Status Export Module

Health Monitor の結果を JSON 形式でエクスポートする。

使用例:
    exporter = StatusExporter(workspace_root="/path/to/workspace")
    exporter.export()  # デフォルトパスにエクスポート
    exporter.export(filepath="/custom/path/status.json")
"""

import json
import os
import time
from pathlib import Path
from typing import Optional

from .health_monitor import HealthMonitor


class StatusExporter:
    """Health Status エクスポート"""

    DEFAULT_DIR = "logs"
    DEFAULT_FILENAME = "health_status.json"

    def __init__(
        self,
        workspace_root: Optional[str] = None,
        output_dir: Optional[str] = None,
    ):
        self.workspace_root = workspace_root or os.getcwd()
        self.output_dir = output_dir or os.path.join(self.workspace_root, self.DEFAULT_DIR)

    def _get_filepath(self, filename: Optional[str] = None) -> str:
        """出力ファイルパスを取得"""
        if filename:
            return os.path.join(self.output_dir, filename)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        return os.path.join(self.output_dir, f"health_status_{timestamp}.json")

    def export(
        self,
        monitor: Optional[HealthMonitor] = None,
        filepath: Optional[str] = None,
        pretty: bool = True,
    ) -> str:
        """
        Health Status を JSON ファイルにエクスポート。

        Args:
            monitor: HealthMonitor インスタンス (新規作成する場合)
            filepath: 出力先パス (None の場合はデフォルトパス)
            pretty: 整形出力

        Returns:
            出力された JSON 文字列
        """
        if monitor is None:
            monitor = HealthMonitor(workspace_root=self.workspace_root)

        status = monitor.get_status()
        json_str = status.to_json(indent=2 if pretty else None)

        # ディレクトリ作成
        if filepath:
            os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        else:
            os.makedirs(self.output_dir, exist_ok=True)

        # ファイル出力
        output_path = filepath or self._get_filepath()
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(json_str)

        return json_str

    def export_latest(self, monitor: Optional[HealthMonitor] = None) -> str:
        """最新ステータスをデフォルトパスにエクスポート"""
        return self.export(monitor=monitor, pretty=True)

    def read_latest(self) -> Optional[dict]:
        """最新のステータスファイルを读取"""
        import glob

        pattern = os.path.join(self.output_dir, "health_status_*.json")
        files = glob.glob(pattern)

        if not files:
            return None

        # 最新ファイルを取得
        latest = max(files, key=os.path.getmtime)

        with open(latest, "r", encoding="utf-8") as f:
            return json.load(f)


def export_health_status(
    workspace_root: Optional[str] = None,
    filepath: Optional[str] = None,
) -> str:
    """ヘルスステータスをエクスポートする convenience 関数"""
    exporter = StatusExporter(workspace_root=workspace_root)
    return exporter.export(filepath=filepath)
