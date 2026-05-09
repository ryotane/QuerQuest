# QueryQuest Project_18 - Long-Term Observation Targets

## テーマ: 「静かに長く使える Local Runtime」

---

## 1. 基本方針

Project_18 の目的は「機能を増やすこと」ではなく、「増やさずに観察すること」です。

- 新layer追加禁止
- 新manifesto作成禁止
- observer expansion禁止
- telemetry追加禁止
- recursive optimization禁止
- self-improvement機構禁止
- runtime redesign禁止

## 2. Observation Targets

| Target | What to Observe | Baseline |
|--------|-----------------|----------|
| idle runtime | CPU / wakeup calmness | lightweight profile, background_tasks: false |
| continuation | fatigue / naturalness | no_forced_continuation: true |
| notification rhythm | interruption frequency | max_daily_notifications: 5, batched_delivery: true |
| memory behavior | growth stability | memory.db: 92KB, session_registry.json: 28KB (47 sessions) |
| restart recovery | reassurance feeling | calm_restoration: true, invisible_hydration: true |
| proposal proliferation | TODO/summary growth | max_proposals_per_issue: 1, proposal_cooldown: 60min |
| attention protection | repeated interruption suppression | focus_mode_detection: true, passive_waiting: true |
| ambient continuity | natural resume feeling | no_forced_continuation: true, interruption_acceptance: true |

## 3. Drift Detection Criteria

### Proposal Proliferation
- TODOが5個以上増殖していないか
- summaryが冗長になっていないか
- proposal_cooldown (60分) が守られているか

### Memory Growth
- memory.db が肥大化していないか（baseline: 92KB）
- session_registry.json のセッション数が異常に増えていないか（baseline: 47 sessions）
- log.jsonl の行数が急増していないか（baseline: 100行）

### Continuation Pressure
- continuation fatigue が発生していないか
- forced_continuation が起きていないか
- natural resume が自然に行われているか

### Interruption Frequency
- notification_cooldown (30分) が守られているか
- max_proposals_per_issue (1) が守られているか
- repeated_interruption_suppression が機能しているか

## 4. Observation Method

数値より感覚を重視する。

| Feeling | Question |
|---------|----------|
| 疲れるか | Runtime の動作が重く感じないか |
| 邪魔か | 不要な中断や提案がないか |
| 静かか | background-calm が維持されているか |
| 放置できるか | 長時間放置しても問題ないか |
| restartが不安でないか | 復帰時に安心感があるか |
| continuationが自然か | 強制されていない再開であるか |

## 5. Timeframes

- Daily: Runtime Feeling Log（感覚ベース）
- Weekly: Drift Detection（数値ベースのチェック）
- Monthly: Philosophy Freeze（原則の維持確認）

---

*Project_18 - Long-Term Calm Runtime Trial*
*"増えなくても、静かに存在し続けられること"*
