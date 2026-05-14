import chromadb
from sentence_transformers import SentenceTransformer


class Memory:

    def __init__(self):
        self.client = chromadb.Client()
        self.collection = self.client.get_or_create_collection("memory")
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

    def save(self, text: str, meta: str = ""):
        emb = self.model.encode(text).tolist()

        self.collection.add(
            embeddings=[emb],
            documents=[text],
            ids=[meta + "_" + str(hash(text))]
        )

    def search(self, query: str, k: int = 5):
        emb = self.model.encode(query).tolist()

        return self.collection.query(
            query_embeddings=[emb],
            n_results=k
        )

    def format_context(self, query: str):
        res = self.search(query)

        docs = res.get("documents", [[]])[0]

        return "\n".join(docs)