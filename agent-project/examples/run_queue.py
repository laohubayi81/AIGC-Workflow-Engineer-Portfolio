"""Day 12：CSV 串行队列。先 --limit 5 冒烟，再去掉 limit 跑满 50 张。"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.job_queue import run_queue

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO / "workflows" / "queue" / "jobs.csv"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--limit", type=int, default=None, help="只跑前 N 条（冒烟用）")
    ap.add_argument("--state", type=Path, default=None, help="已有 state.jsonl 则断点续跑")
    ap.add_argument("--fail-if-below", action="store_true", help="IdentityGate 低于阈值则本条失败")
    ap.add_argument("--identity-threshold", type=float, default=0.5)
    args = ap.parse_args()
    run_queue(
        args.csv,
        state_path=args.state,
        limit=args.limit,
        fail_if_below=args.fail_if_below,
        identity_threshold=args.identity_threshold,
    )
