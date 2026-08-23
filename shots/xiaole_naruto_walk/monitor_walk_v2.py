import json, time, urllib.request, urllib.parse, os, sys

COMFY = "http://127.0.0.1:8188"
PID = "a5fbc394-ac0c-43d5-97ae-b62513215359"
OUTDIR = "D:/WorkBuddy/AI_Video/shots/xiaole_naruto_walk/output"


def get(url):
    try:
        return json.load(urllib.request.urlopen(url, timeout=10))
    except Exception as e:
        return {"_err": str(e)}


print("[monitor] 开始轮询 prompt_id=%s" % PID, flush=True)
for i in range(120):  # 最多 120*30s = 60 分钟
    q = get(COMFY + "/queue")
    running = [t for t in q.get("queue_running", []) if t[1] == PID]
    pending = [t for t in q.get("queue_pending", []) if t[1] == PID]
    h = get(COMFY + "/history/" + PID)
    if h:
        print("[monitor] 任务进入 history，开始提取输出", flush=True)
        found = []
        for entry in h.values():
            for node, o in entry.get("outputs", {}).items():
                for v in (o.get("videos") or []):
                    found.append((v.get("filename"), v.get("subfolder", "")))
                for v in (o.get("images") or []):
                    found.append((v.get("filename"), v.get("subfolder", "")))
        if not found:
            print("[monitor] history 无输出，可能执行报错:", flush=True)
            for entry in h.values():
                for m in entry.get("status", {}).get("messages", []):
                    if isinstance(m, list) and m[0] in ("execution_error", "error"):
                        print("   ERR:", m[1], flush=True)
            sys.exit(2)
        os.makedirs(OUTDIR, exist_ok=True)
        for fn, sub in found:
            params = urllib.parse.urlencode({"filename": fn, "subfolder": sub, "type": "output"})
            data = urllib.request.urlopen(COMFY + "/view?" + params, timeout=120).read()
            dest = os.path.join(OUTDIR, os.path.basename(fn))
            open(dest, "wb").write(data)
            print("[monitor] 已下载 -> %s (%d bytes)" % (dest, len(data)), flush=True)
        print("[monitor] 完成退出", flush=True)
        sys.exit(0)
    status = "running" if running else ("pending" if pending else "unknown")
    print("[monitor] 第%d次: %s (running=%d pending=%d)" % (i + 1, status, len(running), len(pending)), flush=True)
    time.sleep(30)

print("[monitor] 超时(60分钟)仍未完成，请手动检查", flush=True)
