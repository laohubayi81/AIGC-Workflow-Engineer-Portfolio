# 数字人写真批量队列

场景**不写死**。提示词存在 `scenes.json`，自己起名保存；CSV 用场景名，或直接写 `prompt` 列。

## 保存一个场景

```powershell
cd D:\my\AIGC-Workflow-Engineer-Portfolio
python agent-project\examples\save_scene.py library "ohwx, close-up portrait of a person in a quiet library, looking at camera, warm lamp light, photorealistic, 8k"
python agent-project\examples\save_scene.py --list
```

会写入 `scenes.json`。Depth 链建议提示词里带 `close-up` 和 `looking at camera`。

## 单张：临时提示词（不入库）

```powershell
python agent-project\examples\generate_one.py
```

或自己调：

```python
c.generate(image="00027.jpg", prompt="ohwx, close-up portrait of a person at a cafe, looking at camera, photorealistic, 8k")
c.generate(image="00027.jpg", scene="library")  # 用已保存的名字
```

换图：文件先复制到 `D:\Comfy-Desktop\ComfyUI-Shared\input\`，`image` 只写文件名。

## CSV 队列

列：`id,image,scene,prompt,seed,prefix`

- 用场景库：`scene` 填名字，`prompt` 留空
- 一次性自定义：`scene` 留空，`prompt` 写句子（逗号要加引号）

```text
051,00027.jpg,library,,301,Queue_library_051
052,me.jpg,,"ohwx, close-up portrait of a person on a rooftop, looking at camera, city skyline, photorealistic, 8k",302,Queue_roof_052
```

```powershell
python agent-project\examples\run_queue.py --limit 5
python agent-project\examples\run_queue.py
```
