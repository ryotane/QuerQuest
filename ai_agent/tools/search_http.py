import requests
import time

SEARXNG_URL = "http://127.0.0.1:8888/search"

def search(query: str, timeout=5):
    try:
        start = time.time()

        res = requests.get(
            SEARXNG_URL,
            params={
                "q": query,
                "format": "json"
            },
            timeout=timeout
        )

        data = res.json()

        results = []
        for r in data.get("results", [])[:5]:
            results.append({
                "title": r.get("title"),
                "url": r.get("url"),
                "content": r.get("content")
            })

        return {
            "ok": True,
            "type": "search_result",
            "query": query,
            "results": results,
            "elapsed": time.time() - start
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e)
        }