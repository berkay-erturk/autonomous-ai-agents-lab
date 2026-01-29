import time
from collections import defaultdict, deque

MAX_MESSAGES = 24  # last 24 messages (user+assistant)
SESSION_TTL_SECONDS = 3600  # 1 hour

_sessions = defaultdict(lambda: {"updated_at": time.time(), "messages": deque()})


def get_messages(session_id: str):
    _gc()
    return list(_sessions[session_id]["messages"])


def append_message(session_id: str, role: str, content: str):
    s = _sessions[session_id]
    s["updated_at"] = time.time()
    s["messages"].append({"role": role, "content": content})

    while len(s["messages"]) > MAX_MESSAGES:
        s["messages"].popleft()


def _gc():
    now = time.time()
    expired = [
        sid
        for sid, s in _sessions.items()
        if now - s["updated_at"] > SESSION_TTL_SECONDS
    ]
    for sid in expired:
        del _sessions[sid]
        _facts.pop(sid, None)


_facts = {}  # session_id -> dict of facts


def get_facts(session_id: str) -> dict:
    _gc()
    return _facts.get(session_id, {})


def set_fact(session_id: str, key: str, value: str):
    _gc()
    if session_id not in _facts:
        _facts[session_id] = {}
    _facts[session_id][key] = value


def clear_session(session_id: str):
    _sessions.pop(session_id, None)
    _facts.pop(session_id, None)


def list_sessions() -> list[str]:
    _gc()
    return list(_sessions.keys())
