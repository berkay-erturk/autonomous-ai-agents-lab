# autonomous-ai-agents-lab

A hands-on lab to build autonomous and tool-using AI agents from scratch (FastAPI-first), progressing from single-agent tool calling to RAG, multi-agent orchestration, and local LLM deployment.

## Tech Stack
- Python, FastAPI
- (Week 1) Tool-using agent
- (Upcoming) Memory, RAG (vector DB), Multi-agent (orchestration), Local LLMs

## Architecture (Week 1)
Client -> FastAPI (/ask) -> Agent -> (optional) Tools -> Response

## Quickstart
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
