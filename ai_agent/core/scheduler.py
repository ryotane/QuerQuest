import time
from ai_agent.hermes.orchestrator import Orchestrator


class Scheduler:

    def __init__(self):
        self.orch = Orchestrator()

    def run(self):

        print("🤖 AutoGPT 起動")

        while True:
            task = "最新AIニュースを収集して要約"

            res = self.orch.run(task)

            print("🧠", task)
            print("✅", res)

            time.sleep(60)