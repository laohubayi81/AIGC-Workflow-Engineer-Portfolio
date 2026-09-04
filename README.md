<div align="center">

# 🎨 AIGC Workflow Engineer Portfolio

**面向 AIGC 工作流工程师（ComfyUI 方向）的 6 周实战作品集**

> 能演示 · 能复现 · 能测量 · 能解释 —— 仓库里所有数字均为实测，没有数据就不写

![Progress](https://img.shields.io/badge/进度-Week%203%20视频流水线-2ea44f?style=flat-square)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Krea%202%20%2F%20LTX%202.3-blue?style=flat-square)
![LoRA](https://img.shields.io/badge/LoRA-Musubi%20Tuner%20v0.3.4-orange?style=flat-square)
![GPU](https://img.shields.io/badge/本地-RTX%205080%20Laptop%2016GB-8a2be2?style=flat-square)
![计划](https://img.shields.io/badge/6周计划-v4%20精简执行版-red?style=flat-square)

</div>

---

## ✨ 亮点成果 · Week 1：Krea 2 人物 LoRA + 推理端集成

39 张自拍 → 自然语言打标（Qwen3-VL caption）→ 云端 RTX 4090D 训练 48 分钟（1200 步，**rank 32**）→ **身份还原成功** → Day 5 接入 Depth CN-LoRA 与 Identity Edit。

| 无 LoRA | + LoRA（step900 · strength 0.85 · seed 42） |
|---|---|
| ![无 LoRA](Week1/Day3/samples/comparison/comparison_no-lora_step900_s42.png) | ![有 LoRA](Week1/Day3/samples/comparison/comparison_with-lora_s0.85_step900_s42.png) |

同样的 prompt、同样的 seed，仅添加 LoRA：人物从随机中年女性变为目标人物。InsightFace vs 自拍：无 LoRA **0.05** → 有 LoRA **0.62**（权重扫到 1.2 为 0.67）。

完整训练流程 → **[Week 1 训练报告](Week1/Day3/training_report.md)**。Day 4 评估 → [InsightFace](lora-training/benchmarks/2026-09-03-insightface-similarity.md) · [触发词泄漏](Week1/Day3/training_report.md#55-触发词泄漏系统验证day-4-补测)。

### Day 5 · 换场景 / 换装，身份仍在

Krea 2 无 IP-Adapter。人像拆成两条（各配 myface @0.85，seed 42，RAW FP8）：

**Depth CN-LoRA** 锁取景：同一张自拍深度图 +「公园近景、看镜头」。1.0 更贴自拍构图（身份 0.66）；0.6 更听 prompt（0.55）。

| Depth strength 1.0 | Depth strength 0.6 |
|---|---|
| ![B 1.0](Week1/Day5/samples/b_v3_s1.0.png) | ![B 0.6](Week1/Day5/samples/b_v3_s0.6.png) |

**Identity Edit** 按指令换装换背景（须挂 `krea2_identity_edit` LoRA）。白底黑 T，ref_boost 越高越像参考脸（0.68 → 0.73），场景不会被拷回来。

| ref_boost 1.0 | 4.0（推荐） | 8.0 |
|---|---|---|
| ![A 1.0](Week1/Day5/samples/a_v2_rb1.0.png) | ![A 4.0](Week1/Day5/samples/a_v2_rb4.0.png) | ![A 8.0](Week1/Day5/samples/a_v2_rb8.0.png) |

组件边界（身份 / 结构 / 编辑各自由谁负责）→ **[Day 5 报告](Week1/Day5/README.md)**。工作流 JSON：[`day5_routeB_depth_controlnet.json`](lora-training/workflows/day5_routeB_depth_controlnet.json) · [`day5_routeA_krea2edit.json`](lora-training/workflows/day5_routeA_krea2edit.json)。

## ✨ Week 2：数字人写真生产链（API + 队列）

把路线 B 收成可调度的写真：**自拍 → Depth 锁构图 → myface 保身份 → prompt 换场景**。不是新模型，也没有假超分（成片 768）。

| 咖啡馆 | 操场 | 海边（柔光） |
|---|---|---|
| ![cafe](workflows/samples/portrait_cafe.png) | ![playground](workflows/samples/portrait_playground.png) | ![beach](workflows/samples/portrait_beach.png) |

| 项 | 实测（RTX 5080 Laptop 16GB · RAW FP8） |
|---|---|
| 单张 | **57.3 s**（P50=P90，几乎无长尾） |
| 显存 | **14238 MiB** |
| 单张成功率 | 20/20 = **100%** |
| 队列 | CSV **50/50** 成功，断点续跑有效 |
| 成本 | 本地估算 **0.006 元/张**；按 AutoDL 2.18 元/h → **0.035 元/张** |

- 画布 JSON：[digital_portrait.json](workflows/digital_portrait.json) · [说明](workflows/docs/digital-portrait.md)
- HTTP API（UI JSON ≠ API Format）：[portrait_api.json](workflows/api/portrait_api.json) · [`ComfyClient.generate()`](agent-project/src/comfy_client.py)（WebSocket 进度）
- 场景库可自写中文再存英文 prompt：[scenes.json](workflows/queue/scenes.json) · Skill `digital-portrait`
- 性能 / 队列统计：[Day 9](workflows/benchmarks/2026-09-03-portrait-bench.md) · [Day 12](workflows/benchmarks/2026-09-03-queue-50.md)

## ✨ Week 3：视频流水线（LTX 2.3 · 16GB 分段）

写真静帧 → LTX 图生视频 →（可选）换脸 → 超分 + RIFE。16GB **不能**把生成、换脸、超分打进同一次 Queue。Wan 1.3B 未装；MiniMax H3 不当地本地底模。

| 专项 | 图 / 成片 | 实测 |
|---|---|---|
| 生成 | [`LTX2.3_i2v.json`](workflows/video-modules/LTX2.3_i2v.json) | 25f≈1s：冷约 **70s** / 热约 **20s**；121f≈5s：约 **320s** |
| 换脸 | [`reactor_video.json`](workflows/video-modules/reactor_video.json) | 静帧 + 逐帧视频通；GFPGAN 下残、restore=none |
| 超分+插帧 | [`day17_upscale_rife.json`](workflows/video-modules/day17_upscale_rife.json) | **58.3 s**（4x-UltraSharp + RIFE 2x） |
| 时序 | [`LTX2.3_i2v_flf.json`](workflows/video-modules/LTX2.3_i2v_flf.json) 32 节点 | 首尾帧 **73.5 s**；1.4s 切大场景会生硬 |
| API | [`i2v_api.json`](workflows/api/i2v_api.json) · `generate_i2v()` | 分镜 CSV **5/5**，墙钟 **155 s**（热路径约 38s） |

生态表：[ecosystem.md](workflows/video-modules/ecosystem.md)。口型（Day 20）跳过。

## 🧭 模块导航

| 模块 | 说明 | 状态 |
|---|---|---|
| 🧪 [lora-training](./lora-training/) | Krea 2 LoRA 训练、评估、调参、推理端集成 | ✅ Week 1 |
| 🖼️ [workflows](./workflows/) | 数字人写真 + LTX 视频分段流水线 + API | ✅ Week 2–3 |
| 🧩 [custom-nodes](./custom-nodes/) | 1 个有业务价值的自定义节点 | ⬜ Week 4 |
| 🤖 [agent-project](./agent-project/) | Comfy 客户端已落地；Agent 状态机 ⬜ Week 5 | 🚧 API 先行 |

## 🛠️ 技术栈

| 类别 | 工具 / 硬件 |
|---|---|
| 工作流 | ComfyUI（Krea 2 RAW FP8 · LTX 2.3 量化版） |
| 训练 | Musubi Tuner v0.3.4 · 恒源云 RTX 4090D 24GB（BF16 权重，运行时 FP8） |
| 推理 | Krea 2 RAW FP8 · Depth CN-LoRA · krea2edit Identity Edit · Qwen3-VL |
| 调度 | ComfyUI `/prompt` + `/ws` · CSV 串行队列 |
| 本地环境 | RTX 5080 Laptop 16GB + 32GB RAM（[环境基线](./lora-training/benchmarks/2026-09-01-environment.md)） |

## 📈 Week 1 进度

- [x] Day 1 · 建仓 + 环境记录 + AI-Toolkit 安装
- [x] Day 2 · 数据集（39 张自拍）+ 自然语言打标
- [x] Day 3 · 云端训练 1200 步（48 min）+ 6 场景效果评估
- [x] Day 4 · InsightFace 相似度评估（权重扫描 0.41→0.67）+ 触发词泄漏验证（0.57 vs 基线 0.05）
- [x] Day 5 · Depth CN-LoRA + krea2edit Identity Edit 集成（IP-Adapter 无 Krea 2 方案）
- [x] Day 6 · 缓冲（跳过 rank=16 对照，完成标准不要求）
- [x] Day 7 · 周复盘（AutoDL 成本 1.74 元 + Day 5 产物入库）

## 📈 Week 2 进度

- [x] Day 8 · 数字人写真工作流（路线 B 生产封装 + 场景套餐）
- [x] Day 9 · 性能成本：57.3 s/张 · 13.9GB · 100%
- [x] Day 10 · API Format + 最小 HTTP 调用
- [x] Day 11 · `generate()` / WS 进度 / 场景库
- [x] Day 12 · CSV 队列 50/50
- [x] Day 13 · 缓冲（跳过，无必做项）
- [x] Day 14 · 周复盘入库

## 📈 Week 3 进度

- [x] Day 15 · 生态表 + LTX I2V（Wan 1.3B 未装）
- [x] Day 16 · ReActor 静帧 + 视频逐帧
- [x] Day 17 · 4x-UltraSharp + RIFE，58.3 s
- [x] Day 18 · 首尾帧，73.5 s
- [x] Day 19 · 视频 API 5/5
- [x] Day 20 · 口型跳过
- [ ] Day 21 · 推 GitHub + 开始投递

完整 6 周路线图与逐日执行状态 → **[ROADMAP.md](./ROADMAP.md)**（打开项目先看这里）

## 📮 联系方式

- GitHub：[laohubayi81](https://github.com/laohubayi81)

<!-- TODO: 补充邮箱 / 微信 / 简历链接 / 技术博客链接 -->
