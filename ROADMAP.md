# 📍 项目路线图（6 周计划 v4 · 执行跟踪）

> **用法**：每完成一项就把 `[ ]` 改成 `[x]`，并更新下方「当前位置」。打开项目先看这个文件，就知道做到哪了、下一步干什么。

---

## 🎯 当前位置（最后更新：2026-09-03）

- **位置**：**Week 1 · Day 5 待开工**（Day 4 评估已收尾推送）
- **Day 5 可行性探测已完成（09-03），计划修订**：
  - ❌ **ControlNet**：本地 `models/controlnet/` 为空；ComfyUI 唯一的 Qwen 系 ControlNet（DiffSynth）面向 Qwen-Image 底模，与 Krea 2（12.9B 另一套 DiT 维度）大概率不兼容，无 Krea 2 专用 CN 迹象
  - ❌ **IP-Adapter**：IPAdapter Plus 只支持 SD1.5/SDXL/Flux 系，无 Krea 2 版本，节点未装
  - ✅ **替代主路线**：Krea 2 + myface LoRA + **krea2edit Identity Edit**（`comfyui-krea2edit` 节点 + `krea2_identity_edit_v1_2.safetensors` 已就绪）——参考图定构图、LoRA 保身份，零下载
- **Day 5 执行清单**：
  1. 主路线：搭 `Krea2EditModelPatch` + `Krea2EditGroundedEncode` + myface LoRA 工作流，出 ref_boost 0.5 / 1.0 / 1.5 对比图
  2. 支线（可选，≤1h）：下载一个 Qwen DiffSynth CN 实测挂 Krea 2，报错留证
  3. 产出：集成工作流 JSON + 对比图 + 组件边界表写入 `lora-training/`（若将来有 Krea 2 官方 CN，人像选 OpenPose > Depth，Canny 不适合人像）

---

## Week 1 · Krea 2 LoRA 训练（Day 1–7）🚧 进行中

- [x] Day 1 · 建仓 + 环境记录 + AI-Toolkit 安装
- [x] Day 2 · 数据集（39 张自拍）+ 自然语言打标（Qwen3-VL caption，触发词 ohwx）
- [x] Day 3 · 训练 1200 步（Musubi Tuner v0.3.4 · 恒源云 4090D · 48 min）+ 6 场景评估 + [训练报告](Week1/Day3/training_report.md)
- [x] Day 4 · 权重扫描（0.5–1.2）+ 触发词泄漏验证 + InsightFace 评估——0.41→0.67 单调升；泄漏确认（无触发词 0.57 vs 基线 0.05）
- [ ] Day 5 · 推理端集成（已按探测修订）：krea2edit Identity Edit + myface LoRA 工作流 JSON + 组件边界表；ControlNet/IP-Adapter 确认无 Krea 2 方案（可选实测留证）
- [ ] Day 6 · 缓冲（可选：训 rank=16 对照，"应该完成"项）
- [ ] Day 7 · 周复盘（见下方清单）

**Week 1 完成标准**：

- [x] ① LoRA 训练成功（768px + cached latents/text encoder + 1000–1500 步）
- [x] ② 非纯人眼评估：InsightFace 余弦相似度（9 张，[数据](lora-training/benchmarks/2026-09-03-insightface-similarity.md)）
- [x] ③ 触发词泄漏验证记录：2×2 矩阵量化确认（0.57 vs 基线 0.05）
- [x] ④ 推理端调参记录：CFG 3/4/7 + 权重 0.5–1.2 均已扫
- [ ] ⑤ ControlNet / IP-Adapter / LoRA 集成工作流
- [ ] ⑥ lora-training 模块完整，含 benchmark 数据

**Day 7 复盘清单**：把云端训练成本（恒源云 48 min 费用）补进 `benchmarks/`；更新偏差记录表；确认样张 / 报告 / 工作流 JSON 全部提交。

---

## Week 2 · 图像生产工作流 + API 封装 + 批量队列（Day 8–14）

