from typing import List, Tuple, Dict, Any
import os

import chromadb
from chromadb.config import Settings as ChromaSettings
from openai import OpenAI


def get_chroma_client(persist_dir: str = ".chroma"):
    os.makedirs(persist_dir, exist_ok=True)
    client = chromadb.PersistentClient(path=persist_dir, settings=ChromaSettings(is_persistent=True))
    return client


def get_collection(client, name: str):
    return client.get_or_create_collection(name=name, metadata={"hnsw:space": "cosine"})


def upsert_documents(collection, docs: List[Tuple[str, str]], embed_model: str = "text-embedding-3-small") -> int:
    if not docs:
        return 0
    client = OpenAI()
    texts = [text for _url, text in docs]
    ids = [str(i) for i in range(collection.count(), collection.count() + len(docs))]
    metadatas = [{"source_url": url} for url, _ in docs]

    # Batch embed to respect token limits
    embeddings: List[List[float]] = []
    batch_size = 64
    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        resp = client.embeddings.create(model=embed_model, input=batch)
        embeddings.extend([d.embedding for d in resp.data])

    collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=texts)
    return len(ids)


def query_similar(collection, query: str, k: int = 5, embed_model: str = "text-embedding-3-small") -> List[Dict[str, Any]]:
    client = OpenAI()
    resp = client.embeddings.create(model=embed_model, input=[query])
    embedding = resp.data[0].embedding
    results = collection.query(query_embeddings=[embedding], n_results=k, include=["metadatas", "distances", "documents"])
    items: List[Dict[str, Any]] = []
    for doc, meta, dist in zip(results.get("documents", [[]])[0], results.get("metadatas", [[]])[0], results.get("distances", [[]])[0]):
        items.append({"document": doc, "metadata": meta, "distance": float(dist)})
    return items


