# Observability Layer

AI Workspace の内部状態を可視化するモニタリングレイヤー。

## 目的

- Token/Context 成長の追跡と異常検出
- Recursive Loop 危険度のスコアリング
- Compression 効率のモニタリング
- Archive/Active Memory 比率の監視
- SwiftBar へのリアルタイムテレメトリ出力

## 構成

```
observability/
├── health_monitor.py       # 統合ヘルスモニタリングコア
├── token_growth_tracker.py # Token 成長トラッカー
├── loop_risk_score.py      # Loop 危険度スコア計算器
├── compression_efficiency.py # Compression 効率モニタ
├── archive_ratio.py        # Archive Ratio モニタ
├── status_export.py        # JSON エクスポート
├── swiftbar_telemetry.py   # SwiftBar テレメトリ
└── README.md
```

## 使用例

### Health Monitor (統合)

```python
from ai_agent.observability import HealthMonitor

monitor = HealthMonitor()

# メトリクス更新
monitor.update_token_growth(current_tokens=10000, previous_tokens=9500)
monitor.update_loop_risk(injection_count=3, recursion_depth=2)
monitor.update_compression_efficiency(original_size=10000, compressed_size=3000)
monitor.update_archive_ratio(active_size=5000, archive_size=15000)

# ステータス取得
status = monitor.get_status()
print(status.to_json())
```

### Token Growth Tracker

```python
from ai_agent.observability import TokenGrowthTracker

tracker = TokenGrowthTracker()
tracker.record("active_memory", 10000)
tracker.record("active_memory", 15000)  # +50%

alerts = tracker.get_alerts()
```

### Loop Risk Calculator

```python
from ai_agent.observability import LoopRiskCalculator

calculator = LoopRiskCalculator()
score = calculator.calculate(
    injection_count=5,
    recursion_depth=3,
    context_amplification_count=2,
)

if score.is_critical:
    # 対策実行
    pass
```

### Status Export

```python
from ai_agent.observability import StatusExporter

exporter = StatusExporter()
exporter.export()  # logs/health_status_YYYYMMDD_HHMMSS.json
```

### SwiftBar Telemetry

```bash
# SwiftBar プラグインから呼び出す
python -m ai_agent.observability.swiftbar_telemetry

# メニュー付き
python -m ai_agent.observability.swiftbar_telemetry --menu
```

## スコアリング基準

### Loop Risk Score (0.0 - 1.0)

| レベル | スコア範囲 | 意味 |
|--------|-----------|------|
| low | 0.0 - 0.19 | 正常 |
| medium | 0.2 - 0.49 | 注意 |
| high | 0.5 - 0.79 | 危険 |
| critical | 0.8 - 1.0 | 致命 |

### Compression Efficiency

| 効率 | 圧縮率 | 意味 |
|------|--------|------|
| excellent | < 30% | 優秀 |
| good | 30-50% | 良好 |
| normal | 50-80% | 普通 |
| poor | > 80% | 問題 |

### Archive Ratio

| ステータス | 比率 | 意味 |
|-----------|------|------|
| balanced | 30-70% | 正常 |
| archive_heavy | > 70% | archive 過多 |
| active_heavy | < 30% | active 過多 |

## Integration Points

- `memory_stabilization_report.txt` とのデータ連携
- `workspace_registry.json` からのサイズ取得
- SwiftBar へのリアルタイム出力
