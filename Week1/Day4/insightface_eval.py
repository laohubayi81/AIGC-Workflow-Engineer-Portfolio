#!/usr/bin/env python
"""Krea 2 人物 LoRA 身份相似度评估（InsightFace 余弦相似度）

用 InsightFace buffalo_l 提取人脸嵌入，计算生成图与参考自拍的余弦相似度，
作为"非纯人眼"的量化评估指标。

用法（建议用独立评估环境，见同目录 README.md）：
  python insightface_eval.py --ref <参考自拍.jpg> --images <图1> <图2> ... [--out <输出.md>] [--cpu]
"""
import argparse
import glob
import os
import sys


def main():
    ap = argparse.ArgumentParser(description="InsightFace 身份相似度评估")
    ap.add_argument("--ref", required=True, help="参考人脸图（原始自拍）")
    ap.add_argument("--images", nargs="+", required=True, help="待评估图片，可多个，支持通配符")
    ap.add_argument("--out", help="输出 markdown 路径（可选，缺省只打印）")
    ap.add_argument("--cpu", action="store_true", help="强制 CPU 推理")
    args = ap.parse_args()

    import numpy as np
    import cv2
    from insightface.app import FaceAnalysis

    providers = ["CPUExecutionProvider"] if args.cpu else ["CUDAExecutionProvider", "CPUExecutionProvider"]
    app = FaceAnalysis(name="buffalo_l", providers=providers)
    app.prepare(ctx_id=-1 if args.cpu else 0, det_size=(640, 640))

    def embed(path):
        # np.fromfile + imdecode：兼容中文路径
        img = cv2.imdecode(np.fromfile(path, dtype=np.uint8), cv2.IMREAD_COLOR)
        if img is None:
            return None, "读图失败"
        faces = app.get(img)
        if not faces:
            return None, "未检出人脸"
        # 多人脸时取最大（主体人物）
        f = max(faces, key=lambda x: (x.bbox[2] - x.bbox[0]) * (x.bbox[3] - x.bbox[1]))
        return f.normed_embedding, ""

    ref_vec, err = embed(args.ref)
    if ref_vec is None:
        sys.exit(f"参考图无法提取人脸: {args.ref} ({err})")

    paths = []
    for p in args.images:
        hits = sorted(glob.glob(p))
        paths.extend(hits if hits else [p])

    rows, sims = [], []
    for p in paths:
        vec, err = embed(p)
        if vec is None:
            rows.append((p, None, err))
        else:
            sim = float(np.dot(ref_vec, vec))  # normed_embedding 点积 = 余弦相似度
            rows.append((p, sim, ""))
            sims.append(sim)

    lines = [
        "# InsightFace 身份相似度评估",
        "",
        f"- 参考图：`{args.ref}`",
        "- 模型：buffalo_l（SCRFD 人脸检测 + ArcFace 嵌入，多脸取最大）",
        "- 指标：余弦相似度（-1~1）。经验参考：同人不同照片约 0.4–0.7，>0.6 高度相似，<0.2 基本判定不同人",
        "",
        "| 图片 | 相似度 | 备注 |",
        "|---|---|---|",
    ]
    for p, sim, err in rows:
        name = os.path.basename(p)
        if sim is not None:
            lines.append(f"| `{name}` | {sim:.4f} | |")
        else:
            lines.append(f"| `{name}` | - | {err} |")
    if sims:
        lines += [
            "",
            f"**统计**：均值 {np.mean(sims):.4f} · 最高 {np.max(sims):.4f} · 最低 {np.min(sims):.4f}（n={len(sims)}）",
        ]
    report = "\n".join(lines) + "\n"
    print(report)
    if args.out:
        os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
        with open(args.out, "w", encoding="utf-8") as f:
            f.write(report)
        print(f"已写入 {args.out}")


if __name__ == "__main__":
    main()
