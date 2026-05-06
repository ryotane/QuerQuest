# ai_agent/agents/planner_agent.py

from ai_agent.llm.lmstudio import LMStudioClient


class PlannerAgent:

    def __init__(self):
        self.llm = LMStudioClient()

    def run(self, query: str):

        prompt = f"""
次のタスクをステップに分解してください。

タスク:
{query}

出力形式:
- ステップ1
- ステップ2
- ステップ3
"""

        response = self.llm.chat([
            {"role": "user", "content": prompt}
        ])

        # 雑パース（まずはOK）
        lines = [l.strip("- ").strip() for l in response.split("\n") if l.strip()]

        return {
            "plan": lines
        }