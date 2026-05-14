import json
import os
from datetime import datetime


class MemoryStore:
    """
    超シンプル永続メモリ（JSONベース）
    """

    def __init__(self, path="memory.jsonl"):
        self.path = path

    def save(self, key: str, value: dict):

        record = {
            "key": key,
            "value": value,
            "timestamp": datetime.utcnow().isoformat()
        }

        with open(self.path, "a") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def search(self, keyword: str):

        if not os.path.exists(self.path):
            return []

        results = []

        with open(self.path, "r") as f:
            for line in f:
                try:
                    data = json.loads(line)
                    if keyword in json.dumps(data, ensure_ascii=False):
                        results.append(data)
                except:
                    continue

        return results