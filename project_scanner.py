import os
from pathlib import Path

# =========================
# 設定（ここが重要）
# =========================
ROOT_DIR = "/Volumes/Data SSD/Docker/local_ai_project/QueryQuest"

EXCLUDE_DIRS = [".venv", "__pycache__", ".git"]
TARGET_EXT = [".py", ".json", ".md"]

MAX_FILE_SIZE = 2000


# =========================
# ツリー構造
# =========================
def get_tree_structure(root):
    tree = []

    for path, dirs, files in os.walk(root):
        # 除外ディレクトリ
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]

        level = path.replace(root, "").count(os.sep)
        indent = "  " * level
        tree.append(f"{indent}{os.path.basename(path)}/")

        subindent = "  " * (level + 1)
        for f in files:
            tree.append(f"{subindent}{f}")

    return "\n".join(tree)


# =========================
# ファイル読み込み
# =========================
def read_files(root):
    file_data = []

    for path in Path(root).rglob("*"):
        if path.is_file():

            # 除外
            if any(ex in str(path) for ex in EXCLUDE_DIRS):
                continue

            if path.suffix not in TARGET_EXT:
                continue

            try:
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read(MAX_FILE_SIZE)

                file_data.append({
                    "path": str(path),
                    "content": content
                })

            except Exception:
                continue

    return file_data


# =========================
# AI用まとめ
# =========================
def build_summary(tree, files):
    summary = "=== PROJECT STRUCTURE ===\n"
    summary += tree
    summary += "\n\n=== FILE CONTENTS ===\n"

    for f in files:
        summary += f"\n--- {f['path']} ---\n"
        summary += f["content"]
        summary += "\n"

    return summary


# =========================
# 実行
# =========================
if __name__ == "__main__":
    print("🔍 scanning real project...")

    tree = get_tree_structure(ROOT_DIR)
    files = read_files(ROOT_DIR)

    summary = build_summary(tree, files)

    output_path = os.path.join(ROOT_DIR, "project_summary.txt")

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(summary)

    print(f"✅ 出力完了: {output_path}")