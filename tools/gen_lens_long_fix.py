# -*- coding: utf-8 -*-
"""
07 晨湖长镜头接驳抖动修复（用户反馈: 第二段接驳处镜头先下摇又上升）
输出: shots/lens_long_fix_manifest.json
根因: shot01 末帧带"缓升"运动速度, MotionContext 注入后 shot02 启动新上升指令前先反向归零
修复: ①shot01 末段明确"rise is complete + camera holds perfectly still"(运动归零)
      ②shot02 开头声明 "From this calm held static position..."(从静止态重新起步)
      ③shot01 末尾留静止区
- 只出 07 一镜 × 2 段 × 7s, motion_context chain, 720p
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
    "over the water. In the final stretch of this segment the camera settles "
    "into a calm held frame: the rise is complete and the camera holds "
    "perfectly still, keeping Jialing, the boulder, the lake and the hills "
    "exactly in place for the last two seconds."
)
SEG2_LAKE = (
    "CONTINUATION of the same shot, second half. From this calm held static "
    "position the camera resumes a very slow rise, moving upward by only a "
    "small additional amount, then holds steady again at a modest height so "
    "Jialing stays clearly visible in the lower left of the frame the whole "
    "time. The calm mountain lake stays perfectly still, reflecting the "
    "sunrise sky, distant forested hills behind her. The same large grey "
    "boulder remains fixed at the bottom-right corner of the frame. Nothing "
    "in the world rotates or moves except the gentle mist drifting over the "
    "water. The shot ends on a serene, open hold of the quiet lake and "
    "Jialing by the water."
)

SHOTS = [
    {
        "name": "lens_long_fix_07_lake",
        "title": "07长fix 晨湖静谧·嘉玲 远景+低幅缓升 14s(接驳修复)",
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


def make_shot_entry(sh, seg_text):
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
            prompt, issues = make_shot_entry(sh, sh[seg_key])
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
    out = ROOT / "shots" / "lens_long_fix_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套 × 2 段 × 7s = 14s, megapixels=0.7)")
    print(f"校验: {len(SHOTS) * 2 - n_bad}/{len(SHOTS) * 2} 段通过")


if __name__ == "__main__":
    main()
