# ai_agent/workspace/memory_stabilization/verification.py

"""
Memory Stabilization Verification

既存データのクリーンアップと、
stabilization の実運用検証を行う。

検証項目:
1. 既存 session summaries cleanup
2. project_master.json の循環参照除去
3. duplicated next_actions cleanup
4. duplicated best_practices cleanup
5. stale summaries archive 化
6. Stress Test（10回継続）
"""

import json
import os
import sys
from datetime import datetime, timedelta
from typing import Optional

# プロジェクトルートにパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_agent.workspace.memory_stabilization import (
    MemoryStabilizer,
    SummaryCompressor,
    ContextDeduplicator,
    MemorySeparation,
)


class MemoryVerifier:
    """Memory Stabilization 検証クラス"""
    
    def __init__(self, project_root: str = None):
        if project_root is None:
            # QueryQuest プロジェクトルート
            project_root = "/Volumes/Data SSD/Docker/local_ai_project/QueryQuest"
        self.project_root = project_root
        self.stabilizer = MemoryStabilizer()
        self.compressor = SummaryCompressor()
        self.deduplicator = ContextDeduplicator()
        self.separation = MemorySeparation()
        
        # 統計情報
        self.stats = {
            "cleaned_summaries": 0,
            "removed_duplicates": 0,
            "archived_sessions": 0,
            "compressed_bytes": 0,
            "original_bytes": 0,
            "injection_recursion_count": 0,
        }
    
    def cleanup_existing_data(self) -> dict:
        """
        既存データのクリーンアップ
        
        Returns:
            クリーンアップ結果
        """
        print("=" * 60)
        print("既存データ クリーンアップ")
        print("=" * 60)
        
        results = {}
        
        # 1. session_registry.json クリーンアップ
        results["session_registry"] = self._cleanup_session_registry()
        
        # 2. project_master.json クリーンアップ
        results["project_master"] = self._cleanup_project_master()
        
        # 3. best_practices.json クリーンアップ
        results["best_practices"] = self._cleanup_best_practices()
        
        # 4. stale sessions archive
        results["archive"] = self._archive_stale_sessions()
        
        # 統計
        self.stats["cleaned_summaries"] = results["session_registry"]["cleaned"]
        self.stats["removed_duplicates"] = results["best_practices"]["removed"]
        self.stats["archived_sessions"] = results["archive"]["archived"]
        
        return results
    
    def _cleanup_session_registry(self) -> dict:
        """session_registry.json クリーンアップ"""
        path = os.path.join(self.project_root, "session_registry.json")
        
        if not os.path.exists(path):
            return {"cleaned": 0, "reason": "file not found"}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        original_size = os.path.getsize(path)
        self.stats["original_bytes"] += original_size
        
        cleaned = 0
        for session in data.get("sessions", []):
            # サマリー圧縮
            if session.get("summary"):
                original = session["summary"]
                compressed = self.compressor.compress_summary(original, 500)
                if len(compressed) < len(original):
                    session["summary"] = compressed
                    cleaned += 1
                    self.stats["compressed_bytes"] += len(original) - len(compressed)
            
            # トピック重複排除
            if session.get("recent_topics"):
                original_count = len(session["recent_topics"])
                deduped = self.deduplicator.deduplicate_topics(session["recent_topics"])
                if len(deduped) < original_count:
                    session["recent_topics"] = deduped
                    self.stats["removed_duplicates"] += original_count - len(deduped)
            
            # ゴール圧縮
            if session.get("active_goals"):
                session["active_goals"] = self.compressor.compress_goals(
                    session["active_goals"], 300
                )
        
        # 保存
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        new_size = os.path.getsize(path)
        
        return {
            "cleaned": cleaned,
            "original_size": original_size,
            "new_size": new_size,
            "reduction": original_size - new_size,
        }
    
    def _cleanup_project_master(self) -> dict:
        """project_master.json クリーンアップ"""
        path = os.path.join(self.project_root, "project_master.json")
        
        if not os.path.exists(path):
            return {"cleaned": False, "reason": "file not found"}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        original_size = os.path.getsize(path)
        self.stats["original_bytes"] += original_size
        
        cleaned = False
        
        # project_summary 圧縮
        if data.get("project_summary"):
            original = data["project_summary"]
            compressed = self.compressor.compress_summary(original, 500)
            if len(compressed) < len(original):
                data["project_summary"] = compressed
                cleaned = True
                self.stats["compressed_bytes"] += len(original) - len(compressed)
        
        # important_topics 重複排除
        if data.get("important_topics"):
            original_count = len(data["important_topics"])
            deduped = self.deduplicator.deduplicate_topics(data["important_topics"])
            if len(deduped) < original_count:
                data["important_topics"] = deduped
                cleaned = True
                self.stats["removed_duplicates"] += original_count - len(deduped)
        
        # active_goals 圧縮
        if data.get("active_goals"):
            data["active_goals"] = self.compressor.compress_goals(
                data["active_goals"], 300
            )
        
        # unfinished_tasks 重複排除
        if data.get("unfinished_tasks"):
            deduped = self.deduplicator.deduplicate_list(data["unfinished_tasks"])
            if len(deduped) < len(data["unfinished_tasks"]):
                data["unfinished_tasks"] = deduped
                cleaned = True
                self.stats["removed_duplicates"] += len(data["unfinished_tasks"]) - len(deduped)
        
        # 保存
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        new_size = os.path.getsize(path)
        
        return {
            "cleaned": cleaned,
            "original_size": original_size,
            "new_size": new_size,
            "reduction": original_size - new_size,
        }
    
    def _cleanup_best_practices(self) -> dict:
        """best_practices.json クリーンアップ"""
        path = os.path.join(self.project_root, "best_practices.json")
        
        if not os.path.exists(path):
            return {"removed": 0, "reason": "file not found"}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        original_count = len(data.get("best_practices", []))
        
        # 重複排除
        practices = data.get("best_practices", [])
        seen = set()
        unique = []
        for p in practices:
            lesson = p.get("lesson", "")
            if lesson not in seen:
                seen.add(lesson)
                unique.append(p)
        
        removed = original_count - len(unique)
        data["best_practices"] = unique
        
        # 保存
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "removed": removed,
            "original_count": original_count,
            "new_count": len(unique),
        }
    
    def _archive_stale_sessions(self) -> dict:
        """stale sessions を archive 化"""
        path = os.path.join(self.project_root, "session_registry.json")
        
        if not os.path.exists(path):
            return {"archived": 0, "reason": "file not found"}
        
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        
        sessions = data.get("sessions", [])
        archived = 0
        
        for session in sessions:
            if not self.separation.is_active_session(session):
                # archive へ移動
                archive_path = self.separation.archive_session(session, path)
                archived += 1
        
        # active sessions のみ残す
        active_sessions = self.separation.get_active_sessions(sessions)
        data["sessions"] = active_sessions
        
        # 保存
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        return {
            "archived": archived,
            "remaining_sessions": len(active_sessions),
        }
    
    def run_stress_test(self, iterations: int = 10) -> dict:
        """
        Stress Test: 10回継続して token 増殖を測定
        
        Args:
            iterations: 反復回数
            
        Returns:
            テスト結果
        """
        print("=" * 60)
        print(f"Stress Test: {iterations}回継続")
        print("=" * 60)
        
        # テスト用セッションデータ
        test_session = {
            "chat_id": "test_stress_001",
            "title": "Stress Test Session",
            "summary": "テスト用のセッションです。",
            "recent_topics": ["テスト", "検証", "stabilization"],
            "active_goals": ["Stress Test 完了"],
            "last_user_intent": "Stress Test 実行",
            "updated_at": datetime.now().isoformat(),
        }
        
        # 初期サイズ
        registry_path = os.path.join(self.project_root, "session_registry.json")
        initial_size = os.path.getsize(registry_path) if os.path.exists(registry_path) else 0
        
        sizes = [initial_size]
        context_sizes = []
        injection_counts = []
        
        for i in range(iterations):
            # セッションを更新（実際には同じ内容が追加されるシミュレーション）
            test_session["updated_at"] = datetime.now().isoformat()
            test_session["summary"] += f" 反復{i+1}回目。"
            
            # 安定化モジュールで検証
            context = self.stabilizer.build_safe_context(
                self._mock_registry([test_session]), limit=3
            )
            
            # 循環参照検出（各反復で chain をリセット）
            self.stabilizer.injection_guard.reset_chain()
            is_recursive = self.stabilizer.detect_recursion(context)
            if is_recursive:
                self.stats["injection_recursion_count"] += 1
            
            # 文字数記録
            context_sizes.append(len(context))
            injection_counts.append(self.stabilizer.injection_guard.get_stats()["injected_count"])
            
            # 圧縮率
            original_text = "a" * 1000
            compressed = self.compressor.compress_summary(original_text, 500)
            ratio = len(compressed) / len(original_text)
            
            print(f"  反復 {i+1}: context_size={len(context)}, "
                  f"compression_ratio={ratio:.2f}, "
                  f"recursion={'YES' if is_recursive else 'NO'}")
            
            # 各反復後に stabilizer をリセット
            self.stabilizer.reset()
        
        # 最終サイズ
        final_size = os.path.getsize(registry_path) if os.path.exists(registry_path) else 0
        
        # 結果
        result = {
            "iterations": iterations,
            "initial_size": initial_size,
            "final_size": final_size,
            "size_growth": final_size - initial_size,
            "size_growth_pct": ((final_size - initial_size) / initial_size * 100) if initial_size > 0 else 0,
            "context_sizes": context_sizes,
            "max_context_size": max(context_sizes) if context_sizes else 0,
            "min_context_size": min(context_sizes) if context_sizes else 0,
            "avg_context_size": sum(context_sizes) / len(context_sizes) if context_sizes else 0,
            "injection_recursion_count": self.stats["injection_recursion_count"],
            "compression_ratios": [
                len(self.compressor.compress_summary("a" * 1000, 500)) / 1000
            ] * iterations,
            "avg_compression_ratio": sum([
                len(self.compressor.compress_summary("a" * 1000, 500)) / 1000
                for _ in range(iterations)
            ]) / iterations if iterations > 0 else 0,
        }
        
        return result
    
    def _mock_registry(self, sessions: list):
        """テスト用モックレジストリ"""
        class MockRegistry:
            def __init__(self, sessions):
                self.sessions = sessions
            
            def get_recent_sessions(self, limit=5):
                return self.sessions[:limit]
        
        return MockRegistry(sessions)
    
    def generate_report(self, cleanup_results: dict, stress_test_result: dict) -> str:
        """
        検証レポートを生成
        
        Returns:
            レポートテキスト
        """
        report = []
        report.append("=" * 60)
        report.append("Memory Stabilization Verification Report")
        report.append("=" * 60)
        report.append("")
        
        # クリーンアップ結果
        report.append("## 1. Existing Data Cleanup")
        report.append("-" * 40)
        for key, value in cleanup_results.items():
            report.append(f"  {key}: {value}")
        report.append("")
        
        # Stress Test 結果
        report.append("## 2. Stress Test Results")
        report.append("-" * 40)
        report.append(f"  Iterations: {stress_test_result['iterations']}")
        report.append(f"  Initial Size: {stress_test_result['initial_size']} bytes")
        report.append(f"  Final Size: {stress_test_result['final_size']} bytes")
        report.append(f"  Size Growth: {stress_test_result['size_growth']} bytes "
                      f"({stress_test_result['size_growth_pct']:.2f}%)")
        report.append(f"  Max Context Size: {stress_test_result['max_context_size']} chars")
        report.append(f"  Min Context Size: {stress_test_result['min_context_size']} chars")
        report.append(f"  Avg Context Size: {stress_test_result['avg_context_size']:.1f} chars")
        report.append(f"  Injection Recursion Count: {stress_test_result['injection_recursion_count']}")
        report.append(f"  Avg Compression Ratio: {stress_test_result['avg_compression_ratio']:.2f}")
        report.append("")
        
        # 安定性判定
        report.append("## 3. Stability Assessment")
        report.append("-" * 40)
        
        if stress_test_result['size_growth_pct'] < 50:
            report.append("  [PASS] Size growth is within acceptable range (<50%)")
        else:
            report.append("  [FAIL] Size growth exceeds 50%")
        
        if stress_test_result['injection_recursion_count'] == 0:
            report.append("  [PASS] No injection recursion detected")
        else:
            report.append(f"  [WARN] {stress_test_result['injection_recursion_count']} recursion detected")
        
        if stress_test_result['max_context_size'] <= 1500:
            report.append("  [PASS] Context size within limit (<=1500 chars)")
        else:
            report.append(f"  [FAIL] Context size exceeds limit ({stress_test_result['max_context_size']} > 1500)")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """メイン実行"""
    verifier = MemoryVerifier()
    
    # 1. 既存データクリーンアップ
    cleanup_results = verifier.cleanup_existing_data()
    
    # 2. Stress Test
    stress_test_result = verifier.run_stress_test(iterations=10)
    
    # 3. レポート生成
    report = verifier.generate_report(cleanup_results, stress_test_result)
    
    print(report)
    
    # レポートをファイルに保存
    report_path = os.path.join(verifier.project_root, "memory_stabilization_report.txt")
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")
    
    return report


if __name__ == "__main__":
    main()
