# Krea 2 LoRA 训练

第 1 周核心项目：完整跑通 Krea 2 LoRA 训练，产出 1 个可用 LoRA、训练配置、效果评估和调参记录。

## 核心功能

- 用 AI-Toolkit 在 16GB 显存上限下训练 Krea 2 LoRA（768px + cached text embeddings）
- 自然语言 caption 打标（Qwen3-VL，不用 WD14 tag）
- 至少 1 种非纯人眼评估（InsightFace / CLIP-I / 盲评）
- 验证「无触发词也生效」泄漏
- 推理端接入 ControlNet + IP-Adapter

## 效果展示

尚未训练，无样张。Day 3 起放入 `samples/`。

## 技术栈

- 训练：ostris/ai-toolkit（本机独立安装，不进本仓库）
- 推理：ComfyUI + Krea 2 Turbo
- 打标：自然语言 caption

## 安装 / 使用

训练配置将放在 `config/`。权重文件不入库（见根目录 `.gitignore`）。

## 性能 / 成本

环境基线：[../workflows/benchmarks/env.md](../workflows/benchmarks/env.md)。训练耗时与显存在首次跑通后按规范补。
