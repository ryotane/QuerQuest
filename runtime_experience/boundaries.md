# QueryQuest Experience Boundaries

## 「どの状況で、どのような体験を提供するか」の境界線

---

## 1. Idle Runtime（アイドル状態）

| Aspect | Boundary |
|--------|----------|
| 存在感 | invisible（見えない） |
| リソース消費 | minimal（最小限） |
| バックグラウンド活動 | none（なし） |
| UI表示 | hidden（非表示） |
| 通知 | none（なし） |

**体験目標**: Runtime が存在することを忘れる静かさ

---

## 2. Successful Completion（完了時）

| Aspect | Boundary |
|--------|----------|
| 要約 | 1行のみ |
| 提案 | 抑制（人間の要求時のみ） |
| TODO生成 | 抑制（人間の要求時のみ） |
| 継続 | 人間の許可待ち |
| 終了 | 自然な終了 |

**体験目標**: 「できた」という静かな満足

---

## 3. Continuation Restore（再開時）

| Aspect | Boundary |
|--------|----------|
| 記憶の提示 | 最小限（必要時のみ） |
| 強制再開 | 行わない |
| 人間の意図尊重 | 優先 |
| 中断理由の確認 | 必要時のみ |
| 自然な復帰 | 目指す |

**体験目標**: 昨日の続きとして自然に感じられる

---

## 4. Repeated Suggestions（繰り返し提案）

| Aspect | Boundary |
|--------|----------|
| 同一提案の繰り返し | 禁止 |
| 提案数制限 | 1つまで |
| 3回以上同じ提案 | 抑制 |
| 人間の反応尊重 | 優先 |
| 疲労防止 | 最優先 |

**体験目標**: 提案が負担にならない軽さ

---

## 5. Restart Recovery（再起動時）

| Aspect | Boundary |
|--------|----------|
| 安心感提供 | 必要 |
| session recovery | 自然な流れで |
| failure 対応 | calm behavior |
| timeout 対応 | panic suppression |
| 再会感覚 | 「また会える」 |

**体験目標**: 「また始まる」ではなく「また会える」感覚

---

## 6. Human Focus State（人間集中時）

| Aspect | Boundary |
|--------|----------|
| 中断 | 禁止 |
| 通知 | 抑制 |
| 提案 | 待機 |
| 観察 | 最小限 |
| 人間のペース尊重 | 最優先 |

**体験目標**: フローを壊さない静けさ

---

## 7. Failure / Error（失敗時）

| Aspect | Boundary |
|--------|----------|
| panic 抑制 | 必須 |
| calm behavior | 維持 |
| 原因説明 | 最小限 |
| 解決策提示 | 1つまで |
| 人間の判断尊重 | 優先 |

**体験目標**: 不安ではなく冷静な対応

---

## 8. Timeout（タイムアウト時）

| Aspect | Boundary |
|--------|----------|
| panic suppression | 必須 |
| 静かな待機 | 維持 |
| 再試行 | 人間の許可待ち |
| エラー表示 | 最小限 |
| 回復手順 | 自然な流れで |

**体験目標**: パニックではなく冷静な対応

---

## Boundary Violation Detection（境界線違反検知）

以下の状況が発生した場合、Runtime は自律的に抑制する：

1. **通知の過剰**: 5分以内に2回以上の通知
2. **提案の繰り返し**: 同じ提案を3回以上
3. **継続の強制**: 人間の明示的な許可なしに継続
4. **要約の冗長**: 1行を超える要約
5. **観察の無限ループ**: 3回以上の逐次観察

---

## Keywords

- Invisible Idle
- Quiet Satisfaction
- Natural Continuity
- Fatigue Prevention
- Reassurance Recovery
- Flow Protection
- Calm Failure Handling
- Panic Suppression

---

*このドキュメントは QueryQuest Runtime の体験境界を定義する。*
*全てのUX判断は、この Boundaries を基準として行う。*
