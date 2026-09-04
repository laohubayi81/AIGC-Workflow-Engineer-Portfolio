# Day 18 时序一致性

本机视频主干是 **LTX 2.3 distilled GGUF**，不是 Wan / Hunyuan。能落地的时序手段是 **首尾帧**（`LTXVImgToVideoInplace` + `LTXVAddGuide`）。

JSON：[`../video-modules/LTX2.3_i2v_flf.json`](../video-modules/LTX2.3_i2v_flf.json)（32 节点）

## 边界（不编方案）

| 计划项 | 本机 |
|---|---|
| 首帧 | 有。Day 15 已用 `LTXVImgToVideoInplace` |
| 尾帧 | 有。`LTXVAddGuide`，`frame_idx = -1` |
| IC-LoRA | 节点可选口有；**没有** LTX 用的 IC-LoRA 权重。不下 Wan 的 IC-LoRA |
| IP-Adapter | 与 Day 5 相同：只覆盖 SD1.5 / SDXL / Flux，**无** Krea / LTX 版 |

## 冒烟怎么看

| | |
|---|---|
| 第一帧 | `portrait_cafe.png` |
| 最后一帧 | `portrait_playground.png`（Week 2 同一套写真） |
| Length | 25（约 1s @ 24fps） |
| 成片 | `output/video/LTX_flf_00001_.mp4`（384×576，24fps，33 帧 / **1.375 s**） |
| 耗时 | **73.5 s**（用户计时） |

片尾像幻灯片、很生硬：**不是帧率太低**。24fps 正常；1.4 秒里从咖啡馆切到操场，蒸馏 8 步只能变形过渡。RIFE 插帧也救不了构图跳变。要顺：拉长 Length，或首尾改成同一场景的两张图，尾帧 strength 可降到 0.6。

片头应接近咖啡馆，片尾接近操场，中间是模型插出来的运动。身份仍靠写真本身，不是 ReActor。

不要和换脸 / 超分叠在同一张图画布（16GB：unet 12.4GB + Gemma 7.1GB 已经满）。

坑：`LTXVAddGuide` 不能接在 `LTXVConcatAVLatent` 后面。2.3 的 AV latent 是 NestedTensor，`noise_mask.clone()` 会报 `'NestedTensor' object has no attribute 'clone'`。正确顺序：首帧写入视频 latent → **AddGuide 尾帧** → 再拼音频。

## 15+ 节点流水线（分段，不是一张图）

16GB 不能把 LTX + ReActor + 4x + RIFE 塞进一次 Queue。作品集按三段讲，节点合计 45：

| 段 | 图 | 节点 | 作用 |
|---|---|---|---|
| A 生成+时序 | `LTX2.3_i2v_flf.json` | 32 | 首尾帧 I2V |
| B 换脸 | `reactor_video.json` | 6 | 逐帧 ReActor（身份漂了才用） |
| C 后处理 | `day17_upscale_rife.json` | 7 | 4x-UltraSharp + RIFE 24→48，**58.3 s** |

面试口径：生产路径是分段流水线；一张图硬拼会 OOM。
