import requests
import time
import re
from datetime import datetime

from ai_agent.llm.lmstudio import LMStudioClient
from ai_agent.memory.memory import MemorySystem


# =========================================
# 🧠 Core
# =========================================
llm = LMStudioClient()
memory = MemorySystem()

SEARXNG_URL = "http://localhost:8888/search"


# =========================================
# 🚦 HARD SEARCH
# 絶対検索するもの
# =========================================
HARD_SEARCH_KEYWORDS = [
    "天気",
    "ニュース",
    "最新",
    "今日",
    "昨日",
    "2026",
    "株価",
    "為替",
    "ドル円",
    "地震",
    "台風",
    "感染",
    "試合",
    "結果",
    "jリーグ",
    "プロ野球",
    "オープン",
    "新店舗",
    "政策",
    "会合",
    "支持率",
    "宇宙",
    "事故",
    "事件"
]


# =========================================
# 🟢 HARD CHAT
# 絶対検索しない
# =========================================
HARD_CHAT_KEYWORDS = [
    "ありがとう",
    "おはよう",
    "おやすみ",
    "眠い",
    "疲れた",
    "雑談",
    "元気",
    "つらい",
    "不安"
]


# =========================================
# 🤖 LLM Search Judge
# 曖昧ケースだけLLMへ
# =========================================
def llm_search_judge(query: str) -> bool:

    try:

        prompt = f"""
次の発言が
リアルタイム検索を必要とするなら YES、
不要なら NO。

質問:
{query}

ルール:
- 天気
- ニュース
- 最近
- 新しい店
- 2026年
- 今日の出来事
は YES。

雑談や感想は NO。

YES か NO のみ返答。
"""

        result = llm.chat([
            {
                "role": "user",
                "content": prompt
            }
        ])

        result = result.upper().strip()

        print("🧠 LLM SEARCH JUDGE:", result)

        return "YES" in result

    except Exception as e:

        print("❌ SEARCH JUDGE ERROR:", e)

        return False


# =========================================
# 🚦 Search Router
# Hybrid方式
# =========================================
def should_search(query: str) -> bool:

    q = query.lower()

    # =====================================
    # 🔵 HARD SEARCH
    # =====================================
    if any(k in q for k in HARD_SEARCH_KEYWORDS):

        print("🔵 HARD SEARCH TRIGGER")

        return True

    # =====================================
    # 🟢 HARD CHAT
    # =====================================
    if any(k in q for k in HARD_CHAT_KEYWORDS):

        print("🟢 HARD CHAT TRIGGER")

        return False

    # =====================================
    # 🤖 LLM Judge
    # =====================================
    return llm_search_judge(query)


# =========================================
# 🌐 Web Search
# Citation対応
# =========================================
def web_search(query: str):

    try:

        enhanced_query = query

        # 🔥 検索補強
        if "天気" in query:
            enhanced_query += " 気温 降水確率"

        if "ドル円" in query:
            enhanced_query += " 為替 最新"

        if "試合" in query:
            enhanced_query += " 最新結果"

        r = requests.get(
            SEARXNG_URL,
            params={
                "q": enhanced_query,
                "format": "json"
            },
            timeout=10
        )

        data = r.json()

        results = data.get("results", [])[:5]

        cleaned = []

        for i, x in enumerate(results):

            title = x.get("title", "")
            content = x.get("content", "")
            url = x.get("url", "")

            text = f"[Source {i+1}] {title} {content}"

            text = re.sub(r"\s+", " ", text)

            if len(text) < 30:
                continue

            cleaned.append({
                "id": i + 1,
                "title": title,
                "content": content,
                "url": url,
                "text": text
            })

        print("\n🌐 SEARCH RESULTS")
        for c in cleaned:
            print(f"[{c['id']}] {c['title']}")

        return cleaned

    except Exception as e:

        print("❌ SEARCH ERROR:", e)

        return []


# =========================================
# 🔥 LEGACY: 旧システムプロンプト（隔離）
# =========================================
def build_legacy_system_prompt(context: str):

    return f"""
あなたはQueryQuest。
ryotaneの相棒。

【基本】
・自然に話す
・知ったかぶりしない
・検索結果を優先する
・不明なことは正直に言う

【重要】
検索結果に存在しない
数字・日付・固有名詞を
勝手に作らない。

【Citation】
必要なら
[Source 1]
のように軽く参照。

【禁止】
・創作
・話を盛る
・レポート口調
・検索サイト紹介

【会話】
モデル自身の自然な個性を活かす。

【関係性】
{context}
"""


