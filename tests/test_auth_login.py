import pytest
from tests.conftest import ADMIN_HEADERS


def test_admin_login_success(client):
    r = client.post("/api/v1/auth/admin/login", json={"password": "admin123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert data["token_type"] == "bearer"


def test_admin_login_wrong_password(client):
    r = client.post("/api/v1/auth/admin/login", json={"password": "wrong"})
    assert r.status_code == 401


def test_client_login_success(client):
    client.post("/api/v1/admin/tokens",
                json={"name": "Restaurante Test", "username": "rest_test", "password": "senha123"},
                headers=ADMIN_HEADERS)
    r = client.post("/api/v1/auth/login", json={"username": "rest_test", "password": "senha123"})
    assert r.status_code == 200
    data = r.json()
    assert "token" in data
    assert len(data["token"]) == 64


def test_client_login_wrong_password(client):
    client.post("/api/v1/admin/tokens",
                json={"name": "Restaurante Test2", "username": "rest_test2", "password": "senha123"},
                headers=ADMIN_HEADERS)
    r = client.post("/api/v1/auth/login", json={"username": "rest_test2", "password": "errada"})
    assert r.status_code == 401


def test_client_login_unknown_user(client):
    r = client.post("/api/v1/auth/login", json={"username": "naoexiste", "password": "qualquer"})
    assert r.status_code == 401


def test_client_login_inactive_token(client):
    create_r = client.post("/api/v1/admin/tokens",
                           json={"name": "Inativo", "username": "inativo_user", "password": "senha123"},
                           headers=ADMIN_HEADERS)
    token_id = create_r.json()["id"]
    client.patch(f"/api/v1/admin/tokens/{token_id}", json={"is_active": False}, headers=ADMIN_HEADERS)
    r = client.post("/api/v1/auth/login", json={"username": "inativo_user", "password": "senha123"})
    assert r.status_code == 401
