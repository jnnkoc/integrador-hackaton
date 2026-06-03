import pytest
from fastapi.testclient import TestClient
import models
from tests.conftest import ADMIN_HEADERS


def test_client_token_valid(client, db):
    token = models.Token(name="test-client", token="valid-token-abc")
    db.add(token)
    db.commit()
    response = client.get("/api/v1/scripts", headers={"X-Isy-Token": "valid-token-abc"})
    assert response.status_code == 200


def test_client_token_missing(client):
    response = client.get("/api/v1/scripts")
    assert response.status_code == 422


def test_client_token_invalid(client):
    response = client.get("/api/v1/scripts", headers={"X-Isy-Token": "nonexistent-token"})
    assert response.status_code == 401


def test_client_token_inactive(client, db):
    token = models.Token(name="inactive-client", token="inactive-token-xyz", is_active=False)
    db.add(token)
    db.commit()
    response = client.get("/api/v1/scripts", headers={"X-Isy-Token": "inactive-token-xyz"})
    assert response.status_code == 401


def test_admin_token_valid(client):
    response = client.get("/api/v1/admin/scripts", headers=ADMIN_HEADERS)
    assert response.status_code == 200


def test_admin_token_invalid(client):
    response = client.get("/api/v1/admin/scripts", headers={"X-Isy-Admin-Token": "wrong-token"})
    assert response.status_code == 401
