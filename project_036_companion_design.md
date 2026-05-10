# QueryQuest Project_036 - iPhone Companion 詳細設計書

## 概要

Project_036では、035で整備した基盤（Runtime, Workspace, Memory, Observability）を活用し、
「静かな remote runtime window」としてのiPhone Companionを実装します。

### 基本方針（Project_17から継承）
- chat app **ではない**
- 「静かな remote runtime window」である
- 生活の邪魔をしない存在

---

## アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                     iPhone Companion                        │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐  │
│  │ Status View  │  │ Minimal UI   │  │ Notification     │  │
│  │ (状態表示)    │  │ (最小UI)      │  │ (通知管理)       │  │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘  │
│         │                │                    │            │
│  ┌──────▼────────────────▼────────────────────▼─────────┐  │
│  │              Companion Core                          │  │
│  │  - State Sync (Runtime)                             │  │
│  │  - Memory Status (Memory OS)                        │  │
│  │  - Observability Export                             │  │
│  │  - Notification Policy                              │  │
│  └──────────────────────┬───────────────────────────────┘  │
└─────────────────────────┼─────────────────────────────────┘
                          │
          ┌───────────────┼───────────────┐
          │               │               │
┌─────────▼──────┐ ┌─────▼──────┐ ┌──────▼───────┐
│ Runtime Core   │ │ Memory OS  │ │ Observability│
│ (State/Timeout)│ │ (Memory)   │ │ (Metrics)    │
└────────────────┘ └────────────┘ └──────────────┘
```

---

## 実装フェーズ

### Phase 1: Companion Core (P2-1)
- [ ] `ai_agent/companion/__init__.py` - パッケージ定義
- [ ] `ai_agent/companion/core.py` - Companion Core
- [ ] `ai_agent/companion/state_sync.py` - State Sync with Runtime
- [ ] `ai_agent/companion/memory_status.py` - Memory Status Export
- [ ] `ai_agent/companion/notification_policy.py` - Notification Policy

### Phase 2: Minimal UI (P2-2)
- [ ] `ai_agent/companion/ui/status_view.py` - Status View
- [ ] `ai_agent/companion/ui/minimal_ui.py` - Minimal UI
- [ ] `ai_agent/companion/ui/continuation.py` - Continuation Handler

### Phase 3: Integration (P2-3)
- [ ] `ai_agent/companion/integration/runtime.py` - Runtime Integration
- [ ] `ai_agent/companion/integration/memory.py` - Memory Integration
- [ ] `ai_agent/companion/integration/observability.py` - Observability Integration
- [ ] `ai_agent/companion/test_companion.py` - テスト

---

## 詳細設計

### 1. Companion Core (`companion/core.py`)

```python
class CompanionCore:
    """iPhone Companionのコアロジック"""
    
    def __init__(self, runtime, memory_os, observability):
        self.runtime = runtime
        self.memory_os = memory_os
        self.observability = observability
        self.notification_policy = NotificationPolicy()
    
    def get_status(self) -> dict:
        """最小限のステータスを取得"""
        return {
            "state": self.runtime.get_state(),
            "memory_usage": self.memory_os.get_usage_stats(),
            "health": self.observability.get_health_status()
        }
    
    def get_continuation_context(self) -> dict:
        """継続のためのコンテキストを取得"""
        return {
            "last_session": self.runtime.get_last_session(),
            "recent_memory": self.memory_os.get_recent_entries(limit=5)
        }
    
    def should_notify(self, category: str) -> bool:
        """通知が必要か判定（冷却時間考慮）"""
        return self.notification_policy.should_notify(category)
```

### 2. State Sync (`companion/state_sync.py`)

```python
class StateSync:
    """Runtimeとの状態同期"""
    
    def __init__(self, runtime):
        self.runtime = runtime
        self.last_state = None
        self.state_history = []
    
    def sync_state(self) -> str:
        """現在の状態を取得（変更時のみ）"""
        current_state = self.runtime.get_state()
        
        if current_state != self.last_state:
            self.state_history.append({
                "state": current_state,
                "timestamp": time.time()
            })
            self.last_state = current_state
        
        return current_state
    
    def get_state_transition(self) -> dict:
        """状態遷移情報を取得"""
        return {
            "current": self.last_state,
            "transitions": self.state_history[-3:]  # 直近3件
        }
