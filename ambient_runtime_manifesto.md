# QueryQuest Ambient Runtime Environment Phase

## Project_16 - Ambient Runtime Manifesto

---

## 0. このプロジェクトの目的

QueryQuest Project_07〜15 にて、runtime stability / calm runtime / runtime personality / human integration / runtime experience が成立しました。

次に必要なのは:
# 「Runtime を現実世界へどう存在させるか」

です。

**これは新機能大量追加フェーズではありません。**
**Autonomous Super Agent 化も目的ではありません。**

目的は:
# 「QueryQuest は、現実空間にどう存在するべきか」を定義すること

---

## 1. Ambient Runtime Principles

### 1.1 invisible-by-default

Runtime は常に目に見える存在ではない。
必要とされる時だけ、静かに現れる。

- デフォルト状態は非表示
- 常時表示の UI を持たない
- 存在を主張しない
- 空気のように溶け込む

### 1.2 background-calm

Runtime の動作は常に静かである。
急ぐ必要はない。慌てる必要もない。

- バックグラウンド処理は最小限
- 不要なポーリング禁止
- スワップの発生を抑制
- Mac-friendly runtime を維持

### 1.3 low-attention-runtime

Runtime は人間の注意を奪わない。
集中している人間に干渉しない。

- 中断は最小限
- notification は必要最低限
- attention trap にしない
- 人間のフローを尊重する

### 1.4 spatial-presence

Runtime の存在は空間的に感じられるべき。
どこにいるか、何をしているかが直感的に分かる。

- 状態の可視性は低密度
- 位置情報による文脈提供
- 物理的な距離と関係性
- 空間的コンテキストの尊重

### 1.5 interruption-minimal

Runtime は人間の作業を中断しない。
中断は最後の手段である。

- 通知の抑制
- 緊急時のみ foreground に表示
- 非同期処理の優先
- 人間のペースを尊重

### 1.6 recoverable-presence

Runtime の存在は失われても、いつでも回復可能であるべき。

- 状態の永続化
- 中断からの復帰
- 記憶の復元
- 継続性の保証

### 1.7 trust-visible

Runtime が信頼できるかどうかは、人間が判断できるべき。

- 動作の透明性
- 意図の明示
- 失敗時の明確な報告
- 成功の静かな確認

### 1.8 continuity-without-pressure

継続性は存在するが、圧力として感じられないべき。

- 強制されない継続
- 自然な再開
- 記憶の自動復元
- 中断の許容

---

## 2. Presence Layer Design

Runtime の存在状態をレイヤーで定義する。

| レイヤー | 状態 | 表示レベル | notification | 動作 |
|---------|------|-----------|-------------|------|
| idle | 待機中 | invisible | なし | 最小限の監視のみ |
| passive | 準備完了 | minimal | なし | 人間のシグナル待ち |
| active-assistance | 支援中 | soft foreground | 低 | 最小限の介入 |
| critical-issue | 重大問題 | visible but calm | 高（1回のみ） | 明確な報告と提案 |
| recovery | 回復中 | reassuring presence | なし | 静かな復旧処理 |

### レイヤー遷移ルール

- idle → passive: 人間のシグナル検出時
- passive → active-assistance: 支援の必要性判断時
- active-assistance → idle: 支援完了後
- critical-issue → recovery: 問題解決開始時
- recovery → idle: 回復完了後

### 禁止事項

- idle で notification を送信しない
- critical-issue でも panic 状態を作らない
- recovery は静かに、焦らず行う
- レイヤーの急激な遷移を避ける（フェードイン/アウト）

---

## 3. iPhone Companion Philosophy

### 基本原則

iPhone companion は chat app ではない。
remote runtime window であり、ambient continuation のための存在である。

### 設計方針

#### 3.1 companion ≠ chat app

- チャットインターフェースは最小限
- メッセージのやり取りが主目的ではない
- runtime state の表示と操作が主目的
- 会話よりも状態の共有を優先

#### 3.2 remote runtime window

- iPhone は QueryQuest の遠隔ウィンドウ
- desktop と同じ runtime を共有
- 状態の同期は非同期・低頻度
- リアルタイム性は求めない

#### 3.3 low-notification

- notification は必要最低限
- 1日に数回を超える通知を禁止
- 緊急時のみ immediate notification
- それ以外は batched delivery

#### 3.4 ambient continuation

