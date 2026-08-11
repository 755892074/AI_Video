#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HP 人脸实验 v2：照片=ref_image_0（第一参考），分镜=ref_image_1。
   修复：print flush + 视频检测（animated 在节点级）"""
import json, os, sys, time, uuid, urllib.request, urllib.error, urllib.parse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_r2v as B

COMFY = B.COMFY
ROOT = B.ROOT
FFMPEG = B.FFMPEG
WF = os.path.join(ROOT, "shots", "ep01", "workflows", "r2v_api.json")

def log(*a):
    msg = " ".join(str(x) for x in a)
    print(msg, flush=True)

def find_video_fixed(outputs):
    """修复版：H3 SaveVideo 输出在 node 92 的 images[0] 里，
       animated 标记在节点级（o["animated"]），不在 image 内部。"""
    for nid, o in outputs.items():
        if not isinstance(o, dict):
            continue
        if o.get("videos"):
            return o["videos"][0]
        # H3 SaveVideo: images=[{filename,subfolder,type}], animated=[True] at node level
        if o.get("images") and isinstance(o["images"], list):
            im = o["images"][0] if o["images"] else {}
            if im.get("filename") and o.get("animated") == [True]:
                return im
        # fallback: any mp4 filename
        if o.get("images") and isinstance(o["images"], list):
            for im in o["images"]:
                fn = im.get("filename","")
                if fn.endswith(".mp4"):
                    return im
    return None

def main():
    B.CLIENT = uuid.uuid4().hex
    wf = B.load_json(WF)["prompt"]

    log("[1/5] uploading ...")
    u_photo = B.upload_image("hp/assets/characters/harry_original.jpg", "v2_photo")
    u_sb    = B.upload_image("hp/assets/storyboards/storyboard_01.png", "v2_sb")
    u_sc    = B.upload_image("hp/assets/scenes/scene_castle.png", "v2_sc")
    log(f"  photo={u_photo} sb={u_sb} sc={u_sc}")

    log("[2/5] building prompt (photo=ref_image_0)...")
    p = json.loads(json.dumps(wf))
    p["137"]["inputs"]["image"] = u_photo      # ref_image_0 = 真实照片（身份主体）
    p["139"]["inputs"]["image"] = u_sb         # ref_image_1 = 分镜（构图）
    p["900"] = {"class_type": "LoadImage", "inputs": {"image": u_sc}}
    p["136"]["inputs"]["ref_images.ref_image_2"] = ["900", 0]
    p["138"]["inputs"]["value"] = (
        "电影感镜头缓慢推近：戴圆框眼镜的小男孩穿着格兰芬多红金长袍，"
        "在卧室窗边伸手接住白猫头鹰丢下的信封，暖色灯光柔和，温馨奇幻氛围"
    )

    log("[3/5] submitting ...")
    pid = B.submit(p)
    log(f"  pid={pid}")
    if not pid:
        log("SUBMIT FAILED"); return

    log("[4/5] waiting for generation ...")
    out_mp4 = os.path.join(ROOT, "shots", "hp", "output", "_v2_shot01.mp4")
    for i in range(720):
        try:
            h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30).read())
        except Exception:
            h = {}
        if pid not in h:
            if i % 12 == 0: log(f"  waiting... ({i*5}s)")
            time.sleep(5); continue
        res = h[pid]
        st = res.get("status", {})
        if st.get("status_str") == "error":
            log("ERROR:", json.dumps(res.get("messages",[]), ensure_ascii=False)[:300]); return
        vid = find_video_fixed(res.get("outputs", {}))
        if vid:
            ok, sz = B.download_video(vid, out_mp4)
            log(f"[done] {out_mp4} ({sz}B)")
            fr = os.path.join(ROOT, "shots", "hp", "output", "_v2_frame01.png")
            subprocess.run([FFMPEG, "-y", "-i", out_mp4, "-vframes", "1", "-ss", "0", fr],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            log(f"FRAME -> {fr} ({os.path.getsize(fr)}B)")
            return
        if i % 24 == 0:
            log(f"  still generating... ({i*5}s)")
        time.sleep(5)
    log("TIMEOUT after 60min")

if __name__ == "__main__":
    main()
