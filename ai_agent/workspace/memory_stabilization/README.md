# Memory Stabilization Module

## 概要

recursive context amplification を防止する統合モジュール。

## 問題

Project_02 で発生した症状:
- Previous Session Context の自己増殖
- 同一 summary の再注入
- project_master 重複
- token explosion
- context usage 100% 超過

## 原因

1. injected context が再度 session summary に保存される
2. session → project_master → session の循環参照
3. 文字数制限の欠如
4. summary の増殖（merge_sessions で結合され圧縮されない）

## 解決策

### 1. Injected Context Exclusion
- context のハッシュ値を追跡
- 同一ハッシュの再保存をブロック

### 2. Recursive Injection Detection
- context chain を追跡
- 同一 context の繰り返しを検出

### 3. Context Deduplication
- content のハッシュ値で重複検出
- 類似 content のマージ

### 4. Token Budget Hard Limit
- summary: 500 文字
- topics: 200 文字
- goals: 300 文字
- context: 1500 文字

### 5. Summary Compression
- 段落ごとに切り捨て
- 意味を保持

### 6. Active/Archive Memory Separation
- 7日経過で自動アーカイブ
- active sessions のみ injection 対象

## 使用例

```python
from ai_agent.workspace.memory_stabilization import MemoryStabilizer

stabilizer = MemoryStabilizer()

# セッションコンテキスト生成時
context = stabilizer.build_safe_context(registry, limit=3)

# セッション保存時
session_data = stabilizer.validate_session_data(session_data)

# 循環参照検出
if stabilizer.detect_recursion(context):
    # 循環参照あり → 対策
    pass
```

## モジュール構成

```
memory_stabilization/
├── __init__.py
├── stabilizer.py          # 統合クラス
├── injection_guard.py     # injected context 追跡
├── context_deduplicator.py # 重複排除
├── summary_compressor.py  # 要約圧縮
└── memory_separation.py   # active/archive 分離
```

## 統合箇所

- `session_context.py`: build_session_context() が安定化モジュールを使用
- `session_auto_save.py`: セッション保存時に安定化ルールを適用
- `session_registry.py`: merge_sessions() で安定化ルールを適用
