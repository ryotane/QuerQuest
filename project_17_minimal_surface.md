# QueryQuest Project_17 - Minimal Runtime Surface

## 基本方針
- 人間が普段見るもの
- 普段見せないもの
- hidden infrastructure
- visible reassurance layer

---

## Visible Reassurance Layer（普段見えるもの）

### iPhone Companion で表示する情報

| 項目 | 内容 | 条件 |
|------|------|------|
| 状態アイコン | 稼働中 / 停止 | 常時 |
| 簡易ステータス | "稼働中" / "停止中" | 常時 |
| メモリ使用率 | %表示 | オプション（押さない限り見えない） |

### Open WebUI で表示する情報

| 項目 | 内容 | 条件 |
|------|------|------|
| チャット画面 | 対話のみ | 常時 |
| セッション情報 | 最小限 | オプション |
| メトリクス | 最大3つまで | オプション |

---

## Hidden Infrastructure（普段見せないもの）

### バックグラウンドインフラ

| コンポーネント | 状態 | 理由 |
|----------------|------|------|
| Memory OS | hidden | 必要時のみ表示 |
| Vector Search | disabled (lightweight) | リソース節約 |
| Telemetry | disabled | privacy 保護 |
| Background Tasks | disabled | idle calmness |

### 非表示の機能

- メモリの詳細統計
- セッション履歴の詳細
- システムメトリクスの詳細
- エラーログ（critical のみ）
- トークン使用量の詳細

---

## Surface Design Principles

### 1. 最小限の情報
- 常時表示は状態アイコンのみ
- 詳細情報は押さない限り見えない

### 2. 静かな存在
- 通知はバッチ配信（1日5回上限）
- リアルタイム同期禁止

### 3. 必要時のみ
- detail_access_on_demand: true
- surfaced_only_when_needed: true

---

## Summary: Minimal Runtime Surface の原則

1. **普段見えるもの**: 状態アイコン、簡易ステータス
2. **普段見せないもの**: バックグラウンドインフラの詳細
3. **hidden infrastructure**: Memory OS, Vector Search, Telemetry
4. **visible reassurance layer**: 最小限の安心感を提供する情報
