"""
project_history.py - プロジェクト履歴ストレージ

Project_040: 記憶ストレージの拡張
各プロジェクトの決定事項、問題点、解決策を構造化して保存。
"""

import time
import json
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field, asdict
from pathlib import Path

from .memory_entry import MemoryEntry, MemoryLayer


@dataclass
class ProjectHistoryEntry:
    """
    プロジェクト履歴エントリ

    Attributes:
        project_id: プロジェクトID (例: project_040)
        title: プロジェクトタイトル
        summary: プロジェクトの要約
        content: ファイルの内容（検索用）
        decisions: 決定事項のリスト
        problems: 問題点のリスト
        solutions: 解決策のリスト
        lessons: 教訓のリスト
        status: プロジェクトの状態 (planning, in_progress, completed, archived)
        created_at: 作成時刻
        updated_at: 更新時刻
        tags: タグ
        metadata: 追加メタデータ
    """
    project_id: str
    title: str
    summary: str
    content: str = ""
    decisions: List[str] = field(default_factory=list)
    problems: List[str] = field(default_factory=list)
    solutions: List[str] = field(default_factory=list)
    lessons: List[str] = field(default_factory=list)
    status: str = "planning"
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict:
        """辞書へ変換"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict) -> "ProjectHistoryEntry":
        """辞書からエントリを作成"""
        return cls(
            project_id=data["project_id"],
            title=data["title"],
            summary=data["summary"],
            content=data.get("content", ""),
            decisions=data.get("decisions", []),
            problems=data.get("problems", []),
            solutions=data.get("solutions", []),
            lessons=data.get("lessons", []),
            status=data.get("status", "planning"),
            created_at=data.get("created_at", time.time()),
            updated_at=data.get("updated_at", time.time()),
            tags=data.get("tags", []),
            metadata=data.get("metadata", {}),
        )

    def update(self, **kwargs):
        """エントリを更新"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = time.time()


class ProjectHistoryStore:
    """
    プロジェクト履歴ストレージ

    各プロジェクトの履歴をファイルシステムに保存し、検索可能にする。
    """

    def __init__(self, storage_dir: str = "memory/project_history"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.entries: Dict[str, ProjectHistoryEntry] = {}
        self._load_all()

    def _load_all(self):
        """全エントリをロード"""
        if not self.storage_dir.exists():
            return

        for file_path in self.storage_dir.glob("*.json"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    entry = ProjectHistoryEntry.from_dict(data)
                    self.entries[entry.project_id] = entry
            except (json.JSONDecodeError, KeyError) as e:
                print(f"Failed to load {file_path}: {e}")

    def save(self, entry: ProjectHistoryEntry):
        """エントリを保存"""
        file_path = self.storage_dir / f"{entry.project_id}.json"
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(entry.to_dict(), f, ensure_ascii=False, indent=2)
        self.entries[entry.project_id] = entry

    def get(self, project_id: str) -> Optional[ProjectHistoryEntry]:
        """プロジェクト履歴を取得"""
        return self.entries.get(project_id)

    def search(self, query: str, k: int = 5) -> List[ProjectHistoryEntry]:
        """プロジェクト履歴を検索"""
        results = []
        query_lower = query.lower()

        for entry in self.entries.values():
            score = 0.0

            # タグの一致
            for tag in entry.tags:
                if query_lower in tag.lower():
                    score += 0.5

            # タイトルの一致
            if query_lower in entry.title.lower():
                score += 0.3

            # 要約の一致
            if query_lower in entry.summary.lower():
                score += 0.2
            
            # コンテンツの一致
            if query_lower in entry.content.lower():
                score += 0.1

            # 決定事項の一致
            for decision in entry.decisions:
                if query_lower in decision.lower():
                    score += 0.1

            if score > 0:
                results.append((score, entry))

        # スコア降順にソート
        results.sort(key=lambda x: x[0], reverse=True)
        return [entry for _, entry in results[:k]]

    def list_all(self) -> List[ProjectHistoryEntry]:
        """全プロジェクト履歴をリスト"""
        return list(self.entries.values())

    def get_recent(self, n: int = 10) -> List[ProjectHistoryEntry]:
        """最新のプロジェクト履歴を取得
        
        Args:
            n: 取得する件数
            
        Returns:
            最新のプロジェクト履歴（更新時刻降順）
        """
        entries = list(self.entries.values())
        entries.sort(key=lambda e: e.updated_at, reverse=True)
        return entries[:n]

    def get_lessons(self, k: int = 10) -> List[str]:
        """過去の教訓を抽出
        
        Args:
            k: 取得する教訓の数
            
        Returns:
            教訓のリスト
        """
        lessons = []
        for entry in self.entries.values():
            for lesson in entry.lessons:
                lessons.append(f"[{entry.project_id}] {lesson}")
        
        # 更新時刻降順にソート
        lessons.sort(reverse=True)
        return lessons[:k]

    def get_decisions(self, k: int = 10) -> List[str]:
        """過去の決定事項を抽出
        
        Args:
            k: 取得する決定事項の数
            
        Returns:
            決定事項のリスト
        """
        decisions = []
        for entry in self.entries.values():
            for decision in entry.decisions:
                decisions.append(f"[{entry.project_id}] {decision}")
        
        # 更新時刻降順にソート
        decisions.sort(reverse=True)
        return decisions[:k]

    def update_status(self, project_id: str, status: str):
        """プロジェクトの状態を更新"""
        entry = self.entries.get(project_id)
        if entry:
            entry.status = status
            self.save(entry)

    def add_lesson(self, project_id: str, lesson: str):
        """教訓を追加"""
        entry = self.entries.get(project_id)
        if entry:
            entry.lessons.append(lesson)
            entry.tags.append("lesson")
            self.save(entry)

    def add_decision(self, project_id: str, decision: str):
        """決定事項を追加"""
        entry = self.entries.get(project_id)
        if entry:
            entry.decisions.append(decision)
            self.save(entry)

    def add_problem(self, project_id: str, problem: str):
        """問題点を追加"""
        entry = self.entries.get(project_id)
        if entry:
            entry.problems.append(problem)
            self.save(entry)

    def add_solution(self, project_id: str, solution: str):
        """解決策を追加"""
        entry = self.entries.get(project_id)
        if entry:
            entry.solutions.append(solution)
            self.save(entry)
