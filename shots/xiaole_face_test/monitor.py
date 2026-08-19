# -*- coding: utf-8 -*-
"""监控 xiaole_face_test 生成并下载 mp4 到 output/"""
import json
import sys
import urllib.request
import urllib.parse
from pathlib import Path

BASE = "http://100.67.139.74:8188"
WORK = Path(r"F:/WorkBuddy/AI_Video/shots/xiaole_face_test")
OUT = WORK / "output"
OUT.mkdir(exist_ok=True)

pid = sys.argv[1]
out_path = OUT / "shot01.mp4"

deadline = 60 * 60  # 最多等 60 分钟
import time
start = time.time()
while time.time() - start < deadline:
    try:
        h = json.loads(urllib.request.urlopen(f"{BASE}/history/{pid}", timeout=30).read())
    except Exception:
        h = {}
    if pid in h:
        res = h[pid]
        st = res.get("status", {})
        if st.get("status_str") == "error":
            print("EXECUTION ERROR:", json.dumps(res.get("messages", []), ensure_ascii=False)[:800])
            sys.exit(1)
        outs = res.get("outputs", {})
        vid = None
        for nid, o in outs.items():
            if not isinstance(o, dict):
                continue
            if o.get("videos"):
                vid = o["videos"][0]; break
            if o.get("images") and isinstance(o["images"], list) and o["images"]:
                im = o["images"][0]
                if im.get("filename", "").endswith(".mp4"):
                    vid = im; break
        if vid:
            params = urllib.parse.urlencode({
                "filename": vid["filename"],
                "subfolder": vid.get("subfolder", ""),
                "type": vid.get("type", "output"),
            })
            data = urllib.request.urlopen(f"{BASE}/view?{params}", timeout=300).read()
            out_path.write_bytes(data)
            ok = b"ftyp" in data[:32]
            print(f"DONE -> {out_path} ({len(data)}B, mp4={ok})")
            sys.exit(0)
    time.sleep(10)
print("TIMEOUT: 60min 未出结果")
sys.exit(1)
