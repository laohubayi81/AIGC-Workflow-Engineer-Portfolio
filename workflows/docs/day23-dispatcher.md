# 任务分发器（Day 23）

把 CSV 任务派到 **N 个 ComfyUI**。每个 worker 同时只跑 1 条（一台卡上已经 14GB 写真，两进程会 OOM）。

| 文件 | |
|---|---|
| [`../queue/workers.json`](../queue/workers.json) | 默认 1 个：`127.0.0.1:8188`（和现在串行队列一样） |
| [`../../agent-project/src/dispatcher.py`](../../agent-project/src/dispatcher.py) | 线程池，`max_inflight ≤ worker 数` |
| [`../../agent-project/examples/run_dispatch.py`](../../agent-project/examples/run_dispatch.py) | 入口 |

未做云端双实例（Docker `up` 已跳过）。本机验证是 **`--dry-run` + 2 个假 worker**：6 条任务，`max_inflight=2`。

用户复跑（2026-09-04）：`ok=6 fail=0 max_inflight=2`，墙钟 0.16s。

## 命令

逻辑验证（不占 GPU）：

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
python agent-project\examples\run_dispatch.py --limit 6
```

真打本机 Comfy（只有一台，和 `run_queue.py` 等价）：

```powershell
python agent-project\examples\run_dispatch.py --live --limit 1
```

第二台实例：另开 Comfy 在 8189，在 `workers.json` 加 `{"name":"local-b","base_url":"http://127.0.0.1:8189"}`。16GB 不要两台同时跑 Krea/LTX。
