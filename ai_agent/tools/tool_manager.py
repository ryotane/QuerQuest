import os
import importlib


class ToolManager:

    def __init__(self, memory):
        self.memory = memory
        self.folder = "ai_agent/tools/generated"
        os.makedirs(self.folder, exist_ok=True)
        self.tools = {}
        self.load()

    def load(self):
        self.tools = {}

        for f in os.listdir(self.folder):
            if f.endswith(".py"):
                name = f[:-3]

                module = importlib.import_module(f"ai_agent.tools.generated.{name}")
                importlib.reload(module)

                if hasattr(module, "Tool"):
                    self.tools[name] = module.Tool()

    def rank(self):
        scored = []

        for name in self.tools:
            score = self.memory.get_tool_score(name)
            scored.append((name, score))

        return sorted(scored, key=lambda x: x[1], reverse=True)

    def get_best(self):
        ranked = self.rank()
        return ranked[0][0] if ranked else None