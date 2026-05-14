import time
from ai_agent.hermes.orchestrator import Orchestrator


class AutoGPT:

    def __init__(self):
        self.orch = Orchestrator()

    def run(self):

        print("🤖 AutoGPT 起動")

        task = "最新AIニュースを調査してまとめる"

        while True:

            print("🧠 タスク:", task)

            result = self.orch.run(task)

            print("✅", result["final"][:200])

            # 次タスク生成（簡易）
            task = f"次にやるべきこと: {result['final'][:100]}"

            time.sleep(5)