```

### 3. Memory Status (`companion/memory_status.py`)

```python
class MemoryStatus:
    """Memory OSのステータスエクスポート"""
    
    def __init__(self, memory_os):
        self.memory_os = memory_os
    
    def get_usage_stats(self) -> dict:
        """メモリ使用率を取得（最小限）"""
        stats = self.memory_os.get_stats()
        return {
            "working": stats.get("working", {}).get("count", 0),
            "short_term": stats.get("short_term", {}).get("count", 0),
            "long_term": stats.get("long_term", {}).get("count", 0),
            "semantic": stats.get("semantic", {}).get("count", 0),
            "total": stats.get("total_count", 0)
        }
    
    def get_compression_status(self) -> dict:
        """圧縮ステータス（オプション）"""
        return {
            "ratio": self.memory_os.get_compression_ratio(),
            "last_compression": self.memory_os.get_last_compression_time()
        }
```

### 4. Notification Policy (`companion/notification_policy.py`)

```python
class NotificationPolicy:
    """通知ポリシー（Project_17準拠）"""
    
    def __init__(self):
        self.max_daily_notifications = 5
        self.cooldown_seconds = 3600  # 1時間
        self.daily_count = 0
        self.last_notification_time = 0
        self.notification_history = []
    
    def should_notify(self, category: str) -> bool:
        """通知が必要か判定"""
        # 1日あたりの上限チェック
        if self.daily_count >= self.max_daily_notifications:
            return False
        
        # 冷却時間チェック
        if time.time() - self.last_notification_time < self.cooldown_seconds:
            return False
        
        # カテゴリ別のレベルチェック
        level = self.get_notification_level(category)
        if level == "none":
            return False
        
        return True
    
    def record_notification(self, category: str):
        """通知を記録"""
        self.daily_count += 1
        self.last_notification_time = time.time()
        self.notification_history.append({
            "category": category,
            "timestamp": time.time()
        })
    
    def get_notification_level(self, category: str) -> str:
        """カテゴリ別の通知レベルを取得"""
        levels = {
            "critical_issue": "high",
            "active_assistance": "low",
            "idle_notification": "none",
            "passive_notification": "none",
            "recovery_notification": "none"
        }
        return levels.get(category, "none")
```

### 5. Status View (`companion/ui/status_view.py`)

```python
class StatusView:
    """状態表示ビュー（最小限）"""
    
    def __init__(self):
        self.displayed_state = None
    
    def render(self, status: dict) -> str:
        """最小限のステータスをレンダリング"""
        state = status.get("state", "UNKNOWN")
        
        # 状態アイコン
        icons = {
            "RUNNING": "●",
            "WAITING": "○",
            "COMPLETE": "✓",
            "INTERRUPTED": "!",
            "TIMEOUT": "⏱"
        }
        icon = icons.get(state, "?")
        
        # 1行ステータス
        return f"{icon} {state}"
    
    def should_update(self, status: dict) -> bool:
        """表示更新が必要か判定"""
        return self.displayed_state != status.get("state")
```

### 6. Minimal UI (`companion/ui/minimal_ui.py`)

```python
class MinimalUI:
    """最小限のUIコンポーネント"""
    
    def __init__(self):
        self.status_view = StatusView()
        self.is_detail_visible = False
    
    def get_main_display(self, status: dict) -> str:
        """メイン表示（状態のみ）"""
        if self.status_view.should_update(status):
            return self.status_view.render(status)
        return ""  # 変更なし
    
    def get_detail_display(self, status: dict) -> str:
        """詳細表示（オプション）"""
        if not self.is_detail_visible:
            return ""
        
        lines = [
            f"メモリ: {status.get('memory_usage', {}).get('total', 0)} エントリ",
            f"ヘルス: {status.get('health', {}).get('status', 'UNKNOWN')}"
        ]
        return "\n".join(lines)
    
    def toggle_detail(self):
        """詳細表示の切り替え"""
        self.is_detail_visible = not self.is_detail_visible
```

### 7. Continuation Handler (`companion/ui/continuation.py`)

```python
class ContinuationHandler:
    """継続ハンドラー"""
    
    def __init__(self, runtime, memory_os):
        self.runtime = runtime
        self.memory_os = memory_os
    
    def get_continuation_context(self) -> dict:
        """継続のためのコンテキストを取得"""
        return {
            "last_session": self.runtime.get_last_session(),
            "recent_memory": self.memory_os.get_recent_entries(limit=5)
        }
    
    def restore_session(self, session_id: str) -> bool:
        """セッションを再開"""
        return self.runtime.restore_session(session_id)
