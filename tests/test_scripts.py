import pytest
import models
from tests.conftest import ADMIN_HEADERS


def _make_token(db, name="client1", tok="client-token-123"):
    t = models.Token(name=name, token=tok)
    db.add(t)
    db.commit()
    return tok


def _make_script(client, name="greet", content='#!/bin/bash\necho "Hello $1"', params=None):
    payload = {"name": name, "description": "greet", "content": content,
               "parameters": params or ["name"], "is_active": True}
    return client.post("/api/v1/admin/scripts", json=payload, headers=ADMIN_HEADERS).json()


def test_list_scripts_active_only(client, db):
    tok = _make_token(db)
    _make_script(client, name="active-script")
    r = client.get("/api/v1/scripts", headers={"X-Isy-Token": tok})
    assert r.status_code == 200
    assert len(r.json()) == 1


def test_list_scripts_excludes_inactive(client, db):
    tok = _make_token(db)
    s = _make_script(client, name="inactive-script")
    client.put(f"/api/v1/admin/scripts/{s['id']}", json={"is_active": False}, headers=ADMIN_HEADERS)
    r = client.get("/api/v1/scripts", headers={"X-Isy-Token": tok})
    assert r.json() == []


def test_execute_script_success(client, db, tmp_path, monkeypatch):
    monkeypatch.setenv("SCRIPTS_DIR", str(tmp_path))
    tok = _make_token(db)
    _make_script(client, name="greet", content='#!/bin/bash\necho "Hello $1"', params=["name"])
    r = client.post("/api/v1/scripts/greet/execute",
                    json={"parameters": {"name": "Andre"}},
                    headers={"X-Isy-Token": tok})
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "success"
    assert data["exit_code"] == 0
    assert "Hello Andre" in data["stdout"]


def test_execute_script_not_found(client, db):
    tok = _make_token(db)
    r = client.post("/api/v1/scripts/nonexistent/execute",
                    json={"parameters": {}},
                    headers={"X-Isy-Token": tok})
    assert r.status_code == 404


def test_execute_script_inactive(client, db, tmp_path, monkeypatch):
    monkeypatch.setenv("SCRIPTS_DIR", str(tmp_path))
    tok = _make_token(db)
    s = _make_script(client, name="inactive", content="#!/bin/bash\necho hi", params=[])
    client.put(f"/api/v1/admin/scripts/{s['id']}", json={"is_active": False}, headers=ADMIN_HEADERS)
    r = client.post("/api/v1/scripts/inactive/execute",
                    json={"parameters": {}},
                    headers={"X-Isy-Token": tok})
    assert r.status_code == 403


def test_execute_saves_execution_log(client, db, tmp_path, monkeypatch):
    monkeypatch.setenv("SCRIPTS_DIR", str(tmp_path))
    tok = _make_token(db)
    _make_script(client, name="counter", content='#!/bin/bash\necho "count: $1"', params=["n"])
    client.post("/api/v1/scripts/counter/execute",
                json={"parameters": {"n": "42"}},
                headers={"X-Isy-Token": tok})
    executions = db.query(models.Execution).all()
    assert len(executions) == 1
    assert executions[0].status == "success"
