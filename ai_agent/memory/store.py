import chromadb

client = chromadb.Client()
collection = client.get_or_create_collection("memory")


def save_memory(text: str, meta: dict):
    collection.add(
        documents=[text],
        metadatas=[meta],
        ids=[str(hash(text))]
    )


def search_memory(query: str):
    return collection.query(
        query_texts=[query],
        n_results=5
    )