# ai_agent/router/semantic_router.py

from ai_agent.llm.lmstudio import LMStudioClient


class SemanticToolRouter:

    def __init__(self):
        self.llm = LMStudioClient()

    def route(self, query: str):

        prompt = f"""
次の質問を分類してください。

カテゴリ:
- chat（日常会話）
- search（調査・検索）
- code（プログラミング）
- complex（複雑処理・分析）

質問:
{query}

答えはカテゴリ名だけで。
"""

        try:
            res = self.llm.chat([
                {"role": "user", "content": prompt}
            ]).lower()

            if "search" in res:
                return "search"
            elif "code" in res:
                return "code"
            elif "complex" in res:
                return "complex"
            else:
                return "chat"

        except:
            return "chat"