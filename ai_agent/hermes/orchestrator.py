import requests
import time
import re

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
# 🧠 System Prompt
# =========================================
def build_system_prompt(context: str):

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
# 🧠 Generate
# =========================================
def generate_answer(
    query,
    facts,
    context
):

    system_prompt = build_system_prompt(context)

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
# 🔍 Verify
# =========================================
def verify_answer(
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
# ✨ Cleanup
# =========================================
def cleanup_answer(text):

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
            context
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