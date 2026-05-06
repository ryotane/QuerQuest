from ai_agent.hermes.reactor import ReActEngine
from ai_agent.core.reflection import ReflectionEngine
from ai_agent.graph.tool_learning import ToolLearning
from ai_agent.agents.comm_graph import CommunicationGraph
from ai_agent.memory.vector_memory import VectorMemory


class EvolvingCore:

    def __init__(self):

        self.reactor = ReActEngine()
        self.reflection = ReflectionEngine()
        self.learning = ToolLearning()
        self.memory = VectorMemory()
        self.comm = CommunicationGraph()

    def run(self, question: str):

        # -------------------------
        # 1. Execute
        # -------------------------
        result = self.reactor.run(question)

        # -------------------------
        # 2. Reflection
        # -------------------------
        reflection = self.reflection.analyze(question, result)

        # -------------------------
        # 3. Memory update
        # -------------------------
        self.memory.add(question, result)

        # -------------------------
        # 4. Tool learning update
        # -------------------------
        plan = result.get("plan", [])
        self.learning.update(plan, reflection)

        # -------------------------
        # 5. Multi-agent communication
        # -------------------------
        comm = self.comm.exchange(question, {
            "reactor": result,
            "reflection": reflection
        })

        # -------------------------
        # FINAL OUTPUT
        # -------------------------
        return {
            "result": result,
            "reflection": reflection,
            "memory_size": len(self.memory.store),
            "tool_weights": self.learning.weights,
            "communication": comm
        }