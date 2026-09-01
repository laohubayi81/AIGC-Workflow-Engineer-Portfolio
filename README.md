# AIGC Workflow Engineer Portfolio

面向 **AIGC 工作流工程师（ComfyUI）** 的求职作品集。按 6 周计划推进：能演示、能复现、能测量、能解释。仓库里的数字都以本机实测为准，没有数据就不写。

- GitHub：https://github.com/laohubayi81/AIGC-Workflow-Engineer-Portfolio
- 硬件：NVIDIA GeForce RTX 5080 Laptop GPU 16GB + 32GB RAM
- 当前进度：**第 1 周 Day 1**（建仓 + 环境记录 + AI-Toolkit 安装）

## 技能栈

| 方向 | 现状 |
|---|---|
| ComfyUI | 本地已跑通 Krea 2 Turbo（NVFP4）与 LTX 2.3 量化版 |
| Agent / RAG | 有实际项目经验，第 5 周接到 ComfyUI 调度闭环 |
| LoRA 训练 | 未完成。第 1 周只做 Krea 2 单模型 |
| API / 批量 | 未开始（第 2 周） |
| 视频流水线 | 仅文生视频基线，专项未做（第 3 周） |
| Docker / 云端 | 未开始（第 4 周） |

## 模块导航

| 模块 | 说明 | 状态 |
|---|---|---|
| [lora-training](./lora-training/) | Krea 2 LoRA 训练、评估、调参记录 | Day 1 进行中 |
| [workflows](./workflows/) | 图像生产工作流 + 视频生产流水线 | 未开始 |
| [custom-nodes](./custom-nodes/) | 1 个有业务价值的自定义节点 | 未开始 |
| [agent-project](./agent-project/) | Agent 最小状态机闭环 | 未开始 |

环境版本与模型清单见 [lora-training/benchmarks/2026-09-01-environment.md](./lora-training/benchmarks/2026-09-01-environment.md)。
