"""Day 9：数字人写真工作流耗时 / 成功率 / 显存测量。

对 ComfyUI /prompt API 串行跑 N 次（先 1 次预热不计入）。
用法（ComfyUI 已开、8188 可访问）：
  python workflows/benchmarks/bench_portrait.py --n 5
  python workflows/benchmarks/bench_portrait.py --n 20
"""
from __future__ import annotations

import argparse
import json
import statistics
import subprocess
import time
import urllib.error
import urllib.request
import uuid
from pathlib import Path

API = "http://127.0.0.1:8188"
REF = "00027.jpg"
POS = (
    "ohwx, close-up portrait of a person in a sunlit park, looking at camera, "
    "trees in the background, photorealistic, sharp focus, 8k"
)
NEG = "blurry, low quality, distorted, ugly, deformed, extra fingers, bad anatomy"
OUT_MD = Path(__file__).with_name("2026-09-03-portrait-bench.md")


def portrait_prompt(seed: int) -> dict:
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_raw_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "myface_krea2_lora.safetensors", "strength_model": 0.85, "model": ["1", 0]}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": POS}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": NEG}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "7": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "8": {"class_type": "KSampler", "inputs": {
            "seed": seed, "steps": 28, "cfg": 5.5, "sampler_name": "euler",
            "scheduler": "normal", "denoise": 1, "model": ["11", 0],
            "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0],
        }},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["6", 0]}},
        "10": {"class_type": "Krea2ControlLoRALoader", "inputs": {"model": ["2", 0], "lora_name": "depth-control-lora.safetensors", "strength": 0.8}},
        "11": {"class_type": "Krea2ControlApply", "inputs": {"model": ["10", 0], "control_latent": ["13", 0]}},
        "16": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "18": {"class_type": "ImageScale", "inputs": {"image": ["16", 0], "upscale_method": "lanczos", "width": 768, "height": 768, "crop": "center"}},
        "12": {"class_type": "DepthAnythingV2Preprocessor", "inputs": {"image": ["18", 0], "ckpt_name": "depth_anything_v2_vits.pth", "resolution": 768}},
        "13": {"class_type": "Krea2ControlImageEncode", "inputs": {
            "control_image": ["12", 0], "vae": ["6", 0], "latent": ["7", 0],
            "resize": "match_latent_size", "upscale_method": "lanczos", "crop": "center",
            "channel_mode": "grayscale", "normalize": "per_image_minmax", "invert": False,
            "batch_mode": "independent_images",
        }},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 1], "filename_prefix": "Bench_portrait_depth"}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"Bench_portrait_s{seed}"}},
    }


def gpu_mem_mib() -> int | None:
    try:
        r = subprocess.run(
            ["nvidia-smi", "--query-gpu=memory.used", "--format=csv,noheader,nounits"],
            capture_output=True, text=True, timeout=5,
        )
        if r.returncode != 0:
            return None
        return int(float(r.stdout.strip().splitlines()[0]))
    except Exception:
        return None


