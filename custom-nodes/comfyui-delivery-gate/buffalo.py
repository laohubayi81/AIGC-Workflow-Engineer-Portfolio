"""Minimal buffalo_l (SCRFD det_10g + ArcFace w600k_r50) via onnxruntime.

Uses weights already on disk from ReActor:
  models/insightface/models/buffalo_l/{det_10g,w600k_r50}.onnx
No insightface Python package (ComfyUI 3.13 venv cannot pip it while ORT is loaded).
"""
from __future__ import annotations

import os

import cv2
import numpy as np
import onnxruntime as ort

_DET = None
_REC = None
_DET_PATH = None
_REC_PATH = None


def _session(path: str, use_gpu: bool) -> ort.InferenceSession:
    providers = ["CPUExecutionProvider"]
    if use_gpu:
        providers = ["CUDAExecutionProvider", "CPUExecutionProvider"]
    so = ort.SessionOptions()
    so.log_severity_level = 3
    try:
        return ort.InferenceSession(path, sess_options=so, providers=providers)
    except Exception:
        return ort.InferenceSession(path, sess_options=so, providers=["CPUExecutionProvider"])


def _load(det_path: str, rec_path: str, use_gpu: bool):
    global _DET, _REC, _DET_PATH, _REC_PATH
    key = (det_path, rec_path, use_gpu)
    if _DET is not None and (_DET_PATH, _REC_PATH, use_gpu) == key:
        return
    if not os.path.isfile(det_path):
        raise FileNotFoundError(f"缺少检测模型: {det_path}")
    if not os.path.isfile(rec_path):
        raise FileNotFoundError(f"缺少识别模型: {rec_path}")
    _DET = _session(det_path, use_gpu)
    _REC = _session(rec_path, use_gpu)
    _DET_PATH, _REC_PATH = det_path, rec_path


def _nms(dets: np.ndarray, thresh: float) -> np.ndarray:
    if dets.size == 0:
        return dets
    x1, y1, x2, y2, s = dets[:, 0], dets[:, 1], dets[:, 2], dets[:, 3], dets[:, 4]
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = s.argsort()[::-1]
    keep = []
    while order.size > 0:
        i = int(order[0])
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        ovr = w * h / (areas[i] + areas[order[1:]] - w * h)
        order = order[1:][ovr <= thresh]
    return dets[keep]


def detect_largest(bgr: np.ndarray, det_thresh: float = 0.5) -> tuple[np.ndarray, np.ndarray] | None:
    """Return (bbox xyxy, 5 kps) for the largest face, or None."""
    assert _DET is not None
    h0, w0 = bgr.shape[:2]
    im_ratio = h0 / float(w0)
    if im_ratio > 1:
        new_h, new_w = 640, int(640 / im_ratio)
    else:
        new_w, new_h = 640, int(640 * im_ratio)
    det_scale = new_h / float(h0)
    resized = cv2.resize(bgr, (new_w, new_h))
    canvas = np.zeros((640, 640, 3), dtype=np.uint8)
    canvas[:new_h, :new_w] = resized
    blob = cv2.dnn.blobFromImage(canvas, 1.0 / 128.0, (640, 640), (127.5, 127.5, 127.5), swapRB=True)
    inp = _DET.get_inputs()[0].name
    out_names = [o.name for o in _DET.get_outputs()]
    net_outs = _DET.run(out_names, {inp: blob})
    scores_list, bboxes_list, kps_list = [], [], []
    fmc = 3
    for idx, stride in enumerate((8, 16, 32)):
        scores = net_outs[idx]
        bbox_preds = net_outs[idx + fmc] * stride
        kps_preds = net_outs[idx + fmc * 2] * stride
        height = 640 // stride
        width = 640 // stride
        anchor_centers = np.stack(np.mgrid[:height, :width][::-1], axis=-1).astype(np.float32)
        anchor_centers = (anchor_centers * stride).reshape((-1, 2))
        anchor_centers = np.stack([anchor_centers, anchor_centers], axis=1).reshape((-1, 2))
        pos = np.where(scores.reshape(-1) >= det_thresh)[0]
        if pos.size == 0:
            continue
        scores_list.append(scores.reshape(-1)[pos])
        bboxes = np.hstack([anchor_centers[pos] - bbox_preds.reshape(-1, 4)[pos, :2],
                            anchor_centers[pos] + bbox_preds.reshape(-1, 4)[pos, 2:]])
        bboxes_list.append(bboxes)
        kp = kps_preds.reshape(-1, 10)[pos]
        kp = anchor_centers[pos][:, None, :].repeat(5, axis=1) + kp.reshape(-1, 5, 2)
        kps_list.append(kp)
    if not scores_list:
        return None
    scores = np.concatenate(scores_list)
    bboxes = np.concatenate(bboxes_list) / det_scale
    kps = np.concatenate(kps_list) / det_scale
    dets = np.hstack([bboxes, scores[:, None]])
    dets = _nms(dets, 0.4)
    if dets.size == 0:
        return None
    # match kps to remaining boxes by score order after nms — recompute via IoU on pre-nms
    # simpler: take pre-nms argmax area among nms survivors
    areas = (dets[:, 2] - dets[:, 0]) * (dets[:, 3] - dets[:, 1])
    j = int(np.argmax(areas))
    box = dets[j, :4]
    # nearest pre-nms kps by bbox center
    centers = (bboxes[:, :2] + bboxes[:, 2:]) / 2
    target = (box[:2] + box[2:]) / 2
    k = int(np.argmin(((centers - target) ** 2).sum(axis=1)))
    return box, kps[k]


def _align(bgr: np.ndarray, kps: np.ndarray, size: int = 112) -> np.ndarray:
    dst = np.array(
        [
            [38.2946, 51.6963],
            [73.5318, 51.5014],
            [56.0252, 71.7366],
            [41.5493, 92.3655],
            [70.7299, 92.2041],
        ],
        dtype=np.float32,
    )
    tform, _ = cv2.estimateAffinePartial2D(kps.astype(np.float32), dst, method=cv2.LMEDS)
    if tform is None:
        x1, y1, x2, y2 = 0, 0, bgr.shape[1], bgr.shape[0]
        crop = bgr[y1:y2, x1:x2]
        return cv2.resize(crop, (size, size))
    return cv2.warpAffine(bgr, tform, (size, size), borderValue=0.0)


def embed(bgr: np.ndarray) -> np.ndarray | None:
    found = detect_largest(bgr)
    if found is None:
        return None
    _, kps = found
    face = _align(bgr, kps)
    blob = cv2.dnn.blobFromImage(face, 1.0 / 127.5, (112, 112), (127.5, 127.5, 127.5), swapRB=True)
    inp = _REC.get_inputs()[0].name
    out = _REC.get_outputs()[0].name
    vec = _REC.run([out], {inp: blob})[0].reshape(-1).astype(np.float32)
    n = np.linalg.norm(vec) + 1e-9
    return vec / n


def cosine(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.dot(a, b))


def prepare(models_dir: str, use_gpu: bool = True) -> None:
    base = os.path.join(models_dir, "insightface", "models", "buffalo_l")
    _load(os.path.join(base, "det_10g.onnx"), os.path.join(base, "w600k_r50.onnx"), use_gpu)
