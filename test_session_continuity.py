#!/usr/bin/env python3
"""
Session Continuity MVP 動作確認テスト
"""

import sys
import os

# プロジェクトルートにパスを追加
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_agent.workspace.session_registry import SessionRegistry
from ai_agent.workspace.session_context import build_session_context, inject_session_context, build_multi_session_context, build_combined_context
from ai_agent.workspace.intent import analyze_intent, detect_continuity_intent, detect_multi_session_intent, extract_search_keywords
from ai_agent.workspace.session_auto_save import extract_topics, generate_summary, extract_next_actions, auto_save_session, distill_knowledge, auto_merge_sessions
from ai_agent.workspace.project_master import generate_project_master, load_project_master, add_best_practice
from ai_agent.workspace.reflection import evaluate_task, generate_retry_plan, check_resource_usage
from ai_agent.workspace.workspace_scanner import scan_workspace, scan_and_compress


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


def test_session_search():
    """セッション検索機能テスト"""
    print("\n" + "=" * 60)
    print("🧪 セッション検索機能 テスト")
    print("=" * 60)
    
    registry = SessionRegistry()
    
    # キーワード検索テスト
    keywords = ["Session", "Continuity"]
    results = registry.find_sessions_by_keywords(keywords, limit=5)
    
    print(f"\n🔍 キーワード検索: {keywords}")
    print(f"   結果: {len(results)}件")
    
    for i, (session, score) in enumerate(results, 1):
        print(f"   {i}. {session['title']} (関連度: {score})")
        print(f"      要約: {session.get('summary', '')[:50]}...")
    
    # 複数セッション結合テスト
    if results:
        print("\n🔗 マルチセッションコンテキスト生成:")
        context = build_multi_session_context(registry, results, max_total_chars=1000)
        print(context[:500] + "...")


def test_intent_detection_advanced():
    """高度な意図認識テスト"""
    print("\n" + "=" * 60)
    print("🧪 高度な意図認識 テスト")
    print("=" * 60)
    
    test_cases = [
        ("前のチャットの続きをやりたい", "continuity"),
        ("あのプロジェクトの続き", "continuity"),
        ("この作業を再開したい", "continuity"),
        ("前のチャットは何だったっけ", "session_search"),
        ("Session Continuity について話した過去のチャットを探して", "session_search"),
        ("Session と Registry の内容を踏まえて新しい機能を考えて", "multi_session"),
        ("A と B の両方を合わせて", "multi_session"),
        ("こんにちは", "normal"),
        ("天気教えて", "normal"),
    ]
    
    for query, expected_type in test_cases:
        intent = analyze_intent(query)
        status = "✅" if intent["type"] == expected_type else "❌"
        print(f"  {status} '{query}'")
        print(f"     結果: {intent['type']} (期待: {expected_type})")
        if intent['keywords']:
            print(f"     キーワード: {intent['keywords']}")


