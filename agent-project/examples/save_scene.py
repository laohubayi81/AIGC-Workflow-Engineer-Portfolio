"""保存 / 列出场景库。提示词写入 workflows/queue/scenes.json。"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.comfy_client import ComfyClient


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("name", nargs="?", help="场景名，例如 library")
    ap.add_argument("prompt", nargs="?", help="正向提示词（英文，建议含 close-up + looking at camera）")
    ap.add_argument("--list", action="store_true", help="只列出已保存场景")
    ap.add_argument("--negative", default=None, help="可选负向")
    args = ap.parse_args()
    c = ComfyClient()
    if args.list or not args.name:
        scenes = c.list_scenes()
        print(json.dumps(scenes, ensure_ascii=False, indent=2))
        if not args.list and not args.name:
            print("\n保存：python agent-project/examples/save_scene.py 名字 \"提示词\"", flush=True)
        raise SystemExit(0)
    if not args.prompt:
        raise SystemExit("保存需要：save_scene.py 名字 \"提示词\"")
    path = c.save_scene(args.name, args.prompt, negative=args.negative)
    print(f"已写入 {path} 场景 '{args.name}'")
