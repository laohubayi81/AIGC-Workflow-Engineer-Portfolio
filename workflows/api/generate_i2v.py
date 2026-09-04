"""Day 19 最小调用：POST /prompt 一条 LTX 图生视频，轮询 /history。ComfyUI 需已开。"""
import json
import sys
import time
import urllib.request
import uuid
from pathlib import Path

API = "http://127.0.0.1:8188"
API_JSON = Path(__file__).with_name("i2v_api.json")


def main():
    prompt = json.loads(API_JSON.read_text(encoding="utf-8"))
    client_id = uuid.uuid4().hex
    body = json.dumps({"prompt": prompt, "client_id": client_id}).encode()
    req = urllib.request.Request(API + "/prompt", data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=60) as r:
            resp = json.loads(r.read())
    except Exception as e:
        sys.exit(f"POST /prompt 失败（ComfyUI 开了吗）：{e}")
    pid = resp.get("prompt_id")
    if not pid:
        sys.exit(f"没有 prompt_id: {resp}")
    print(f"queued {pid}", flush=True)
    t0 = time.time()
    while True:
        time.sleep(3)
        with urllib.request.urlopen(f"{API}/history/{pid}", timeout=30) as r:
            h = json.loads(r.read())
        if pid not in h:
            print(f"waiting {time.time()-t0:.0f}s", flush=True)
            continue
        st = h[pid].get("status", {})
        print(f"status={st.get('status_str')} {time.time()-t0:.0f}s", flush=True)
        if st.get("status_str") == "success" or st.get("completed"):
            outs = []
            for node in h[pid].get("outputs", {}).values():
                for key in ("images", "gifs", "videos"):
                    for im in node.get(key) or []:
                        fn = im.get("filename")
                        if fn:
                            sub = im.get("subfolder") or ""
                            outs.append(f"{sub}/{fn}" if sub else fn)
            print("outputs:", ", ".join(outs) or "(none)", flush=True)
            return
        if st.get("status_str") == "error":
            sys.exit(f"execution error: {st}")


if __name__ == "__main__":
    main()
