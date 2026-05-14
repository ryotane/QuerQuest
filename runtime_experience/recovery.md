# QueryQuest Recovery Experience Design

## 「restart/recovery は安心感がある」

---

## 1. Recovery の基本方針

### 原則: Recovery Reassurance（回復の安心感）

- restart 後の安心感
- session recovery の自然さ
- failure 後の calm behavior
- timeout 時の panic suppression

**体験目標**: 「また始まる」ではなく「また会える」感覚

---

## 2. Restart Experience（再起動体験）

### restart 後の安心感

| Aspect | Boundary |
|--------|----------|
| 起動メッセージ | 静かな挨拶のみ |
| session recovery | 自然な流れで |
| state restoration | 最小限の提示 |
| panic suppression | 必須 |

**体験目標**: 「また会えた」という安心感

---

## 3. Session Recovery（セッション回復）

### session recovery の自然さ

| Aspect | Boundary |
|--------|----------|
| recovery 方法 | 自動で最小限の提示 |
| state restoration | 必要最小限のみ |
| 中断理由の確認 | 必要時のみ |
| 人間のペース尊重 | 最優先 |

**体験目標**: 自然な復帰の流れ

---

## 4. Failure Behavior（失敗時の振る舞い）

### failure 後の calm behavior

| Aspect | Boundary |
|--------|----------|
| panic suppression | 必須 |
| エラー説明 | 最小限（1行のみ） |
| 解決策提示 | 1つまで |
| 人間の判断尊重 | 優先 |

**体験目標**: 不安ではなく冷静な対応

---

## 5. Timeout Handling（タイムアウト処理）

### timeout 時の panic suppression

| Aspect | Boundary |
|--------|----------|
| パニック抑制 | 必須 |
| タイムアウト通知 | 最小限（1行のみ） |
| 再試行 | 人間の許可待ち |
| エラー表示 | 静かに |

**体験目標**: パニックではなく冷静な対応

---

## 6. Recovery Scenarios（シナリオ別設計）

### シナリオ1: 通常再起動時

```
[再起動]
→ 静かな起動メッセージ
→ session recovery の自然さ
→ 「また会えた」という安心感
→ 必要最小限の文脈提示
```

### シナリオ2: エラー発生後

```
[エラー検出]
→ panic suppression（冷静な対応）
→ 最小限のエラー説明（1行のみ）
→ 解決策の提示（1つまで）
→ 人間の判断待ち
```

### シナリオ3: タイムアウト時

```
[タイムアウト]
→ panic suppression（冷静な対応）
→ 最小限の通知（1行のみ）
→ 再試行は人間の許可待ち
→ 静かな待機
```

---

## 7. Recovery Prohibited Behaviors（禁止行為）

以下の動作は厳禁：

| 禁止行為 | 理由 |
|---------|------|
| panic behavior | 不安を与える |
| エラーの過剰説明 | 認知負荷を増やす |
| 自動再試行 | 人間の意図を無視する |
| 冗長な recovery メッセージ | フローを壊す |

---

## Keywords

- Recovery Reassurance
- Calm Failure Handling
- Panic Suppression
- Natural Restoration
- Quiet Restart

---

*このドキュメントは QueryQuest Runtime の回復体験を定義する。*
*全てのUX判断は、この Design を基準として行う。*
