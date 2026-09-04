"""Day 23 dispatcher. Default --dry-run (no GPU). Live: drop --dry-run (needs ComfyUI)."""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.dispatcher import dispatch

REPO = Path(__file__).resolve().parents[2]


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=REPO / "workflows" / "queue" / "jobs.csv")
    ap.add_argument("--workers", type=Path, default=REPO / "workflows" / "queue" / "workers.json")
    ap.add_argument("--limit", type=int, default=6)
    ap.add_argument("--dry-run", action="store_true", default=True)
    ap.add_argument("--live", action="store_true", help="really POST /prompt")
    ap.add_argument("--fake-workers", type=int, default=0, help="dry-run only: pretend N workers")
    args = ap.parse_args()
    dry = not args.live
    override = None
    nfake = args.fake_workers or (2 if dry else 0)
    if dry and nfake:
        override = [{"name": f"fake-{i}", "base_url": f"http://127.0.0.1:{8188 + i}"} for i in range(nfake)]
    summary = dispatch(
        args.csv,
        workers_path=args.workers,
        limit=args.limit,
        dry_run=dry,
        workers_override=override,
    )
    keys = ("this_run", "max_inflight", "workers", "dry_run", "seconds", "success_rate", "jobs_in_state")
    print(json.dumps({k: summary[k] for k in keys}, ensure_ascii=False, indent=2))
