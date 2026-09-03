"""Day 11 示例：batch_generate 串行两张（公园 + 夜景）。约 2 分钟。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.comfy_client import ComfyClient

if __name__ == "__main__":
    c = ComfyClient()
    rows = c.batch_generate(
        [
            {"scene": "park", "seed": 101, "prefix": "Batch_park"},
            {"scene": "night", "seed": 102, "prefix": "Batch_night"},
        ],
        image="00027.jpg",
    )
    for r in rows:
        print(r)
