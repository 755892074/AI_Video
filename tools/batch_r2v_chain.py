#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量 R2V 生成器：读取 batch_manifest.json，对每套每镜
  上传 分镜图+角色表+场景图 -> 提交 H3 ReferenceToVideo -> 轮询 -> 下载 MP4
  同套镜头用 ffmpeg 拼接成 30-50s 成片。
支持断点续跑：已存在的输出 mp4 会跳过；prompt 状态存于 batch_state.json。
"""
import json, os, sys, time, uuid, urllib.request, urllib.error, subprocess, shutil, threading
import imageio_ffmpeg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import comfy_monitor as cm

COMFY = "http://100.67.139.74:8188"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "shots", "batch_manifest.json")
STATE = os.path.join(ROOT, "shots", "batch_state.json")
LOG = os.path.join(ROOT, "shots", "batch_r2v.log")
TARGET_W, TARGET_H = 768, 512  # 兜底：manifest 未配 target 且探测失败时用
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def detect_size(path):
    """探测视频原生分辨率 (w,h)。失败返回 (None, None)。"""
    try:
        r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True, timeout=30)
        import re
        m = re.search(r"Video:.*?(\d{3,5})x(\d{3,5})", r.stderr)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return None, None

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

def upload_audio(rel_path, unique_name):
    """上传音频/对白文件到 ComfyUI input 目录（供 LoadAudio 使用）"""
    abs_path = os.path.join(ROOT, "shots", rel_path)
    with open(abs_path, "rb") as f:
        data = f.read()
    ext = os.path.splitext(abs_path)[1].lower() or ".mp3"
    unique_name = os.path.splitext(unique_name)[0] + ext
    boundary = "----workbuddyboundary"
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{unique_name}"\r\n'.encode()
    body += b"Content-Type: audio/mpeg\r\n\r\n"
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

def assemble_ref2va_prompt(ref2va, has_ref_video=False):
    """把结构化的 ref2va 字典拼成 H3 ReferenceToVideo 的六段提示词。
    顺序严格遵循 MiniMax 官方 h3-prompt-writing：
    subject_definitions -> summary -> retention_analysis ->
    detailed_description -> overall_soundscape -> non_diegetic_music
    ref2va 各字段可为字符串或列表（列表按行拼接）。
    可选字段：
      camera —— 电影摄影语言（镜头距离/运动/景深/光线），拼到 detailed_description
                开头，用于打破"AI 平铺感"、制造镜头层次与差异化。
      ref_video —— 若提供了参考视频（has_ref_video=True），按官方格式用 <Video 1>
                标签在 subject_definitions 和 retention_analysis 中显式引用并分配
                "动作/运动来自 <Video 1>" 任务。官方指南：显式分配效果远好于不提。
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

    # 视频参考：不再自动追加任何内容（按官方规范，动作必须内嵌到
    # <Subject N> 定义里写"动作来自 <Video 1>"，而 <Video N> 不能单独
    # 定义为主体）。manifest 里已经按官方写法组织，代码层不再插手。
    sd = _blk(ref2va.get("subject_definitions", "")).rstrip()
    ra = _blk(ref2va.get("retention_analysis", "")).rstrip()

    sections = [
        ("subject_definitions", sd),
        ("summary", ref2va.get("summary", "")),
        ("retention_analysis", ra),
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

VIDEO_NODE = "140"
# H3 节点最多支持 3 路参考视频：节点 ID 配对 (LoadVideo, GetVideoComponents)
VIDEO_SLOTS = [("140", "141"), ("143", "144"), ("146", "147")]


def build_prompt(wf, sb_name, ch_name, sc_name, prompt_text, ref2va=None, ref_videos_names=None,
                 ref_video_name=None,  # 兼容旧签名
                 extra_images=None, megapixels=None, seconds=None, audio_name=None, aspect_ratio=None):
    """ref_videos_names: list，已上传到 ComfyUI 的视频文件名（最多 3 路）。
       第 1 路接 LoadVideo 140/GetVideoComponents 141；第 2/3 路动态创建 143+144 / 146+147。
       H3 的 ref_videos.ref_video_0/1/2 接 GetVideoComponents 输出 0（frames），
       ref_video_audios.ref_video_audio_0/1/2 接输出 1（audio）。
       extra_images: list of 已上传文件名，依次接到 ref_images.ref_image_3..N
       ... 其他参数同注释
    """
    # 兼容旧 ref_video_name 单值
    if ref_videos_names is None and ref_video_name:
        ref_videos_names = [ref_video_name]
    ref_videos_names = list(ref_videos_names or [])[:3]
    # 若提供结构化 ref2va（官方六段），优先用它组装提示词
    if ref2va:
        prompt_text = assemble_ref2va_prompt(ref2va, has_ref_video=bool(ref_video_name))
    p = json.loads(json.dumps(wf))  # deep copy
    if seconds is not None:
        p["132"]["inputs"]["value"] = seconds
    if sb_name:
        p[SB]["inputs"]["image"] = sb_name
    else:
        # 无分镜参考图：移除 LoadImage(137) 并断开 ref_image_0
        p.pop(SB, None)
        p[H3]["inputs"].pop("ref_images.ref_image_0", None)
    if ch_name:
        p[CH]["inputs"]["image"] = ch_name
    else:
        # 无角色参考图：移除 LoadImage(139) 并断开 ref_image_1
        p.pop(CH, None)
        p[H3]["inputs"].pop("ref_images.ref_image_1", None)
    if sc_name:
        p[SCENE_NODE] = {"class_type": "LoadImage", "inputs": {"image": sc_name}}
        p[H3]["inputs"]["ref_images.ref_image_2"] = [SCENE_NODE, 0]
    else:
        # 无第三张参考图：断开 ref_image_2，避免 LoadImage 加载空文件
        p.pop(SCENE_NODE, None)
        p[H3]["inputs"].pop("ref_images.ref_image_2", None)
    p[PROMPT]["inputs"]["value"] = prompt_text
    
    # 修改分辨率（如果指定了 megapixels 或 aspect_ratio）
    if megapixels is not None or aspect_ratio is not None:
        for nid, node in p.items():
            if isinstance(node, dict) and node.get("class_type") == "ResolutionSelector":
                if megapixels is not None:
                    node["inputs"]["megapixels"] = megapixels
                if aspect_ratio is not None:
                    node["inputs"]["aspect_ratio"] = aspect_ratio
                break
    
    # 参考视频：第 k 路用 VIDEO_SLOTS[k] 节点对；H3 ref_video_k 接 GetVideoComponents 输出 0，
    # ref_video_audio_k 接输出 1（audio）。无视频时全部 pop 防默认文件加载失败。
    if ref_videos_names:
        for k, vname in enumerate(ref_videos_names):
            load_id, gc_id = VIDEO_SLOTS[k]
            p[load_id] = {"class_type": "LoadVideo", "inputs": {"file": vname}}
            p[gc_id] = {"class_type": "GetVideoComponents", "inputs": {"video": [load_id, 0]}}
            p[H3]["inputs"][f"ref_videos.ref_video_{k}"] = [gc_id, 0]
            p[H3]["inputs"][f"ref_video_audios.ref_video_audio_{k}"] = [gc_id, 1]
        # 清理未使用的视频槽（防止旧 default 文件导致提交失败）
        for k in range(len(ref_videos_names), 3):
            load_id, gc_id = VIDEO_SLOTS[k]
            p.pop(load_id, None)
            p.pop(gc_id, None)
            p[H3]["inputs"].pop(f"ref_videos.ref_video_{k}", None)
            p[H3]["inputs"].pop(f"ref_video_audios.ref_video_audio_{k}", None)
    else:
        for load_id, gc_id in VIDEO_SLOTS:
            p.pop(load_id, None)
            p.pop(gc_id, None)
        for k in range(3):
            p[H3]["inputs"].pop(f"ref_videos.ref_video_{k}", None)
            p[H3]["inputs"].pop(f"ref_video_audios.ref_video_audio_{k}", None)
    # 多图参考：动态创建 LoadImage 节点（901 起），接到 ref_images.ref_image_3..N
    if extra_images:
        for i, img_name in enumerate(extra_images):
            nid = str(901 + i)
            p[nid] = {"class_type": "LoadImage", "inputs": {"image": img_name}}
            p[H3]["inputs"][f"ref_images.ref_image_{3 + i}"] = [nid, 0]
    # 对白/语音参考：创建 LoadAudio(142) 接到 H3 的 ref_audios.ref_audio_0
    if audio_name:
        p["142"] = {"class_type": "LoadAudio", "inputs": {"audio": audio_name}}
        p[H3]["inputs"]["ref_audios.ref_audio_0"] = ["142", 0]
    else:
        p.pop("142", None)
        p[H3]["inputs"].pop("ref_audios.ref_audio_0", None)
    return p


def find_node(pg, class_type):
    for nid, nd in pg.items():
        if isinstance(nd, dict) and nd.get("class_type") == class_type:
            return nid
    return None

def apply_chain(pg, sid, i_in_set, ctx_prefix="h3_chain"):
    """把 pg 配置成链中第 i_in_set(0-based) 段：
       - 每段 latent 存到 h3_chain/<sid>/clip_NNNNN.safetensors（供下一段续接）
       - 首段无前驱：不走 MotionContext，回归原始 H3 链路
         (guider 直接吃 H3、CreateVideo 直接吃 decode)，SaveLatent 仍存盘 clip1
       - 第 2 段起：guider 走 MotionContext、CreateVideo 走 Trim，
         MotionContext 用 LoadLatent 续上一段的 latent（画面+音频尾一起钉）
       返回是否启用 chain（找不到 MotionContext 节点则退化成普通 ref2va）"""
    mc = find_node(pg, "MiniMaxH3MotionContext")
    if mc is None:
        return False
    load = find_node(pg, "MiniMaxH3MotionContextLoadLatent")
    save = find_node(pg, "MiniMaxH3MotionContextSaveLatent")
    trimb = find_node(pg, "MiniMaxH3MotionContextTrim")
    # Save 前缀必须含一个按 set 隔离的子目录名(作文件名 stem)，
    # 这样 Load 才能把 dirname 当成真实目录去读 *_NNNNN.safetensors。
    #   存: h3_chain/<sid>/clip  -> h3_chain/<sid>/clip_0000N.safetensors
    #   读: h3_chain/<sid>        -> 该目录里 *_0000(N-1).safetensors
    dirname = "%s/%s" % (ctx_prefix, sid)
    save_prefix = "%s/clip" % dirname
    idx = i_in_set + 1  # 1-based 段号（clip 1,2,3...）
    if save:
        pg[save]["inputs"]["filename_prefix"] = save_prefix
        pg[save]["inputs"]["clip_index"] = idx
    if load:
        pg[load]["inputs"]["latent_path"] = dirname
        pg[load]["inputs"]["clip_index"] = idx - 1 if idx > 1 else 0
    # 原始（无 MotionContext）接线
    ORIG_GUIDER = ["136", 0]
    ORIG_CV_IMG = ["122", 0]
    ORIG_CV_AUD = ["121", 0]
    if idx == 1:
        # 首段：断开 MotionContext 路径，回归原始 H3 链路；SaveLatent 仍存盘
        pg[mc]["inputs"].pop("context_latent", None)
        pg[mc]["inputs"].pop("context_frames", None)
        pg["126"]["inputs"]["conditioning"] = ORIG_GUIDER
        pg["130"]["inputs"]["images"] = ORIG_CV_IMG
        pg["130"]["inputs"]["audio"] = ORIG_CV_AUD
    else:
        if load:
            pg[mc]["inputs"].pop("context_frames", None)
            pg[mc]["inputs"]["context_latent"] = [load, 0]
        pg["126"]["inputs"]["conditioning"] = [mc, 0]
        if trimb:
            pg["130"]["inputs"]["images"] = [trimb, 0]
            pg["130"]["inputs"]["audio"] = [trimb, 1]
    return True

def apply_nochain(pg):
    """--no-chain: 恢复原始 H3 链路，断开 MotionContext。
    模板默认接线是 chain 版（126 guider 吃 200 MotionContext，130 吃 210 Trim，
    201/211 残留 __SID__ 占位符），不处理直接提交必失败。此函数把每镜都改成
    首段接线：126 conditioning -> 136，130 images/audio -> 122/121，
    并断开 mc 的 context_latent/context_frames（201/210/211 随之不被执行）。"""
    mc = find_node(pg, "MiniMaxH3MotionContext")
    if mc is not None:
        pg[mc]["inputs"].pop("context_latent", None)
        pg[mc]["inputs"].pop("context_frames", None)
    pg["126"]["inputs"]["conditioning"] = ["136", 0]
    pg["130"]["inputs"]["images"] = ["122", 0]
    pg["130"]["inputs"]["audio"] = ["121", 0]

def submit(prompt_graph):
    """提交任务 + 队列验证。返回 prompt_id；失败抛异常（快速失败，立即退出）。"""
    return cm.submit_with_verify(prompt_graph, CLIENT, comfy=COMFY)

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
    ap.add_argument("--no-chain", action="store_true", help="关闭链式接力(退化成普通ref2va)")
    ap.add_argument("--notify-wechat", action="store_true", help="全部渲染+拼接完成后推送到微信(文本摘要+成片)")
    ap.add_argument("--workflow", default=None, help="覆盖 manifest 里的 workflow 路径")
    args = ap.parse_args()
    MANIFEST = args.manifest
    STATE = args.state
    LOG = args.log
    CHAIN = not args.no_chain
    CLIENT = uuid.uuid4().hex
    man = load_json(MANIFEST)
    state = load_json(STATE) if os.path.exists(STATE) else {}
    wf_path = args.workflow or man.get("workflow")
    wf = load_json(os.path.join(ROOT, wf_path))["prompt"]

    # 收集所有待跑镜头
    plan = []  # (sid, shot, rel_sb, rel_ch, rel_sc, prompt, ref2va, ref_videos, extra_images, megapixels, seconds, audio, aspect, out_path)
    for s in man["sets"]:
        sid = s["id"]
        out_dir = os.path.join(ROOT, "shots", sid, "output")
        os.makedirs(out_dir, exist_ok=True)
        for i_in_set, sh in enumerate(s["shots"]):
            out_path = os.path.join(out_dir, f"shot{sh['shot']:02d}.mp4")
            # 兼容旧 manifest：ref_video 单值；新：ref_videos 列表（推荐）
            ref_videos = sh.get("ref_videos") or ([sh["ref_video"]] if sh.get("ref_video") else [])
            plan.append((sid, sh["shot"], sh["storyboard"], sh["character"],
                         sh["scene"], sh.get("prompt", ""), sh.get("ref2va"), ref_videos,
                         sh.get("extra_images", []), sh.get("megapixels"), sh.get("seconds"), sh.get("audio"), sh.get("aspect_ratio"), out_path, i_in_set))

    log(f"计划镜头数={len(plan)}，开始处理")

    # 0) 提交前健康检查：ComfyUI 不在线直接快速失败
    try:
        info = cm.health_check(comfy=COMFY)
        log(f"[health] ComfyUI 在线: GPU={info['gpu']}, VRAM={info['vram_gb']}GB")
    except Exception as e:
        log(f"[FATAL] {e}")
        sys.exit(1)

    # WS 实时监听：中途失败事件立刻记录并让主循环感知
    ws_error = {"msg": None}
    def _on_ws_err(msg):
        ws_error["msg"] = msg
        log(f"[WS-ERROR] {msg}")
    def _on_ws_evt(evt, data):
        if evt == "execution_start":
            log(f"[ws] 任务开始执行")
    ws_thread = threading.Thread(target=cm.ws_watch,
                                 args=(CLIENT, _on_ws_evt, _on_ws_err),
                                 kwargs={"timeout_sec": 60 * 60}, daemon=True)
    ws_thread.start()

    # 1) 提交阶段（跳过已存在 & 已提交且未完成）
    pending = {}  # key -> prompt_id
    for sid, shot, rel_sb, rel_ch, rel_sc, prompt, ref2va, ref_videos, extra_images, megapixels, seconds, audio, aspect, out_path, i_in_set in plan:
        key = shot_key(sid, shot)
        if os.path.exists(out_path) and os.path.getsize(out_path) > 5000:
            log(f"[skip] {key} 已有输出")
            continue
        if key in state and state[key].get("prompt_id") and not state[key].get("done"):
            pending[key] = state[key]["prompt_id"]
            log(f"[queued-resume] {key} pid={pending[key]}")
            continue
        # 上传三张图（带唯一名，避免跨套同名冲突；返回值含真实扩展名）
        u_sb = upload_image(rel_sb, f"batch_{sid}_{shot:02d}_sb.png") if rel_sb else None
        u_ch = upload_image(rel_ch, f"batch_{sid}_{shot:02d}_ch.png") if rel_ch else None
        u_sc = upload_image(rel_sc, f"batch_{sid}_{shot:02d}_sc.png") if rel_sc else None
        # 多图参考：上传额外参考图（如多角度角色表），接 ref_images.ref_image_3..
        u_extra = []
        for i, rel_extra in enumerate(extra_images or []):
            u_extra.append(upload_image(rel_extra, f"batch_{sid}_{shot:02d}_x{i}.png"))
        # 视频参考：上传 ref_videos[0..2]（H3 节点最多 3 路），当前取 [0] 走原链路
        # TODO: 多路支持（ref_videos.ref_video_1/2 + LoadVideo 143/146 + GetVideoComponents 144/147）
        u_videos = []
        for i, rel_video in enumerate((ref_videos or [])[:3]):
            if not rel_video: continue
            u_videos.append(upload_video(rel_video, f"batch_{sid}_{shot:02d}_ref{i}.mp4"))
        u_video = u_videos[0] if u_videos else None
        # 如果有对白/语音参考，上传并接入 ref_audios（LoadAudio 读取）
        u_audio = None
        if audio:
            u_audio = upload_audio(audio, f"batch_{sid}_{shot:02d}_aud")
        pg = build_prompt(wf, u_sb, u_ch, u_sc, prompt, ref2va,
                          ref_videos_names=u_videos,
                          extra_images=u_extra or None,
                          megapixels=megapixels, seconds=seconds,
                          audio_name=u_audio, aspect_ratio=aspect)
        if CHAIN:
            chained = apply_chain(pg, sid, i_in_set)
            if chained:
                log(f"[chain] {key} 段#{i_in_set+1} context={"无(首段)" if i_in_set==0 else "续上一段"}")
        else:
            apply_nochain(pg)
            log(f"[nochain] {key} 独立镜头（断开 MotionContext）")
        try:
            pid = submit(pg)
        except Exception as e:
            import traceback
            log(f"[FATAL] {key} 提交失败: {e}")
            traceback.print_exc()
            sys.exit(1)
        if not pid:
            log(f"[FATAL] {key} 未拿到 prompt_id，立即退出")
            sys.exit(1)
        state[key] = {"prompt_id": pid, "done": False, "out": out_path}
        pending[key] = pid
        log(f"[submit] {key} pid={pid}")

    save_state(state)

    # 2) 轮询下载
    for key, pid in list(pending.items()):
        out_path = state[key]["out"]
        done = False
        for _ in range(720):  # 最多 720*5s = 60min/镜头
            if ws_error["msg"]:
                log(f"[FATAL] WS 检测到任务异常: {ws_error['msg']}")
                sys.exit(1)
            try:
                h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30).read())
            except Exception:
                h = {}
            if pid not in h:

                time.sleep(5); continue
            res = h[pid]
            st = res.get("status", {})
            if st.get("status_str") == "error":
                log(f"[FATAL] {key} 生成失败: {json.dumps(res.get('messages', []), ensure_ascii=False)[:300]}")
                sys.exit(1)
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
    finals = []
    for s in man["sets"]:
        sid = s["id"]
        # 拼接目标分辨率：优先 set 级 target_w/target_h；未配置则自动探测单镜原生分辨率
        # （防呆：H3 竖屏原生 768x1376 若用旧默认 768x512 会被压成横屏黑边小片）
        TW, TH = s.get("target_w"), s.get("target_h")
        if not TW or not TH:
            TW, TH = detect_size(os.path.join(ROOT, "shots", sid, "output", f"shot{s['shots'][0]['shot']:02d}.mp4"))
            if TW and TH:
                log(f"[concat] {sid} 未配置 target，自动探测单镜原生 {TW}x{TH}")
            else:
                TW, TH = TARGET_W, TARGET_H
                log(f"[concat] {sid} 探测失败，回落默认 {TW}x{TH}")
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
                   f"scale={TW}:{TH}:force_original_aspect_ratio=decrease,pad={TW}:{TH}:(ow-iw)/2:(oh-ih)/2",
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
            finals.append((sid, final))
        else:
            log(f"[concat FAIL] {sid}")

    # 4) 微信推送（可选）
    if args.notify_wechat and finals:
        try:
            sys.path.insert(0, os.path.join(ROOT, "tools"))
            import send_wechat as sw
            cfg = sw.load_cfg()
            if not cfg:
                log("[notify] 无法读取 ClawBot 配置，跳过微信推送")
            else:
                lines = ["🎬 渲染完成！"]
                for sid, fp in finals:
                    lines.append(f"· {sid}: {os.path.getsize(fp)//1024}KB")
                if sw.send_msg(cfg, "\n".join(lines)):
                    log("[notify] 微信文本推送 OK")
                else:
                    log("[notify] 微信文本推送失败")
                for sid, fp in finals:
                    if sw.send_file(cfg, fp):
                        log(f"[notify] 微信文件推送 OK: {os.path.basename(fp)}")
                    else:
                        log(f"[notify] 微信文件推送失败: {os.path.basename(fp)}")
        except Exception as e:
            log(f"[notify] 微信推送异常: {e}")

    log("全部完成。")

def save_state(state):
    with open(STATE, "w", encoding="utf-8") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
