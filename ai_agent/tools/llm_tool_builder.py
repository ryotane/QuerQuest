from ai_agent.hermes.reactor import ReActEngine


class LLMToolBuilder:

    def __init__(self):
        self.llm = ReActEngine()

    def generate(self, query):

        prompt = f"""
Pythonで実行可能なツールを作れ。

要件:
{query}

制約:
- class Tool
- run(self, query)
- return dict {{ok, result}}
- エラー処理必須
- requests使用OK
"""

        res = self.llm.run(prompt)
        return res.get("final", "")