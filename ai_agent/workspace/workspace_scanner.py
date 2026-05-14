# ai_agent/workspace/workspace_scanner.py

"""
ワークスペーススキャナー

プロジェクト内のドキュメントを走査し、
主要な設計思想やルールを抽出する。
"""

import os
import re
import json
from datetime import datetime
from typing import Optional


def scan_workspace(root_path: str = None) -> dict:
    """
    ワークスペースをスキャン
    
    Markdown ファイル、requirements.txt、README.md などを走査。
    
    Args:
        root_path: スキャン対象のルートパス
    
    Returns:
        スキャン結果 {
            "documents": list,
            "tech_stack": dict,
            "rules": list,
            "summary": str
        }
    """
    if root_path is None:
        # 現在のディレクトリをルートとする
        root_path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    result = {
        "documents": [],
        "tech_stack": {},
        "rules": [],
        "summary": "",
        "scanned_at": datetime.now().isoformat()
    }
    
    # ドキュメントを走査
    result["documents"] = _scan_documents(root_path)
    
    # テックスタックを抽出
    result["tech_stack"] = _extract_tech_stack(root_path)
    
    # ルールを抽出
    result["rules"] = _extract_rules(result["documents"])
    
    # サマリーを生成
    result["summary"] = _generate_summary(result)
    
    return result


def _scan_documents(root_path: str) -> list:
    """
    ドキュメントファイルを走査
    
    Args:
        root_path: ルートパス
    
    Returns:
        走査結果のリスト
    """
    documents = []
    
    # 対象拡張子
    target_extensions = ['.md', '.txt', '.rst']
    
    for dirpath, dirnames, filenames in os.walk(root_path):
        # 無視するディレクトリ
        skip_dirs = ['.git', 'venv', 'ai-env', '__pycache__', 'node_modules', 'archive']
        dirnames[:] = [d for d in dirnames if d not in skip_dirs]
        
        for filename in filenames:
            ext = os.path.splitext(filename)[1].lower()
            if ext in target_extensions:
                filepath = os.path.join(dirpath, filename)
                
                # ファイルサイズが大きい場合はスキップ（1MB 以上）
                if os.path.getsize(filepath) > 1024 * 1024:
                    continue
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 相対パスを取得
                    rel_path = os.path.relpath(filepath, root_path)
                    
                    documents.append({
                        "path": rel_path,
                        "filename": filename,
                        "size": os.path.getsize(filepath),
                        "content_preview": content[:500]  # プレビューのみ
                    })
                except Exception as e:
                    print(f"⚠️ ファイル読み込みエラー: {filepath} - {e}")
    
    return documents


def _extract_tech_stack(root_path: str) -> dict:
    """
    テックスタックを抽出
    
    requirements.txt や setup.py からライブラリとバージョンを抽出。
    
    Args:
        root_path: ルートパス
    
    Returns:
        テックスタック辞書
    """
    tech_stack = {
        "python_version": "3.12",
        "libraries": {},
        "tools": [],
        "frameworks": []
    }
    
    # requirements.txt を探す
    requirements_path = os.path.join(root_path, "requirements.txt")
    if os.path.exists(requirements_path):
        try:
            with open(requirements_path, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        # パッケージ名とバージョンを抽出
                        match = re.match(r'^([a-zA-Z0-9_-]+)==(.+)$', line)
                        if match:
                            tech_stack["libraries"][match.group(1)] = match.group(2)
                        else:
                            # バージョンなしの場合
                            match = re.match(r'^([a-zA-Z0-9_-]+)', line)
                            if match:
                                tech_stack["libraries"][match.group(1)] = "latest"
        except Exception as e:
            print(f"⚠️ requirements.txt 読み込みエラー: {e}")
    
    # Python バージョンを検出
    python_version_path = os.path.join(root_path, "Dockerfile")
    if os.path.exists(python_version_path):
        try:
            with open(python_version_path, 'r', encoding='utf-8') as f:
                content = f.read()
                version_match = re.search(r'python:(\d+\.\d+)', content)
                if version_match:
                    tech_stack["python_version"] = version_match.group(1)
        except Exception:
            pass
    
    return tech_stack


def _extract_rules(documents: list) -> list:
    """
    ドキュメントからルールを抽出
    
    Args:
        documents: 文書リスト
    
    Returns:
        ルールのリスト
    """
    rules = []
    
    for doc in documents:
        content = doc.get("content_preview", "")
        
        # ルールキーワードを検索
        rule_keywords = [
            "禁止", "注意", "重要", "ルール", "制約",
            "must", "should", "must not", "should not",
            "禁止", "必須", "推奨"
        ]
        
        for line in content.split('\n'):
            line = line.strip()
            if any(kw in line for kw in rule_keywords):
                if len(line) > 10 and len(line) < 200:
                    rules.append({
                        "source": doc["path"],
                        "rule": line
                    })
    
    # 重複除去
    unique_rules = []
    seen = set()
    for rule in rules:
        key = rule["rule"][:50]
        if key not in seen:
            unique_rules.append(rule)
            seen.add(key)
    
    return unique_rules[:20]  # 最大 20 件


def _generate_summary(result: dict) -> str:
    """
    スキャン結果のサマリーを生成
    
    Args:
        result: スキャン結果
    
    Returns:
        サマリーテキスト
    """
    summary_parts = []
    
    # ドキュメント数
    summary_parts.append(f"ドキュメント数：{len(result['documents'])}件")
    
    # テックスタック
    if result["tech_stack"].get("libraries"):
        libs = ", ".join(list(result["tech_stack"]["libraries"].keys())[:5])
        summary_parts.append(f"主要ライブラリ：{libs}")
    
    # ルール数
    summary_parts.append(f"抽出ルール：{len(result['rules'])}件")
    
    return " | ".join(summary_parts)


def scan_and_compress(root_path: str = None) -> str:
    """
    スキャン結果を圧縮して返す
    
    プロンプトに注入するための圧縮形式。
    
    Args:
        root_path: ルートパス
    
    Returns:
        圧縮されたテキスト
    """
    result = scan_workspace(root_path)
    
    compressed_parts = []
    
    # テックスタック
    if result["tech_stack"].get("libraries"):
        libs = "; ".join([f"{k}={v}" for k, v in result["tech_stack"]["libraries"].items()[:10]])
        compressed_parts.append(f"tech_stack: {libs}")
    
    # ルール
    if result["rules"]:
        rules = "; ".join([r["rule"][:50] for r in result["rules"][:5]])
        compressed_parts.append(f"rules: {rules}")
    
    # ドキュメント一覧
    if result["documents"]:
        docs = "; ".join([d["filename"] for d in result["documents"][:10]])
        compressed_parts.append(f"documents: {docs}")
    
    return "\n".join(compressed_parts)
