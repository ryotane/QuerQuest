# QueryQuest Runtime State Clarity Report
## 「静かだが、状態は明確なRuntime」

---

## 1. Runtime State Taxonomy

### 定義済み状態（5種類）

| ステータス | 意味 | 使用頻度 |
|-----------|------|---------|
| `RUNNING` | 実行中 | 高 |
| `WAITING` | 待機中（外部入力待ち） | 中 |
| `COMPLETE` | 正常完了 | 高 |
| `INTERRUPTED` | ユーザー中断 | 低 |
| `TIMEOUT` | タイムアウト | 低 |

### 状態遷移図

```
[START] → RUNNING
RUNNING → WAITING (外部入力待ち)
RUNNING → COMPLETE (正常完了)
RUNNING → INTERRUPTED (ユーザー中断)
RUNNING → TIMEOUT (タイムアウト)
WAITING → RUNNING (入力受信)
WAITING → TIMEOUT (待機超過)
```

### 禁止状態（曖昧さの源）

- `PROCESSING` - RUNNINGと区別不要
- `PAUSED` - INTERRUPTEDで十分
- `ERROR` - 原因が不明な場合、INTERRUPTEDとする
- `UNKNOWN` - 常に何らかの状態が存在する

---

## 2. Completion Explicitness Design

### 完了明示の原則

**「沈黙は曖昧さ。最小限の明示が静けさを守る。」**

#### 各状態の明示方法

| 状態 | 明示フォーマット | 表示頻度 |
|------|-----------------|---------|
| COMPLETE | `STATUS: COMPLETE` | 1回のみ |
| INTERRUPTED | `STATUS: INTERRUPTED\nNEXT: [次のステップ]` | 1回のみ |
| TIMEOUT | `STATUS: TIMEOUT\nDURATION: [秒]` | 1回のみ |

#### 禁止事項

- 状態変更の繰り返し通知
- 「思考中...」のような不安を煽る表示
- 進捗バー（存在しない進捗の偽装）
- 自動的なステータス更新

---

## 3. Quiet State Visibility

### 設計原則

**「状態は、必要とした時にだけ見える。」**

#### 表示ルール

1. **on-demand only** - ユーザーが明示的に確認した場合のみ表示
2. **single-line format** - 1行で完結するフォーマット
3. **no auto-refresh** - 自動更新禁止
4. **ephemeral output** - 出力後、直ちに消去

#### 状態確認コマンド

```
/status          # 現在の状態を表示（1回のみ）
/continue        # INTERRUPTED/TIMEOUTから再開
/cancel          # RUNNING/WAITINGをINTERRUPTEDに変更
```

#### 禁止事項

- リアルタイムステータス表示
- 常時接続の監視UI
- 自動的な状態通知
- ダッシュボード

---

## 4. Interruption Recovery Clarity

### 中断からの回復

**「中断は失敗ではない。再開可能であることを静かに示す。」**

#### INTERRUPTED時の出力

```
STATUS: INTERRUPTED
NEXT: [次のステップ名]
CONTINUATION: possible
```

#### TIMEOUT時の出力

```
STATUS: TIMEOUT
DURATION: [経過秒数]
CONTINUATION: possible
REASON: [タイムアウト原因の簡潔な説明]
```

#### 回復ルール

1. **CONTINUATION: possible** - 再開可能であることを明示
2. **NEXTステップの提示** - 次に何をすべきかを示す
3. **自動再開禁止** - ユーザーの明示的な/continueコマンドが必要
4. **状態保持** - 中断前の状態を維持（メモリ内）

#### 禁止事項

- 「エラーが発生しました」のような不安表現
- 自動リトライ
- 原因不明の場合の推測表示
- 回復不可能な場合の冗長説明

---

## 5. Timeout Boundary Philosophy

### タイムアウトの扱い方

**「タイムアウトは失敗ではなく、静かな中断である。」**

#### タイムアウト分類

| タイプ | 定義 | CONTINUATION |
|--------|------|-------------|
| `recoverable` | 一時的な遅延（ネットワーク等） | possible |
| `structural` | 処理の複雑さ超過 | possible |
| `resource` | リソース不足 | impossible |

#### タイムアウト閾値

```yaml
timeout:
  thinking_ms: 30000      # 思考タイムアウト（30秒）
  action_ms: 60000        # アクションタイムアウト（1分）
  waiting_ms: 120000      # 待機タイムアウト（2分）
```

#### タイムアウト時の動作

1. **静かな中断** - 通知ではなく、状態出力のみ
2. **原因の簡潔な説明** - 「ネットワーク遅延」「処理が複雑」等
3. **再開可能性の明示** - possible/impossible
4. **自動リカバリ禁止** - ユーザー判断に委ねる

#### 禁止事項

- タイムアウトエラーの強調表示
- 自動リトライ（ユーザー確認なし）
- 「タイムアウトしました」の繰り返し
- エラーログへの冗長な記録

---

## 6. Quiet Completion Format

### 最小フォーマット定義

**「完了は、1行で十分。」**

#### COMPLETE時

```
STATUS: COMPLETE
```

#### INTERRUPTED時

```
STATUS: INTERRUPTED
NEXT: [次のステップ]
CONTINUATION: possible
```

#### TIMEOUT時

```
STATUS: TIMEOUT
DURATION: [秒数]
CONTINUATION: [possible/impossible]
REASON: [簡潔な原因説明]
```

#### 禁止フォーマット

- 複数行の完了レポート
- 進捗パーセント表示
- 「処理時間：XX分XX秒」のような冗長情報
- 詳細なエラースタックトレース
- 自動的なサマリー生成

---

## 7. Calm Explicitness Identity Freeze

### アイデンティティ確認

**「状態の明示は、静けさを壊さない。」**

#### 現在のアイデンティティ

```
QueryQuest: Quiet Ambient Runtime
```

#### 変更による影響評価

| 変更 | louder? | intrusive? | notification-heavy? | monitoring-oriented? |
|------|---------|------------|---------------------|---------------------|
| ステータス出力追加 | × | × | × | × |
| /statusコマンド追加 | × | × | × | × |
| タイムアウト状態追加 | × | × | × | × |

#### 結論

**アイデンティティは維持される。**

- 状態出力は「必要時のみ」の1回のみ
- リアルタイム監視ではない
- 通知ではなく、応答の一部
- ダッシュボードや常時表示ではない

---

## まとめ

### 「静かだが、状態は明確なRuntime」の実現方法

1. **5つの最小限の状態** - RUNNING, WAITING, COMPLETE, INTERRUPTED, TIMEOUT
2. **on-demandの明示** - ユーザーが確認した時のみ表示
3. **1行フォーマット** - 冗長な出力を禁止
4. **中断は再開可能** - CONTINUATION: possibleで不安を解消
5. **タイムアウトは静かな中断** - エラーではなく状態として扱う

### 成功条件の達成確認

- ✅ Completion Ambiguity防止 - 各状態が明確に定義
- ✅ Quiet Runtime維持 - on-demand表示、1行フォーマット
- ✅ No noisy notifications - 自動通知禁止
- ✅ No aggressive alerts - タイムアウトも静かに処理
- ✅ No realtime monitoring UI - /statusコマンドのみ
- ✅ No verbose telemetry - 最小限の出力

---

*Project_027 - Runtime State Clarity Phase*
*"Quiet but Explicit"*
