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


def write_dated_csv(path, counts=(("small", 20), ("medium", 12), ("big", 8))):
    rows = ["tier,handle,niche,price,payout_date,paid"]
    for tier, n in counts:
        for i in range(n):
            rows.append(f"{tier},{tier}_{i},,{1000 * (i + 1)}.0,2026-0{1 + i % 9}-1{i % 9},{'yes' if i % 2 else 'no'}")
    path.write_text("\n".join(rows) + "\n")
    return path


def test_import_deals_holds_out_a_share_of_each_tier_from_creators_not_excluded(db, tmp_path):
    from datetime import datetime, timezone

    csv_path = write_dated_csv(tmp_path / "creators2.csv")
    exclude = {f"small_{i}" for i in range(15)} | {"big_0"}  # creators the served model was trained on
    assert import_deals(db, csv_path, holdout_share=0.1, exclude=exclude) == {"deals": 40, "holdout": 4}
    held = {d["handle"]: d["tier"] for d in db.deals.find({"holdout": True})}
    assert sorted(held.values()) == ["big", "medium", "small", "small"]  # 10% of 20, 12 and 8, rounded
    assert not set(held) & exclude
    doc = db.deals.find_one({"handle": "small_3"})
    assert doc["payout_date"].replace(tzinfo=timezone.utc) == datetime(2026, 4, 13, tzinfo=timezone.utc) and doc["price"] == 4000  # Mongo returns UTC without a zone
    assert "paid" not in doc  # the user's call: the paid column carries nothing
    first = set(held)
    import_deals(db, csv_path, holdout_share=0.1, exclude=exclude)
    assert {d["handle"] for d in db.deals.find({"holdout": True})} == first


def test_import_deals_command_with_a_holdout_share(db, tmp_path, monkeypatch):
    monkeypatch.setattr(cli, "get_db", lambda: db)
    exclude = write_csv(tmp_path / "old.csv", per_tier=2)
    result = CliRunner().invoke(cli.app, ["import-deals", str(write_dated_csv(tmp_path / "c.csv")), "--holdout-share", "0.1", "--exclude", str(exclude)])
    assert result.exit_code == 0, result.output
    assert "Imported 40 deals (4 held out)" in result.output
