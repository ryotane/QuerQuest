import numpy as np
from sentence_transformers import SentenceTransformer
from rank_bm25 import BM25Okapi
from janome.tokenizer import Tokenizer


class HybridMemory:

    def __init__(self):
        print("🧠 HybridMemory 初期化")

        self.embed_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.rerank_model = SentenceTransformer("all-MiniLM-L6-v2")

        self.texts = []
        self.embeddings = []
        self.metas = []

        self.tokenizer = Tokenizer()
        self.bm25 = None

    # =========================
    # chunk分割
    # =========================
    def chunk_text(self, text, size=300, overlap=50):
        chunks = []
        start = 0

        while start < len(text):
            chunk = text[start:start+size]
            chunks.append(chunk)
            start += size - overlap

        return chunks

    # =========================
    # tokenize
    # =========================
    def tokenize(self, text):
        return [t.surface for t in self.tokenizer.tokenize(text)]

    # =========================
    # add
    # =========================
    def add(self, text, meta=None):

        chunks = self.chunk_text(text)

        for c in chunks:
            emb = self.embed_model.encode(c)

            self.texts.append(c)
            self.embeddings.append(emb)
            self.metas.append(meta or {})

        tokenized = [self.tokenize(t) for t in self.texts]
        self.bm25 = BM25Okapi(tokenized)

    # =========================
    # normalize
    # =========================
    def normalize(self, arr):
        if max(arr) == min(arr):
            return arr
        return [(x - min(arr)) / (max(arr) - min(arr)) for x in arr]

    # =========================
    # multi query（検索強化）
    # =========================
    def expand_query(self, query):
        return [
            query,
            f"{query}とは",
            f"{query}について",
            f"{query} 解説",
        ]

    # =========================
    # search
    # =========================
    def search(self, query, k=5):

        if not self.texts:
            return []

        queries = self.expand_query(query)

        total_scores = np.zeros(len(self.texts))

        for q in queries:

            # --- embedding ---
            q_emb = self.embed_model.encode(q)

            sims = np.dot(self.embeddings, q_emb) / (
                np.linalg.norm(self.embeddings, axis=1) * np.linalg.norm(q_emb)
            )
            sims = self.normalize(sims.tolist())

            # --- BM25 ---
            tokens = self.tokenize(q)
            bm25_scores = self.bm25.get_scores(tokens)
            bm25_scores = self.normalize(bm25_scores.tolist())

            for i in range(len(self.texts)):
                total_scores[i] += 0.5 * sims[i] + 0.5 * bm25_scores[i]

        total_scores = total_scores / len(queries)

        # 初期候補
        results = []
        for i in range(len(self.texts)):
            results.append({
                "text": self.texts[i],
                "meta": self.metas[i],
                "score": float(total_scores[i])
            })

        results.sort(key=lambda x: x["score"], reverse=True)
        top = results[:k*2]

        # =========================
        # rerank（最強）
        # =========================
        q_emb = self.rerank_model.encode(query)

        for r in top:
            emb = self.rerank_model.encode(r["text"])
            score = np.dot(q_emb, emb) / (
                np.linalg.norm(q_emb) * np.linalg.norm(emb)
            )
            r["score"] = float(score)

        top.sort(key=lambda x: x["score"], reverse=True)

        return top[:k]


_memory = None


def get_memory():
    global _memory
    if _memory is None:
        _memory = HybridMemory()
    return _memory