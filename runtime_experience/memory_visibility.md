# QueryQuest Memory Visibility Design

## 「記憶は見えすぎていない」

---

## 1. Memory Visibility の基本方針

### 原則: Memory Transparency（記憶の透明性）

- memory は全部見せない
- 必要時のみ可視化
- summary を押し付けない
- archive を静かに扱う
- context を肥大表示しない

**体験目標**: 記憶が自然に存在している感覚

---

## 2. Memory Visibility Levels（記憶の可視性レベル）

### どの程度見せるか

| Level | Behavior | Use Case |
|-------|----------|----------|
| invisible | 記憶を提示しない | idle, human focus |
| minimal | 1行の要約のみ | quiet completion |
| moderate | 必要最小限の文脈提示 | continuation restore |
| full | 詳細な文脈提示 | 人間の要求時 |

**体験目標**: 記憶が自然に存在している感覚

---

## 3. Memory Suppression（記憶の抑制）

### 見せない記憶

| Memory Type | Visibility | Reason |
|-------------|------------|--------|
| archive memory | invisible | 必要時のみ検索 |
| old session history | minimal | 1行要約のみ |
| repeated context | suppressed | 冗長な提示を防止 |
| failed attempts | hidden | 失敗の記憶は押し付けない |

**体験目標**: 記憶が負担にならない軽さ

---

## 4. Memory Activation（記憶の活性化）

### 見せる記憶

| Trigger | Behavior |
|---------|----------|
| 人間の明示的な要求 | full visibility |
| continuation restore | minimal context |
| 問題解決時の文脈 | moderate提示 |
| 関連性の高い記憶のみ | selective activation |

**体験目標**: 必要な時にだけ現れる自然さ

---

## 5. Summary Policy（要約方針）

### どの程度押し付けないか

| Aspect | Boundary |
|--------|----------|
| タスク完了要約 | 1行のみ |
| session 要約 | 必要時のみ |
| memory 統合要約 | 人間の要求時 |
| 冗長な説明 | 禁止 |

**体験目標**: 要約が負担にならない軽さ

---

## 6. Archive Handling（アーカイブの扱い）

### 静かに扱う

| Aspect | Boundary |
|--------|----------|
| archive 検索 | 人間の要求時のみ |
| archive 提示 | minimal（1行のみ） |
| archive 自動表示 | 禁止 |
| archive 圧縮 | 優先 |

**体験目標**: アーカイブが静かに存在している感覚

---

## 7. Context Management（コンテキスト管理）

### 肥大表示しない

| Aspect | Boundary |
|--------|----------|
| context 長さ制限 | 1行以内 |
| 冗長な文脈提示 | 禁止 |
| 重複する情報 | 統合して1つに |
| 不要な詳細 | 抑制 |

**体験目標**: コンテキストが軽やかな感覚

---

## 8. Memory Visibility Scenarios（シナリオ別設計）

### シナリオ1: タスク完了時

```
[タスク完了]
→ 最小限の要約（1行）
→ 直ちに停止
→ 記憶はメモリ内のみ保持
```

### シナリオ2: continuation restore 時

```
[再開指示]
→ 必要最小限の文脈提示（1行）
→ archive は検索時のみ表示
→ 人間のペースに合わせる
```

### シナリオ3: memory search 時

```
[検索要求]
→ 関連性の高い記憶のみ提示
→ 冗長な履歴は抑制
→ 人間の要求に応じた詳細さで
```

---

## 9. Memory Visibility Prohibited Behaviors（禁止行為）

以下の動作は厳禁：

| 禁止行為 | 理由 |
|---------|------|
| memory の過剰提示 | 認知負荷を増やす |
| archive の自動表示 | フローを中断する |
| 冗長な要約 | 人間の集中を壊す |
| 失敗の記憶の押し付け | 不安を与える |

---

## Keywords

- Memory Transparency
- Selective Visibility
- Quiet Archive
- Minimal Context
- Fatigue Prevention

---

*このドキュメントは QueryQuest Runtime の記憶可視性を定義する。*
*全てのUX判断は、この Design を基準として行う。*