# =========================================
# 🆕 新: 最小限のシステムプロンプト
# =========================================
def build_system_prompt(context: str, session_context_override: str = None):
    # ワークスペースコンテキストを取得
    from ai_agent.workspace.registry import WorkspaceRegistry
    workspace = WorkspaceRegistry()
    ws_context = workspace.get_context()
    
    # セッションコンテキストを取得
    from ai_agent.workspace.session_registry import SessionRegistry
    from ai_agent.workspace.session_context import inject_session_context
    session_registry = SessionRegistry()
    
    # 基本システムプロンプト
    base_prompt = f"""
あなたはQueryQuest OS上で動作するAIアシスタントです。

【制約】
・検索結果が存在する場合はそれを優先して使用してください。
・検索結果にない事実を捏造しないでください。
・不明な場合は「分かりません」と答えてください。

【ワークスペースコンテキスト】
{ws_context}

【ユーザー関係性】
{context}
"""
    
    # セッションコンテキストを注入
    if session_context_override:
        # オーバーライドがある場合はそちらを使用
        full_prompt = f"""【結合されたセッションコンテキスト】
{session_context_override}

---

{base_prompt}"""
    else:
        # デフォルトの直近セッションを使用
        full_prompt = inject_session_context(base_prompt, session_registry, limit=3)
    
    # 🔍 DEBUG: system prompt をログ出力
    print("\n" + "="*60)
    print("🔍 SYSTEM PROMPT (DEBUG)")
    print("="*60)
    print(full_prompt)
    print("="*60 + "\n")
    
    return full_prompt


# =========================================
# 🧠 Generate
# =========================================
def generate_answer(
    query,
    facts,
    context,
    session_context_override: str = None
):

    system_prompt = build_system_prompt(context, session_context_override)

    # =====================================
    # 🔵 Search Mode
    # =====================================
    if facts:

        facts_text = "\n\n".join([
            x["text"]
            for x in facts
        ])

        user_prompt = f"""
以下はWeb検索結果。

{facts_text}

ユーザー質問:
{query}

ルール:
・検索結果を優先
・検索結果に無い内容は作らない
・数字を捏造しない
・自然な会話で返答
・必要なら [Source X] を使う
"""

    # =====================================
    # 🟢 Chat Mode
    # =====================================
    else:

        user_prompt = query

    return llm.chat([
        {
            "role": "system",
            "content": system_prompt
        },
        {
            "role": "user",
            "content": user_prompt
        }
    ])


# =========================================
# 🔥 LEGACY: 旧検証（隔離）
# =========================================
def legacy_verify_answer(
    query,
    answer,
    facts
):

    banned = [
        "多分",
        "おそらく",
        "〜らしい",
        "〜みたい"
    ]

    for b in banned:
        answer = answer.replace(b, "")

    # 🔥 検索必要なのに失敗
    if should_search(query) and facts == []:

        return (
            "今ちょっと検索結果を"
            "うまく拾えなかったんだよな。"
            "もう一回聞いてくれる？"
        )

    return answer


# =========================================
# 🆕 新: 検証（事実チェックのみ）
# =========================================
def verify_answer(
    query,
    answer,
    facts
):

    # 検索が必要だったのに事実がない場合は警告
    if should_search(query) and facts == []:
        return "検索結果が見つかりませんでした。別の質問を試してください。"

    return answer


# =========================================
# 🔥 LEGACY: 旧後処理（隔離）
# =========================================
def legacy_cleanup_answer(text):

    text = re.sub(r"\n{3,}", "\n\n", text)

    sentences = re.split(
        r"[。！？]",
        text
    )

    sentences = [
        s.strip()
        for s in sentences
        if s.strip()
    ]

    sentences = sentences[:6]

    result = "。".join(sentences)

    if not result.endswith("。"):
        result += "。"

    return result


