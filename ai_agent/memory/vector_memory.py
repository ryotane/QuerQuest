# ai_agent/memory/vector_memory.py

import numpy as np
from sentence_transformers import SentenceTransformer


class VectorMemory:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.texts = []
        self.vectors = []
        self.metas = []

    def add(self, text, meta=None):

        if not text or not text.strip():
            return

        vec = self.model.encode([text])[0]

        self.texts.append(text)
        self.vectors.append(vec)
        self.metas.append(meta or {})

    def search(self, query, k=3):

        if not self.texts:
            return []

        q_vec = self.model.encode([query])[0]

        sims = []
        for i, v in enumerate(self.vectors):
            score = np.dot(q_vec, v) / (
                np.linalg.norm(q_vec) * np.linalg.norm(v) + 1e-8
            )
            sims.append((score, i))

        sims.sort(reverse=True)

        results = []
        for score, i in sims[:k]:
            results.append({
                "text": self.texts[i],
                "meta": self.metas[i],
                "score": float(score)
            })

        return results


# =========================
# 🔥 共有メモリ（重要）
# =========================
_global_memory = None


def get_memory():
    global _global_memory
    if _global_memory is None:
        print("🧠 VectorMemory 初期化")
        _global_memory = VectorMemory()
    return _global_memory