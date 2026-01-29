import time
from collections import defaultdict, deque

# 30 requests / 5 minutes per IP (baseline)
WINDOW_SECONDS = 300
MAX_REQUESTS = 30

_requests = defaultdict(lambda: deque())


def check_rate_limit(ip: str) -> bool:
    now = time.time()
    q = _requests[ip]
    # drop old
    while q and now - q[0] > WINDOW_SECONDS:
        q.popleft()
    if len(q) >= MAX_REQUESTS:
        return False
    q.append(now)
    return True
