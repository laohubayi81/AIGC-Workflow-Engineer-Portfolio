# Krea 2 LoRA 训练

第 1 周核心项目：完整跑通 Krea 2 LoRA 训练，产出 1 个可用 LoRA、训练配置、效果评估和调参记录。**已完成（Day 3）**，完整记录见 [Week1/Day3 训练报告](../Week1/Day3/training_report.md)。

## 核心功能

- Musubi Tuner v0.3.4 训练 Krea 2 人物 LoRA（768px、BF16 基座运行时转 FP8、cached latents + text encoder outputs）
- 自然语言 caption 打标（Qwen3-VL，不用 WD14 tag）
- 6 场景 × 4 checkpoint（step300/600/900/1200）横评，给出分场景最佳参数
- 触发词泄漏验证：step600 发现触发词出现在生成图中（过拟合信号），已记录
- 待做：非纯人眼评估（InsightFace / CLIP-I / 盲评）、推理端接入 ControlNet + IP-Adapter

## 效果展示

无 LoRA vs 有 LoRA（同 seed=42、同 prompt、step900 checkpoint、strength 0.85）——仅添加 LoRA，人物从随机中年女性变为目标人物，身份还原成功：

| 无 LoRA | 有 LoRA |
|---|---|
| ![无 LoRA](../Week1/Day3/samples/comparison/comparison_no-lora_step900_s42.png) | ![有 LoRA](../Week1/Day3/samples/comparison/comparison_with-lora_s0.85_step900_s42.png) |

最佳配置：**step1200 checkpoint + strength 0.85**（微笑/艺术感场景 step600 更好）。完整横评见训练报告 §5，更多样张见 `../Week1/Day3/samples/`（front / side / smile / outdoor / fullbody / artistic 六个场景）。

## 技术栈

- 训练：Musubi Tuner v0.3.4（恒源云 RTX 4090D 24GB 云训练；本地 AI-Toolkit 路线未用于最终训练，尝试配置保留在 `config/`）
- 推理：ComfyUI + Krea 2 RAW FP8（工作流：[krea2_raw_lora_test.json](../krea2_raw_lora_test.json)）
- 打标：自然语言 caption

## 安装 / 使用

- 实际训练配置：[Week1/Day3/training/](../Week1/Day3/training/)（dataset.toml + 训练命令，按训练报告参数重建，云端原始文件未保存）
- 本地 AI-Toolkit 尝试配置：`config/krea2_ohwx_person.yml`（未用于最终训练）
- 权重文件不入库（见根目录 `.gitignore`）

## 性能 / 成本

- 首次实测：RTX 4090D 24GB 云服务器，1200 步 / 48 分钟（约 2.4 秒/步），峰值显存约 18–20GB
- 环境基线：[benchmarks/2026-09-01-environment.md](./benchmarks/2026-09-01-environment.md)
