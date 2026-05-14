"""
SwiftBar Telemetry Integration

SwiftBar (macOS menubar app) 用のテレメトリデータを出力する。

使用例:
    # SwiftBar プラグインから呼び出す
    python -m ai_agent.observability.swiftbar_telemetry

出力形式:
    ✅ QueryQuest Health
    ---
    Tokens: 10,000 (+5.2%)
    Loop Risk: 🟢 0.15
    Compression: good (45.3%)
    Archive: 65.2% (balanced)
"""

import os
import sys
import json
from pathlib import Path

# プロジェクトルートにパスを追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from .health_monitor import HealthMonitor, quick_health_check


def get_workspace_root() -> str:
    """Workspace ルートを取得"""
    # 環境変数で指定されている場合
    workspace = os.environ.get("QUERYQUEST_WORKSPACE")
    if workspace and os.path.isdir(workspace):
        return workspace

    # デフォルトパス
    default = os.path.join(os.path.expanduser("~"), "local_ai_project", "QueryQuest")
    if os.path.isdir(default):
        return default

    # カレントディレクトリ
    return os.getcwd()


def generate_swiftbar_output() -> str:
    """SwiftBar 用出力を生成"""
    workspace_root = get_workspace_root()
    monitor = HealthMonitor(workspace_root=workspace_root)

    # メトリクス更新 (実際の値を取得)
    # TODO: 実際の memory サイズを取得するロジックに接続
    # 現在はダミー値

    return monitor.export_swiftbar()


def generate_swiftbar_menu() -> str:
    """SwiftBar メニュー項目を生成"""
    workspace_root = get_workspace_root()
    monitor = HealthMonitor(workspace_root=workspace_root)
    status = monitor.get_status()

    lines = []
    lines.append("---")

    # Token 詳細
    tg = status.token_growth
    lines.append(f"Tokens: {tg.current_tokens:,} | growth: {tg.growth_rate:+.1f}%")

    # Loop Risk 詳細
    lr = status.loop_risk
    lines.append(f"Loop Risk: {lr.risk_score:.2f} | depth: {lr.recursion_depth}")

    # Compression 詳細
    ce = status.compression
    lines.append(f"Compression: {ce.efficiency} | ratio: {ce.compression_ratio:.1f}%")

    # Archive 詳細
    ar = status.archive_ratio
    lines.append(f"Archive: {ar.archive_ratio:.1f}% | {ar.ratio_status}")

    # 全体ステータス
    lines.append(f"Status: {status.status}")

    # Action items
    lines.append("---")
    lines.append("Export JSON | shell: python -c 'from ai_agent.observability import export_health_status; export_health_status()'")
    lines.append("Open Logs | shell: open logs/")

    return "\n".join(lines)


def main():
    """SwiftBar 用メインエントリポイント"""
    # モード判定
    if "--menu" in sys.argv:
        output = generate_swiftbar_menu()
    else:
        output = generate_swiftbar_output()

    print(output)


if __name__ == "__main__":
    main()
