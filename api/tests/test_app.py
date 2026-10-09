from fastapi.testclient import TestClient

from truerate.app import app
from truerate.config import Settings


def test_health():
    assert TestClient(app).get("/api/health").json() == {"ok": True}


def test_settings_read_env(monkeypatch):
    monkeypatch.setenv("MONGODB_DB", "truerate_test")
    assert Settings(_env_file=None).mongodb_db == "truerate_test"


import json  # noqa: E402

import pytest  # noqa: E402
from test_pipeline import deps, target_snapshot, world  # noqa: E402,F401

from truerate import app as app_module  # noqa: E402
from truerate.app import parse_handle  # noqa: E402


def test_parse_handle_accepts_handles_and_links():
    assert parse_handle("@Komal.Pandey") == "komal.pandey"
    assert parse_handle("https://www.instagram.com/newcreator/?hl=en") == "newcreator"
    assert parse_handle("instagram.com/new_creator") == "new_creator"
    assert parse_handle("not a handle!") is None


@pytest.fixture
def client(world, monkeypatch):
    monkeypatch.setattr(app_module, "get_db", lambda: world)
    monkeypatch.setattr(app_module, "make_deps", lambda db: deps(db, target_snapshot()))
    monkeypatch.setattr(app_module, "submit", lambda fn: fn())  # run the job inline
    return TestClient(app)


def test_analysis_runs_and_reports(client):
    res = client.post("/api/analyses", json={"handle": "https://instagram.com/newcreator", "quote": 5000})
    assert res.status_code == 202
    a = client.get(f"/api/analyses/{res.json()['id']}").json()
    assert a["status"] == "done" and a["handle"] == "newcreator" and a["inputs"]["quote"] == 5000
    assert a["step"] == 3 and len(a["steps"]) == 4
    assert a["result"]["decision"]["call"] in ("Go", "Negotiate") and a["result"]["price"]["fair"] > 0
    recent = client.get("/api/analyses").json()
    assert recent[0]["id"] == res.json()["id"] and recent[0]["call"] == a["result"]["decision"]["call"] and recent[0]["fair"] == a["result"]["price"]["fair"]


def test_bad_handle_is_rejected(client):
    assert client.post("/api/analyses", json={"handle": "!!"}).status_code == 422


def test_out_of_scope_and_failures_are_recorded(client, world, monkeypatch):
    private = target_snapshot()
    private["data"] = {"profile": private["data"]["profile"] | {"is_private": True}}
    monkeypatch.setattr(app_module, "make_deps", lambda db: deps(db, private))
    a = client.get(f"/api/analyses/{client.post('/api/analyses', json={'handle': 'someone'}).json()['id']}").json()
    assert a["status"] == "out_of_scope" and "private" in a["reason"] and a["result"] is None

    def broken(handle):
        raise RuntimeError("HikerAPI 402 on /v1/user/by/username: Top up your account")

    monkeypatch.setattr(app_module, "make_deps", lambda db: _with_collect(deps(db, None), broken))
    a = client.get(f"/api/analyses/{client.post('/api/analyses', json={'handle': 'someone'}).json()['id']}").json()
    assert a["status"] == "failed" and "402" in a["error"]


def _with_collect(d, fn):
    d.collect = fn
    return d


def test_meta_lists_categories_and_coverage(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "MODELS_DIR", tmp_path)
    assert client.get("/api/meta").json() == {"categories": list(app_module.CATEGORIES), "range_coverage": None}
    (tmp_path / "model_report.json").write_text(json.dumps({"holdout": {"coverage": 0.8}}))
    (tmp_path / "redteam.json").write_text(json.dumps({"n": 150}))
    assert client.get("/api/meta").json()["range_coverage"] == 0.8
    assert client.get("/api/model-report").json() == {"validation": {"holdout": {"coverage": 0.8}}, "redteam": {"n": 150}}
