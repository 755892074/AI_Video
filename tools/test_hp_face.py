#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""单镜实验：把真实小孩照片放到 ref_image_0（第一参考位），测试 H3 是否以其脸为主体生成。"""
import json, os, sys, time, uuid, urllib.request, urllib.error, urllib.parse, subprocess
import imageio_ffmpeg
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import batch_r2v as B

COMFY = B.COMFY
ROOT = B.ROOT
FFMPEG = B.FFMPEG
WF = os.path.join(ROOT, "shots", "ep01", "workflows", "r2v_api.json")

def main():
    B.CLIENT = uuid.uuid4().hex
    wf = B.load_json(WF)["prompt"]

    # 上传三张图：照片放 ch 位、分镜放 sb 位、场景放 sc 位
    u_photo = B.upload_image("hp/assets/characters/harry_original.jpg", "exp_hp_photo.png")
    u_sb    = B.upload_image("hp/assets/storyboards/storyboard_01.png", "exp_hp_sb.png")
    u_sc    = B.upload_image("hp/assets/scenes/scene_castle.png", "exp_hp_sc.png")
    print("uploaded:", u_photo, u_sb, u_sc)

    # 关键：照片 -> 137 (ref_image_0, 第一参考=身份主体)；分镜 -> 139 (ref_image_1, 构图)
    p = json.loads(json.dumps(wf))
    p["137"]["inputs"]["image"] = u_photo      # ref_image_0 = 真实照片
    p["139"]["inputs"]["image"] = u_sb         # ref_image_1 = 分镜(构图)
    p["900"] = {"class_type": "LoadImage", "inputs": {"image": u_sc}}  # ref_image_2 = 场景
    p["136"]["inputs"]["ref_images.ref_image_2"] = ["900", 0]
    p["138"]["inputs"]["value"] = ("电影感镜头缓慢推近：戴圆框眼镜的小男孩，穿着格兰芬多红金长袍，"
                                   "在卧室窗边伸手接住白猫头鹰丢下的信封，暖色灯光柔和，温馨奇幻氛围")

    pid = B.submit(p)
    print("SUBMIT pid:", pid)
    if not pid:
        return

    # 轮询
    out = os.path.join(ROOT, "shots", "hp", "output", "_exp_shot01.mp4")
    for _ in range(720):
        try:
            h = json.loads(urllib.request.urlopen(f"{COMFY}/history/{pid}", timeout=30).read())
        except Exception:
            h = {}
        if pid not in h:
            time.sleep(5); continue
        res = h[pid]
        st = res.get("status", {})
        if st.get("status_str") == "error":
            print("ERROR:", json.dumps(res.get("messages", []), ensure_ascii=False)[:300]); return
        vid = B.find_video_output(res.get("outputs", {}))
        if vid:
            ok, sz = B.download_video(vid, out)
            print("DOWNLOADED", out, sz, "mp4=", ok)
            # 抽首帧
            fr = os.path.join(ROOT, "shots", "hp", "output", "_exp_frame01.png")
            subprocess.run([FFMPEG, "-y", "-i", out, "-vframes", "1", "-ss", "0", fr],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print("FRAME ->", fr, os.path.getsize(fr) if os.path.exists(fr) else 0)
            return
        time.sleep(5)
    print("TIMEOUT")

if __name__ == "__main__":
    main()
