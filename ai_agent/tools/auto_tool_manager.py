import os
import importlib


class AutoToolManager:

    def __init__(self):
        self.folder = "ai_agent/tools/generated"
        os.makedirs(self.folder, exist_ok=True)
        self.tools = {}
        self.load_tools()

    def load_tools(self):

        self.tools = {}

        for file in os.listdir(self.folder):
            if file.endswith(".py"):

                name = file[:-3]
                module_path = f"ai_agent.tools.generated.{name}"

                try:
                    module = importlib.import_module(module_path)
                    importlib.reload(module)

                    if hasattr(module, "Tool"):
                        self.tools[name] = module.Tool()

                except Exception as e:
                    print("❌ Tool load error:", e)

        print("🔧 Loaded tools:", list(self.tools.keys()))

    def get_tools(self):
        return self.tools