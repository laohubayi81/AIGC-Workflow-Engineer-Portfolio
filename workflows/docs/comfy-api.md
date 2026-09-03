# ComfyUI API（Day 10）

画布里拖的 JSON **不能**直接 POST 到 `/prompt`。前端 workflow 带节点坐标、连线 id、widgets；API 只要 `class_type` + `inputs`。

## 两个必踩坑

1. **前端 workflow ≠ API Format**  
   `digital_portrait.json` 是给 ComfyUI 桌面打开的。HTTP 调用用 `workflows/api/portrait_api.json`（节点字典）。把 UI JSON 原样 POST 会 400。
2. **进度必须走 WebSocket**  
   `POST /prompt` 只返回 `prompt_id`，不会推百分比。轮询 `GET /history/{id}` 只能知道完没完。节点级进度要连 `ws://127.0.0.1:8188/ws?clientId=`。Day 10 最小脚本用 history 轮询；Day 11 再加 WS 回调。

## 会用到的接口

| 接口 | 作用 |
|---|---|
| `POST /prompt` | 投递 API Format 图，拿 `prompt_id` |
| `GET /history/{id}` | 完成态、输出文件名、报错 |
| `GET /view?filename=&type=output` | 读生成图 |
| `GET /object_info` | 节点类型与输入定义（对 JSON） |
| `GET /queue` | 排队长度 |
| `WS /ws` | 执行进度 |

## 最小调用

ComfyUI 已开：

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
python workflows\api\generate_portrait.py
```

默认公园场景、`00027.jpg`、seed 42。成功会打印输出文件名。约 57 秒（底模已在显存里时）。

Day 10 实测：`queued 33907aea-…` → `status=success 57s` → `Api_portrait_depth_00001_.png, Api_portrait_00001_.png`。

Day 11 封装：`agent-project/src/comfy_client.py`（`generate` / `batch_generate` / WS 进度 / 指数退避）。
