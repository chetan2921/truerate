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
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import httpx  # noqa: E402

from truerate.instagram import BASE_URL, Hiker, HikerError, collect  # noqa: E402

BACK_DAYS = 90  # the reels in the 90 days before a payout show what the creator was delivering when booked
MIN_FREE_GB = 1.0
PACER = None  # set by main(): its rate and 429 count go into the progress line  # the server is shared: stop before its disk gets close to full


class Paced(httpx.BaseTransport):
    """Spaces requests at `rate` a second across every worker. A 429 waits the time HikerAPI asks (`retry-after`) and cuts
    the rate by 30%; each success adds a little back, up to `ceiling`. Two machines share one account's limit, so each
    settles just under its share instead of bouncing creators."""

    def __init__(self, inner: httpx.BaseTransport, rate: float = 8.0, ceiling: float = 20.0, floor: float = 1.0):
        self.inner, self.rate, self.ceiling, self.floor = inner, rate, ceiling, floor
        self.lock, self.next, self.limited = threading.Lock(), time.monotonic(), 0

    def _slot(self) -> None:
        with self.lock:
            now = time.monotonic()
            start = max(now, self.next)
            self.next = start + 1 / self.rate
        if start > now:
            time.sleep(start - now)

    def handle_request(self, request: httpx.Request) -> httpx.Response:
        for attempt in range(10):
            self._slot()
            response = self.inner.handle_request(request)
            if response.status_code != 429:
                with self.lock:
                    self.rate = min(self.ceiling, self.rate + 0.05)
                return response
            response.close()
            with self.lock:
                self.limited += 1
                self.rate = max(self.floor, self.rate * 0.7)
            time.sleep(min(30.0, float(response.headers.get("retry-after") or 1) * (attempt + 1)))
        return response

    def close(self) -> None:
        self.inner.close()


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
            if i % 10 == 0:
                pace = f", {PACER.rate:.1f}/s, {PACER.limited} rate-limited so far" if PACER else ""
                print(f"[{i}/{len(todo)}] done {len(out['done'])}, retry {len(out['retry'])}, failed {len(out['failed'])}{pace}", flush=True)
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
    ap.add_argument("--rate", type=float, default=6.0, help="requests a second, at most; slows down on 429s")
    a = ap.parse_args()
    rows = list(csv.DictReader(a.csv.open(newline="")))
    done = set(a.log.read_text().split()) if a.log.exists() else set()
    todo, workers = plan(rows, done), a.workers
    # httpx allows 100 connections by default; each worker needs up to 5 at once (its reel pages plus 4 per-reel lists).
    inner = httpx.HTTPTransport(limits=httpx.Limits(max_connections=a.workers * 5, max_keepalive_connections=a.workers * 2))
    global PACER
    PACER = Paced(inner, rate=a.rate, ceiling=a.rate)  # the account's limit is fixed (`/sys/balance` says 9 a second)
    http = httpx.Client(base_url=BASE_URL, headers={"x-access-key": os.environ["HIKERAPI_KEY"]}, timeout=60, transport=PACER)
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
