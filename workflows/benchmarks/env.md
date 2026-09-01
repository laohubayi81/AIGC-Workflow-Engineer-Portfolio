# 环境基线（Day 1）

测试日期：2026-09-01

本文件只记录本机实测，不引用社区数字当自己的结果。不记录本机绝对路径。

## 硬件

| 项 | 实测 |
|---|---|
| GPU | NVIDIA GeForce RTX 5080 Laptop GPU |
| 显存 | 16303 MiB（nvidia-smi）/ torch 报告 15.92 GB |
| 系统内存 | 约 32 GB |
| 驱动 | nvidia-smi 610.62 |
| CUDA UMD | 13.3（nvidia-smi） |

记录当日空闲、无其它 GPU 进程。

## ComfyUI

| 项 | 实测 |
|---|---|
| 安装形态 | Comfy Desktop |
| ComfyUI 版本 | 0.28.2 |
| git | `306af3a8771a8232d26bd20acbfc6b07f862ad2b`（tag `v0.28.2`） |
| Python | 3.13.12（ComfyUI 运行时 venv） |
| PyTorch | 2.10.0+cu130 |
| torch CUDA | 13.0 |
| Web UI | 本机 `127.0.0.1:8188`（当日日志有启动记录） |

Installer manifest 仍写 `v0.20.1-env1`，实际仓库已更新到 0.28.2，以 git / `comfyui_version.py` 为准。

## 自定义节点

| 节点 | 版本 | 备注 |
|---|---|---|
| ComfyUI-GGUF | pyproject 1.1.10 | 目录无独立 git |
| comfyui-kjnodes | pyproject 1.4.7 | 目录无独立 git；`PatchTritonVAE` 因缺 triton 未加载 |
| comfyui-krea2edit | pyproject 1.2.5 | git `86f886dac23013d88996e3a2e99093ba44d322fb` |

## 已装模型（仅文件名，未算 hash）

| 文件 | 角色 |
|---|---|
| `krea2_turbo_nvfp4.safetensors` | Krea 2 Turbo 推理（NVFP4） |
| `krea2_darkbrush.safetensors` | 现成 LoRA，非本计划训练产物 |
| `krea2_identity_edit_v1_2.safetensors` | 现成 LoRA，非本计划训练产物 |
| `qwen3vl_4b_fp8_scaled.safetensors` | Krea 2 文本编码器 |
| `qwen_image_vae.safetensors` | 图像 VAE |
| `ltx-2.3-22b-distilled-1.1-Q4_K_S.gguf` | LTX 2.3 量化 |
| `ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | LTX 文本侧 |
| `gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` | LTX / Gemma |
| `mmproj-BF16.gguf` | mmproj |
| `ltx-2.3-22b-distilled_video_vae.safetensors` | LTX 视频 VAE |
| `ltx-2.3-22b-distilled_audio_vae.safetensors` | LTX 音频 VAE |
| `ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | LTX 空间超分 |

**缺口（训练前必须补）：** 本机目前只有 Krea 2 **Turbo NVFP4**，没有 Krea 2 **Raw**。计划要求 Raw 训 LoRA、Turbo 推理。Day 3 训练前需下载 Raw，或明确改用 Turbo + training adapter 并在日志里写清。

## AI-Toolkit（Day 1 已冒烟）

| 项 | 实测 |
|---|---|
| 来源 | ostris/ai-toolkit |
| git | `9d6a9a0803656e903284785d891cd9e7a3a27fac`（`version.py` = 0.13.4） |
| 系统 Python | 3.12.10（独立 venv，不与 ComfyUI 混用） |
| PyTorch | 2.13.0+cu130 |
| torch CUDA | 13.0 |
| `torch.cuda.is_available()` | True |
| GPU | NVIDIA GeForce RTX 5080 Laptop GPU |
| 冒烟 | `python run.py -h` 退出码 0 |
| import 验证 | 在 AI-Toolkit 目录下 `from toolkit.job import get_job` 成功 |

安装按官方 Windows 手动步骤：venv → `torch==2.13.0` / `torchvision==0.28.0` / `torchaudio==2.11.0`（cu130）→ `pip install -r requirements.txt`。RTX 5080 使用 cu130，未使用 cu121。

真正开训用：`python run.py config/<your>.yml`。`config/examples/` 没有现成 Krea 2 yaml，Day 3 要自己写或走 UI。

## 成本口径（计划约定，尚未用于实测任务）

本地 5080 laptop 显卡部分按计划估算约 0.3 元/小时 + 电费约 0.1 元/小时 = **约 0.4 元/小时**。单件成本 = 0.4 ÷ 每小时生成数量。后续 benchmark 用这个口径，并写明「估算」。
