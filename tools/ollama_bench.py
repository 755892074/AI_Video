import urllib.request, json, time, os

OLLAMA = "http://100.67.139.74:11434/api/chat"
OUTDIR = "F:/WorkBuddy/AI_Video/shots"
os.makedirs(OUTDIR, exist_ok=True)

PROMPT = """你是一位擅长暗黑、强情绪题材的资深编剧。请创作一部名为《蚀骨》的暗黑复仇短剧，基调冷峻、有张力、敢写狠话、不自我审查，但严格禁止任何色情/性描写。
请严格按以下结构用中文输出：
## 一、核心人物（2-3人）每人含：姓名、年龄、外貌特征、性格、核心动机。
## 二、关键场景（3个）每个含：场景名、时间、环境氛围。
## 三、分镜（6镜）每一镜含：镜号、画面描述（动作/机位/光影）、中文对白（自然像真人说话）、承接（接上一镜结尾、本镜结尾停在哪个动作/情绪）。
要求：人物前后一致不OOC，剧情连贯有因果，对白推动冲突。直接输出内容，不要解释。"""

def chat(model, num_gpu, attempts=3):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": PROMPT}],
        "stream": False,
        "options": {"num_gpu": num_gpu, "temperature": 0.85, "num_predict": 900, "keep_alive": 0},
    }
    data = json.dumps(payload).encode()
    last = None
    for i in range(attempts):
        try:
            req = urllib.request.Request(
                OLLAMA, data=data, headers={"Content-Type": "application/json"})
            t0 = time.perf_counter()
            with urllib.request.urlopen(req, timeout=1800) as r:
                resp = json.loads(r.read().decode())
            dt = time.perf_counter() - t0
            content = resp["message"]["content"]
            ev = resp.get("eval_count") or 0
            return content, dt, ev
        except Exception as e:
            last = e
            print(f"  attempt {i+1} failed: {e}; retry in 5s", flush=True)
            time.sleep(5)
    raise last

def main():
    rows = []
    for model in ["qwenab", "mythomax"]:
        for mode, ng in [("cpu", 0), ("gpu", 999)]:
            print(f"=== {model} / {mode} (num_gpu={ng}) ===", flush=True)
            content, dt, ev = chat(model, ng)
            fn = f"bench_{model}_{mode}.md"
            with open(os.path.join(OUTDIR, fn), "w", encoding="utf-8") as f:
                f.write(content)
            tps = ev / dt if dt > 0 and ev else 0
            rows.append((model, mode, dt, ev, tps))
            print(f"  -> {dt:.1f}s, {ev} tok, {tps:.1f} tok/s, saved {fn}", flush=True)
    print("\n===== TIMING SUMMARY =====", flush=True)
    for model, mode, dt, ev, tps in rows:
        print(f"{model:10s} {mode:4s} {dt:7.1f}s  {ev:5d} tok  {tps:5.1f} tok/s", flush=True)

if __name__ == "__main__":
    main()
