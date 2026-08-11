#!/usr/bin/env python3
"""Batch-generate a continuous 5-shot HP-style short film on the desktop ComfyUI.

- Uploads the 3 reference images ONCE (storyboard / character / scene)
- Submits 5 sequential shots with continuity cues (same boy wizard, same courtyard)
- Polls each prompt and downloads its MP4 into ep01_series/
All 5 share: identity = son real photo (harry_original.jpg), scene = Chinese countryside.
"""
import json, os, sys, time
sys.path.insert(0, "f:/WorkBuddy/AI_Video/tools")
import r2v_run as R

URL = "http://100.67.139.74:8188"
WF = "f:/WorkBuddy/AI_Video/shots/ep01/workflows/r2v_api.json"
CHAR = "f:/WorkBuddy/AI_Video/shots/hp/assets/characters/harry_original.jpg"
SCENE = "c:/Users/Lionel/Downloads/220271_openai_20260807_写实，一个中国乡村，_1.png"
STORY = "c:/Users/Lionel/Downloads/220268_openai_20260807_生成一张干净的角色三_1.png"
OUT = "f:/WorkBuddy/AI_Video/shots/hp/output/ep01_series"
os.makedirs(OUT, exist_ok=True)

# 5 shots: continuous plot, same courtyard, same little boy wizard (the son)
PROMPTS = [
    ("shot01",
     "Cinematic establishing shot. The same little Chinese boy wizard in a Gryffindor robe pushes open an old weathered wooden gate and steps into a peaceful Chinese countryside courtyard with grey brick walls under golden sunset light. He looks around curiously, eyes wide with wonder. Soft magical glimmers drifting in the air. Photorealistic, Harry Potter film style, warm cinematic tone, 4K."),
    ("shot02",
     "Close-up of the same little boy wizard. He lowers his gaze to his own open palm where tiny golden light points leak between his fingers, glowing softly. He slowly looks up, eyes wide with surprise and awe. Same grey-brick courtyard behind him, golden hour light. Photorealistic, Harry Potter film style, 4K."),
    ("shot03",
     "Medium shot of the same little boy wizard raising a small wooden wand. The golden light points gather and swirl into a glowing dandelion-spirit that flutters and circles around him. He watches it with a delighted smile. Same Chinese countryside courtyard, magical golden particles in the air. Photorealistic, Harry Potter film style, 4K."),
    ("shot04",
     "The same little boy wizard laughs, mouth open in joy, as the glowing dandelion-spirit drifts near a red sweater hanging on the clothesline that flaps gently in the breeze. He points at it playfully. Same courtyard, warm sunlight. Photorealistic, Harry Potter film style, 4K."),
    ("shot05",
     "The same little boy wizard swings his wand upward; countless dandelions lift off the ground and transform into floating stars filling the courtyard sky. He stands among them, a content and proud smile on his face. Same Chinese countryside courtyard at dusk, magical and warm. Photorealistic, Harry Potter film style, 4K."),
]

print("[upload] reference images once ...", flush=True)
sb = R._post_multipart(URL, STORY)
ch = R._post_multipart(URL, CHAR)
sc = R._post_multipart(URL, SCENE)
print(f"  storyboard={sb} character={ch} scene={sc}", flush=True)

pids = []
for name, txt in PROMPTS:
    wf = json.load(open(WF, encoding="utf-8"))
    p = wf["prompt"]
    p["137"]["inputs"]["image"] = sb
    p["139"]["inputs"]["image"] = ch
    p["900"] = {"class_type": "LoadImage", "inputs": {"image": sc}}
    p["136"]["inputs"]["ref_images.ref_image_2"] = ["900", 0]
    p["138"]["inputs"]["value"] = txt
    pid = R.submit(URL, p)
    pids.append((name, pid))
    print(f"[submit] {name} -> {pid}", flush=True)
    time.sleep(1)

print(f"[queued] {len(pids)} shots, polling ...", flush=True)
for name, pid in pids:
    res = R.wait(URL, pid, timeout=1800)
    status = res.get("status", {}) if isinstance(res, dict) else {}
    if status.get("status_str") == "error":
        print(f"[ERROR] {name}: {json.dumps(res.get('status', {}).get('messages', []), ensure_ascii=False)[:1500]}", file=sys.stderr)
        continue
    outputs = res.get("outputs", {})
    vid = None
    for nid, o in outputs.items():
        if isinstance(o, dict):
            if o.get("videos"):
                vid = o["videos"][0]; break
            if o.get("images") and o.get("animated"):
                vid = o["images"][0]; break
    if not vid:
        print(f"[NO VIDEO] {name}: {json.dumps(outputs, ensure_ascii=False)[:1000]}", file=sys.stderr)
        continue
    out_path = os.path.join(OUT, f"{name}.mp4")
    R.download(URL, vid["filename"], vid.get("subfolder", ""), vid.get("type", "output"), out_path)
    print(f"[DONE] {name} -> {out_path} ({os.path.getsize(out_path)} bytes)", flush=True)

print("[all shots done]", flush=True)
