# ai_agent/workspace/memory_stabilization/extended_verification.py

"""
Extended Verification

より現実的なシナリオで検証。

シナリオ:
1. 複数セッションが交互に更新される
2. 古いセッションが archive 化される
3. project_master が再生成される
"""

import json
import os
import sys
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_agent.workspace.memory_stabilization import (
    MemoryStabilizer,
    SummaryCompressor,
    ContextDeduplicator,
    MemorySeparation,
)


class ExtendedVerifier:
    """Extended Verification クラス"""
    
    def __init__(self):
        self.stabilizer = MemoryStabilizer()
        self.compressor = SummaryCompressor()
        self.deduplicator = ContextDeduplicator()
        self.separation = MemorySeparation()
        
        # テスト用セッションデータ
        self.sessions = []
        for i in range(10):
            self.sessions.append({
                "chat_id": f"test_ext_{i:03d}",
                "title": f"Extended Test Session {i}",
                "summary": f"テストセッション{i}の要約。",
                "recent_topics": [f"トピック_{i}", f"検証_{i}"],
                "active_goals": [f"ゴール_{i}"],
                "last_user_intent": f"テスト意図{i}",
                "updated_at": (datetime.now() - timedelta(days=i)).isoformat(),
            })
    
    def test_multi_session_merge(self) -> dict:
        """複数セッションマージテスト"""
        print("=" * 60)
        print("複数セッションマージテスト")
        print("=" * 60)
        
        # 最初の 3 セッションを取得
        target = self.sessions[0].copy()
        sources = self.sessions[1:4]
        
        # マージ前のサイズ
        original_summary = target["summary"]
        for s in sources:
            original_summary += f"\n[元セッション {s['title']}] {s['summary']}"
        
        print(f"  マージ前サマリーサイズ: {len(original_summary)} chars")
        
        # マージ（安定化ルール適用）
        merged_summary = original_summary
        merged_summary = self.compressor.compress_summary(merged_summary, 500)
        
        print(f"  マージ後サマリーサイズ: {len(merged_summary)} chars")
        print(f"  圧縮率: {len(merged_summary) / len(original_summary):.2f}")
        
        return {
            "original_size": len(original_summary),
            "merged_size": len(merged_summary),
            "compression_ratio": len(merged_summary) / len(original_summary),
        }
    
    def test_archive_separation(self) -> dict:
        """Archive 分離テスト"""
        print("=" * 60)
        print("Archive 分離テスト")
        print("=" * 60)
        
        active = self.separation.get_active_sessions(self.sessions)
        archived = [s for s in self.sessions if s not in active]
        
        print(f"  全セッション: {len(self.sessions)}")
        print(f"  Active: {len(active)}")
        print(f"  Archived: {len(archived)}")
        
        return {
            "total": len(self.sessions),
            "active": len(active),
            "archived": len(archived),
        }
    
    def test_long_term_stability(self, iterations: int = 50) -> dict:
        """長期安定性テスト（50回）"""
        print("=" * 60)
        print(f"長期安定性テスト: {iterations}回")
        print("=" * 60)
        
        sizes = []
        context_sizes = []
        
        for i in range(iterations):
            # セッションを更新
            self.sessions[0]["updated_at"] = datetime.now().isoformat()
            self.sessions[0]["summary"] += f" 反復{i+1}。"
            
            # 安定化モジュールで検証
            context = self.stabilizer.build_safe_context(
                self._mock_registry(self.sessions), limit=3
            )
            
            sizes.append(len(json.dumps(self.sessions)))
            context_sizes.append(len(context))
            
            # 10 回ごとに出力
            if (i + 1) % 10 == 0:
                print(f"  反復 {i+1}: session_size={sizes[-1]}, "
                      f"context_size={context_sizes[-1]}")
            
            # stabilizer リセット
            self.stabilizer.reset()
        
        # 結果
        return {
            "iterations": iterations,
            "initial_size": sizes[0],
            "final_size": sizes[-1],
            "size_growth": sizes[-1] - sizes[0],
            "size_growth_pct": ((sizes[-1] - sizes[0]) / sizes[0] * 100) if sizes[0] > 0 else 0,
            "max_context_size": max(context_sizes),
            "min_context_size": min(context_sizes),
            "avg_context_size": sum(context_sizes) / len(context_sizes),
        }
    
    def _mock_registry(self, sessions: list):
        """テスト用モックレジストリ"""
        class MockRegistry:
            def __init__(self, sessions):
                self.sessions = sessions
            
            def get_recent_sessions(self, limit=5):
                return self.sessions[:limit]
        
        return MockRegistry(sessions)
    
    def generate_report(self, merge_result: dict, archive_result: dict, 
                        long_term_result: dict) -> str:
        """レポート生成"""
        report = []
        report.append("=" * 60)
        report.append("Extended Verification Report")
        report.append("=" * 60)
        report.append("")
        
        # マージテスト
        report.append("## 1. Multi-Session Merge Test")
        report.append("-" * 40)
        report.append(f"  Original Size: {merge_result['original_size']} chars")
        report.append(f"  Merged Size: {merge_result['merged_size']} chars")
        report.append(f"  Compression Ratio: {merge_result['compression_ratio']:.2f}")
        report.append(f"  [PASS] Compression applied" if merge_result['compression_ratio'] < 1.0 else "  [FAIL]")
        report.append("")
        
        # Archive 分離
        report.append("## 2. Archive Separation Test")
        report.append("-" * 40)
        report.append(f"  Total Sessions: {archive_result['total']}")
        report.append(f"  Active: {archive_result['active']}")
        report.append(f"  Archived: {archive_result['archived']}")
        report.append(f"  [PASS] Separation working" if archive_result['archived'] > 0 else "  [WARN] No archived sessions")
        report.append("")
        
        # 長期安定性
        report.append("## 3. Long-Term Stability Test")
        report.append("-" * 40)
        report.append(f"  Iterations: {long_term_result['iterations']}")
        report.append(f"  Initial Size: {long_term_result['initial_size']} bytes")
        report.append(f"  Final Size: {long_term_result['final_size']} bytes")
        report.append(f"  Size Growth: {long_term_result['size_growth']} bytes "
                      f"({long_term_result['size_growth_pct']:.2f}%)")
        report.append(f"  Max Context Size: {long_term_result['max_context_size']} chars")
        report.append(f"  Min Context Size: {long_term_result['min_context_size']} chars")
        report.append(f"  Avg Context Size: {long_term_result['avg_context_size']:.1f} chars")
        
        if long_term_result['size_growth_pct'] < 50:
            report.append(f"  [PASS] Size growth within limit (<50%)")
        else:
            report.append(f"  [FAIL] Size growth exceeds 50%")
        
        if long_term_result['max_context_size'] <= 1500:
            report.append(f"  [PASS] Context size within limit (<=1500)")
        else:
            report.append(f"  [FAIL] Context size exceeds limit")
        
        report.append("")
        report.append("=" * 60)
        
        return "\n".join(report)


def main():
    """メイン実行"""
    verifier = ExtendedVerifier()
    
    # テスト実行
    merge_result = verifier.test_multi_session_merge()
    archive_result = verifier.test_archive_separation()
    long_term_result = verifier.test_long_term_stability(iterations=50)
    
    # レポート生成
    report = verifier.generate_report(merge_result, archive_result, long_term_result)
    
    print(report)
    
    # レポート保存
    report_path = "/Volumes/Data SSD/Docker/local_ai_project/QueryQuest/extended_verification_report.txt"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report)
    
    print(f"\nReport saved to: {report_path}")


if __name__ == "__main__":
    main()
