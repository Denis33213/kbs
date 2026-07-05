"""
Тесты API-уровня (QA-01/QA-02, упрощённая версия без реального Elasticsearch/Redis).

Каждый тест использует уникальное имя пользователя (на основе uuid), поэтому
тесты идемпотентны и не зависят от того, очищается ли тестовая БД между
запусками pytest — коллизий "пользователь уже существует" быть не может.

TestClient создаётся без контекстного менеджера ("with"), поэтому startup-событие
(инициализация Elasticsearch) не выполняется — это позволяет тестировать auth и
валидацию без поднятого Elasticsearch. Тесты поиска мокают search_chunks напрямую.
"""

import io
import uuid
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def _unique_username(prefix: str) -> str:
    """Генерирует уникальное имя пользователя для теста, чтобы избежать коллизий в БД."""
    return f"{prefix}_{uuid.uuid4().hex[:8]}"


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_register_new_user():
    username = _unique_username("alice")
    response = client.post(
        "/api/v1/auth/register",
        json={"username": username, "password": "secret123"},
    )
    assert response.status_code == 201


def test_register_duplicate_user_returns_400():
    username = _unique_username("bob")
    client.post("/api/v1/auth/register", json={"username": username, "password": "secret123"})
    response = client.post("/api/v1/auth/register", json={"username": username, "password": "secret123"})
    assert response.status_code == 400


def test_login_success_returns_token():
    username = _unique_username("carol")
    client.post("/api/v1/auth/register", json={"username": username, "password": "secret123"})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "secret123"},
    )
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_wrong_password_returns_401():
    username = _unique_username("dave")
    client.post("/api/v1/auth/register", json={"username": username, "password": "secret123"})
    response = client.post(
        "/api/v1/auth/login",
        data={"username": username, "password": "wrong_password"},
    )
    assert response.status_code == 401


@pytest.fixture
def auth_headers():
    """Регистрирует тестового пользователя с уникальным именем и возвращает заголовок Authorization с токеном."""
    username = _unique_username("eve")
    client.post("/api/v1/auth/register", json={"username": username, "password": "secret123"})
    response = client.post("/api/v1/auth/login", data={"username": username, "password": "secret123"})
    assert response.status_code == 200, f"Не удалось залогиниться в фикстуре: {response.text}"
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


def test_upload_without_auth_returns_401():
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("test.pdf", io.BytesIO(b"%PDF-1.4 fake"), "application/pdf")},
    )
    assert response.status_code == 401


def test_upload_rejects_unsupported_format(auth_headers):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("notes.txt", io.BytesIO(b"hello world"), "text/plain")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_upload_rejects_empty_file(auth_headers):
    response = client.post(
        "/api/v1/documents/upload",
        files={"file": ("empty.pdf", io.BytesIO(b""), "application/pdf")},
        headers=auth_headers,
    )
    assert response.status_code == 400


def test_search_without_auth_returns_401():
    response = client.get("/api/v1/search", params={"q": "тест"})
    assert response.status_code == 401


@patch("app.api.search.search_chunks")
def test_search_returns_mocked_results(mock_search_chunks, auth_headers):
    mock_search_chunks.return_value = {
        "total": 1,
        "page": 1,
        "page_size": 10,
        "results": [
            {
                "chunk_id": "doc1_1_0",
                "file_name": "lecture.pdf",
                "page": 1,
                "text": "тестовый фрагмент текста",
                "highlighted_text": "<mark>тестовый</mark> фрагмент текста",
                "score": 2.3,
            }
        ],
    }
    response = client.get("/api/v1/search", params={"q": "тестовый"}, headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["total"] == 1
    assert data["results"][0]["file_name"] == "lecture.pdf"
    mock_search_chunks.assert_called_once()