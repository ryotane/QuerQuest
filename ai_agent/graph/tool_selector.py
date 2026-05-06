class ToolSelector:

    def __init__(self):

        self.weights = {
            "search": 1.0,
            "xcode": 1.0,
            "memory": 1.0,
            "vision": 1.0
        }

    def select(self, question: str):

        q = question.lower()

        if "コード" in q or "xcode" in q:
            return ["xcode", "memory"]

        if "画像" in q:
            return ["vision"]

        return ["search", "memory"]

    def reward(self, tools, score):

        for t in tools:
            self.weights[t] += score * 0.01