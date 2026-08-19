# -*- coding: utf-8 -*-
"""监控《小乐拜师记》7 镜生成并下载。"""
import json
import os
import time
import urllib.request
import urllib.parse

BASE = "http://100.67.139.74:8188"
WORK = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = r"c:/Users/Lionel/WorkBuddy/Claw/ai_video_results/xiaole_baishi"
os.makedirs(OUT_DIR, exist_ok=True)

pids = json.load(open(os.path.join(WORK, "pids.json"), encoding="utf-8"))
name_by_pid = {s["pid"]: s["name"] for s in pids}


def is_done(pid: str) -> tuple[bool, str]:
    try:
        with urllib.request.urlopen(f"{BASE}/history/{pid}", timeout=10) as r:
            h = json.load(r)
        if pid not in h:
            return False, ""
        st = h[pid].get("status", {}).get("status_str", "")
        if st == "error":
            return True, "ERROR"
        outputs = h[pid].get("outputs", {})
        for nid, o in outputs.items():
            for key in ("gifs", "videos"):
                for v in o.get(key, []):
                    if v.get("filename", "").endswith(".mp4"):
                        return True, "DONE"
        if st == "success":
            return True, "DONE"
        return False, st
    except Exception:
        return False, ""


def download(pid: str, name: str) -> None:
    with urllib.request.urlopen(f"{BASE}/history/{pid}", timeout=10) as r:
        h = json.load(r)[pid]
    for nid, o in h.get("outputs", {}).items():
        for key in ("gifs", "videos"):
            for v in o.get(key, []):
                if v.get("filename", "").endswith(".mp4"):
                    fn = v["filename"]
                    sub = v.get("subfolder", "")
                    url = f"{BASE}/view?filename={urllib.parse.quote(fn)}&subfolder={urllib.parse.quote(sub)}&type=output"
                    dest = os.path.join(OUT_DIR, f"{name}_{fn}")
                    with urllib.request.urlopen(url, timeout=120) as rr:
                        data = rr.read()
                    with open(dest, "wb") as fh:
                        fh.write(data)
                    print(f"✅ {name} → {dest} ({len(data)//1024}KB)", flush=True)
                    return
    print(f"⚠️ {name} 未找到 mp4 输出", flush=True)


def main() -> None:
    pending = {pid: name_by_pid.get(pid, pid) for pid in name_by_pid}
    start = time.time()
    while pending:
        time.sleep(30)
        for pid in list(pending):
            done, st = is_done(pid)
            if done:
                name = pending.pop(pid)
                if st == "ERROR":
                    print(f"❌ {name} 出错", flush=True)
                else:
                    download(pid, name)
        if pending:
            elapsed = int(time.time() - start)
            print(f"⏳ 剩余 {len(pending)} 镜, 已运行 {elapsed//60}min", flush=True)
    print("🎉 全部完成", flush=True)


if __name__ == "__main__":
    main()
