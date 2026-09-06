# -*- coding: utf-8 -*-
"""《她还在》EP01 资产缺口 + 样板分镜图批量生成（本地 qwen-image 0 积分）"""
import sys, os, subprocess, time

ROOT = r"D:/WorkBuddy/AI_Video"
CHAR = os.path.join(ROOT, "characters", "she_is_still_here")
SCENE = os.path.join(ROOT, "shots", "she_is_still_here", "scenes")
SB = os.path.join(ROOT, "scripts", "she_is_still_here", "storyboard")
for d in [os.path.join(CHAR, "fangxu"), SCENE, SB]:
    os.makedirs(d, exist_ok=True)

STYLE = ("Photorealistic cinematic 3D CG render, UE5 quality, detailed skin shader with subsurface scattering, "
         "cold desaturated cinematic color grade, film grain. NOT cartoon, NOT anime.")
NEG = ("text, watermark, logo, subtitle, caption, signature, letter, label, lowres, blurry, jpeg artifacts, "
       "deformed, bad anatomy, extra fingers, cartoon, anime, illustration, painting, oversaturated")

JOBS = [
    # 1) 方旭定妆（正脸半身）→ bean_fangxu.png + reference.png
    dict(
        name="fangxu",
        prefix="shestill_fangxu",
        out=os.path.join(CHAR, "fangxu"),
        w=832, h=1216,
        prompt=(STYLE + " Portrait of a Chinese man around 45, tired gaunt face with deep eye bags, sparse stubble, "
                "slightly receding thin dark hair, thin pressed lips, hollow weary eyes, worn plain dark-blue "
                "technical work jacket over a grey hoodie, night-shift IT technician look, head-and-shoulders "
                "facing camera, dim computer workstation with faint screen glow on his face, low-key somber "
                "lighting, solemn worn-down mood."),
    ),
    # 2) 死者公寓内景（镜 11 书桌现场）
    dict(
        name="apt_scene",
        prefix="shestill_apt",
        out=SCENE,
        w=832, h=1216,
        prompt=(STYLE + " Dim cramped single-room apartment interior at night in an old aging building, cluttered "
                "desk with old dual monitors showing faint blue screens, stacks of loose documents and instant "
                "noodle cups scattered, unmade narrow bed, cold fluorescent ceiling light, rain-streaked window "
                "with blurred city lights, lonely depressing atmosphere, no people, vertical 9:16 composition."),
    ),
    # 3) 雨夜街头（镜 09 江彻勘查外景）
    dict(
        name="nightstreet_scene",
        prefix="shestill_street",
        out=SCENE,
        w=832, h=1216,
        prompt=(STYLE + " Empty old residential street at night in light rain, wet asphalt mirroring cold streetlamp "
                "and faint neon reflections, aged low apartment buildings receding into mist, single streetlamp "
                "casting cold pale light, damp gloomy atmosphere, no people, vertical 9:16 composition."),
    ),
    # 4) 样板分镜图 镜01：机房死者独坐
    dict(
        name="sb_ep01_s01",
        prefix="shestill_sb01",
        out=SB,
        w=832, h=1216,
        prompt=(STYLE + " Cinematic film still, vertical 9:16. 1am in a dim IT server room corner: rows of faint "
                "blinking server racks blurred in the background, a gaunt Chinese man around 45 in a worn dark-blue "
                "work jacket sits at a small desk in the LOWER-RIGHT of frame eating instant noodles, staring at an "
                "old phone in his other hand, single cold fluorescent tube above his desk, vast empty dark negative "
                "space above and left around him emphasizing isolation, low-key moody lighting, storyboard "
                "composition quality."),
    ),
    # 5) 样板分镜图 镜05：病房江彻握林眠手絮叨
    dict(
        name="sb_ep01_s05",
        prefix="shestill_sb05",
        out=SB,
        w=832, h=1216,
        prompt=(STYLE + " Cinematic film still, vertical 9:16. Private hospital ICU ward at night: rain-streaked "
                "window on the right with blurred city lights, a young woman around 22 lies unconscious in the bed "
                "on the RIGHT side under a white blanket, long straight black hair spread on the pillow, eyes "
                "closed, pale calm face; a weary Chinese man around 31 in a dark charcoal jacket sits on a chair at "
                "the LEFT of the bed leaning forward, holding her hand gently in both of his, head bowed in quiet "
                "tenderness, his face half-lit by cold blue-green monitor glow. Medium shot, balanced two-person "
                "composition, quiet grief atmosphere, storyboard composition quality."),
    ),
]

def run(py, prefix, out, w, h, prompt, neg):
    cmd = [py, os.path.join(ROOT, "tools", "qwen_t2i.py"),
           "--prefix", prefix, "--out", out,
           "--width", str(w), "--height", str(h),
           "--steps", "20", "--cfg", "4",
           "--prompt", prompt, "--negative", neg]
    print(">>>", prefix, flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print("FAIL", prefix, r.stderr[-2000:], flush=True)
        return None
    for line in r.stdout.splitlines():
        if "[copy]" in line:
            dst = line.split("]", 1)[1].strip()
            print("OK", dst, flush=True)
            return dst
    print("WARN no copy line:", r.stdout[-500:], flush=True)
    return None

if __name__ == "__main__":
    py = sys.executable
    results = []
    for j in JOBS:
        dst = run(py, j["prefix"], j["out"], j["w"], j["h"], j["prompt"], NEG)
        results.append((j["name"], dst))
        time.sleep(1)
    print("ALL DONE", flush=True)
    for n, d in results:
        print(n, "->", d, flush=True)
