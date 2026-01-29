import os
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
MODEL = os.getenv("OLLAMA_MODEL", "llama3.1")


def ollama_generate(prompt: str) -> str:
    r = requests.post(
        f"{BASE_URL}/api/generate",
        json={"model": MODEL, "prompt": prompt, "stream": False},
        timeout=180,
    )
    r.raise_for_status()
    return (r.json().get("response") or "").strip()
