import os


class AutoToolGenerator:

    def __init__(self):
        self.folder = "ai_agent/tools/generated"
        os.makedirs(self.folder, exist_ok=True)

    def create_tool(self, name: str, code: str):

        path = os.path.join(self.folder, f"{name}.py")

        with open(path, "w", encoding="utf-8") as f:
            f.write(code)

        print("🛠 Tool生成:", path)