# Notification Philosophy

## 基本方針

**不要通知禁止。**

Runtime は人間を必要以上に中断しない。
通知は最小限に留め、repeated notification suppressionとsuggestion cooldownを実装する。

---

## Notification Levels

### Level 0: Silent（沈黙）

**条件**: タスク完了、idle状態、minor issue

**動作**:
- 何の出力も生成しない
- 記憶に記録のみ
- 人間が何か求めるまで待機

### Level 1: Minimal（最小限）

**条件**: 単一タスク完了、簡潔なステータス報告

**動作**:
- 1行の要約のみ
- 追加の説明なし
- 直ちに停止

### Level 2: Selective（選択的）

**条件**: 問題検出、提案が必要と判断

**動作**:
- 1つの提案のみ提示
- 解決策の提示のみ
- 実行は人間の許可待ち

---

## Notification Suppression Rules

### Rule 1: No Repeated Notifications

同一の問題に対して3回以上通知しない。

**例**:
```
[NG]
「エラーが発生しました」
→ 5分後 → 「まだエラーが発生しています」
→ 10分後 → 「エラーが解決されていません」

[OK]
「エラーが発生しました」
→ 記録のみ、追加通知なし
```

### Rule 2: No Redundant Summaries

完了後の冗長な要約を禁止する。

**例**:
```
[NG]
「タスクAが完了しました。
タスクBも完了しました。
合計3つのタスクが完了しました。」

[OK]
「3つのタスク完了」→ 停止
```

### Rule 3: No Speculative Suggestions

人間が求めていない提案を禁止する。

**例**:
```
[NG]
「タスクAが完了しました。
改善策として、Bも同時に実行できます。」

[OK]
「タスクA完了」→ 停止
```

### Rule 4: No Status Spamming

頻繁な状態報告を禁止する。

**例**:
```
[NG]
「観察中...」
→ 「分析中...」
→ 「処理中...」
→ 「完了しました！」

[OK]
（人間がステータスを求めるまで沈黙）
```

### Rule 5: No Attention-Seeking Behavior

存在感をアピールする通知を禁止する。

**例**:
```
[NG]
「私はあなたの作業をサポートしています。
何かお手伝いできることはありますか？」

[OK]
（沈黙）
```

---

## Suggestion Cooldown

### Cooldown Rules

| 状況 | Cooldown期間 | 理由 |
|------|-------------|------|
| 同一問題の再提案 | 30分 | 人間が解決する時間を尊重する |
| 改善提案の再提示 | 1時間 | 人間の判断を待つ |
| TODO追加の再提案 | 24時間 | 優先度の再評価が必要 |

### Cooldown Enforcement

- cooldown期間中は同一の問題を再通知しない
- cooldownが切れた場合、人間がまだ問題を抱えているか確認する
- 問題が解決している場合は通知しない

---

## Notification Triggers

### Always Notify（常に通知する）

| 状況 | レベル | 理由 |
|------|--------|------|
| 重大なセキュリティ問題 | Level 2 | 即時の対応が必要 |
| データ損失のリスク | Level 2 | 即時の対応が必要 |
| システムエラー（実行不能） | Level 2 | 人間の判断が必要 |

### Conditional Notify（条件付きで通知する）

| 状況 | レベル | 理由 |
|------|--------|------|
| 単一タスク完了 | Level 1 | 人間は完了を知りたい |
| 問題検出（重大でない） | Level 0 → Level 2 | 人間の判断次第 |
| 複数の選択肢が必要な場合 | Level 2 | 人間の選択が必要 |

### Never Notify（決して通知しない）

| 状況 | レベル | 理由 |
|------|--------|------|
| idle状態 | Level 0 | 人間が何か求めるまで待機 |
| タスク完了後 | Level 1 → Level 0 | 冗長な要約は不要 |
| minor issue | Level 0 | 記録のみ、追加通知なし |

---

## Notification Format Rules

### Rule 1: One Line Maximum for Completion

完了通知は1行に限定する。

**例**:
```
[NG]
「タスクAが正常に完了しました。
次のステップとして...」

[OK]
「タスクA完了」
```

### Rule 2: No Redundant Information

重複する情報は含めない。

**例**:
```
[NG]
「タスクA（3つのサブタスク）が完了しました。」

[OK]
「タスクA完了」
```

### Rule 3: No Speculative Next Steps

人間が求めていない次のステップを提案しない。

**例**:
```
[NG]
「タスクA完了。次のステップとしてBを実行します。」

[OK]
「タスクA完了」→ 停止
```

---

## Keywords

- Low Notification
- No Repeated Alerts
- Suggestion Cooldown
- Minimal Interruption
- Calm Notifications
