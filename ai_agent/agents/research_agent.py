from ai_agent.mcp.router import route_mcp


class ResearchAgent:
    """
    Web検索・外部情報取得専用Agent
    """

    def run(self, query: str):
        result = route_mcp(f"検索 {query}")

        return {
            "agent": "research",
            "query": query,
            "result": result
        }