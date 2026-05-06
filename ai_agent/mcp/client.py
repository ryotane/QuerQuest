from ai_agent.mcp.http_client import MCPHTTPClient

client = MCPHTTPClient()


def run_mcp(command: list):

    tool = command[1] if len(command) > 1 else ""
    query = command[2] if len(command) > 2 else ""

    # -------------------------
    # SEARCH
    # -------------------------
    if tool == "search":
        return client.search(query)

    # -------------------------
    # XCODE（仮HTTP化）
    # -------------------------
    if tool == "xcode":
        return {
            "ok": True,
            "note": "xcode http gateway not implemented yet"
        }

    return {
        "ok": False,
        "error": "unknown_tool",
        "command": command
    }