from ai_agent.llm.lmstudio import LMStudioClient

class DebateSystem:

    def __init__(self):
        self.llm = LMStudioClient()

    def run(self, query):

        pro = self.llm.chat([
            {"role": "user", "content": f"{query}について賛成意見を述べて"}
        ])

        con = self.llm.chat([
            {"role": "user", "content": f"{query}について反対意見を述べて"}
        ])

        judge = self.llm.chat([
            {"role": "user", "content": f"""
以下を統合して最適な結論を出してください。

賛成:
{pro}

反対:
{con}
"""}
        ])

        return {
            "pro": pro,
            "con": con,
            "final": judge
        }