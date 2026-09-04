"""Delivery-gate nodes: identity check after generate, LTX length check before sample."""
from __future__ import annotations

import os

import numpy as np
import torch

from . import buffalo

try:
    import folder_paths
except ImportError:
    folder_paths = None


def _models_dir() -> str:
    if folder_paths is not None:
        return folder_paths.models_dir
    return os.path.join(os.path.dirname(__file__), "..", "..", "models")


def _tensor_to_bgr(image: torch.Tensor) -> np.ndarray:
    t = image[0].detach().cpu().float().numpy()
    t = (np.clip(t, 0.0, 1.0) * 255.0).astype(np.uint8)
    import cv2
    return cv2.cvtColor(t, cv2.COLOR_RGB2BGR)


class IdentityGate:
    """Compare generated image (or first video frame) to a reference face. Day 4 used the same metric."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "generated": ("IMAGE",),
                "reference": ("IMAGE",),
                "threshold": ("FLOAT", {"default": 0.50, "min": 0.0, "max": 1.0, "step": 0.01}),
                "fail_if_below": ("BOOLEAN", {"default": False}),
            }
        }

    RETURN_TYPES = ("IMAGE", "FLOAT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("image", "similarity", "passed", "report")
    FUNCTION = "run"
    CATEGORY = "aigc/delivery"
    OUTPUT_NODE = True

    def run(self, generated, reference, threshold, fail_if_below):
        buffalo.prepare(_models_dir(), use_gpu=False)
        gen = _tensor_to_bgr(generated)
        ref = _tensor_to_bgr(reference)
        n_frames = int(generated.shape[0])
        ev = buffalo.embed(gen)
        rv = buffalo.embed(ref)
        if ev is None:
            sim, passed, note = 0.0, False, "generated: no face"
        elif rv is None:
            sim, passed, note = 0.0, False, "reference: no face"
        else:
            sim = buffalo.cosine(ev, rv)
            passed = sim >= float(threshold)
            extra = f", batch_frames={n_frames} (scored first)" if n_frames > 1 else ""
            note = f"cosine={sim:.4f} threshold={float(threshold):.2f}{' PASS' if passed else ' FAIL'}{extra}"
        if fail_if_below and not passed:
            raise RuntimeError(f"IdentityGate rejected: {note}")
        return (generated, round(sim, 4), passed, note)


class LtxLengthGuard:
    """LTX frame count must be 8n+1. Invalid length wastes a 70–320s run."""

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "length": ("INT", {"default": 25, "min": 9, "max": 257, "step": 1}),
                "fail_if_invalid": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("INT", "BOOLEAN", "STRING")
    RETURN_NAMES = ("length", "ok", "report")
    FUNCTION = "run"
    CATEGORY = "aigc/delivery"
    OUTPUT_NODE = True

    def run(self, length, fail_if_invalid):
        n = int(length)
        ok = n >= 9 and (n - 1) % 8 == 0
        seconds = n / 24.0
        report = f"length={n} ({seconds:.2f}s @24fps) {'OK 8n+1' if ok else 'INVALID, use 9/17/25/49/73/121'}"
        if fail_if_invalid and not ok:
            raise RuntimeError(f"LtxLengthGuard: {report}")
        return (n, ok, report)


NODE_CLASS_MAPPINGS = {
    "IdentityGate": IdentityGate,
    "LtxLengthGuard": LtxLengthGuard,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "IdentityGate": "Identity Gate (InsightFace cosine)",
    "LtxLengthGuard": "LTX Length Guard (8n+1)",
}
