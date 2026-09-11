import os
import secrets
import time
from fastapi import HTTPException, Request

USERS = {"servidor": "acesso-demo-2026", "colega": "acesso-demo-2026"}
SESSIONS: dict[str, dict] = {}

def login(username: str, password: str):
    if USERS.get(username) != password or username not in USERS:
        raise HTTPException(401, "Usuário ou senha inválidos.")
    ttl = int(os.getenv("TOKEN_TTL_SECONDS", "600"))
    token = secrets.token_urlsafe(24)
    SESSIONS[token] = {"username": username, "expires_at": time.time() + ttl}
    return {"token": token, "expires_in": ttl, "username": username}

def require_user(request: Request):
    scheme, _, token = request.headers.get("authorization", "").partition(" ")
    session = SESSIONS.get(token) if scheme.lower() == "bearer" else None
    if session is None:
        raise HTTPException(401, "Entre novamente para continuar.")
    if session["expires_at"] <= time.time():
        raise HTTPException(403, "Você não tem permissão para acessar este recurso.")
    return session["username"]
