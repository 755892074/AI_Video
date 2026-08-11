#!/usr/bin/env python3
"""Run a MiniMax H3 Reference-to-Video (R2V) workflow on the desktop ComfyUI.

Pipeline:
  1. upload storyboard / character / scene images to ComfyUI input dir
  2. patch the 2 LoadImage ref nodes + add a 3rd LoadImage for the scene
  3. append the 3rd ref to H3 ref_images (so it becomes Picture 1/2/3)
  4. set the prompt node text
  5. submit /prompt, poll /history, download the resulting MP4
"""
import json, os, sys, uuid, time, argparse, urllib.request, urllib.error, urllib.parse

def _post_multipart(url, path):
    boundary = "----workbuddy" + uuid.uuid4().hex
    with open(path, "rb") as f:
        data = f.read()
    head = (
        f"--{boundary}\r\n"
        f'Content-Disposition: form-data; name="image"; filename="{os.path.basename(path)}"\r\n'
        "Content-Type: application/octet-stream\r\n\r\n"
    ).encode("utf-8")
    body = head + data + f"\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(url + "/upload/image", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=180) as r:
        return json.loads(r.read().decode("utf-8"))["name"]

def _post_json(url, endpoint, payload, timeout=60):
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(url + endpoint, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def _get_json(url, endpoint, timeout=30):
    with urllib.request.urlopen(url + endpoint, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))

def submit(url, prompt):
    return _post_json(url, "/prompt", {"prompt": prompt, "client_id": uuid.uuid4().hex})["prompt_id"]

def wait(url, pid, interval=5, timeout=1500):
    deadline = time.time() + timeout
    last = None
    while time.time() < deadline:
        try:
            h = _get_json(url, f"/history/{pid}")
        except Exception:
            h = {}
        if pid in h:
            return h[pid]
        # surface immediate execution errors
        last = h
        time.sleep(interval)
    return last

def download(url, filename, subfolder, ftype, out_path):
    params = urllib.parse.urlencode({"filename": filename, "subfolder": subfolder, "type": ftype})
    with urllib.request.urlopen(url + f"/view?{params}", timeout=180) as r:
        data = r.read()
    with open(out_path, "wb") as f:
        f.write(data)
    return out_path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workflow", required=True)
    ap.add_argument("--comfy-url", default="http://100.67.139.74:8188")
    ap.add_argument("--storyboard", required=True)
    ap.add_argument("--character", required=True)
    ap.add_argument("--scene", required=True)
    ap.add_argument("--prompt-file", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--storyboard-node", default="137")
    ap.add_argument("--character-node", default="139")
    ap.add_argument("--scene-node", default="900")
    ap.add_argument("--h3-node", default="136")
    ap.add_argument("--prompt-node", default="138")
    a = ap.parse_args()

    wf = json.load(open(a.workflow, encoding="utf-8"))
    p = wf["prompt"]
    prompt_text = open(a.prompt_file, encoding="utf-8").read().strip()

    print("[1/5] uploading images ...", flush=True)
    sb = _post_multipart(a.comfy_url, a.storyboard)
    ch = _post_multipart(a.comfy_url, a.character)
    sc = _post_multipart(a.comfy_url, a.scene)
    print(f"      storyboard={sb} character={ch} scene={sc}", flush=True)

    print("[2/5] patching workflow ...", flush=True)
    p[a.storyboard_node]["inputs"]["image"] = sb
    p[a.character_node]["inputs"]["image"] = ch
    p[a.scene_node] = {"class_type": "LoadImage", "inputs": {"image": sc}}
    # 3rd reference image: H3 autogrow uses full sub-input key "ref_images.ref_image_2"
    p[a.h3_node]["inputs"]["ref_images.ref_image_2"] = [a.scene_node, 0]
    p[a.prompt_node]["inputs"]["value"] = prompt_text
    print("      H3 ref_images: 3 references wired (0=storyboard,1=character,2=scene)", flush=True)

    print("[3/5] submitting ...", flush=True)
    pid = submit(a.comfy_url, p)
    print(f"      prompt_id={pid}", flush=True)

    print("[4/5] waiting for generation ...", flush=True)
    res = wait(a.comfy_url, pid)

    # surface errors
    status = res.get("status", {}) if isinstance(res, dict) else {}
    if status.get("status_str") == "error":
        msgs = status.get("messages", [])
        print("EXECUTION ERROR:", json.dumps(msgs, ensure_ascii=False)[:2000], file=sys.stderr)
        sys.exit(1)
    if not isinstance(res, dict) or "outputs" not in res:
        print("UNEXPECTED HISTORY:", json.dumps(res, ensure_ascii=False)[:1000], file=sys.stderr)
        sys.exit(1)

    outputs = res["outputs"]
    vid = None
    for nid, o in outputs.items():
        if not isinstance(o, dict):
            continue
        # H3 SaveVideo returns {"images":[{...}], "animated":[true]} (not "videos")
        if o.get("videos"):
            vid = o["videos"][0]
            break
        if o.get("images") and o.get("animated"):
            vid = o["images"][0]
            break
    if not vid:
        print("NO VIDEO OUTPUT. outputs:", json.dumps(outputs, ensure_ascii=False)[:1500], file=sys.stderr)
        sys.exit(1)

    print("[5/5] downloading MP4 ...", flush=True)
    os.makedirs(a.output, exist_ok=True)
    out_path = os.path.join(a.output, os.path.basename(vid["filename"]))
    download(a.comfy_url, vid["filename"], vid.get("subfolder", ""), vid.get("type", "output"), out_path)
    print(f"DONE -> {out_path}  ({os.path.getsize(out_path)} bytes)", flush=True)

if __name__ == "__main__":
    main()
