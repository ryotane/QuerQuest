# QueryQuest Project_18 - Runtime Maintenance Boundaries

## テーマ: 「どこまで maintenance するか」

---

## 1. Maintenance Philosophy

**基本原則:**
- 最小限の maintenance で最大限の calmness を維持する
- 放置できる範囲を最大化する
- observer を増やさない
- cleanup は最後に行う

## 2. Where to Maintain

### 2.1 Memory Cleanup（月次）
- memory.db が baseline の3倍以上になった場合のみ
- session_registry.json にテストセッションが50個以上追加された場合のみ
- log.jsonl が500行を超えた場合のみ

**方法:**
- archive の圧縮
- テストセッションの削除
- 古いログのアーカイブ

### 2.2 Runtime Config Validation（四半期）
- runtime_config.yaml の安全デフォルトが維持されているか確認
- safety_guard, collapse_prevention, loop_risk の値が変更されていないか確認

**方法:**
- 設定ファイルの確認のみ
- 変更は最小限

### 2.3 Health Check（四半期）
- observability セクションの設定が有効か確認
- export_json が機能しているか確認

**方法:**
- logs/health_status.json の存在確認
- 内容の確認のみ

## 3. Where NOT to Maintain

### 3.1 No New Observers
- observer expansion は禁止
- 新しい観察項目の追加は禁止
- telemetry の追加は禁止

### 3.2 No Recursive Optimization
- recursive optimization は禁止
- self-improvement 機構は禁止
- 計画の無限拡張は禁止

### 3.3 No Aggressive Cleanup
- aggressive cleanup は禁止
- rapid unload は禁止
- repeated compression は禁止
- panic cleanup は禁止

### 3.4 No Runtime Redesign
- runtime redesign は禁止
- new layer の追加は禁止
- manifesto の更新は禁止（哲学の維持確認のみ）

## 4. Where to Let Go

### 4.1 Test Sessions
- テストセッションは放置する
- session_registry.json にテストセッションが大量に追加されても、直ちに削除しない
- 月次の memory cleanup で初めて考慮

### 4.2 Minor Drifts
- minor drift（10%以内）は観察のみ
- 修正は行わない
- 記録のみ行う

### 4.3 Non-Critical Warnings
- loop_risk の warning は放置する
- token_budget の warning は放置する
- memory pressure の warning は放置する

## 5. Maintenance Schedule

| Frequency | Action |
|-----------|--------|
| Daily | Runtime Feeling Log（感覚ベース） |
| Weekly | Drift Detection（数値ベースのチェック） |
| Monthly | Memory Cleanup（必要時のみ） |
| Quarterly | Config Validation, Health Check |

## 6. Maintenance Decision Tree

```
[問題発生]
    ↓
[Drift Level を判断]
    ↓
├── Minor (10%以内) → 観察のみ、記録
├── Moderate (50%以内) → 観察のみ、記録
└── Major (50%超) → 観察のみ、記録、人間に報告

[Memory Growth]
    ↓
├── baseline の3倍以内 → 放置
└── baseline の3倍以上 → 月次 cleanup で対応

[Proposal Proliferation]
    ↓
├── TODO ≤5個 → 放置
└── TODO >5個 → 人間に報告、統合検討
```

---

*Project_18 - Runtime Maintenance Boundaries*
*"最小限の maintenance で最大限の calmness"*
