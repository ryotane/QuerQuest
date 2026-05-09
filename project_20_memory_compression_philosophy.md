# QueryQuest Project_20 - Memory Compression Philosophy

## テーマ: 「圧縮して保持、自然に減衰」

---

## Core Concept

**「全文保持しない。要点のみを圧縮して保持する」**

memory compression は以下の原則に従う：
- compress before store（保存前に圧縮）
- rolling summaries（ローリング要約）
- layered archive（階層化アーカイブ）
- low-token continuity（低トークン継続性）
- no recursive summarization（再帰的要約禁止）

---

## Compression Principles

### 1. compress before store
保存前に圧縮する。全文を保存してから要約するのではなく、最初から要点のみを記録する。

**Before (非推奨):**
```json
{
  "full_conversation": "長い会話の全文...",
  "summary": "要約"
}
```

**After (推奨):**
```json
{
  "summary": "Project_20設計開始。continuity depthの定義。",
  "themes": ["project_20", "design"],
  "sentiment": 0.7
}
```

### 2. rolling summaries
要約はローリングで更新する。古い情報を追加していくのではなく、最新の要点に更新する。

**Example:**
- Session 1: "Project_20設計開始"
- Session 2: "Project_20設計継続。レイヤー定義完了"
- Session 3: "Project_20設計完了。レポート作成中"

### 3. layered archive
アーカイブは階層化する。各レイヤーで保持内容と保持期間を区別する。

| Layer | Content | Duration |
|-------|---------|----------|
| immediate | セッション要約（3行） | 1 session |
| recent | テーマ単位要約 | 7日 |
| archive | 圧縮アーカイブ（1行） | 90日 |

### 4. low-token continuity
継続性は低トークンで表現する。詳細な説明ではなく、キーワードと状態のみで十分。

**Example:**
```json
{
  "theme": "project_20",
  "status": "design phase",
  "sentiment": 0.7
}
```

### 5. no recursive summarization
再帰的要約は禁止する。要約の要約を作らない。1段階の要約のみ保持する。

**Before (非推奨):**
```json
{
  "summary": "Project_20設計",
  "meta_summary": "プロジェクト設計フェーズ"
}
```

**After (推奨):**
```json
{
  "summary": "Project_20設計開始。continuity depthの定義。"
}
```

---

## Compression Ratios

| Content Type | Original Size | Compressed Size | Ratio |
|--------------|---------------|-----------------|-------|
| Session log (1時間) | ~5KB | ~200 bytes | 96% reduction |
| Decision record | ~500 bytes | ~80 bytes | 84% reduction |
| Theme tracking | ~300 bytes | ~50 bytes | 83% reduction |

**平均圧縮率: 85-96%**

---

## Compression Algorithm (Simple)

```python
def compress_session(session):
    # 1. キーワード抽出（テーマ）
    themes = extract_keywords(session.content, max=3)
    
    # 2. 要約生成（3行以内）
    summary = generate_summary(session.content, max_lines=3)
    
    # 3. 感情スコア計算
    sentiment = calculate_sentiment(session.content)
    
    return {
        "summary": summary,
        "themes": themes,
        "sentiment": sentiment
    }

def compress_theme(theme):
    # キーワード+状態のみ
    return {
        "theme": theme.name,
        "status": theme.status,
        "last_updated": theme.updated_at
    }
```

---

## Anti-Compression (禁止事項)

- ❌ 全文保存 + 要約（冗長）
- ❌ 再帰的要約（トークン増大）
- ❌ 詳細なメタデータ（memory pressure増加）
- ❌ 会話の逐語的記録（圧縮率0%）

---

## Memory Budget Revisited

| Layer | Max Entries | Compressed Size/Entry | Total Cost |
|-------|-------------|----------------------|------------|
| immediate | 1 | ~200 bytes | ~200 bytes |
| recent | 5 | ~150 bytes | ~750 bytes |
| ongoing | 3 | ~50 bytes | ~150 bytes |
| stable | 1 | ~500 bytes | ~500 bytes |
| archive | 20 | ~80 bytes | ~1.6 KB |

**合計: ~3.2 KB**（memory.db baseline 92KBの約3.5%）

---

*Project_20 - Memory Compression Philosophy*
*"圧縮して保持、自然に減衰"*
