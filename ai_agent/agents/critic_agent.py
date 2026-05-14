class CriticAgent:
    """
    出力の品質チェック・自己評価
    """

    def run(self, result: dict):

        score = 1.0

        if isinstance(result, dict) and result.get("ok") is False:
            score -= 0.5

        if "error" in str(result):
            score -= 0.3

        return {
            "agent": "critic",
            "score": score,
            "feedback": "ok" if score > 0.7 else "needs improvement"
        }