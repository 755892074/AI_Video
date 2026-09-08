# -*- coding: utf-8 -*-
"""qwen_image_tool.py - ComfyUI Qwen-Image img2img/文生图 CLI
用法:
  python qwen_image_tool.py --image gray_frame_80.png --positive "text" \
      --negative "text" --denoise 0.72 --prefix gray2real --outdir D:/xxx
说明: image 可为本地路径(自动上传到 ComfyUI input) 或已上传文件名
模型: qwen_image_fp8_e4m3fn + qwen_2.5_vl_7b_fp8 + qwen_image_vae
"""
import argparse, json, os, sys, time, urllib.request, uuid

HOST = "http://127.0.0.1:8188"
UNET = "qwen_image_fp8_e4m3fn.safetensors"
CLIP_NAME = "qwen_2.5_vl_7b_fp8_scaled.safetensors"
VAE_NAME = "qwen_image_vae.safetensors"


def api(path, data=None, method="GET"):
    url = HOST + path
    req = urllib.request.Request(url, data=data, method=method)
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode("utf-8"))


def upload(path):
    # multipart 上传
    boundary = uuid.uuid4().hex
    fname = os.path.basename(path)
    with open(path, "rb") as f:
        content = f.read()
    body = (
        f"--{boundary}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{fname}\"\r\n"
        f"Content-Type: image/png\r\n\r\n"
    ).encode("utf-8") + content + f"\r\n--{boundary}\r\nContent-Disposition: form-data; name=\"overwrite\"\r\n\r\ntrue\r\n--{boundary}--\r\n".encode("utf-8")
    req = urllib.request.Request(HOST + "/upload/image", data=body, method="POST")
    req.add_header("Content-Type", f"multipart/form-data; boundary={boundary}")
    with urllib.request.urlopen(req, timeout=120) as r:
        out = json.loads(r.read().decode("utf-8"))
    print(f"[up] {fname} -> {out.get('name')}")
    return out.get("name")


def build(name, positive, negative, denoise, steps, cfg, seed, prefix):
    nodes = {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": UNET, "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": CLIP_NAME, "type": "qwen_image", "device": "default"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": VAE_NAME}},
        "4": {"class_type": "LoadImage", "inputs": {"image": name}},
        "5": {"class_type": "VAEEncode", "inputs": {"pixels": ["4", 0], "vae": ["3", 0]}},
        "6": {"class_type": "CLIPTextEncode", "inputs": {"text": positive, "clip": ["2", 0]}},
        "7": {"class_type": "CLIPTextEncode", "inputs": {"text": negative, "clip": ["2", 0]}},
        "8": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "positive": ["6", 0], "negative": ["7", 0], "latent_image": ["5", 0],
            "seed": seed, "steps": steps, "cfg": cfg, "sampler_name": "euler",
            "scheduler": "simple", "denoise": denoise}},
        "9": {"class_type": "VAEDecode", "inputs": {"samples": ["8", 0], "vae": ["3", 0]}},
        "10": {"class_type": "SaveImage", "inputs": {"images": ["9", 0], "filename_prefix": prefix}},
    }
    return nodes


def submit(nodes):
    data = json.dumps({"prompt": nodes, "client_id": "g2r-" + uuid.uuid4().hex[:8]}).encode("utf-8")
    out = api("/prompt", data=data, method="POST")
    if "error" in out:
        print("SUBMIT_ERROR:", json.dumps(out, ensure_ascii=False)[:800]); sys.exit(1)
    pid = out.get("prompt_id")
    print(f"[submit] pid={pid}")
    return pid


def wait_download(pid, prefix, outdir):
    os.makedirs(outdir, exist_ok=True)
    deadline = time.time() + 900
    while time.time() < deadline:
        hist = api("/history/" + pid)
        if pid in hist:
            outs = hist[pid].get("outputs", {})
            for nid, o in outs.items():
                for img in o.get("images", []):
                    fn = img["filename"]; sub = img.get("subfolder", ""); typ = img.get("type", "output")
                    if fn.startswith(prefix) or True:
                        url = f"{HOST}/view?filename={fn}&subfolder={sub}&type={typ}"
                        local = os.path.join(outdir, fn)
                        req = urllib.request.Request(url)
                        with urllib.request.urlopen(req, timeout=120) as r:
                            data = r.read()
                        with open(local, "wb") as f:
                            f.write(data)
                        print(f"[out] {local}  {len(data)/1024:.0f} KB")
                        return local
        time.sleep(5)
    print("[timeout] 900s 未等到结果"); sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--image", required=True, help="本地图片路径或 ComfyUI 已上传文件名")
    ap.add_argument("--positive", required=True)
    ap.add_argument("--negative", default="low quality, watermark, text")
    ap.add_argument("--denoise", type=float, default=0.72)
    ap.add_argument("--steps", type=int, default=24)
    ap.add_argument("--cfg", type=float, default=3.5)
    ap.add_argument("--seed", type=int, default=12345)
    ap.add_argument("--prefix", default="gray2real")
    ap.add_argument("--outdir", default=".")
    a = ap.parse_args()

    name = a.image
    if os.path.exists(a.image):
        name = upload(a.image)
    nodes = build(name, a.positive, a.negative, a.denoise, a.steps, a.cfg, a.seed, a.prefix)
    pid = submit(nodes)
    wait_download(pid, a.prefix, a.outdir)


if __name__ == "__main__":
    main()
