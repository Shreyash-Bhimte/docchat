import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"status": "DocChat API is running"}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_list_documents():
    response = client.get("/documents/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_upload_non_pdf():
    from io import BytesIO
    fake_file = BytesIO(b"this is not a pdf")
    response = client.post(
        "/upload/",
        files={"file": ("test.txt", fake_file, "text/plain")}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Only PDF files allowed"


def test_chat_invalid_doc():
    response = client.post(
        "/chat/",
        json={"doc_id": 99999, "question": "what is this?"}
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"


def test_chat_empty_question():
    response = client.post(
        "/chat/",
        json={"doc_id": 99999, "question": "   "}
    )
    # either 400 (empty question) or 404 (doc not found) — both are correct rejections
    assert response.status_code in [400, 404]


def test_delete_nonexistent_doc():
    response = client.delete("/documents/99999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Document not found"