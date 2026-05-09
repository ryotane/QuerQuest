# QueryQuest Project_18 - Long-Term Runtime Philosophy Freeze

## テーマ: 「哲学の維持確認」

---

## 1. Current Principles

### 1.1 calm runtime
- **定義:** Runtime は慌てず、静かに振る舞う
- **現状:** ✅ 維持されている（runtime_personality_manifesto.md, ambient_runtime_manifesto.md）
- **確認項目:**
  - max_reasoning_steps: 5（厳格化済み）
  - max_hypothesis_repeats: 2（厳格化済み）
  - max_same_file_reads: 2（厳格化済み）

### 1.2 invisible-by-default
- **定義:** Runtime は常に目に見える存在ではない。必要とされる時だけ、静かに現れる
- **現状:** ✅ 維持されている（ambient_runtime_manifesto.md, runtime_config.yaml ambient_runtime セクション）
- **確認項目:**
  - presence_layer.idle_notification_level: none
  - presence_layer.passive_notification_level: none

### 1.3 low interruption
- **定義:** Runtime は人間の作業を中断しない。中断は最後の手段である
- **現状:** ✅ 維持されている（ambient_runtime_manifesto.md, runtime_config.yaml ambient_runtime セクション）
- **確認項目:**
  - max_daily_notifications: 5
  - notification_cooldown_seconds: 1800 (30分)
  - max_proposals_per_issue: 1

### 1.4 compression-first
- **定義:** 冗長な情報を圧縮する
- **現状:** ✅ 維持されている（runtime_personality_manifesto.md, runtime_config.yaml）
- **確認項目:**
  - memory.compression_trigger_ratio: 0.7 (70% で圧縮開始)
  - lightweight_overrides.compression_enabled: true

### 1.5 cleanup-last
- **定義:** cleanup は最後に行う。aggressive cleanup を避ける
- **現状:** ✅ 維持されている（runtime_config.yaml degradation セクション）
- **確認項目:**
  - degradation.on_memory_pressure: compress_archive (shutdown ではない)
  - degradation.on_loop_risk_critical: force_observation (shutdown ではない)

### 1.6 human-first
- **定義:** Runtime は人間の判断を優先する。自律的な判断は、人間の意図と一致する場合のみ行う
- **現状:** ✅ 維持されている（runtime_personality_manifesto.md）
- **確認項目:**
  - continuation-conservative: 継続は慎重に行う
  - proposal-selective: 提案は必要な時のみ行う

### 1.7 stop-aware
- **定義:** 停止基準を常に意識する
- **現状:** ✅ 維持されている（runtime_personality_manifesto.md）
- **確認項目:**
  - observation_cooldown_ms: 500
  - loop_risk.max_recursion_depth: 3

## 2. Philosophy Freeze Confirmation

### 2.1 No New Principles
- 新manifesto作成禁止
- new layer追加禁止
- observer expansion禁止

### 2.2 Existing Principles Maintenance
- runtime_personality_manifesto.md の原則を維持
- ambient_runtime_manifesto.md の原則を維持
- runtime_config.yaml の安全デフォルトを維持

### 2.3 Drift Prevention
- proposal proliferation の防止（max_proposals_per_issue: 1）
- memory growth の防止（compression_trigger_ratio: 0.7）
- continuation pressure の防止（no_forced_continuation: true）

## 3. Philosophy Verification Checklist

| Principle | Status | Last Verified | Next Verification |
|-----------|--------|---------------|-------------------|
| calm runtime | ✅ | Project_18 Start | Monthly |
| invisible-by-default | ✅ | Project_18 Start | Monthly |
| low interruption | ✅ | Project_18 Start | Monthly |
| compression-first | ✅ | Project_18 Start | Monthly |
| cleanup-last | ✅ | Project_18 Start | Monthly |
| human-first | ✅ | Project_18 Start | Monthly |
| stop-aware | ✅ | Project_18 Start | Monthly |

## 4. Philosophy Change Policy

哲学の変更は、以下の条件を満たす場合のみ許可される：

1. **人間による明示的な指示** - Runtime が自律的に変更することは禁止
2. **重大な問題の解決** - runtime の安定性が脅かされている場合のみ
3. **最小限の変更** - 原則の一部のみを変更し、全体を再設計しない

---

*Project_18 - Long-Term Runtime Philosophy Freeze*
*"哲学は変えない。維持する。"*
