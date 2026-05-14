class Planner:

    def plan(self, question: str):

        q = question.lower()

        # -----------------------
        # SEARCH系
        # -----------------------
        if any(w in q for w in ["調べ", "検索", "京都", "とは"]):
            return ["search", "memory"]

        # -----------------------
        # CODE系
        # -----------------------
        if "xcode" in q or "build" in q:
            return ["xcode", "memory"]

        # -----------------------
        # IMAGE/vision系
        # -----------------------
        if "画像" in q:
            return ["vision"]

        # fallback
        return ["search"]