class RewardSystem:

    def compute(self, reflection):

        score = reflection.get("score", 0)

        # success bonus
        if reflection["status"] == "success":
            reward = 1.0 + score

        elif reflection["status"] == "partial":
            reward = 0.5 * score

        else:
            reward = -0.5

        return reward