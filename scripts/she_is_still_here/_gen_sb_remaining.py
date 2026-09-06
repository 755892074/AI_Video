# -*- coding: utf-8 -*-
"""《她还在》EP01 剩余 10 镜分镜图批量生成（本地 qwen-image 0 积分）"""
import sys, os, subprocess, time

ROOT = r"D:/WorkBuddy/AI_Video"
SB = os.path.join(ROOT, "scripts", "she_is_still_here", "storyboard")
os.makedirs(SB, exist_ok=True)

STYLE = ("Photorealistic cinematic 3D CG render, UE5 quality, detailed skin shader with subsurface scattering, "
         "cold desaturated cinematic color grade, film grain, vertical 9:16 composition. NOT cartoon, NOT anime.")
NEG = ("text, watermark, logo, subtitle, caption, signature, letter, label, lowres, blurry, jpeg artifacts, "
       "deformed, bad anatomy, extra fingers, cartoon, anime, illustration, painting, oversaturated, readable text")

# 角色特征速查（跨镜一致）
JIANG = ("a weary Chinese man around 31 with short neat black hair and light stubble, deep tired eyes, "
         "dark charcoal jacket over a grey shirt, plain-clothes detective")
LIN = ("a young Chinese woman around 22 with long straight black hair, pale calm face, lying unconscious")
FANG = ("a gaunt Chinese man around 45 in a worn dark-blue work jacket, hollow tired eyes, thin receding hair")

