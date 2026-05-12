# Project_041 移行コンテキスト - 記憶継承版

## 現在のプロジェクト状態
- **最新コミット**: `59ea782 feat: Project_040 - 記憶の継承機能の実装`
- **Project_040**: 完了済み。
- **Project_041**: 完了済み。

## 直前の実装内容 (Project_040)
- **記憶ストレージの拡張**: `ProjectHistoryStore` を実装。プロジェクト履歴を構造化保存。
- **記憶の継承機能**: `SessionLogger` と `SessionRestorer` を実装。
    - セッション履歴の自動保存・復元。
    - 関連する過去のセッションを検索して復元。

## QueryQuest スペック (v0.4.0)
- **Memory OS**: 階層型メモリ管理 + HybridMemory検索。
- **ProjectHistoryStore**: プロジェクト履歴の構造化保存・検索。
- **Session Logger/Restorer**: セッション履歴の自動保存・復元。
- **Runtime Core**: 状態管理、タイムアウト管理。
- **Loop Detector**: ループ検知。

## 記憶システム構造
```
QueryQuest/
├── ai_agent/
│   └── memory/
│       ├── memory_os.py          # MemoryOS コア
│       ├── project_history.py    # ProjectHistoryStore
│       ├── session_logger.py     # SessionLogger
│       ├── session_restorer.py   # SessionRestorer
│       └── hybrid_memory.py      # HybridMemory (ベクトル+BM25)
├── memory/
│   ├── project_history/          # プロジェクト履歴JSON (28件)
│   └── sessions/                 # セッション履歴JSON
└── project_041_context.md        # このファイル（記憶継承用）
```

## 重要な設計決定
1. **階層型メモリ**: Working → Short-term → Long-term → Semantic
2. **自動統合**: 短期メモリが閾値に達したら長期メモリへ移動
3. **忘却ポリシー**: LRU, importance, time の3種類
4. **ハイブリッド検索**: ベクトル埋め込み + BM25

## 教訓 (Project_040)
- **記憶の継承は必須**: チャット間で記憶がリセットされる問題を解決するため、ファイルベースの記憶継承が必須。
- **セッション履歴の保存**: `memory/sessions/` にセッション履歴を保存し、次チャットで復元する仕組みが重要。
- **プロジェクト履歴の構造化**: `ProjectHistoryStore` でプロジェクトの決定事項、問題点、解決策、教訓を構造化保存。

## Project_041 の実装内容
- **過去振り返り機能**: `ProjectHistoryStore` に `get_recent()`, `get_lessons()`, `get_decisions()` メソッドを追加
- **長期記憶の強化**: `MemoryOS` に `consolidate_high_importance()` メソッドを追加
- **セッション履歴の復元**: `SessionRestorer` に `get_recent_sessions()` メソッドを追加

## 次チャットで自動的に読み込まれる内容
1. この `project_041_context.md` の内容
2. `memory/project_history/` のプロジェクト履歴
3. `memory/sessions/` のセッション履歴

## 記憶継承の仕組み
1. **`project_041_context.md`**: 記憶継承の中心ファイル。次チャットで自動的に読み込まれる。
2. **`memory/project_history/`**: プロジェクト履歴を保存。`ProjectHistoryStore` で検索可能。
3. **`memory/sessions/`**: セッション履歴を保存。`SessionRestorer` で復元可能。

## Project_042 のテーマ案
- **ユーザープロファイルの強化**: ユーザーの好みや行動パターンの学習
- **自動回復と予防**: ループ検知結果に基づく自動パラメータ調整
- **記憶の圧縮**: 長期記憶の自動圧縮と重要度管理
