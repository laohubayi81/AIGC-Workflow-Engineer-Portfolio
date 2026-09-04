# 视频模型生态对比（Day 15）

本机实测列只填已经装上的。没装的不编数字。

| | LTX 2.3 | Wan | HunyuanVideo | CogVideoX | MiniMax Hailuo / H3 |
|---|---|---|---|---|---|
| 谁做的 | Lightricks | 阿里 | 腾讯 | 智谱 | MiniMax |
| 开源权重 | 是（有蒸馏 / GGUF） | 是（1.3B / 14B 等） | 是 | 是 | 偏 API / 闭源产品 |
| 本机 | **已装** distilled 22B **Q4_K_S GGUF** + Gemma + video/audio VAE + x2 latent upscaler | 未装 | 未装 | 未装 | 不装权重 |
| 16GB 可行性 | Q4 量化后可试（紧）；全量 22B 不行 | **1.3B** 适合 16GB；14B 吃力 | 多数量化版，仍偏重 | 2B 档可试 | 走云 API |
| 擅长 | 较短镜头、消费级量化路径清楚 | 中文社区、I2V、可控性讨论多 | 画质/时长宣传强 | 学术+开源生态 | 产品级文生视频 |
| Day 15 角色 | **基线 A（已跑通 I2V）** | **基线 B（LTX 通了再下 1.3B，尚未装）** | 对比表，本周不装 | 对比表 | 对比表，不作为本地流水线 |
| 本机 I2V 计时 | 冷启动约 **70s** / 只换图约 **20s**（384×576×25f≈1s）；Length **121≈5s** 用户计时约 **320s**，16GB 跑通 | 未测 | — | — | — |

## 本机 LTX 文件（`ComfyUI-Shared/models/`）

| 路径 | 约 |
|---|---|
| `unet/ltx-2.3-22b-distilled-1.1-Q4_K_S.gguf` | 12.4 GB |
| `text_encoders/gemma-3-12b-it-qat-UD-Q4_K_XL.gguf` | 7.1 GB |
| `text_encoders/mmproj-BF16.gguf` | 0.8 GB |
| `text_encoders/ltx-2.3-22b-distilled_embeddings_connectors.safetensors` | 2.2 GB |
| `vae/ltx-2.3-22b-distilled_video_vae.safetensors` | 1.4 GB |
| `vae/ltx-2.3-22b-distilled_audio_vae.safetensors` | 0.3 GB |
| `latent_upscale_models/ltx-2.3-spatial-upscaler-x2-1.0.safetensors` | 0.9 GB |

unet + gemma 合计已超 19GB，**不能同时整模进 16GB**。必须 GGUF 分层卸载（CPU offload）。跑不通就记 VRAM 报错，不要硬上 14B Wan。

## 本机图生视频 JSON（Day 15）

官方 `Image to Video (LTX-2.3)` 是 UUID 子图，画布改不了。按已跑通的文生视频做成可编辑图：[`LTX2.3_i2v.json`](./LTX2.3_i2v.json)。说明：[docs/ltx-i2v.md](../docs/ltx-i2v.md)。

- 写真 → `LTXVImgToVideoInplace` 写入第一帧
- 仍拼接音频潜空间（LTX 2.3 是音视频模型），不解码声音
- 关掉 prompt 扩写和二段空间放大，给 16GB 冒烟
- 默认 384×576、Length 25、8 step、CFG 1、seed 42

## 本周流水线怎么接

数字人写真（Week 2）出的静帧 → 视频侧做：短镜头生成（LTX/Wan）→ 换脸（Day 16）→ 超分+插帧（Day 17）→ 时序（Day 18）拼成 15+ 节点。

Day 16 静帧+视频已通（ReActor + inswapper；restore=none）。视频图：[`reactor_video.json`](./reactor_video.json)。成片 `ReActor_i2v_00001/00002`。说明：[docs/day16-faceswap.md](../docs/day16-faceswap.md)。

Day 17 后处理已通：[`day17_upscale_rife.json`](./day17_upscale_rife.json)（4x-UltraSharp + RIFE 2x）。成片 `Day17_upscale_rife_00001_.mp4`，用户计时 **58.3 s**。说明：[docs/day17-upscale-rife.md](../docs/day17-upscale-rife.md)。

Day 18 时序：[`LTX2.3_i2v_flf.json`](./LTX2.3_i2v_flf.json) 首尾帧（咖啡馆→操场）。IC-LoRA / IP-Adapter 无本机权重。说明：[docs/day18-temporal.md](../docs/day18-temporal.md)。
