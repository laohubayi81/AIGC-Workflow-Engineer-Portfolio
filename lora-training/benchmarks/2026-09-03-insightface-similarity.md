# InsightFace 身份相似度评估

- 参考图：`lora-training/datasets/self/images/00001.jpg`
- 模型：buffalo_l（SCRFD 人脸检测 + ArcFace 嵌入，多脸取最大）
- 指标：余弦相似度（-1~1）。经验参考：同人不同照片约 0.4–0.7，>0.6 高度相似，<0.2 基本判定不同人

| 图片 | 相似度 | 备注 |
|---|---|---|
| `front_seed42_s0.5_step900.png` | 0.4077 | |
| `front_seed42_s0.7_step900.png` | 0.5449 | |
| `front_seed42_s0.85_step900.png` | 0.5918 | |
| `front_seed42_s1.0_step900.png` | 0.6261 | |
| `front_seed42_s1.2_step900.png` | 0.6661 | |
| `comparison_no-lora_step900_s42.png` | 0.0494 | |
| `comparison_with-lora_s0.85_step900_s42.png` | 0.6151 | |
| `leak_lora-on_no-trigger_seed42_step900.png` | 0.5666 | |
| `leak_lora-off_no-trigger_seed42_step900.png` | -0.0096 | |

**统计**：均值 0.4509 · 最高 0.6661 · 最低 -0.0096（n=9）
