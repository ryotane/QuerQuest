# Observability Layer

AI Workspace の内部状態を可視化するモニタリングレイヤー。

## 目的

- Token/Context 成長の追跡と異常検出
- Recursive Loop 危険度のスコアリング
- Compression 効率のモニタリング
- Archive/Active Memory 比率の監視
- SwiftBar へのリアルタイムテレメトリ出力
- **低負荷なリアルタイム監視**

## 設計原則

- **low overhead**: 監視自体が負荷源にならない
- **non-intrusive**: 既存処理を妨害しない
- **live state cache**: キャッシュファースト
- **adaptive telemetry frequency**: 状態に応じた適応的頻度
- **event-driven priority**: イベント駆動型通知
- **cache-first access**: 不要な再計算を防止
- **lightweight metrics**: 軽量メトリクス優先
- **resource safety**: リソース安全最優先

## 構成

```
observability/
├── health_monitor.py           # 統合ヘルスモニタリングコア
├── token_growth_tracker.py     # Token 成長トラッカー
├── loop_risk_score.py          # Loop 危険度スコア計算器
├── compression_efficiency.py   # Compression 効率モニタ
├── archive_ratio.py            # Archive Ratio モニタ
├── status_export.py            # JSON エクスポート
├── swiftbar_telemetry.py       # SwiftBar テレメトリ
├── runtime_metrics_collector.py # 生メトリクスコレクタ
├── telemetry_scheduler.py      # 適応的テレメトリスケジューラ
├── live_health_stream.py       # イベント駆動型ヘルスストリーム
└── README.md
```

## アーキテクチャ

```
┌─────────────────────────────────────────────────┐
│              Observability Layer                 │
├─────────────────────────────────────────────────┤
│                                                  │
│  ┌──────────────┐    ┌──────────────────────┐   │
│  │ Runtime      │    │ Telemetry            │   │
│  │ Metrics      │───▶│ Scheduler            │   │
│  │ Collector    │    │ (adaptive freq)      │   │
│  └──────────────┘    └──────────┬───────────┘   │
│                                 │                │
│                    ┌────────────▼────────────┐   │
│                    │ Live Health Stream      │   │
│                    │ (event-driven)          │   │
│                    └────────────┬────────────┘   │
│                                 │                │
│                    ┌────────────▼────────────┐   │
│                    │ Health Monitor          │   │
│                    │ (unified status)        │   │
│                    └────────────┬────────────┘   │
│                                 │                │
│                    ┌────────────▼────────────┐   │
│                    │ Status Export           │   │
│                    │ (JSON / SwiftBar)       │   │
│                    └─────────────────────────┘   │
│                                                  │
└─────────────────────────────────────────────────┘
```

## 使用例

### 1. Health Monitor (統合)

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

### 2. Runtime Metrics Collector

```python
from ai_agent.observability import RuntimeMetricsCollector

collector = RuntimeMetricsCollector(
    workspace_path="/path/to/workspace",
    cache_ttl=10.0  # 10秒キャッシュ
)

metrics = collector.collect()
# {
#   "timestamp": ...,
#   "context_usage": 0.05,
#   "memory_pressure": 0.12,
#   "loop_risk": 0.0,
#   "token_growth": "stable",
#   "compression_efficiency": 0.5,
#   "process_info": {"pid": 1234, "rss_mb": 150.0}
# }
```

### 3. Telemetry Scheduler (適応的頻度)

```python
from ai_agent.observability import TelemetryScheduler, TelemetryState

scheduler = TelemetryScheduler()

# コールバック登録
def on_collect(metrics: dict):
    print(f"Collected: {metrics}")

scheduler.register_callback(on_collect)

# 状態更新 (外部メトリクスから)
scheduler.update_state(
    cpu_usage=15.0,
    loop_risk=0.3,
    memory_pressure=0.1
)

# 収集判定
if scheduler.should_collect():
    metrics = collector.collect()
    scheduler.record_collection(metrics)
```

**状態遷移:**

| 状態 | CPU 使用率 | Loop Risk | Interval |
|------|-----------|-----------|----------|
| IDLE | < 5% | < 0.5 | 60s |
| NORMAL | 5-20% | < 0.5 | 30s |
| ACTIVE | > 20% | < 0.5 | 10s |
| ALERT | - | > 0.5 | 5s |

### 4. Live Health Stream (イベント駆動)

```python
from ai_agent.observability import LiveHealthStream, HealthEventType

stream = LiveHealthStream()

# イベントハンドラ登録
@stream.on_event
def handle_event(event):
    if event.event_type == HealthEventType.ALERT:
        print(f"ALERT: {event.data}")
    elif event.event_type == HealthEventType.STATE_CHANGE:
        print(f"State: {event.data['from']} → {event.data['to']}")

# メトリクス更新 (有意な変化時のみイベント発生)
stream.update_metric("cpu_usage", 15.0)
stream.update_metric("loop_risk", 0.6)  # アラート発生

# イベント取得
events = stream.get_events()
summary = stream.get_summary()
```

### 5. 統合使用例

```python
from ai_agent.observability import (
    HealthMonitor,
    RuntimeMetricsCollector,
    TelemetryScheduler,
    LiveHealthStream,
    TelemetryState,
)

# 初期化
collector = RuntimeMetricsCollector(workspace_path="/path/to/workspace")
scheduler = TelemetryScheduler()
stream = LiveHealthStream(scheduler=scheduler)
monitor = HealthMonitor()

# イベントハンドラ
@stream.on_event
def on_health_event(event):
    if event.severity == "critical":
        # アラート処理
        pass

# メインループ
while True:
    # 収集判定
    if scheduler.should_collect():
        # メトリクス収集
        metrics = collector.collect()
        
        # スケジューラ更新
        scheduler.update_state(
            cpu_usage=metrics.get("cpu_usage", 0),
            loop_risk=metrics.get("loop_risk", 0),
            memory_pressure=metrics.get("memory_pressure", 0),
        )
        
        # ストリーム更新
        stream.update_metric("context_usage", metrics.get("context_usage", 0))
        stream.update_metric("memory_pressure", metrics.get("memory_pressure", 0))
        
        # スナップショット記録
        scheduler.record_collection(metrics)
        
        # Health Monitor 更新
        monitor.update_token_growth(
            current_tokens=metrics.get("token_count", 0),
            previous_tokens=metrics.get("prev_token_count", 0),
        )
    
    import time
    time.sleep(1)  # メインループ間隔
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
- `project_master.json` へのヘルス状態連携

## Performance Budget

| コンポーネント | 最大 CPU | 最大メモリ | 収集頻度 |
|---------------|---------|-----------|---------|
| RuntimeMetricsCollector | < 1% | < 5MB | 適応的 |
| TelemetryScheduler | < 0.1% | < 1MB | イベント駆動 |
| LiveHealthStream | < 0.1% | < 1MB | イベント駆動 |
| HealthMonitor | < 0.5% | < 2MB | 必要時 |
| **合計** | **< 2%** | **< 10MB** | **適応的** |
