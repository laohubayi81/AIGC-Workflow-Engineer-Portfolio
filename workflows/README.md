# 工作流

第 2–3 周核心：1 个 10+ 节点图像生产工作流，以及 1 个 15+ 节点视频生产流水线（换脸 / 超分 / 帧插值 / 时序一致性）。

## 核心功能

- 图像：批量输入 → 预处理 → ControlNet → LoRA → 生成 → 后处理 → 批量输出
- 视频：生成 → 一致性控制 → 换脸 → 超分 → 帧插值
- 每个工作流附 JSON、使用说明、效果预览和 benchmark

## 效果展示

- **数字人写真（Day 8）**：[digital_portrait.json](./digital_portrait.json) · [使用说明](./docs/digital-portrait.md)
  - 主干 = Week 1 路线 B（Depth + myface）；增量 = 输入统一 768 + 固定 Depth 0.8 + 三场景套餐
  - **不是**新模型和超分；768 即成片
  - Day 9 实测（5080 16GB，n=20）：**57.3 s/张** · 显存 13.9GB · 成功率 100% · [benchmark](./benchmarks/2026-09-03-portrait-bench.md)
  - Day 12 队列 50 张：100% 成功 · [统计](./benchmarks/2026-09-03-queue-50.md)
- **视频（Week 3，16GB 分段）**
  - 生成 [`video-modules/LTX2.3_i2v.json`](./video-modules/LTX2.3_i2v.json)：25f≈1s 冷约 70s / 热约 20s；121f≈5s 约 320s
  - 换脸 / 超分+RIFE **58.3 s** / 首尾帧 **73.5 s**（32 节点）
  - API [`api/i2v_api.json`](./api/i2v_api.json) 分镜 5/5、墙钟 155s · [Day 19](./benchmarks/2026-09-04-video-api.md)
  - 生态表：[video-modules/ecosystem.md](./video-modules/ecosystem.md)

## 技术栈

ComfyUI 0.34.2 · Krea 2 RAW FP8 · LTX 2.3 Q4 GGUF · Depth CN-LoRA · myface LoRA rank 32 · ReActor · 4x-UltraSharp · RIFE。模型见 `lora-training/benchmarks/`。

## 安装 / 使用

- 画布：`digital_portrait.json`
- HTTP：`api/portrait_api.json` + `python workflows/api/generate_portrait.py`
- 封装：`python agent-project/examples/generate_one.py`
- 队列：`python agent-project/examples/run_queue.py`
- 场景库：`queue/scenes.json`（`save_scene.py` 增改）
- 中文出图：Skill `digital-portrait`
- 图生视频：`video-modules/LTX2.3_i2v.json`（[说明](./docs/ltx-i2v.md)）
- 视频 API：`python agent-project/examples/generate_i2v.py` · 分镜 `python agent-project/examples/run_video_queue.py --limit 5`

说明：[docs/digital-portrait.md](./docs/digital-portrait.md) · [docs/comfy-api.md](./docs/comfy-api.md) · [docs/ltx-i2v.md](./docs/ltx-i2v.md) · [docs/day16-faceswap.md](./docs/day16-faceswap.md) · [docs/day17-upscale-rife.md](./docs/day17-upscale-rife.md) · [docs/day18-temporal.md](./docs/day18-temporal.md) · [docs/day19-video-api.md](./docs/day19-video-api.md)。
