import json
import os
from datetime import datetime


class SuccessLogger:

    def __init__(self, path="logs/improvement.jsonl"):
        self.path = path
        os.makedirs("logs", exist_ok=True)

    def log(self, question, plan, result, score):

        record = {
            "question": question,
            "plan": plan,
            "result": result,
            "score": score,
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")