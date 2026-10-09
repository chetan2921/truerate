import mongomock
import pytest
from pymongo.errors import DuplicateKeyError
from typer.testing import CliRunner

from truerate import cli
from truerate.db import CACHE_TTL_SECONDS, ensure_indexes, import_deals


def write_csv(path, per_tier=11):
    rows = ["tier,handle,niche,price"]
    for tier in ("small", "medium", "big"):
        for i in range(per_tier):
            rows.append(f'{tier},User_{tier}_{i},"Gadgets, Technology",{1000 * (i + 1)}')
    path.write_text("\n".join(rows) + "\n")
    return path


@pytest.fixture
def db():
    database = mongomock.MongoClient().truerate
    ensure_indexes(database)
    return database


def test_indexes(db):
    cache_index = next(v for v in db.cache.index_information().values() if v["key"] == [("fetched_at", 1)])
    assert cache_index["expireAfterSeconds"] == CACHE_TTL_SECONDS
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
