import json, time, urllib.request, urllib.parse, os, sys

COMFY = "http://127.0.0.1:8188"
PID = "106d2524-5992-45c2-b158-a3ccf3cbee64"
OUTDIR = "D:/WorkBuddy/AI_Video/shots/xiaole_naruto/output"
PREFIX = "video/xiaole_naruto_shot01_rasengan"

def get(url):
    try:
        return json.load(urllib.request.urlopen(url, timeout=10))
    except Exception as e:
        return {"_err": str(e)}

print("[monitor] 开始轮询 prompt_id=%s" % PID, flush=True)
for i in range(60):  # 最多 60*30s = 30 分钟
    q = get(COMFY + "/queue")
    running = [t for t in q.get("queue_running", []) if t[1] == PID]
    pending = [t for t in q.get("queue_pending", []) if t[1] == PID]
    h = get(COMFY + "/history/" + PID)
    if h:  # 完成
        print("[monitor] 任务进入 history，开始提取输出", flush=True)
        # 找到 video 输出
        found = []
        for entry in h.values():
            outputs = entry.get("outputs", {})
            for node, o in outputs.items():
                for v in o.get("videos", []):
                    fn = v.get("filename")
                    sub = v.get("subfolder", "")
                    found.append((fn, sub))
        if not found:
            # 也检查 images（有些节点存 gif）
            for node, o in outputs.items():
                for v in o.get("images", []):
                    found.append((v.get("filename"), v.get("subfolder","")))
        os.makedirs(OUTDIR, exist_ok=True)
        for fn, sub in found:
            # 下载
            params = urllib.parse.urlencode({"filename": fn, "subfolder": sub, "type": "output"})
            url = COMFY + "/view?" + params
            data = urllib.request.urlopen(url, timeout=60).read()
            dest = os.path.join(OUTDIR, os.path.basename(fn))
            open(dest, "wb").write(data)
            print("[monitor] 已下载 -> %s (%d bytes)" % (dest, len(data)), flush=True)
        print("[monitor] 完成退出", flush=True)
        sys.exit(0)
    status = "running" if running else ("pending" if pending else "unknown")
    print("[monitor] 第%d次: %s (running=%d pending=%d)" % (i+1, status, len(running), len(pending)), flush=True)
    time.sleep(30)

print("[monitor] 超时(30分钟)仍未完成，请手动检查", flush=True)