**核心目标**：10+ 节点图像生产工作流 + Python API 封装模块 + 单实例批量队列（100+ 任务）+ 一套真实性能成本数据。

- [ ] Day 8 · 从零设计图像生产工作流（选业务场景：电商产品图 / 数字人写真 / 营销素材；覆盖 预处理 → ControlNet → LoRA → 生成 → 后处理 → 输出）→ JSON + 使用说明
- [ ] Day 9 · 性能优化 + 成本测量（耗时 5 次均值 P50/P90、显存峰值、成功率 20 次、0.4 元/h 单件成本）→ `workflows/benchmarks/`
- [ ] Day 10 · ComfyUI API 深入（`/prompt`、`/history`、`/view`、`/object_info`、`/ws`；两个坑：前端 workflow ≠ API Format、进度必须走 WebSocket）→ API Format 工作流 + 最小调用脚本
- [ ] Day 11 · Python API 封装模块（`generate()` / `batch_generate()`、参数校验、指数退避重试、WebSocket 进度回调）
- [ ] Day 12 · 单实例批量队列（CSV 100+ 任务、串行、状态管理、失败自动重试、日志）→ 实跑 50–100 张出统计报告
- [ ] Day 13 · 缓冲 / 补漏
- [ ] Day 14 · 周复盘

**完成标准**：① 10+ 节点工作流 ② 性能成本表 ③ API 封装模块 ④ 批量队列脚本 + 统计 ⑤ GitHub workflows 与 agent-project（API 部分）完整

---

## Week 3 · 视频生产流水线（Day 15–21）→ **Day 21 开始投递**

**核心目标**：15+ 节点视频生产流水线，集成换脸 / 超分 / 帧插值 / 时序一致性 4 个专项（口型可选）。

- [ ] Day 15 · 视频模型生态对比表（LTX / Wan / Hunyuan / CogVideoX / MiniMax H3）+ LTX 量化版与 Wan 1.3B 基线实测
- [ ] Day 16 · 换脸工作流（ReActor / FaceSwap Lab + GFPGAN 修复）+ 问题排查笔记 + 性能数据
- [ ] Day 17 · 超分（RealESRGAN / 4x-UltraSharp）+ 帧插值（RIFE 24→48/60fps）→ 整合后处理工作流
- [ ] Day 18 · 时序一致性（IC-LoRA / 首尾帧约束 / IP-Adapter）→ 15+ 节点整合流水线 + 完整文档
- [ ] Day 19 · 视频 API 化 + 批量生成（分镜 CSV，超时拉长，5–10 条短视频验证）
- [ ] Day 20 · 口型对齐（可选，卡住不超半天）/ 缓冲
- [ ] Day 21 · 周复盘 + **开始投递**（BOSS 直聘主力，首日 10–15 个，关键词：ComfyUI / AIGC 工程师 / AI 视频工程师）

**完成标准**：① 4 个视频专项各有样例和笔记 ② 15+ 节点流水线 ③ 生态对比表 ④ 视频 API + 批量 ⑤ 投递启动 ⑥ GitHub 完整

---

## Week 4 · 工程化：Docker + 云端 + 自定义节点（Day 22–28）

**核心目标**：Docker 部署方案 + 多实例分发器 + 云端成本对比 + 1 个有业务价值的自定义节点 + 监控统计。

- [ ] Day 22 · Docker 部署 ComfyUI（nvidia/cuda 基础镜像 + GPU 直通 + 模型 volume 挂载）→ Dockerfile + compose + 文档
- [ ] Day 23 · 多实例原理 + 任务分发器脚本（云端双实例验证，或本地单实例逻辑验证）
- [ ] Day 24 · 云端 GPU 实践 + 成本对比报告（本地 5080 / 云 4090 / RunningHub 三方对比 + 选型建议）
- [ ] Day 25 · 自定义节点开发（三选一：参数校验注入 / 生成质量检测 / 任务状态记录；含 NODE_CLASS_MAPPINGS 注册）
- [ ] Day 26 · 节点完善 + `custom-nodes/` 模块 README（安装 / 参数 / 依赖 / 效果截图）
- [ ] Day 27 · 监控统计模块（成功率、P50/P90、失败原因分布）集成进批量调度脚本
- [ ] Day 28 · 周复盘

