# QueryQuest Project_20 - Continuity Layer Design

## テーマ: 「流れ保持」のための階層構造

---

## Core Concept

**「全文保持」ではなく、「流れ保持」**

各レイヤーは「何を保つか」「どれくらい保つのか」を定義する。
memory pressure を増やさないことが最優先。

---

## Layer Definition

| Layer | Purpose | Retention | Format | Memory Cost |
|-------|---------|-----------|--------|-------------|
| **immediate** | 前回セッションの文脈 | 1 session | 要約（3行以内） | minimal |
| **recent** | 最近の流れ（数日） | 数日〜1週間 | テーマ単位要約 | low |
| **ongoing** | active themes | 数週間 | キーワード+状態 | very low |
| **stable** | 長期方針・identity | 長期 | 原則のみ | minimal |
| **archive** | 古い流れ（完了テーマ） | passive | 圧縮アーカイブ | negligible |

---

## Layer Details

### immediate - 前回セッションの文脈
- **目的**: 「前回の続き」を自然に開始できる
- **保持内容**: セッション要約（3行以内）、残タスク、感情スコア
- **削除条件**: 次のセッション開始時に圧縮・統合
- **memory cost**: minimal（1セッション分）

### recent - 最近の流れ
- **目的**: 「数日前の流れ」を自然に思い出せる
- **保持内容**: テーマ単位要約（各テーマ2-3行）、進行状態、感情スコア
- **削除条件**: 完了から7日経過でnatural decay
- **memory cost**: low（テーマ数×2-3行）

### ongoing - active themes
- **目的**: 「現在進行中のテーマ」を軽く保持
- **保持内容**: キーワード+状態（例: "project_20: design phase"）
- **削除条件**: 完了または1ヶ月経過でarchiveへ移行
- **memory cost**: very low（キーワードのみ）

### stable - 長期方針・identity
- **目的**: QueryQuestの根本原則を保持
- **保持内容**: identity, philosophy, boundaries（Project_18/19の原則）
- **削除条件**: 変更がない限り永続
- **memory cost**: minimal（原則のみ）

### archive - 古い流れ
- **目的**: 完了したテーマの記録を静かに保持
- **保持内容**: 圧縮アーカイブ（1行要約+日付）
- **削除条件**: 3ヶ月経過で自動消去
- **memory cost**: negligible（1行×テーマ数）

---

## Flow Retention Model

```
[immediate] ← [recent] ← [ongoing] ← [stable] ← [archive]
   ↑              ↑            ↑           ↑           ↑
 前回          最近の流れ    active      長期        古い流れ
 session       数日〜1週間    themes      方針        passive
```

**重要**: 各レイヤーは独立して管理される。
- immediate は常に最新に更新
- recent は自然減衰（7日）
- ongoing は完了でarchiveへ移行
- stable は原則のみ（変更稀）
- archive は3ヶ月で消去

---

## Memory Budget

| Layer | Max Entries | Avg Size/Entry | Total Cost |
|-------|-------------|----------------|------------|
| immediate | 1 | ~200 bytes | ~200 bytes |
| recent | 5 | ~150 bytes | ~750 bytes |
| ongoing | 3 | ~50 bytes | ~150 bytes |
| stable | 1 | ~500 bytes | ~500 bytes |
| archive | 20 | ~80 bytes | ~1.6 KB |

**合計: ~3.2 KB**（memory.db baseline 92KBの約3.5%）

---

## Natural Decay Mechanism

```
recent → decay (7日) → archive → decay (3ヶ月) → delete
ongoing → complete → archive → decay (3ヶ月) → delete
immediate → next session → compress into recent
```

**強制削除ではなく、優先度の低下として表現する。**

---

*Project_20 - Continuity Layer Design*
*"流れ保持のための階層構造"*
