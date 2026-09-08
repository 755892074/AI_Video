# -*- coding: utf-8 -*-
"""h3_itv_tool.py - MiniMax H3 纯图生视频(ImageToVideo) 提交/轮询/下载 CLI
用法:
  python h3_itv_tool.py --image sb_001.png --prompt "六段式或动作描述" \
      --prefix ep01_shot01 --outdir D:/xxx/output --frames 124 --width 1344 --height 768
说明:
  - image 可为本地路径(自动上传到 ComfyUI input) 或已上传文件名
  - 模板: shots/ep01/workflows/h3_imagetovideo_test.json (LoadImage->MiniMaxH3ImageToVideo->SaveVideo)
  - 无 ref_video 依赖; 构图/机位/方向由分镜图锁定, 运动靠文字 prompt
  - 支持多张图: --images a.png,b.png 每张独立提交一个镜(共用 prompt), 顺序排队渲染
"""
import argparse, json, os, sys, time, urllib.request, uuid, glob

HOST = os.environ.get("COMFY_HOST", "http://127.0.0.1:8188")
TEMPLATE = "D:/WorkBuddy/AI_Video/shots/ep01/workflows/h3_imagetovideo_test.json"


def api(path, data=None, method="GET"):
    url = HOST + path
    req = urllib.request.Request(url, data=data, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        body = r.read().decode("utf-8")
    return json.loads(body) if body.strip() else {}


def upload(path):
    boundary = uuid.uuid4().hex
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        content = f.read()
    ext = os.path.splitext(fname)[1].lower().lstrip(".")
    ctype = "image/png" if ext in ("png",) else "image/jpeg"
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{fname}\"\r\n"
        f"Content-Type: {ctype}\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(HOST + "/upload/image", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.loads(r.read().decode("utf-8"))
    name = out.get("name")
    print(f"[up] {fname} -> {name}", flush=True)
    return name


def submit(image_name, prompt, prefix, frames, width, height, fps=24):
    wf = json.load(open(TEMPLATE, encoding="utf-8"))
    # 找节点: LoadImage / MiniMaxH3ImageToVideo / SaveVideo
    img_nid = vid_nid = save_nid = None
    for nid, n in wf.items():
        if not isinstance(n, dict) or "class_type" not in n:
            continue
        ct = n["class_type"]
        if ct == "LoadImage":
            img_nid = nid
        elif ct == "MiniMaxH3ImageToVideo":
            vid_nid = nid
        elif ct == "SaveVideo":
            save_nid = nid
    if not (img_nid and vid_nid):
        raise RuntimeError(f"模板缺少 LoadImage/MiniMaxH3ImageToVideo: {TEMPLATE}")
    wf[img_nid]["inputs"]["image"] = image_name
    wf[vid_nid]["inputs"]["prompt"] = prompt
    wf[vid_nid]["inputs"]["width"] = int(width)
    wf[vid_nid]["inputs"]["height"] = int(height)
    wf[vid_nid]["inputs"]["length"] = int(frames)
    if save_nid:
        wf[save_nid]["inputs"]["filename_prefix"] = prefix
    # 同步 CLIPTextEncode 文本(若存在且引用同一 clip)
    for nid, n in wf.items():
        if isinstance(n, dict) and n.get("class_type") == "CLIPTextEncode":
            n["inputs"]["text"] = prompt
    payload = {"prompt": wf, "client_id": "h3-itv-" + uuid.uuid4().hex[:8]}
    req = urllib.request.Request(HOST + "/prompt", data=json.dumps(payload).encode("utf-8"), method="POST")
    req.add_header("Content-Type", "application/json")
    with urllib.request.urlopen(req, timeout=30) as r:
        out = json.loads(r.read().decode("utf-8"))
    pid = out.get("prompt_id")
    print(f"[submit] {image_name} -> prompt_id={pid} prefix={prefix}", flush=True)
    return pid


def wait_and_download(pid, outdir, prefix, timeout_min=120):
    t0 = time.time()
    while time.time() - t0 < timeout_min * 60:
        hist = api(f"/history/{pid}")
        if pid in hist:
            st = hist[pid].get("status", {})
            if st.get("completed"):
                outs = hist[pid].get("outputs", {})
                for nid, o in outs.items():
                    for v in o.get("videos", []):
                        fname = v.get("filename")
                        sub = v.get("subfolder", "")
                        url = f"{HOST}/view?filename={fname}&subfolder={sub}&type=output"
                        os.makedirs(outdir, exist_ok=True)
                        dst = os.path.join(outdir, fname)
                        urllib.request.urlretrieve(url, dst)
                        print(f"[done] {pid} -> {dst}", flush=True)
                        return dst
                # SaveVideo 有时用 gifs
                for nid, o in outs.items():
                    for v in o.get("gifs", []):
                        fname = v.get("filename")
                        url = f"{HOST}/view?filename={fname}&type=output"
                        dst = os.path.join(outdir, fname)
                        urllib.request.urlretrieve(url, dst)
                        print(f"[done] {pid} -> {dst}", flush=True)
                        return dst
                print(f"[warn] {pid} completed but no video output", flush=True)
                return None
            if st.get("status_str") == "error":
                print(f"[error] {pid}: {st}", flush=True)
                return None
        time.sleep(15)
    print(f"[timeout] {pid} >{timeout_min}min", flush=True)
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", help="单张: 本地路径或已上传名")
    ap.add_argument("--images", help="多张: 逗号分隔本地路径, 每张独立一镜")
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--prefix", required=True)
    ap.add_argument("--outdir", default="D:/WorkBuddy/AI_Video/shots/_itv_out/output")
    ap.add_argument("--frames", type=int, default=124)
    ap.add_argument("--width", type=int, default=1344)
    ap.add_argument("--height", type=int, default=768)
    ap.add_argument("--no-wait", action="store_true", help="只提交不轮询")
    args = ap.parse_args()

    imgs = []
    if args.images:
        imgs = [x.strip() for x in args.images.split(",") if x.strip()]
    elif args.image:
        imgs = [args.image]
    if not imgs:
        ap.error("需要 --image 或 --images")

    os.makedirs(args.outdir, exist_ok=True)
    ids = []
    for i, im in enumerate(imgs):
        if os.path.isfile(im):
            im = upload(im)
        pref = args.prefix if len(imgs) == 1 else f"{args.prefix}_s{i+1:02d}"
        pid = submit(im, args.prompt, pref, args.frames, args.width, args.height)
        ids.append((pid, pref))
    if args.no_wait:
        print("submitted:", ids)
        return
    for pid, pref in ids:
        wait_and_download(pid, args.outdir, pref)


if __name__ == "__main__":
    main()
