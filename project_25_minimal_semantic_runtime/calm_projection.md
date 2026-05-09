# QueryQuest Project_25 - Calm Projection Design

## テーマ: 「静かな投影」の設計

---

## Core Principle

**Projectionは、必要時のみ生成される。**

- ephemeral（一時的）
- low-density（低密度）
- low-attention（低注意）
- non-persistent（非永続）

---

## Projection Characteristics

### 1. Ephemeral

Projectionは一度生成されると、再生成されない限り保持されない。
stateのsourceではないため、永続化の必要はない。

```
[Runtime State] → [Projection] → [View]
     ↓                    ↓
  persistent         ephemeral
```

### 2. Low-Density

Projectionは低密度で生成される。
大量の情報や詳細な表示は行わない。

```
Bad: 50項目のリスト + グラフ + テーブル
Good: 3項目の要約 + ステータスインジケーター
```

### 3. Low-Attention

Projectionは人間の注意を奪わない。
"Quiet Ambient Runtime"の哲学に準拠する。

- アニメーション禁止
- バッジ通知禁止
- 視覚的なノイズ排除
- 落ち着いた配色とレイアウト

### 4. Non-Persistent

Projectionは永続化されない。
再生成可能な情報であるため、保存の必要はない。

```
Bad: ProjectionをDBに保存
Good: Runtime Stateのみ保存、Projectionは都度生成
```

---

## Calm Projection Rules

| Rule | Description |
|------|-------------|
| No auto-projection | 自動投影禁止 |
| No persistent projection | 永続投影禁止 |
| No high-density output | 高密度出力禁止 |
| No attention-grabbing UI | 注意を引くUI禁止 |
| No animation | アニメーション禁止 |

---

## Projection Triggers

Projectionは以下のトリガーでのみ生成される：

1. **on_request** - ユーザーの明示的な要求時
2. **on_state_change** - Runtime stateの変更時（最小限）
3. **on_error** - エラー発生時の静かな報告

---

## Identity Alignment

**"Quiet Ambient Runtime"** のidentityを維持するため：

- Projectionは「空気のように存在し、必要時だけ現れる」
- 常時表示のProjection禁止
- 自動更新のProjection禁止
- 人間のフローを尊重した投影タイミング

---

*Project_25 - Calm Projection Design*
*"静かな投影"*
