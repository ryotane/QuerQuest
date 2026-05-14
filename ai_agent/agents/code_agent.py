from ai_agent.mcp.router import route_mcp


class CodeAgent:
    """
    開発・Xcode・コード関連Agent
    """

    def run(self, query: str):

        if "xcode" in query.lower() or "build" in query.lower():
            result = route_mcp("xcode build status")
        else:
            result = {
                "ok": True,
                "stdout": "CodeAgent: no matching dev task"
            }

        return {
            "agent": "code",
            "query": query,
            "result": result
        }