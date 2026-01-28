import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text:latest")


def ollama_embed(text: str) -> list[float]:
    r = requests.post(
        f"{BASE_URL}/api/embeddings",
        json={"model": EMBED_MODEL, "prompt": text},
        timeout=180,
    )
    r.raise_for_status()
    data = r.json()
    emb = data.get("embedding")
    if not emb or not isinstance(emb, list):
        raise RuntimeError(f"Invalid embeddings response: {data}")
    return emb
