"""Saves every HikerAPI response for the deal creators in a CSV (handle, payout_date), with reels reaching back
BACK_DAYS before each payout. Network work only: it needs httpx and `truerate/instagram.py`, so it runs on a small
server. The snapshots are rebuilt later from the saved responses (`truerate collect-benchmark`), at no cost.

    HIKERAPI_KEY=... python collect_deals.py deals.csv --store hikerapi --workers 32

Resumable: each finished creator is appended to `--log`, and a rerun skips them. Rate-limited creators get up to
three more passes, each with half the workers. Running out of HikerAPI credit (402) stops the run.
"""

import argparse
import csv
import os
import shutil
import sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx  # noqa: E402

from truerate.instagram import BASE_URL, Hiker, HikerError, collect  # noqa: E402

BACK_DAYS = 90  # the reels in the 90 days before a payout show what the creator was delivering when booked
MIN_FREE_GB = 1.0  # the server is shared: stop before its disk gets close to full


def plan(rows: list[dict], done: set[str]) -> list[tuple[str, datetime]]:
    todo = {}
    for r in rows:
        handle = r["handle"].strip().lstrip("@").lower()
        if handle and handle not in done:
            paid = datetime.strptime(r["payout_date"].strip(), "%Y-%m-%d").replace(tzinfo=timezone.utc)
            todo[handle] = paid - timedelta(days=BACK_DAYS)
    return sorted(todo.items())


def run(hiker, todo: list[tuple[str, datetime]], workers: int, log: Path, collect=collect, store: Path | None = None) -> dict:
    out = {"done": [], "retry": [], "failed": [], "stopped": False}
    with ThreadPoolExecutor(max_workers=workers) as pool, log.open("a") as done_log:
        def fetch(h, when):
            collect(hiker, h, workers=4, back_to=when)  # the snapshot itself is not kept: the saved responses are the result

        futures = {pool.submit(fetch, h, when): (h, when) for h, when in todo}
        for i, future in enumerate(as_completed(futures), 1):
            handle, when = futures.pop(future)
            try:
                future.result()
            except HikerError as e:
                if e.status == 402:
                    out["stopped"] = True
                    pool.shutdown(cancel_futures=True)
                    break
                (out["retry"].append((handle, when)) if e.status == 429 else out["failed"].append((handle, str(e)[:120])))
                continue
            except Exception as e:  # one creator's timeout or odd profile must not stop the run
                out["failed"].append((handle, str(e)[:120]))
                continue
            out["done"].append(handle)
            done_log.write(handle + "\n")
            done_log.flush()
            if i % 25 == 0:
                print(f"[{i}/{len(todo)}] done {len(out['done'])}, retry {len(out['retry'])}, failed {len(out['failed'])}", flush=True)
                if store is not None and shutil.disk_usage(store).free / 1e9 < MIN_FREE_GB:
                    print("Less than 1 GB free: stopping", flush=True)
                    out["stopped"] = True
                    pool.shutdown(cancel_futures=True)
                    break
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("csv", type=Path)
    ap.add_argument("--store", type=Path, default=Path("hikerapi"))
    ap.add_argument("--log", type=Path, default=Path("done.txt"))
    ap.add_argument("--workers", type=int, default=32)
    a = ap.parse_args()
    rows = list(csv.DictReader(a.csv.open(newline="")))
    done = set(a.log.read_text().split()) if a.log.exists() else set()
    todo, workers = plan(rows, done), a.workers
    # httpx allows 100 connections by default; each worker needs up to 5 at once (its reel pages plus 4 per-reel lists).
    http = httpx.Client(base_url=BASE_URL, headers={"x-access-key": os.environ["HIKERAPI_KEY"]}, timeout=60,
                        limits=httpx.Limits(max_connections=a.workers * 5, max_keepalive_connections=a.workers * 2))
    hiker = Hiker(os.environ["HIKERAPI_KEY"], a.store, http)
    print(f"{len(todo)} creators to collect, {len(done)} already done", flush=True)
    failed = []
    for _ in range(4):
        out = run(hiker, todo, workers, a.log, store=a.store)
        failed += out["failed"]
        if out["stopped"] or not out["retry"]:
            break
        todo, workers = out["retry"], max(1, workers // 2)
        print(f"{len(todo)} rate-limited: another pass with {workers} workers", flush=True)
    print(f"Finished. Failed {len(failed)}:", flush=True)
    for handle, why in failed:
        print(f"  {handle}: {why}", flush=True)


if __name__ == "__main__":
    main()
