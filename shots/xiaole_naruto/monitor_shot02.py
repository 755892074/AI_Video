import json, time, urllib.request, urllib.parse, urllib.error, os, sys, uuid

COMFY = "http://127.0.0.1:8188"
WF = "D:/WorkBuddy/AI_Video/shots/xiaole_naruto/workflows/h3_ref2va_xiaole_naruto_shot02_shadowclone.json"
OUTDIR = "D:/WorkBuddy/AI_Video/shots/xiaole_naruto/output"
CLIENT_ID = str(uuid.uuid4())

def post(url, data):
    req = urllib.request.Request(url, data=json.dumps(data).encode(),
                                 headers={"Content-Type": "application/json"})
    return json.load(urllib.request.urlopen(req, timeout=60))

def get(url):
    try:
        return json.load(urllib.request.urlopen(url, timeout=10))
    except Exception as e:
        return {"_err": str(e)}

# 1) 提交工作流
with open(WF, "r", encoding="utf-8") as f:
    graph = json.load(f)
resp = post(COMFY + "/prompt", {"prompt": graph, "client_id": CLIENT_ID})
PID = resp.get("prompt_id")
if not PID:
    print("[submit] 提交失败:", resp, flush=True)
    sys.exit(1)
print("[submit] 已提交 shot02, prompt_id=%s" % PID, flush=True)

# 2) 轮询
print("[monitor] 开始轮询 shot02 prompt_id=%s" % PID, flush=True)
for i in range(60):  # 最多 30 分钟
    q = get(COMFY + "/queue")
    running = [t for t in q.get("queue_running", []) if t[1] == PID]
    pending = [t for t in q.get("queue_pending", []) if t[1] == PID]
    h = get(COMFY + "/history/" + PID)
    if h:
        print("[monitor] shot02 进入 history，提取输出", flush=True)
        found = []
        for entry in h.values():
            outputs = entry.get("outputs", {})
            for node, o in outputs.items():
                for v in o.get("videos", []):
                    found.append((v.get("filename"), v.get("subfolder", "")))
        if not found:
            for node, o in outputs.items():
                for v in o.get("images", []):
                    found.append((v.get("filename"), v.get("subfolder", "")))
        os.makedirs(OUTDIR, exist_ok=True)
        for fn, sub in found:
            params = urllib.parse.urlencode({"filename": fn, "subfolder": sub, "type": "output"})
            data = urllib.request.urlopen(COMFY + "/view?" + params, timeout=120).read()
            dest = os.path.join(OUTDIR, os.path.basename(fn))
            open(dest, "wb").write(data)
            print("[monitor] 已下载 -> %s (%d bytes)" % (dest, len(data)), flush=True)
        print("[monitor] shot02 完成退出", flush=True)
        sys.exit(0)
    status = "running" if running else ("pending" if pending else "unknown")
    print("[monitor] 第%d次: %s (running=%d pending=%d)" % (i+1, status, len(running), len(pending)), flush=True)
    time.sleep(30)

print("[monitor] shot02 超时(30分钟)仍未完成，请手动检查", flush=True)
