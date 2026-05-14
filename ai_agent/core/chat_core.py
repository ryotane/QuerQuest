from ai_agent.memory.vector_memory import VectorMemory
from ai_agent.hermes.reactor import ReActEngine
from ai_agent.self_improve.improver import SelfImprover
from ai_agent.agents.debate import DebateAgent


class ChatCore:

    def __init__(self):

        self.engine = ReActEngine()
        self.memory = VectorMemory()
        self.improver = SelfImprover()
        self.debate = DebateAgent()

    def run(self, question: str):

        # -------------------------
        # 1. Memory retrieve
        # -------------------------
        memories = self.memory.search(question)

        # -------------------------
        # 2. ReAct execution
        # -------------------------
        result = self.engine.run(question)

        # -------------------------
        # 3. Debate (validation)
        # -------------------------
        verdict = self.debate.debate(question, result)

        # -------------------------
        # 4. Memory store
        # -------------------------
        self.memory.add(question, {"result": result})

        # -------------------------
        # 5. Self improve log
        # -------------------------
        score = 1.0 if verdict["verdict"] == "approve" else 0.3
        self.improver.log(question, result.get("plan"), result, score)

        # -------------------------
        # FINAL OUTPUT
        # -------------------------
        return {
            "result": result,
            "memory": memories,
            "debate": verdict
        }