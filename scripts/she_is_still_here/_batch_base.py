# -*- coding: utf-8 -*-
"""一次性顺序出《她还在》6 张关键基底/定妆图（写实 CG 电影感·冷调）"""
import sys, os, random
sys.path.insert(0, r"D:/WorkBuddy/AI_Video/tools")
from qwen_t2i import build_workflow, http_json, download_image, COMFY

NEG = ("text, watermark, logo, subtitle, caption, signature, lowres, blurry, "
       "jpeg artifacts, deformed, bad anatomy, extra fingers, cartoon, anime, "
       "illustration, painting, oversaturated")
STYLE = ("Photorealistic cinematic 3D CG render, AAA game cinematic quality, "
         "Unreal Engine 5 rendering style, detailed skin shader with subsurface "
         "scattering, octane render quality, natural film grain, human realistic "
         "proportions (NOT cartoon, NOT anime). Cold teal night color grade with "
         "desaturated palette, restrained cinematic lighting, movie-animation "
         "realistic style. Vertical 9:16 composition.")

JOBS = [
    ("linmian_comatose_ref",
     "D:/WorkBuddy/AI_Video/characters/she_is_still_here/linmian_comatose",
     "Cinematic close-up shot of a young Chinese woman in her early twenties lying unconscious in a hospital bed, eyes peacefully closed, very pale fair skin, long straight black hair spread on a white pillow, wearing a pale blue hospital gown, an oxygen nasal cannula on her face, soft green glow from a heart monitor touching her cheek, a single dried tear on her cheek, melancholic emotional atmosphere. " + STYLE,
     NEG),
    ("linmian_awake_ref",
     "D:/WorkBuddy/AI_Video/characters/she_is_still_here/linmian_awake",
     "Upper body portrait of a young Chinese woman around 22, very pale fair skin, long straight black hair reaching her waist, gentle oval face with calm intelligent dark eyes, soft natural no-makeup look, wearing a simple clean white blouse, plain clean beauty, gentle subtle smile, soft window light from the side, contemplative mood, slightly melancholy undertone. " + STYLE,
     NEG),
    ("jiangche_ref",
     "D:/WorkBuddy/AI_Video/characters/she_is_still_here/jiangche",
     "Upper body portrait of a Chinese man around 31, short neat black hair, light stubble, tired but sharp dark eyes with deep fatigue, strong jaw, faint nasolabial lines hint of years on the job, wearing a dark charcoal jacket over a grey shirt, plain-clothes detective, dim corridor backlight with rim light on his shoulder, serious focused expression, vertical composition. " + STYLE,
     NEG),
    ("ward_scene",
     "D:/WorkBuddy/AI_Video/shots/she_is_still_here/scenes",
     "A dim private hospital ICU ward at night, a single hospital bed with white sheets neatly folded and slightly sunken from a body recently in it, a glowing heart monitor beside the bed casting cold green-cyan light, an IV drip stand with empty drip chamber, a white coat hung on a hook near the door, rain streaks on the large window with faint blurred city lights bokeh outside, soft cold teal night lighting, no people in the scene, moody atmospheric empty room composition, vertical composition. " + STYLE,
     NEG),
    ("lab_scene",
     "D:/WorkBuddy/AI_Video/shots/she_is_still_here/scenes",
     "A sleek modern neuroscience research laboratory at night, cold white and cyan color grade, a large experimental medical pod with transparent glass cover at center, sleek white tables with monitoring equipment and screens, holographic brain scan displays floating faintly, empty lab, a single distant silhouette of a person standing far back near the door as silhouette only (no detailed face visible), sterile cold atmosphere, no people close to camera, vertical composition. " + STYLE,
     NEG),
    ("cctv_scene",
     "D:/WorkBuddy/AI_Video/shots/she_is_still_here/scenes",
     "Surveillance CCTV point-of-view shot from top corner of a hospital corridor at night, fisheye lens distortion, cold cyan-green desaturated CCTV color grade, scanline grain, soft vignette, timecode overlay 'CAM-07 23:41:08' at bottom-left, faint 'REC' red dot indicator, showing a dim empty hospital corridor stretching into the distance with closed door on the left, no people visible, cinematic surveillance thriller aesthetic, vertical composition. " + STYLE,
     NEG),
]

def run(prefix, out_dir, prompt, negative, seed):
    wf = build_workflow(prompt, negative, 576, 1024, 20, 4.0,
                        "euler", "simple", seed, f"shestill_{prefix}")
    pid = http_json(f"{COMFY}/prompt", {"prompt": wf, "client_id": "batch"})["prompt_id"]
    print(f"[{prefix}] seed={seed} pid={pid} -> ", end="", flush=True)
    import time
    t0 = time.time()
    while time.time() - t0 < 1200:
        time.sleep(6)
        try:
            h = http_json(f"{COMFY}/history/{pid}", timeout=15)
        except Exception:
            continue
        if pid in h:
            st = h[pid].get("status", {})
            if st.get("completed") or st.get("status_str") == "success":
                imgs = [im for nid, nd in h[pid]["outputs"].items() for im in nd.get("images", [])]
                if imgs:
                    # 把文件改名为更易读的 reference.png / {scene}.png
                    img = imgs[0]
                    dst = download_image(img, out_dir)
                    ext = os.path.splitext(img["filename"])[1]
                    if "ref" in prefix:
                        final = os.path.join(out_dir, "reference.png")
                    else:
                        final = os.path.join(out_dir, f"{prefix}{ext}")
                    os.replace(dst, final)
                    print(f"OK {int(time.time()-t0)}s -> {final}")
                    return
            for m in st.get("messages", []):
                if m[0] == "execution_error":
                    print(f"FAIL: {m[1]}")
                    raise SystemExit(1)
    raise SystemExit("timeout " + prefix)

if __name__ == "__main__":
    for i, (prefix, out_dir, prompt, neg) in enumerate(JOBS):
        seed = 200_000_000 + i * 12345  # 不同 seed 让构图自然
        run(prefix, out_dir, prompt, neg, seed)
    print("ALL DONE")