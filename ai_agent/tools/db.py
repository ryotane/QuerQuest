import chromadb
from sentence_transformers import SentenceTransformer

client = chromadb.Client()
collection = client.get_or_create_collection("docs")

model = SentenceTransformer("all-MiniLM-L6-v2")


def split_text(text, size=500):
    return [text[i:i+size] for i in range(0, len(text), size)]


def save_document(text, source):
    chunks = split_text(text)

    for i, chunk in enumerate(chunks):
        emb = model.encode(chunk).tolist()

        collection.add(
            embeddings=[emb],
            documents=[chunk],
            ids=[f"{source}_{i}"]
        )


def search(query):
    emb = model.encode(query).tolist()

    return collection.query(
        query_embeddings=[emb],
        n_results=5
    )