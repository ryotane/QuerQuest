class RLLearningLoop:

    def update(self, tool_learning, plan, reward):

        for tool in plan:

            if tool in tool_learning.weights:

                # 強化学習的更新
                tool_learning.weights[tool] += reward * 0.05

                # 安定化
                tool_learning.weights[tool] = max(0.1, min(3.0, tool_learning.weights[tool]))