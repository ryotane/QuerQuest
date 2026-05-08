# QueryQuest Project_17 - Open WebUI Integration Review

## 基本方針
- 「思想追加」ではなく「最小実運用」の観点で評価する
- calm UX を壊していないか確認する
- 情報密度が高すぎないか確認する

---

## 現状設定との整合性チェック

### runtime_config.yaml の ambient_runtime セクション

```yaml
ambient_runtime:
  dashboard:
    low_density_mode: true          # ✓ calm UX に適合
    minimal_graphs: true            # ✓ 情報密度抑制
    calm_observability: true        # ✓ 静かな可観測性
    reassurance_first: true         # ✓ 安心感優先
    max_visible_metrics: 3          # ✓ 最小限の表示
    detail_access_on_demand: true   # ✓ 必要時のみ詳細

  attention_protection:
    focus_mode_detection: true      # ✓ 集中状態検出
    repeated_interruption_suppression: true  # ✓ 繰り返し中断抑制
    passive_waiting_behavior: true  # ✓ 受動的待機動作
    notification_cooldown_seconds: 1800  # ✓ 30分冷却
```

### iPhone Companion Settings

```yaml
iphone_companion:
  notification_cooldown_seconds: 3600     # ✓ 1時間（緊急時以外）
  max_daily_notifications: 5              # ✓ 1日5回上限
  batched_delivery_enabled: true          # ✓ バッチ配信有効
  realtime_sync_enabled: false            # ✓ リアルタイム同期無効
```

---

## カラムチェックリスト

### 1. calm UX を壊していないか
- [x] low_density_mode: true → 低密度情報表示
- [x] minimal_graphs: true → グラフ最小限
- [x] calm_observability: true → 静かな可観測性
- **判定: OK** - 設定は calm UX に適合

### 2. 情報密度が高すぎないか
- [x] max_visible_metrics: 3 → 最大表示メトリクス数制限
- [x] detail_access_on_demand: true → 詳細は必要時のみ
- **判定: OK** - 設定は情報密度抑制に適合

### 3. continuation が強制的でないか
- [x] no_forced_continuation: true → 強制継続禁止
- [x] natural_resume_enabled: true → 自然な再開有効
- **判定: OK** - 設定は強制継続を禁止

### 4. notification 的挙動がないか
- [x] idle_notification_level: none → アイドル通知なし
- [x] passive_notification_level: none → パッシブ通知なし
- [x] max_daily_notifications: 5 → 1日5回上限
- **判定: OK** - 設定は通知的挙動を抑制

### 5. memory visibility が過剰でないか
- [x] surfaced_only_when_needed: true → 必要時のみ表示
- [x] quiet_archive: true → 静かなアーカイブ
- [x] no_forced_recall: true → 強制想起禁止
- **判定: OK** - 設定はメモリ可視性を抑制

---

## Open WebUI 固有の懸念点

### 潜在的な問題
1. **デフォルトの UI が情報過多**: Open WebUI の標準 UI はチャット中心で、情報密度が高い可能性がある
2. **通知システム**: Open WebUI の通知が runtime_config.yaml のポリシーと矛盾する可能性
3. **セッション管理**: Open WebUI のセッション表示が強制的な continuation を誘発する可能性

### 推奨アクション
1. Open WebUI の UI カスタマイズ（低密度モード）
2. notification_policy の明示的設定
3. セッション表示の最小化

---

## 結論

**現状の設定は calm UX に適合している。**

ただし、Open WebUI の標準 UI が情報過多である可能性があり、実際の動作確認が必要。

ブラウザ環境が整っていないため、実際の Open WebUI 画面での確認は後日実施する。
