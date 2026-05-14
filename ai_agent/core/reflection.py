class ReflectionEngine:

    def analyze(self, question, result):

        score = 1.0
        issues = []

        # -------------------------
        # failure detection
        # -------------------------
        if isinstance(result, dict):

            if result.get("error"):
                score -= 0.5
                issues.append("tool_error")

            if not result.get("execution"):
                score -= 0.3
                issues.append("no_execution")

        # -------------------------
        # success heuristics
        # -------------------------
        if score > 0.8:
            status = "success"
        elif score > 0.4:
            status = "partial"
        else:
            status = "fail"

        return {
            "score": score,
            "status": status,
            "issues": issues
        }