#!/usr/bin/env python3
"""
Session Continuity MVP 動作確認テスト
"""

import sys
import os

# プロジェクトルートにパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.workspace.session_registry import SessionRegistry
from ai_agent.workspace.session_context import build_session_context, inject_session_context
from ai_agent.workspace.intent import analyze_intent, detect_continuity_intent
from ai_agent.workspace.session_auto_save import extract_topics, generate_summary, extract_next_actions, auto_save_session


def test_session_registry():
    """SessionRegistry の基本機能テスト"""
    print("=" * 60)
    print("🧪 SessionRegistry テスト")
    print("=" * 60)
    
    registry = SessionRegistry()
    
    # 1. get_recent_sessions
    print("\n📋 最近のセッション:")
    sessions = registry.get_recent_sessions(limit=5)
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s['title']}")
        print(f"     要約: {s.get('summary', '')[:50]}...")
    
    # 2. find_session_by_title
    print("\n🔍 タイトル検索テスト:")
    found = registry.find_session_by_title("QueryQuest")
    if found:
        print(f"  ✅ 見つかった: {found['title']}")
    else:
        print("  ❌ 見つからない")
    
    # 3. update_session
    print("\n📝 セッション更新テスト:")
    updated = registry.update_session(
        chat_id="chat_test_001",
        title="テストセッション",
        summary="テスト用の要約",
        recent_topics=["テスト", "MVP"],
        active_goals=["Phase 4: session continuity"],
        last_user_intent="テスト意図"
    )
    print(f"  ✅ 更新/作成完了: {updated['title']}")
    
    # 4. get_recent_sessions (更新後)
    print("\n📋 更新後の最近のセッション:")
    sessions = registry.get_recent_sessions(limit=5)
    for i, s in enumerate(sessions, 1):
        print(f"  {i}. {s['title']}")
    
    return True


def test_session_context():
    """セッションコンテキスト生成テスト"""
    print("\n" + "=" * 60)
    print("🧪 セッションコンテキスト テスト")
    print("=" * 60)
    
    registry = SessionRegistry()
    
    # build_session_context
    context = build_session_context(registry, limit=3)
    print("\n📄 生成されたセッションコンテキスト:")
    print("-" * 40)
    print(context)
    print("-" * 40)
    
    # inject_session_context
    base_prompt = "あなたはAIアシスタントです。"
    injected = inject_session_context(base_prompt, registry, limit=3)
    
    print("\n📄 セッションコンテキスト注入後のプロンプト:")
    print("-" * 40)
    print(injected[:500] + "...")
    print("-" * 40)
    
    return True


def test_intent_detection():
    """意図認識テスト"""
    print("\n" + "=" * 60)
    print("🧪 意図認識 テスト")
    print("=" * 60)
    
    test_cases = [
        ("前のチャットの続きをやりたい", "continuity"),
        ("あのプロジェクトの続き", "continuity"),
        ("この作業を再開したい", "continuity"),
        ("前のチャットは何だったっけ", "session_search"),
        ("こんにちは", "normal"),
        ("天気教えて", "normal"),
    ]
    
    for query, expected_type in test_cases:
        intent = analyze_intent(query)
        status = "✅" if intent["type"] == expected_type else "❌"
        print(f"  {status} '{query}'")
        print(f"     結果: {intent['type']} (期待: {expected_type})")


def test_auto_save():
    """自動保存機能テスト"""
    print("\n" + "=" * 60)
    print("🧪 自動保存機能 テスト")
    print("=" * 60)
    
    # テスト用の会話データ
    test_query = "Session Continuity MVP を実装したい。session_registry.json を作成して、SessionRegistry クラスを実装する。"
    test_answer = "了解しました。Session Continuity MVP を実装します。session_registry.json を作成し、SessionRegistry クラスで load/save/update/get_recent_sessions/find_session_by_title の機能を実装します。"
    
    # トピック抽出
    topics = extract_topics(test_query + " " + test_answer)
    print(f"\n📋 抽出されたトピック:")
    for t in topics:
        print(f"  - {t}")
    
    # 要約生成（LLM 使用）
    print("\n📝 要約生成中...")
    summary = generate_summary(test_query, test_answer)
    print(f"  要約: {summary}")
    
    # next_actions 抽出（LLM 使用）
    print("\n📋 next_actions 抽出中...")
    next_actions = extract_next_actions(test_query, test_answer)
    print(f"  next_actions:")
    for i, action in enumerate(next_actions, 1):
        print(f"    {i}. {action}")
    
    # 自動保存
    print("\n💾 自動保存中...")
    try:
        saved = auto_save_session(
            chat_id="chat_test_auto_001",
            title="テストセッション自動保存",
            query=test_query,
            answer=test_answer
        )
        print(f"  ✅ 保存完了: {saved['title']}")
        
        # 保存確認
        registry = SessionRegistry()
        saved_session = registry.get_session("chat_test_auto_001")
        if saved_session:
            print(f"\n📋 保存確認:")
            print(f"  title: {saved_session['title']}")
            print(f"  summary: {saved_session.get('summary', '')[:50]}...")
            print(f"  topics: {saved_session.get('recent_topics', [])}")
            print(f"  next_actions: {saved_session.get('next_actions', [])}")
    except Exception as e:
        print(f"  ❌ 保存失敗: {e}")
        import traceback
        traceback.print_exc()


def main():
    """メインテスト実行"""
    print("\n" + "=" * 60)
    print("🚀 Session Continuity MVP 動作確認")
    print("=" * 60)
    
    try:
        test_session_registry()
        test_session_context()
        test_intent_detection()
        test_auto_save()
        
        print("\n" + "=" * 60)
        print("✅ 全テスト完了")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ テスト失敗: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
