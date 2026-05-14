"""
Memory OS テスト - Project_035

メモリオペレーティングシステムの動作確認。
"""

import sys
import os
import time

# プロジェクトルートにパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from ai_agent.memory import (
    MemoryOS,
    MemoryEntry,
    MemoryLayer,
    create_memory_os,
)


def test_memory_store():
    """メモリ保存テスト"""
    print("\n=== Memory Store Test ===")
    
    memory_os = MemoryOS()
    
    # 作業メモリへ保存
    entry = MemoryEntry(
        id="mem_001",
        content="ユーザーはPythonを好む",
        metadata={"source": "conversation", "type": "preference"},
        importance=0.8,
        layer=MemoryLayer.WORKING,
        tags=["preference", "python"],
    )
    memory_os.store(entry)
    assert entry.id in memory_os.working_memory
    print(f"✅ Stored in working memory: {entry.id}")
    
    # 短期メモリへ保存
    entry2 = MemoryEntry(
        id="mem_002",
        content="ユーザーはMacを使用",
        metadata={"source": "conversation", "type": "fact"},
        importance=0.6,
        layer=MemoryLayer.SHORT_TERM,
        tags=["fact", "mac"],
    )
    memory_os.store(entry2)
    assert entry2.id in memory_os.short_term_memory
    print(f"✅ Stored in short-term memory: {entry2.id}")
    
    # 長期メモリへ保存
    entry3 = MemoryEntry(
        id="mem_003",
        content="QueryQuestの哲学",
        metadata={"source": "system", "type": "rule"},
        importance=0.9,
        layer=MemoryLayer.LONG_TERM,
        tags=["philosophy", "queryquest"],
    )
    memory_os.store(entry3)
    assert entry3.id in memory_os.long_term_memory
    print(f"✅ Stored in long-term memory: {entry3.id}")
    
    print("✅ Memory Store Test PASSED\n")


def test_memory_retrieve():
    """メモリ検索テスト"""
    print("\n=== Memory Retrieve Test ===")
    
    memory_os = MemoryOS()
    
    # メモリ登録
    for i in range(5):
        entry = MemoryEntry(
            id=f"mem_{i:03d}",
            content=f"Pythonプログラミングのメモ{i}",
            metadata={"source": "conversation", "type": "fact"},
            importance=0.5 + i * 0.1,
            layer=MemoryLayer.WORKING,
            tags=["python", "programming", f"mem{i}"],
        )
        memory_os.store(entry)
    
    # 検索
    results = memory_os.retrieve("Python", k=3)
    assert len(results) <= 3
    print(f"✅ Retrieved {len(results)} results for 'Python'")
    
    # 検索結果の重要度確認
    for result in results:
        assert result.importance > 0
        print(f"   - {result.content[:30]}... (importance: {result.importance})")
    
    print("✅ Memory Retrieve Test PASSED\n")


def test_memory_update_delete():
    """メモリ更新・削除テスト"""
    print("\n=== Memory Update/Delete Test ===")
    
    memory_os = MemoryOS()
    
    # メモリ登録
    entry = MemoryEntry(
        id="mem_update_test",
        content="元のコンテンツ",
        metadata={"source": "test"},
        importance=0.5,
        layer=MemoryLayer.WORKING,
        tags=["test"],
    )
    memory_os.store(entry)
    
    # 更新
    result = memory_os.update("mem_update_test", {"content": "更新されたコンテンツ", "importance": 0.9})
    assert result
    updated = memory_os.retrieve("更新", k=1)
    assert updated[0].content == "更新されたコンテンツ"
    print(f"✅ Memory updated")
    
    # 削除
    result = memory_os.delete("mem_update_test")
    assert result
    deleted = memory_os.retrieve("更新", k=1)
    assert len(deleted) == 0
    print(f"✅ Memory deleted")
    
    print("✅ Memory Update/Delete Test PASSED\n")


