from ai_agent.llm.lmstudio import LMStudioClient
from ai_agent.memory.vector_memory import VectorMemory
from ai_agent.router.semantic_router import SemanticToolRouter


class ReActEngine:

    def __init__(self):
        self.llm = LMStudioClient()
        self.memory = VectorMemory()
        self.router = SemanticToolRouter()

    def run(self, query: str):
        """シンプルな単発クエリ実行"""
        messages = [
            {"role": "system", "content": "あなたは親切なAIアシスタントです。日本語で自然に答えてください。"},
            {"role": "user", "content": query}
        ]
        return self.run_messages(messages)

    def run_messages(self, messages: list):
        """会話履歴付きで実行（orchestratorから呼ばれる）"""
        try:
            answer = self.llm.chat(messages)
        except Exception as e:
            answer = f"LLMエラー: {str(e)}"

        return {
            "final": answer
        }
