# SDXL 补测 · 基线数据（2026-09-04）

> 目的：补齐 SD/SDXL 生态字面缺口（3/5 目标 JD 点名），建立 SDXL 底座基线，为后续 SDXL LoRA 对照实验（09-11 下单）做铺垫。
> 全程 API 排队（`/prompt` 串行 ×4），无人工干预。

## 环境

- RTX 5080 Laptop 16GB · ComfyUI 0.34.2 · `.venv`（torch 2.10.0+cu130）
- 模型：`sd_xl_base_1.0.safetensors`（6,938,078,334 字节，HF 官方 base-1.0）

## 参数

- 1024×1024 · steps 30 · CFG 7.0 · dpmpp_2m / karras · seed 42 · batch 1
- 负向：blurry, low quality, distorted, deformed, watermark, extra limbs

## 结果

| # | 场景 | 耗时 | 产物 |
|---|---|---|---|
| 1 | portrait（人像/棚拍） | **14.1s**（含模型首次加载） | `SdxlBench/portrait_1_00001_.png` |
| 2 | street（夜景街拍） | **12.1s** | `SdxlBench/street_2_00001_.png` |
| 3 | product（产品静物） | **12.1s** | `SdxlBench/product_3_00001_.png` |
| 4 | landscape（幻想风景） | **12.1s** | `SdxlBench/landscape_4_00001_.png` |

- **成功率 4/4** · 热路径稳定 **12.1s/张**（1024×1024 · 30 步）
- **显存峰值 7.93 GiB**（/system_stats 1s 采样；总 15.92 GiB）
- 首张 14.1s 含 SDXL 权重加载（约 +2s），无长尾

## 与 Krea 2 基线对照（不同定位，非优劣关系）

| | Krea 2 RAW FP8 | SDXL base 1.0 |
|---|---|---|
| 分辨率 | 768×768 | 1024×1024 |
| 单张 | 57.3s（P50） | **12.1s** |
| 显存峰值 | 14.2 GB | **7.9 GB** |
| 身份定制 | myface LoRA + Identity Edit（核心能力） | 原生无（待 LoRA 对照） |
| 定位 | 身份还原主力 | 生态兼容 + 高吞吐出图 |

结论：SDXL 快 4.7 倍、省显存一半、原生 1024——适合**高吞吐与生态兼容场景**；身份还原仍走 Krea 2 管线。两条管线互补，组合使用（SDXL 出图 → 超分/其他下游）是后续实验方向。

## 方法说明

- 排队方式：`POST /prompt` 串行 4 任务，`/history` 轮询
- 显存采样：独立线程 1s 间隔读 `/system_stats`（vram_total − vram_free 取最大值），非官方 peak 计数器，数值略保守
- 脚本：`.tmp_dl/sdxl_bench.py`（可复用，改 PROMPTS 即可）

## 待办

- [ ] IP-Adapter 接入测试（需装 ComfyUI_IPAdapter_Plus，SDXL 生态版）
- [ ] SDXL LoRA 训练对照（09-11 AutoDL 下单，与 Krea 2 版同数据集）
