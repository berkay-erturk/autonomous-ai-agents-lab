# Week 1 — Local LLM Tool-Using Agent (Ollama + FastAPI)

## What it does
- FastAPI `/ask` endpoint
- Uses a local LLM (Ollama) to decide whether a tool is needed
- Executes `calculator` tool for exact arithmetic
- Returns structured JSON including tool usage metadata
- Basic IP rate limiting + structured logs

## Prerequisites
- Ollama installed
- Model pulled: `llama3.1`

Check:
- `curl http://localhost:11434/api/tags`

## Run (Windows)
Double-click:
- `run_local.bat`

Or manually:
```bat
.venv\Scripts\activate
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
