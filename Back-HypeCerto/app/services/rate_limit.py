"""
services/rate_limit.py
Limitador em memória (janela deslizante) para rotas sensíveis (login, exclusão de conta).
Conta apenas FALHAS por (escopo, IP, identificador). Para vários workers/instâncias, troque o
armazenamento por Redis mantendo esta interface.
"""
import time
from collections import defaultdict, deque
from threading import Lock

from fastapi import HTTPException, Request, status

_lock = Lock()
_hits: dict = defaultdict(deque)


def _key(request: Request, scope: str, ident: str) -> str:
    ip = request.client.host if request.client else "unknown"
    return f"{scope}:{ip}:{ident.lower()}"


def check_rate_limit(request: Request, scope: str, ident: str = "", limit: int = 5, window_s: int = 900) -> None:
    """Levanta 429 se já houve `limit` falhas na janela."""
    key, now = _key(request, scope, ident), time.monotonic()
    with _lock:
        q = _hits[key]
        while q and now - q[0] > window_s:
            q.popleft()
        if len(q) >= limit:
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Muitas tentativas. Tente novamente mais tarde.",
                headers={"Retry-After": str(int(window_s - (now - q[0])) + 1)},
            )


def register_failure(request: Request, scope: str, ident: str = "") -> None:
    with _lock:
        _hits[_key(request, scope, ident)].append(time.monotonic())


def clear_failures(request: Request, scope: str, ident: str = "") -> None:
    with _lock:
        _hits.pop(_key(request, scope, ident), None)


def reset_rate_limits() -> None:
    """Uso em testes."""
    with _lock:
        _hits.clear()
