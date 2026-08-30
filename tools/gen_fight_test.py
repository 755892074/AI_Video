# -*- coding: utf-8 -*-
"""
嘉玲 × 小乐 近战打斗测试批次
输出: shots/fight_test_manifest.json
- 2 镜 × 6s × 720p(0.7MP), 单镜(无 chain 首段)
- 双人同框: 参考 gen_jialing_cast.py 的 duo 模式
  storyboard=嘉玲, character=小乐, scene=哥特厅; 两角色都带 Picture
- 规避 H3 双人分身: 体型差大(少女 vs 7岁男童), 服装色差大(黑袍 vs 红毛衣),
  动作清晰可读, 一次一个动作, 距离明确
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_XIAOLE = "../characters/xiaole_daily/reference.jpg"
IMG_HALL = "../scenes/lantern_hall_v2.png"

JIALING_SUBJECT = (
    "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, solemn fierce expression, wearing a "
    "black floor-length hooded robe, in fighting stance"
)
XIAOLE_SUBJECT = (
    "a 7-year-old Chinese boy in an elementary school uniform of a red patterned "
    "cardigan over a dark top, blue jeans, sneakers, clear-frame round glasses, "
    "short black hair, agile nimble small body, in fighting stance"
)
HALL_SUBJECT = (
    "the vast ruined gothic castle great hall shown in Picture 1: carved stone "
    "altar in center foreground, deep perspective with two rows of stone columns "
    "vanishing into distant background, towering vaulted ceiling with broken dome, "
    "gothic arched windows on left wall, broken stone pillar on right with candelabras"
)

SHOTS = [
    {
        "name": "fight_01_faceoff_clash",
        "title": "打斗·对峙到近身交锋",
        "action": (
            "Medium-wide shot inside the vast ruined gothic hall matching Picture 3. "
            "Jialing matching Picture 1 and Xiaole matching Picture 2 face off in the "
            "center foreground. Jialing is a tall 17-year-old girl in a black hooded "
            "robe; Xiaole is a small 7-year-old boy in a red cardigan with round glasses, "
            "his head barely reaching her chest. They circle each other slowly, "
            "candlelight flickering, dust drifting. Jialing steps in and throws a fast "
            "open-palm strike; Xiaole ducks low, slides under her arm and kicks at her "
            "shin. Jialing hops back, then they clash again: she grabs his collar with "
            "one hand, he grips her wrist and twists, both locked in a brief struggle. "
            "The movements are clear and crisp, the two bodies always clearly separated "
            "and distinct, her black robe against his red cardigan, readable motion, "
            "not blurred. No one speaks."
        ),
        "weather": "dark gothic hall, candlelight pools, swirling dust, long shadows",
        "grade": "warm candle amber, deep blacks, high contrast, fine grain",
        "sound": "footsteps on stone, cloth rustle, a soft grunt, candle crackle",
        "music": "tense percussion, low drums building",
    },
    {
        "name": "fight_02_lock_breakaway",
        "title": "打斗·锁腕挣脱拉开距离",
        "action": (
            "Medium close-up shot inside the ruined gothic hall matching Picture 3. "
            "Jialing matching Picture 1 has Xiaole matching Picture 2's right wrist "
            "locked in her grip, both bent low. Xiaole pulls back hard, spins around, "
            "and breaks free, staggering two steps away, breathing hard. Jialing steps "
            "after him, but he raises one hand palm-out and she stops; both stare at "
            "each other, the fight paused mid-beat. He adjusts his glasses with a small "
            "grin. The two bodies remain clearly distinct and sharp, her black robe "
            "versus his red cardigan, faces readable. The camera holds on both, then "
            "slowly racks focus from her face to his."
        ),
        "weather": "dark gothic hall, one candle pool lighting the pair, dust settling",
        "grade": "warm amber key light, deep shadows, crisp edges, grain",
        "sound": "shoes scuffing stone, heavy breathing, a faint chuckle, candle crackle",
        "music": "low strings, a single soft drum hit, then silence",
    },
]


def build_subjects():
    """duo 模式: 两角色 + 场景 都带 picture, 顺序=Picture 编号=refs 顺序"""
    return [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/black robe"},
        {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/red cardigan/small body"},
        {"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
         "picture_retention": "partially_preserved", "note": "scene geometry anchor, keep the vast hall"},
    ]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        subjects = build_subjects()
        ref_list = [IMG_JIALING, IMG_XIAOLE, IMG_HALL]
        action = (
            f"{sh['action']}\n"
            f"Weather and lighting: {sh['weather']}.\n"
            f"Color grade: {sh['grade']}."
        )
        shot = dict(sh)
        shot["action"] = action
        shot["dialogue"] = None
        shot["speaker"] = "S1, S2"
        prompt = build_prompt(shot, subjects)
        issues = check_prompt(prompt, ref_list)
        if issues:
            n_bad += 1
            print(f"[FAIL] {sh['name']}  {sh['title']}")
            for it in issues:
                print("   - " + it)
        else:
            print(f"[OK]   {sh['name']}  {sh['title']}")

        sets.append({
            "id": sh["name"],
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": IMG_JIALING,
                    "character": IMG_XIAOLE,
                    "scene": IMG_HALL,
                    "extra_images": [],
                    "seconds": 6.0,
                    "megapixels": 0.7,
                    "prompt": prompt,
                }
            ],
        })

    manifest = {
        "comfy_url": "http://100.67.139.74:8188",
        "workflow": "workflows/h3_r2v_motion_context_api.json",
        "base_dir": "shots",
        "sets": sets,
    }
    out = ROOT / "shots" / "fight_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
