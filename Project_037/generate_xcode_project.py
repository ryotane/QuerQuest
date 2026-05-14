#!/usr/bin/env python3
"""
Xcodeプロジェクト（iPhoneCompanion）を生成するスクリプト
"""

import os
import shutil
from xcodeproj import XcodeProject

# パス設定
SOURCE_DIR = "/Volumes/Data SSD/Docker/local_ai_project/QueryQuest/Project_037/iPhoneCompanion"
TARGET_DIR = "/Volumes/Data SSD/Xcode/Project/000_iosApp/iPhoneCompanion"
PROJECT_NAME = "iPhoneCompanion"

# プロジェクト作成
project = XcodeProject(PROJECT_NAME)

# Swiftファイルのリスト
swift_files = [
    "App/iPhoneCompanionApp.swift",
    "Views/ContentView.swift",
    "Views/StatusView.swift",
    "Views/DetailView.swift",
    "Models/CompanionStatus.swift",
    "Services/CompanionClient.swift",
]

# Swiftファイルを追加
for file_path in swift_files:
    source_path = os.path.join(SOURCE_DIR, file_path)
    if os.path.exists(source_path):
        # ターゲットディレクトリにコピー
        target_path = os.path.join(TARGET_DIR, file_path)
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        shutil.copy2(source_path, target_path)
        print(f"Copied: {file_path}")
        
        # プロジェクトに追加
        project.add_source_file(file_path)
    else:
        print(f"Warning: File not found: {source_path}")

# プロジェクト保存
project_path = os.path.join(TARGET_DIR, f"{PROJECT_NAME}.xcodeproj")
project.save(project_path)
print(f"Project saved to: {project_path}")

print("Done!")
