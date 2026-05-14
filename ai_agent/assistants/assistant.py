from ai_agent.hermes.reactor import ReActEngine
from ai_agent.memory.memory import save_memory

class Assistant:

    def __init__(self):
        self.engine = ReActEngine()

    def run(self, message: str):
        result = self.engine.run(message)

        save_memory({
            "query": message,
            "result": result
        })

        return result