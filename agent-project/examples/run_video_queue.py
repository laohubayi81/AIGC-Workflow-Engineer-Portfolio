"""Day 19：分镜 CSV 串行。先 --limit 1 冒烟，再 --limit 5。单条视频约 20–70s，不要和 UI 同时 Queue。"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.job_queue import run_queue

REPO = Path(__file__).resolve().parents[2]
DEFAULT_CSV = REPO / "workflows" / "queue" / "video_jobs.csv"


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", type=Path, default=DEFAULT_CSV)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--state", type=Path, default=None)
    args = ap.parse_args()
    run_queue(args.csv, state_path=args.state, limit=args.limit, kind="i2v")
