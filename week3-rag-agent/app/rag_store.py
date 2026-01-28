import os
import uuid
from typing import Any

import chromadb
from chromadb.config import Settings

from .llm_ollama_embeddings import ollama_embed
import hashlib

PERSIST_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".chroma"))
COLLECTION_NAME = "knowledge_base"

_client = chromadb.PersistentClient(
    path=PERSIST_DIR,
    settings=Settings(anonymized_telemetry=False),
)
_collection = _client.get_or_create_collection(name=COLLECTION_NAME)


def ingest_text(text: str, source: str = "manual") -> str:
    clean = " ".join((text or "").split()).strip()
    if not clean:
        raise ValueError("text cannot be empty")

    # deterministic id => same text+source won't be duplicated
    h = hashlib.sha256((source + "||" + clean).encode("utf-8")).hexdigest()[:24]
    doc_id = f"{source}-{h}"

    # check if exists
    existing = _collection.get(ids=[doc_id])
    if existing and existing.get("ids"):
        return doc_id

    emb = ollama_embed(clean)
    _collection.add(
        ids=[doc_id],
        embeddings=[emb],
        documents=[clean],
        metadatas=[{"source": source}],
    )
    return doc_id


def retrieve(query: str, top_k: int = 3) -> list[dict[str, Any]]:
    q_emb = ollama_embed(query)

    res = _collection.query(
        query_embeddings=[q_emb],
        n_results=top_k,
        include=["documents", "metadatas", "distances"],
    )

    docs = (res.get("documents") or [[]])[0]
    metas = (res.get("metadatas") or [[]])[0]
    dists = (res.get("distances") or [[]])[0]

    out = []
    seen = set()
    for doc, meta, dist in zip(docs, metas, dists):
        key = (meta.get("source"), doc)
        if key in seen:
            continue
        seen.add(key)
        out.append({"text": doc, "meta": meta, "distance": dist})
    return out
