import uuid

import chromadb

from app.config import settings

_client = None
_collection = None


def get_collection():
    global _client, _collection
    if _collection is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        _collection = _client.get_or_create_collection(
            name=settings.chroma_collection,
            metadata={"hnsw:space": "cosine"},
        )
    return _collection


def add_chunks(texts: list[str], embeddings: list[list[float]], sources: list[str]) -> int:
    if not texts:
        return 0
    collection = get_collection()
    ids = [str(uuid.uuid4()) for _ in texts]
    metadatas = [{"source": s} for s in sources]
    collection.add(ids=ids, embeddings=embeddings, documents=texts, metadatas=metadatas)
    return len(ids)


def query(query_embedding: list[float], top_k: int) -> list[dict]:
    collection = get_collection()
    if collection.count() == 0:
        return []
    results = collection.query(query_embeddings=[query_embedding], n_results=min(top_k, collection.count()))

    hits = []
    docs = results.get("documents", [[]])[0]
    metas = results.get("metadatas", [[]])[0]
    distances = results.get("distances", [[]])[0]
    for doc, meta, dist in zip(docs, metas, distances):
        hits.append({"text": doc, "source": meta.get("source", "unknown"), "distance": dist})
    return hits