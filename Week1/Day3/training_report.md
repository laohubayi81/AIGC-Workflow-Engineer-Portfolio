# Krea 2 人物 LoRA 训练报告

> **项目**：AIGC 工作流工程师学习计划 - Week 1 Day 3
> **日期**：2026-09-02
> **目标**：训练 Krea 2 人物 LoRA（自拍数据集），掌握 LoRA 训练全流程与调参方法

---

## 1. 项目概述

使用 Krea 2 RAW 模型 + Musubi Tuner 训练工具，基于 39 张自拍照片训练人物 LoRA。训练在恒源云 RTX 4090D 24GB 云服务器上完成，耗时 48 分钟。最终 LoRA 在正面、侧面、微笑、户外、艺术感等场景均能稳定还原人物身份特征。

### 1.1 技术栈

| 组件 | 选型 |
|------|------|
| 基座模型 | Krea 2 RAW（BF16 训练 / FP8 推理） |
| 训练工具 | Musubi Tuner v0.3.4（kohya-ss 出品） |
| 推理框架 | ComfyUI（原生 Krea 2 支持） |
| 云平台 | 恒源云 seetacloud（北京机房） |
| 硬件 | RTX 4090D 24GB / 18核 AMD EPYC / 60GB 内存 |

---

## 2. 训练参数

### 2.1 核心参数

| 参数 | 值 | 说明 |
|------|-----|------|
| network_module | networks.lora_krea2 | Krea 2 专用 LoRA 模块 |
| network_dim | 32 | LoRA 秩（Krea 2 官方推荐 dim=alpha=32） |
| network_alpha | 32 | LoRA alpha |
| learning_rate | 1e-4 | 学习率 |
| lr_scheduler | constant_with_warmup | 带 warmup 的常数学习率 |
| lr_warmup_steps | 20 | warmup 步数 |
| max_train_steps | 1200 | 总训练步数 |
| optimizer_type | AdamW8bit | 8位 AdamW 优化器（省显存） |
| batch_size | 1 | 批大小 |
| resolution | 768x768 | 训练分辨率 |
| mixed_precision | bf16 | 混合精度 |
| save_precision | bf16 | 保存精度 |

### 2.2 Krea 2 专用参数

| 参数 | 值 | 说明 |
|------|-----|------|
| timestep_sampling | krea2_shift | Krea 2 专用分辨率感知时间步采样 |
| fp8_base | 开启 | 基座模型运行时 FP8 量化（省显存） |
| fp8_scaled | 开启 | FP8 缩放（必须与 fp8_base 同时开启） |
| gradient_checkpointing | 开启 | 梯度检查点（省显存） |
| sdpa | 开启 | Scaled Dot-Product Attention |
| cache_latents | 开启 | 预缓存 VAE latent |
| cache_text_encoder_outputs | 开启 | 预缓存文本编码器输出 |

### 2.3 保存与采样

| 参数 | 值 |
|------|-----|
| save_every_n_steps | 300（共 4 个 checkpoint：step300/600/900/1200） |
| output_name | myface_krea2_lora |
| LoRA 文件大小 | 224MB（每个 checkpoint） |

---

## 3. 数据集准备

### 3.1 数据集概况

| 项目 | 数据 |
|------|------|
| 图片数量 | 39 张 |
| 分辨率 | 768x768（统一裁剪） |
| 内容 | 自拍人物照片，多角度/多表情/多场景 |
| Caption 方式 | 自然语言描述（Krea 2 使用 Qwen3-VL 文本编码器，支持自然语言，无需 WD14 tag） |
| 触发词 | ohwx（用户自定义） |

### 3.2 数据集结构

```
/datasets/self/
├── images/           # 图片 + caption（同一目录，Musubi Tuner 要求）
│   ├── 00001.jpg
│   ├── 00001.txt
│   ├── 00002.jpg
│   ├── 00002.txt
│   └── ...
├── cache/            # latent + 文本编码器输出缓存
└── dataset.toml      # 数据集配置文件
```

### 3.3 dataset.toml 配置

```toml
[general]
resolution = [768, 768]
caption_extension = ".txt"
batch_size = 1
enable_bucket = false

[[datasets]]
image_directory = "/root/datasets/self/images"
cache_directory = "/root/datasets/self/cache"
num_repeats = 1
```

---

## 4. 训练过程记录

### 4.1 训练时间线