# =========================================
# 🆕 新: 後処理（基本的な改行処理のみ）
# =========================================
def cleanup_answer(text):

    # 連続する改行を整理するのみ
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# =========================================
# 🚀 Orchestrator
# =========================================
class Orchestrator:

    def run(
        self,
        query,
        history=None
    ):

        print(f"\n🧠 {query}")

        # =====================================
        # 🎯 Intent Detection
        # =====================================
        from ai_agent.workspace.intent import analyze_intent
        intent = analyze_intent(query)
        
        if intent["type"] in ["continuity", "session_search", "multi_session"]:
            print(f"🎯 CONTINUITY INTENT DETECTED: {intent['type']}")
            print(f"   Keyword: {intent['keyword']}")
            print(f"   Keywords: {intent['keywords']}")
        
        # =====================================
        # 🔍 Session Search (if needed)
        # =====================================
        session_context_override = None
        
        if intent["type"] == "session_search" and intent["keywords"]:
            # セッション検索
            from ai_agent.workspace.session_registry import SessionRegistry
            registry = SessionRegistry()
            results = registry.find_sessions_by_keywords(intent["keywords"], limit=5)
            
            if results:
                print(f"\n📋 検索結果 ({len(results)}件):")
                for i, (session, score) in enumerate(results, 1):
                    print(f"  {i}. {session['title']} (関連度: {score})")
                    print(f"     要約: {session.get('summary', '')[:50]}...")
            else:
                print("\n⚠️ 該当するセッションが見つかりませんでした。")
        
        elif intent["type"] == "multi_session" and intent["keywords"]:
            # 複数セッション結合
            from ai_agent.workspace.session_registry import SessionRegistry
            from ai_agent.workspace.session_context import build_multi_session_context
            
            registry = SessionRegistry()
            results = registry.find_sessions_by_keywords(intent["keywords"], limit=3)
            
            if results:
                # 関連度順に結合（最大 2000 文字）
                session_context_override = build_multi_session_context(
                    registry, results, max_total_chars=2000
                )
                print(f"\n🔗 マルチセッションコンテキスト結合完了")
            else:
                print("\n⚠️ 該当するセッションが見つかりませんでした。")
        
        # =====================================
        # 🧠 Memory
        # =====================================
        memory.update(query)

        context = memory.get_context()

        # =====================================
        # 🔍 Search Judge
        # =====================================
        use_search = should_search(query)

        print("🔍 SEARCH MODE:", use_search)

        facts = []

        # =====================================
        # 🌐 Search
        # =====================================
        if use_search:

            print("🌐 searching...")

            facts = web_search(query)

            time.sleep(0.3)

        # =====================================
        # 🧠 Generate
        # =====================================
        draft = generate_answer(
            query,
            facts,
            context,
            session_context_override=session_context_override
        )

        # =====================================
        # 🔍 Verify
        # =====================================
        verified = verify_answer(
            query,
            draft,
            facts
        )

        # =====================================
        # ✨ Cleanup
        # =====================================
        final = cleanup_answer(
            verified
        )

        # =====================================
        # 💾 Save
        # =====================================
        memory.save_log(
            query,
            final
        )

        # =====================================
        # 📦 Session Auto-Save
        # =====================================
        try:
            from ai_agent.workspace.session_auto_save import auto_save_session
            import uuid
            
            # chat_id の生成（MVP: 新規生成）
            chat_id = f"chat_{uuid.uuid4().hex[:8]}"
            title = f"Chat_{datetime.now().strftime('%Y%m%d_%H%M')}"
            
            # セッション自動保存
            auto_save_session(
                chat_id=chat_id,
                title=title,
                query=query,
                answer=final
            )
            
            # 自動マージチェック（同一タイトルまたは高関連度）
            try:
                from ai_agent.workspace.session_registry import SessionRegistry
                registry = SessionRegistry()
                
                # 同一タイトルのセッションを検索
                existing = registry.find_session_by_title(title.split('_')[-1] if '_' in title else title)
                
                if existing and existing.get("chat_id") != chat_id:
                    # 高関連度セッションがある場合、自動マージを提案
                    high_score_results = registry.find_sessions_by_keywords(
                        [title.split('_')[-1] if '_' in title else title],
                        limit=5
                    )
                    
                    high_score = [r for r in high_score_results if r[1] >= 5]
                    
                    if high_score:
                        print(f"\n🔄 自動マージ候補検出: {len(high_score)}件")
                        # 実際のマージはユーザー確認後（MVP 段階ではログのみ）
            except Exception as e:
                print(f"⚠️ 自動マージチェック失敗: {e}")
            
            # プロジェクトマスタードキュメントを更新
            try:
                from ai_agent.workspace.project_master import generate_project_master
                master = generate_project_master("queryquest_project")
                print(f"\n📊 プロジェクトマスター更新完了 (セッション数：{master['session_count']})")
            except Exception as e:
                print(f"⚠️ プロジェクトマスター更新失敗: {e}")
        except Exception as e:
            print(f"⚠️ Session auto-save failed: {e}")

        # =====================================
        # 🚀 Return
        # =====================================
        return {
            "mode": (
                "search"
                if use_search
                else "chat"
            ),
            "final": final,
            "sources": len(facts)
        }