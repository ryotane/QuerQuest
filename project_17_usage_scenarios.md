# QueryQuest Project_17 - Real-Life Usage Scenarios

## 基本方針
- Runtime は生活の主役ではない
- 静かに存在し、必要に応じて応答する
- 過剰な関与は禁止

---

## シナリオ定義

| Scenario | Goal | Frequency |
|----------|------|-----------|
| iPhoneから確認 | calm remote presence | 1-2回/日 |
| 長時間放置 | idle calmness | 常時 |
| restart後再開 | recovery reassurance | 必要時 |
| continuation利用 | soft continuity | 作業中 |
| 朝の起動 | gentle wake-up | 1回/日 |
| 作業中の存在 | quiet companion | 作業中 |
| 夜の終了 | calm shutdown | 1回/日 |

---

## シナリオ詳細

### 1. iPhoneから確認 (calm remote presence)
- **目的**: Runtime の状態を静かに確認する
- **期待動作**: 
  - 最小限のステータス表示（稼働中/停止）
  - 通知はバッチ配信（1日5回まで）
  - chat app ではない
- **禁止**: リアルタイム同期、頻繁な通知

### 2. 長時間放置 (idle calmness)
- **目的**: 存在を維持しつつリソース消費を抑える
- **期待動作**: 
  - バックグラウンドインフラのみ稼働
  - メモリ圧縮（70%でトリガー）
  - 強制想起禁止
- **禁止**: 不要なプロセス、メモリ洪水

### 3. restart後再開 (recovery reassurance)
- **目的**: 停止からの静かな復帰
- **期待動作**: 
  - invisible_hydration（目に見えない状態復元）
  - サイレントリカバリ
  - 強制継続禁止
- **禁止**: 冗長なログ、強制的な再開

### 4. continuation利用 (soft continuity)
- **目的**: 中断からの自然な再開
- **期待動作**: 
  - natural_resume_enabled（自然な再開有効）
  - 中断の許容
  - 強制継続禁止
- **禁止**: 強制再開、コンテキストの押し付け

### 5. 朝の起動 (gentle wake-up)
- **目的**: 一日の始まりを静かに開始する
- **期待動作**: 
  - 最小限のステータス確認
  - 前日の状態の静かな復元
  - 過剰なサマリー禁止
- **禁止**: 冗長な朝礼、強制通知

### 6. 作業中の存在 (quiet companion)
- **目的**: 邪魔しないが、必要な時に存在する
- **期待動作**: 
  - focus_mode_detection（集中状態検出）
  - repeated_interruption_suppression（繰り返し中断抑制）
  - passive_waiting_behavior（受動的待機動作）
- **禁止**: 頻繁な提案、強制介入

### 7. 夜の終了 (calm shutdown)
- **目的**: 一日の終わりを静かに迎える
- **期待動作**: 
  - バックグラウンドインフラの最小化
  - メモリの静かなアーカイブ
  - 強制シャットダウン禁止
- **禁止**: 冗長なログ、強制保存
