# LTX 2.3 图生视频（Day 15 冒烟）

官方模板 `Image to Video (LTX-2.3)` 是打包子图，画布改不了。本图按已跑通的文生视频 `LTX2.3视频.json` 改成可编辑图生视频。

JSON：[`../video-modules/LTX2.3_i2v.json`](../video-modules/LTX2.3_i2v.json)

## 和文生视频差在哪

| | 文生视频（已跑通） | 本图（图生视频冒烟） |
|---|---|---|
| 第一帧 | 随机噪声 | 写真经 `LTXVImgToVideoInplace` 写入 |
| 音频潜空间 | 有（2.3 是音视频模型） | **同样拼接**，但不解码声音 |
| prompt 扩写 | `TextGenerateLTX2Prompt` | 关掉，省显存 |
| 二段空间放大 | 有 | 关掉，省显存 |
| 默认尺寸 / 时长 | 约 448×256、较长 | **384×576**、Length **25**（约 1 秒） |

## 点哪里

1. ComfyUI 打开工作流 **`LTX2.3_i2v`**
2. 左边 **Load Image** 选 `portrait_cafe.png`（或近景 `00027.jpg`）
3. **Length** 保持 **25**
4. 点 **Queue**
5. 成片：`D:\Comfy-Desktop\ComfyUI-Shared\output\video\LTX_i2v_*.mp4`

爆显存：Length 改 **17**，ImageScale 改 **256 × 384**。通了再加长。正向提示只写动作，不要另写一张新脸。

## 表情别写 smile

第一次冒烟写了 `small smile`，模型会把嘴型拉得很夸张。

`portrait_cafe.png` **静帧嘴角本身是抬的**。图生视频第一帧锁的就是这张脸，后面很难变成完全不笑。要：

- **嘴别再动**：正向写 `mouth completely frozen, lips do not move`；负向直接禁 `smile, smirk, mouth movement`
- **整段都不笑**：Load Image 换成更中性的 `00027.jpg` 再 Queue

## 冷启动 vs 热启动

首次 Queue 约 **70s**：要把 unet 12.4GB + Gemma 7.1GB 从磁盘加载进内存。之后只换 Load Image 约 **20s**：权重还在，只做第一帧编码 + 8 步采样 + 解码。重启 ComfyUI 会回到约 70s。面试报两个数：冷启动 / 稳态。

## 加长（用户实测）

Length **121**（8×15+1）@ 24fps = **5.04 s**，16GB **能跑通**，用户计时约 **320 s**。本机成片含 384×576 与 1056×1920 的 121 帧文件（`LTX_i2v_00009`–`00012`）。

API/队列默认仍是 **25（约 1s）**：5 秒一条要五分钟级，批量会把队列拉爆。要 5 秒片：画布 Length 改 121，或 `generate_i2v(..., length=121)`。
