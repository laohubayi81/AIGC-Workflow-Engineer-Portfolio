<div align="center">

# 🎨 AIGC Workflow Engineer Portfolio

**面向 AIGC 工作流工程师（ComfyUI 方向）的 6 周实战作品集**

> 能演示 · 能复现 · 能测量 · 能解释 —— 仓库里所有数字均为实测，没有数据就不写

![Progress](https://img.shields.io/badge/进度-Week%201%20LoRA%20训练-2ea44f?style=flat-square)
![ComfyUI](https://img.shields.io/badge/ComfyUI-Krea%202%20%2F%20LTX%202.3-blue?style=flat-square)
![LoRA](https://img.shields.io/badge/LoRA-Musubi%20Tuner%20v0.3.4-orange?style=flat-square)
![GPU](https://img.shields.io/badge/本地-RTX%205080%20Laptop%2016GB-8a2be2?style=flat-square)
![计划](https://img.shields.io/badge/6周计划-v4%20精简执行版-red?style=flat-square)

</div>

---

## ✨ 亮点成果 · Week 1：Krea 2 人物 LoRA

39 张自拍 → 自然语言打标（Qwen3-VL caption）→ 云端 RTX 4090D 训练 48 分钟（1200 步）→ **身份还原成功**

| 无 LoRA | + LoRA（step900 · strength 0.85 · seed 42） |
|---|---|
| ![无 LoRA](Week1/Day3/samples/comparison/comparison_no-lora_step900_s42.png) | ![有 LoRA](Week1/Day3/samples/comparison/comparison_with-lora_s0.85_step900_s42.png) |

同样的 prompt、同样的 seed，仅添加 LoRA：人物从随机中年女性变为目标人物，性别 / 发型 / 五官全部对齐。

完整流程见 **[Week 1 训练报告](Week1/Day3/training_report.md)**（参数表 · 6 个踩坑与解决 · 4 checkpoint × 6 场景横评 · 分场景最佳参数）。

## 🧭 模块导航

| 模块 | 说明 | 状态 |
|---|---|---|
| 🧪 [lora-training](./lora-training/) | Krea 2 LoRA 训练、评估、调参记录 | ✅ 训练+评估完成 · Day 5 集成中 |
| 🖼️ [workflows](./workflows/) | 图像生产工作流 + 视频生产流水线 | ⬜ Week 2–3 |
| 🧩 [custom-nodes](./custom-nodes/) | 1 个有业务价值的自定义节点 | ⬜ Week 4 |
| 🤖 [agent-project](./agent-project/) | Agent 最小状态机闭环 | ⬜ Week 5 |

## 🛠️ 技术栈

| 类别 | 工具 / 硬件 |
|---|---|
| 工作流 | ComfyUI（Krea 2 Turbo NVFP4 · LTX 2.3 量化版） |
| 训练 | Musubi Tuner v0.3.4 · 恒源云 RTX 4090D 24GB |
| 推理 | Krea 2 RAW FP8 · Qwen3-VL 文本编码器 |
| 本地环境 | RTX 5080 Laptop 16GB + 32GB RAM（[环境基线](./lora-training/benchmarks/2026-09-01-environment.md)） |

## 📈 Week 1 进度

- [x] Day 1 · 建仓 + 环境记录 + AI-Toolkit 安装
- [x] Day 2 · 数据集（39 张自拍）+ 自然语言打标
- [x] Day 3 · 云端训练 1200 步（48 min）+ 6 场景效果评估
- [x] Day 4 · InsightFace 相似度评估（权重扫描 0.41→0.67）+ 触发词泄漏验证（0.57 vs 基线 0.05）
- [ ] 🚧 Day 5 · ControlNet + IP-Adapter 集成工作流
- [ ] Day 6 · 缓冲 / 补漏
- [ ] Day 7 · 周复盘

完整 6 周路线图与逐日执行状态 → **[ROADMAP.md](./ROADMAP.md)**（打开项目先看这里）

## 📮 联系方式

- GitHub：[laohubayi81](https://github.com/laohubayi81)

<!-- TODO: 补充邮箱 / 微信 / 简历链接 / 技术博客链接 -->
