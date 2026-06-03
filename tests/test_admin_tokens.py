import pytest
from tests.conftest import ADMIN_HEADERS


def test_list_tokens_empty(client):
    r = client.get("/api/v1/admin/tokens", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json() == []


def test_create_token(client):
    r = client.post("/api/v1/admin/tokens", json={"name": "Restaurante A", "username": "rest_a", "password": "senha123"}, headers=ADMIN_HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "Restaurante A"
    assert len(data["token"]) == 64
    assert data["is_active"] is True


def test_list_tokens_returns_created(client):
    client.post("/api/v1/admin/tokens", json={"name": "Restaurante B", "username": "rest_b", "password": "senha123"}, headers=ADMIN_HEADERS)
    r = client.get("/api/v1/admin/tokens", headers=ADMIN_HEADERS)
    assert len(r.json()) == 1


def test_patch_token_deactivate(client):
    create_r = client.post("/api/v1/admin/tokens", json={"name": "Restaurante C", "username": "rest_c", "password": "senha123"}, headers=ADMIN_HEADERS)
    token_id = create_r.json()["id"]
    r = client.patch(f"/api/v1/admin/tokens/{token_id}", json={"is_active": False}, headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_delete_token(client):
    create_r = client.post("/api/v1/admin/tokens", json={"name": "Restaurante D", "username": "rest_d", "password": "senha123"}, headers=ADMIN_HEADERS)
    token_id = create_r.json()["id"]
    r = client.delete(f"/api/v1/admin/tokens/{token_id}", headers=ADMIN_HEADERS)
    assert r.status_code == 204
    list_r = client.get("/api/v1/admin/tokens", headers=ADMIN_HEADERS)
    assert list_r.json() == []


def test_delete_token_not_found(client):
    r = client.delete("/api/v1/admin/tokens/nonexistent-id", headers=ADMIN_HEADERS)
    assert r.status_code == 404


def test_create_token_unauthorized(client):
    r = client.post("/api/v1/admin/tokens", json={"name": "X", "username": "x_user", "password": "senha123"}, headers={"X-Isy-Admin-Token": "wrong"})
    assert r.status_code == 401


def test_create_token_duplicate_username(client):
    client.post("/api/v1/admin/tokens", json={"name": "Restaurante E", "username": "same_user", "password": "senha123"}, headers=ADMIN_HEADERS)
    r = client.post("/api/v1/admin/tokens", json={"name": "Restaurante F", "username": "same_user", "password": "outra_senha"}, headers=ADMIN_HEADERS)
    assert r.status_code == 400