def submit(prompt: dict, client_id: str) -> str:
    body = json.dumps({"prompt": prompt, "client_id": client_id}).encode()
    req = urllib.request.Request(API + "/prompt", data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        resp = json.loads(r.read())
    pid = resp.get("prompt_id")
    if not pid:
        raise RuntimeError(f"submit failed: {resp}")
    return pid


def wait(pid: str) -> tuple[bool, str]:
    while True:
        time.sleep(3)
        try:
            with urllib.request.urlopen(f"{API}/history/{pid}", timeout=30) as r:
                h = json.loads(r.read())
        except Exception as e:
            print(f"  poll {e}", flush=True)
            continue
        if pid not in h:
            continue
        st = h[pid].get("status", {})
        msg = st.get("status_str") or "done"
        if st.get("status_str") != "success":
            for m in st.get("messages", []):
                if isinstance(m, (list, tuple)) and m and m[0] == "execution_error":
                    info = m[1] if len(m) > 1 and isinstance(m[1], dict) else {}
                    msg = f"{info.get('node_type')}: {info.get('exception_message')}"
                    return False, msg
        return st.get("status_str", "success") == "success", msg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=5, help="计入统计的次数（另有 1 次预热）")
    ap.add_argument("--warmup", action="store_true", default=True)
    args = ap.parse_args()

    try:
        urllib.request.urlopen(API + "/system_stats", timeout=5).read()
    except Exception as e:
        raise SystemExit(f"ComfyUI 未在 {API} 监听：{e}")

    client_id = uuid.uuid4().hex
    if args.warmup:
        print("[warmup] seed=41 …", flush=True)
        t0 = time.time()
        pid = submit(portrait_prompt(41), client_id)
        ok, msg = wait(pid)
        print(f"[warmup] {'ok' if ok else 'FAIL'} {time.time()-t0:.1f}s {msg}", flush=True)
        if not ok:
            raise SystemExit("预热失败，停止")

    times = []
    peak = gpu_mem_mib()
    fails = 0
    rows = []
    for i in range(args.n):
        seed = 42 + i
        mem0 = gpu_mem_mib()
        print(f"[{i+1}/{args.n}] seed={seed} …", flush=True)
        t0 = time.time()
        try:
            pid = submit(portrait_prompt(seed), client_id)
            ok, msg = wait(pid)
        except urllib.error.HTTPError as e:
            ok, msg = False, e.read().decode(errors="replace")[:400]
        except Exception as e:
            ok, msg = False, str(e)
        dt = time.time() - t0
        mem1 = gpu_mem_mib()
        for m in (mem0, mem1):
            if m is not None:
                peak = m if peak is None else max(peak, m)
        if ok:
            times.append(dt)
        else:
            fails += 1
        rows.append((seed, dt, ok, msg, mem1))
        print(f"  {'ok' if ok else 'FAIL'} {dt:.1f}s mem={mem1} MiB {msg}", flush=True)

    n_ok = len(times)
    rate = n_ok / args.n if args.n else 0
    lines = [
        "# 数字人写真 · 性能成本（Day 9）",
        "",
        f"- 工作流：Depth 0.8 + myface 0.85 + RAW FP8 + 输入 768 crop，参考图 `{REF}`",
        f"- 机器：本机 RTX 5080 Laptop 16GB · ComfyUI `{API}`",
        f"- 预热 1 次不计入；计入 n={args.n}，成功 {n_ok}，失败 {fails}，成功率 **{rate:.0%}**",
        "",
        "| # | seed | 耗时 s | 成功 | 显存 MiB |",
        "|---|---|---|---|---|",
    ]
    for i, (seed, dt, ok, msg, mem) in enumerate(rows, 1):
        lines.append(f"| {i} | {seed} | {dt:.1f} | {'是' if ok else '否'} | {mem if mem is not None else '-'} |")

    if times:
        mean = statistics.mean(times)
        p50 = statistics.median(times)
        xs = sorted(times)
        p90 = xs[min(len(xs) - 1, int(round(0.9 * (len(xs) - 1))))]
        per_h = 3600 / mean
        unit = 0.4 / per_h
        lines += [
            "",
            f"- 均值 **{mean:.1f} s** · P50 **{p50:.1f} s** · P90 **{p90:.1f} s**",
            f"- 显存峰值（nvidia-smi used）**{peak} MiB**" if peak is not None else "- 显存：未读到 nvidia-smi",
            f"- 吞吐约 **{per_h:.1f} 张/小时**",
            f"- 单件成本（口径 0.4 元/h 估算）**{unit:.3f} 元/张** = 0.4 × {mean:.1f} / 3600",
        ]
    report = "\n".join(lines) + "\n"
    print("\n" + report, flush=True)
    OUT_MD.write_text(report, encoding="utf-8")
    print(f"已写入 {OUT_MD}", flush=True)


if __name__ == "__main__":
    main()
