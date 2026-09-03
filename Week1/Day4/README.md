# Day 4 · 效果评估（InsightFace 身份相似度）

## 方法

- **指标**：InsightFace（buffalo_l）人脸嵌入的余弦相似度——生成图 vs 原始自拍参考图
- **管线**：SCRFD 人脸检测（多人脸取最大）→ ArcFace 嵌入（L2 归一化）→ 点积即余弦相似度
- **判读基准（经验值）**：同人不同照片相似度约 0.4–0.7；>0.6 高度相似；<0.2 基本判定为不同人
- **为什么选它**：人物 LoRA 的核心诉求是"身份还原"，InsightFace 是社区通行的人脸身份度量，比 CLIP-I 更对口、比纯人眼可复现——对应 Week 1 完成标准②"非纯人眼评估至少 1 种"

## 复现步骤

1. 建独立评估环境（ComfyUI 自带 venv 是 Python 3.13，装不了 insightface 预编译包，所以用 uv 单独建 3.11 环境）：

```bash
cd /d/my/AIGC-Workflow-Engineer-Portfolio
UV=/d/Comfy-Desktop/ComfyUI-Installs/ComfyUI/standalone-env/Scripts/uv.exe
$UV venv --python 3.11 .venv-eval
$UV pip install --python .venv-eval \
  "https://github.com/Gourieff/Assets/raw/main/Insightface/insightface-0.7.3-cp311-cp311-win_amd64.whl" \
  "albumentations==1.3.1" "numpy<2" onnxruntime opencv-python
```

> **两个必踩坑**（实测记录）：
> 1. `albumentations` 新版会拉 `albucore → stringzilla`，需现场编译 C++（要装 Visual Studio Build Tools）；钉在 `1.3.1` 绕过。
> 2. insightface 预编译 wheel 是按 **numpy 1.x ABI** 编的，numpy 2.x 会报 `dtype size changed`，必须 `numpy<2`（其余包按 numpy 2 SDK 编译，向下兼容 1.x）。

2. 运行评估（参考图选一张清晰正面自拍）：

```bash
.venv-eval/Scripts/python.exe Week1/Day4/insightface_eval.py \
  --ref lora-training/datasets/self/images/00001.jpg \
  --images <待评估图片...> \
  --out lora-training/benchmarks/2026-09-03-insightface-similarity.md
```

> 首次运行会自动下载 buffalo_l 模型（约 330MB）到 `~/.insightface/`，需联网，之后离线可用。若 GitHub 直连中途断流（实测会断），先断点续传再解压：
>
> ```bash
> curl -L -C - --retry 10 -o ~/.insightface/models/buffalo_l.zip \
>   https://github.com/deepinsight/insightface/releases/download/v0.7/buffalo_l.zip
> # 然后把 zip 解压到 ~/.insightface/models/buffalo_l/（含 det_10g.onnx 等 5 个 onnx）
> ```

## 输出

- `lora-training/benchmarks/2026-09-03-insightface-similarity.md`：逐图相似度表 + 均值/最高/最低统计
- 结论写回 [Day 3 训练报告](../Day3/training_report.md) 的效果评估章节