| 时间 | 事件 |
|------|------|
| 19:39 | 训练开始，加载模型与数据集 |
| 19:51 | step300 checkpoint 保存（12分钟） |
| 20:03 | step600 checkpoint 保存（12分钟） |
| 20:15 | step900 checkpoint 保存（12分钟） |
| 20:27 | step1200 训练完成，最终模型保存（12分钟） |
| **总计** | **48 分钟**（每步约 2.4 秒） |

### 4.2 Loss 曲线

| 指标 | 初始（step 1） | 最终（step 1200） | 最低 |
|------|---------------|-------------------|------|
| loss/current | 0.0696 | **0.0450** | 0.0191 |
| loss/average | 0.0696 | **0.0536** | 0.0398 |
| learning_rate | 5e-6（warmup 起始） | 1e-4（目标值） | - |

**分析**：
- Loss 从 0.0696 降至 0.0450，下降约 35%，模型有效学习到人物特征
- 最低 loss 0.0191 出现在某些容易拟合的样本上
- 学习率从 5e-6 经 20 步 warmup 升至 1e-4，之后保持常数
- 31 个 epoch（1200步 ÷ 39张/epoch），人物 LoRA 正常训练范围

### 4.3 遇到的问题与解决方案

训练过程中遇到 6 个主要问题，全部解决：

#### 问题 1：模型仓库名错误（401 Unauthorized）

- **现象**：`huggingface-cli download Comfy-Org/krea2_raw` 报 401
- **原因**：仓库名错误，正确仓库名是 `Comfy-Org/Krea-2`（大写 K，无 raw 后缀）
- **解决**：使用正确仓库名 `Comfy-Org/Krea-2`

#### 问题 2：Gated 仓库无法访问（403 Forbidden）

- **现象**：`krea/Krea-2-Raw` 仓库报 403，需要 HuggingFace 账号授权
- **原因**：Krea 官方仓库是 gated（受限访问）
- **解决**：使用 ComfyUI 官方维护的非 gated 仓库 `Comfy-Org/Krea-2`（240万+ 下载量）

#### 问题 3：FP8 量化模型格式不兼容

- **现象**：用 `krea2_raw_fp8_scaled.safetensors` 训练时报错 `Unexpected key(s): weight_scale, comfy_quant`
- **原因**：ComfyUI 格式的 FP8 量化文件包含 `weight_scale` 和 `comfy_quant` 等量化缩放因子键，Musubi Tuner 的模型结构不包含这些键
- **解决**：必须使用 **BF16 版本**（`krea2_raw_bf16.safetensors`，26GB）训练，配合 `--fp8_base --fp8_scaled` 在运行时转 FP8 省显存
- **经验**：FP8 量化文件是给 ComfyUI 推理用的，训练工具必须用标准精度（BF16/FP16/FP32）权重

#### 问题 4：24GB 显存 OOM

- **现象**：加载 BF16 DiT（26GB）时 `CUDA out of memory`，24GB 显存全部占满
- **原因**：BF16 模型 26GB > 24GB 显存
- **解决**：
  1. 开启 `--fp8_base --fp8_scaled`：运行时将基座模型转 FP8，显存占用减半（约 13GB）
  2. 开启 `--gradient_checkpointing`：用计算换显存
  3. 训练时不生成样例图（去掉 `--sample_every_n_steps`），避免文本编码器常驻显存
- **结果**：峰值显存约 18-20GB，稳定训练

#### 问题 5：磁盘空间不足

- **现象**：下载 BF16 模型（26GB）时报 `Cannot write`，根目录 30GB 已用满
- **原因**：容器根目录只有 30GB，已存 FP8 模型（13GB）+ 文本编码器（8GB）+ 系统 + 数据集
- **解决**：
  1. 删除不需要的 FP8 版本模型和文本编码器（腾出约 18GB）
  2. 将 BF16 模型下载到 `/dev/shm`（内存盘，60GB 可用）
  3. 训练时模型路径指向 `/dev/shm/models/`
- **经验**：云服务器容器根目录通常较小，大模型文件可放内存盘或数据盘

#### 问题 6：ComfyUI 文本编码器类型选项不匹配

- **现象**：CLIPLoader 节点的 type 下拉框没有 `qwen3_vl` 选项
- **原因**：用户的 ComfyUI 版本将 Krea 2 文本编码器类型命名为 `krea2`，而非 `qwen3_vl`
- **解决**：CLIPLoader 的 type 选 `krea2`（下拉框最底部）

