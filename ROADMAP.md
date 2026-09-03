# 📍 项目路线图（6 周计划 v4 · 执行跟踪）

> **用法**：每完成一项就把 `[ ]` 改成 `[x]`，并更新下方「当前位置」。打开项目先看这个文件，就知道做到哪了、下一步干什么。

---

## 🎯 当前位置（最后更新：2026-09-03 夜）

- **位置**：**Week 1 完成**（Day 1–5 交付 + Day 6 跳过 rank=16 + Day 7 复盘已提交）→ 下一步 **Week 2 · Day 8** 图像生产工作流
- **Day 5 可行性探测（09-03）+ 复核修正（09-03，用户纠错 → 检索证实）**：
  - ✅ **ControlNet（复核修正，恢复集成）**：Krea 2 的 CN 以 **ControlNet-LoRA** 形态实现——文件放 `models/loras/`、经自定义节点加载（原探测只查 `models/controlnet/` 与传统 CN 形态，搜索框架错误导致漏判）：
    - **Depth**：HF `Patil/Krea-2-depth-controlnet`（862MB rank64 + expanded input projection；Raw / Turbo 通吃；深度一致性 Pearson 0.98 无 prompt / 0.99 有 prompt）
    - **OpenPose**：`krea2_turbo_openpose_controlnet.safetensors`（block-LoRA + reference latent，见 ComfyUI-QwenImageLoraLoader 集成说明；权重下载源待定位）
    - 社区补充：HF `tori29umai/krea2-controlnet`（anythng 剪影控制；lineart 规划中）
    - 节点：`facok/comfyui-krea2-controlnet`（174★ / 无 license，使用前过一眼代码；3 节点：Control LoRA Loader / Control Image Encode / Control Apply）
  - ❌ **IP-Adapter**：维持原结论（IPAdapter Plus 只支持 SD1.5/SDXL/Flux 系，无 Krea 2 版本）
  - **本地安装现状（09-03 11:20 后已装齐，午后复核确认）**：底模 ✅；`depth-control-lora.safetensors` ✅（861,995,928 字节）；`myface_krea2_lora.safetensors` ✅；facok 节点 ✅；krea2edit ✅；controlnet_aux ✅；Depth Anything V2-Small 权重 ✅（`custom_nodes/comfyui_controlnet_aux/ckpts/.../depth_anything_v2_vits.pth`）；参考图 `IMG_20260901_185310_edit_85976.jpg` ✅ 在 `ComfyUI-Shared/input/`。`models/controlnet/` 为空属正常——CN-LoRA 不进该目录
  - **Day 5 双路线**：A = krea2edit Identity Edit + myface LoRA（构图/编辑迁移）；B = **Depth CN-LoRA + myface LoRA**（结构控制）；A+B+myface 三重叠加为 stretch（未跑）
