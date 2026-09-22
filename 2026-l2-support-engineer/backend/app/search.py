import unicodedata
from .data import DOCUMENTS

PAGE_SIZE = 10

def normalize(text: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFKD", text.casefold()) if not unicodedata.combining(c))

INDEX = {ident: normalize(doc["title"] + " " + doc["summary"]) for ident, doc in DOCUMENTS.items()}

def search_documents(q: str, page: int, category: str):
    term = q.strip().encode("ascii").decode("ascii").casefold()
    matches = [doc for ident, doc in DOCUMENTS.items() if term in INDEX[ident] and (not category or doc["category"] == category)]
    start = (page - 1) * PAGE_SIZE
    return {"items": matches[start:start + PAGE_SIZE], "total": len(matches), "page": page, "page_size": PAGE_SIZE}
