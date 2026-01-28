import json
import re
from dataclasses import dataclass

from .llm_ollama import ollama_generate
from .tools import calculator


@dataclass
class AgentResult:
    answer: str
    used_tools: bool = False
    tool_name: str | None = None
    tool_input: str | None = None
    tool_output: str | None = None


TOOL_DECIDER_PROMPT = """You are a strict JSON generator.

Task: Decide if the calculator tool is required.
- Use calculator ONLY for exact arithmetic.
- If the question requires exact math, use_tool must be true.
- Otherwise use_tool must be false.

Return ONLY JSON.
Schema:
{{"use_tool": boolean}}

User question: {q}
"""


FINAL_ANSWER_PROMPT = """You are a helpful assistant.

IMPORTANT:
- You MUST use the provided session facts when answering.
- If a fact is present, do not say you don't know it.
- Be concise.

Session facts:
{facts}

Conversation so far:
{history}

Current user question: {q}

Tool used: {used}
Tool output: {out}

Answer in Turkish.
"""


def _extract_json(s: str) -> dict:
    """Best-effort JSON extraction from a possibly noisy / double-encoded response."""
    s = (s or "").strip()

    def _normalize_keys(d: dict) -> dict:
        # normalize keys like '"use_tool"' -> 'use_tool'
        out = {}
        for k, v in d.items():
            nk = k.strip()
            if len(nk) >= 2 and nk[0] == '"' and nk[-1] == '"':
                nk = nk[1:-1]
            out[nk] = v
        return out

    # 1) direct parse
    try:
        obj = json.loads(s)
        # If model returned a JSON *string* (double-encoded), parse again
        if (
            isinstance(obj, str)
            and obj.strip().startswith("{")
            and obj.strip().endswith("}")
        ):
            obj2 = json.loads(obj)
            if isinstance(obj2, dict):
                return _normalize_keys(obj2)
        if isinstance(obj, dict):
            return _normalize_keys(obj)
    except Exception:
        pass

    # 2) find first {...} block
    m = re.search(r"\{.*\}", s, flags=re.DOTALL)
    if m:
        chunk = m.group(0)
        try:
            obj = json.loads(chunk)
            if (
                isinstance(obj, str)
                and obj.strip().startswith("{")
                and obj.strip().endswith("}")
            ):
                obj2 = json.loads(obj)
                if isinstance(obj2, dict):
                    return _normalize_keys(obj2)
            if isinstance(obj, dict):
                return _normalize_keys(obj)
        except Exception:
            pass

    # fallback
    return {"use_tool": False, "tool_name": "calculator", "expression": ""}


def _extract_math_expression(question: str) -> str | None:
    """
    Extract a reasonable arithmetic expression from user text.
    Supports + - * / ( ) % ^ and decimals.
    Converts ^ to ** for our calculator.
    """
    q = question.replace(",", ".")
    q = q.replace("^", "**")

    # Find the longest chunk that looks like an arithmetic expression
    candidates = re.findall(r"[\d\.\s\+\-\*\/\(\)\%]+(?:\*\*[\d\.\s]+)?", q)
    candidates = [c.strip() for c in candidates if any(ch.isdigit() for ch in c)]

    if not candidates:
        return None

    # Pick the longest candidate (usually the actual expression)
    expr = max(candidates, key=len)
    # Collapse multiple spaces
    expr = re.sub(r"\s+", " ", expr).strip()
    return expr if expr else None


def run_agent_local(question: str, history: list[dict], facts_text: str) -> AgentResult:
    history_text = (
        "\n".join([f"{m['role']}: {m['content']}" for m in history])
        if history
        else "(no prior messages)"
    )
    decision_raw = ollama_generate(TOOL_DECIDER_PROMPT.format(q=question))
    decision = _extract_json(decision_raw)
    print("DECISION_RAW:", decision_raw)
    use_tool = bool(decision.get("use_tool"))

    if use_tool:
        expr = _extract_math_expression(question)
        if not expr:
            # LLM tool dedi ama expression bulamadık -> tool kullanmayalım
            final = ollama_generate(
                FINAL_ANSWER_PROMPT.format(
                    facts=facts_text,
                    history=history_text,
                    q=question,
                    used=True,
                    out=tool_out,
                )
            )
            return AgentResult(answer=final, used_tools=False)

        tool_out = calculator(expr)

        final = ollama_generate(
            FINAL_ANSWER_PROMPT.format(
                facts=facts_text,
                history=history_text,
                q=question,
                used=True,
                out=tool_out,
            )
        )

        return AgentResult(
            answer=final,
            used_tools=True,
            tool_name="calculator",
            tool_input=expr,
            tool_output=tool_out,
        )

    final = ollama_generate(
        FINAL_ANSWER_PROMPT.format(
            facts=facts_text, history=history_text, q=question, used=False, out=""
        )
    )
    return AgentResult(answer=final, used_tools=False)
