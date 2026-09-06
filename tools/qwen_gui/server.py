# -*- coding: utf-8 -*-
"""
qwen_gui_server.py - 本地 AI 生成网页工具（零依赖，标准库实现）
  Tab1 文生图 : Qwen-Image（标准节点链，实测稳定，非 UI 聚合黑图节点）
  Tab2 生视频 : MiniMax H3 三种常用模式
       T2V 文生视频 / I2V 首帧图生视频 / R2V 参考图生视频(可选语音参考克隆)

启动:  python tools/qwen_gui/server.py [--port 8099]
打开:  http://127.0.0.1:8099
"""
import json, os, sys, time, threading, random, uuid, urllib.request, urllib.parse, argparse, re
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------- 配置 ----------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
COMFY = os.environ.get("COMFY_URL", "http://127.0.0.1:8188")
IMG_OUT = os.environ.get("QWEN_OUT", r"D:/WorkBuddy/AI_Video/output/qwen_gui")
VID_OUT = os.environ.get("H3_OUT", r"D:/WorkBuddy/AI_Video/output/h3_gui")
UPLOAD_DIR = os.environ.get("UPLOAD_DIR", os.path.join(BASE_DIR, "uploads"))
for _d in (IMG_OUT, VID_OUT, UPLOAD_DIR):
    os.makedirs(_d, exist_ok=True)

DEFAULT_NEG = ("text, watermark, logo, signature, lowres, blurry, jpeg artifacts, "
               "deformed, extra fingers, bad anatomy")

# H3 本机已装模型（勿引官方模板默认的 h8.control / turbo 8step lora —— 本机没有）
H3_UNET = {
    "t2v": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "i2v": "minimax_h3_fl2va_pruned_int8_convrot.safetensors",
    "r2v": "minimax_h3_ref2va_pruned_int8_convrot.safetensors",
}
H3_CLIP = "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors"
H3_VAE_VIDEO = "minimax_h3_video_vae_fp16.safetensors"
H3_VAE_AUDIO = "minimax_h3_audio_vae_fp32.safetensors"

JOBS = {}
JOBS_LOCK = threading.Lock()
JOB_SEQ = [0]

ALLOWED_OPEN = {os.path.realpath(IMG_OUT), os.path.realpath(VID_OUT)}


def _opener():
    return urllib.request.build_opener(urllib.request.ProxyHandler({}))


def http_json(url, data=None, timeout=120):
    req = urllib.request.Request(url, data=json.dumps(data).encode() if data else None,
                                 headers={"Content-Type": "application/json"})
    with _opener().open(req, timeout=timeout) as r:
        return json.loads(r.read().decode())


def http_upload(path, remote_name):
    """上传任意文件到 ComfyUI input，返回实际远端文件名。"""
    with open(path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(path)[1].lower() or ".png"
    remote_name = os.path.splitext(remote_name)[0] + ext
    boundary = uuid.uuid4().hex
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{remote_name}"\r\n'.encode()
    body += f"Content-Type: application/octet-stream\r\n\r\n".encode()
    body += data + b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{COMFY}/upload/image", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"})
    with _opener().open(req, timeout=180) as r:
        return json.loads(r.read().decode())["name"]


def download_view(meta, dst_dir):
    q = urllib.parse.urlencode({"filename": meta["filename"],
                                "subfolder": meta.get("subfolder", ""),
                                "type": meta.get("type", "output")})
    with _opener().open(f"{COMFY}/view?{q}", timeout=300) as r:
        data = r.read()
    dst = os.path.join(dst_dir, meta["filename"].replace("/", "_").replace("\\", "_"))
    with open(dst, "wb") as f:
        f.write(data)
    return dst, data


# ============ 1) Qwen-Image 文生图 workflow ============
def build_img_workflow(prompt, negative, w, h, steps, cfg, sampler, scheduler, seed, prefix, batch=1):
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


