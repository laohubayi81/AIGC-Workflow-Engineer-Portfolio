# 动作迁移 Demo · 接力手册（motion demo runbook）

> **目标产出**：一段 10-15s 成片——参考视频的动作，"你"的身体，新背景新着装。
> **时间盒**：1 天。**架构**：不硬拼一张大图（Week 3 已用 OOM 验证），四段接力，段间传文件。
> **诚实边界**：这是 I2V 驱动的**动作近似**，不是逐帧 pose transfer。v2 路线：VACE / AnimateAnyone 逐帧迁移，或 H3 API Ref2VA 真角色迁移（写进 README 的 v2 规划）。

## 链路总览

```
参考视频(自拍≤5s) → 抽首帧 → [Day5路线A: krea2edit 换人+换背景]
    → [LTX I2V 驱动动作] → [ReActor 逐帧锁脸] → [超分+RIFE] → 成片
```

六步里五步是已验证模块，唯一的"新活"是把它们按顺序跑一遍并记录每段耗时。

---

## Step 0 · 参考视频（你自己拍）

- 规格：**≤5 秒**、1080p、横屏或竖屏都行、单人、动作幅度中等（挥手/转身/走动）、光线均匀、脸部别逆光
- 肖像安全：用自己的素材；不要用网上人物视频（肖像权 + demo 可信度都受损）
- 抽首帧（Windows cmd，ffmpeg 需在 PATH）：

```cmd
ffmpeg -i ref_video.mp4 -vf "select=eq(n\,0)" -frames:v 1 first_frame.png
```

## Step 1 · 换人 + 换背景（复用 Day 5 路线 A）

1. 拖入 [`../../lora-training/workflows/day5_routeA_krea2edit.json`](../../lora-training/workflows/day5_routeA_krea2edit.json)
2. `Load Image` 节点换成 `first_frame.png`
3. 正向 prompt 改成**编辑指令**（这是 identity edit 的正确用法，不是文生图 caption）：

```
把画面中的人物替换为 ohwx 本人，穿黑色 T 恤，背景换成海边日落，保持人物当前的姿态、构图和镜头
```

4. `ref_boost` 先用 4.0（Day 5 实测推荐值）；脸不像再加到 8.0
5. 输出改名归档：`motion_demo/01_edited_frame.png`
6. 预期：单张约 60s（Day 5 基线）

## Step 2 · LTX I2V 驱动动作

1. 拖入 [`LTX2.3_i2v.json`](LTX2.3_i2v.json)，图像输入换 `01_edited_frame.png`
2. 动作 prompt 写参考视频里**实际发生的动作**（镜头 + 主体运动 + 节奏），例如：

```
The person waves their right hand slowly, then turns their head toward the camera. Static camera, medium shot, natural daylight.
```

3. 时长：**先 25f≈1s 冒烟**（热路径 20-38s），动作对了再拉到 5s（约 320s）
4. 输出归档：`motion_demo/02_i2v.mp4`

## Step 3 · ReActor 逐帧锁脸

1. 拖入 [`reactor_video.json`](reactor_video.json)
2. VIDEO 输入 = `02_i2v.mp4`；source face = 你的清晰自拍（`lora-training/datasets/self/images/00001.jpg` 同款用法则在 input 目录放一份）
3. 参数按 Day 16 结论：**restore = none**（GFPGAN 会下残）、不改发型
4. **第一次实测，把耗时记进下面的表**（Day 16 没测过视频耗时，这是要补的数字）
5. 输出归档：`motion_demo/03_faceswap.mp4`

## Step 4 · 超分 + RIFE 插帧

1. 拖入 [`day17_upscale_rife.json`](day17_upscale_rife.json)
2. VIDEO 输入 = `03_faceswap.mp4`；参数不动（4x-UltraSharp + RIFE 2x，24→48fps）
3. 基线 **58.3s**（Day 17 实测）；输出归档：`motion_demo/motion_demo_v1.mp4`

## Step 5 · 入库

- 成片 + 各段中间产物放 `workflows/video-modules/motion_demo/`
- 主 README 亮点区嵌入（MP4 或转 GIF）：

```markdown
| 参考视频 | 数字分身成片 |
|---|---|
| ![ref](workflows/video-modules/motion_demo/ref.gif) | ![demo](workflows/video-modules/motion_demo/motion_demo_v1.gif) |
```

---

## 全链耗时表（跑的时候填，数字进 benchmark）

| 段 | 耗时 | 备注 |
|---|---|---|
| Step 1 · krea2edit 换人换景 | | 单张 |
| Step 2 · LTX I2V | | 帧数/时长： |
| Step 3 · ReActor 逐帧 | | **首次实测** |
| Step 4 · 超分+RIFE | | 58.3s 基线 |
| **全链** | | 不含人工等待 |

## 失败模式与对策

| 症状 | 对策 |
|---|---|
| LTX 生成的人不像你 | 回 Step 1：编辑帧里身份要够强（ref_boost ↑），脸越正、漂移越少 |
| 动作和参考视频不像 | prompt 动作词逐条对齐参考视频；先用 1s 版精调再拉长 |
| 脸在视频中段漂移 | Step 3 必跑（ReActor 就是干这个的）；还不稳就缩短信时长 |
| OOM | 降帧数（25f）；三段分开 Queue，别合并 |
| 换背景后边缘穿帮 | 编辑指令里明确"保持人物轮廓和姿态不变"；ref_boost 微调 |

## v2 规划（写进 README，不实现）

- 逐帧姿态迁移：VACE / AnimateAnyone（需评估 16GB 显存）
- 真·角色参考迁移：海螺 H3 API Ref2VA（多参考锁定，约 1-3 元/条）
- 口型：对白镜头接口型对齐模型（Day 20 跳过项）
