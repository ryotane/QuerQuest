import json


class Optimizer:

    def analyze(self, log_path="logs/improvement.jsonl"):

        scores = []
        tasks = []

        try:
            with open(log_path, "r") as f:
                for line in f:
                    data = json.loads(line)

                    scores.append(data.get("score", 0))
                    tasks.append(data.get("task"))

        except FileNotFoundError:
            return {"status": "no_data"}

        avg_score = sum(scores) / len(scores) if scores else 0

        return {
            "avg_score": avg_score,
            "total": len(scores),
            "suggestion": "increase planner strictness" if avg_score < 0.6 else "stable"
        }