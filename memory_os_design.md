# Memory OS 設計文書

## 概要
QueryQuest 用の統一メモリ管理システム。
階層型メモリ + 統一インターフェース + 自動スケジューリング

## メモリ階層

### 1. Working Memory（作業メモリ）
- **容量**: 最大 50 エントリ
- **寿命**: セッション中のみ
- **用途**: 現在の会話コンテキスト、即時処理情報
- **ストレージ**: インメモリ

### 2. Short-term Memory（短期メモリ）
- **容量**: 最大 500 エントリ
- **寿命**: 24時間
- **用途**: 直近の対話履歴、一時的なタスク情報
- **ストレージ**: SQLite

### 3. Long-term Memory（長期メモリ）
- **容量**: 無制限（圧縮対象）
- **寿命**: 恒久的
- **用途**: 学習済みの知識、ユーザープロファイル、重要な記憶
- **ストレージ**: SQLite + ChromaDB（ベクトル）

### 4. Semantic Memory（意味メモリ）
- **容量**: 無制限
- **寿命**: 恒久的
- **用途**: 概念間の関係、知識グラフ、推論ルール
- **ストレージ**: Neo4j / SQLite（グラフ）

## 統一インターフェース

```python
class MemoryOS:
    def store(self, memory: MemoryEntry) -> str
    def retrieve(self, query: str, k: int = 5) -> list[MemoryEntry]
    def update(self, id: str, data: dict) -> bool
    def delete(self, id: str) -> bool
    def consolidate(self) -> None  # 短期→長期の移動
    def forget(self, policy: str = "lru") -> int  # 忘却
```

## メモリエントリ形式

```python
@dataclass
class MemoryEntry:
    id: str
    content: str
    metadata: dict
    embedding: list[float]
    importance: float  # 0.0 - 1.0
    created_at: datetime
    accessed_at: datetime
    access_count: int
    layer: str  # working, short_term, long_term, semantic
    tags: list[str]
```

## スケジューリング

### 自動統合（Consolidation）
- 短期メモリが閾値に達したら長期メモリへ移動
- 重要度スコアが高いものから優先的に移動

### 忘却（Forgetting）
- LRU（Least Recently Used）
- 重要度ベース
- 時間ベース（古いエントリ）

### 圧縮（Compression）
- 類似エントリのマージ
- 要約生成（LLM使用）

## メタデータ標準

```json
{
    "source": "conversation|tool|user|system",
    "type": "fact|preference|event|rule|relationship",
    "confidence": 0.95,
    "related_ids": ["mem_001", "mem_002"],
    "user_id": "user_123"
}
```

## 実装フェーズ

### Phase 1: 基本構造
- MemoryOS コアクラス
- 統一インターフェース
- Working + Short-term メモリ

### Phase 2: 永続化
- SQLite スキーマ設計
- ChromaDB 統合
- 長期メモリ

### Phase 3: 高度な機能
- 意味メモリ（グラフ）
- 自動統合
- 忘却メカニズム

### Phase 4: 最適化
- 埋め込みバッチ処理
- インデックス最適化
- パフォーマンスチューニング
