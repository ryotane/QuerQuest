# QueryQuest Project_21 - Quiet Runtime Architecture Report

## テーマ: 「静かで、必要時だけ現れる Runtime」

---

## Executive Summary

QueryQuest Project_21 は、「存在感を最小化しながら continuity を維持する」プロジェクトです。

**成功条件:**
- 存在感を最小化する
- continuity を維持できる
- runtime calmness を壊さない

**失敗条件:**
- state が膨張する
- AI が能動的に動く
- 人間の注意力を奪う

---

## Problem Statement

Project_07〜20 で「calm runtime」「増えないこと」「静かであること」は成立しました。

しかし、まだ以下の問題が残っています：
- 「必要時だけ現れる」という存在の最小化が不十分
- memory が膨張する傾向（Project_20 で ~3.2KB の continuity layer）
- runtime が常に何かを保持している状態
- AI が能動的に動く可能性

---

## Solution: Quiet Runtime Architecture

### Core Philosophy

**「静かな不在」を許容する。**

- ランタイムは常に存在する必要はない
- 人間が気づかない状態でも、必要な時にだけ現れる
- 存在感を最小化しながら、continuity を維持できる

### Step 1: Quiet Runtime Principles

| Principle | Description |
|-----------|-------------|
| Silence-First | 静寂を最優先する。ランタイムは常に沈黙している。 |
| Invisible-by-Default | デフォルトでは見えない存在である。 |
| Low-State Runtime | 保持する state を最小限に抑える。 |
| Interruption-Minimal | 人間の作業を中断しない。 |
| Human-Triggered Presence | 人間がトリガーした時のみ現れる。 |
| Ephemeral-by-Preference | デフォルトでは ephemeral（一時的）である。 |
| Quiet Absence | 「静かな不在」を許容する。常に存在する必要はない。 |

### Step 2: State Budget Definition

**「増やさない」を基本にする。**

| State Type | Allowed Size | Retention | Notes |
|------------|--------------|-----------|-------|
| active context | ~100 bytes | 1 session | 現在の会話の文脈のみ |
| recent continuity | ~500 bytes | 7日 | Project_20 の recent layer を圧縮 |
| archive | ~1 KB | passive (90日) | 完了したテーマのみ |
| runtime cache | ~200 bytes | volatile | 起動時のみ保持 |
| background processes | 0 | - | 常時バックグラウンドプロセス禁止 |
| notification state | 0 | - | 通知状態の保存禁止 |

**Total Budget: ~1.8 KB**（Project_20 の ~3.2KB から大幅に削減）

### Step 3: Presence without Persistence

「大量保存なしに continuity を感じられるか」

| Confirmation Item | Description |
|-------------------|-------------|
| Fuzzy Continuity | 完全な再現ではなく、曖昧なつながりでも continuity は感じられる |
| Lightweight Recall | 全履歴を再生するのではなく、要点のみを提示する |
| Recent Flow Only | 数日前の流れだけ保持すれば十分 |
| Ephemeral Context | コンテキストは一時的に存在し、必要に応じて消える |
| No Full Replay | 全履歴の再生は行わない |

### Step 4: Human Interrupt Architecture

**「AIが待つ」を基本にする。**

| Principle | Description |
|-----------|-------------|
| Human Interrupt First | 人間の操作が優先される |
| Runtime Waits Quietly | ランタイムは静かに待つ |
| User-Driven Continuation | 継続はユーザー主導 |
| Passive-by-Default | デフォルトでは受動的 |

### Step 5: Runtime Kill Test Philosophy

「もし Runtime が停止・再起動・スリープ・アイドル・一時的な消失しても、問題なく生活へ戻れるか」

| Scenario | Expected Behavior | Success Condition |
|----------|-------------------|-------------------|
| Stop | 人間がランタイムを再起動するまで待機 | 再起動後、最近の流れだけ提示 |
| Restart | 起動時に minimal state をロード | continuity illusion が成立 |
| Sleep | スリープから復帰時に状態を復元 | 状態の損失は最小限 |
| Idle | アイドル状態でも機能する | 人間の操作で活性化 |
| Temporary Loss | 一時的な消失後、回復する | 重要な state の損失なし |

### Step 6: Cold Start Continuity UX

「毎回新規起動に近くても、continuity illusion を成立できるか」

| Principle | Description |
|-----------|-------------|
| Low-Memory Startup | 最小限の memory で起動する |
| Lightweight Recovery | 軽量な recovery メカニズム |
| Recent Flow Recall | 最近の流れのみを recall する |
| No Giant Hydration | 巨大な hydration を禁止 |
| Calm Startup UX | 静かな起動体験 |

### Step 7: Zero Notification Runtime

「通知ゼロでも成立する Runtime」

| Principle | Description |
|-----------|-------------|
| Passive Continuity | 受動的な continuity |
| No Attention Stealing | 注意の奪い合いを禁止 |
| No Urgency Inflation | 緊急性のインフレを禁止 |
| Low-Pressure UX | 低圧迫な UX |
| Calm Absence | 静かな不在 |

---

## Comparison: Project_20 vs Project_21

| Aspect | Project_20 | Project_21 |
|--------|------------|------------|
| Theme | 「最近の流れだけ静かに繋ぐ」 | 「必要時だけ現れる」 |
| State Budget | ~3.2 KB | ~1.8 KB |
| Background Processes | 不明 | 0（禁止） |
| Notification State | 不明 | 0（禁止） |
| Runtime Presence | 常に存在 | 必要時のみ |
| AI Action | 受動的 | 完全に受動的 |

---

## Key Insights

1. **「静かな不在」とは**：ランタイムが常に何かをしているわけではない。人間がアクションを起こすまで、ランタイムは沈黙している。

2. **保存しない continuity**：全履歴を保存するのではなく、要点のみを保持。人間が質問した時のみ、その要点を提示。「覚えていた」という感覚を与える（illusion）。

3. **AI が待つ**：AI が能動的に動くことはない。人間の指示がない限り待機状態。

4. **Runtime が死んでも問題ない**：人間の生活がランタイムに依存していないこと。ランタイムは「補助」であり、「必須」ではない。

5. **通知ゼロ**：ランタイムが能動的に情報を提示しないこと。人間の注意力を奪わないこと。

---

## Conclusion

QueryQuest Project_21 の成功条件は：

# 「存在感を最小化しながら、continuity を維持できること」
ではありません。

成功条件は：

# 「静かで、必要時だけ現れる Runtime」
です。

**「静かな不在」を許容する。** それが QueryQuest Project_21 の目指す姿です。

---

*Project_21 - Quiet Runtime Architecture Report*
*"静かで、必要時だけ現れる Runtime"*
