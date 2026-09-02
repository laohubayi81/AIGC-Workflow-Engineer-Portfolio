# 环境基线（Day 1）

测试日期：2026-09-01

本文件只记录本机实测，不引用社区数字当自己的结果。

## 硬件

| 项 | 实测 |
|---|---|
| GPU | NVIDIA GeForce RTX 5080 Laptop GPU |
| 显存 | 16303 MiB（nvidia-smi）/ torch 报告 15.92 GB |
| 系统内存 | 33752997888 bytes（约 31.4 GB） |
| 驱动 | nvidia-smi 610.62 |
| CUDA UMD | 13.3（nvidia-smi） |

空闲时显存占用 0 MiB，无其它 GPU 进程。

## ComfyUI

| 项 | 实测 |
|---|---|
| 安装形态 | Comfy Desktop（`D:\Comfy-Desktop`） |
| ComfyUI 版本 | 0.28.2（`comfyui_version.py` / `pyproject.toml`） |
| git | `306af3a8771a8232d26bd20acbfc6b07f862ad2b`（tag `v0.28.2`） |
| 代码路径 | `D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI` |
| 运行 Python | `D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\.venv\Scripts\python.exe` |
| Python | 3.13.12 |
| PyTorch | 2.10.0+cu130 |
| torch CUDA | 13.0 |
| 模型 / 输入 / 输出 | `D:\Comfy-Desktop\ComfyUI-Shared\` |
| Web UI | `http://127.0.0.1:8188`（当日日志有启动记录） |

Installer manifest 仍写 `v0.20.1-env1`，实际仓库已更新到 0.28.2，以 git / `comfyui_version.py` 为准。

## 自定义节点

| 节点 | 版本 | 备注 |
|---|---|---|
| ComfyUI-GGUF | pyproject 1.1.10 | 目录无独立 git |
| comfyui-kjnodes | pyproject 1.4.7 | 目录无独立 git；`PatchTritonVAE` 因缺 triton 未加载 |
| comfyui-krea2edit | pyproject 1.2.5 | git `86f886dac23013d88996e3a2e99093ba44d322fb` |

## 已装模型（文件名，未算 hash）

路径根：`D:\Comfy-Desktop\ComfyUI-Shared\models\`

| 文件 | 角色 |
|---|---|
| `diffusion_models/krea2_turbo_nvfp4.safetensors` | Krea 2 Turbo 推理（NVFP4） |
| `loras/krea2_darkbrush.safetensors` | 现成 LoRA，非本计划训练产物 |
| `loras/krea2_identity_edit_v1_2.safetensors` | 现成 LoRA，非本计划训练产物 |
| `text_encoders/qwen3vl_4b_fp8_scaled.safetensors` | Krea 2 文本编码器 |
| `vae/qwen_image_vae.safetensors` | 图像 VAE |
| `unet/ltx-2.3-22b-distilled-1.1-Q4_K_S.gguf` | LTX 2.3 量化 |
| `text_encoders/ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | LTX 文本侧 |
| `text_encoders/gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` | LTX / Gemma |
| `text_encoders/mmproj-BF16.gguf` | mmproj |
| `vae/ltx-2.3-22b-distilled_video_vae.safetensors` | LTX 视频 VAE |
| `vae/ltx-2.3-22b-distilled_audio_vae.safetensors` | LTX 音频 VAE |
| `latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | LTX 空间超分 |

**缺口（训练前必须补）：** 本机目前只有 Krea 2 **Turbo NVFP4**，没有 Krea 2 **Raw**。计划要求 Raw 训 LoRA、Turbo 推理。Day 3 训练前需下载 Raw，或明确改用 Turbo + training adapter 并在日志里写清。

## AI-Toolkit（Day 1 已冒烟）

安装不在本仓库内，路径：`D:\ai-toolkit`。

| 项 | 实测 |
|---|---|
| 来源 | https://github.com/ostris/ai-toolkit |
| git | `9d6a9a0803656e903284785d891cd9e7a3a27fac`（`version.py` = 0.13.4） |
| 系统 Python | 3.12.10（`python -m venv D:\ai-toolkit\venv`） |
| PyTorch | 2.13.0+cu130 |
| torch CUDA | 13.0 |
| `torch.cuda.is_available()` | True |
| GPU | NVIDIA GeForce RTX 5080 Laptop GPU |
| 冒烟命令 | `D:\ai-toolkit\venv\Scripts\python.exe run.py -h` |
| 冒烟结果 | 2026-09-01 退出码 0，打印 argparse help（需要 config 文件才会真正开训） |

安装步骤（本机已执行）：官方 README 的 Windows 手动安装——venv → `torch==2.13.0` / `torchvision==0.28.0` / `torchaudio==2.11.0`（cu130）→ `pip install -r requirements.txt`。torch 轮子约 1.9GB，下载中途断过一次，pip 自动续传后成功。

真正开训用：`python run.py config/<your>.yml`。仓库 `config/examples/` 没有现成 Krea 2 yaml，Day 3 要自己写或走 UI。

## 成本口径（计划约定，尚未用于实测任务）

本地 5080 laptop 显卡部分约 8000 元 ÷ 3 年 ÷ 8760 小时 ≈ 0.3 元/小时 + 电费约 0.1 元/小时 = **约 0.4 元/小时**。单件成本 = 0.4 ÷ 每小时生成数量。后续 benchmark 用这个口径，并写明「估算」。
