from ai_agent.tools.search_http import search

def route_mcp(query: str):
    if "調べて" in query or "検索" in query:
        return search(query)

    if "xcode" in query:
        return {
            "ok": True,
            "type": "xcode",
            "data": "mock xcode status"
        }

    return {
        "ok": False,
        "error": "no_tool"
    }