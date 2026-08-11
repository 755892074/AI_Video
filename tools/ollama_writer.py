#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ollama_writer.py — 调台式机 ollama 写结构化短视频剧本（流水线组件）

- 经 TailScale 打到 http://100.67.139.74:11434/api/chat
- 模型默认 qwenab（9B，开放无限制，benchmark 中剧本质量最佳）
- 输出强结构化 JSON：人物(含详细 appearance 供生图) / 场景 / 分镜(含承接)
- 用完 keep_alive=0 立即卸载，释放显存给 ComfyUI

用法:
  python tools/ollama_writer.py --model qwenab --topic "..." \
      --out-json shots/figures/script.json --out-md shots/figures/script.md --num-gpu 999
"""
import argparse
import json
import os
import sys
import time
import urllib.request

OLLAMA_HOST = "http://100.67.139.74:11434"

SYSTEM_PROMPT = """你是一个专业的 AI 短视频编剧引擎。你的任务是把用户的创意转化为可以直接驱动"参考图生视频(R2V)"工作流的、结构化、强连贯的短视频剧本。

输出要求（严格遵守）：
1. 只输出一个 JSON 对象，不要任何解释、不要 markdown 代码块、不要推理过程。
2. JSON 结构必须如下：
{
  "title": "短片标题",
  "logline": "一句话梗概",
  "setting": "场景环境详细描述（用于生成场景参考图）",
  "characters": [
    {
      "id": "A",
      "name": "角色名",
      "role": "同学A/同学B",
      "age": 17,
      "appearance": "用于生图的极详细视觉描述：性别、年龄感、脸型、发型发色、瞳色、身材、穿着（上衣/裤子/鞋子）、配饰。要具体到能画三视图。",
      "personality": "性格一句话"
    }
  ],
  "shots": [
    {
      "shot_id": 1,
      "duration_sec": 5,
      "visual": "本镜画面描述（机位、人物动作、表情、光影）",
      "dialogue": "本镜中文对白（若无对白写空字符串）",
      "action": "动作/互动说明",
      "continuation": "承接说明：与上一镜同一角色、同款服装同场景；上一镜结尾发生了什么，本镜从哪里接着拍"
    }
  ],
  "total_duration_sec": 40
}
3. 所有对白必须是中文，禁止英文或其他语言。
4. 每镜 duration_sec 在 3-10 之间，全部镜头之和约 30-50 秒。
5. 镜头之间必须连贯：人物身份、服装、场景一致；用 continuation 字段显式写清承接关系。
6. 角色 appearance 要足够详细，能直接作为生图提示词生成三视图角色表。
7. 禁止任何色情、血腥、违法内容。"""


def chat(host, model, user_prompt, num_gpu, retries=3):
    url = f"{host}/api/chat"
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "options": {
            "num_gpu": num_gpu,
            "num_ctx": 8192,
            "temperature": 0.8,
            "keep_alive": 0,   # 用完立即卸载，释放显存给 ComfyUI
        },
    }
    last_err = None
    for attempt in range(1, retries + 1):
        try:
            req = urllib.request.Request(
                url, data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}, method="POST")
            with urllib.request.urlopen(req, timeout=600) as resp:
                data = json.loads(resp.read().decode("utf-8"))
            return data["message"]["content"]
        except Exception as e:  # noqa
            last_err = e
            print(f"  [retry {attempt}/{retries}] ollama 调用失败: {e}", file=sys.stderr)
            time.sleep(3 * attempt)
    raise RuntimeError(f"ollama 调用失败 after {retries} tries: {last_err}")


def extract_json(text):
    s = text.find("{")
    e = text.rfind("}")
    if s == -1 or e == -1 or e <= s:
        raise ValueError("响应中未找到 JSON 对象")
    return text[s:e + 1]


def to_md(script):
    lines = [f"# {script.get('title','未命名')}", ""]
    lines.append(f"**一句话**：{script.get('logline','')}", )
    lines.append("")
    lines.append(f"**场景**：{script.get('setting','')}", )
    lines.append("")
    lines.append("## 人物")
    for c in script.get("characters", []):
        lines.append(f"- **{c.get('name')}**（{c.get('role')}，{c.get('age')}岁）")
        lines.append(f"  - 外貌：{c.get('appearance')}")
        lines.append(f"  - 性格：{c.get('personality')}")
    lines.append("")
    lines.append(f"## 分镜（共 {script.get('total_duration_sec')} 秒）")
    for sh in script.get("shots", []):
        lines.append(f"### 镜 {sh.get('shot_id')} · {sh.get('duration_sec')}s")
        lines.append(f"- 画面：{sh.get('visual')}")
        d = sh.get('dialogue') or ''
        lines.append(f"- 对白：{d if d else '（无）'}")
        lines.append(f"- 动作：{sh.get('action')}")
        lines.append(f"- 承接：{sh.get('continuation')}")
        lines.append("")
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default=OLLAMA_HOST)
    ap.add_argument("--model", default="qwenab")
    ap.add_argument("--topic", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    ap.add_argument("--num-gpu", type=int, default=999)
    args = ap.parse_args()

    os.makedirs(os.path.dirname(os.path.abspath(args.out_json)), exist_ok=True)

    user_prompt = (args.topic + "\n\n请严格按系统要求的 JSON 结构输出剧本。")
    print(f"[ollama_writer] model={args.model} num_gpu={args.num_gpu}")
    print(f"[ollama_writer] 调用中（可能需数十秒）...")
    raw = chat(args.host, args.model, user_prompt, args.num_gpu)
    print("[ollama_writer] 收到响应，解析 JSON...")

    js = extract_json(raw)
    script = json.loads(js)

    with open(args.out_json, "w", encoding="utf-8") as f:
        json.dump(script, f, ensure_ascii=False, indent=2)
    with open(args.out_md, "w", encoding="utf-8") as f:
        f.write(to_md(script))

    n = len(script.get("shots", []))
    total = script.get("total_duration_sec")
    print(f"[ollama_writer] 完成：{n} 镜，约 {total}s")
    print(f"  JSON -> {args.out_json}")
    print(f"  MD   -> {args.out_md}")


if __name__ == "__main__":
    main()
