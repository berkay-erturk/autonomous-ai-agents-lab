from fastapi import FastAPI, HTTPException, Request
from .rate_limit import check_rate_limit
from .logger import log_event
from .schemas import AskRequest, AskResponse
from .agent_local_llm import run_agent_local
import traceback

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
        log_event("ask_received", ip=ip, question=payload.question)

        result = run_agent_local(payload.question)

        log_event(
            "ask_completed",
            ip=ip,
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
        log_event("ask_failed", ip=ip, error=str(e))
        raise HTTPException(status_code=500, detail=str(e))
