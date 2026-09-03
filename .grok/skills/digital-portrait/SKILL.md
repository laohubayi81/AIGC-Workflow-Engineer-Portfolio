---
name: digital-portrait
description: 中文描述数字人写真并出图。用户说中文场景（图书馆、咖啡馆、夜景等）、给参考图或自拍路径时使用。把中文翻成英文提示词，拷参考图到 ComfyUI input，调用写真工作流 generate()。触发词：写真、出图、生成一张、换场景、用这张图、参考图、自拍、digital portrait、帮我生成。
argument-hint: 中文场景描述，可附参考图路径
---

# 数字人写真（中文 → 英文提示词 → 出图）

用户用**中文**说要什么图，你负责：① 写成英文 prompt ② 准备参考图 ③ 调用本仓库的 Comfy 写真链。不要让用户自己写英文。

仓库根：`D:\my\AIGC-Workflow-Engineer-Portfolio`（若当前不在此目录，命令都 `cd` 过去再跑）。
Comfy 输入目录：`D:\Comfy-Desktop\ComfyUI-Shared\input`
成片目录：`D:\Comfy-Desktop\ComfyUI-Shared\output`
客户端：`agent-project/src/comfy_client.py`

## 步骤（必须按顺序）

### 1. 确认 ComfyUI

`http://127.0.0.1:8188/system_stats` 要通。不通就告诉用户先打开 ComfyUI Desktop，不要空跑。

### 2. 参考图

必须有一张近景、看镜头的脸。来源优先级：

1. 用户消息里的本地路径 / 附件
2. 用户说的 Comfy input 文件名（如 `00027.jpg`）
3. 都没有 → **问一张**，不要用错人的图

若给的是完整路径：复制到 input，文件名只用字母数字下划线，例如 `ref_20260903.jpg`。generate 的 `image=` **只传文件名**。

仰拍、全身、侧脸要提醒：Depth 会锁构图，效果可能怪；用户坚持就照做。

### 3. 中文 → 英文 prompt

你来翻译，不要另调翻译 API。模板：

```
ohwx, close-up portrait of a person, {场景/服装/光线的英文}, looking at camera, photorealistic, sharp focus, 8k
```

铁规则：

- 以 `ohwx,` 开头（myface 触发词）
- 默认加 `close-up` + `looking at camera`（除非用户明确要全身/侧脸，并警告 Depth）
- 只译场景、衣服、光线、时间、情绪；**不要写五官、不要写具体人名**（身份由 LoRA + 参考图负责）
- 不要堆中文拼音
- 先把英文 prompt **完整发给用户看一眼**，再出图

用户说「保存成某某场景」→ 翻译后执行：

```powershell
python agent-project\examples\save_scene.py <英文名或拼音名> "<英文prompt>"
```

名字用小写英文或拼音，不要空格。

### 4. 出图

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
python -c "import sys; sys.path.insert(0, r'agent-project'); from src.comfy_client import ComfyClient; c=ComfyClient(); r=c.generate(image='FILENAME', prompt='PROMPT', seed=SEED, prefix='Zh_portrait'); print(r)"
```

把 `FILENAME` / `PROMPT` / `SEED` 换成本轮的值。seed 用户没指定就用当前 unix 时间的后 6 位，或 42。

约 57 秒。跑完告诉用户：

- 英文 prompt（便于以后保存）
- 成片路径：`D:\Comfy-Desktop\ComfyUI-Shared\output\` + `r['files']` 里不带 `_depth` 的那张
- 深度质检图文件名（近处应白）

### 5. 失败

- 8188 不通 → 开 ComfyUI
- 参考图找不到 → 核对 input 目录
- 显存 / 红字 → 把报错原文给用户，别猜着改 Depth/LoRA

## 例子

用户：「用 00027，做一张图书馆暖光写真」

Prompt：

```
ohwx, close-up portrait of a person in a quiet library, looking at camera, warm lamp light, wooden shelves in the background, photorealistic, sharp focus, 8k
```

然后 `generate(image="00027.jpg", prompt=...)`。

用户：「把这张保存成 library」→ `save_scene.py library "..."`。以后可 `scene="library"`。
