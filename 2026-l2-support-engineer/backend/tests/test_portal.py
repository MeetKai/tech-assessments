def test_login_rejects_invalid_credentials(client):
    response = client.post("/api/login", json={"username": "servidor", "password": "incorreta"})
    assert response.status_code == 401
    assert response.json()["request_id"] == response.headers["x-request-id"]

def test_search_requires_session(client):
    assert client.get("/api/search").status_code == 401

def test_search_contracts(client, headers):
    response = client.get("/api/search", params={"q": "contrato"}, headers=headers)
    assert response.status_code == 200
    assert response.json()["total"] == 10
    assert "Contrato" in response.json()["items"][0]["title"]

def test_pagination(client, headers):
    first = client.get("/api/search", headers=headers).json()
    second = client.get("/api/search?page=2", headers=headers).json()
    assert first["total"] == 200
    assert len(first["items"]) == 10
    assert {d["id"] for d in first["items"]}.isdisjoint(d["id"] for d in second["items"])

def test_categories_and_filter(client, headers):
    categories = client.get("/api/categories", headers=headers).json()
    assert len(categories) == 5
    result = client.get("/api/search?category=pessoas", headers=headers).json()
    assert result["total"] == 40
    assert all(d["category"] == "pessoas" for d in result["items"])

def test_document_details(client, headers):
    assert client.get("/api/documents/1", headers=headers).json()["body"]
    assert client.get("/api/documents/999", headers=headers).status_code == 404

def test_page_validation(client, headers):
    assert client.get("/api/search?page=0", headers=headers).status_code == 422
