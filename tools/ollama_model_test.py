"""经 TailScale 调台式机 ollama(:11434)，对比 qwenab / mythomax 的剧本写作能力。

安全约定：
- num_gpu=0 强制纯 CPU，不占台式机 16GB 显存，与正在跑的 ComfyUI/H3 零冲突。
- keep_alive=0 用完即卸载模型。
- 主题为非色情的暗黑/强情绪题材，仅用于评测模型创作力/中文对白/结构服从/连贯性。

用法：python ollama_model_test.py
输出：shots/model_test_<model>.md
"""
import urllib.request
import json
import os
import time

OLLAMA = "http://100.67.139.74:11434/api/chat"
OUT_DIR = "F:/WorkBuddy/AI_Video/shots"

THEME_PROMPT = """你是一位擅长暗黑、强情绪题材的资深编剧。请创作一部名为《蚀骨》的暗黑复仇短剧，基调冷峻、有张力、敢写狠话、不自我审查，但严格禁止任何色情或性描写。

请严格按以下结构用中文输出：

## 一、核心人物（2-3人）
每人含：姓名、年龄、外貌特征、性格、核心动机。

## 二、关键场景（3个）
每个含：场景名、时间、环境氛围。

## 三、分镜（6镜）
每一镜含：
- 镜号
- 画面描述（动作/机位/光影）
- 中文对白（自然、像真人说话，不要书面腔、不要翻译腔）
- 承接（本镜如何接上一镜结尾；本镜结尾停在哪个动作/情绪，供下一镜接力）

要求：人物前后一致不OOC，剧情连贯有因果，对白推动冲突。直接输出内容，不要开头结尾的解释。"""


def chat(model, prompt, num_gpu=0, num_predict=1100):
    payload = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}],
        "stream": False,
        "options": {
            "num_gpu": num_gpu,
            "temperature": 0.85,
            "num_predict": num_predict,
            "keep_alive": 0,
        },
    }
    req = urllib.request.Request(
        OLLAMA,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=2400) as r:
        resp = json.loads(r.read().decode("utf-8"))
    cost = time.time() - t0
    return resp["message"]["content"], cost


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    models = ["qwenab", "mythomax"]
    for m in models:
        print(f"=== 开始测试 {m} (CPU, num_gpu=0) ===", flush=True)
        try:
            out, cost = chat(m, THEME_PROMPT)
        except Exception as e:
            print(f"!! {m} 失败: {e}", flush=True)
            continue
        path = os.path.join(OUT_DIR, f"model_test_{m}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(out)
        print(f"==> 保存 {path} （{len(out)} 字，耗时 {cost:.0f}s）", flush=True)


if __name__ == "__main__":
    main()
