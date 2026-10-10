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


def test_quote_check_endpoint(client):
    analysis_id = client.post("/api/analyses", json={"handle": "newcreator"}).json()["id"]
    fair = client.get(f"/api/analyses/{analysis_id}").json()["result"]["price"]["fair"]
    res = client.post(f"/api/analyses/{analysis_id}/quote", json={"quote": fair * 3})
    assert res.status_code == 200 and res.json()["position"] == "above" and res.json()["counter_offer"] == fair
    assert client.post("/api/analyses/nope/quote", json={"quote": 1000}).status_code == 404


def test_batch_runs_every_handle_and_ranks_by_cost(client):
    res = client.post("/api/batches", json={"handles": ["@one", "instagram.com/two", "three"], "budget": 50000})
    assert res.status_code == 202
    b = client.get(f"/api/batches/{res.json()['id']}").json()
    assert (b["total"], b["done"]) == (3, 3) and b["inputs"]["budget"] == 50000
    assert {row["handle"] for row in b["rows"]} == {"one", "two", "three"}
    costs = [row["cost_per_1k"] for row in b["rows"]]
    assert costs == sorted(costs) and all(row["call"] for row in b["rows"])


def test_batch_rejects_bad_or_too_many_handles(client):
    assert client.post("/api/batches", json={"handles": ["ok", "not ok!!"]}).status_code == 422
    assert client.post("/api/batches", json={"handles": [f"h{i}" for i in range(51)]}).status_code == 422


def test_rate_card_endpoint(client, tmp_path, monkeypatch):
    monkeypatch.setattr(app_module, "MODELS_DIR", tmp_path)
    import joblib

    from test_pricing import synthetic_rows

    from truerate.pricing import fit

    joblib.dump(fit(synthetic_rows()), tmp_path / "price.joblib")
    card = client.get("/api/rate-card").json()
    assert len(card["categories"]) == 3 and card["categories"][0]["category"] == "Tech and gadgets"


def test_batch_puts_avoid_after_everything_else(client, world, monkeypatch):
    import numpy as np

    from truerate.signals import make_fake

    fakes = iter([make_fake(make_fake(target_snapshot(), "bot_likers", np.random.default_rng(1)), "pod_comments", np.random.default_rng(2)), target_snapshot()])
    monkeypatch.setattr(app_module, "make_deps", lambda db: deps(db, next(fakes)))
    b = client.get(f"/api/batches/{client.post('/api/batches', json={'handles': ['fakeone', 'realone']}).json()['id']}").json()
    assert [row["call"] for row in b["rows"]][-1] == "Avoid" and b["rows"][0]["handle"] == "realone"


def test_verify_endpoints_and_the_report_show_creator_verified_data(client, world, monkeypatch):
    from test_phyllo import fake_phyllo

    monkeypatch.setattr(app_module, "make_phyllo", lambda: fake_phyllo())
    start = client.post("/api/verify", json={"handle": "asha.cooks"}).json()
    assert start == {"user_id": "user-1", "sdk_token": "token-1", "environment": "sandbox"}
    v = client.get("/api/verify/asha.cooks").json()
    assert v["followers"] == 78_976 and world.verified.find_one({"_id": "asha.cooks"})["followers"] == 78_976
    monkeypatch.setattr(app_module, "make_phyllo", lambda: fake_phyllo(connected=False))
    assert client.get("/api/verify/asha.cooks").status_code == 404
    analysis_id = client.post("/api/analyses", json={"handle": "asha.cooks"}).json()["id"]
    report = client.get(f"/api/analyses/{analysis_id}").json()["result"]
    assert report["verified"]["followers"] == 78_976 and report["verified"]["countries"][0]["code"] == "US"


def test_a_report_made_before_the_creator_verified_shows_their_verified_data(client, world, monkeypatch):
    from test_phyllo import fake_phyllo

    analysis_id = client.post("/api/analyses", json={"handle": "asha.cooks"}).json()["id"]
    assert client.get(f"/api/analyses/{analysis_id}").json()["result"]["verified"] is None
    monkeypatch.setattr(app_module, "make_phyllo", lambda: fake_phyllo())
    client.get("/api/verify/asha.cooks")
    assert client.get(f"/api/analyses/{analysis_id}").json()["result"]["verified"]["followers"] == 78_976