**完成标准**：① Docker 部署 ② 分发器 + 吞吐对比 ③ 成本对比报告 ④ 业务价值节点 ⑤ 监控模块 ⑥ 持续投递面试

---

## Week 5 · Agent 最小闭环（Day 29–35）

**核心目标**：状态机 v1——自然语言 → LLM 解析参数 → schema 校验 → 选工作流 → 调 ComfyUI API → 返回结果。**不做**自动调参 / 复杂质量评估 / 自动重试（全部归入 v2 规划，写进 README 但不实现）。

- [ ] Day 29 · 状态机设计文档 + 流程图
- [ ] Day 30 · 基础框架 + 最小闭环 demo（"生成一张猫的图片"全链路跑通）
- [ ] Day 31 · 工作流注册表（注册 2–3 个前几周的工作流 + JSON Schema 参数校验填充）
- [ ] Day 32 · 批量任务支持 + 简单结果检查（文件存在 / 尺寸 / 有效性）
- [ ] Day 33 · 实时进度展示（WebSocket 透传节点级进度）+ 成本统计报告 + 基础错误处理
- [ ] Day 34 · 完整 README + demo GIF + 技术博客（掘金 / 知乎 / CSDN）
- [ ] Day 35 · 周复盘 + Agent 项目加入简历，持续投递

**完成标准**：① 最小闭环稳定可用 ② 注册表 + schema ③ 批量 + 结果检查 ④ 进度 + 成本统计 ⑤ README + demo + 博客 ⑥ v1 局限与 v2 规划明确

---

## Week 6 · 求职冲刺 + 缓冲（Day 36–42）

- [ ] Day 36 · 作品集最终整理（4 模块 README 统一模板：简介 / 核心功能 / 效果展示 / 技术栈 / 安装使用 / 性能成本；检查 commit 历史）
- [ ] Day 37 · 简历定稿（**不注水**：所有数字有 GitHub 支撑；3 个项目 STAR 法则：Agent 系统 / 视频流水线 / Krea 2 LoRA）
- [ ] Day 38 · 面试题准备（ComfyUI 基础 / LoRA 与模型 / 视频工作流 / 工程化 / Agent 五类；具体数字带"我在 XX 配置下实测"表述）
- [ ] Day 39 · 模拟面试（3 个项目各准备 1 分钟电梯版 + 5 分钟详细版，录音回听）
- [ ] Day 40 · 持续投递（累计 30–50 个岗位）+ 面试复盘机制
- [ ] Day 41–42 · 纯缓冲：面试 / 补漏 / 可选迭代（Agent v2、SDXL LoRA 对照）

---

## 📌 与计划的偏差记录

| 日期 | 偏差 | 原因 / 说明 |
|---|---|---|
| 09-02 | Day 3 训练改用 Musubi Tuner v0.3.4 + 恒源云 RTX 4090D（计划为本地 AI-Toolkit 16GB） | 本地 16GB 走 AI-Toolkit 未跑通，按计划"环境装不上→云端租卡"兜底；产物等价：768px + cached + 1200 步 |
| 09-03 | 训练配置按报告重建入库（云端原始 dataset.toml / 训练命令未保存） | 见 [Week1/Day3/training/README.md](Week1/Day3/training/README.md) |
| 09-03 | Day 5 集成方案修订：ControlNet / IP-Adapter 对 Krea 2 均无可用方案（探测：本地无 CN 权重；Qwen DiffSynth CN 面向 Qwen-Image 架构；IPAdapter Plus 只支持 SD1.5/SDXL/Flux） | 改用 Krea 2 原生 krea2edit Identity Edit 做参考迁移（节点与 LoRA 已就绪）；组件边界表随 Day 5 产出 |

## 🗒 面试反哺记录

（面试被问到的问题、暴露的短板记在这里，用于反向调整作品集优先级）

- 暂无
