# 自定义节点

选题：**交付门禁**（计划三选一里的「生成结果质量检测」+ 顺手做 LTX 帧数校验）。不是玩具节点：写真/视频身份不过阈值就不算交付；Length 填错会白跑 70–320 秒。

包：[`comfyui-delivery-gate`](./comfyui-delivery-gate/)

| 节点 | 作用 |
|---|---|
| `IdentityGate` | 生成图（或视频第一帧）vs 自拍，buffalo_l 余弦 |
| `LtxLengthGuard` | Length 必须 `8n+1` |

安装、参数、冒烟数字 → [comfyui-delivery-gate/README.md](./comfyui-delivery-gate/README.md)

已接到写真 API：`portrait_api.json` 节点 `19` IdentityGate（参考图=控制自拍）。`generate(..., fail_if_below=True)` 时不够像整单失败。

## 技术栈

`INPUT_TYPES` / `RETURN_TYPES` / `NODE_CLASS_MAPPINGS`。ONNX Runtime + 本机已有 `buffalo_l`。无额外 pip。

## 安装 / 使用

拷到 ComfyUI `custom_nodes/comfyui-delivery-gate` 后重启。画布搜 `Identity Gate`。
