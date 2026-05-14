# QueryQuest Project_20 - Continuity vs Calmness Balance

## テーマ: 「継続性を深くしすぎない」

---

## Core Concept

**「continuity を深くしすぎず、calmness を壊さない」**

Project_20の最大のリスクは：
- continuity を深くしすぎる
- memory を foreground 化する
- continuation pressure を増やす
- summary fatigue を生む
- runtime calmness を損なう

---

## Balance Matrix

| Aspect | Too Much Continuity | Too Little Continuity | **Balance** |
|--------|---------------------|-----------------------|-------------|
| Memory depth | 全履歴保存 | 前回のみ | 前々回〜数日 |
| Memory pressure | high | low | **low** |
| Continuation pressure | high | low | **low** |
| Summary fatigue | high | low | **low** |
| Runtime calmness | degraded | maintained | **maintained** |

---

## Balance Rules

### 1. continuity を深くしすぎない
- recent_sessions: 最大5件（前々回+α）
- active_themes: 最大3件
- これ以上は不要。深くする必要はない。

### 2. memory を foreground 化しない
- memory は background で動作する
- ユーザーに意識させない
- 必要時のみ参照可能

### 3. continuation pressure を増やさない
- forced_continuation は禁止（Project_18の原則を維持）
- natural resume のみを支援
- 「続きをやろう」という圧力を生まない

### 4. summary fatigue を生まない
- 要約は最小限（3行以内）
- 再帰的要約は禁止
- メタデータは不要

### 5. runtime calmness を壊さない
- memory pressure は低く保つ（< 5% of baseline）
- wakeup frequency は増加させない
- CPU usage は影響を受けない

---

## Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Memory explosion | Low | High | Entry limits + compression |
| Continuation pressure | Medium | Medium | No forced continuation |
| Summary fatigue | Low | Medium | 3行制限 + no recursive summary |
| Runtime slowdown | Low | High | Memory budget enforcement |
| User awareness of memory | Low | Low | Background operation only |

---

## Calmness Preservation Checklist

- [ ] memory pressure が baseline の5%以内か
- [ ] continuation pressure が増加していないか
- [ ] summary fatigue が発生していないか
- [ ] runtime calmness が損なわれていないか
- [ ] memory が foreground に上がっていないか

---

## Success Criteria (Revisited)

**成功条件:**
memory explosion を起こさず、前々回くらいの流れを自然に保てること。

**Calmness Preservation Condition:**
- memory pressure: < 5% of baseline
- continuation pressure: no increase
- summary fatigue: none
- runtime calmness: maintained

---

*Project_20 - Continuity vs Calmness Balance*
*"継続性を深くしすぎない"*
