# -*- coding: utf-8 -*-
"""
《最后一盏灯》长镜头接驳版 (1 条连续镜头 × 6 段 × 7s = 42s)
欧美暗黑哥特微短剧，单条连续镜头，用 motion_context chain 逐段接驳。
- 单一空间: 古堡大堂 (石台 + 右侧石柱/烛台锚点)
- 单角色: 嘉玲 (黑长袍 + 铜提灯)，规避双人同框分身
- 相机全程只做极小幅缓推/缓升，世界不旋转；段末静止 2s 防接驳抖动
- 每段是"同一镜头第 N 段"完整独立提示词，剧情事件逐段推进
输出: shots/lantern_long_manifest.json
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
    "Asian oval face, single eyelids, solemn reserved expression, wearing a "
    "black floor-length hooded robe with the hood down, carrying a small old "
    "brass lantern"
)
JIALING_CU_SUBJECT = (
    "the same 17-year-old girl in a close-up portrait, wavy auburn-red hair, "
    "Asian oval face, single eyelids, solemn determined eyes, black hooded robe"
)

CONT_UNIT = (
    "This is segment {n} of ONE single continuous shot inside the ruined gothic "
    "castle great hall. There is no cut, no jump cut, no scene change, no "
    "rotation of the world — the camera only glides very slowly in one "
    "unbroken take."
)
ANCHOR = (
    "A massive broken stone pillar stays fixed at the right edge of the frame, "
    "with a row of flickering candelabras on the right side, fixed throughout "
    "the entire shot. Jialing wears the same black robe and carries the same "
    "brass lantern throughout."
)
HOLD = (
    "In the final stretch of this segment the camera settles into a perfectly "
    "still hold for the last two seconds."
)

# 每段: 独立完整提示词 + 氛围音 (剧情事件逐段推进)
SEGMENTS = [
    {
        "name": "01_castle",
        "seg": (
            f"{CONT_UNIT.format(n='1 of 6')} Medium shot. "
            "Jialing matching Picture 1 walks slowly from the deep background "
            "toward the carved stone altar in the center of the frame, then "
            "sets the brass lantern down on the altar and straightens. The "
            "camera glides slowly forward throughout. " + ANCHOR +
            " Nothing moves except Jialing, the candle flames and the camera "
            "glide. " + HOLD
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, cold blue-black "
            "shadows, warm amber candlelight accents, thin drifting dust, "
            "broken vaulted ceiling with faint pale moonlight falling through"
        ),
        "grade": "chiaroscuro, cold steel-blue shadows with warm candle "
                 "highlights, film grain, dark gothic color grade",
        "sound": "hollow wind through broken windows, distant crows",
        "music": "low somber drone, cold and vast",
    },
    {
        "name": "02_ritual",
        "seg": (
            f"{CONT_UNIT.format(n='2 of 6')} CONTINUATION. From this held "
            "position the camera resumes a very slow forward glide. Jialing "
            "now stands before the stone altar and raises both hands in a "
            "summoning gesture; a heavy black grimoire rises from the altar "
            "surface, floating a hand's height, its pages glowing faint "
            "green. The candle flames all tilt slightly toward her. " +
            ANCHOR + " Nothing rotates. " + HOLD
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, cold blue-black "
            "shadows, warm amber candlelight, faint green glow from the "
            "floating grimoire, thin drifting dust"
        ),
        "grade": "chiaroscuro, cold steel-blue with warm candle and eerie "
                 "green highlights, film grain, dark gothic color grade",
        "sound": "low chanting, candle wax crackling",
        "music": "whispered choir, ominous and hushed",
    },
    {
        "name": "03_shadow",
        "seg": (
            f"{CONT_UNIT.format(n='3 of 6')} CONTINUATION. The camera "
            "continues an extremely slow forward glide into a near shot. "
            "Jialing closes her eyes and murmurs silently; on the wall behind "
            "her, her own shadow detaches from the wall and slowly grows into "
            "a huge horned beast silhouette looming over her. Only the shadow, "
            "the candle flames and the camera glide move; the world does not "
            "rotate. " + ANCHOR + " " + HOLD
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, cold blue-black "
            "shadows, warm amber candlelight on her face, the horned shadow "
            "beast darker than black against the stone wall"
        ),
        "grade": "chiaroscuro, high contrast, cold steel-blue with warm candle "
                 "highlights, film grain, dark gothic color grade",
        "sound": "rising heartbeat, faint low breathing",
        "music": "dark pulse, tension building",
    },
    {
        "name": "04_mirror",
        "seg": (
            f"{CONT_UNIT.format(n='4 of 6')} CONTINUATION. Still in the same "
            "take, the camera keeps gliding forward at a crawl into a close "
            "shot. A large antique bronze mirror standing in the right "
            "foreground catches green light — inside the mirror, her "
            "reflection does NOT follow her actions: the reflection slowly "
            "smiles an eerie grin and shakes its head. She opens her eyes, "
            "pupils narrowing. " + ANCHOR + " " + HOLD
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, the antique "
            "bronze mirror reflecting cold green light, her face lit by warm "
            "candle amber, surrounding darkness"
        ),
        "grade": "chiaroscuro, eerie green against warm amber, film grain, "
                 "dark gothic color grade",
        "sound": "low eerie hum, a faint wrong laugh",
        "music": "dissonant strings, slow and unsettling",
    },
    {
        "name": "05_giant",
        "seg": (
            f"{CONT_UNIT.format(n='5 of 6')} CONTINUATION. The camera rises "
            "very slowly and only by a small amount into a low angle, "
            "close-medium shot. Jialing lifts her gaze; high above, through a "
            "shattered dome, a colossal faceless black figure presses down "
            "from the clouds, eclipsing the pale moon. On the altar the flame "
            "of the brass lantern gutters violently in a wind that moves "
            "nothing else. " + ANCHOR + " " + HOLD
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, the shattered "
            "dome opening to a clouded sky, a colossal faceless black figure "
            "pressing down and eclipsing the pale moon, candle flames guttering"
        ),
        "grade": "chiaroscuro, extreme low-key, cold steel-blue, moonlit rim "
                 "on her hair, film grain, dark gothic color grade",
        "sound": "muffled thunder, faint rubble falling, wind gusts",
        "music": "low timpani roll, dread approaching",
    },
    {
        "name": "06_sacrifice",
        "seg": (
            f"{CONT_UNIT.format(n='6 of 6')} CONTINUATION, final segment. The "
            "camera glides into an extreme close shot. Jialing bites the tip "
            "of her right index finger and presses one drop of blood onto the "
            "wick of the brass lantern. The wick erupts in a blinding white "
            "blaze; a shockwave of light floods outward and overexposes the "
            "entire frame to pure white, ending the shot. " + ANCHOR
        ),
        "weather": (
            "Night inside a ruined gothic castle great hall, extreme close on "
            "the girl and the brass lantern, warm candlelight on her face "
            "before the blinding white burst floods the whole frame"
        ),
        "grade": "dark gothic that is abruptly overexposed to pure white by "
                 "the light blast, film grain",
        "sound": "sharp burst, rushing air, then ringing silence",
        "music": "single choir strike, then silence",
    },
]


def make_shot_entry(seg, shot_no):
    img = IMG_JIALING
    subjects = [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/robe/lantern"},
        {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
    ]
    ref_list = [img, img]
    action = (
        f"{seg['seg']}\n"
        f"Scene and weather: {seg['weather']}.\n"
        f"Color grade: {seg['grade']}."
    )
    shot = {
        "action": action,
        "sound": seg["sound"],
        "music": seg["music"],
        "dialogue": None,
        "speaker": "S1",
    }
    prompt = build_prompt(shot, subjects)
    issues = check_prompt(prompt, ref_list)
    return prompt, issues


def main():
    img = IMG_JIALING
    entries = []
    n_bad = 0
    for i, seg in enumerate(SEGMENTS, start=1):
        prompt, issues = make_shot_entry(seg, i)
        if issues:
            n_bad += 1
            print(f"[FAIL] {seg['name']} seg{i}: {issues}")
        else:
            print(f"[OK]   {seg['name']} seg{i}")
        entries.append({
            "shot": i,
            "storyboard": img,
            "character": img,
            "scene": None,
            "extra_images": [],
            "seconds": 7.0,
            "megapixels": 0.7,
            "prompt": prompt,
        })

    sets = [{
        "id": "jialing_lantern_long",
        "title": "《最后一盏灯》42s 连续长镜头 6×7s chain 接驳",
        "shots": entries,
    }]

    manifest = {
        "comfy_url": "http://100.67.139.74:8188",
        "workflow": "workflows/h3_r2v_motion_context_api.json",
        "base_dir": "shots",
        "sets": sets,
    }
    out = ROOT / "shots" / "lantern_long_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    total_s = len(entries)
    print(f"\nmanifest -> {out}  (1 条 × {total_s} 段 × 7s = {total_s * 7}s, megapixels=0.7)")
    print(f"校验: {total_s - n_bad}/{total_s} 段通过")


if __name__ == "__main__":
    main()
