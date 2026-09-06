# -*- coding: utf-8 -*-
"""
qwen_t2i.py - 本地 Qwen-Image 文生图（0 积分，走本机 ComfyUI）
用法:
  python tools/qwen_t2i.py --prompt "..." --negative "..." \
      --width 576 --height 1024 --steps 20 --cfg 4 \
      --sampler euler --scheduler simple --prefix qwen_t2i \
      --out "D:/xxx/style_test" --seed 42
模型链: UNETLoader(qwen_image_fp8) + CLIPLoader(type=qwen_image) + TextEncodeQwenImageEdit(纯文本)
       + EmptySD3LatentImage + KSampler + VAEDecode(qwen_image_vae)
"""
import json, os, sys, time, argparse, random, urllib.request, urllib.parse

COMFY = "http://100.67.139.74:8188"
COMFY_OUT = r"D:/Comfy-Desktop/ComfyUI-Installs/ComfyUI/ComfyUI/output"

def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))

def http_json(url, data=None, timeout=30):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    with _opener().open(req, timeout=timeout) as r:
        return json.loads(r.read().decode())

def download_image(img, dst_dir):
    """沙箱读不到宿主 ComfyUI output 盘，走 /view HTTP 下载"""
    q = urllib.parse.urlencode({"filename": img["filename"],
                                "subfolder": img.get("subfolder", ""),
                                "type": img.get("type", "output")})
    os.makedirs(dst_dir, exist_ok=True)
    dst = os.path.join(dst_dir, img["filename"])
    with _opener().open(f"{COMFY}/view?{q}", timeout=120) as r, open(dst, "wb") as f:
        f.write(r.read())
    return dst

def build_workflow(prompt, negative, w, h, steps, cfg, sampler, scheduler, seed, prefix, batch=1):
    return {
        "1": {"class_type": "UNETLoader", "inputs": {"unet_name": "qwen_image_fp8_e4m3fn.safetensors", "weight_dtype": "default"}},
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": "qwen_2.5_vl_7b_fp8_scaled.safetensors", "type": "qwen_image"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": "qwen_image_vae.safetensors"}},
        "4": {"class_type": "TextEncodeQwenImageEdit", "inputs": {"clip": ["2", 0], "prompt": prompt}},
        "5": {"class_type": "TextEncodeQwenImageEdit", "inputs": {"clip": ["2", 0], "prompt": negative}},
        "6": {"class_type": "EmptySD3LatentImage", "inputs": {"width": w, "height": h, "batch_size": batch}},
        "7": {"class_type": "KSampler", "inputs": {
            "model": ["1", 0], "seed": seed, "steps": steps, "cfg": cfg,
            "sampler_name": sampler, "scheduler": scheduler,
            "positive": ["4", 0], "negative": ["5", 0],
            "latent_image": ["6", 0], "denoise": 1.0}},
        "8": {"class_type": "VAEDecode", "inputs": {"samples": ["7", 0], "vae": ["3", 0]}},
        "9": {"class_type": "SaveImage", "inputs": {"images": ["8", 0], "filename_prefix": prefix}},
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prompt", required=True)
    ap.add_argument("--negative", default="text, watermark, logo, signature, lowres, blurry, jpeg artifacts, deformed, extra fingers, bad anatomy")
    ap.add_argument("--width", type=int, default=576)
    ap.add_argument("--height", type=int, default=1024)
    ap.add_argument("--steps", type=int, default=20)
    ap.add_argument("--cfg", type=float, default=4.0)
    ap.add_argument("--sampler", default="euler")
    ap.add_argument("--scheduler", default="simple")
    ap.add_argument("--prefix", default="qwen_t2i")
    ap.add_argument("--out", default=None, help="把成图拷贝到该目录")
    ap.add_argument("--seed", type=int, default=None)
    ap.add_argument("--batch", type=int, default=1, help="一次采样 N 张（同 prompt 变体，GPU 利用率高）")
    ap.add_argument("--wait", type=int, default=1800, help="最长等待秒数")
    a = ap.parse_args()

    seed = a.seed if a.seed is not None else random.randint(1, 2**31)
    wf = build_workflow(a.prompt, a.negative, a.width, a.height, a.steps, a.cfg,
                        a.sampler, a.scheduler, seed, a.prefix, a.batch)
    print(f"[submit] {a.width}x{a.height} steps={a.steps} cfg={a.cfg} seed={seed} batch={a.batch}")
    pid = http_json(f"{COMFY}/prompt", {"prompt": wf, "client_id": "qwen_t2i"})["prompt_id"]
    print(f"[pid] {pid}")

    # 轮询结果
    t0 = time.time()
    while time.time() - t0 < a.wait:
        time.sleep(6)
        try:
            h = http_json(f"{COMFY}/history/{pid}", timeout=15)
        except Exception:
            continue
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "success":
                imgs = []
                for nid, nd in h[pid]["outputs"].items():
                    for img in nd.get("images", []):
                        imgs.append(img)
                if imgs:
                    for img in imgs:
                        print(f"[done] {COMFY}/view ...{img['filename']}")
                        if a.out:
                            dst = download_image(img, a.out)
                            print(f"[copy] {dst}")
                    return
            msgs = st.get("messages", [])
            for m in msgs:
                if m[0] == "execution_error":
                    print("[ERROR]", json.dumps(m[1], ensure_ascii=False)[:2000])
                    sys.exit(1)
        # 进度
        if int(time.time() - t0) % 60 < 6:
            print(f"[waiting] {int(time.time()-t0)}s ...")
    print("[timeout] 未在窗口内完成")
    sys.exit(2)

if __name__ == "__main__":
    main()
