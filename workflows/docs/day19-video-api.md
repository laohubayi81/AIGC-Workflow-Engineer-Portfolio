# Day 19 视频 API + 分镜队列

UI 图画布 JSON **不能** POST。HTTP 用 [`../api/i2v_api.json`](../api/i2v_api.json)（从已跑通的 `LTX2.3_i2v.json` 转的 API Format）。

16GB **不要**把换脸/超分和 LTX 打进同一次 `/prompt`。本 API 只跑图生视频（Length 25）。后处理仍用 `day17_upscale_rife` 分段。

## 会改的节点

| 节点 | 字段 |
|---|---|
| `5` LoadImage | `image` 文件名 |
| `14` / `15` | 正/负向提示 |
| `19` RandomNoise | `noise_seed` |
| `9` PrimitiveInt | `value` = Length（冒烟 25） |
| `27` SaveVideo | `filename_prefix` |

## 单条

ComfyUI 已开，**不要同时在画布点 Queue**：

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
python workflows\api\generate_i2v.py
```

或：

```powershell
python agent-project\examples\generate_i2v.py
```

成片：`ComfyUI-Shared/output/video/Api_i2v_*.mp4`（最小脚本前缀是图里的 `video/LTX_i2v`；封装脚本默认 `video/Api_i2v`）。

耗时：冷启动约 70s，热启动约 20s（Day 15 用户数）。轮询 `/history` 等到 success，没有额外短超时。

## 分镜 CSV（5 条）

[`../queue/video_jobs.csv`](../queue/video_jobs.csv) + 场景库 [`../queue/video_scenes.json`](../queue/video_scenes.json)

列：`id,image,scene,prompt,seed,prefix,length`

```powershell
python agent-project\examples\run_video_queue.py --limit 1
python agent-project\examples\run_video_queue.py --limit 5
```

失败可 `--state` 指向上次 `state.jsonl` 续跑（成功过的 id 会 skip）。

## 实测（2026-09-04）

`generate_i2v.py` 出 `Api_i2v_00001_.mp4`；随后 `run_video_queue.py --limit 5`：**5/5**，墙钟 **155 s**。分条 2.6 / 41.1 / 37.1 / 39.0 / 35.1 s。首条 2.6s 是同参缓存，不当热启动。另外 4 条均值 **38.1 s**。数据：[benchmarks/2026-09-04-video-api.md](../benchmarks/2026-09-04-video-api.md)。
