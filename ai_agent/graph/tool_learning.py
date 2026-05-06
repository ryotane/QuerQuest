class ToolLearning:

    def __init__(self):

        self.weights = {
            "search": 1.0,
            "xcode": 1.0,
            "memory": 1.0,
            "vision": 1.0
        }

    def update(self, plan, reflection):

        score = reflection["score"]

        for tool in plan:

            if tool in self.weights:

                # 成功 → 強化 / 失敗 → 弱化
                self.weights[tool] += (score - 0.5) * 0.1

                # clamp
                self.weights[tool] = max(0.1, min(2.0, self.weights[tool]))

    def select(self, question, planner_output):

        # weighted selection
        sorted_tools = sorted(
            planner_output,
            key=lambda t: self.weights.get(t, 1.0),
            reverse=True
        )

        return sorted_tools