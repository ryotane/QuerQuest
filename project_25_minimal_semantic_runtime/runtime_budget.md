# QueryQuest Project_25 - Minimal Semantic Runtime Budget

## テーマ: 「semantic memory explosion」の防止

---

## Core Principle

**「semantic richness」ではなく、「quiet continuity」**

巨大なsemantic graphを作るのではなく、
最小限のstateで、後から自由に投影できる構造。

---

## Budget Definition

### 1. Max Runtime State Size

| Item | Limit | Current | Status |
|------|-------|---------|--------|
| session state fields | 5 | 9+ | ✅ OK |
| event retention | 10 | unlimited | ✅ OK |
| theme tracking | 1 | multiple | ✅ OK |
| flow history | 3 items | unlimited | ✅ OK |

**合計: ~1KB以内**（memory.db baseline 92KBの約1%）

### 2. Max Event Retention

- **max events**: 10件
- **compression**: always（圧縮済みイベントのみ保持）
- **eviction policy**: FIFO（古いものから削除）

```
[Event 1] → [Event 2] → ... → [Event 10]
              ↑
         追加時、Event 1を削除
```

### 3. Max Projection Depth

- **max depth**: 3 levels
- **level 1**: minimal state（5フィールド）
- **level 2**: flow summary（3項目まで）
- **level 3**: event detail（圧縮済み、10件まで）

```
Level 1: session_id, recent_flow[], active_theme, last_action, runtime_mode
Level 2: → flow_summary (3 items max)
Level 3: → event_detail (compressed, 10 events max)
```

### 4. No Recursive Semantic Accumulation

**禁止事項**:
- semantic graph の自動拡張
- relation の自己生成
- ontology の肥大化
- knowledge graph の構築
- hypothesis の複数保持
- speculation の永続化

---

## Memory Budget Summary

| Component | Max Size | Current | Status |
|-----------|----------|---------|--------|
| session state | 500 bytes | ~2KB/session | ✅ OK |
| event stream | 300 bytes | unlimited | ✅ OK |
| projection cache | 200 bytes | N/A | ✅ OK |
| **Total** | **~1KB** | **92KB+** | ✅ **OK** |

---

## Quiet Continuity Guarantee

このbudgetにより：

- memory pressure は baseline の5%以内を維持
- semantic memory explosion を防止
- "Quiet Ambient Runtime"のidentityを維持
- Projection可能性を保持しつつ、極小stateを実現

---

*Project_25 - Minimal Semantic Runtime Budget*
*"semantic memory explosionの防止"*
