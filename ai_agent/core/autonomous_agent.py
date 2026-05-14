from ai_agent.core.evolving_core import EvolvingCore
from ai_agent.core.reflection import ReflectionEngine
from ai_agent.core.reward import RewardSystem
from ai_agent.core.rl_loop import RLLearningLoop
from ai_agent.core.goal_generator import GoalGenerator
from ai_agent.core.loop_control import LoopController
from ai_agent.memory.memory_manager import MemoryManager
from ai_agent.utils.timeout import run_with_timeout, TimeoutException


class AutonomousAgent:

    def __init__(self):

        self.core = EvolvingCore()
        self.reflection = ReflectionEngine()
        self.reward_system = RewardSystem()
        self.rl = RLLearningLoop()
        self.goal_gen = GoalGenerator()
        self.loop = LoopController(max_steps=5)
        self.memory_manager = MemoryManager(self.core.memory)

    def run(self, initial_goal: str):

        goal = initial_goal
        history = []

        step = 0

        while True:

            try:
                # -------------------------
                # 1. Execute with timeout
                # -------------------------
                result = run_with_timeout(
                    lambda: self.core.run(goal),
                    seconds=5
                )

            except TimeoutException:
                result = {"error": "timeout"}

            # -------------------------
            # 2. Reflect
            # -------------------------
            reflection = self.reflection.analyze(goal, result)

            # -------------------------
            # 3. Reward
            # -------------------------
            reward = self.reward_system.compute(reflection)

            # -------------------------
            # 4. Learn
            # -------------------------
            plan = result.get("result", {}).get("plan", [])
            self.rl.update(self.core.learning, plan, reward)

            # -------------------------
            # 5. Save history
            # -------------------------
            history.append({
                "step": step,
                "goal": goal,
                "reflection": reflection,
                "reward": reward
            })

            # -------------------------
            # 6. Memory control
            # -------------------------
            self.memory_manager.compress()

            # -------------------------
            # 7. Stop condition
            # -------------------------
            if not self.loop.should_continue(step, reflection):
                break

            # -------------------------
            # 8. Next goal
            # -------------------------
            goal = self.goal_gen.generate(result)

            step += 1

        return {
            "steps": history,
            "final_weights": self.core.learning.weights,
            "memory_size": len(self.core.memory.store)
        }