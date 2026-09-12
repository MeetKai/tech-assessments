import time
from collections import defaultdict, deque
from fastapi import HTTPException, Request

WINDOW_SECONDS = 60
MAX_REQUESTS = 30
REQUESTS: dict[str, deque] = defaultdict(deque)

def check_limit(request: Request):
    key = request.client.host if request.client else "local"
    now = time.monotonic()
    recent = REQUESTS[key]
    while recent and recent[0] <= now - WINDOW_SECONDS:
        recent.popleft()
    if len(recent) >= MAX_REQUESTS:
        retry = max(1, int(WINDOW_SECONDS - (now - recent[0])) + 1)
        raise HTTPException(429, "Muitas requisições. Aguarde um minuto e tente novamente.", headers={"Retry-After": str(retry)})
    recent.append(now)
