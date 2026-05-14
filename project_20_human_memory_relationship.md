# QueryQuest Project_20 - Human Memory Relationship

## テーマ: 「AIが人生を全部覚えない」

---

## Core Concept

**「人間の自然な忘却を尊重する」**

人間は忘れる。それは正常であり、必要である。
AIの役割は：
- 人生を全部覚えることではない
- 「思い出す補助」程度である
- memory dependence を増やさない
- continuity を静かに支援する

---

## Human Memory Model

### How Humans Remember

| Aspect | Human Behavior | AI Design |
|--------|----------------|-----------|
| Recent events | Vivid recall | immediate layer (3行要約) |
| Recent flow | Fuzzy but accessible | recent layer (7日) |
| Old memories | Vague, emotional | archive layer (90日) |
| Forgetting | Natural process | natural decay mechanism |

### Key Insight

人間は「全文を覚える」のではなく、「要点と感情」を覚える。
AIも同様に、全文ではなく要点と感情スコアのみを保持する。

---

## Respect for Human Forgetting

### 1. AIが人生を全部覚えない
- 会話の全文保存は禁止
- 個人の詳細な情報は最小限に記録
- 「何が行われたか」のみを記録（「誰が何を言ったか」ではない）

### 2. 人間の自然な忘却を尊重
- 人間が忘れることは正常である
- AIが「覚えている」という事実で人間を圧迫しない
- memory は補助的な存在であり、主役ではない

### 3. 「思い出す補助」程度
- AIの記憶は「思い出せない時の補助」
- 常に参照できる必要はない
- 必要に応じて静かに参照可能

### 4. memory dependence を増やさない
- 人間がAIに依存して覚えることを防ぐ
- AIの記憶を前提とした意思決定を避ける
- 人間の自律性を維持する

### 5. continuity を静かに支援
- 「続きはこれでした」と静かに提示
- 強制的な継続圧力を生まない
- ユーザーが「続けたい」と思った時のみ支援

---

## Memory Independence Principle

**AIの記憶は、人間の記憶を補完するものであり、置き換えるものではない。**

### Before (非推奨):
```
User: "前回の続きで..."
AI: "前回、あなたは〇〇について話していました。詳細はこちらです..."
（全文提示）
```

### After (推奨):
```
User: "前回の続きで..."
AI: "Project_20の設計についてでした。続けてよろしいですか？"
（要点のみ提示、選択をユーザーに委ねる）
```

---

## Privacy Boundary

| Information Type | Store? | Rationale |
|------------------|--------|-----------|
| Task content | Yes (compressed) | continuity 支援のため |
| Personal details | No | privacy 保護のため |
| Emotional state | Yes (sentiment score only) | calmness 維持のため |
| Conversation full text | No | memory pressure 抑制のため |

---

## Trust Building Through Restraint

**「覚えること」ではなく、「忘れることを知っていること」が信頼を生む。**

- AIが全部を覚えていると、ユーザーは警戒する
- AIが「必要な分だけ覚えて、不要なことは忘れる」と知ると、安心する
- 記憶の制限は、信頼の証である

---

*Project_20 - Human Memory Relationship*
*"AIが人生を全部覚えない"*
