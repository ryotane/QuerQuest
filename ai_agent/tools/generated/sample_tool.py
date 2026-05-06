class Tool:

    def run(self, query):
        return {
            "ok": True,
            "result": f"Tool実行結果: {query}"
        }