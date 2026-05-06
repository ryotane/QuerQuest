from ai_agent.mcp.router import route_mcp


class ToolNode:

    def __init__(self, name, func):
        self.name = name
        self.func = func


class ToolGraph:

    def __init__(self):

        self.nodes = {
            "search": ToolNode("search", self.search),
            "xcode": ToolNode("xcode", self.xcode),
            "memory": ToolNode("memory", self.memory),
            "vision": ToolNode("vision", self.vision),
        }

    # -------------------------
    # EXEC UTILS
    # -------------------------
    def search(self, query):
        return route_mcp(f"検索 {query}")

    def xcode(self, query):
        return route_mcp(f"xcode {query}")

    def memory(self, query):
        return {
            "ok": True,
            "type": "memory",
            "data": f"[memory lookup] {query}"
        }

    def vision(self, query):
        return {
            "ok": True,
            "type": "vision",
            "data": f"[vision analysis] {query}"
        }

    # -------------------------
    # DAG EXECUTOR
    # -------------------------
    def run(self, plan: list, query: str):

        results = []

        for step in plan:

            if step not in self.nodes:
                continue

            node = self.nodes[step]
            result = node.func(query)

            results.append({
                "node": step,
                "result": result
            })

        return results