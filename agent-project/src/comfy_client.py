"""ComfyUI HTTP + WebSocket 客户端（Day 11）。

前端 workflow JSON 不能 POST；这里加载 API Format（workflows/api/portrait_api.json）。
进度优先走 /ws；连不上则退回轮询 /history。
"""
from __future__ import annotations

import json
import random
import threading
import time
import urllib.error
import urllib.request
import uuid
from copy import deepcopy
from pathlib import Path
from typing import Callable, Iterable

from . import comfy_ws

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_GRAPH = REPO_ROOT / "workflows" / "api" / "portrait_api.json"
DEFAULT_I2V_GRAPH = REPO_ROOT / "workflows" / "api" / "i2v_api.json"
DEFAULT_SCENES = REPO_ROOT / "workflows" / "queue" / "scenes.json"
DEFAULT_VIDEO_SCENES = REPO_ROOT / "workflows" / "queue" / "video_scenes.json"
DEFAULT_NEG = "blurry, low quality, distorted, ugly, deformed, extra fingers, bad anatomy"
DEFAULT_VIDEO_NEG = (
    "blurry, still frame, watermark, subtitles, morphing, extra limbs, different person, "
    "smile, smiling, smirk, grin, showing teeth, wide mouth, laughing, mouth opening, "
    "mouth movement, talking, facial distortion"
)


def load_scenes(path: Path | None = None) -> dict:
    p = Path(path) if path else DEFAULT_SCENES
    if not p.exists():
        return {}
    data = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"场景库必须是 JSON 对象: {p}")
    return data


