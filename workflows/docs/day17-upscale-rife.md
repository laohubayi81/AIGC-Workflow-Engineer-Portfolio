# Day 17 超分 + 插帧

JSON：[`../video-modules/day17_upscale_rife.json`](../video-modules/day17_upscale_rife.json)

| | |
|---|---|
| 输入 | `input/post_in.mp4`（`ReActor_i2v_00002_.mp4` 拷贝） |
| 超分 | 原生 `UpscaleModelLoader` + `ImageUpscaleWithModel`，`4x-UltraSharp.pth`（hf-mirror，66.9MB） |
| 插帧 | `RIFE VFI`，`rife49.pth`，multiplier **2**（约 24→48fps） |
| 成片 | `output/video/Day17_upscale_rife_00001_.mp4`（2.14MB；输入换脸片 250KB。用户确认跑通） |
| 耗时 | **58.3 s**（用户计时，未测显存峰值） |

## 本机取舍

- GitHub / huggingface.co 连不上，权重走 **hf-mirror**，节点 zip 走 **ghproxy.net**。
- Frame-Interpolation 全量 import 会拉 cupy（CUDA 13 + Python 3.13 没轮子）。`__init__.py` **只注册 RIFE**，其它 VFI 模型本周不用。
- 未跑 `install.py`（会装 cupy）。
- 4x 后再 RIFE，16GB 可能紧。爆显存：把 **Upscale Image** Bypass，只插帧。

## 点哪里

1. **关掉再打开 ComfyUI**（新节点必须重启）
2. 打开工作流 **`day17_upscale_rife`**
3. Load Video = `post_in.mp4`
4. Queue
5. 成片在 `D:\Comfy-Desktop\ComfyUI-Shared\output\video\Day17_upscale_rife_*.mp4`
