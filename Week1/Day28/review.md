# Day 28 · Week 4 周复盘（09-05 · 照着做，10 分钟）

> **你只需要做 Step 2 和 Step 4**（Step 1/3 我已替你填好核对完）。

---

## Step 1 · 五项产物核对（我已核对 ✅ 直接看结论）

| Day | 产物 | 是否在盘 | 复盘发现（可直接用） |
|---|---|---|---|
| 22 | `deploy/README.md` Docker 方案 | ✅ | 方案完整但容器未实测——09-06 补测；面试按"方案已交付、边界已知"讲 |
| 23 | `agent-project/src/dispatcher.py` 分发器 | ✅ | dry-run 验证了派发逻辑与上限（6/6、max_inflight=2）；云端双实例留给有卡环境 |
| 24 | `workflows/benchmarks/2026-09-04-cost-compare.md` | ✅ | 三档成本口径清晰（本地实测/AutoDL 实测/RH 折算），RH 标注"未实跑" |
| 25-26 | `custom-nodes/comfyui-delivery-gate/` 节点 | ✅ | 冒烟数据有效（自拍 vs 写真 0.54 过阈、vs 无 LoRA −0.00）；画布截图待补 |
| 27 | 队列监控 `report.md` | ✅ | state 回放 P50 与实测一致，证明日志格式设计可用 |

## Step 2 · 数字汇总（直接抄进简历/面试）

| 项 | 数字 |
|---|---|
| 分发器 dry-run | 6/6 · max_inflight=2 |
| 门禁节点冒烟 | 0.54（过 0.5 阈值）· vs 无 LoRA −0.00 |
| 监控回放 | 50 张 P50=57.3s，与实测一致 |
| Docker | 方案交付，**未 up**（09-06 补测） |

## Step 3 · 完成标准对照

- [ ] ① Docker 部署 → 部分（方案 ✅ / 容器 **09-06 补测**）
- [x] ② 分发器 + 吞吐对比
- [x] ③ 成本对比报告
- [x] ④ 业务价值节点
- [x] ⑤ 监控模块
- [ ] ⑥ 持续投递 → **09-08 启动**（`docs/投递记录.md` 已备）

## Step 4 · 提交 GitHub（3 条命令，CMD 逐条粘贴）

```cmd
cd /d D:\my\AIGC-Workflow-Engineer-Portfolio
git add -A
git commit -m "Day 28: Week 4 复盘 + SDXL 基线补测 + 动迁接力手册 + IPAdapter 节点"
git push
```

push 卡住就开一下 clash 再 `git push` 重试。

## 遗留 → carry-over

- Docker `up` 实测 → **09-06 上午**
- delivery-gate 画布截图 → Queue 后补
- 云端双实例 → v2 规划（README 已写）
- 微服务/Redis+Celery → 跳过（仅上海岗对口）

## 面试讲述建议（Week 4 一段话）

*"Week 4 我把工具变成了可交付系统：多卡分发器（dry-run 验证派发上限）、批量质检门禁节点（InsightFace 阈值自动过滤）、队列监控（state 回放与实测一致）、成本对照表。Docker 方案和步骤已交付，容器在本机因网络受限未跑通——这是我知道且声明的边界。"*