def test_session_merge():
    """セッションマージ機能テスト"""
    print("\n" + "=" * 60)
    print("🧪 セッションマージ機能 テスト")
    print("=" * 60)
    
    registry = SessionRegistry()
    
    # テスト用のセッションを作成
    test_sessions = [
        {
            "chat_id": "chat_merge_test_001",
            "title": "テストセッション A",
            "summary": "テスト A の要約",
            "recent_topics": ["テスト", "A"],
            "active_goals": ["ゴール A"],
            "next_actions": ["タスク A1", "タスク A2"],
            "updated_at": "2026-05-07T10:00:00Z"
        },
        {
            "chat_id": "chat_merge_test_002",
            "title": "テストセッション B",
            "summary": "テスト B の要約",
            "recent_topics": ["テスト", "B"],
            "active_goals": ["ゴール B"],
            "next_actions": ["タスク B1", "タスク B2"],
            "updated_at": "2026-05-07T11:00:00Z"
        }
    ]
    
    # セッションを追加
    for session in test_sessions:
        registry.update_session(
            chat_id=session["chat_id"],
            title=session["title"],
            summary=session["summary"],
            recent_topics=session["recent_topics"],
            active_goals=session["active_goals"],
            last_user_intent="テスト"
        )
        # next_actions を直接追加
        import json
        with open(registry.path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for s in data["sessions"]:
            if s["chat_id"] == session["chat_id"]:
                s["next_actions"] = session["next_actions"]
        with open(registry.path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    # マージ実行
    print("\n🔄 マージ実行:")
    merged = registry.merge_sessions(
        target_chat_id="chat_merge_test_001",
        source_sessions=test_sessions
    )
    
    print(f"  ✅ マージ完了: {merged['title']}")
    print(f"  サマリー: {merged.get('summary', '')[:100]}...")
    print(f"  トピック: {merged.get('recent_topics', [])}")
    print(f"  next_actions: {merged.get('next_actions', [])}")
    print(f"  merged_from: {merged.get('merged_from', [])}")


def test_project_master():
    """プロジェクトマスタードキュメント生成テスト"""
    print("\n" + "=" * 60)
    print("🧪 プロジェクトマスタードキュメント テスト")
    print("=" * 60)
    
    # 生成
    master = generate_project_master("queryquest_project")
    
    print(f"\n📊 プロジェクトマスター:")
    print(f"  workspace_id: {master['workspace_id']}")
    print(f"  セッション数: {master['session_count']}")
    print(f"  重要トピック: {master['important_topics'][:5]}")
    print(f"  未完了タスク数: {len(master['unfinished_tasks'])}")
    print(f"  テックスタック：{master.get('tech_stack', {}).get('python_version', 'N/A')}")
    
    if master['unfinished_tasks']:
        print(f"\n📋 未完了タスクリスト (上位 5 件):")
        for i, task in enumerate(master['unfinished_tasks'][:5], 1):
            print(f"  {i}. {task}")
    
    # 読み込みテスト
    loaded = load_project_master("queryquest_project")
    print(f"\n✅ 読み込みテスト完了: {loaded['workspace_id']}")


def test_reflection():
    """自己評価テスト"""
    print("\n" + "=" * 60)
    print("🧪 自己評価テスト")
    print("=" * 60)
    
    # テスト用のタスクと出力
    task = "Python でファイルを読み込むコードを書く"
    output = "```python\nwith open('file.txt', 'r') as f:\n    content = f.read()\nprint(content)\n```"
    
    # 自己評価
    evaluation = evaluate_task(task, output)
    
    print(f"\n🪞 自己評価結果:")
    print(f"  スコア: {evaluation['score']}/10")
    print(f"  改善点: {evaluation['improvements'][:2]}")
    print(f"  教訓: {evaluation['lessons'][:2]}")
    print(f"  再実行必要: {evaluation['retry_needed']}")
    
    # 再実行プラン生成
    if evaluation['score'] < 7:
        retry_plan = generate_retry_plan(task, evaluation)
        print(f"\n🔄 再実行プラン:")
        print(f"  プラン: {retry_plan['plan'][:100]}...")
        print(f"  優先度: {retry_plan['priority']}")
    
    # リソース監視
    resource_usage = check_resource_usage()
    print(f"\n📊 リソース使用状況:")
    print(f"  メモリ：{resource_usage['memory_usage_mb']:.1f}MB")
    print(f"  重大：{resource_usage['is_critical']}")
    print(f"  推奨：{resource_usage['recommendation']}")


def test_workspace_scanner():
    """ワークスペーススキャナーテスト"""
    print("\n" + "=" * 60)
    print("🧪 ワークスペーススキャナーテスト")
    print("=" * 60)
    
    # スキャン
    result = scan_workspace()
    
    print(f"\n📋 スキャン結果:")
    print(f"  ドキュメント数：{len(result['documents'])}件")
    print(f"  ルール数：{len(result['rules'])}件")
    print(f"  サマリー：{result['summary']}")
    
    # テックスタック
    tech_stack = result.get('tech_stack', {})
    if tech_stack.get('libraries'):
        libs = list(tech_stack['libraries'].keys())[:5]
        print(f"  主要ライブラリ：{', '.join(libs)}")
    
    # 圧縮形式
    compressed = scan_and_compress()
    print(f"\n📦 圧縮形式:")
    print(f"  {compressed[:200]}...")


def test_self_reflection():
    """自己評価・反省機能テスト"""
    print("\n" + "=" * 60)
    print("🧪 自己評価・反省機能 テスト")
    print("=" * 60)
    
    # テスト用のタスクと出力
    test_query = "Python でファイル操作を行うコードを書いてください"
    test_output = """
import os

# ファイルの読み込み
with open('test.txt', 'r') as f:
    content = f.read()
    print(content)

# ファイルの書き込み
with open('output.txt', 'w') as f:
    f.write('Hello, World!')
"""
    
    # 自己評価
    print("\n🪞 自己評価実行:")
    evaluation = evaluate_task_output(
        task_description=test_query,
        output=test_output,
        success_criteria="ファイル操作が正しく行えること"
    )
    
    print(f"  スコア: {evaluation['score']}/10")
    print(f"  改善点: {evaluation['improvements'][:2]}")
    print(f"  教訓: {evaluation['lessons'][:2]}")
    print(f"  再実行必要: {evaluation['needs_retry']}")
    
    # 改善プラン生成
    print("\n🔄 改善プラン生成:")
    improvement_plan = generate_improvement_plan(
        task_description=test_query,
        evaluation=evaluation,
        previous_attempts=[]
    )
    
    print(f"  プラン: {improvement_plan['plan'][:100]}...")
    print(f"  優先度: {improvement_plan['priority']}")
    print(f"  見積もり: {improvement_plan['estimated_effort']}")
    
    # リソース監視
    print("\n📊 リソース監視:")
    resource_usage = check_resource_usage()
    print(f"  メモリ使用率: {resource_usage['memory_percent']:.1f}%")
    print(f"  RSS: {resource_usage['memory_rss_mb']:.1f} MB")
    print(f"  危険度: {'⚠️ 危険' if resource_usage['is_critical'] else '✅ 正常'}")
    
    # ベストプラクティス追加
    print("\n📚 ベストプラクティス追加:")
    if evaluation['lessons']:
        add_best_practice("queryquest_project", evaluation['lessons'][0], "reflection")
        print(f"  ✅ 教訓を追加: {evaluation['lessons'][0][:50]}...")


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
        test_session_search()
        test_intent_detection_advanced()
        test_session_merge()
        test_project_master()
        test_reflection()
        test_workspace_scanner()
        
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
