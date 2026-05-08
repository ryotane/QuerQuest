# QueryQuest Notification Rhythm Design

## 「Runtime は attention を奪わない」

---

## 1. Notification の基本方針

### 原則: Interruption-Light（低中断）

- 通知頻度は最小限
- cooldown を設ける
- repeated interruption を防止
- silent mode を尊重

**体験目標**: フローを壊さない静けさ

---

## 2. Notification Frequency（通知頻度）

### どの程度通知するか

| Situation | Frequency | Cooldown |
|-----------|-----------|----------|
| task completion | 1回のみ | none |
| continuation restore | 1回のみ | none |
| error / failure | 1回のみ | 5分 |
| proposal | 1つまで | 10分 |
| routine update | suppressed | - |

**体験目標**: 通知が負担にならない静かさ

---

## 3. Cooldown Policy（クールダウン方針）

### 重複通知の防止

| Notification Type | Cooldown | Reason |
|-------------------|----------|--------|
| task completion | none | 1回のみで十分 |
| error notification | 5分 | 同一エラーの繰り返し防止 |
| proposal | 10分 | 提案疲労防止 |
| status update | suppressed | フローを壊さないため |

**体験目標**: 同じ通知が繰り返されない静けさ

---

## 4. Suppression Rules（抑制ルール）

### いつ黙るか

| Situation | Behavior | Reason |
|-----------|----------|--------|
| human focus state | no notification | フロー保護 |
| task in progress | suppressed | 中断防止 |
| repeated error | suppressed after 2回 | パニック抑制 |
| idle runtime | no notification | invisible 維持 |

**体験目標**: 人間の集中を壊さない静けさ

---

## 5. Silent Mode（サイレントモード）

### silent mode の尊重

| Aspect | Boundary |
|--------|----------|
| silent mode 有効時 | 通知を抑制 |
| silent mode 無効化 | 人間の明示的な許可が必要 |
| emergency notification | 例外として許可 |
| silent mode 状態表示 | minimal（1行のみ） |

**体験目標**: 人間の選択を尊重する静けさ

---

## 6. Repeated Interruption Prevention（繰り返し中断防止）

### 同一通知の禁止

| Aspect | Boundary |
|--------|----------|
| 同一通知の繰り返し | 禁止 |
| 3回以上同じ提案 | 抑制 |
| notification spam | 厳禁 |
| フロー保護 | 最優先 |

**体験目標**: 中断が繰り返されない静けさ

---

## 7. Notification Scenarios（シナリオ別設計）

### シナリオ1: タスク完了時

```
[タスク完了]
→ 最小限の通知（1行のみ）
→ 直ちに停止
→ 追加通知なし
```

### シナリオ2: エラー発生時

```
[エラー検出]
→ 最初のエラー通知（1回のみ）
→ cooldown 5分
→ 同一エラーは抑制
→ 人間の判断待ち
```

### シナリオ3: human focus state 時

```
[人間集中状態]
→ 全ての通知を抑制
→ タスク完了後も待機
→ 人間の指示で再開
```

---

## 8. Notification Prohibited Behaviors（禁止行為）

以下の動作は厳禁：

| 禁止行為 | 理由 |
|---------|------|
| notification spam | フローを壊す |
| repeated interruption | 人間を疲弊させる |
| silent mode の無視 | 人間の選択を無視する |
| emergency 以外の常時通知 | 不安を与える |

---

## Keywords

- Interruption-Light
- Quiet Notification
- Flow Protection
- Cooldown Policy
- Silent Mode Respect

---

*このドキュメントは QueryQuest Runtime の通知リズムを定義する。*
*全てのUX判断は、この Design を基準として行う。*