---

## 5. 效果评估

### 5.1 无 LoRA vs 有 LoRA 对比

使用相同 seed=42、相同 prompt（正面证件照）、相同参数，对比无 LoRA 和有 LoRA（step900, strength=0.85）的生成结果：

| | 无 LoRA | 有 LoRA |
|---|--------|---------|
| 性别 | 女性 | 男性 |
| 年龄 | 中年 | 年轻 |
| 发型 | 短黑发（偏分） | 黑色中长发（自然下垂） |
| 肤色 | 较深 | 较白 |
| 五官 | 成熟女性特征 | 目标人物特征 |

**结论**：同样的 prompt（含触发词 ohwx），仅添加 LoRA，人物从随机中年女性变为目标人物特征——性别、年龄、发型、五官全部改变，说明 LoRA 成功学习到身份特征，身份还原度高。

### 5.2 Checkpoint 对比（step300/600/900/1200）

使用相同 seed=42、相同 prompt、相同 strength=0.85，在 6 个场景下对比 4 个 checkpoint：

| 场景 | step300 | step600 | step900 | step1200 | 最佳 |
|------|---------|---------|---------|----------|------|
| 正面 | 不错（细节稍少） | ⚠️ 意外生成眼镜 | ✅ 最佳（自然） | ✅ 很好（细节丰富） | step900/1200 |
| 侧面 | ⚠️ 一般（身份特征弱） | ⚠️ 出眼镜 | ✅ 最佳 | ✅ 很好 | step900/1200 |
| 微笑 | ✅ 不错 | ✅ **最佳**（戴眼镜真实） | ✅ 不错 | ✅ 不错 | step600 |
| 户外 | ✅ 不错（戴眼镜） | ⚠️ 触发词泄露（T恤出现"phwx"） | ✅ 不错（无眼镜） | ✅ **最佳**（戴眼镜+无过拟合） | step1200 |
| 全身 | 脸部还行 | 脸部还行 | 脸部还行 | 脸部还行 | step900/1200 |
| 艺术感 | ⚠️ 一般（偏中性） | ✅ **最佳**（项链+伦勃朗光） | ✅ 不错 | ✅ 不错 | step600 |

**关键发现**：
1. **step300 已有效**：39 张图 300 步就学到了身份特征，学习速度快
2. **step600 眼镜强触发**：正面/侧面/微笑/户外均出现眼镜，说明训练集中戴眼镜照片占比较高，step600 是眼镜特征强触发点
3. **step600 触发词泄露**：户外场景 T 恤上出现"phwx"字样（触发词 ohwx 的变形），是轻微过拟合迹象
4. **step900/1200 稳定**：无触发词泄露，身份特征稳定，step1200 更可能出眼镜（更真实）
5. **step1200 提升有限**：与 step900 非常接近，说明 900 步后提升不大

### 5.3 6 场景效果评估

| 场景 | 评分 | 说明 |
|------|------|------|
| 正面证件照 | ⭐⭐⭐⭐⭐ | 非常好，细节丰富自然，身份特征明确 |
| 侧面 | ⭐⭐⭐⭐ | 不错，五官轮廓清晰，无明显变形 |
| 微笑 | ⭐⭐⭐⭐⭐ | 笑容自然，牙齿整齐，戴眼镜更真实 |
| 户外 | ⭐⭐⭐⭐ | 身份特征稳定，背景自然，光线合理 |
| 全身 | ⭐⭐⭐ | 脸部特征在，身体比例受数据集限制（训练集无全身照） |
| 艺术感 | ⭐⭐⭐⭐ | 伦勃朗光到位，暗背景戏剧性光影，艺术肖像感强 |

**整体评估**：作为脸部特写人物 LoRA，在头像/半身/证件照场景效果优秀；全身场景受数据集限制（训练集均为脸部特写），身体比例不够准确，属正常现象。

---

### 5.4 LoRA 权重扫描（Day 4 补测）

固定 front 场景 / seed 42 / step900 checkpoint / steps 28 / CFG 5.5，扫描 strength：

| strength | InsightFace 相似度 | 目视 |
|---|---|---|
| 0.5 | 0.4077 | 身份偏弱，脸部偏柔 |
| 0.7 | 0.5449 | 身份明确，自然 |
| 0.85 | 0.5918 | 平衡（原默认值） |
| 1.0 | 0.6261 | 身份感强 |
| 1.2 | 0.6661 | 最高，但皮肤纹理开始变硬（过拟合前兆） |

