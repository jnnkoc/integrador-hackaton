import pytest
import models
from tests.conftest import ADMIN_HEADERS


def _seed(client, db, tmp_path, monkeypatch):
    monkeypatch.setenv("SCRIPTS_DIR", str(tmp_path))
    t = models.Token(name="client1", token="log-test-token")
    db.add(t)
    db.commit()
    client.post("/api/v1/admin/scripts",
                json={"name": "ls-test", "description": "", "content": "#!/bin/bash\nls",
                      "parameters": [], "is_active": True},
                headers=ADMIN_HEADERS)
    client.post("/api/v1/scripts/ls-test/execute",
                json={"parameters": {}}, headers={"X-Isy-Token": "log-test-token"})


def test_client_logs_own_executions(client, db, tmp_path, monkeypatch):
    _seed(client, db, tmp_path, monkeypatch)
    r = client.get("/api/v1/logs", headers={"X-Isy-Token": "log-test-token"})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_client_cannot_see_other_token_logs(client, db, tmp_path, monkeypatch):
    _seed(client, db, tmp_path, monkeypatch)
    other = models.Token(name="other", token="other-token-999")
    db.add(other)
    db.commit()
    r = client.get("/api/v1/logs", headers={"X-Isy-Token": "other-token-999"})
    assert r.json() == []


def test_client_log_detail(client, db, tmp_path, monkeypatch):
    _seed(client, db, tmp_path, monkeypatch)
    logs = client.get("/api/v1/logs", headers={"X-Isy-Token": "log-test-token"}).json()
    execution_id = logs[0]["id"]
    r = client.get(f"/api/v1/logs/{execution_id}", headers={"X-Isy-Token": "log-test-token"})
    assert r.status_code == 200
    assert r.json()["id"] == execution_id


def test_admin_sees_all_logs(client, db, tmp_path, monkeypatch):
    _seed(client, db, tmp_path, monkeypatch)
    r = client.get("/api/v1/admin/logs", headers=ADMIN_HEADERS)
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_log_detail_wrong_token_returns_404(client, db, tmp_path, monkeypatch):
    _seed(client, db, tmp_path, monkeypatch)
    logs = client.get("/api/v1/logs", headers={"X-Isy-Token": "log-test-token"}).json()
    execution_id = logs[0]["id"]
    other = models.Token(name="other", token="other-token-999")
    db.add(other)
    db.commit()
    r = client.get(f"/api/v1/logs/{execution_id}", headers={"X-Isy-Token": "other-token-999"})
    assert r.status_code == 404
