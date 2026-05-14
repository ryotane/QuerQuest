# Project_037 - iPhone Companion UI (Swift/SwiftUI)

## 概要

Project_036 で実装した Python Companion Core と連携する、
Swift/SwiftUI による iPhone Companion UI です。

### 基本方針
- chat app **ではない**
- 「静かな remote runtime window」である
- 生活の邪魔をしない存在

## プロジェクト構造

```
iPhoneCompanion/
├── App/
│   └── iPhoneCompanionApp.swift    # アプリのエントリポイント
├── Views/
│   ├── ContentView.swift           # メインビュー
│   ├── StatusView.swift            # 状態表示ビュー
│   └── DetailView.swift            # 詳細表示ビュー
├── Models/
│   └── CompanionStatus.swift       # ステータスモデル
├── Services/
│   └── CompanionClient.swift       # HTTP クライアント
└── Utils/
    └── (今後追加)
```

## 主な機能

### 1. Status View
- 状態アイコン（●○✓!⏱）
- 1 行ステータス表示
- 状態に応じた色とアニメーション

### 2. Minimal UI
- メイン表示（状態のみ）
- 詳細表示（オプション）
- 必要時のみ表示

### 3. Companion Core 連携
- HTTP API 経由で Python Companion Core と連携
- 自動更新（30 秒ごと）
- エラーハンドリング

## 設定

### API エンドポイント
- デフォルト：`http://localhost:8000`
- `CompanionClient` の `baseURL` で変更可能

### 更新間隔
- デフォルト：30 秒
- `startAutoRefresh()` の `Timer.scheduledTimer` で変更可能

## 開発手順

1. Xcode でプロジェクトを開く
2. Python Companion Core を起動
3. シミュレータまたは実機でテスト

## 関連プロジェクト

- [Project_036](../project_036_report.md) - iPhone Companion Python 実装
- [Project_036 設計書](../project_036_companion_design.md) - 詳細設計書

## ライセンス

QueryQuest Project_037 - MIT License
