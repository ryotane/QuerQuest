# QueryQuest Ambient Runtime Presence

## 「空気のように存在する」

---

## 1. Ambient Presence の基本方針

### 原則: Ambient Presence（環境的な存在感）

- idle 時は静か
- 必要時だけ foreground に上がる
- 常時アピール禁止
- human focus 優先

**体験目標**: 意識しなくても馴染む自然さ

---

## 2. Idle State（アイドル状態）

### idle 時の振る舞い

| Aspect | Boundary |
|--------|----------|
| 存在感 | invisible（見えない） |
| リソース消費 | minimal（最小限） |
| バックグラウンド活動 | none（なし） |
| UI表示 | hidden（非表示） |
| 通知 | none（なし） |

**体験目標**: Runtime が存在することを忘れる静かさ

---

## 3. Foreground Activation（フォアグラウンド昇格）

### 必要時だけ現れる

| Trigger | Behavior |
|---------|----------|
| 人間の明示的な要求 | foreground に上がる |
| emergency notification | 最小限の表示 |
| continuation restore | minimal context |
| error / failure | calm behavior |

**体験目標**: 必要な時にだけ現れる自然さ

---

## 4. Constant Appeal Prohibition（常時アピール禁止）

### アピールしない

| Aspect | Boundary |
|--------|----------|
| 常時アピール | 禁止 |
| バッジ表示 | 抑制 |
| ポップアップ | 禁止 |
| 自動通知 | 抑制 |

**体験目標**: Runtime が主張しない静けさ

---

## 5. Human Focus Priority（人間集中優先）

### 人間の作業を最優先する

| Aspect | Boundary |
|--------|----------|
| 人間の集中を中断しない | 最優先 |
| 人間のペースに合わせる | 必須 |
| 人間の判断を尊重する | 必須 |
| 人間の停止要求は直ちに実行 | 必須 |

**体験目標**: 人間の思考が主役である感覚

---

## 6. Ambient Presence Scenarios（シナリオ別設計）

### シナリオ1: idle 状態

```
[idle]
→ invisible（見えない）
→ リソース消費 minimal
→ バックグラウンド活動 none
→ 通知なし
```

### シナリオ2: 人間の要求時

```
[人間からの要求]
→ foreground に上がる
→ 最小限の表示
→ 静かな応答
→ 完了後直ちに invisible に戻る
```

### シナリオ3: emergency 時

```
[緊急事態]
→ minimal な表示（1行のみ）
→ panic suppression
→ 人間の判断待ち
→ 解決後直ちに invisible に戻る
```

---

## 7. Ambient Presence Prohibited Behaviors（禁止行為）

以下の動作は厳禁：

| 禁止行為 | 理由 |
|---------|------|
| 常時アピール | フローを壊す |
| バッジ表示 | 注意を奪う |
| ポップアップ | 人間の集中を中断する |
| 自動通知 | フローを壊す |

---

## Keywords

- Ambient Presence
- Invisible Idle
- Foreground Activation
- No Constant Appeal
- Human Focus Priority

---

*このドキュメントは QueryQuest Runtime の環境的な存在感を定義する。*
*全てのUX判断は、この Design を基準として行う。*
