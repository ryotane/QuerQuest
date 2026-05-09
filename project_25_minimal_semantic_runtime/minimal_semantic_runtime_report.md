# QueryQuest Project_25 - Minimal Semantic Runtime Report

## テーマ: 「静かなRuntimeを維持したまま、後から自由に投影できる構造」

---

## 1. Project Overview

### Purpose

Project_24までで定義された「quiet runtime」「ambient infrastructure」「silence-first philosophy」「lightweight continuity」「no-maintenance runtime」を壊さず、
**Projection可能だが極小stateのRuntime**を定義する。

### Success Criteria

- HTMLを作ることではない
- Runtimeを壊さず、Projection可能性だけを持つこと

---

## 2. Minimal Runtime State Definition

### Before (Project_07-24)

```json
{
  "chat_id": "",
  "title": "",
  "workspace_id": "",
  "summary": "",
  "recent_topics": [],
  "active_goals": [],
  "last_user_intent": "",
  "updated_at": "",
  "next_actions": []
}
```

**問題**: 9フィールド以上、過剰な情報保持

### After (Project_25)

```json
{
  "session_id": "",
  "recent_flow": [],
  "active_theme": "",
  "last_action": "",
  "runtime_mode": ""
}
```

**改善**: 5フィールドに削減、Projectionに必要な情報のみ保持

---

## 3. Minimal Event System Definition

### Defined Events (6 types)

| Type | Purpose | Compression |
|------|---------|-------------|
| reasoning | 推論イベント | always |
| continuation | 継続イベント | always |
| tool_call | ツール呼び出し | always |
| compression | 圧縮イベント | - |
| interruption | 中断イベント | - |
| restart | リスタートイベント | - |

### Retention Policy

- **max events**: 10件
- **eviction**: FIFO（古いものから削除）
- **compression**: always（圧縮済みイベントのみ保持）

---

## 4. Semantic Structure Boundaries

### Boundary 1: No Semantic Graph Expansion

**禁止**: semantic graphの自動拡張、relationの自己生成、ontologyの肥大化

**許可**: minimal stateの保持（5フィールド）、event streamの記録（圧縮済み）

### Boundary 2: No Branch Persistence Overload

**禁止**: branchの永続化（3つ以上）、parallel contextの保存、fork historyの保持

**許可**: single flowの追跡、linear continuationの記録

### Boundary 3: No Uncertainty Over-save

**禁止**: uncertaintyの詳細保存、confidence scoreの逐次記録、hypothesisの複数保持

**許可**: last_actionの記録、runtime_modeの追跡

### Boundary 4: No Replay System

**禁止**: full replayの実装、session historyの逐次再生、time travelのサポート

**許可**: last_actionの参照、recent_flowのスキャン（3件まで）

---

## 5. Projection Separation Philosophy

### Architecture

```
┌─────────────────────────────────────┐
│         Runtime (Minimal)           │
│                                     │
│  - session_id                       │
│  - recent_flow []                   │
│  - active_theme ""                  │
│  - last_action ""                   │
│  - runtime_mode ""                  │
│                                     │
│  + events[] (compressed, max:10)    │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│      Projection Layer               │
│                                     │
│  - state → HTML/MD/SVG              │
│  - ephemeral generation             │
│  - low-density output               │
│  - on-demand rendering              │
└──────────────┬──────────────────────┘
               │
               ▼
┌─────────────────────────────────────┐
│         View (HTML/MD/SVG)          │
│                                     │
│  - no state source                  │
│  - read-only                        │
│  - ephemeral                        │
│  - low-attention                    │
└─────────────────────────────────────┘
```

### Separation Rules

1. **Runtime Never Generates HTML** - RuntimeはHTMLを生成しない
2. **Projection is Ephemeral** - Projectionは一時的に生成される
3. **State Source is Always Runtime** - stateの唯一のsourceはRuntime
4. **Projection is Low-Density** - Projectionは低密度で生成される

---

## 6. Calm Projection Design

### Projection Characteristics

| Characteristic | Description |
|---------------|-------------|
| Ephemeral | 一度生成されると再生成されない限り保持されない |
| Low-Density | 大量の情報や詳細な表示は行わない |
| Low-Attention | 人間の注意を奪わない |
| Non-Persistent | 永続化されない |

### Calm Projection Rules

| Rule | Description |
|------|-------------|
| No auto-projection | 自動投影禁止 |
| No persistent projection | 永続投影禁止 |
| No high-density output | 高密度出力禁止 |
| No attention-grabbing UI | 注意を引くUI禁止 |
| No animation | アニメーション禁止 |

---

## 7. Minimal Semantic Runtime Budget

### Memory Budget

| Component | Max Size | Status |
|-----------|----------|--------|
| session state | 500 bytes | ✅ OK |
| event stream | 300 bytes | ✅ OK |
| projection cache | 200 bytes | ✅ OK |
| **Total** | **~1KB** | ✅ **OK** |

### Projection Depth Budget

- **max depth**: 3 levels
- level 1: minimal state（5フィールド）
- level 2: flow summary（3項目まで）
- level 3: event detail（圧縮済み、10件まで）

---

## 8. Identity Freeze Verification

### Current Identity

**"Quiet Ambient Runtime"** - 変更なし

### Projection-Compatible Addition

```
Quiet Ambient Runtime
├── Quiet (維持)
│   ├── projection on-demand only
│   ├── low-density output
│   └── no animation
├── Ambient (維持)
│   ├── invisible-by-default
│   ├── background presence
│   └── no forced continuity
├── Runtime (維持)
│   ├── calm runtime
│   ├── ambient presence
│   └── low interruption
└── Projection-Compatible (追加)
    ├── state → projection separation
    ├── ephemeral projection
    └── on-demand rendering
```

**重要**: "Projection-Compatible"はidentityの拡張ではなく、
既存identityの「投影可能性」を追加するものである。

---

## 9. Summary

### What Changed

- Runtime state: 9+ fields → 5 fields（44%削減）
- Event retention: unlimited → 10 events（FIFO）
- Semantic graph expansion: prohibited
- Branch persistence: limited to single flow
- Uncertainty over-save: prohibited
- Replay system: not implemented

### What Stayed the Same

- "Quiet Ambient Runtime" identity - unchanged
- Calm runtime principles - maintained
- Ambient presence philosophy - maintained
- Low interruption policy - maintained
- Compression-first approach - maintained

### New Capability Added

- Projection compatibility（後からHTML/MD/SVGへ投影可能）
- State → Projection Layer → View separation
- Ephemeral, low-density projection design

---

## 10. Conclusion

Project_25の成功条件は達成された：

**「Runtimeを壊さず、Projection可能性だけを持つこと」**

- Runtime stateは極小（5フィールド）
- Event systemは最小限（6 types, max:10 events）
- Semantic structure boundariesで肥大化防止
- Projection Separation PhilosophyでHTMLと分離
- Calm Projection Designで静かな投影を実現
- Minimal Budgetでsemantic memory explosion防止
- Identity Freezeで"Quiet Ambient Runtime"を維持

---

*Project_25 - Minimal Semantic Runtime Report*
*"静かなRuntimeを維持したまま、後から自由に投影できる構造"*
