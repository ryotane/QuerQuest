"""
PDF RAGモジュール
PDFをロードしてFAISSに保存、検索できる
"""
import os
import json
import requests
import numpy as np

try:
    import faiss
    FAISS_OK = True
except ImportError:
    FAISS_OK = False

try:
    import pdfplumber
    PDF_OK = True
except ImportError:
    PDF_OK = False


STORE_PATH = "/tmp/queryquest_rag_store.json"


class PDFRag:

    def __init__(self, embed_url="http://localhost:1234/v1"):
        self.embed_url = embed_url
        self.texts = []
        self.index = None
        self._load_store()

        if FAISS_OK and len(self.texts) > 0:
            self._rebuild_index()

    def _load_store(self):
        """保存済みのテキストを読み込む"""
        if os.path.exists(STORE_PATH):
            try:
                with open(STORE_PATH, "r") as f:
                    self.texts = json.load(f)
            except Exception:
                self.texts = []

    def _save_store(self):
        """テキストを保存する"""
        try:
            with open(STORE_PATH, "w") as f:
                json.dump(self.texts, f, ensure_ascii=False)
        except Exception:
            pass

    def _rebuild_index(self):
        """FAISSインデックスを再構築"""
        if not FAISS_OK or not self.texts:
            return
        vecs = [self._embed(t) for t in self.texts]
        dim = len(vecs[0])
        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(vecs).astype("float32"))

    def _embed(self, text: str):
        """LM Studioのembeddingを使う"""
        try:
            r = requests.post(
                f"{self.embed_url}/embeddings",
                json={
                    "model": "text-embedding-nomic-embed-text-v1.5",
                    "input": text[:500]
                },
                timeout=10
            )
            return np.array(r.json()["data"][0]["embedding"]).astype("float32")
        except Exception:
            return np.zeros(768).astype("float32")

    def load_pdf(self, pdf_path: str):
        """PDFをロードしてRAGに追加"""
        if not PDF_OK:
            return {"ok": False, "error": "pdfplumber未インストール"}

        if not os.path.exists(pdf_path):
            return {"ok": False, "error": f"ファイルが見つかりません: {pdf_path}"}

        try:
            chunks = []
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    text = page.extract_text() or ""
                    # 500文字ごとにチャンク
                    for i in range(0, len(text), 500):
                        chunk = text[i:i+500].strip()
                        if chunk:
                            chunks.append(chunk)

            self.texts.extend(chunks)
            self._save_store()
            self._rebuild_index()

            return {"ok": True, "chunks": len(chunks)}

        except Exception as e:
            return {"ok": False, "error": str(e)}

    def add_text(self, text: str):
        """テキストを直接追加"""
        chunks = [text[i:i+500] for i in range(0, len(text), 500)]
        self.texts.extend(chunks)
        self._save_store()
        self._rebuild_index()

    def search(self, query: str, k: int = 3):
        """クエリに近いテキストを検索"""
        if not FAISS_OK or self.index is None or not self.texts:
            return []

        try:
            qv = self._embed(query)
            D, I = self.index.search(np.array([qv]), k)
            return [self.texts[i] for i in I[0] if i < len(self.texts)]
        except Exception:
            return []

    def clear(self):
        """全データを削除"""
        self.texts = []
        self.index = None
        if os.path.exists(STORE_PATH):
            os.remove(STORE_PATH)
