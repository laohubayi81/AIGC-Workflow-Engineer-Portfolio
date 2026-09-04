"""Day 27：从已有 state.jsonl 出成功率 / P50 / P90 / 失败原因。不跑 GPU。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.job_queue import summarize_state, write_report


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--state", type=Path, required=True, help="state.jsonl")
    ap.add_argument("--out", type=Path, default=None, help="report.md，默认和 state 同目录")
    args = ap.parse_args()
    stats = summarize_state(args.state)
    stats["state"] = str(args.state)
    out = args.out or args.state.with_name("report.md")
    write_report(stats, out)
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    print("wrote", out)