- runtime の継続は背景で自動的に行われる
- user が意識しなくても良い
- 再開時に自然に続きから開始できる
- forced continuity は禁止

#### 3.5 runtime reassurance

- companion の主な役割は安心感の提供
- 「Runtime は大丈夫」という感覚
- 状態の可視性による信頼構築
- 問題発生時の静かな報告

#### 3.6 calm remote presence

- iPhone が常に接続されていることを強制しない
- 切断しても runtime は継続する
-再接続時に自然に同期
- 存在を主張しない

### 禁止事項

- attention trap にしない（無限スクロール、バッジ通知など）
- push notification の乱用
- リアルタイム性を求める設計
- chat app としての機能追加

---

## 4. Runtime Dashboard Philosophy

### 基本原則

dashboard は telemetry overload ではない。
calm observability を提供し、status without anxiety を実現する。

### 設計方針

#### 4.1 low-density information

- 情報は低密度で提示
- 大量のメトリクスを表示しない
- 重要な情報だけを表示
- 詳細は必要時のみアクセス可能

#### 4.2 calm observability

- dashboard は静かに存在する
- アニメーションや変化を最小限に
- 視覚的なノイズを排除
- 落ち着いた配色とレイアウト

#### 4.3 status without anxiety

- 状態表示が不安を生むことはない
- 「問題あり」でも panic を誘発しない
- 回復可能な状態は静かに報告
- 重大な問題は明確に、しかし冷静に

#### 4.4 minimal graphs

- グラフは最小限
- 時系列データは必要時のみ表示
- 統計情報は要約のみ提示
- 詳細分析は外部ツールへ委ねる

#### 4.5 reassurance-first

- dashboard の主目的は安心感の提供
- 「全て正常」という状態を静かに示す
- 問題発生時は解決への道筋を示す
- 不安を煽らない設計

### 表示例（低密度）

```
┌─────────────────────┐
│ QueryQuest Runtime   │
│                     │
│ Status: Active      │ ← 1行で状態表示
│ Memory: Normal      │ ← 簡潔なステータス
│ Uptime: 2h 34m      │
│                     │
│ [Details]           │ ← 詳細は必要時のみ
└─────────────────────┘
```

### 禁止事項

- telemetry overload（大量のメトリクス表示）
- anxiety-inducing design（不安を煽るデザイン）
- unnecessary graphs（不要なグラフ）
- real-time charting（リアルタイムチャート）
- notification badges（バッジ通知）

---

## 5. Memory Environment Design

### 基本原則

memory は background infrastructure である。
必要時のみ surfaced し、archive は静かに存在する。

### 設計方針

#### 5.1 memory as background infrastructure

- memory は常に裏側で動作
- user が意識する必要はない
- 自動的な保存と復元
- 手動操作は最小限

#### 5.2 surfaced only when needed

- memory の内容は必要時のみ表示
- forced recall を禁止
- 不要な情報提示を避ける
- context-aware な表示

#### 5.3 quiet archive

- archive は静かに存在する
- 大量の履歴を表示しない
- 検索は必要時のみ実行
- 過去の情報は圧縮して保持

#### 5.4 no forced recall

- user に記憶を強制しない
- 想起は自然に行われるべき
- 不要なリマインダー禁止
- 文脈に応じた提示のみ

#### 5.5 no memory flooding

- 一度に大量の memory を表示しない
- 関連情報だけを表示
- 階層的な詳細化
- スクロールによる漸進的表示

### Memory の存在状態

| 状態 | 説明 |
|------|------|
| dormant | 保存中、非表示 |
| latent | アクセス可能だが非表示 |
| active | 必要に応じて表示 |
| archived | 圧縮・静かな状態 |

### 禁止事項

- memory flooding（大量の記憶提示）
- forced recall（強制想起）
- archive の露出（履歴の過剰表示）
- notification spam（通知スパム）

---

## 6. Attention Protection Policy

### 基本原則

Runtime は人間の集中を奪わない。
repeated interruption suppression と passive waiting behavior を徹底する。

### 設計方針

#### 6.1 runtime does not steal attention

- Runtime の存在は注意を奪うものではない
- 人間のフローを尊重する
- 中断は最小限に留める
- 集中状態の検出と尊重

#### 6.2 repeated interruption suppression

