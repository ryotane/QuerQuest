class ToolSelector:

    def __init__(self):

        self.stats = {
            "search": 1.0,
            "code": 1.0
        }

    def update(self, tool, success: bool):

        if tool not in self.stats:
            self.stats[tool] = 1.0

        if success:
            self.stats[tool] *= 1.05
        else:
            self.stats[tool] *= 0.95

    def select(self, context: str):

        if "xcode" in context:
            return "code"

        return max(self.stats, key=self.stats.get)