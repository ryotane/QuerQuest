# QueryQuest Project_18 - Calm Failure Handling

## テーマ: 「panic runtime へ戻さない」

---

## 1. Failure Philosophy

**基本原則:**
- 失敗は自然な現象として受容する
- panic runtime へ戻さない
- 静かな回復処理を優先する
- 人間の不安を増幅しない

## 2. Timeout Handling

### 2.1 LLM Timeout
- 応答がタイムアウトした場合、慌てず待機
- retry は最大3回まで（冷却時間5秒）
- 3回失敗したら静かに報告

**Report Format:**
```
[Timeout] モデルの応答にタイムアウトしました。
- 試行回数: [X]/3
- 待機時間: [X]秒
- 次のアクション: 再試行または人間の判断待ち
```

### 2.2 Network Timeout
- ネットワーク接続がタイムアウトした場合、静かに再接続を試みる
- retry は最大5回まで（冷却時間10秒）
- 5回失敗したら静かに報告

**Report Format:**
```
[Network] ネットワーク接続にタイムアウトしました。
- 試行回数: [X]/5
- 待機時間: [X]秒
- 次のアクション: 再試行または人間の判断待ち
```

## 3. Restart Handling

### 3.1 Graceful Restart
- restart は静かに、焦らず行う
- invisible_hydration を有効にする
- forced_continuation を禁止する

**Restart Flow:**
```
[restart開始]
→ 現在の状態を保存（最小限）
→ モデルのシャットダウン
→ モデルのロード
→ 状態の復元（目に見えない）
→ 通常状態への復帰
```

### 3.2 Cold Start
- コールドスタート時は、最小限の状態から開始
- 強制再開は行わない
- user が再開を希望する場合のみ継続

**Cold Start Flow:**
```
[cold start]
→ モデルのロード（静かに）
→ 最小限の状態復元
→ 通常状態への復帰
→ user の判断待ち
```

## 4. Continuation Failure Handling

### 4.1 Continuation Failure
- continuation が失敗した場合、慌てず待機
- retry は最大3回まで（冷却時間5秒）
- 3回失敗したら静かに報告

**Report Format:**
```
[Continuation] 継続処理に失敗しました。
- 試行回数: [X]/3
- 待機時間: [X]秒
- 次のアクション: 再試行または人間の判断待ち
```

### 4.2 State Loss
- 状態消失が発生した場合、静かに報告
- forced restoration を禁止する
- user の判断を待つ

**Report Format:**
```
[State Loss] 状態の復元に失敗しました。
- 損失した状態: [説明]
- 次のアクション: 再開または人間の判断待ち
```

## 5. Browser Automation Failure Handling

### 5.1 Browser Timeout
- browser automation がタイムアウトした場合、慌てず待機
- retry は最大3回まで（冷却時間5秒）
- 3回失敗したら静かに報告

**Report Format:**
```
[Browser] ブラウザ操作にタイムアウトしました。
- 試行回数: [X]/3
- 待機時間: [X]秒
- 次のアクション: 再試行または人間の判断待ち
```

### 5.2 Browser Crash
- browser がクラッシュした場合、静かに再起動を試みる
- retry は最大3回まで（冷却時間10秒）
- 3回失敗したら静かに報告

**Report Format:**
```
[Browser] ブラウザがクラッシュしました。
- 試行回数: [X]/3
- 待機時間: [X]秒
- 次のアクション: 再試行または人間の判断待ち
```

## 6. Panic Prevention Rules

### 6.1 No Panic Messages
- panic、エラー、失敗などのネガティブな表現を最小限にする
- 「問題ありません」「静かに回復しています」などの安心感を与える表現を優先する

### 6.2 No Repeated Notifications
- 同じ内容の通知・提案を繰り返さない
- 1つの問題に対して1回のみの報告

### 6.3 No Aggressive Recovery
- aggressive recovery は禁止
- silent recovery を優先する

### 6.4 No Forced Continuation
- forced continuation は禁止
- user の判断を待つ

## 7. Failure Response Matrix

| Failure Type | Retry Count | Cooldown | Report Level | Action |
|-------------|-------------|----------|--------------|--------|
| LLM Timeout | 3 | 5秒 | low | 再試行または待機 |
| Network Timeout | 5 | 10秒 | low | 再試行または待機 |
| Continuation Failure | 3 | 5秒 | low | 再試行または待機 |
| State Loss | 0 | - | medium | user の判断待ち |
| Browser Timeout | 3 | 5秒 | low | 再試行または待機 |
| Browser Crash | 3 | 10秒 | medium | 再試行または待機 |

---

*Project_18 - Calm Failure Handling*
*"panic runtime へ戻さない"*
