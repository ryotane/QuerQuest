from ai_agent.llm.lmstudio import LMStudioClient

class ToolRouter:

    def __init__(self):
        self.llm = LMStudioClient()

    def choose_tool(self, query, tools):

        tool_list = ", ".join(tools.keys())

        prompt = f"""
ユーザーの質問に最適なツールを1つ選んでください。

ツール一覧:
{tool_list}

質問:
{query}

ツール名のみ答えてください。
"""

        res = self.llm.chat([
            {"role": "user", "content": prompt}
        ]).lower()

        for t in tools:
            if t in res:
                return t

        return "llm"