JOBS = [
    # 镜02 方旭倒下（胸口一震 → 手松 → 弓身）
    dict(name="ep01_shot02", prefix="shestill_sb02", desc="shot02 Fangxu collapses",
         prompt=(STYLE + " A dim IT server room corner at night, same tired night-shift workstation as an earlier "
                 "shot: {F} sits at a small desk, his body suddenly jerking stiff with a sharp pain in his chest, "
                 "bending forward rigidly, one hand letting go of the chopsticks while the instant-noodle bowl tips "
                 "over on the desk, his hollow eyes unfocused and glassy, a single cold fluorescent tube above, "
                 "medium shot fixed camera, sudden fatal shock frozen in mid-motion.").replace("{F}", FANG)),
    # 镜03 江彻推开机房玻璃门
    dict(name="ep01_shot03", prefix="shestill_sb03", desc="shot03 Jiang opens server room door",
         prompt=(STYLE + " Seen from inside the dim server room doorway: {J} shoves the glass door open hard and "
                 "steps in, holding a flashlight whose cold beam cuts across the dark room toward the left side of "
                 "the frame, his weary face lit half by the flashlight half by faint rack lights, tense alert "
                 "expression, medium shot from a low angle, the man framed at right inside the door frame, dark "
                 "corridor behind him.").replace("{J}", JIANG)),
    # 镜04 老人机发现 306（死者外套口袋）
    dict(name="ep01_shot04", prefix="shestill_sb04", desc="shot04 old phone 306 found",
         prompt=(STYLE + " Extreme close-up in dim light: a rough adult male hand (detective) carefully pulls an "
                 "old-fashioned bar phone (cheap elderly-style phone) out of a dead man's jacket pocket, its small "
                 "screen half-glowing and showing one unread message whose sender number reads as digits 306, "
                 "shallow depth of field, cold somber tones, tense quiet mood, gloved and ungloved hands visible.")),
    # 镜06 双手相握（江彻手 × 林眠手 特写）
    dict(name="ep01_shot06", prefix="shestill_sb06", desc="shot06 hands clasped bedside",
         prompt=(STYLE + " Extreme close-up vertical shot at a hospital bedside at night: a rough weathered man's "
                 "hand (dark grey jacket sleeve visible) gently clasping a pale thin unconscious young woman's hand, "
                 "fingers softly interlocked, a faint IV needle taped on the back of her hand, cold blue-green "
                 "ward light, shallow depth of field, five years of quiet devotion in one gesture, tender yet "
                 "heavy atmosphere.")),
    # 镜07 她听得到（俯视全卧 + 心电监护）
    dict(name="ep01_shot07", prefix="shestill_sb07", desc="shot07 she can hear",
         prompt=(STYLE + " Private ICU ward at night, high-angle medium shot looking down at the bed: {L} on the "
                 "white bed as if peacefully asleep, face calm, long black hair spread on the pillow, a heart "
                 "monitor beside the bed glowing with a steady cold green curve, the blurred figure of a weary man "
                 "in a dark jacket sitting guard at the edge of the frame, the room utterly still, large quiet "
                 "negative space above for subtitle, cold blue-green night grade.").replace("{L}", LIN)),
    # 镜08 老人机骤然亮起 306
    dict(name="ep01_shot08", prefix="shestill_sb08", desc="shot08 old phone screen lights up",
         prompt=(STYLE + " Extreme close-up of an old bar phone screen suddenly lighting up bright cold white in "
                 "near-total darkness, the screen showing one incoming message thread with a sender labeled 306 "
                 "(message text blurred and unreadable on purpose), a man's hand holding the phone trembling "
                 "slightly, the screen the only light source in the frame, eerie suspense pulse.")),
    # 镜09 江彻雨夜下车勘查
    dict(name="ep01_shot09", prefix="shestill_sb09", desc="shot09 Jiang walks rainy street",
         prompt=(STYLE + " Night in an old residential street in light rain: {J} steps out of an unmarked black "
                 "sedan parked at the curb, standing on wet asphalt mirroring cold streetlamp light, rain streaks "
                 "slanting through the light, he looks up at old low apartment buildings ahead, lonely investigative "
                 "beginning, medium shot three-quarter angle, character at right of frame with the buildings "
                 "receding left.").replace("{J}", JIANG)),
    # 镜10 公寓门口·走廊影子
    dict(name="ep01_shot10", prefix="shestill_sb10", desc="shot10 corridor silhouette",
         prompt=(STYLE + " Old apartment building corridor at night, wide shot: {J} seen from behind standing at "
                 "an open apartment doorway, while at the far end of the dim corridor a faint blurred female "
                 "silhouette flickers and is gone in a second (translucent ghost-like figure, face unreadable), "
                 "cold pale fluorescent light, big empty negative space, she is here, suspense atmosphere.").replace("{J}", JIANG)),
    # 镜11 书桌发现半张名单
    dict(name="ep01_shot11", prefix="shestill_sb11", desc="shot11 half name list found",
         prompt=(STYLE + " Cluttered cramped apartment study desk at night: {J} stands half in shadow beside the "
                 "desk, one hand pulling a folded yellowing paper (a torn half list of names with handwriting, "
                 "text blurred and unreadable) out of a messy drawer, old dual monitors, instant-noodle cups and "
                 "document stacks on the desk, cold fluorescent light, medium shot, the paper at upper-center "
                 "focus while his dark silhouette anchors the right side.").replace("{J}", JIANG)),
    # 镜12 短信落点：别查了
    dict(name="ep01_shot12", prefix="shestill_sb12", desc="shot12 final SMS",
         prompt=(STYLE + " Extreme close-up in pure darkness: a modern phone screen glowing as the only light "
                 "source, displaying one SMS conversation from a sender numbered 306 with several lines of text "
                 "(the actual Chinese words deliberately blurred and unreadable in this pre-viz frame), the hand "
                 "holding it slightly out of focus below, huge black negative space above, oppressive quiet "
                 "weight, final beat of the episode.")),
]

def run(py, prefix, out, prompt, neg):
    cmd = [py, os.path.join(ROOT, "tools", "qwen_t2i.py"),
           "--prefix", prefix, "--out", out,
           "--width", "832", "--height", "1216",
           "--steps", "20", "--cfg", "4",
           "--prompt", prompt, "--negative", neg]
    print(">>>", prefix, flush=True)
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        print("FAIL", prefix, r.stderr[-1500:], flush=True)
        return None
    for line in r.stdout.splitlines():
        if "[copy]" in line:
            return line.split("]", 1)[1].strip()
    print("WARN", r.stdout[-400:], flush=True)
    return None

if __name__ == "__main__":
    py = sys.executable
    for j in JOBS:
        src = run(py, j["prefix"], SB, j["prompt"], NEG)
        if src:
            dst = os.path.join(SB, j["name"] + ".png")
            subprocess.run(["cp", src, dst])
            print("NAMED", j["name"] + ".png", flush=True)
        time.sleep(1)
    print("ALL DONE", flush=True)