- **Day 5 执行清单（修订）**：
  0. 准备：`git clone facok/comfyui-krea2-controlnet` → `D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\`（与 comfyui-krea2edit 同级，Desktop 双层嵌套路径）；`depth-control-lora.safetensors`（862MB）→ `D:\Comfy-Desktop\ComfyUI-Shared\models\loras\`；Manager 装 comfyui_controlnet_aux（Depth Anything 预处理）；推理全程挂 **Krea 2 RAW FP8**（与 Day 3/4 同链），不跑 Turbo / NVFP4
  1. 路线 A：搭 `Krea2EditModelPatch` + `Krea2EditGroundedEncode` + myface LoRA，出 ref_boost 0.5 / 1.0 / 1.5 对比图
  2. 路线 B：Depth CN-LoRA + myface LoRA，出 lora-scale 0.6 / 1.0 对比 + 输入|深度|输出 三联条带图
  3. stretch（可选）：A + B + myface 三重叠加兼容性测试
  4. 产出：集成工作流 JSON ×2 + 对比图 + 组件边界表写入 `lora-training/`（人像控制取舍：OpenPose 保姿态、Depth 保三维结构；B 路线先跑 Depth 因文档与评估数据最全，OpenPose 权重源核实后补测）
- **进度（09-03 傍晚关账）**：正式对比 = 控制图 `00027.jpg` + RAW FP8 + seed 42。报告 [Week1/Day5/README.md](Week1/Day5/README.md)，InsightFace [benchmarks/2026-09-03-day5-insightface.md](lora-training/benchmarks/2026-09-03-day5-insightface.md)。
  - ✅ 路线 B v3：公园近景、看镜头。strength 1.0 更贴自拍取景（身份 0.66）；0.6 更听 prompt（0.55）。深度近白远黑。v2 全身侧拍对打出「草地后脑勺」，作压力测试反例保留。
  - ✅ 路线 A v2：identity_edit LoRA @1.0 + myface @0.85，prompt 为编辑指令。ref_boost 1.0/4.0/8.0 都完成白底黑 T；身份 vs 00001 为 0.68→0.69→0.73。第一轮未挂专用 LoRA 的蜡像图作废。
  - ✅ 组件边界表已写入 Day 5 README。stretch（A+B+myface 三重）未跑。OpenPose 未测。推理全程 RAW FP8，未跑 Turbo / NVFP4。
  - **下一步**：已进入 Week 2 Day 8（数字人写真生产工作流，待确认场景后开工）

---

## Week 1 · Krea 2 LoRA 训练（Day 1–7）✅ 完成

- [x] Day 1 · 建仓 + 环境记录 + AI-Toolkit 安装
- [x] Day 2 · 数据集（39 张自拍）+ 自然语言打标（Qwen3-VL caption，触发词 ohwx）
- [x] Day 3 · 训练 1200 步（Musubi Tuner v0.3.4 · 恒源云 4090D · 48 min）+ 6 场景评估 + [训练报告](Week1/Day3/training_report.md)
- [x] Day 4 · 权重扫描（0.5–1.2）+ 触发词泄漏验证 + InsightFace 评估——0.41→0.67 单调升；泄漏确认（无触发词 0.57 vs 基线 0.05）
- [x] Day 5 · 推理端集成：路线 A krea2edit Identity Edit（ref_boost 1/4/8）+ 路线 B Depth CN-LoRA（strength 0.6/1.0）+ 组件边界表；IP-Adapter 无方案已留证；stretch 未跑
- [x] Day 6 · 缓冲：**跳过** rank=16 对照（完成标准不要求；现有 myface 是 rank 32。再训要重新租卡，本周不做）
- [x] Day 7 · 周复盘：AutoDL 成本 1.74 元入库；偏差表已更新；Day 5 JSON / 样张 / 报告已推 GitHub（`24d579f`）

**Week 1 完成标准**：

- [x] ① LoRA 训练成功（768px + cached latents/text encoder + 1000–1500 步）
- [x] ② 非纯人眼评估：InsightFace 余弦相似度（9 张，[数据](lora-training/benchmarks/2026-09-03-insightface-similarity.md)）
- [x] ③ 触发词泄漏验证记录：2×2 矩阵量化确认（0.57 vs 基线 0.05）
- [x] ④ 推理端调参记录：CFG 3/4/7 + 权重 0.5–1.2 均已扫
- [x] ⑤ ControlNet（CN-LoRA 形态）/ Identity Edit / LoRA 集成工作流（IP-Adapter 无方案已留证）
- [x] ⑥ lora-training 模块完整，含 benchmark 数据（含 [训练成本 1.74 元](lora-training/benchmarks/2026-09-03-training-cost.md)）

**Day 7 复盘清单**：云端训练成本已按 AutoDL 2.18 元/h × 48 min = 1.74 元写入 `benchmarks/`；偏差表已更新；样张 / 报告 / 工作流 JSON 已提交（`24d579f`）。

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
| 09-02 | Day 3 训练改用 Musubi Tuner v0.3.4 + 云端 RTX 4090D（计划为本地 AI-Toolkit 16GB） | 本地 16GB 走 AI-Toolkit 未跑通，按计划"环境装不上→云端租卡"兜底；产物等价：768px + cached + 1200 步 |
| 09-03 | 训练成本按 AutoDL 2.18 元/h 入账（48 min → 1.74 元），Day 3 报告写的是恒源云 seetacloud | 无订单截图；单价为用户口述。平台名称两处不一致，成本不以估算冒充实付 |
| 09-03 | Day 6 跳过 rank=16 对照 | 完成标准不要求。现网 LoRA 为 rank 32；再训 16 需重新租 4090D，本周把时间留给 Week 2 生产工作流 |
| 09-03 | 训练配置按报告重建入库（云端原始 dataset.toml / 训练命令未保存） | 见 [Week1/Day3/training/README.md](Week1/Day3/training/README.md) |
| 09-03 | Day 5 集成方案修订：ControlNet / IP-Adapter 对 Krea 2 均无可用方案（探测：本地无 CN 权重；Qwen DiffSynth CN 面向 Qwen-Image 架构；IPAdapter Plus 只支持 SD1.5/SDXL/Flux） | 改用 Krea 2 原生 krea2edit Identity Edit 做参考迁移（节点与 LoRA 已就绪）；组件边界表随 Day 5 产出 |
| 09-03 | Day 5 探测结论复核修正：Krea 2 存在 **ControlNet-LoRA** 形态的 CN（Depth / OpenPose），上条"无 Krea 2 CN 方案"结论有误 | 原探测只查了本地 `models/controlnet/` 与传统 CN 形态，而 CN-LoRA 实际放 `models/loras/`、经自定义节点（facok/comfyui-krea2-controlnet）加载，搜索框架不完整导致漏判。恢复 v4 计划的 CN 集成项，与 krea2edit 并行 A/B 测试（证据：HF `Patil/Krea-2-depth-controlnet`、comfyui-wiki 2026-07-03 发布新闻、RunComfy 节点页） |
| 09-03 | 路线 A 第一轮蜡像：工作流用 myface 顶替 `krea2_identity_edit_v1_2`，prompt 还是文生图 caption | 官方链路是底模 → identity_edit LoRA → ModelPatch，prompt 必须是编辑指令。v2 按此重跑，ref_boost 改为 1.0/4.0/8.0（官方推荐 4） |
| 09-03 | 路线 B 用近景自拍 + 证件照 prompt 时 0.6 vs 1.0 肉眼几乎没差 | 结构和 prompt 同向。改成公园近景后差别清楚；再改成全身侧拍对打，strength 1.0 出无身子后脑勺。Depth 只锁剪影，景别必须和 prompt 对齐 |

## 🗒 面试反哺记录

（面试被问到的问题、暴露的短板记在这里，用于反向调整作品集优先级）

- 暂无
