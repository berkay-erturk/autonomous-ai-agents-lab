# Week 3 – Local RAG Agent (Ollama + Chroma)

This project implements a **local Retrieval-Augmented Generation (RAG) agent** using **Ollama** for embeddings + LLM inference and **ChromaDB** as a persistent vector store.  
Goal: a **fully local**, **deterministic**, and **verifiable** RAG pipeline with strong guardrails against hallucination.

---

## Architecture

User Question
↓
Session Memory + Structured Facts
↓
Vector Retrieval (ChromaDB)
↓
Context Injection
↓
Local LLM (Ollama)
↓
Cited Answer / "Bilmiyorum."

### Design Principles

- **Local-first**: No external APIs
- **Deterministic ingest**: Same text + source does not create duplicates
- **Evidence-based answers**: Mandatory citations when using retrieved context
- **Hallucination-safe**: If the answer is not supported, respond with “Bilmiyorum.”

---

## Tech Stack

- Python **3.12**
- FastAPI
- Ollama (LLM + embeddings)
- ChromaDB (persistent vector DB)
- nomic-embed-text (embedding model)

---

## Core Features

- `/ingest/text`: idempotent text ingestion (hash-based IDs)
- `/ask`: answers using session memory + retrieved context
- `/rag/debug`: inspect retrieval hits and distances
- Guardrails:
  - If context is used → **must cite** `[1]`, `[2]`, ...
  - If context is missing/insufficient → **“Bilmiyorum.”**
- Duplicate prevention:
  - idempotent ingestion + retrieval dedupe

---

## Environment Variables

Example `.env`:

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:latest
OLLAMA_EMBED_MODEL=nomic-embed-text:latest
```

## Running Locally (Windows)

Activate venv and run:
- `.\.venv\Scripts\activate`
- `python -m uvicorn app.main:app --reload`

Swagger UI:

- http://127.0.0.1:8000/docs

## API Endpoints

**`POST /ingest/text`**
Ingests text into the vector store. The operation is idempotent.

- Request:

  ```JSON
  {
    "text": "Ecvatorline, bir e-ticaret satış mağazasıdır. Ürünler tedarikçilerden toptan alım yapılarak perakende satışa sunulur.",
    "source": "company-profile"
  }
  ```

- Response:
  ```JSON
  {
    "status": "ok",
    "id": "company-profile-<hash>",
    "source": "company-profile",
    "chars": 140
  }
  ```

**`POST /ask`**
Asks a question using session memory and retrieved context.

- Request:
  ```JSON
  {
    "session_id": "rag-1",
    "question": "Ecvatorline ürünleri nasıl temin ediyor?"
  }
  ```
- Response (with citations):
  ```JSON
  {
    "answer": "Ecvatorline, ürünlerini tedarikçilerden toptan alım yaparak temin ediyor [1].",
    "used_tools": false,
    "tool_name": null,
    "tool_input": null,
    "tool_output": null
  }
  ```
- Response (no relevant context):

  ```JSON
  {
    "answer": "Bilmiyorum.",
    "used_tools": false,
    "tool_name": null,
    "tool_input": null,
    "tool_output": null
  }
  ```

**`POST /ask`**
Debug endpoint to inspect retrieval results.

- Request:
  ```JSON
  {
    "query": "Ecvatorline ürünleri nasıl temin ediyor?",
    "top_k": 3
  }
  ```
- Response:
  ```JSON
  {
  "query": "Ecvatorline ürünleri nasıl temin ediyor?",
  "hits": [
            {
                "text": "Ecvatorline, bir e-ticaret satış mağazasıdır. Ürünler tedarikçilerden toptan alım yapılarak perakende satışa sunulur.",
                "meta": { "source": "company-profile" },
                "distance": 259.8234
            }
        ]
  }
  ```

## RAG Guardrails (Behavior)

- Uses session facts and retrieved context when relevant

- If context is used → must cite [1], [2], ...

- If the answer is not supported by facts/history/context → “Bilmiyorum.”

- No fabricated sources

## Week 3 Outcome

Week 3 delivers a production-grade local RAG foundation:

- local embeddings + persistent vector store

- verifiable retrieval with debug endpoint

- cited answers + anti-hallucination behavior

- deterministic ingestion and deduped retrieval

Ready to extend into Week 4: Multi-Agent Orchestration (planner/researcher/writer) on top of the same local knowledge base.