无 LoRA 基线：**0.0494**（基本视为不同人）。样张：`samples/front/front_seed42_s*_step900.png`

**结论**：相似度随 strength 单调上升；0.7–1.0 是身份感与自然度的实用区间，默认 0.85 合理；>1.2 收益递减且质感劣化。

### 5.5 触发词泄漏系统验证（Day 4 补测）

2×2 矩阵（同 seed 42 / step900 / s0.85 / steps 28 / CFG 5.5），相似度 = 与参考自拍的 InsightFace 余弦相似度：

| | prompt 含 ohwx | prompt 不含 ohwx |
|---|---|---|
| **LoRA 开** | 0.6151（目标人物） | **0.5666（仍是目标人物）→ 泄漏确认** |
| **LoRA 关** | 0.0494（随机人物） | -0.0096（随机人物） |

图片：`samples/comparison/comparison_*.png` 与 `samples/comparison/leak_*.png`

**结论**：prompt 不写触发词时相似度仍达 0.5666（接近带触发词的 0.6151），远高于无 LoRA 基线 0.05——**「无触发词也生效」泄漏量化确认**，与社区已知的 Krea 2 LoRA 缺陷一致。成因：训练 caption 全部含触发词，模型把"人物特征"与任意 prompt 绑定而非与触发词绑定。缓解（训练端）：部分 caption 去掉触发词或提高 caption dropout 重训；推理端无法根治。面试可主动提及此验证。

### 5.6 非纯人眼量化评估（Week 1 完成标准②）

- 方法：InsightFace buffalo_l（SCRFD 人脸检测 + ArcFace 嵌入），参考图 = 训练集自拍 00001.jpg，多人脸取最大
- 数据：[lora-training/benchmarks/2026-09-03-insightface-similarity.md](../../lora-training/benchmarks/2026-09-03-insightface-similarity.md)（9 张逐张相似度 + 统计）
- 复现：脚本 `Week1/Day4/insightface_eval.py`，环境与步骤见 `Week1/Day4/README.md`

---

## 6. 最佳参数推荐

### 6.1 通用推荐

| 参数 | 推荐值 | 说明 |
|------|--------|------|
| 最佳 checkpoint | **step1200** | 戴眼镜更真实（用户平时戴眼镜），无过拟合，各场景稳定 |
| LoRA strength | **0.85** | 通用值；想要更强身份感加到 0.9-1.0；想要更自然降到 0.7 |
| 推理 steps | 28 | Krea 2 RAW 推荐 20-30 步 |
| CFG | 5.5 | Krea 2 RAW 推荐 4-7 |
| 采样器 | euler / dpmpp_2m | |
| 调度器 | normal / karras | |
| 分辨率 | 768x768 | 与训练分辨率一致 |

### 6.2 分场景推荐

| 场景 | 推荐 step | 推荐 strength |
|------|----------|--------------|
| 正面/证件照 | step900 或 step1200 | 0.85 |
| 侧面 | step900 或 step1200 | 0.85 |
| 微笑 | step600（戴眼镜更真实） | 0.85 |
| 户外 | step1200 | 0.85 |
| 艺术感 | step600 | 0.85 |
| 想要不戴眼镜 | step900（稳定不出眼镜） | 0.85 |

### 6.3 避免使用

- **step600 用于文字密集场景**：有触发词泄露风险（图片中可能出现"ohwx"变形文字）
- **低于 step300**：身份特征不够稳定

---

## 7. 局限性与改进方向

### 7.1 当前局限性

1. **定位为脸部特写 LoRA**：训练集 39 张均为脸部特写/半身照，无全身照，导致全身场景身体比例不准确
2. **眼镜特征不稳定**：训练集中戴眼镜照片占比约 50%，导致 step300/600/1200 出眼镜、step900 不出眼镜，无法稳定控制是否戴眼镜
3. **衣服/背景泛化有限**：训练集衣服和背景种类有限，生成时衣服变化范围不大
4. **无编辑能力**：当前为标准人物 LoRA（文生图），不支持图生图编辑（in-context edit），编辑能力需单独训练 krea2_edit LoRA

### 7.2 改进方向

