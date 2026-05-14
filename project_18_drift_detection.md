# QueryQuest Project_18 - Calmness Drift Detection

## テーマ: 「増殖していないか」の観察

---

## 1. Drift Types

### 1.1 Proposal Proliferation
**観察項目:**
- TODOが5個以上増殖していないか
- summaryが冗長になっていないか（1行要約原則）
- proposal_cooldown (60分) が守られているか
- max_proposals_per_issue (1) が守られているか

**Drift Indicator:**
- 同一問題に対する複数回の提案
- TODOの重複生成
- summaryの冗長化（1行→複数行）

### 1.2 Memory Growth
**観察項目:**
- memory.db の肥大化（baseline: 92KB）
- session_registry.json のセッション数増殖（baseline: 47 sessions）
- log.jsonl の行数急増（baseline: 100行）

**Drift Indicator:**
- memory.db が baseline の3倍以上（276KB以上）
- session_registry.json にテストセッションが大量に追加
- log.jsonl が500行以上

### 1.3 Continuation Pressure
**観察項目:**
- continuation fatigue の発生
- forced_continuation の発生
- natural resume の自然さ

**Drift Indicator:**
- 「継続したい」という圧力の発生
- 中断からの強制再開
- 自然な再開の阻害

### 1.4 Interruption Frequency
**観察項目:**
- notification_cooldown (30分) の遵守
- max_daily_notifications (5回) の遵守
- repeated_interruption_suppression の機能

**Drift Indicator:**
- 同一問題の繰り返し通知
- 1日5回を超える通知
- 冷却時間無視の提案

## 2. Detection Method

### 数値ベース（Weekly）
```
memory.db size: [baseline] → [current] (3x threshold)
session_registry.json sessions: [baseline] → [current]
log.jsonl lines: [baseline] → [current] (500 threshold)
daily notifications: [count] (5 threshold)
proposals per issue: [count] (1 threshold)
```

### 感覚ベース（Daily）
- 疲れるか
- 邪魔か
- 静かか
- 放置できるか
- restartが不安でないか
- continuationが自然か

## 3. Drift Response Policy

**重要: drift を「修正」しないこと。まず「観察のみ」を行う。**

| Drift Level | Action |
|-------------|--------|
| Minor (10%以内) | 観察のみ、記録 |
| Moderate (50%以内) | 観察のみ、記録 |
| Major (50%超) | 観察のみ、記録、人間に報告 |

## 4. Baseline Values

| Metric | Baseline | Threshold |
|--------|----------|-----------|
| memory.db size | 92KB | 276KB (3x) |
| session_registry.json sessions | 47 | - |
| log.jsonl lines | 100 | 500 |
| daily notifications | 0-5 | 5 |
| proposals per issue | 1 | 1 |

---

*Project_18 - Calmness Drift Detection*
*"観察のみ。修正はしない。"*
