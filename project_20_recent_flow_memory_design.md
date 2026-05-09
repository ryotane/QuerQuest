# QueryQuest Project_20 - Recent Flow Memory Design

## テーマ: 「前々回程度は自然に思い出せる」

---

## Core Concept

**「memory pressure を増やさない」**

recent flow memory は、以下の条件を満たす必要がある：
- 前々回程度の流れを自然に思い出せる
- recent decisions は保持
- active themes は軽く保持
- stale flow は自然減衰
- duplicate summaries は collapse

---

## Recent Flow Structure

### recent_flow.json

```json
{
  "recent_sessions": [
    {
      "session_id": "2025-01-15_14:30",
      "summary": "Project_20設計開始。continuity depthの定義。",
      "themes": ["project_20", "design"],
      "sentiment": 0.7,
      "status": "active",
      "created_at": 1736945400,
      "updated_at": 1736945400
    },
    {
      "session_id": "2025-01-14_10:00",
      "summary": "Project_19レポート確認。runtime preservationの整理。",
      "themes": ["project_19", "review"],
      "sentiment": 0.5,
      "status": "completed",
      "created_at": 1736842800,
      "updated_at": 1736842800
    }
  ],
  "active_themes": [
    {
      "theme": "project_20",
      "status": "design phase",
      "last_updated": 1736945400
    },
    {
      "theme": "runtime_calmness",
      "status": "ongoing",
      "last_updated": 1736842800
    }
  ],
  "recent_decisions": [
    {
      "decision": "continuity depth balance approach",
      "rationale": "memory explosionを回避するため、流れ保持に特化",
      "timestamp": 1736945400,
      "status": "active"
    }
  ],
  "decay_config": {
    "recent_ttl_days": 7,
    "archive_ttl_days": 90,
    "max_recent_sessions": 5,
    "max_active_themes": 3,
    "max_recent_decisions": 10
  }
}
```

---

## Flow Retention Rules

### 1. Natural Recall (前々回程度)
- recent_sessions は最大5件保持（直近5セッション）
- 各セッションは2-3行の要約のみ
- sentiment スコアで感情状態を記録
- status で進行中/完了を区別

### 2. Active Themes (軽く保持)
- active_themes は最大3件まで
- キーワード+状態のみ（詳細な説明なし）
- 完了したらstatus: "completed" に変更し、archiveへ移行

### 3. Recent Decisions (保持)
- recent_decisions は最大10件まで
- 決定内容と理由を簡潔に記録
- status で active/inactive を区別

### 4. Natural Decay (自然減衰)
- recent_sessions: 完了から7日経過でarchiveへ移行
- archive: 90日経過で自動消去
- decay は強制削除ではなく、優先度の低下として表現

### 5. Duplicate Collapse (重複要約の統合)
- 類似するセッションは統合する（同じテーマの連続セッション）
- duplicate detection は単純なキーワードマッチングで十分
- collapse 時は要約を結合し、sentiment を平均化

---

## Memory Pressure Control

### Entry Limits
| Field | Max Entries | Rationale |
|-------|-------------|-----------|
| recent_sessions | 5 | 前々回+α。これ以上は不要 |
| active_themes | 3 | 同時進行テーマの最小限 |
| recent_decisions | 10 | 重要な決定のみ保持 |

### Size Limits
- total file size: < 2KB（memory.db の約2%）
- session summary: < 50文字/件
- theme entry: < 30文字/件
- decision entry: < 100文字/件

---

## Stale Flow Handling

### Detection
- status: "completed" + created_at > 7日 → stale
- sentiment が低下（< 0.3）→ interest loss

### Action
- stale flow は archive へ移行
- archive 内の stale flow は90日で消去
- **強制削除ではなく、自然な忘却として処理**

---

## Example Flow Retention

```
Session A (1/15, active) → immediate layer
Session B (1/14, completed) → recent layer
Session C (1/13, completed) → recent layer
Session D (1/10, completed) → archive layer
Session E (12/20, completed) → deleted (>90 days)
```

**重要**: 各セッションは「全文」ではなく「要約」のみ保持。
memory pressure を増やさないことが最優先。

---

*Project_20 - Recent Flow Memory Design*
*"前々回程度は自然に思い出せる"*
