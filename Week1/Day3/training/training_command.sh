#!/usr/bin/env bash
# Krea 2 人物 LoRA 训练命令 — 按 training_report.md §2 参数重建
#
# 环境：恒源云 RTX 4090D 24GB。基座模型放内存盘 /dev/shm/models/（容器根目录磁盘不足，见报告 §4.3 问题5）
# 注意：云端原始命令未保存；脚本入口名、个别未记录参数以 Musubi Tuner v0.3.4 实际为准。

python krea2_train_network.py \
  --dit /dev/shm/models/krea2_raw_bf16.safetensors \
  --config_file /root/datasets/self/dataset.toml \
  --network_module networks.lora_krea2 \
  --network_dim 32 \
  --network_alpha 32 \
  --learning_rate 1e-4 \
  --lr_scheduler constant_with_warmup \
  --lr_warmup_steps 20 \
  --max_train_steps 1200 \
  --optimizer_type AdamW8bit \
  --mixed_precision bf16 \
  --save_precision bf16 \
  --timestep_sampling krea2_shift \
  --fp8_base \
  --fp8_scaled \
  --gradient_checkpointing \
  --sdpa \
  --cache_latents \
  --cache_text_encoder_outputs \
  --save_every_n_steps 300 \
  --output_dir /root/output \
  --output_name myface_krea2_lora
