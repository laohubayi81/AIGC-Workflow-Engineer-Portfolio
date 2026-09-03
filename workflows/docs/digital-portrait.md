# 数字人写真（Day 8）

**主干就是 Week 1 路线 B**（Depth CN + myface），不是新模型、也不是超分。Day 8 做的是把它收成一条可给客户用的生产链。

JSON：[`../digital_portrait.json`](../digital_portrait.json)

## 和路线 B 差在哪

| | 路线 B（实验） | 本工作流（生产） |
|---|---|---|
| 目的 | 扫 strength 0.6 vs 1.0，证明 Depth 有没有锁构图 | 一张自拍 → 多套写真 |
| 输入 | 假定图已经能直接喂 | **先 center-crop 到 768**，任意尺寸自拍都能进 |
| Depth | 对照用 1.0 / 0.6 | 固定 **0.8** |
| 输出 | 实验前缀 | `Portrait_final` + `Portrait_depth_qc` |
| 后处理 | 无 | **不做假超分**（768 就是成片；真超分归 Week 3） |
| 场景 | 一张 prompt 扫参数 | 同一套参数换 prompt：公园 / 棚拍 / 夜景 |

生成能力与 B 相同。面试时就这么说，不要说「我做了全新 16 节点流水线」。

## 链路

客户自拍 → ImageScale 768 crop → Depth 预处理 → Depth CN 0.8 + myface 0.85 → KSampler → 768 成片 + 深度质检图。

## 默认参数

- 底模 RAW FP8 · 参考图 `00027.jpg` · seed 42/fixed · invert 不要勾
- prompt 必须 `close-up` + `looking at camera`

## 场景 / 提示词

不再写死三种场景。保存到 `workflows/queue/scenes.json`，或单次传入 prompt。见 [队列说明](../queue/README.md)。

仍建议提示词带 `close-up` + `looking at camera`。

### 原先三套（已作为示例写进场景库）

公园：

```
ohwx, close-up portrait of a person in a sunlit park, looking at camera, trees in the background, photorealistic, sharp focus, 8k
```

室内棚拍：

```
ohwx, close-up studio portrait of a person, looking at camera, softbox lighting, plain grey backdrop, photorealistic, sharp focus, 8k
```

夜景虚化：

```
ohwx, close-up portrait of a person at night, looking at camera, city bokeh lights in the background, photorealistic, sharp focus, 8k
```

## 换装 / 换证件底

那是路线 A（Identity Edit），另一条产品，不要塞进这张图。

## Day 9 边界

今天：1 自拍 × 3 场景能出片。耗时、显存、成功率、单件成本是 Day 9。
