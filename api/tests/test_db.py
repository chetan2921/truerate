import pytest
from pymongo.errors import DuplicateKeyError
from typer.testing import CliRunner

from truerate import cli
from truerate.db import import_deals


def write_csv(path, per_tier=11):
    rows = ["tier,handle,niche,price"]
    for tier in ("small", "medium", "big"):
        for i in range(per_tier):
            rows.append(f'{tier},User_{tier}_{i},"Gadgets, Technology",{1000 * (i + 1)}')
    path.write_text("\n".join(rows) + "\n")
    return path


def test_indexes(db):
    assert "cache" not in db.list_collection_names()  # HikerAPI responses live on disk (data/hikerapi/), not in Mongo
    db.deals.insert_one({"handle": "a"})
    with pytest.raises(DuplicateKeyError):
        db.deals.insert_one({"handle": "a"})


def test_import_deals_holds_out_10_per_tier_and_is_idempotent(db, tmp_path):
    csv_path = write_csv(tmp_path / "creators.csv")
    assert import_deals(db, csv_path) == {"deals": 33, "holdout": 30}
    first = {d["handle"] for d in db.deals.find({"holdout": True})}
    assert import_deals(db, csv_path) == {"deals": 33, "holdout": 30}
    assert {d["handle"] for d in db.deals.find({"holdout": True})} == first
    assert db.deals.count_documents({}) == 33
    assert db.deals.count_documents({"holdout": True, "tier": "small"}) == 10
    doc = db.deals.find_one({"handle": "user_small_0"})
    assert doc["niche"] == ["Gadgets", "Technology"] and doc["price"] == 1000


def test_import_deals_command(db, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "get_db", lambda: db)
    result = CliRunner().invoke(cli.app, ["import-deals", str(write_csv(tmp_path / "c.csv"))])
    assert result.exit_code == 0, result.output
    assert "Imported 33 deals (30 held out)" in result.output
