"""[过时] Day 5 第一轮 API 草稿，不要直接跑。

缺 identity_edit LoRA、prompt 仍是文生图 caption、路线 B 无结构/prompt 对打。
正式工作流：lora-training/workflows/day5_routeA_krea2edit.json
与 day5_routeB_depth_controlnet.json。说明见同目录 README.md。

---
原说明：Day 5 双路线批量排队：通过 ComfyUI API (/prompt) 串行执行 5 个对比任务。

路线 B（Depth CN-LoRA + myface LoRA）：strength 1.0 / 0.6
路线 A（krea2edit Identity Edit + myface LoRA）：ref_boost 1.0 / 0.5 / 1.5
seed 固定 42，与 Day 4 基线一致。输出 → ComfyUI-Shared/output/Krea2_Day5*/
"""
import json
import time
import urllib.request
import uuid

API = "http://127.0.0.1:8188"
REF = "IMG_20260901_185310_edit_85976.jpg"
POS = "ohwx, a photo of a person, upper body, looking at camera, neutral expression, plain white background, photorealistic, sharp focus, 8k"
NEG = "blurry, low quality, distorted, ugly, deformed, extra fingers, bad anatomy"
KS = {"seed": 42, "steps": 28, "cfg": 5.5, "sampler_name": "euler", "scheduler": "normal", "denoise": 1}


def common_nodes():
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "krea2_raw_fp8_scaled.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "LoraLoaderModelOnly", "inputs": {"lora_name": "myface_krea2_lora.safetensors", "strength_model": 0.85, "model": ["1", 0]}},
        "3": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen3vl_4b_fp8_scaled.safetensors", "type": "krea2"}},
        "6": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "7": {"class_type": "EmptySD3LatentImage", "inputs": {"width": 768, "height": 768, "batch_size": 1}},
        "16": {"class_type": "LoadImage", "inputs": {"image": REF}},
    }


def route_b(strength):
    p = common_nodes()
    p.update({
        "4": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": POS}},
        "5": {"class_type": "CLIPTextEncode", "inputs": {"clip": ["3", 0], "text": NEG}},
        "8": {"class_type": "KSampler", "inputs": {**KS, "model": ["11", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0]}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["6", 0]}},
        "10": {"class_type": "Krea2ControlLoRALoader", "inputs": {"model": ["2", 0], "lora_name": "depth-control-lora.safetensors", "strength": strength}},
        "11": {"class_type": "Krea2ControlApply", "inputs": {"model": ["10", 0], "control_latent": ["13", 0]}},
        "12": {"class_type": "DepthAnythingV2Preprocessor", "inputs": {"image": ["16", 0], "ckpt_name": "depth_anything_v2_vits.pth", "resolution": 768}},
        "13": {"class_type": "Krea2ControlImageEncode", "inputs": {"control_image": ["12", 0], "vae": ["6", 0], "latent": ["7", 0], "resize": "match_latent_size", "upscale_method": "lanczos", "crop": "center", "channel_mode": "grayscale", "normalize": "per_image_minmax", "invert": False, "batch_mode": "independent_images"}},
        "14": {"class_type": "SaveImage", "inputs": {"images": ["13", 1], "filename_prefix": f"Krea2_Day5B_depth_preview_s{strength}"}},
        "15": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": f"Krea2_Day5B_depthcn_s{strength}"}},
    })
    return p


def route_a(ref_boost):
    p = common_nodes()
    p.update({
        "4": {"class_type": "Krea2EditGroundedEncode", "inputs": {"clip": ["3", 0], "prompt": POS, "image": ["16", 0], "grounding_px": 768, "system_prompt": ""}},
        "5": {"class_type": "Krea2EditGroundedEncode", "inputs": {"clip": ["3", 0], "prompt": "", "image": ["16", 0], "grounding_px": 768, "system_prompt": ""}},
        "8": {"class_type": "LoadImage", "inputs": {"image": REF}},
        "9": {"class_type": "VAEEncode", "inputs": {"pixels": ["8", 0], "vae": ["6", 0]}},
        "10": {"class_type": "Krea2EditModelPatch", "inputs": {"model": ["2", 0], "source_latent": ["9", 0], "ref_boost": ref_boost, "ref_boost_a": 1.0, "fit_mode": "fit", "vae": ["6", 0], "source_image": ["8", 0], "target_latent": ["7", 0]}},
        "11": {"class_type": "KSampler", "inputs": {**KS, "model": ["10", 0], "positive": ["4", 0], "negative": ["5", 0], "latent_image": ["7", 0]}},
        "12": {"class_type": "VAEDecode", "inputs": {"samples": ["11", 0], "vae": ["6", 0]}},
        "13": {"class_type": "SaveImage", "inputs": {"images": ["12", 0], "filename_prefix": f"Krea2_Day5A_refboost_{ref_boost}"}},
    })
    return p


JOBS = [
    ("B_s1.0", route_b(1.0)),
    ("B_s0.6", route_b(0.6)),
    ("A_rb1.0", route_a(1.0)),
    ("A_rb0.5", route_a(0.5)),
    ("A_rb1.5", route_a(1.5)),
]

client_id = uuid.uuid4().hex
for name, prompt in JOBS:
    body = json.dumps({"prompt": prompt, "client_id": client_id}).encode()
    req = urllib.request.Request(API + "/prompt", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
    except urllib.error.HTTPError as e:
        print(f"[{name}] 提交被拒: {e.code} {e.read().decode(errors='replace')[:800]}", flush=True)
        continue
    pid = resp.get("prompt_id")
    if not pid:
        print(f"[{name}] 提交失败: {resp}", flush=True)
        continue
    print(f"[{name}] queued {pid}", flush=True)
    t0 = time.time()
    while True:
        time.sleep(5)
        try:
            with urllib.request.urlopen(f"{API}/history/{pid}", timeout=30) as r:
                h = json.loads(r.read())
        except Exception as e:
            print(f"[{name}] 轮询异常 {e}", flush=True)
            continue
        if pid in h:
            st = h[pid].get("status", {})
            print(f"[{name}] 完成 status={st.get('status_str')} 耗时 {time.time() - t0:.0f}s", flush=True)
            if st.get("status_str") != "success":
                for m in st.get("messages", []):
                    if m[0] == "execution_error":
                        print(f"  ERROR node={m[1].get('node_type')}: {m[1].get('exception_message')}", flush=True)
            break
print("ALL DONE", flush=True)