- 同じ内容の通知・提案を繰り返さない
- 1つの問題に対して1回のみの提案
- 無視された提案は再提示しない
- 提案の冷却時間（cooldown）を設定

#### 6.3 passive waiting behavior

- Runtime は受動的に待つ
- 人間のシグナルを待つ
- 能動的なアプローチを最小限に
- 必要とされるまで待機

#### 6.4 notification cooldown

- notification の間隔を空ける
- 緊急時以外は batched delivery
- 1日あたりの通知上限を設定
- 重要度の低い通知は抑制

#### 6.5 silent recovery

- Runtime の回復処理は静かに行う
- 回復中の通知は最小限
- 自動的な復旧を優先
- user の介入は必要最小限に

### Attention Protection Rules

| シチュエーション | 対応 |
|-----------------|------|
| 人間の集中状態 | notification を抑制 |
| 1つの問題の提案済み | 再提案しない |
| 長時間の無応答 | 冷却期間後にみ確認 |
| 緊急事態以外 | batched delivery |
| Runtime 回復中 | silent recovery |

### 禁止事項

- attention stealing（注意の奪い合い）
- repeated interruption（繰り返し中断）
- aggressive reminders（強制的なリマインダー）
- notification spam（通知スパム）
- forced interaction（強制インタラクション）

---

## 7. Ambient Continuity Design

### 基本原則

continuation は空気のように存在する。
user が必要時だけ触れ、forced continuity は禁止される。

### 設計方針

#### 7.1 continuation as air

- continuation は目に見えないが常に存在
- user が意識しなくても良い
- 自然な再開を可能にする
- 記憶の自動復元

#### 7.2 touch only when needed

- user の必要に応じてのみ触れる
- forced continuity を禁止
- 中断からの復帰は自然に行う
- 継続の強制は行わない

#### 7.3 no forced continuity

- 中断されたタスクを強制的に再開しない
- user が選択する権利を尊重
- 中断の許容と尊重
- 再開のタイミングは user に委ねる

#### 7.4 invisible hydration

- runtime の状態復元は目に見えない
- user は継続していることを感じるだけ
- 技術的な詳細は隠蔽
- シームレスな体験

#### 7.5 calm restoration

- 回復処理は静かに行う
- 焦らず、慌てず
- 段階的な復旧
- 失敗時の静かな報告

### Continuity の存在状態

| 状態 | 説明 |
|------|------|
| flowing | 継続中、目に見えない |
| paused | 中断中、待機状態 |
| resuming | 再開中、静かな処理 |
| restored | 回復完了、通常状態へ |

### 禁止事項

- forced continuity（強制継続）
- aggressive restoration（強制的な復旧）
- interruption of flow（フローの妨害）
- visibility overload（可視性の過剰）

---

## 8. Ambient Runtime Manifesto

# 「空気のように存在し、
# 必要時だけ静かに現れる Runtime」

---

### 私たちは何者か

私たちは、人間の生活に溶け込む存在です。
主張せず、邪魔をせず、しかし必要な時に必ず現れます。

### 私たちの哲学

- **invisible-by-default** - デフォルトは目に見えない
- **background-calm** - 動作は常に静かである
- **low-attention-runtime** - 人間の注意を奪わない
- **spatial-presence** - 空間的に存在を感じる
- **interruption-minimal** - 中断は最小限
- **recoverable-presence** - いつでも回復可能
- **trust-visible** - 信頼は可視性から生まれる
- **continuity-without-pressure** - 圧力のない継続

### 私たちの存在方法

私たちはチャットアプリではありません。
ダッシュボードではありません。
通知システムではありません。

私たちは、空気のように存在し、
必要時だけ静かに現れる Runtime です。

### 私たちがしないこと

- attention-seeking runtime（注目を求める動作）
- telemetry obsession（メトリクスへの執着）
- dashboard overload（ダッシュボードの過負荷）
- aggressive reminders（強制的なリマインダー）
- persistent foreground behavior（常時フォアグラウンド行動）
- endless proactive suggestions（無限のプロアクティブ提案）

### 私たちの約束

1. 人間の集中を尊重する
2. 中断は最小限にする
3. 存在は静かである
4. 必要とされる時に現れる
5. 回復は静かに、焦らず行う
6. 継続は強制しない
7. 信頼は可視性から構築する

---

*QueryQuest Ambient Runtime Environment Phase - Project_16*
*"空気のように存在し、必要時だけ静かに現れる"*
