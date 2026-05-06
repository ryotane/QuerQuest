import json
import os

class SelfImprover:

    def __init__(self, path="logs/improve.jsonl"):
        self.path = path
        os.makedirs("logs", exist_ok=True)

    def log(self, question, plan, result, score):

        entry = {
            "q": question,
            "plan": plan,
            "score": score
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def analyze(self):

        if not os.path.exists(self.path):
            return {}

        scores = []

        with open(self.path, "r") as f:
            for line in f:
                scores.append(json.loads(line))

        return {
            "total": len(scores),
            "avg_score": sum(s.get("score", 0) for s in scores) / max(len(scores), 1)
        }

# 既存クラスのインスタンスキャッシュ（オプション）
_instance = None
def _get_instance():
    global _instance
    if _instance is None:
        _instance = YourExistingClass()
    return _instance