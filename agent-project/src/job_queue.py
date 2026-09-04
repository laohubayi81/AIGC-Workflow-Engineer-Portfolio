"""单实例串行队列：读 CSV → 跳过已成功 → 失败重试 → jsonl 状态 + 汇总。"""
from __future__ import annotations

import csv
import json
import time
from collections import Counter
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


def classify_error(err: str | None) -> str:
    t = (err or "").lower()
    if "identitygate" in t or "identity gate" in t or "cosine=" in t:
        return "identity_gate"
    if "未在" in (err or "") or "comfyui" in t and ("监听" in (err or "") or "refused" in t):
        return "comfy_down"
    if "timed out" in t or "timeout" in t:
        return "timeout"
    if "execution error" in t or "runtimerror" in t or "runtimeerror" in t:
        return "execution"
    if "场景库" in (err or "") or "必须提供" in (err or "") or "valueerror" in t:
        return "validation"
    if not err:
        return "unknown"
    return "other"


def _percentile(xs: list[float], p: float) -> float | None:
    if not xs:
        return None
    ys = sorted(xs)
    if len(ys) == 1:
        return round(ys[0], 2)
    k = (len(ys) - 1) * p / 100.0
    lo = int(k)
    hi = min(lo + 1, len(ys) - 1)
    frac = k - lo
    return round(ys[lo] * (1.0 - frac) + ys[hi] * frac, 2)


def summarize_state(state_path: Path) -> dict:
    """Latest record per id. Success rate, P50/P90, failure reason histogram."""
    latest: dict[str, dict] = {}
    if state_path.exists():
        for line in state_path.read_text(encoding="utf-8").splitlines():
            if not line.strip():
                continue
            rec = json.loads(line)
            jid = rec.get("id")
            if jid:
                latest[str(jid)] = rec
    recs = list(latest.values())
    ok = [r for r in recs if r.get("ok")]
    fail = [r for r in recs if r.get("ok") is False]
    secs = [float(r["seconds"]) for r in ok if isinstance(r.get("seconds"), (int, float))]
    reasons = Counter(classify_error(r.get("error")) for r in fail)
    n_ok, n_fail = len(ok), len(fail)
    attempted = n_ok + n_fail
    return {
        "jobs_in_state": len(recs),
        "ok": n_ok,
        "fail": n_fail,
        "success_rate": round((n_ok / attempted), 4) if attempted else 1.0,
        "latency_s": {
            "n": len(secs),
            "mean": round(sum(secs) / len(secs), 2) if secs else None,
            "p50": _percentile(secs, 50),
            "p90": _percentile(secs, 90),
            "min": round(min(secs), 2) if secs else None,
            "max": round(max(secs), 2) if secs else None,
        },
        "fail_reasons": dict(reasons),
    }


def write_report(summary: dict, path: Path) -> Path:
    lat = summary.get("latency_s") or {}
    reasons = summary.get("fail_reasons") or {}
    reason_lines = (
        "\n".join(f"| `{k}` | {v} |" for k, v in sorted(reasons.items()))
        or "| (none) | 0 |"
    )
    md = f"""# Queue monitor

- state: `{summary.get("state", "")}`
- 本轮墙钟: {summary.get("seconds")} s · skip={summary.get("skip")}
- 状态文件（每 id 最后一条）: jobs={summary.get("jobs_in_state")} ok={summary.get("ok")} fail={summary.get("fail")}
- **成功率**: {summary.get("success_rate")}

## 耗时（成功任务 seconds）

| n | mean | P50 | P90 | min | max |
|---|---|---|---|---|---|
| {lat.get("n")} | {lat.get("mean")} | {lat.get("p50")} | {lat.get("p90")} | {lat.get("min")} | {lat.get("max")} |

## 失败原因

| reason | n |
|---|---|
{reason_lines}

`identity_gate` = IdentityGate 拒收；`comfy_down` = 服务没开；`execution` = 图执行红字。
"""
    path.write_text(md, encoding="utf-8")
    return path


def run_queue(
    csv_path: Path,
    *,
    state_path: Path | None = None,
    limit: int | None = None,
    extra_retries: int = 1,
    client: ComfyClient | None = None,
    kind: str = "portrait",
    fail_if_below: bool = False,
    identity_threshold: float = 0.5,
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
                        fail_if_below=fail_if_below,
                        identity_threshold=identity_threshold,
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
            rec = {"ok": False, "id": jid, **job, "error": last, "fail_reason": classify_error(last)}
            append_state(state_path, rec)
            fail_n += 1
            log(f"REASON {jid} {rec['fail_reason']}")

    elapsed = time.time() - t0
    stats = summarize_state(state_path)
    summary = {
        "csv": str(csv_path),
        "state": str(state_path),
        "report": str(run_dir / "report.md"),
        "total": len(jobs),
        "ok": ok_n,
        "fail": fail_n,
        "skip": skip_n,
        "seconds": round(elapsed, 1),
        **stats,
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    write_report(summary, run_dir / "report.md")
    log(
        f"DONE ok={summary['ok']} fail={summary['fail']} rate={summary['success_rate']} "
        f"p50={summary['latency_s']['p50']} p90={summary['latency_s']['p90']} reasons={summary['fail_reasons']}"
    )
    return summary
