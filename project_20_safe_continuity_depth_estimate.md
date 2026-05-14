# QueryQuest Project_20 - Safe Continuity Depth Estimate

## テーマ: 「Calm Runtime を壊さず、continuity をどこまで深くできるか」

---

## Executive Summary

**Safe continuity depth: 5 recent sessions + 3 active themes + 20 archive entries (~3.2KB)**

これにより：
- ✅ Recent flow retention（前々回〜数日前）
- ✅ Active theme tracking
- ✅ Archive for completed themes
- ✅ Safe growth limit内（148KBの余裕）
- ❌ Recursive summarization risk なし
- ❌ Continuation fatigue risk なし

---

## Current State Analysis

### Memory Pressure Baseline

| Metric | Value | Baseline | Status |
|--------|-------|----------|--------|
| memory.db size | 94,208 bytes (~92KB) | ~92KB | ✅ Normal |
| session_registry.json | 28,469 bytes (~28KB) | ~28KB (47 sessions) | ⚠️ Test sessions inflated |
| memory/log.jsonl | 7,973 bytes (~8KB) | ~8KB (4 entries) | ✅ Normal |
| **Total** | **~128KB** | **~92KB** | **+39%** |

### Key Findings

1. **memory.db is stable** - baseline level maintained
2. **session_registry.json inflated by test sessions** - 47 sessions, mostly tests
3. **Compression mechanism exists but simple** - MemoryManager.compress() only removes oldest entries when exceeding max_items (500)
4. **No recursive summarization** - current compression is just truncation
5. **Continuation orchestrator has adaptive modes** - FULL/COMPRESSED/PARTIAL based on context_usage

---

## Analysis: Where Safe Growth Ends

### 1. Where safe growth ends

Current memory pressure: ~128KB (baseline +39%)

Safe growth threshold: baseline × 3 = **276KB**（Project_19 definition）

**Safe growth limit: ~276KB total**
- Current: ~128KB
- Room for growth: **~148KB**

### 2. Where recursive memory pressure starts

Recursive memory pressure occurs when：
- Memory grows without compression → token explosion risk
- Continuation context becomes too large → LLM processing degradation
- Multiple layers of summaries create amplification

**Threshold: When memory.db exceeds 276KB (3x baseline)**
- At this point, compression_trigger_ratio (0.7) would trigger
- But current compress() only truncates oldest entries - no intelligent summarization
- Risk: token budget explosion if context grows beyond 50k tokens

### 3. Where summary amplification starts

Summary amplification occurs when：
- Each session generates a summary → next session summarizes the summary → recursive loop
- Current system has NO recursive summarization (good)
- But continuation orchestrator's restore_context() could amplify if context_usage is high

**Threshold: When context_usage > 0.6 (PARTIAL mode)**
- At this point, only minimal context is restored
- Risk: If FULL/COMPRESSED modes are used with large summaries, amplification occurs

### 4. Where continuation fatigue starts

Continuation fatigue occurs when：
- Forced continuation pressure increases
- User feels "I have to continue" instead of "I want to continue"
- Natural resume feeling degrades

**Threshold: When forced_continuation > 0 (currently disabled)**
- Project_18/19 established no_forced_continuation: true
- Risk: If continuity depth increases, user may feel pressure to continue

### 5. How deep can we go for natural flow retention?

Based on current architecture：

**immediate layer**: 1 session (~200 bytes) - already exists via continuation orchestrator
**recent layer**: 5 sessions (~750 bytes) - needs implementation
**ongoing layer**: 3 themes (~150 bytes) - needs implementation
**stable layer**: principles only (~500 bytes) - already exists in philosophy files
**archive layer**: 20 entries (~1.6KB) - needs implementation

Total: **~3.2KB additional**（well within safe growth limit of 148KB）

---

## Safe Continuity Depth Estimate

### Memory Budget Allocation

| Layer | Max Entries | Size/Entry | Total | Status |
|-------|-------------|------------|-------|--------|
| immediate | 1 | ~200 bytes | ~200 bytes | ✅ Exists (continuation orchestrator) |
| recent | 5 | ~150 bytes | ~750 bytes | ⚠️ Needs implementation |
| ongoing | 3 | ~50 bytes | ~150 bytes | ⚠️ Needs implementation |
| stable | 1 | ~500 bytes | ~500 bytes | ✅ Exists (philosophy files) |
| archive | 20 | ~80 bytes | ~1.6KB | ⚠️ Needs implementation |

**Total additional: ~3.2KB**
**Current memory pressure: ~128KB**
**Safe growth limit: ~276KB**
**Remaining headroom: ~145KB**

### Safe Continuity Depth Limits

| Aspect | Current | Safe Limit | Risk Threshold |
|--------|---------|------------|----------------|
| Recent sessions | 0 (only immediate) | **5** | >10 → recursive pressure |
| Active themes | 0 | **3** | >5 → summary amplification |
| Archive entries | 0 | **20** | >50 → memory explosion |
| Total continuity memory | ~0 bytes | **~3.2KB** | >148KB → compression trigger |

### Key Risk Points

1. **Recursive memory pressure**: Starts when session_registry.json exceeds 100 sessions（currently 47, mostly tests）
2. **Summary amplification**: Starts when context_usage > 0.6 and FULL/COMPRESSED modes are used with large summaries
3. **Continuation fatigue**: Starts when forced_continuation is enabled or natural resume feeling degrades
4. **Memory explosion**: Starts when total memory exceeds 276KB（3x baseline）

---

## Unsafe Continuity Depth (Avoid)

| Aspect | Unsafe Limit | Risk |
|--------|--------------|------|
| Recent sessions | >10 | Recursive memory pressure |
| Active themes | >5 | Summary amplification |
| Archive entries | >50 | Memory explosion |
| Total continuity memory | >148KB | Compression trigger + token explosion |
| Context usage | >0.6 with FULL mode | Summary amplification |
| Forced continuation | Enabled | Continuation fatigue |

---

## Conclusion

**Safe continuity depth: 5 recent sessions + 3 active themes + 20 archive entries (~3.2KB)**

This provides：
- ✅ Recent flow retention（前々回〜数日前）
- ✅ Active theme tracking
- ✅ Archive for completed themes
- ✅ Well within safe growth limit（148KB headroom）
- ❌ No recursive summarization risk
- ❌ No continuation fatigue risk

**Unsafe continuity depth**: Anything beyond this requires：
- ❌ Recursive summarization（amplification risk）
- ❌ Full conversation storage（memory explosion risk）
- ❌ Forced continuation（fatigue risk）
- ❌ Vector DB expansion（calmness destruction risk）

---

*Project_20 - Safe Continuity Depth Estimate*
*"Calm Runtime を壊さず、continuity をどこまで深くできるか"*
