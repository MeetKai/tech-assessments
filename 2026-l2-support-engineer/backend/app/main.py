import logging
import re
import time
import traceback
import uuid
from fastapi import Depends, FastAPI, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from starlette.exceptions import HTTPException
from .auth import login, require_user
from .data import CATEGORIES, DOCUMENTS
from .search import search_documents
from .limits import check_limit

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
logger = logging.getLogger("portal")
app = FastAPI(title="Base de Conhecimento", version="1.3.0")

@app.middleware("http")
async def request_context(request: Request, call_next):
    supplied = request.headers.get("x-request-id", "")
    request.state.request_id = supplied if re.fullmatch(r"[a-zA-Z0-9-]{1,64}", supplied) else str(uuid.uuid4())
    ident = request.state.request_id
    start = time.monotonic()
    try:
        response = await call_next(request)
    except Exception:
        for line in traceback.format_exc().splitlines():
            logger.error("request_id=%s %s", ident, line)
        response = JSONResponse(status_code=500, content={"message": "Não foi possível concluir a consulta. Tente novamente ou informe o código ao suporte.", "request_id": ident})
    response.headers["X-Request-ID"] = ident
    logger.info("request_id=%s method=%s path=%s status=%s duration_ms=%.1f", ident, request.method, request.url.path, response.status_code, (time.monotonic() - start) * 1000)
    return response

@app.exception_handler(HTTPException)
async def http_error(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"message": str(exc.detail), "request_id": request.state.request_id}, headers=exc.headers)

@app.exception_handler(RequestValidationError)
async def validation_error(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"message": "Confira os parâmetros informados.", "request_id": request.state.request_id})

class Credentials(BaseModel):
    username: str
    password: str

@app.post("/api/login")
def create_session(credentials: Credentials):
    return login(credentials.username, credentials.password)

@app.get("/api/categories")
def categories(user: str = Depends(require_user)):
    return CATEGORIES

@app.get("/api/search")
def search(request: Request, q: str = Query("", max_length=200), page: int = Query(1, ge=1), category: str = "", user: str = Depends(require_user)):
    check_limit(request)
    return search_documents(q, page, category)

@app.get("/api/documents/{document_id}")
def document(document_id: int, user: str = Depends(require_user)):
    if document_id not in DOCUMENTS:
        raise HTTPException(404, "Documento não encontrado.")
    return DOCUMENTS[document_id]
