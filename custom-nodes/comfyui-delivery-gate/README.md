# Delivery Gate（身份质检 + LTX 帧数校验）

数字人交付不能靠眼看。生成图/视频第一帧和自拍算 InsightFace 余弦；低于阈值标失败。LTX 的 Length 必须是 `8n+1`，填错会白跑 70–320 秒。

节点：`IdentityGate`、`LtxLengthGuard`。`NODE_CLASS_MAPPINGS` 在 `__init__.py`。

不依赖 `insightface` 包（本机 ComfyUI 是 Python 3.13，装不上）。检测/识别用已经在盘上的 ReActor 权重：

`models/insightface/models/buffalo_l/det_10g.onnx` + `w600k_r50.onnx`

## 本机冒烟（脚本，非 Comfy 节点）

| 对比 | 余弦 |
|---|---|
| `00027.jpg` vs 自己 | **1.00** |
| `00027.jpg` vs `portrait_cafe.png`（LoRA 写真） | **0.54** |
| `00027.jpg` vs `ref_noloRA_step900.png`（无 LoRA） | **-0.00** |

默认阈值 **0.50**：写真过、无 LoRA 不过。Day 4 官方 InsightFace 脚本对 step900 LoRA 是 0.62，实现不同，阈值以本节点冒烟为准，不要混报。

## 安装

把本目录拷到（或 junction）：

`D:\Comfy-Desktop\ComfyUI-Installs\ComfyUI\ComfyUI\custom_nodes\comfyui-delivery-gate`

重启 ComfyUI。搜索 `Identity Gate` / `LTX Length Guard`。

## 参数

**Identity Gate**

| 输入 | 含义 |
|---|---|
| generated | 生成图；视频则取**第一帧** |
| reference | 自拍参考 |
| threshold | 默认 0.50 |
| fail_if_below | true 时不通过就让 Queue 失败（给 API/队列用） |

输出：`image`（原样传出）、`similarity`、`passed`、`report`。

**LTX Length Guard**：Length 接到这个节点再接到 `EmptyLTXVLatentVideo`。不是 `8n+1` 且 `fail_if_invalid` 时直接报错。

## 接到队列

`fail_if_below=true` 时 identity 不达标会 `RuntimeError`，`/history` 记 error，CSV 队列记 FAIL，不把废片当成功。

写真 API 已挂节点 `19`。2026-09-04 `generate_one.py` 跑通，成片 `Api_portrait_00003_.png`（Save 在门禁之后）。默认 `fail_if_below=false`。
