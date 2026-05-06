# ai_agent/agent/react_engine.py

from ai_agent.mcp.router import route_mcp
from ai_agent.llm.lmstudio import LMStudioClient
from ai_agent.memory.vector_memory import VectorMemory
from ai_agent.router.semantic_router import SemanticToolRouter
from ai_agent.self_improve.improver import SelfImprover


class ReActEngine:

    def __init__(self, max_steps=5, retry_limit=2):
        self.max_steps = max_steps
        self.retry_limit = retry_limit
        self.llm = LMStudioClient()
        self.memory = VectorMemory()
        self.router = SemanticToolRouter()
        self.improver = SelfImprover()

    def run(self, query: str):
        trace = []

        # ① ルーティング（安全化）
        try:
            action = self.router.route(query)
        except Exception:
            action = "chat"

        if action not in ["search", "code", "chat"]:
            action = "chat"

        trace.append({"step": 0, "action": action})

        # ② メモリ取得（安全化）
        try:
            memories = self.memory.search(query)
            if not isinstance(memories, list):
                memories = []
        except Exception:
            memories = []

        memory_context = "\n".join(map(str, memories))

        # ③ 検索処理
        search_context = ""

        if action == "search":
            try:
                result = route_mcp(query)

                if isinstance(result, dict) and result.get("ok"):
                    search_context = "\n".join([
                        f"- {r.get('title','')}: {r.get('content','')}"
                        for r in result.get("results", [])[:3]
                    ])
                else:
                    search_context = ""

                trace.append({"step": 1, "search": "ok"})

            except Exception as e:
                trace.append({"step": 1, "search_error": str(e)})

        # ④ プロンプト構築
        if action == "code":
            system = "あなたはSwift/Xcodeの専門家です。日本語で技術的に正確に答えてください。"
        else:
            system = "あなたは親切なAIです。日本語で簡潔に答えてください。"

        user_content = f"""
質問:
{query}

検索結果:
{search_context}

過去の記憶:
{memory_context}
"""

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_content}
        ]

        # ⑤ LLM（リトライ付き）
        answer = ""
        for i in range(self.retry_limit):
            try:
                answer = self.llm.chat(messages)
                if answer:
                    break
            except Exception as e:
                if i == self.retry_limit - 1:
                    answer = f"LLMエラー: {str(e)}"

        trace.append({"step": 2, "answer_preview": answer[:100]})

        # ⑥ メモリ保存
        try:
            self.memory.add(f"Q: {query}\nA: {answer}")
        except Exception:
            pass

        # ⑦ 簡易スコア（改善用）
        reward = 1.0 if len(answer) > 20 else 0.3

        try:
            self.improver.log(query, action, {"final": answer}, reward)
        except Exception:
            pass

        return {
            "final": answer,
            "trace": trace
        }