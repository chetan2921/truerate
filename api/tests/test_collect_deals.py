import importlib.util
from datetime import datetime, timedelta, timezone
from pathlib import Path

from truerate.instagram import HikerError

spec = importlib.util.spec_from_file_location("collect_deals", Path(__file__).resolve().parents[1] / "scripts" / "collect_deals.py")
collect_deals = importlib.util.module_from_spec(spec)
spec.loader.exec_module(collect_deals)


def test_plan_reaches_back_before_each_payout_and_skips_creators_done():
    rows = [{"handle": " @Alpha ", "payout_date": "2026-09-04"}, {"handle": "beta", "payout_date": "2025-02-10"}, {"handle": "gamma", "payout_date": "2026-01-01"}]
    todo = collect_deals.plan(rows, done={"gamma"})
    assert todo == [("alpha", datetime(2026, 9, 4, tzinfo=timezone.utc) - timedelta(days=collect_deals.BACK_DAYS)),
                    ("beta", datetime(2025, 2, 10, tzinfo=timezone.utc) - timedelta(days=collect_deals.BACK_DAYS))]


def test_run_keeps_going_past_failures_and_queues_rate_limits_for_another_pass(tmp_path):
    seen = []

    def fake_collect(hiker, handle, workers, back_to):
        seen.append((handle, back_to))
        if handle == "busy":
            raise HikerError(429, "slow down")
        if handle == "gone":
            raise HikerError(404, "no such user")
        return {"handle": handle}

    when = datetime(2026, 1, 1, tzinfo=timezone.utc)
    out = collect_deals.run(None, [("ok", when), ("busy", when), ("gone", when)], workers=3, log=tmp_path / "done.txt", collect=fake_collect)
    assert out["done"] == ["ok"] and out["retry"] == [("busy", when)] and [h for h, _ in out["failed"]] == ["gone"]
    assert (tmp_path / "done.txt").read_text().split() == ["ok"]  # resumable: the next run skips it
    assert sorted(seen) == sorted([("ok", when), ("busy", when), ("gone", when)])


def test_run_stops_when_credit_runs_out(tmp_path):
    def broke(hiker, handle, workers, back_to):
        raise HikerError(402, "top up")

    when = datetime(2026, 1, 1, tzinfo=timezone.utc)
    out = collect_deals.run(None, [(f"c{i}", when) for i in range(5)], workers=1, log=tmp_path / "done.txt", collect=broke)
    assert out["stopped"] and not out["done"]