def test_consolidation():
    """自動統合テスト"""
    print("\n=== Consolidation Test ===")
    
    memory_os = MemoryOS()
    
    # 短期メモリに多数のエントリを登録
    for i in range(400):
        entry = MemoryEntry(
            id=f"mem_consolidate_{i:03d}",
            content=f"短期メモリのエントリ{i}",
            metadata={"source": "test"},
            importance=0.5,
            layer=MemoryLayer.SHORT_TERM,
            tags=["test"],
        )
        memory_os.store(entry)
    
    initial_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory before consolidation: {initial_count}")
    
    # 統合実行
    count = memory_os.consolidate()
    print(f"✅ Consolidated {count} entries")
    
    final_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory after consolidation: {final_count}")
    
    assert final_count < initial_count
    print("✅ Consolidation Test PASSED\n")


def test_forgetting():
    """忘却テスト"""
    print("\n=== Forgetting Test ===")
    
    memory_os = MemoryOS()
    
    # 短期メモリに多数のエントリを登録（過去の日付）
    past_time = time.time() - 86400 * 2  # 2日前
    for i in range(100):
        entry = MemoryEntry(
            id=f"mem_forget_{i:03d}",
            content=f"忘却テストエントリ{i}",
            metadata={"source": "test"},
            importance=0.5,
            layer=MemoryLayer.SHORT_TERM,
            tags=["test"],
            created_at=past_time,  # 過去の日付
            accessed_at=past_time,  # 過去の日付
        )
        memory_os.store(entry)
    
    initial_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory before forgetting: {initial_count}")
    
    # LRU忘却
    count = memory_os.forget(policy="lru")
    print(f"✅ Forgotten {count} entries (LRU)")
    
    final_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory after forgetting: {final_count}")
    
    assert final_count < initial_count
    print("✅ Forgetting Test PASSED\n")


def test_compression():
    """圧縮テスト"""
    print("\n=== Compression Test ===")
    
    memory_os = MemoryOS()
    
    # 類似エントリを登録
    for i in range(10):
        entry = MemoryEntry(
            id=f"mem_compress_{i:03d}",
            content=f"Pythonプログラミングのメモ{i}",
            metadata={"source": "test"},
            importance=0.5,
            layer=MemoryLayer.SHORT_TERM,
            tags=["python", "programming"],  # 同じタグ
        )
        memory_os.store(entry)
    
    initial_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory before compression: {initial_count}")
    
    # 圧縮実行
    count = memory_os.compress()
    print(f"✅ Compressed {count} entries")
    
    final_count = len(memory_os.short_term_memory)
    print(f"✅ Short-term memory after compression: {final_count}")
    
    assert final_count < initial_count
    print("✅ Compression Test PASSED\n")


def test_memory_stats():
    """メモリ統計テスト"""
    print("\n=== Memory Stats Test ===")
    
    memory_os = MemoryOS()
    
    # メモリ登録
    for i in range(5):
        entry = MemoryEntry(
            id=f"mem_stats_{i:03d}",
            content=f"統計テストエントリ{i}",
            metadata={"source": "test"},
            importance=0.5,
            layer=MemoryLayer.WORKING,
            tags=["test"],
        )
        memory_os.store(entry)
    
    # 統計取得
    stats = memory_os.get_stats()
    assert stats["working_memory_count"] == 5
    assert stats["total_entries"] == 5
    print(f"✅ Stats: {stats['total_entries']} total entries")
    
    # ステータス取得
    status = memory_os.get_status()
    assert "short_term_usage" in status
    print(f"✅ Status: {status['short_term_usage']:.2%} short-term usage")
    
    print("✅ Memory Stats Test PASSED\n")


def main():
    """全テスト実行"""
    print("=" * 60)
    print("QueryQuest Memory OS Tests (Project_035)")
    print("=" * 60)
    
    try:
        test_memory_store()
        test_memory_retrieve()
        test_memory_update_delete()
        test_consolidation()
        test_forgetting()
        test_compression()
        test_memory_stats()
        
        print("=" * 60)
        print("✅ ALL TESTS PASSED")
        print("=" * 60)
        return 0
    
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
