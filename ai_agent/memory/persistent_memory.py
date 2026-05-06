import sqlite3
import chromadb
from sentence_transformers import SentenceTransformer


class PersistentMemory:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")

        # Chroma
        self.chroma = chromadb.Client()
        self.collection = self.chroma.get_or_create_collection("rag")

        # SQLite
        self.conn = sqlite3.connect("memory.db")
        self._init_db()

    def _init_db(self):
        cur = self.conn.cursor()

        cur.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            query TEXT,
            answer TEXT
        )
        """)

        cur.execute("""
        CREATE TABLE IF NOT EXISTS tool_stats (
            name TEXT PRIMARY KEY,
            success INTEGER,
            fail INTEGER
        )
        """)

        self.conn.commit()

    # ----------------
    # RAG
    # ----------------
    def add(self, text, meta=None):
        emb = self.model.encode([text])[0].tolist()

        self.collection.add(
            embeddings=[emb],
            documents=[text],
            metadatas=[meta or {}],
            ids=[str(hash(text))]
        )

    def search(self, query, k=5):
        emb = self.model.encode([query])[0].tolist()

        res = self.collection.query(
            query_embeddings=[emb],
            n_results=k
        )

        out = []
        for i in range(len(res["documents"][0])):
            out.append({
                "text": res["documents"][0][i],
                "score": res["distances"][0][i]
            })

        return out

    # ----------------
    # 履歴
    # ----------------
    def save_history(self, q, a):
        cur = self.conn.cursor()
        cur.execute("INSERT INTO history(query, answer) VALUES (?,?)", (q, a))
        self.conn.commit()

    # ----------------
    # Tool評価
    # ----------------
    def update_tool(self, name, success=True):
        cur = self.conn.cursor()

        cur.execute("SELECT * FROM tool_stats WHERE name=?", (name,))
        row = cur.fetchone()

        if not row:
            cur.execute("INSERT INTO tool_stats VALUES (?,?,?)",
                        (name, int(success), int(not success)))
        else:
            if success:
                cur.execute("UPDATE tool_stats SET success=success+1 WHERE name=?", (name,))
            else:
                cur.execute("UPDATE tool_stats SET fail=fail+1 WHERE name=?", (name,))

        self.conn.commit()

    def get_tool_score(self, name):
        cur = self.conn.cursor()
        cur.execute("SELECT success, fail FROM tool_stats WHERE name=?", (name,))
        row = cur.fetchone()

        if not row:
            return 0.5

        s, f = row
        return s / (s + f + 1)