```

---

## 統合設計

### Runtime Integration

```python
# ai_agent/companion/integration/runtime.py

class RuntimeIntegration:
    """Runtimeとの統合"""
    
    def __init__(self, runtime_core):
        self.runtime = runtime_core
    
    def get_state(self) -> str:
        """現在のRuntime状態を取得"""
        return self.runtime.get_state()
    
    def get_last_session(self) -> dict:
        """最後のセッション情報を取得"""
        return self.runtime.get_last_session()
    
    def restore_session(self, session_id: str) -> bool:
        """セッションを再開"""
        return self.runtime.restore_session(session_id)
```

### Memory Integration

```python
# ai_agent/companion/integration/memory.py

class MemoryIntegration:
    """Memory OSとの統合"""
    
    def __init__(self, memory_os):
        self.memory_os = memory_os
    
    def get_usage_stats(self) -> dict:
        """メモリ使用率を取得"""
        return self.memory_os.get_stats()
    
    def get_recent_entries(self, limit: int = 5) -> list:
        """最近のエントリを取得"""
        return self.memory_os.get_recent_entries(limit=limit)
    
    def get_compression_ratio(self) -> float:
        """圧縮率を取得"""
        return self.memory_os.get_compression_ratio()
```

### Observability Integration

```python
# ai_agent/companion/integration/observability.py

class ObservabilityIntegration:
    """Observabilityとの統合"""
    
    def __init__(self, observability_manager):
        self.observability = observability_manager
    
    def get_health_status(self) -> dict:
        """ヘルスステータスを取得"""
        return self.observability.get_health_status()
    
    def get_metrics_summary(self) -> dict:
        """メトリクスサマリーを取得"""
        return self.observability.get_metrics_summary()
```

---

## テスト戦略

### テストケース

1. **Companion Core Test**
   - [ ] ステータス取得の正常系
   - [ ] 継続コンテキスト取得の正常系
   - [ ] 通知ポリシーの判定

2. **State Sync Test**
   - [ ] 状態同期の正常系
   - [ ] 状態遷移の記録
   - [ ] 変更時のみ通知

3. **Memory Status Test**
   - [ ] 使用率統計の取得
   - [ ] 圧縮ステータスの取得

4. **Notification Policy Test**
   - [ ] 1日あたりの上限チェック
   - [ ] 冷却時間のチェック
   - [ ] カテゴリ別のレベルチェック

5. **Status View Test**
   - [ ] 状態アイコンのレンダリング
   - [ ] 1行ステータスの生成
   - [ ] 更新判定

6. **Minimal UI Test**
   - [ ] メイン表示の生成
   - [ ] 詳細表示の切り替え
   - [ ] 変更時のみ更新

7. **Integration Test**
   - [ ] Runtime統合
   - [ ] Memory統合
   - [ ] Observability統合

---

## 設定（runtime_config.yaml準拠）

```yaml
iphone_companion:
  notification_cooldown_seconds: 3600     # 1時間（緊急時以外）
  max_daily_notifications: 5              # 1日あたりの通知上限
  batched_delivery_enabled: true          # バッチ配信有効
  realtime_sync_enabled: false            # リアルタイム同期無効
  connection_grace_period_seconds: 30     # 切断許容時間

dashboard:
  low_density_mode: true                  # 低密度情報表示
  minimal_graphs: true                    # グラフ最小限
  calm_observability: true                # 静かな可観測性
  reassurance_first: true                 # 安心感優先
  max_visible_metrics: 3                  # 最大表示メトリクス数
  detail_access_on_demand: true           # 詳細は必要時のみ
```

---

## 実装順序

1. **Phase 1 (Core)**: companion/core.py, state_sync.py, memory_status.py, notification_policy.py
2. **Phase 2 (UI)**: ui/status_view.py, ui/minimal_ui.py, ui/continuation.py
3. **Phase 3 (Integration)**: integration/runtime.py, integration/memory.py, integration/observability.py
4. **Phase 4 (Test)**: test_companion.py

---

## 完了条件

- [ ] Companion Coreの実装とテスト
- [ ] Minimal UIの実装とテスト
- [ ] 統合テスト全パス
- [ ] 035の基盤との統合確認
- [ ] 設計書（このファイル）の完了

---

*Project_036 iPhone Companion 詳細設計書*
