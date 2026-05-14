import requests


class MCPHTTPClient:

    def __init__(self):
        self.searxng_url = "http://127.0.0.1:8888/search"

    def search(self, query: str):

        try:
            res = requests.get(
                self.searxng_url,
                params={"q": query},
                timeout=10
            )

            return {
                "ok": True,
                "data": res.json() if res.headers.get("content-type") == "application/json" else res.text
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e),
                "query": query
            }