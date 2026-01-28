from os import name
from fastapi import FastAPI, HTTPException, Request
from .rate_limit import check_rate_limit
from .logger import log_event
from .schemas import AskRequest, AskResponse, IngestTextRequest
from .agent_local_llm import run_agent_local
import traceback
from .memory_store import (
    get_messages,
    append_message,
    get_facts,
    set_fact,
    clear_session,
)
from .facts_extractor import extract_name
from .rag_store import ingest_text, retrieve

app = FastAPI(title="Week 1 - Local LLM Tool Using Agent")


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
def ask(payload: AskRequest, request: Request):
    ip = request.client.host if request.client else "unknown"

    if not check_rate_limit(ip):
        raise HTTPException(
            status_code=429, detail="Rate limit exceeded. Try again later."
        )

    try:
        log_event(
            "ask_received",
            ip=ip,
            session_id=payload.session_id,
            question=payload.question,
        )
        name = extract_name(payload.question)
        if name:
            set_fact(payload.session_id, "name", name)
        facts = get_facts(payload.session_id)
        facts_text = (
            "\n".join([f"- {k}: {v}" for k, v in facts.items()]) if facts else "(none)"
        )
        hits = retrieve(payload.question, top_k=3)
        context_text = (
            "\n\n".join(
                [
                    f"[{i+1}] (source={h['meta'].get('source')}, dist={h['distance']:.4f}) {h['text']}"
                    for i, h in enumerate(hits)
                ]
            )
            if hits
            else "(none)"
        )
        context_text = (
            "\n\n".join([f"[{i+1}] {h['text']}" for i, h in enumerate(hits)])
            if hits
            else "(none)"
        )

        history = get_messages(payload.session_id)
        result = run_agent_local(payload.question, history, facts_text, context_text)

        append_message(payload.session_id, "user", payload.question)
        append_message(payload.session_id, "assistant", result.answer)

        log_event(
            "ask_completed",
            ip=ip,
            session_id=payload.session_id,
            used_tools=result.used_tools,
            tool_name=result.tool_name,
            tool_input=result.tool_input,
        )

        return AskResponse(
            answer=result.answer,
            used_tools=result.used_tools,
            tool_name=result.tool_name,
            tool_input=result.tool_input,
            tool_output=result.tool_output,
        )
    except Exception as e:
        log_event("ask_failed", ip=ip, session_id=payload.session_id, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/session/clear")
def session_clear(payload: dict):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    clear_session(session_id)
    return {"status": "ok", "cleared": session_id}


@app.post("/session/debug")
def session_debug(payload: dict):
    session_id = payload.get("session_id")
    if not session_id:
        raise HTTPException(status_code=400, detail="session_id is required")
    return {
        "session_id": session_id,
        "facts": get_facts(session_id),
        "messages": get_messages(session_id),
    }


@app.post("/ingest/text")
def ingest_text_endpoint(payload: IngestTextRequest):
    doc_id = ingest_text(payload.text, source=payload.source)
    return {
        "status": "ok",
        "id": doc_id,
        "source": payload.source,
        "chars": len(payload.text),
    }


@app.post("/rag/debug")
def rag_debug(payload: dict):
    q = payload.get("query")
    if not q:
        raise HTTPException(status_code=400, detail="query is required")
    hits = retrieve(q, top_k=int(payload.get("top_k", 3)))
    return {"query": q, "hits": hits}