def save_scenes(scenes: dict, path: Path | None = None) -> Path:
    p = Path(path) if path else DEFAULT_SCENES
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(scenes, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return p


# 兼容旧 import；内容以 scenes.json 为准
SCENES = {k: v.get("prompt", "") for k, v in load_scenes().items()}


class ComfyError(RuntimeError):
    pass


class ComfyClient:
    def __init__(
        self,
        base_url: str = "http://127.0.0.1:8188",
        graph_path: Path | None = None,
        scenes_path: Path | None = None,
    ):
        self.base = base_url.rstrip("/")
        self.graph_path = Path(graph_path) if graph_path else DEFAULT_GRAPH
        self.scenes_path = Path(scenes_path) if scenes_path else DEFAULT_SCENES

    def _url(self, path: str) -> str:
        return self.base + path

    def _get(self, path: str, timeout: float = 30):
        with urllib.request.urlopen(self._url(path), timeout=timeout) as r:
            return json.loads(r.read())

    def _post(self, path: str, payload: dict, timeout: float = 60):
        body = json.dumps(payload).encode()
        req = urllib.request.Request(
            self._url(path), data=body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read())

    def ping(self) -> None:
        try:
            self._get("/system_stats", timeout=5)
        except Exception as e:
            raise ComfyError(f"ComfyUI 未在 {self.base} 监听：{e}") from e

    def generate(
        self,
        *,
        image: str = "00027.jpg",
        scene: str | None = None,
        prompt: str | None = None,
        seed: int = 42,
        depth_strength: float = 0.8,
        lora_strength: float = 0.85,
        prefix: str = "Api_portrait",
        identity_threshold: float = 0.5,
        fail_if_below: bool = False,
        on_progress: Callable[[dict], None] | None = None,
        retries: int = 3,
    ) -> dict:
        """生成一张写真。返回 {prompt_id, files, seconds}。fail_if_below=True 时身份门禁不达标整单失败。"""
        spec = self._validate(
            image=image, scene=scene, prompt=prompt, seed=seed,
            depth_strength=depth_strength, lora_strength=lora_strength,
            identity_threshold=identity_threshold, fail_if_below=fail_if_below,
        )
        graph = self._build_graph(spec, prefix)
        client_id = uuid.uuid4().hex
        last_err: Exception | None = None
        delay = 1.0
        for attempt in range(retries):
            try:
                self.ping()
                return self._run_once(graph, client_id, on_progress)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ComfyError) as e:
                last_err = e
                if attempt == retries - 1:
                    break
                time.sleep(delay + random.random() * 0.2)
                delay *= 2
        raise ComfyError(f"generate 失败（已重试 {retries} 次）：{last_err}") from last_err

    def batch_generate(self, jobs: Iterable[dict], **defaults) -> list[dict]:
        """串行批量。每个 job 是 generate() 的关键字；失败记进结果，不中断后续。"""
        out = []
        for i, job in enumerate(jobs):
            kw = {**defaults, **job}
            try:
                r = self.generate(**kw)
                r["ok"] = True
                r["index"] = i
            except Exception as e:
                r = {"ok": False, "index": i, "error": str(e), **{k: kw.get(k) for k in ("image", "scene", "prompt", "seed")}}
            out.append(r)
        return out

    def list_scenes(self) -> dict:
        return load_scenes(self.scenes_path)

    def save_scene(self, name: str, prompt: str, negative: str | None = None) -> Path:
        name = (name or "").strip()
        prompt = (prompt or "").strip()
        if not name or not prompt:
            raise ValueError("保存场景需要非空的 name 和 prompt")
        if any(c in name for c in '\\/:*?"<>|'):
            raise ValueError("场景名不要包含路径或特殊符号")
        scenes = load_scenes(self.scenes_path)
        entry = {"prompt": prompt}
        if negative:
            entry["negative"] = negative.strip()
        scenes[name] = entry
        save_scenes(scenes, self.scenes_path)
        global SCENES
        SCENES = {k: v.get("prompt", "") for k, v in scenes.items()}
        return self.scenes_path

    def generate_i2v(
        self,
        *,
        image: str = "portrait_cafe.png",
        scene: str | None = None,
        prompt: str | None = None,
        seed: int = 42,
        length: int = 25,
        prefix: str = "video/Api_i2v",
        on_progress: Callable[[dict], None] | None = None,
        retries: int = 3,
    ) -> dict:
        """LTX 图生视频一条。返回 {prompt_id, files, seconds}。热启动约 20s，冷启动约 70s。"""
        spec = self._validate_i2v(image=image, scene=scene, prompt=prompt, seed=seed, length=length)
        graph = self._build_i2v_graph(spec, prefix)
        client_id = uuid.uuid4().hex
        last_err: Exception | None = None
        delay = 1.0
        for attempt in range(retries):
            try:
                self.ping()
                return self._run_once(graph, client_id, on_progress)
            except (urllib.error.URLError, urllib.error.HTTPError, TimeoutError, ComfyError) as e:
                last_err = e
                if attempt == retries - 1:
                    break
                time.sleep(delay + random.random() * 0.2)
                delay *= 2
        raise ComfyError(f"generate_i2v 失败（已重试 {retries} 次）：{last_err}") from last_err

    def _resolve_prompt(self, scene: str | None, prompt: str | None) -> tuple[str, str]:
        prompt = (prompt or "").strip() or None
        scene = (scene or "").strip() or None
        scenes = load_scenes(self.scenes_path)
        if prompt:
            return prompt, DEFAULT_NEG
        if scene:
            if scene not in scenes:
                names = ", ".join(scenes) or "(空)"
                raise ValueError(f"场景库没有 '{scene}'。已有：{names}。用 save_scene() 保存，或直接传 prompt=")
            entry = scenes[scene]
            text = (entry.get("prompt") or "").strip()
            if not text:
                raise ValueError(f"场景 '{scene}' 的 prompt 为空")
            return text, (entry.get("negative") or DEFAULT_NEG)
        raise ValueError("必须提供 prompt= 自定义提示词，或 scene= 场景库里的名字")

    def _validate(self, **kw) -> dict:
        image = kw["image"]
        if not image or not isinstance(image, str):
            raise ValueError("image 必须是 ComfyUI input 目录下的文件名")
        if "/" in image or "\\" in image:
            raise ValueError("image 只写文件名，不要带路径（文件需已在 ComfyUI-Shared/input/）")
        text, neg = self._resolve_prompt(kw.get("scene"), kw.get("prompt"))
        seed = int(kw["seed"])
        if seed < 0:
            raise ValueError("seed 必须 >= 0")
        depth = float(kw["depth_strength"])
        lora = float(kw["lora_strength"])
        if not 0 <= depth <= 2:
            raise ValueError("depth_strength 应在 0–2")
        if not 0 <= lora <= 2:
            raise ValueError("lora_strength 应在 0–2")
        thr = float(kw.get("identity_threshold", 0.5))
        if not 0 <= thr <= 1:
            raise ValueError("identity_threshold 应在 0–1")
        return {
            "image": image, "prompt": text, "negative": neg, "seed": seed,
            "depth": depth, "lora": lora, "identity_threshold": thr,
            "fail_if_below": bool(kw.get("fail_if_below", False)),
        }

    def _build_graph(self, spec: dict, prefix: str) -> dict:
        graph = deepcopy(json.loads(self.graph_path.read_text(encoding="utf-8")))
        graph["16"]["inputs"]["image"] = spec["image"]
        graph["4"]["inputs"]["text"] = spec["prompt"]
        graph["5"]["inputs"]["text"] = spec["negative"]
        graph["8"]["inputs"]["seed"] = spec["seed"]
        graph["10"]["inputs"]["strength"] = spec["depth"]
        graph["2"]["inputs"]["strength_model"] = spec["lora"]
        graph["15"]["inputs"]["filename_prefix"] = prefix
        graph["14"]["inputs"]["filename_prefix"] = prefix + "_depth"
        if "19" in graph:
            graph["19"]["inputs"]["threshold"] = spec["identity_threshold"]
            graph["19"]["inputs"]["fail_if_below"] = spec["fail_if_below"]
        return graph

    def _validate_i2v(self, **kw) -> dict:
        image = kw["image"]
        if not image or not isinstance(image, str):
            raise ValueError("image 必须是 ComfyUI input 目录下的文件名")
        if "/" in image or "\\" in image:
            raise ValueError("image 只写文件名，不要带路径")
        length = int(kw["length"])
        if length < 9 or length > 129:
            raise ValueError("length 应在 9–129（LTX 用 8n+1：25≈1s，121≈5s）。16GB 已跑通 121")
        seed = int(kw["seed"])
        if seed < 0:
            raise ValueError("seed 必须 >= 0")
        prompt, neg = self._resolve_video_prompt(kw.get("scene"), kw.get("prompt"))
        return {"image": image, "prompt": prompt, "negative": neg, "seed": seed, "length": length}

    def _resolve_video_prompt(self, scene: str | None, prompt: str | None) -> tuple[str, str]:
        prompt = (prompt or "").strip() or None
        scene = (scene or "").strip() or None
        scenes = load_scenes(DEFAULT_VIDEO_SCENES)
        if prompt:
            return prompt, DEFAULT_VIDEO_NEG
        if scene:
            if scene not in scenes:
                names = ", ".join(scenes) or "(空)"
                raise ValueError(f"视频场景库没有 '{scene}'。已有：{names}")
            entry = scenes[scene]
            text = (entry.get("prompt") or "").strip()
            if not text:
                raise ValueError(f"视频场景 '{scene}' 的 prompt 为空")
            return text, (entry.get("negative") or DEFAULT_VIDEO_NEG)
        raise ValueError("必须提供 prompt= 或 scene=（视频场景名）")

    def _build_i2v_graph(self, spec: dict, prefix: str) -> dict:
        graph = deepcopy(json.loads(DEFAULT_I2V_GRAPH.read_text(encoding="utf-8")))
        graph["5"]["inputs"]["image"] = spec["image"]
        graph["14"]["inputs"]["text"] = spec["prompt"]
        graph["15"]["inputs"]["text"] = spec["negative"]
        graph["19"]["inputs"]["noise_seed"] = spec["seed"]
        graph["9"]["inputs"]["value"] = spec["length"]
        graph["27"]["inputs"]["filename_prefix"] = prefix
        return graph

    def _run_once(self, graph: dict, client_id: str, on_progress) -> dict:
        t0 = time.time()
        stop = threading.Event()

        def _ws_loop():
            def cb(msg: dict):
                if on_progress:
                    on_progress(msg)
            try:
                comfy_ws.listen(self.base, client_id, cb, stop)
            except Exception as e:
                if on_progress:
                    on_progress({"type": "ws_error", "data": {"message": str(e)}})

        th = threading.Thread(target=_ws_loop, daemon=True)
        th.start()
        try:
            resp = self._post("/prompt", {"prompt": graph, "client_id": client_id})
        except Exception:
            stop.set()
            raise
        pid = resp.get("prompt_id")
        if not pid:
            stop.set()
            raise ComfyError(f"POST /prompt 无 prompt_id: {resp}")
        if on_progress:
            on_progress({"type": "queued", "data": {"prompt_id": pid}})
        try:
            files, err = self._wait_history(pid)
        finally:
            stop.set()
            th.join(timeout=2)
        if err:
            raise ComfyError(err)
        return {"prompt_id": pid, "files": files, "seconds": round(time.time() - t0, 1)}

    def _wait_history(self, pid: str) -> tuple[list[str], str | None]:
        while True:
            time.sleep(2)
            try:
                h = self._get(f"/history/{pid}", timeout=30)
            except Exception:
                continue
            if pid not in h:
                continue
            job = h[pid]
            st = job.get("status", {})
            if st.get("status_str") == "error":
                msg = "execution error"
                for m in st.get("messages", []):
                    if isinstance(m, (list, tuple)) and m and m[0] == "execution_error":
                        info = m[1] if len(m) > 1 and isinstance(m[1], dict) else {}
                        msg = f"{info.get('node_type')}: {info.get('exception_message')}"
                return [], msg
            if st.get("status_str") == "success" or st.get("completed"):
                files = []
                for node in job.get("outputs", {}).values():
                    for key in ("images", "gifs", "videos", "audio"):
                        for im in node.get(key) or []:
                            fn = im.get("filename")
                            if not fn:
                                continue
                            sub = im.get("subfolder") or ""
                            files.append(f"{sub}/{fn}" if sub else fn)
                return files, None
