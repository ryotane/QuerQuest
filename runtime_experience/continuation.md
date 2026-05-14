# QueryQuest Continuation Experience Design

## 「自然な再開」であり、「強制的な継続」ではない

---

## 1. Continuation の基本方針

### 原則: Soft Continuity（柔らかな継続性）

- continuation は「自然な再開」である
- 強制再開は行わない
- 人間の意図を尊重する再開
- 記憶の提示は最小限

**体験目標**: 昨日の続きとして自然に感じられる

---

## 2. Continuation Visibility（継続の可視性）

### どの程度見せるか

| Level | Behavior | Use Case |
|-------|----------|----------|
| invisible | 記憶を提示しない | idle, human focus |
| minimal | 1行の要約のみ | quiet completion |
| moderate | 必要最小限の文脈提示 | continuation restore |
| full | 詳細な文脈提示 | 人間の要求時 |

**体験目標**: 記憶が自然に存在している感覚

---

## 3. Continuation Automation（継続の自動化）

### どの程度自動化しないか

| Aspect | Boundary |
|--------|----------|
| 自動再開 | 禁止 |
| 自動提案 | 抑制（1つまで） |
| 自動TODO生成 | 禁止 |
| 自動観察 | 禁止 |
| 人間の許可待ち | 必須 |

**体験目標**: 強制再開は不安を与える

---

## 4. Continuation Quietness（継続の静かさ）

### どの程度静かに行うか

| Aspect | Boundary |
|--------|----------|
| 通知頻度 | 最小限（1回のみ） |
| 提案数 | 1つまで |
| 要約長さ | 1行のみ |
| UI表示 | hidden（非表示） |
| バックグラウンド活動 | none（なし） |

**体験目標**: フローを壊さない静けさ

---

## 5. Continuation Human-Led（人間主導の継続）

### どの程度人間主導にするか

| Aspect | Boundary |
|--------|----------|
| 再開の判断 | 人間の許可が必要 |
| 継続範囲の決定 | 人間が指定 |
| 中断理由の確認 | 必要時のみ |
| 記憶の提示タイミング | 人間の要求時 |
| 継続の終了 | 人間の指示で停止 |

**体験目標**: 人間の思考が主役である感覚

---

## 6. Continuation Scenarios（シナリオ別設計）

### シナリオ1: タスク中断後の再開

```
[中断]
→ 最小限の文脈保持（メモリ内のみ）
→ 通知なし
→ 人間の再開指示待ち

[再開指示]
→ 必要最小限の文脈提示（1行）
→ 自然な復帰
→ 人間のペースに合わせる
```

### シナリオ2: セッション終了後の再開

```
[セッション終了]
→ session state を保存
→ 静かな終了

[次回起動]
→ session recovery の自然さ
→ 「また会えた」という安心感
→ 必要最小限の文脈提示
```

### シナリオ3: 複数タスク間の切り替え

```
[タスクA完了]
→ 最小限の要約（1行）
→ 直ちに停止

[タスクB開始]
→ タスクAの文脈は必要時のみ提示
→ 強制継続は行わない
```

---

## 7. Continuation Prohibited Behaviors（禁止行為）

以下の動作は厳禁：

| 禁止行為 | 理由 |
|---------|------|
| 自動再開 | 人間の意図を無視する |
| 強制提案 | フローを壊す |
| 冗長な文脈提示 | 認知負荷を増やす |
| 連続する3回の継続要求 | 人間を疲弊させる |
| 観察の無限ループ | runtime stability を損なう |

---

## 8. Continuation Metrics（測定指標）

### 体験品質の測定

| Metric | Target |
|--------|--------|
| continuation 再開までの時間 | < 3秒 |
| 文脈提示の冗長さ | 1行以内 |
| 人間の中断率 | < 5% |
| 提案の繰り返し率 | 0回 |
| 継続拒否率 | < 10% |

---

## Keywords

- Soft Continuity
- Natural Restart
- Human-Led Continuation
- Minimal Context
- Quiet Restoration
- Flow Protection

---

*このドキュメントは QueryQuest Runtime の継続体験を定義する。*
*全てのUX判断は、この Design を基準として行う。*
