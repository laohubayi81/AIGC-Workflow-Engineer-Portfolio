"""Fan jobs out to N ComfyUI workers. One in-flight job per worker.

Local proof: --dry-run with 2 fake workers (no GPU). Live: workers.json URLs.
Two real instances on one 16GB GPU will OOM; default workers.json has 1 entry.
"""
from __future__ import annotations

import json
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

from .comfy_client import ComfyClient
from .job_queue import (
    append_state,
    classify_error,
    load_done,
    load_jobs,
    summarize_state,
    write_report,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_WORKERS = REPO_ROOT / "workflows" / "queue" / "workers.json"


def load_workers(path: Path | None = None) -> list[dict]:
    p = Path(path) if path else DEFAULT_WORKERS
    data = json.loads(p.read_text(encoding="utf-8"))
    workers = data.get("workers") if isinstance(data, dict) else data
    if not workers:
        raise ValueError(f"workers 列表为空: {p}")
    out = []
    for i, w in enumerate(workers):
        name = str(w.get("name") or f"w{i}")
        url = str(w.get("base_url") or "").rstrip("/")
        if not url:
            raise ValueError(f"worker {name} 缺 base_url")
        out.append({"name": name, "base_url": url})
    return out


def _run_one(job: dict, worker: dict, *, kind: str, dry_run: bool, fail_if_below: bool, identity_threshold: float) -> dict:
    t0 = time.time()
    if dry_run:
        time.sleep(0.05)
        return {
            "ok": True,
            "id": job["id"],
            **job,
            "worker": worker["name"],
            "base_url": worker["base_url"],
            "prompt_id": "dry-run",
            "files": [],
            "seconds": round(time.time() - t0, 3),
            "dry_run": True,
        }
    client = ComfyClient(base_url=worker["base_url"])
    if kind == "i2v":
        r = client.generate_i2v(
            image=job["image"],
            scene=job["scene"],
            prompt=job.get("prompt"),
            seed=job["seed"],
            prefix=job["prefix"],
            length=job.get("length") or 25,
            retries=2,
        )
    else:
        r = client.generate(
            image=job["image"],
            scene=job["scene"],
            prompt=job.get("prompt"),
            seed=job["seed"],
            prefix=job["prefix"],
            fail_if_below=fail_if_below,
            identity_threshold=identity_threshold,
            retries=2,
        )
    return {"ok": True, "id": job["id"], **job, "worker": worker["name"], "base_url": worker["base_url"], **r}


def dispatch(
    csv_path: Path,
    *,
    workers_path: Path | None = None,
    state_path: Path | None = None,
    limit: int | None = None,
    kind: str = "portrait",
    dry_run: bool = False,
    fail_if_below: bool = False,
    identity_threshold: float = 0.5,
    workers_override: list[dict] | None = None,
) -> dict:
    csv_path = Path(csv_path)
    workers = workers_override or load_workers(workers_path)
    run_dir = csv_path.parent / "runs" / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = Path(state_path) if state_path else run_dir / "state.jsonl"
    log_path = run_dir / "dispatch.log"
    jobs = load_jobs(csv_path)
    if limit is not None:
        jobs = jobs[:limit]
    done = load_done(state_path)
    pending = [j for j in jobs if j["id"] not in done]
    skip_n = len(jobs) - len(pending)
    n_workers = len(workers)
    lock = threading.Lock()
    inflight = 0
    max_inflight = 0

    def log(msg: str) -> None:
        line = f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    log(f"workers={n_workers} pending={len(pending)} skip={skip_n} dry_run={dry_run}")
    t0 = time.time()
    ok_n = fail_n = 0
    rr = 0

    def submit(job: dict) -> dict:
        nonlocal inflight, max_inflight, rr
        with lock:
            w = workers[rr % n_workers]
            rr += 1
            inflight += 1
            max_inflight = max(max_inflight, inflight)
        log(f"ASSIGN {job['id']} -> {w['name']} inflight={inflight}")
        try:
            rec = _run_one(
                job, w, kind=kind, dry_run=dry_run,
                fail_if_below=fail_if_below, identity_threshold=identity_threshold,
            )
            rec["max_inflight_seen"] = max_inflight
            append_state(state_path, rec)
            log(f"OK {job['id']} worker={w['name']} {rec.get('seconds')}s")
            return rec
        except Exception as e:
            rec = {
                "ok": False, "id": job["id"], **job,
                "worker": w["name"], "base_url": w["base_url"],
                "error": str(e), "fail_reason": classify_error(str(e)),
            }
            append_state(state_path, rec)
            log(f"FAIL {job['id']} worker={w['name']} {e}")
            return rec
        finally:
            with lock:
                inflight -= 1

    if pending:
        with ThreadPoolExecutor(max_workers=n_workers) as ex:
            futs = [ex.submit(submit, j) for j in pending]
            for fut in as_completed(futs):
                rec = fut.result()
                if rec.get("ok"):
                    ok_n += 1
                else:
                    fail_n += 1

    elapsed = time.time() - t0
    stats = summarize_state(state_path)
    summary = {
        "csv": str(csv_path),
        "state": str(state_path),
        "workers": [w["name"] for w in workers],
        "dry_run": dry_run,
        "max_inflight": max_inflight,
        "ok": stats.get("ok", ok_n),
        "fail": stats.get("fail", fail_n),
        "skip": skip_n,
        "this_run": {"ok": ok_n, "fail": fail_n, "skip": skip_n},
        "seconds": round(elapsed, 3),
        "jobs_in_state": stats.get("jobs_in_state"),
        "success_rate": stats.get("success_rate"),
        "latency_s": stats.get("latency_s"),
        "fail_reasons": stats.get("fail_reasons"),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(summary, run_dir / "report.md")
    log(f"DONE max_inflight={max_inflight} (cap={n_workers}) ok={ok_n} fail={fail_n} {elapsed:.2f}s")
    if max_inflight > n_workers:
        raise RuntimeError(f"dispatcher bug: max_inflight {max_inflight} > workers {n_workers}")
    return summary
