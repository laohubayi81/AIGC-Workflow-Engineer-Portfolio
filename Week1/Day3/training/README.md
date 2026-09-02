# 训练配置（重建）

云端（恒源云）原始文件未保存，以下文件按 [training_report.md](../training_report.md) 的参数记录重建，用于复现：

- `dataset.toml` — 数据集与缓存路径配置（§3.3 原文）
- `training_command.sh` — 完整训练命令（按 §2 参数表拼装；脚本入口名与个别未记录参数以 Musubi Tuner v0.3.4 实际为准）

云端产物（TensorBoard 日志 events.out.tfevents.*、4 个 checkpoint 权重）未保留，权重不入库见根目录 `.gitignore`。
