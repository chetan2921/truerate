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
    assert (recent[0]["low"], recent[0]["high"]) == (a["result"]["price"]["low"], a["result"]["price"]["high"])  # the list shows the range


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
    meta = client.get("/api/meta").json()
    assert meta["categories"] == list(app_module.CATEGORIES) and meta["range_coverage"] is None
    # The product list is broader than WLDD's 7 pricing categories; each product is priced through one of them.
    assert len(meta["products"]) >= 40 and {p["category"] for p in meta["products"]} == set(app_module.CATEGORIES)
    assert {"name": "Skincare", "category": "Fashion and beauty"} in meta["products"]
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
    assert {c["category"] for c in card["thin"]} == set(app_module.CATEGORIES) - {c["category"] for c in card["categories"]}


def test_batch_puts_avoid_after_everything_else(client, world, monkeypatch):
    import numpy as np

    from truerate.signals import make_fake

    fakes = iter([make_fake(make_fake(target_snapshot(), "bot_likers", np.random.default_rng(1)), "pod_comments", np.random.default_rng(2)), target_snapshot()])
    monkeypatch.setattr(app_module, "make_deps", lambda db: deps(db, next(fakes)))
    b = client.get(f"/api/batches/{client.post('/api/batches', json={'handles': ['fakeone', 'realone']}).json()['id']}").json()
    assert [row["call"] for row in b["rows"]][-1] == "Avoid" and b["rows"][0]["handle"] == "realone"


def test_removing_an_analysis_hides_it_from_recent_but_keeps_its_report(client):
    first = client.post("/api/analyses", json={"handle": "newcreator"}).json()["id"]
    second = client.post("/api/analyses", json={"handle": "newcreator"}).json()["id"]
    assert client.delete(f"/api/analyses/{first}").status_code == 204
    assert [a["id"] for a in client.get("/api/analyses").json()] == [second]
    assert client.get(f"/api/analyses/{first}").json()["status"] == "done"  # a shared report link still opens
    assert client.delete("/api/analyses/nope").status_code == 404


def test_analyses_left_running_by_a_stopped_server_are_marked_failed(world):
    world.analyses.insert_many([{"_id": "orphan", "handle": "x", "status": "running", "step": 1},
                                {"_id": "finished", "handle": "y", "status": "done", "step": 3}])
    app_module.fail_interrupted(world)
    orphan = world.analyses.find_one({"_id": "orphan"})
    assert orphan["status"] == "failed" and "stopped" in orphan["error"]
    assert world.analyses.find_one({"_id": "finished"})["status"] == "done"
