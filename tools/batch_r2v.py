#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量 R2V 生成器：读取 batch_manifest.json，对每套每镜
  上传 分镜图+角色表+场景图 -> 提交 H3 ReferenceToVideo -> 轮询 -> 下载 MP4
  同套镜头用 ffmpeg 拼接成 30-50s 成片。
支持断点续跑：已存在的输出 mp4 会跳过；prompt 状态存于 batch_state.json。
"""
import json, os, sys, time, uuid, urllib.request, urllib.error, subprocess, shutil
import imageio_ffmpeg

COMFY = "http://100.67.139.74:8188"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "shots", "batch_manifest.json")
STATE = os.path.join(ROOT, "shots", "batch_state.json")
LOG = os.path.join(ROOT, "shots", "batch_r2v.log")
TARGET_W, TARGET_H = 768, 512
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

# 节点 ID（来自 r2v_api.json）
H3, SB, CH, PROMPT = "136", "137", "139", "138"
SCENE_NODE = "900"
VIDEO_NODE = "140"

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(time.strftime("[%H:%M:%S] ") + msg + "\n")

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def http_post(url, data: bytes, headers):
    req = urllib.request.Request(url, data=data, method="POST")
    for k, v in headers.items():
        req.add_header(k, v)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read().decode()

def http_get(url, timeout=60):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode()

def upload_video(rel_path, unique_name):
    abs_path = os.path.join(ROOT, "shots", rel_path)
    with open(abs_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(abs_path)[1].lower() or ".mp4"
    unique_name = os.path.splitext(unique_name)[0] + ext
    boundary = "----workbuddyboundary"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{unique_name}"\r\n'.encode()
    body += b"Content-Type: video/mp4\r\n\r\n"
    body += data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    hdr = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    try:
        resp = http_post(f"{COMFY}/upload/image", body, hdr)
        return json.loads(resp)["name"]
    except urllib.error.HTTPError as e:
        log("UPLOAD FAIL", unique_name, e.code, e.read().decode()[:200])
        raise

def upload_image(rel_path, unique_name):
    abs_path = os.path.join(ROOT, "shots", rel_path)
    with open(abs_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(abs_path)[1].lower() or ".png"
    unique_name = os.path.splitext(unique_name)[0] + ext
    boundary = "----workbuddyboundary"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{unique_name}"\r\n'.encode()
    body += b"Content-Type: image/png\r\n\r\n"
    body += data
    body += b"\r\n"
    body += f"--{boundary}--\r\n".encode()
    hdr = {"Content-Type": f"multipart/form-data; boundary={boundary}"}
    try:
        resp = http_post(f"{COMFY}/upload/image", body, hdr)
        return json.loads(resp)["name"]
    except urllib.error.HTTPError as e:
        log("UPLOAD FAIL", unique_name, e.code, e.read().decode()[:200])
        raise

def extract_video_frame(video_rel_path, output_rel_path):
    """用 ffmpeg 提取视频第一帧作为参考图"""
    abs_video = os.path.join(ROOT, "shots", video_rel_path)
    abs_output = os.path.join(ROOT, "shots", output_rel_path)
    os.makedirs(os.path.dirname(abs_output), exist_ok=True)
    cmd = [FFMPEG, "-y", "-i", abs_video, "-ss", "00:00:00", "-vframes", "1", "-q:v", "2", abs_output]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return output_rel_path

def assemble_ref2va_prompt(ref2va):
    """把结构化的 ref2va 字典拼成 H3 ReferenceToVideo 的六段提示词。
    顺序严格遵循 MiniMax 官方 h3-prompt-writing：
    subject_definitions -> summary -> retention_analysis ->
    detailed_description -> overall_soundscape -> non_diegetic_music
    ref2va 各字段可为字符串或列表（列表按行拼接）。
    可选字段：
      camera —— 电影摄影语言（镜头距离/运动/景深/光线），拼到 detailed_description
                开头，用于打破"AI 平铺感"、制造镜头层次与差异化。
    """
    def _blk(v):
        if isinstance(v, list):
            return "\n".join(str(x) for x in v)
        return str(v)
    # 电影摄影语言：拼到 detailed_description 最前面（如有）
    camera = _blk(ref2va.get("camera", "")).strip()
    dd = _blk(ref2va.get("detailed_description", "")).rstrip()
    if camera:
        dd = camera + "\n" + dd
    # 强制语言锁（用户硬性要求：中文对白+中文画面文字，禁英文/其他语言）
    if "中文" not in dd:
        dd += "\n所有对白与画面文字用中文，禁止英文或其他语言字幕。"
    sections = [
        ("subject_definitions", ref2va.get("subject_definitions", "")),
        ("summary", ref2va.get("summary", "")),
        ("retention_analysis", ref2va.get("retention_analysis", "")),
        ("detailed_description", dd),
        ("overall_soundscape", ref2va.get("overall_soundscape", "")),
        ("non_diegetic_music", ref2va.get("non_diegetic_music", "")),
    ]
    parts = []
    for name, val in sections:
        b = _blk(val).rstrip()
        if b:
            parts.append(f"{name}:\n{b}")
    return "\n\n".join(parts)

def build_prompt(wf, sb_name, ch_name, sc_name, prompt_text, ref2va=None, ref_video_name=None):
    # 若提供结构化 ref2va（官方六段），优先用它组装提示词
    if ref2va:
        prompt_text = assemble_ref2va_prompt(ref2va)
    p = json.loads(json.dumps(wf))  # deep copy
    p[SB]["inputs"]["image"] = sb_name
    p[CH]["inputs"]["image"] = ch_name
    p[SCENE_NODE] = {"class_type": "LoadImage", "inputs": {"image": sc_name}}
    p[H3]["inputs"]["ref_images.ref_image_2"] = [SCENE_NODE, 0]
    p[PROMPT]["inputs"]["value"] = prompt_text
    # 如果有参考视频，上传并接到 LoadVideo 节点(140)，经 GetVideoComponents 拆帧后
    # 由 H3 的 ref_videos.ref_video_0 作为动作参考（帧序列），音轨接 ref_video_audio_0
    if ref_video_name:
        p[VIDEO_NODE]["inputs"]["file"] = ref_video_name
    return p

def submit(prompt_graph):
    payload = json.dumps({"prompt": prompt_graph, "client_id": CLIENT}).encode()
    try:
        resp = http_post(f"{COMFY}/prompt", payload,
                         {"Content-Type": "application/json"})
        return json.loads(resp).get("prompt_id")
    except urllib.error.HTTPError as e:
        log("SUBMIT FAIL", e.code, e.read().decode()[:400])
        return None

def find_video_output(outputs):
    for nid, o in outputs.items():
        if not isinstance(o, dict):
            continue
        if o.get("videos"):
            return o["videos"][0]
        # H3 SaveVideo: images=[{filename,...}], animated=[True] 在节点级
        if o.get("images") and isinstance(o["images"], list) and o["images"]:
            im = o["images"][0]
            if im.get("filename") and (o.get("animated") == [True] or im.get("animated")):
                return im
            # fallback: 任何 mp4 文件名
            if im.get("filename","").endswith(".mp4"):
                return im
    return None

def download_video(vid_meta, out_path):
    params = urllib.parse.urlencode({
        "filename": vid_meta["filename"],
        "subfolder": vid_meta.get("subfolder", ""),
        "type": vid_meta.get("type", "output"),
    })
    data = urllib.request.urlopen(f"{COMFY}/view?{params}", timeout=300).read()
    with open(out_path, "wb") as f:
        f.write(data)
    ok = b"ftyp" in data[:32]
    return ok, len(data)

import urllib.parse

def shot_key(sid, shot):
    return f"{sid}_{shot:02d}"

def main():
    global CLIENT, MANIFEST, STATE, LOG
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", default=MANIFEST)
    ap.add_argument("--state", default=STATE)
    ap.add_argument("--log", default=LOG)
    args = ap.parse_args()
    MANIFEST = args.manifest
    STATE = args.state
    LOG = args.log
    CLIENT = uuid.uuid4().hex
    man = load_json(MANIFEST)
    state = load_json(STATE) if os.path.exists(STATE) else {}
    wf = load_json(os.path.join(ROOT, man["workflow"]))["prompt"]

    # 收集所有待跑镜头
    plan = []  # (sid, shot, rel_sb, rel_ch, rel_sc, prompt, out_path)
    for s in man["sets"]:
        sid = s["id"]
        out_dir = os.path.join(ROOT, "shots", sid, "output")
        os.makedirs(out_dir, exist_ok=True)
        for sh in s["shots"]:
            out_path = os.path.join(out_dir, f"shot{sh['shot']:02d}.mp4")
            plan.append((sid, sh["shot"], sh["storyboard"], sh["character"],
                         sh["scene"], sh.get("prompt", ""), sh.get("ref2va"), sh.get("ref_video"), out_path))

    log(f"计划镜头数={len(plan)}，开始处理")

    # 1) 提交阶段（跳过已存在 & 已提交且未完成）
    pending = {}  # key -> prompt_id
    for sid, shot, rel_sb, rel_ch, rel_sc, prompt, ref2va, ref_video, out_path in plan:
        key = shot_key(sid, shot)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            log(f"[skip] {key} 已有输出")
            continue
        if key in state and state[key].get("prompt_id") and not state[key].get("done"):
            pending[key] = state[key]["prompt_id"]
            log(f"[queued-resume] {key} pid={pending[key]}")
            continue
        # 上传三张图（带唯一名，避免跨套同名冲突；返回值含真实扩展名）
        u_sb = upload_image(rel_sb, f"batch_{sid}_{shot:02d}_sb.png")
        u_ch = upload_image(rel_ch, f"batch_{sid}_{shot:02d}_ch.png")
        u_sc = upload_image(rel_sc, f"batch_{sid}_{shot:02d}_sc.png")
        # 如果有视频参考，上传到台式机并接入 ref_videos（帧序列动作参考）
        u_video = None
        if ref_video:
            u_video = upload_video(ref_video, f"batch_{sid}_{shot:02d}_ref.mp4")
        pg = build_prompt(wf, u_sb, u_ch, u_sc, prompt, ref2va, u_video)
        pid = submit(pg)
        if not pid:
            log(f"[ERROR] {key} 提交失败，跳过")
            continue
        state[key] = {"prompt_id": pid, "done": False, "out": out_path}
        pending[key] = pid
        log(f"[submit] {key} pid={pid}")

    save_state(state)

    # 2) 轮询下载
    for key, pid in list(pending.items()):
        out_path = state[key]["out"]
        done = False
        for _ in range(720):  # 最多 720*5s = 60min/镜头
            try:
                h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30).read())
            except Exception:
                h = {}
            if pid not in h:
                time.sleep(5); continue
            res = h[pid]
            st = res.get("status", {})
            if st.get("status_str") == "error":
                log(f"[ERROR] {key} 生成失败: {json.dumps(res.get('messages', []), ensure_ascii=False)[:300]}")
                done = True  # 标记处理过，避免反复
                break
            outs = res.get("outputs", {})
            vid = find_video_output(outs)
            if vid:
                ok, sz = download_video(vid, out_path)
                log(f"[done] {key} -> {out_path} ({sz}B, mp4={ok})")
                state[key]["done"] = True
                done = True
                break
            time.sleep(5)
        if not done:
            log(f"[TIMEOUT] {key} 超时未出，留待下次续跑")
        save_state(state)

    # 3) 每套拼接
    for s in man["sets"]:
        sid = s["id"]
        clips = []
        for sh in s["shots"]:
            p = os.path.join(ROOT, "shots", sid, "output", f"shot{sh['shot']:02d}.mp4")
            if os.path.exists(p) and os.path.getsize(p) > 5000:
                clips.append(p)
        if len(clips) < 2:
            log(f"[concat] {sid} 镜头不足({len(clips)})，跳过拼接")
            continue
        # 先归一化每个片段到统一分辨率/帧率
        tmp_dir = os.path.join(ROOT, "shots", sid, "output", "_norm")
        os.makedirs(tmp_dir, exist_ok=True)
        normed = []
        for i, c in enumerate(clips):
            t = os.path.join(tmp_dir, f"n{i}.mp4")
            cmd = [FFMPEG, "-y", "-i", c, "-vf",
                   f"scale={TARGET_W}:{TARGET_H}:force_original_aspect_ratio=decrease,pad={TARGET_W}:{TARGET_H}:(ow-iw)/2:(oh-ih)/2",
                   "-r", "24", "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "44100", "-b:a", "128k", t]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            normed.append(t)
        final = os.path.join(ROOT, "shots", sid, "output", f"{sid}_final.mp4")
        # ffmpeg concat demuxer
        list_txt = os.path.join(tmp_dir, "list.txt")
        with open(list_txt, "w", encoding="utf-8") as f:
            for t in normed:
                f.write(f"file '{t}'\n")
        cmd = [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", list_txt,
               "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24", "-c:a", "aac", final]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode == 0 and os.path.getsize(final) > 5000:
            log(f"[FINAL] {sid} 成片 -> {final} ({os.path.getsize(final)}B)")
        else:
            log(f"[concat FAIL] {sid}")

    log("全部完成。")

def save_state(state):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
