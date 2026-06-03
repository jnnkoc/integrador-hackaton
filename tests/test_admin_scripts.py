import pytest
from tests.conftest import ADMIN_HEADERS

SCRIPT_PAYLOAD = {
    "name": "ping",
    "description": "Checks connectivity",
    "content": "#!/bin/bash\necho pong",
    "parameters": [],
    "is_active": True
}


def test_list_scripts_empty(client):
    r = client.get("/api/v1/admin/scripts", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json() == []


def test_create_script(client):
    r = client.post("/api/v1/admin/scripts", json=SCRIPT_PAYLOAD, headers=ADMIN_HEADERS)
    assert r.status_code == 201
    data = r.json()
    assert data["name"] == "ping"
    assert data["content"] == "#!/bin/bash\necho pong"


def test_create_script_duplicate_name(client):
    client.post("/api/v1/admin/scripts", json=SCRIPT_PAYLOAD, headers=ADMIN_HEADERS)
    r = client.post("/api/v1/admin/scripts", json=SCRIPT_PAYLOAD, headers=ADMIN_HEADERS)
    assert r.status_code == 400


def test_update_script(client):
    create_r = client.post("/api/v1/admin/scripts", json=SCRIPT_PAYLOAD, headers=ADMIN_HEADERS)
    script_id = create_r.json()["id"]
    r = client.put(f"/api/v1/admin/scripts/{script_id}", json={"is_active": False}, headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert r.json()["is_active"] is False


def test_update_script_not_found(client):
    r = client.put("/api/v1/admin/scripts/nonexistent", json={"is_active": False}, headers=ADMIN_HEADERS)
    assert r.status_code == 404


def test_delete_script(client):
    create_r = client.post("/api/v1/admin/scripts", json=SCRIPT_PAYLOAD, headers=ADMIN_HEADERS)
    script_id = create_r.json()["id"]
    r = client.delete(f"/api/v1/admin/scripts/{script_id}", headers=ADMIN_HEADERS)
    assert r.status_code == 204
    list_r = client.get("/api/v1/admin/scripts", headers=ADMIN_HEADERS)
    assert list_r.json() == []


def test_scripts_unauthorized(client):
    r = client.get("/api/v1/admin/scripts", headers={"X-Isy-Admin-Token": "wrong"})
    assert r.status_code == 401
