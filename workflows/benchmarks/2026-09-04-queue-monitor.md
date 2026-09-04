# 队列监控（Day 27）

对已有 `state.jsonl` 跑 `queue_report.py`（不跑 GPU）。数字与入库时一致。

## 写真 Day 12 · `20260903_174818`

| | |
|---|---|
| jobs / ok / fail | 50 / 50 / 0 |
| 成功率 | **1.0** |
| mean / P50 / P90 | **57.22** / **57.3** / **57.3** s |
| min–max | 56.5–57.4 s |
| fail_reasons | （空） |

与 [2026-09-03-queue-50.md](./2026-09-03-queue-50.md) 一致。

## 视频 Day 19 · `20260904_104240`

| | |
|---|---|
| jobs / ok / fail | 5 / 5 / 0 |
| 成功率 | **1.0** |
| mean / P50 / P90 | 30.98 / 37.1 / 40.26 s |
| min–max | 2.6–41.1 s |
| fail_reasons | （空） |

min 2.6s 是同参节点缓存，不当热启动。见 [2026-09-04-video-api.md](./2026-09-04-video-api.md)。

身份门禁失败会记 `fail_reasons.identity_gate`。本两次历史跑都未开 `fail_if_below`。
