"""Day 11 示例：generate() + WebSocket 进度。ComfyUI 需已开。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.comfy_client import ComfyClient


def on_progress(msg: dict):
    t = msg.get("type")
    d = msg.get("data") or {}
    if t == "progress":
        v, m = d.get("value"), d.get("max")
        print(f"  progress {v}/{m}", flush=True)
    elif t in ("queued", "executing", "ws_error"):
        print(f"  {t} {d}", flush=True)


if __name__ == "__main__":
    c = ComfyClient()
    r = c.generate(
        image="00027.jpg",
        prompt="ohwx, close-up portrait of a person in a quiet library, looking at camera, warm lamp light, photorealistic, 8k",
        seed=100,
        on_progress=on_progress,
    )
    print(r)
