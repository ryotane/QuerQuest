# QueryQuest Project_25 - Semantic Structure Boundaries

## テーマ: 「静かな継続」のための境界線

---

## Core Principle

**「semantic richness」ではなく、「quiet continuity」**

巨大なsemantic graphを作るのではなく、
最小限のstateで、後から自由に投影できる構造。

---

## Boundary 1: No Semantic Graph Expansion

### 禁止事項
- semantic graph の自動拡張
- relation の自己生成
- ontology の肥大化
- knowledge graph の構築

### 許可事項
- minimal state の保持（5フィールドのみ）
- event stream の記録（圧縮済み）
- theme の追跡（1つまで）

---

## Boundary 2: No Branch Persistence Overload

### 禁止事項
- branch の永続化（3つ以上）
- parallel context の保存
- fork history の保持
- merge tracking の複雑化

### 許可事項
- single flow の追跡
- linear continuation の記録
- simple merge のサポート（1回のみ）

---

## Boundary 3: No Uncertainty Over-save

### 禁止事項
- uncertainty の詳細保存
- confidence score の逐次記録
- hypothesis の複数保持
- speculation の永続化

### 許可事項
- last_action の記録
- runtime_mode の追跡
- interruption の記録（1回のみ）

---

## Boundary 4: No Replay System

### 禁止事項
- full replay の実装
- session history の逐次再生
- event stream の逆再生
- time travel のサポート

### 許可事項
- last_action の参照
- recent_flow のスキャン（3件まで）
- simple resume のサポート

---

## Quiet Continuity Model

```
[Runtime State] ← [Event Stream]
     ↓                  ↓
  minimal            compressed
  (5 fields)         (6 types)
     ↓                  ↓
  Projection Layer   Projection Layer
     ↓                  ↓
  HTML/MD/SVG        HTML/MD/SVG
```

**重要**: Runtimeは投影しない。Projection Layerが投影する。

---

*Project_25 - Semantic Structure Boundaries*
*"静かな継続のための境界線"*
