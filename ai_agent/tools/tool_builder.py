from ai_agent.llm.lmstudio import LMStudioClient

class ToolBuilder:

    def __init__(self):
        self.llm = LMStudioClient()

    def generate(self, task):

        prompt = f"""
Pythonでツール関数を書いてください。

タスク:
{task}

def run(query): の形式で出力
"""

        code = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        return code