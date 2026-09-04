"""Day 19：generate_i2v() 一条短视频。ComfyUI 需已开。热启动约 20s，冷启动约 70s。"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.comfy_client import ComfyClient


def on_progress(msg: dict):
    t = msg.get("type")
    d = msg.get("data") or {}
    if t == "progress":
        print(f"  progress {d.get('value')}/{d.get('max')}", flush=True)
    elif t in ("queued", "executing", "ws_error"):
        print(f"  {t} {d}", flush=True)


if __name__ == "__main__":
    c = ComfyClient()
    r = c.generate_i2v(
        image="portrait_cafe.png",
        scene="blink",
        seed=42,
        length=25,
        on_progress=on_progress,
    )
    print(r)
