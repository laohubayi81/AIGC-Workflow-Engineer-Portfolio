# Day 16 换脸（ReActor）

节点：Codeberg `Gourieff/comfyui-reactor-node`（0.7，不依赖 InsightFace 编译）。
静帧 JSON：[`../video-modules/reactor_still.json`](../video-modules/reactor_still.json)
视频 JSON：[`../video-modules/reactor_video.json`](../video-modules/reactor_video.json)

## 静帧结论（已跑通）

| | |
|---|---|
| 被换 | `ref_noloRA_step900.png`（无 LoRA 女性证件照） |
| 源脸 | `00027.jpg` |
| 模型 | `inswapper_128.onnx` + 可选 GFPGAN |
| 成片 | `ComfyUI-Shared/output/ComfyUI_00001`–`00007` |

- **GFPGANv1.4.pth 第一次下残**（161MB / 应 349MB）→ `unexpected EOF`。改用完整 **v1.3**（或后来补全的 v1.4）。
- GFPGAN 会往平均脸修，身份变弱。最终 **face_restore_model = none**。
- inswapper **不改发型/头型/骨架**。女性短发底图换完仍是短发证件照，不会变成自拍。并排看换前 vs 换后，不要和自拍比。
- 侧脸、眼镜、办公室多人图：效果更弱。

身份靠 Week 2 LoRA。换脸的用途是贴到**别人的正脸/视频**上。

## 视频（已跑通）

`Load Video` → `Get Video Components` → `ReActor`（逐帧）→ `Create Video` → `Save Video`。

| | |
|---|---|
| 被换片 | `input/swap_target.mp4`（Day 15 文生视频短片，随机人脸） |
| 源脸 | `00027.jpg` |
| restore | none |
| 成片 | `ComfyUI-Shared/output/video/ReActor_i2v_00001_.mp4`、`00002_.mp4`（用户确认换通） |

未测逐帧耗时 / 显存，不编数字。闪烁留给 Day 18。不要和 LTX 同一张图画布 Queue。
