# 简历项目段落（v1 草稿 · 数字全部有 GitHub 支撑）

> 用法：Day 37 简历定稿时直接从这里摘。每个项目 = 一句话定位 + 4~5 条要点 + 技术栈 + 证据锚点。
> 红线在文末：哪些词不能写，写了就是注水。

---

## 先记住一条主线（面试先讲线，再讲点）

**模型层 → 工作流层 → 服务层 → 质量层**（+ Agent 层，Week 5 启用）：

1. **模型层**：训练一个"自己"的人物 LoRA——会做数据、会训练、会评估、会集成
2. **工作流层**：把它封装成 10+ 节点的 ComfyUI 生产工作流——能出片、可换景
3. **服务层**：API 化 + 批量队列 + 监控——可量产、可计价、可交接
4. **质量层**：交付门禁自定义节点 + 成本对比——不合格不入库，每张图有价签

仓库里每一个 Week 都是这条栈上的一层。没有零散，只有没讲出来的顺序。

---

## 项目一 · Krea 2 人物 LoRA 全链路（训练 → 评估 → 集成）

**一句话**：从 39 张自拍训练出"数字分身"LoRA，用非人眼指标闭环验证到推理端集成。

- **数据**：39 张自拍，Qwen3-VL 自然语言打标（触发词 ohwx）
- **训练**：Musubi Tuner · 云端 RTX 4090D · 768px + cached latents · 1200 步 48 min · 成本 1.74 元
- **评估**：InsightFace 余弦相似度 0.05（无 LoRA 基线）→ 0.67（权重 1.2）；触发词泄漏 2×2 矩阵量化（0.57 vs 0.05）
- **集成**：Krea 2 无 IP-Adapter（留证）→ 双路线替代：Depth CN-LoRA 锁构图（strength 0.6/1.0）+ krea2edit Identity Edit 按指令换装换景（ref_boost 1/4/8），峰值相似度 **0.73**
- **技术栈**：Musubi Tuner · Krea 2 RAW FP8 · ComfyUI · InsightFace · Python
- **证据**：`Week1/Day3/training_report.md` · `lora-training/benchmarks/` · `Week1/Day5/README.md`

## 项目二 · 数字人写真生产链（工作流 → API → 批量队列）

**一句话**：把 LoRA 能力封装成可量产、可计价的生产服务。

- **工作流**：10+ 节点（预处理 → Depth CN 0.8 → LoRA → 生成 → 成片），三场景已出片
- **API**：ComfyUI `/prompt` + WebSocket 进度封装 `ComfyClient`（指数退避、失败重试、场景参数外注）
- **队列**：CSV 驱动 50 张，成功率 100%，断点续跑有效
- **性能成本**：n=20 成功率 100% · P50 **57.3s** · 显存峰值 **14.2GB** · 单张 **0.006 元**（本地）/ 0.035 元（云端 AutoDL）
- **技术栈**：Python · requests/websocket · ComfyUI API
- **证据**：`workflows/benchmarks/2026-09-03-portrait-bench.md` · `2026-09-03-queue-50.md` · `agent-project/src/comfy_client.py`

## 项目三 · 视频生产流水线（生成 → 换脸 → 后处理 → 队列）

**一句话**：16GB 显存下的视频多段流水线：能跑通、有数字、知道为什么分段。

- **生成**：LTX 2.3 I2V 图生视频——1s 视频热路径 38s；5s 视频约 320s
- **后处理**：4x-UltraSharp 超分 + RIFE 24→48fps 全链 **58.3s**；换脸 ReActor（静帧 + 逐帧）
- **时序一致性**：首尾帧 32 节点工作流 **73.5s**
- **队列**：分镜 CSV **5/5**，墙钟 155s
- **架构取舍**：生成/换脸/后处理不进同一 Queue（16GB 会 OOM）→ 按 A 生成 / B 换脸 / C 后处理三段编排
- **技术栈**：LTX 2.3 · ReActor · RIFE · ComfyUI API
- **证据**：`workflows/video-modules/` · `workflows/benchmarks/2026-09-04-video-api.md`

## 项目四 · ComfyUI Agent 状态机（Week 5 完成后回填）

**一句话**：自然语言 → 参数解析 → schema 校验 → 选工作流 → 出图。
（Day 29–35 执行后替换本节；v1 明确不做自动调参/质量评估/自动重试，v2 规划写进 README）

---

## 简历技能栏（草稿）

ComfyUI（复杂工作流编排 · API 化 · WebSocket 进度）· LoRA 训练全流程（数据构建/打标/训练/评估）· Python · 性能与成本测量 · Git · 云端 GPU（AutoDL）

---

## 🚫 红线（不注水，写错就是面试雷）

| 不说 | 改说 |
|---|---|
| "已用 Docker 部署" | "Docker 方案与步骤已交付，容器未在本机跑通（镜像拉取受限）" |
| "用过 RunningHub" | "按官网单价折算进成本对比，未实测" |
| "熟悉 SD/SDXL" | "以 Krea 2 新架构为主，SDXL 迁移中"（补测后改口） |
| "对比过 Wan" | "视频生态对比已做，Wan 基线未装（16GB 显存取舍）" |
| "做过 1 年" | "6 周全栈闭环 + 全部数字有 benchmark 支撑" |

---

## ⏱ 30 秒电梯版（背下来）

> "我用 6 周从 0 到 1 做了一条 AIGC 生产栈：先训练了一个自己的数字分身 LoRA——云端 48 分钟、成本 1 块 7，InsightFace 验证相似度做到 0.73；然后把它封装成 10+ 节点的 ComfyUI 写真工作流，API 化之后跑了 50 张批量队列零失败，单张成本算到 6 厘钱；再延伸出视频分段流水线——生成、换脸、插帧各有实测耗时，还写了交付门禁自定义节点做质量把关。所有数字在 GitHub 里都有 benchmark 支撑，欢迎现场验。"
