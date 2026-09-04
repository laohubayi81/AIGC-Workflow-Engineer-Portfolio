"""单实例串行队列：读 CSV → 跳过已成功 → 失败重试 → jsonl 状态 + 汇总。"""
from __future__ import annotations

import csv
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from .comfy_client import ComfyClient

REQUIRED = ("id", "image", "seed", "prefix")


def load_jobs(csv_path: Path) -> list[dict]:
    with csv_path.open(encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    jobs = []
    for r in rows:
        missing = [k for k in REQUIRED if not str(r.get(k, "")).strip()]
        if missing:
            raise ValueError(f"CSV 缺列 {missing}：{r}")
        scene = str(r.get("scene") or "").strip() or None
        prompt = str(r.get("prompt") or "").strip() or None
        if not scene and not prompt:
            raise ValueError(f"CSV 第 {r.get('id')} 行要有 scene（场景库名字）或 prompt（自定义提示词）")
        length_raw = str(r.get("length") or "").strip()
        jobs.append({
            "id": r["id"].strip(),
            "image": r["image"].strip(),
            "scene": scene,
            "prompt": prompt,
            "seed": int(r["seed"]),
            "prefix": r["prefix"].strip(),
            "length": int(length_raw) if length_raw else 25,
        })
    return jobs


def load_done(state_path: Path) -> set[str]:
    done = set()
    if not state_path.exists():
        return done
    for line in state_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rec = json.loads(line)
        if rec.get("ok") and rec.get("id"):
            done.add(rec["id"])
    return done


def append_state(state_path: Path, rec: dict) -> None:
    state_path.parent.mkdir(parents=True, exist_ok=True)
    with state_path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")


def run_queue(
    csv_path: Path,
    *,
    state_path: Path | None = None,
    limit: int | None = None,
    extra_retries: int = 1,
    client: ComfyClient | None = None,
    kind: str = "portrait",
) -> dict:
    csv_path = Path(csv_path)
    run_dir = csv_path.parent / "runs" / datetime.now().strftime("%Y%m%d_%H%M%S")
    run_dir.mkdir(parents=True, exist_ok=True)
    state_path = Path(state_path) if state_path else run_dir / "state.jsonl"
    log_path = run_dir / "queue.log"
    jobs = load_jobs(csv_path)
    if limit is not None:
        jobs = jobs[:limit]
    done = load_done(state_path)
    client = client or ComfyClient()
    t0 = time.time()
    ok_n = fail_n = skip_n = 0

    def log(msg: str) -> None:
        line = f"{datetime.now(timezone.utc).strftime('%H:%M:%S')} {msg}"
        print(line, flush=True)
        with log_path.open("a", encoding="utf-8") as f:
            f.write(line + "\n")

    log(f"jobs={len(jobs)} already_done={len(done)} state={state_path}")
    for job in jobs:
        jid = job["id"]
        if jid in done:
            skip_n += 1
            log(f"SKIP {jid}")
            continue
        attempts = 1 + extra_retries
        last = None
        for a in range(attempts):
            log(f"RUN {jid} scene={job['scene']} seed={job['seed']} try={a+1}/{attempts}")
            try:
                if kind == "i2v":
                    r = client.generate_i2v(
                        image=job["image"],
                        scene=job["scene"],
                        prompt=job.get("prompt"),
                        seed=job["seed"],
                        prefix=job["prefix"],
                        length=job.get("length") or 25,
                    )
                else:
                    r = client.generate(
                        image=job["image"],
                        scene=job["scene"],
                        prompt=job.get("prompt"),
                        seed=job["seed"],
                        prefix=job["prefix"],
                    )
                rec = {"ok": True, "id": jid, **job, **r}
                append_state(state_path, rec)
                done.add(jid)
                ok_n += 1
                log(f"OK {jid} {r['seconds']}s files={r['files']}")
                last = None
                break
            except Exception as e:
                last = str(e)
                log(f"FAIL {jid} {e}")
        if last is not None:
            append_state(state_path, {"ok": False, "id": jid, **job, "error": last})
            fail_n += 1

    elapsed = time.time() - t0
    summary = {
        "csv": str(csv_path),
        "state": str(state_path),
        "total": len(jobs),
        "ok": ok_n,
        "fail": fail_n,
        "skip": skip_n,
        "seconds": round(elapsed, 1),
        "success_rate": (ok_n / (ok_n + fail_n)) if (ok_n + fail_n) else 1.0,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    log(f"DONE {summary}")
    return summary
