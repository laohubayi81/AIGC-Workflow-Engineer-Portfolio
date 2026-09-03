# Agent 最小闭环

第 5 周核心：自然语言请求 → 参数 schema 校验 → 选择工作流 → 调用 ComfyUI API → 返回结果。v1 不做自动调参、复杂质量评估、自动重试。

第 2 周的 Python API 封装会先落在本模块。

## 核心功能

- 状态机 6 步（解析 / 校验 / 选工作流 / 调 API / 返回）
- 工作流注册表（JSON Schema）
- 批量任务 + 简单结果检查（文件存在、尺寸、是否有效）

## 效果展示

第 5 周状态机未开始。第 2 周 ComfyUI 客户端已可用：

```powershell
python agent-project/examples/generate_one.py
```

`generate(scene="studio")` 约 57s；进度走 WebSocket `progress value/max`。

批量：`python agent-project/examples/run_queue.py`（CSV 50 条，可 `--limit` / `--state` 续跑）。Day 12 实跑 50/50 成功。

## 技术栈

Python 标准库（HTTP + 自研最小 WebSocket，无 pip 依赖）+ ComfyUI `/prompt` `/history` `/ws`。

## 安装 / 使用

- 客户端：`agent-project/src/comfy_client.py`
  - `generate()`：单张；校验 scene/seed/strength；HTTP 失败指数退避重试
  - `batch_generate()`：串行，单张失败不阻断后续
  - `on_progress`：WebSocket 回调（连不上则静默，仍靠 history 收尾）
- 场景库：`workflows/queue/scenes.json`（`save_scene.py` 增改；不限于 park/studio/night）
- 单张可直接 `prompt=` 不入库；队列 CSV 用 `scene` 名或 `prompt` 列
- 图必须已在 `ComfyUI-Shared/input/`，参数只传文件名

中文出图 Skill：`.grok/skills/digital-portrait/SKILL.md`（用户级副本 `~/.grok/skills/digital-portrait/`）。对 Agent 说中文场景 + 参考图即可。

v1 局限：不上传本地任意路径、不做质量评估、batch 只串行。自动选工作流归 Week 5。