# ============ 2) MiniMax H3 视频 workflow ============
def h3_frames_for(seconds):
    """H3 帧数：24fps，模型 17k+5 网格。5s → 124 帧。"""
    n = max(5, round(float(seconds) * 24))
    return n + (5 - n % 17) % 17


def build_h3_workflow(mode, prompt, w, h, seconds, steps, seed, prefix,
                      ref_files=None, audio_file=None, sampler="res_multistep",
                      scheduler="simple"):
    """mode: t2v / i2v / r2v
    ref_files: i2v=首帧图列表(取第0张); r2v=参考图列表(1..N张) → ref_images.ref_image_i
    audio_file: r2v 语音参考(克隆对白) → ref_audios.ref_audio_0
    """
    length = h3_frames_for(seconds)
    ref_files = ref_files or []
    wf = {
        "2": {"class_type": "CLIPLoader", "inputs": {"clip_name": H3_CLIP, "type": "minimax"}},
        "3": {"class_type": "VAELoader", "inputs": {"vae_name": H3_VAE_VIDEO}},
        "4": {"class_type": "VAELoader", "inputs": {"vae_name": H3_VAE_AUDIO}},
        "10": {"class_type": "UNETLoader", "inputs": {"unet_name": H3_UNET[mode], "weight_dtype": "default"}},
    }
    next_id = 20
    load_img_ids = []
    for i, fn in enumerate(ref_files):
        nid = str(next_id); next_id += 1
        wf[nid] = {"class_type": "LoadImage", "inputs": {"image": fn}}
        load_img_ids.append(nid)

    if mode in ("t2v", "i2v"):
        inp = {"clip": ["2", 0], "vae": ["3", 0], "prompt": prompt,
               "width": w, "height": h, "length": length}
        if mode == "i2v" and load_img_ids:
            inp["first_frame"] = [load_img_ids[0], 0]
        wf["40"] = {"class_type": "MiniMaxH3ImageToVideo", "inputs": inp}
    else:  # r2v
        inp = {"clip": ["2", 0], "vae": ["3", 0], "audio_vae": ["4", 0],
               "prompt": prompt, "width": w, "height": h, "length": length,
               "ref_image_size": "match"}
        for i, nid in enumerate(load_img_ids):
            inp[f"ref_images.ref_image_{i}"] = [nid, 0]
        if audio_file:
            anid = str(next_id); next_id += 1
            wf[anid] = {"class_type": "LoadAudio", "inputs": {"audio": audio_file}}
            inp["ref_audios.ref_audio_0"] = [anid, 0]
        wf["40"] = {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": inp}

    wf.update({
        "41": {"class_type": "BasicGuider", "inputs": {"model": ["10", 0], "conditioning": ["40", 0]}},
        "42": {"class_type": "KSamplerSelect", "inputs": {"sampler_name": sampler}},
        "43": {"class_type": "BasicScheduler", "inputs": {"scheduler": scheduler, "steps": steps,
                                                          "denoise": 1, "model": ["10", 0]}},
        "44": {"class_type": "RandomNoise", "inputs": {"noise_seed": seed}},
        "45": {"class_type": "SamplerCustomAdvanced", "inputs": {
            "noise": ["44", 0], "guider": ["41", 0], "sampler": ["42", 0],
            "sigmas": ["43", 0], "latent_image": ["40", 1]}},
        "46": {"class_type": "VAEDecode", "inputs": {"samples": ["45", 0], "vae": ["3", 0]}},
        "47": {"class_type": "VAEDecodeAudio", "inputs": {"samples": ["45", 0], "vae": ["4", 0]}},
        "48": {"class_type": "CreateVideo", "inputs": {"images": ["46", 0], "audio": ["47", 0],
                                                       "fps": 24, "bit_depth": 8}},
        "49": {"class_type": "SaveVideo", "inputs": {"video": ["48", 0], "filename_prefix": prefix,
                                                     "format": "mp4", "codec": "auto"}},
    })
    return wf


# ============ 后台任务 ============
def _set_job(job_id, **kw):
    with JOBS_LOCK:
        JOBS[job_id].update(kw)


def run_img_job(job_id, p):
    t0 = time.time()
    try:
        w, h = int(p.get("width", 832)), int(p.get("height", 1216))
        steps = int(p.get("steps", 20)); cfg = float(p.get("cfg", 4.0))
        batch = max(1, min(8, int(p.get("batch", 1))))
        prefix = (p.get("prefix", "").strip() or "qwen_gui")
        seed = random.randint(1, 2**31 - 1) if p.get("seed") in (None, "", "0") else int(p.get("seed"))
        prompt = (p.get("prompt") or "").strip()
        if not prompt:
            _set_job(job_id, status="error", error="提示词不能为空", elapsed=int(time.time()-t0)); return
        negative = (p.get("negative") or "").strip() or DEFAULT_NEG
        wf = build_img_workflow(prompt, negative, w, h, steps, cfg,
                                p.get("sampler", "euler"), p.get("scheduler", "simple"),
                                seed, prefix, batch)
        _set_job(job_id, status="submitting", params={"prompt": prompt[:120], "width": w, "height": h,
                 "steps": steps, "cfg": cfg, "seed": seed, "batch": batch, "kind": "image"})
        pid = http_json(f"{COMFY}/prompt", {"prompt": wf, "client_id": f"gui_{job_id}"})["prompt_id"]
        _set_job(job_id, status="running", pid=pid, started=int(time.time()))
        deadline = t0 + int(p.get("wait", 3600))
        while time.time() < deadline:
            time.sleep(5)
            try:
                h = http_json(f"{COMFY}/history/{pid}", timeout=15)
            except Exception:
                continue
            if pid in h:
                stt = h[pid].get("status", {})
                if stt.get("completed") or stt.get("status_str") == "success":
                    imgs = [im for nd in h[pid]["outputs"].values() if isinstance(nd, dict)
                            for im in nd.get("images", [])]
                    if imgs:
                        saved = [download_view(im, IMG_OUT)[0] for im in imgs]
                        _set_job(job_id, status="done", images=[os.path.basename(s) for s in saved],
                                 elapsed=int(time.time()-t0))
                        return
                for m in stt.get("messages", []):
                    if m[0] == "execution_error":
                        _set_job(job_id, status="error", error=json.dumps(m[1], ensure_ascii=False)[:3000],
                                 elapsed=int(time.time()-t0)); return
            _set_job(job_id, elapsed=int(time.time()-t0))
        _set_job(job_id, status="error", error="超时", elapsed=int(time.time()-t0))
    except Exception as e:
        _set_job(job_id, status="error", error=repr(e)[:3000], elapsed=int(time.time()-t0))


def run_video_job(job_id, p):
    t0 = time.time()
    try:
        mode = p.get("mode", "r2v")
        w, h = int(p.get("width", 768)), int(p.get("height", 1344))
        seconds = float(p.get("seconds", 5))
        steps = int(p.get("steps", 20))
        prefix = (p.get("prefix", "").strip() or f"h3_{mode}")
        seed = random.randint(1, 2**31 - 1) if p.get("seed") in (None, "", "0") else int(p.get("seed"))
        prompt = (p.get("prompt") or "").strip()
        if not prompt:
            _set_job(job_id, status="error", error="提示词不能为空", elapsed=int(time.time()-t0)); return
        refs = p.get("refs") or []   # 上传后的远端文件名
        audio = p.get("audio") or None

        # 上传本地临时文件 → ComfyUI input（若 refs 是绝对路径先上传）
        remote_refs = []
        for rf in refs:
            if os.path.isabs(rf) and os.path.isfile(rf):
                remote_refs.append(http_upload(rf, f"gui_{job_id}_{uuid.uuid4().hex[:8]}"))
            else:
                remote_refs.append(rf)
        remote_audio = None
        if audio:
            if os.path.isabs(audio) and os.path.isfile(audio):
                remote_audio = http_upload(audio, f"gui_{job_id}_{uuid.uuid4().hex[:8]}")
            else:
                remote_audio = audio

        wf = build_h3_workflow(mode, prompt, w, h, seconds, steps, seed, prefix,
                               remote_refs, remote_audio,
                               p.get("sampler", "res_multistep"), p.get("scheduler", "simple"))
        _set_job(job_id, status="submitting", params={"prompt": prompt[:120], "mode": mode,
                 "width": w, "height": h, "seconds": seconds, "steps": steps,
                 "seed": seed, "n_refs": len(remote_refs), "kind": "video"})
        pid = http_json(f"{COMFY}/prompt", {"prompt": wf, "client_id": f"gui_{job_id}"})["prompt_id"]
        _set_job(job_id, status="running", pid=pid, started=int(time.time()))
        deadline = t0 + int(p.get("wait", 5400))
        while time.time() < deadline:
            time.sleep(8)
            try:
                h = http_json(f"{COMFY}/history/{pid}", timeout=20)
            except Exception:
                continue
            if pid in h:
                stt = h[pid].get("status", {})
                if stt.get("completed") or stt.get("status_str") == "success":
                    vids = []
                    for nd in h[pid]["outputs"].values():
                        if not isinstance(nd, dict):
                            continue
                        for im in nd.get("images", []):
                            if str(im.get("filename", "")).endswith((".mp4", ".webm")):
                                vids.append(im)
                        for v in nd.get("videos", []) or []:
                            vids.append(v)
                    if vids:
                        saved = []
                        for v in vids:
                            dst, data = download_view(v, VID_OUT)
                            saved.append(os.path.basename(dst))
                        _set_job(job_id, status="done", images=saved,
                                 elapsed=int(time.time()-t0))
                        return
                for m in stt.get("messages", []):
                    if m[0] == "execution_error":
                        _set_job(job_id, status="error", error=json.dumps(m[1], ensure_ascii=False)[:3000],
                                 elapsed=int(time.time()-t0)); return
            _set_job(job_id, elapsed=int(time.time()-t0))
        _set_job(job_id, status="error", error="超时(>90min)", elapsed=int(time.time()-t0))
    except Exception as e:
        _set_job(job_id, status="error", error=repr(e)[:3000], elapsed=int(time.time()-t0))


def comfy_stats():
    try:
        st = http_json(f"{COMFY}/system_stats", timeout=8)
        q = http_json(f"{COMFY}/queue", timeout=8)
        dev = (st.get("devices") or [{}])[0]
        return {"online": True, "gpu_name": dev.get("name", "?"),
                "vram_total_gb": round(dev.get("vram_total", 0) / 2**30, 1),
                "vram_free_gb": round(dev.get("vram_free", 0) / 2**30, 1),
                "queue_running": len(q.get("queue_running", [])),
                "queue_pending": len(q.get("queue_pending", []))}
    except Exception as e:
        return {"online": False, "error": str(e)}


def public_job(jid, j):
    return {"id": jid, "status": j.get("status"), "elapsed": j.get("elapsed", 0),
            "images": j.get("images", []), "error": (j.get("error") or "")[:3000],
            "params": j.get("params", {}), "created": j.get("created", 0)}


# ============ HTTP ============
class Handler(BaseHTTPRequestHandler):
    def log_message(self, *a):
        pass

    def _send(self, code, obj, ctype="application/json"):
        data = obj if isinstance(obj, bytes) else json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", ctype + "; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _serve_file(self, fp, ctype):
        if not os.path.isfile(fp):
            return self._send(404, {"error": "no file"})
        with open(fp, "rb") as f:
            data = f.read()
        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def _parse_multipart(self, body, boundary):
        """极简 multipart/form-data 解析：只取第一个文件字段。"""
        parts = body.split(b"--" + boundary.encode())
        for part in parts:
            if b'filename="' not in part:
                continue
            head, _, data = part.partition(b"\r\n\r\n")
            m = re.search(rb'filename="([^"]*)"', head)
            fname = m.group(1).decode("utf-8", "ignore") if m else "file"
            data = data.rstrip(b"\r\n")
            return fname, data
        return None, None

    def do_GET(self):
        path = urllib.parse.urlparse(self.path).path
        if path == "/":
            return self._serve_file(os.path.join(BASE_DIR, "index.html"), "text/html")
        if path == "/api/stats":
            return self._send(200, comfy_stats())
        if path == "/api/jobs":
            with JOBS_LOCK:
                jobs = [public_job(j, jj) for j, jj in sorted(
                    JOBS.items(), key=lambda x: x[1].get("created", 0), reverse=True)][:40]
            return self._send(200, {"jobs": jobs})
        if path.startswith("/img/"):
            return self._serve_file(os.path.join(IMG_OUT, os.path.basename(path[5:])),
                                    "image/png")
        if path.startswith("/vfile/"):
            return self._serve_file(os.path.join(VID_OUT, os.path.basename(path[7:])),
                                    "video/mp4")
        if path.startswith("/thumb/"):
            # 历史图片预览
            return self._serve_file(os.path.join(IMG_OUT, os.path.basename(path[7:])),
                                    "image/png")
        return self._send(404, {"error": "not found"})

    def do_POST(self):
        path = urllib.parse.urlparse(self.path).path
        ln = int(self.headers.get("Content-Length", 0))
        body = self.rfile.read(ln)

        if path == "/api/generate":  # 文生图
            try:
                p = json.loads(body.decode())
            except Exception:
                return self._send(400, {"error": "bad json"})
            with JOBS_LOCK:
                JOB_SEQ[0] += 1
                jid = f"img{int(time.time())}_{JOB_SEQ[0]}"
                JOBS[jid] = {"status": "queued", "created": int(time.time()), "elapsed": 0}
            threading.Thread(target=run_img_job, args=(jid, p), daemon=True).start()
            return self._send(200, {"job_id": jid})

        if path == "/api/video":  # H3 生视频
            try:
                p = json.loads(body.decode())
            except Exception:
                return self._send(400, {"error": "bad json"})
            with JOBS_LOCK:
                JOB_SEQ[0] += 1
                jid = f"vid{int(time.time())}_{JOB_SEQ[0]}"
                JOBS[jid] = {"status": "queued", "created": int(time.time()), "elapsed": 0}
            threading.Thread(target=run_video_job, args=(jid, p), daemon=True).start()
            return self._send(200, {"job_id": jid})

        if path == "/api/upload":  # 文件上传 → ComfyUI input
            ct = self.headers.get("Content-Type", "")
            boundary = ct.split("boundary=")[-1].strip() if "boundary=" in ct else ""
            fname, data = self._parse_multipart(body, boundary) if boundary else (None, None)
            if fname is None or not data:
                return self._send(400, {"error": "no file"})
            safe = re.sub(r"[^\w.\-]", "_", os.path.basename(fname))
            tmp = os.path.join(UPLOAD_DIR, f"{int(time.time())}_{safe}")
            with open(tmp, "wb") as f:
                f.write(data)
            try:
                remote = http_upload(tmp, f"gui_{int(time.time())}_{safe}")
            except Exception as e:
                return self._send(502, {"error": f"上传 ComfyUI 失败: {e}"})
            try:
                os.remove(tmp)
            except Exception:
                pass
            return self._send(200, {"remote": remote, "name": remote})

        if path == "/api/open_folder":
            try:
                p = json.loads(body.decode())
                key = p.get("dir", "")
            except Exception:
                key = ""
            target = {"video": VID_OUT, "img": IMG_OUT}.get(key, VID_OUT)
            try:
                os.startfile(os.path.realpath(target))  # Windows 打开资源管理器
                return self._send(200, {"ok": True, "dir": target})
            except Exception as e:
                return self._send(500, {"error": str(e)})

        return self._send(404, {"error": "not found"})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8099)
    ap.add_argument("--host", default="127.0.0.1")
    a = ap.parse_args()
    print(f"[gui] http://{a.host}:{a.port}")
    print(f"      img_out={IMG_OUT}\n      vid_out={VID_OUT}")
    ThreadingHTTPServer((a.host, a.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