| 方向 | 具体措施 | 预期效果 |
|------|---------|---------|
| 补充全身照 | 增加 10-20 张全身照（多角度/多穿搭），重新训练 | 全身场景身体比例准确 |
| 稳定眼镜特征 | 增加戴眼镜照片比例至 70%+，或分别训练"戴眼镜"和"不戴眼镜"两个 LoRA | 可稳定控制是否戴眼镜 |
| 增加数据集多样性 | 增加至 80-100 张，覆盖更多表情/角度/场景/穿搭 | 提升泛化能力和表情多样性 |
| 尝试编辑 LoRA | 使用 krea2_edit 训练方式，支持图生图人物编辑 | 支持换背景/换衣服/换姿势等编辑任务 |
| 更高 dim 实验 | 尝试 network_dim=64/128，对比身份还原度与泛化能力的 trade-off | 找到最佳 dim |
| 多人物 LoRA | 训练多人物 LoRA（如自己+朋友），测试身份分离能力 | 扩展应用场景 |

---

## 8. 资源与文件清单

### 8.1 模型文件

| 文件 | 大小 | 用途 | 路径 |
|------|------|------|------|
| krea2_raw_bf16.safetensors | 26GB | 训练基座模型 | 服务器 /dev/shm/models/ |
| krea2_raw_fp8_scaled.safetensors | 13GB | 推理基座模型 | 本地 ComfyUI/models/diffusion_models/ |
| qwen_image_vae.safetensors | 242MB | VAE | 本地 ComfyUI/models/vae/ |
| qwen3vl_4b_fp8_scaled.safetensors | 4.88GB | 文本编码器（推理） | 本地 ComfyUI/models/text_encoders/ |
| qwen3vl_4b_bf16.safetensors | 8GB | 文本编码器（训练） | 服务器 |

### 8.2 训练产出

| 文件 | 大小 | 说明 |
|------|------|------|
| myface_krea2_lora.safetensors | 224MB | 最终 LoRA（=step1200） |
| myface_krea2_lora-step00000300.safetensors | 224MB | step300 checkpoint |
| myface_krea2_lora-step00000600.safetensors | 224MB | step600 checkpoint |
| myface_krea2_lora-step00000900.safetensors | 224MB | step900 checkpoint |
| myface_krea2_lora-step00001200.safetensors | 224MB | step1200 checkpoint |

### 8.3 配置与工作流

| 文件 | 说明 |
|------|------|
| dataset.toml | 数据集配置文件（已按本报告重建入库：[training/dataset.toml](./training/dataset.toml)） |
| training_command.sh | 完整训练命令（已按本报告重建入库：[training/training_command.sh](./training/training_command.sh)） |
| krea2_raw_lora_test.json | ComfyUI 推理工作流 |
| events.out.tfevents.* | TensorBoard 训练日志 |

### 8.4 样例图目录结构

```
Week1/Day3/samples/
├── comparison/     # 无LoRA vs 有LoRA对比 + 触发词泄漏 2×2 矩阵（git 中保留）
├── front/          # 正面证件照（含 CFG 3/4/7 对比、4个checkpoint）
├── side/           # 侧面（4个checkpoint）
├── smile/          # 微笑（4个checkpoint）
├── outdoor/        # 户外（4个checkpoint）
├── fullbody/       # 全身（4个checkpoint）
└── artistic/       # 艺术感（4个checkpoint）
```

---

## 9. 经验总结

1. **FP8 ≠ 训练友好**：ComfyUI 格式的 FP8 量化文件是给推理用的，训练必须用 BF16/FP16 权重，配合运行时 FP8 量化省显存
2. **显存不够的三件套**：`fp8_base + fp8_scaled` + `gradient_checkpointing` + 训练时不生成样例图（省文本编码器显存）
3. **Gated 仓库有替代**：官方 gated 仓库访问不了时，找 Comfy-Org 等社区维护的非 gated 镜像
4. **Checkpoint 一定要多存**：不同 step 适合不同场景，step600 微笑好、step1200 户外好，只存最终版会错过最佳效果
5. **触发词泄露是过拟合信号**：如果生成图片中出现触发词的变形文字，说明该 step 开始过拟合，应降低 step 或 strength
6. **数据集决定上限**：39 张脸部特写只能训练出脸部特写 LoRA，想要全身效果必须有全身照，数据集多样性决定泛化能力
7. **云服务器磁盘要提前规划**：容器根目录通常只有 20-40GB，大模型文件要放数据盘或内存盘

---

*报告生成时间：2026-09-02*
*训练工具：Musubi Tuner v0.3.4*
*基座模型：Krea 2 RAW*
