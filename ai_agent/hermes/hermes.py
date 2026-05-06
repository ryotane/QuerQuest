class Hermes:

    def think(self, question: str):

        q = question.lower()

        if "京都" in q or "調べ" in q:
            return {"intent": "research"}

        if "xcode" in q:
            return {"intent": "dev"}

        return {"intent": "general"}