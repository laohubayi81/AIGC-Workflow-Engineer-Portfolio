"""合并 LTX I2V → ReActor 换脸 → 超分+RIFE 三图为单文件全链实验 JSON。

规则：
- B/C 段节点 ID +100/+200，链接 ID +100/+200，纵向错开布局
- B/C 段入口 LoadVideo 静音(mode=4)并断开，改由上一段 CreateVideo/SaveVideo 的 VIDEO 直连
- 分组框标注三段；主 Note 写明 OOM 风险与渐进解锁步骤
"""
import copy
import json

BASE = "D:/my/AIGC-Workflow-Engineer-Portfolio/workflows/video-modules/"

a = json.load(open(BASE + "LTX2.3_i2v.json", encoding="utf-8"))
b = json.load(open(BASE + "reactor_video.json", encoding="utf-8"))
c = json.load(open(BASE + "day17_upscale_rife.json", encoding="utf-8"))


def take(g, node_off, link_off, y_off):
    g = copy.deepcopy(g)
    for n in g["nodes"]:
        n["id"] += node_off
        n["pos"][1] += y_off
        for inp in n.get("inputs", []):
            if inp.get("link") is not None:
                inp["link"] += link_off
        for o in n.get("outputs", []):
            if o.get("links"):
                o["links"] = [x + link_off for x in o["links"]]
    for l in g["links"]:
        l[0] += link_off
        l[1] += node_off
        l[3] += node_off
    return g


B = take(b, 100, 100, 1600)
C = take(c, 200, 200, 3200)

# B/C 段入口 LoadVideo 静音 + 断开其输出；GetVideoComponents 的 video 输入置空待重接
for g, load_id, get_id in ((B, 101, 102), (C, 201, 202)):
    for n in g["nodes"]:
        if n["id"] == load_id:
            n["mode"] = 4
            for o in n.get("outputs", []):
                o["links"] = None
            n["title"] = "LoadVideo (muted)"
        if n["id"] == get_id:
            for inp in n.get("inputs", []):
                if inp["name"] == "video":
                    inp["link"] = None
    g["links"] = [l for l in g["links"] if not (l[3] == get_id and l[5] == "VIDEO")]

# 跨段接线：A.SaveVideo(27) -> B.GetVideoComponents(102)；B.CreateVideo(105) -> C.GetVideoComponents(202)
for n in a["nodes"]:
    if n["id"] == 27:
        for o in n.get("outputs", []):
            if o["type"] == "VIDEO":
                o["links"] = (o.get("links") or []) + [300]

for g, src_out, lid in ((B, 105, 301),):
    for n in g["nodes"]:
        if n["id"] == src_out:
            for o in n.get("outputs", []):
                if o["type"] == "VIDEO" and o["links"]:
                    o["links"].append(lid)

new_links = [
    [300, 27, 0, 102, 0, "VIDEO"],
    [301, 105, 0, 202, 0, "VIDEO"],
]

for g in (a, B, C):
    for n in g["nodes"]:
        for o in n.get("outputs", []):
            if o.get("links") and 300 in o["links"]:
                pass

master_note = {
    "id": 300,
    "type": "Note",
    "pos": [3460, 1650],
    "size": [820, 420],
    "flags": {},
    "order": 99,
    "mode": 0,
    "inputs": [],
    "outputs": [],
    "properties": {},
    "widgets_values": [
        "动作迁移全链实验（LTX I2V -> ReActor 换脸 -> 超分+RIFE，一张图）\n"
        "\n"
        "⚠️ Day 18 实测：这种全链同 Queue 在 16GB 上会 OOM。本图就是来验证短片(25f)上结论是否仍成立。\n"
        "\n"
        "渐进跑法：\n"
        "1. 先框选 Stage C 整段 Ctrl+M 静音，只跑 A+B；成功后解禁 C 再跑全链\n"
        "2. LTX 的 Load Image 换成编辑后的首帧——先用 day5_routeA_krea2edit.json 做换人+换背景（见 motion-demo.md Step 1）\n"
        "3. ReActor source face = 00027.jpg（需在 input 目录）\n"
        "4. Length 25 起步；OOM 就改 17 帧 + ImageScale 256x384\n"
        "5. 三段输出：video/LTX_i2v_*.mp4 -> ReActor_i2v_*.mp4 -> Day17_upscale_rife_*.mp4\n"
        "\n"
        "保底方案：按 motion-demo.md 三段接力手动跑（每段单独 Queue）"
    ],
}

merged = {
    "id": "motion-demo-fullchain",
    "revision": 0,
    "last_node_id": 300,
    "last_link_id": 301,
    "nodes": a["nodes"] + B["nodes"] + C["nodes"] + [master_note],
    "links": a["links"] + B["links"] + C["links"] + new_links,
    "groups": [
        {"id": 1, "title": "Stage A · LTX I2V 驱动", "bounding": [30, 20, 3330, 1530], "color": "#3f5152", "font_size": 28, "flags": {}},
        {"id": 2, "title": "Stage B · ReActor 逐帧锁脸", "bounding": [30, 1630, 1800, 1060], "color": "#a1309b", "font_size": 28, "flags": {}},
        {"id": 3, "title": "Stage C · 超分 + RIFE", "bounding": [30, 3230, 2130, 780], "color": "#b06634", "font_size": 28, "flags": {}},
    ],
    "config": {},
    "extra": {},
    "version": 0.4,
}

out = BASE + "motion_demo_fullchain.json"
with open(out, "w", encoding="utf-8") as f:
    json.dump(merged, f, ensure_ascii=False, indent=2)
print("written:", out, "| nodes:", len(merged["nodes"]), "| links:", len(merged["links"]))
