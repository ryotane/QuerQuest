class Reflexion:

    def improve(self, trace: dict):

        score = trace.get("feedback", {}).get("score", 0)

        if score < 0.7:

            return {
                "action": "retry",
                "reason": "low score"
            }

        return {
            "action": "accept",
            "reason": "good output"
        }