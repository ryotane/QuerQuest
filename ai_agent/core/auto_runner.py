import time
from ai_agent.hermes.orchestrator import Orchestrator

class AutoRunner:

    def __init__(self):
        self.orch = Orchestrator()

    def loop(self):

        while True:
            task = self.generate_task()

            print("🧠 AutoTask:", task)

            result = self.orch.run(task)

            print("✅ Result:", result.get("final"))

            time.sleep(15)

    def generate_task(self):
        return "最新のAIニュースを調べて要約して"