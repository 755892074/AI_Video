# -*- coding: utf-8 -*-
"""
《最后一盏灯》混合结构 v2 (切镜 + 接驳) —— 修复版 v2
基于 v2 反馈 (23:43) 修复空间一致性 + 23:52 反馈"宏大感丢失"修复纵深:
  P0-1: 注入场景参考图 (scenes/lantern_hall_v2.png, 纵深/宏大版, 替代 v1 紧凑版)
  P0-2: ANCHOR 改 world-relative (不再 "right edge of frame" 这种 screen-relative)
  P0-3: A/B/C 全部拆 3 段: seg2 同景别起事件 (无运镜), seg3 才改景别收尾
  P0-4: B 删 "camera positioned slightly left of the altar" 机位重设 (导致贴墙角落的元凶)
  P0-5: B 镜子绑定世界坐标: "against the base of the broken stone pillar on the right side of the hall"
       (与 v2 场景图右侧柱对齐, 避免 H3 凭空重想空间)
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_SCENE = "../scenes/lantern_hall_v2.png"  # v2: 强调纵深/宏大, 替代 v1 紧凑版

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
SCENE_SUBJECT = (  # 改: v2 强调纵深 + 宏大
    "the vast ruined gothic castle great hall matching Picture 3: a carved stone "
    "altar in the center foreground, extreme deep perspective with two rows of tall "
    "stone columns vanishing into a distant background, a towering vaulted ceiling "
    "with a shattered broken dome high above, tall gothic arched stained-glass windows "
    "along the left wall, a massive broken stone pillar on the right side of the hall "
    "with a row of flickering candelabras, cracked stone floor with long perspective lines"
)

# 改 world-relative: 锚点描述的是世界空间位置，不再随景别变化失效
ANCHOR = (
    "In the world, the carved stone altar stays fixed at the center of the hall, "
    "the massive broken stone pillar stays fixed on the right side of the hall "
    "with the row of flickering candelabras at its base. Throughout the entire "
    "shot the altar, the pillar and the candelabras never move; only Jialing, "
    "the candle flames and the camera move. Jialing wears the same black robe "
    "and carries the same brass lantern throughout."
)
HOLD = (
    "In the final stretch of this segment the camera settles into a perfectly "
    "still hold for the last two seconds."
)

# 3 个镜头, 每镜 2 段 (A 修复版为 3 段)
SHOTS = [
    {
        "id": "jialing_lantern2_a_fix",  # 改后缀避免 skip 旧输出
        "title": "镜头A 入厅·仪式 (3段修复: 推进 + 同景别起事件 + 推近收尾)",
        "weather": (
            "Night inside a ruined gothic castle great hall, cold blue-black "
            "shadows, warm amber candlelight accents, thin drifting dust, "
            "broken vaulted ceiling with faint pale moonlight falling through"
        ),
        "grade": "chiaroscuro, cold steel-blue shadows with warm candle "
                 "highlights, film grain, dark gothic color grade",
        "segs": [
            {
                # seg1: 入厅推进 (与原版同)
                "prompt": (
                    "Shot A, segment 1 of 3, of ONE continuous take inside the "
                    "ruined gothic castle great hall matching Picture 3. Medium "
                    "shot. Jialing matching Picture 1 walks from the deep "
                    "background toward the carved stone altar at the center of "
                    "the hall, carrying a small old brass lantern; she sets it "
                    "down on the altar and straightens. The camera glides "
                    "forward noticeably, following her approach the whole "
                    "time. " + ANCHOR + " Nothing moves except Jialing's walk, "
                    "the candle flames and the camera glide. " + HOLD
                ),
                "sound": "hollow wind through broken windows, distant crows",
                "music": "low somber drone, cold and vast",
            },
            {
                # seg2: 新增 — 同景别起 grimoire 事件, 运镜静止 (避免 re-zero dip)
                "prompt": (
                    "Shot A, segment 2 of 3, CONTINUATION of the same take. "
                    "From this held position the camera remains perfectly "
                    "still in the same medium shot — NO dolly, NO push, NO "
                    "movement of the camera at all. Jialing standing before the "
                    "stone altar raises both hands in a summoning gesture; a "
                    "heavy black grimoire rises from the altar surface, "
                    "floating a hand's height above it, its pages glowing "
                    "faint green. The candle flames tilt slightly toward her. " +
                    ANCHOR + " Throughout this segment the camera does not "
                    "move; only the grimoire, the candle flames and Jialing's "
                    "hands move. The segment ends on the floating green book."
                ),
                "sound": "low chanting, candle wax crackling",
                "music": "whispered choir, ominous and hushed",
            },
            {
                # seg3: 新增 — 推近收尾 (景别从 medium → medium-close)
                "prompt": (
                    "Shot A, segment 3 of 3, CONTINUATION of the same take, "
                    "final segment. From this still position the camera glides "
                    "slowly forward into a medium-close shot of Jialing and "
                    "the floating green grimoire. Jialing's summoning hands "
                    "and the book's green glow become the focus. " + ANCHOR +
                    " The shot ends on her hands and the floating book."
                ),
                "sound": "low chanting continues, swelling slightly",
                "music": "whispered choir intensifies, then fades",
            },
        ],
    },
    {
        "id": "jialing_lantern2_b_fix",  # 改后缀避免 skip 旧输出
        "title": "镜头B 影子·魔镜 (3段修复: 影兽+镜子+推近收尾)",
        "weather": (
            "Night inside the same vast ruined gothic castle great hall, cold "
            "blue-black shadows, warm amber candlelight on her face, the horned "
            "shadow beast darker than black against the stone wall, an antique "
            "bronze mirror standing against the base of the broken stone pillar "
            "on the right side of the hall reflecting cold green light"
        ),
        "grade": "chiaroscuro, high contrast, eerie green against warm amber, "
                 "film grain, dark gothic color grade",
        "segs": [
            {
                # seg1: 影兽从无长到巨大 (运镜缓推, 同景别, 删 camera slightly left 重设)
                "prompt": (
                    "Shot B, segment 1 of 3, of ONE continuous take inside the "
                    "same vast ruined gothic castle great hall matching Picture 3. "
                    "Medium-close shot of Jialing standing before the stone altar, "
                    "deep perspective visible behind her with stone columns vanishing "
                    "into the distance. Jialing closes her eyes and murmurs silently; "
                    "on the wall behind her, her own shadow detaches from the wall and "
                    "slowly grows into a huge horned beast silhouette looming over her "
                    "and filling the wall behind her. The camera glides forward slowly. " +
                    ANCHOR + " Only the shadow, the candle flames and the camera glide "
                    "move; the world does not rotate. " + HOLD
                ),
                "sound": "rising heartbeat, faint low breathing",
                "music": "dark pulse, tension building",
            },
            {
                # seg2: 新增 — 同景别起镜子+反射事件 (运镜静止)
                "prompt": (
                    "Shot B, segment 2 of 3, CONTINUATION of the same take. From this "
                    "held position the camera remains perfectly still in the same "
                    "medium-close shot — NO dolly, NO push, NO movement of the camera "
                    "at all. A large antique bronze mirror appears standing against the "
                    "base of the broken stone pillar on the right side of the hall, "
                    "catching cold green light. Inside the mirror, her reflection does "
                    "NOT follow her: the reflection slowly grins an eerie smile and "
                    "shakes its head. She opens her eyes, pupils narrowing. The horned "
                    "shadow still looms on the wall behind her. " + ANCHOR + " Throughout "
                    "this segment the camera does not move; only the reflection, the "
                    "green light, and Jialing's eyes move."
                ),
                "sound": "low eerie hum, a faint wrong laugh",
                "music": "dissonant strings, slow and unsettling",
            },
            {
                # seg3: 新增 — 推近收尾 (景别 medium-close → close)
                "prompt": (
                    "Shot B, segment 3 of 3, CONTINUATION of the same take, final "
                    "segment. From this still position the camera glides slowly "
                    "forward into a close shot of Jialing facing the mirror on her "
                    "right. The eerie reflection still grins inside the bronze mirror. "
                    "The horned shadow still looms behind her. " + ANCHOR + " The shot "
                    "ends on her wide eyes and the grinning reflection side by side."
                ),
                "sound": "low eerie hum continues, then fading",
                "music": "dissonant strings resolve into low silence",
            },
        ],
    },
    {
        "id": "jialing_lantern2_c_fix",  # 改后缀避免 skip 旧输出
        "title": "镜头C 巨影·献灯 (3段修复: 巨影+灯笼摇晃+血滴白光收尾)",
        "weather": (
            "Night inside the same vast ruined gothic castle great hall, the "
            "shattered dome opening to a clouded sky, a colossal faceless black "
            "figure pressing down and eclipsing the pale moon, candle flames "
            "guttering, then an extreme close on the brass lantern before the "
            "blinding white burst floods the frame"
        ),
        "grade": "chiaroscuro, extreme low-key, cold steel-blue, moonlit rim on "
                 "her hair, abruptly overexposed to pure white by the light "
                 "blast at the end, film grain",
        "segs": [
            {
                # seg1: 巨影压下 (低角度仰视, 缓升运镜)
                "prompt": (
                    "Shot C, segment 1 of 3, of ONE continuous take inside the "
                    "same vast ruined gothic castle great hall matching Picture 3. "
                    "Low angle close-medium shot looking up at Jialing, the towering "
                    "vaulted ceiling with shattered dome visible above. She lifts "
                    "her gaze; high above, through the shattered dome, a colossal "
                    "faceless black figure presses down from the clouds, eclipsing "
                    "the pale moon. The camera rises slowly and only by a small "
                    "amount. On the altar the brass lantern's flame gutters "
                    "violently in a wind that moves nothing else. " + ANCHOR + " " + HOLD
                ),
                "sound": "muffled thunder, faint rubble falling, wind gusts",
                "music": "low timpani roll, dread approaching",
            },
            {
                # seg2: 新增 — 同景别, 灯笼火焰猛晃 (运镜静止)
                "prompt": (
                    "Shot C, segment 2 of 3, CONTINUATION of the same take. From "
                    "this held position the camera remains perfectly still in the "
                    "same low-angle close-medium shot — NO dolly, NO rise, NO "
                    "movement of the camera at all. The colossal faceless black "
                    "figure still eclipses the moon above the shattered dome. "
                    "Jialing looks up at it, her face lit by the cold moonlit rim "
                    "and warm amber from the altar. The brass lantern's flame "
                    "on the altar gutters violently, almost extinguished, then "
                    "fights back. " + ANCHOR + " Throughout this segment the "
                    "camera does not move; only the figure, the flame, and the "
                    "drifting dust move."
                ),
                "sound": "muffled thunder louder, strong wind",
                "music": "timpani intensifies, a dread chord sustained",
            },
            {
                # seg3: 新增 — 推近到 extreme close, 血滴灯芯白光爆发
                "prompt": (
                    "Shot C, segment 3 of 3, CONTINUATION of the same take, final "
                    "segment. From this still position the camera glides quickly "
                    "forward into an extreme close shot of Jialing's face and "
                    "the brass lantern. She bites the tip of her right index "
                    "finger and presses one drop of blood onto the lantern wick. "
                    "The wick erupts in a blinding white blaze; a shockwave of "
                    "light floods outward and overexposes the whole frame to pure "
                    "white, ending the shot. " + ANCHOR
                ),
                "sound": "sharp burst, rushing air, then ringing silence",
                "music": "single choir strike, then silence",
            },
        ],
    },
]


def make_shot_entry(seg, img, shot_no):
    subjects = [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/robe/lantern"},
        {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        {"label": SCENE_SUBJECT, "picture": True, "retention": "partially_preserved",
         "picture_retention": "partially_preserved",
         "note": "scene geometry anchor: keep altar in center, broken pillar on right, "
                 "vaulted ceiling, gothic windows; allow lighting/action variation"},
    ]
    ref_list = [img, img, IMG_SCENE]  # 改: 加场景图作 Picture 3
    action = (
        f"{seg['prompt']}\n"
        f"Scene and weather: {SHOTS_BY_ID[seg.get('_shot_id')]['weather']}.\n"
        f"Color grade: {SHOTS_BY_ID[seg.get('_shot_id')]['grade']}."
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


SHOTS_BY_ID = {s["id"]: s for s in SHOTS}


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default=None,
                    help="只输出指定 set id (如 jialing_lantern2_a_fix)")
    ap.add_argument("--out", default=None,
                    help="manifest 输出文件名 (默认 lantern_hybrid_manifest.json)")
    args = ap.parse_args()

    selected = SHOTS
    if args.only:
        selected = [s for s in SHOTS if s["id"] == args.only]
        if not selected:
            print(f"[FATAL] --only {args.only} 未匹配任何 set")
            sys.exit(1)

    sets = []
    n_bad = 0
    total = 0
    for sh in selected:
        img = IMG_JIALING
        entries = []
        for i, seg in enumerate(sh["segs"], start=1):
            seg["_shot_id"] = sh["id"]
            prompt, issues = make_shot_entry(seg, img, i)
            if issues:
                n_bad += 1
                print(f"[FAIL] {sh['id']} seg{i}: {issues}")
            else:
                print(f"[OK]   {sh['id']} seg{i}")
            entries.append({
                "shot": i,
                "storyboard": img,
                "character": img,
                "scene": IMG_SCENE,  # 改: 填场景图路径
                "extra_images": [],
                "seconds": 7.0,
                "megapixels": 0.7,
                "prompt": prompt,
            })
            total += 1
        sets.append({
            "id": sh["id"],
            "title": sh["title"],
            "shots": entries,
        })

    manifest = {
        "comfy_url": "http://100.67.139.74:8188",
        "workflow": "workflows/h3_r2v_motion_context_api.json",
        "base_dir": "shots",
        "sets": sets,
    }
    out_name = args.out or "lantern_hybrid_manifest.json"
    out = ROOT / "shots" / out_name
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    per = [len(s["shots"]) for s in sets]
    print(f"\nmanifest -> {out}  ({len(sets)} 镜头 × {per} 段 = {total} 段, 每镜 {per[0]*7}s, 合计约 {total*7}s)")
    print(f"校验: {total - n_bad}/{total} 段通过")


if __name__ == "__main__":
    main()
