# -*- coding: utf-8 -*-
"""
lens_04/lens_07 长镜头版本生成器（用户反馈: 镜头太慢/舒展力不够 → 延长到 12-15s）
输出: shots/lens_long_manifest.json
- 2 镜 × 2 段 × 7s = 14s, 720p(megapixels=0.7), 用 motion_context 工作流 chain 接驳
- 每镜拆 2 段: shot1 运镜前半程, shot2 运镜后半程(MotionContext latent 续接尾帧),
  让同一运镜在 14s 内舒展完成
- 沿用 fix 的修复技巧: 30° 短弧替代 orbit / 低幅缓升 + 世界坐标锚点(松树/巨石)固定不动
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"

JIALING_SUBJECT = (
    "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, cool detached big-sister aura, wearing "
    "Hogwarts style dark robe, red and yellow striped scarf, grey pleated skirt"
)
JIALING_CU_SUBJECT = (
    "the same 17-year-old girl in a close-up portrait, wavy auburn-red hair, "
    "Asian oval face, single eyelids, red and yellow striped scarf"
)

SEG1_BONFIRE = (
    "Close-up on Jialing matching Picture 1 kneeling beside a single campfire "
    "in a dark forest clearing. Only the camera moves: it begins one short slow "
    "arc of about 30 degrees, starting from her right side and gliding very "
    "slowly toward the front of her. The world does not rotate at all: Jialing "
    "stays kneeling and facing the campfire the whole time without turning her "
    "body, and one large dark pine tree remains firmly fixed at the right edge "
    "of the frame throughout the entire shot. Warm firelight flickers steadily "
    "across her face, sparks drifting up from that same single fire. The camera "
    "movement is unhurried and continuous, gaining a gentle sense of openness "
    "as it slowly reaches the front of her by the end of this segment."
)
SEG2_BONFIRE = (
    "CONTINUATION of the same shot, second half. The camera continues the same "
    "short slow arc from where it was, gliding just a few more degrees past "
    "the front of Jialing, then gently holds still. The world does not rotate "
    "at all: Jialing keeps kneeling and facing the single campfire without "
    "turning her body, and the same large dark pine tree stays firmly fixed at "
    "the right edge of the frame the whole time. Only her hair and the scarf "
    "tremble slightly in the warm air as sparks keep drifting up from that same "
    "single fire. The shot ends on a calm, open hold of the firelight on her face."
)
SEG1_LAKE = (
    "Wide shot on the shore of a calm mountain lake at sunrise. Jialing "
    "matching Picture 1 stands at the water's edge on the left side of the "
    "frame, seen from her side profile. Only the camera moves: it starts to "
    "rise very slowly and by only a small amount, staying at a modest height "
    "so Jialing remains clearly visible in the lower left of the frame at all "
    "times. The lake surface stays perfectly calm and still, reflecting the "
    "sky, distant forested hills behind her. A large grey boulder stays fixed "
    "at the bottom-right corner of the frame throughout the entire shot. "
    "Nothing in the world rotates or moves except the gentle mist drifting "
    "over the water. The rise is unhurried and continuous, the composition "
    "gradually opening wider toward the sky."
)
SEG2_LAKE = (
    "CONTINUATION of the same shot, second half. The camera continues rising "
    "very slowly from where it was, by only a small additional amount, then "
    "holds steady at a modest height so Jialing stays clearly visible in the "
    "lower left of the frame the whole time. The calm mountain lake stays "
    "perfectly still, reflecting the sunrise sky, distant forested hills "
    "behind her. The same large grey boulder remains fixed at the bottom-right "
    "corner of the frame. Nothing in the world rotates or moves except the "
    "gentle mist drifting over the water. The shot ends on a serene, open hold "
    "of the quiet lake and Jialing by the water."
)

SHOTS = [
    {
        "name": "lens_long_04_bonfire",
        "title": "04长 篝火夜林·嘉玲 特写+30°短弧 14s",
        "seg1": SEG1_BONFIRE,
        "seg2": SEG2_BONFIRE,
        "weather": (
            "Clear starry night, dark pine forest, one steady campfire, drifting "
            "sparks, cool air, faint smoke curling upward"
        ),
        "grade": "warm firelight against dark teal, high contrast cinematic",
        "dialogue": "火的声音，真好听。",
        "sound": "crackling fire, night insects, distant owl call",
        "music": "warm fingerpicked acoustic, calm and meditative",
    },
    {
        "name": "lens_long_07_lake",
        "title": "07长 晨湖静谧·嘉玲 远景+低幅缓升 14s",
        "seg1": SEG1_LAKE,
        "seg2": SEG2_LAKE,
        "weather": (
            "Sunrise, soft golden-pink light over a still mirror-like lake, thin mist "
            "on the water surface, quiet forested hills, calm and peaceful"
        ),
        "grade": "soft dawn pastel grade, serene and airy",
        "dialogue": "好安静啊。",
        "sound": "still water, faint birdsong, soft morning breeze",
        "music": "minimal ambient piano, quiet and vast",
    },
]


def make_shot_entry(sh, seg_text, shot_no):
    img = IMG_JIALING
    subjects = [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
        {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
    ]
    ref_list = [img, img]
    action = (
        f"{seg_text}\n"
        f"Scene and weather: {sh['weather']}.\n"
        f"Color grade: {sh['grade']}."
    )
    shot = dict(sh)
    shot["action"] = action
    shot["sound"] = sh["sound"]
    shot["music"] = sh["music"]
    shot["dialogue"] = sh["dialogue"]
    shot["speaker"] = "S1"
    prompt = build_prompt(shot, subjects)
    issues = check_prompt(prompt, ref_list)
    return prompt, issues


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING
        seg_entries = []
        for seg_key, shot_no in (("seg1", 1), ("seg2", 2)):
            prompt, issues = make_shot_entry(sh, sh[seg_key], shot_no)
            if issues:
                n_bad += 1
                print(f"[FAIL] {sh['name']} seg{shot_no}: {issues}")
            else:
                print(f"[OK]   {sh['name']} seg{shot_no}")
            seg_entries.append({
                "shot": shot_no,
                "storyboard": img,
                "character": img,
                "scene": None,
                "extra_images": [],
                "seconds": 7.0,
                "megapixels": 0.7,
                "prompt": prompt,
            })
        sets.append({
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": seg_entries,
        })

    manifest = {
        "comfy_url": "http://100.67.139.74:8188",
        "workflow": "workflows/h3_r2v_motion_context_api.json",
        "base_dir": "shots",
        "sets": sets,
    }
    out = ROOT / "shots" / "lens_long_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套 × 2 段 × 7s = 14s, "
          f"megapixels=0.7)")
    print(f"校验: {len(SHOTS) * 2 - n_bad}/{len(SHOTS) * 2} 段通过")


if __name__ == "__main__":
    main()
