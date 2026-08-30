# -*- coding: utf-8 -*-
"""
欧美暗黑风电影质感 专项测试批次生成器
输出: shots/dark_film_manifest.json
- 8 镜: 哥特城堡/烛光仪式/迷雾提灯/魔镜幻象/老街黑影/影子变身/巨影降临/黑暗凝视
- 720p(megapixels=0.7), 6s 短镜, 一镜一个暗黑核心画面
- 风格参考: 毛白技能包 "暗黑哥特, 荒野古堡废墟, 满月枯树林" / "暗黑神秘, 戏剧化, 强光影"
- 全部单角色, 规避双人同框/镜像依赖/大流体/大尺度运镜等已知弱项
- 02/05 带 scene 参考图(礼堂/老街), 其余纯文字
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_XIAOLE = "../characters/xiaole_wizard/reference.jpg"
IMG_HALL = "../scenes/hogwarts_old_hall.png"
IMG_STREET = "../scenes/hk_old_street_night.png"

JIALING_SUBJECT = (
    "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, cool detached big-sister aura, wearing "
    "Hogwarts style dark robe, red and yellow striped scarf, grey pleated skirt"
)
JIALING_CU_SUBJECT = (
    "the same 17-year-old girl in a close-up portrait, wavy auburn-red hair, "
    "Asian oval face, single eyelids, red and yellow striped scarf"
)
XIAOLE_SUBJECT = (
    "a 7-year-old Chinese schoolboy with short black hair, round glasses, lively "
    "curious face, wearing a dark wizard robe and round glasses"
)
XIAOLE_CU_SUBJECT = (
    "the same 7-year-old boy in a close-up portrait, short black hair, round glasses, "
    "dark wizard robe"
)
HALL_SUBJECT = (
    "the old candle-lit Hogwarts-style hall shown in Picture 3, dark stone walls, "
    "long wooden tables, floating candles, warm amber lighting"
)
STREET_SUBJECT = (
    "the night city street shown in Picture 3, wet asphalt reflecting neon, "
    "narrow old street with signboards, thin mist"
)

SHOTS = [
    {
        "name": "dark_01_castle",
        "title": "01 哥特·古堡满月 嘉玲剪影",
        "char": "jialing",
        "scene": None,
        "action": (
            "Extreme wide shot of a ruined gothic castle on a hill under a full "
            "moon, dead trees on the hillside, thick ground fog rolling low. "
            "Jialing matching Picture 1 is a small dark silhouette on the stone "
            "path far below, a tiny warm lantern glowing in her hand, walking "
            "toward the castle gates. The moon is huge and pale behind the broken "
            "towers, her silhouette stays small and distant, the fog creeps across "
            "the path in slow waves. Shot like the opening frame of a gothic "
            "horror film."
        ),
        "weather": (
            "Night, enormous pale full moon, rolling ground fog, dead bare trees, "
            "cold blue-black palette, one tiny warm lantern light far below"
        ),
        "grade": "high-contrast desaturated blue-black grade, heavy film grain, "
                "gothic horror atmosphere",
        "dialogue": "",
        "sound": "low wind over the moor, distant owl, faint crunch of footsteps",
        "music": "slow cello drone, dark and ominous",
    },
    {
        "name": "dark_02_ritual",
        "title": "02 仪式·烛光暗室 嘉玲",
        "char": "jialing",
        "scene": IMG_HALL,
        "action": (
            "Medium shot inside the dark hall matching Picture 3, now nearly black "
            "except for a ring of candles on a stone table. Jialing matching "
            "Picture 1 stands behind the table, both hands raised over an old "
            "leather-bound book that floats an inch above the wood, its pages "
            "turning by themselves. A sickly green-black light seeps from the "
            "book and glows up across her face and hands, the candle flames lean "
            "toward her, shadows on the stone walls writhe behind her. She "
            "whispers and the book snaps shut, the glow dying, candle flames "
            "straighten. Dark magic ritual, dramatic and controlled."
        ),
        "weather": (
            "Nearly black stone hall, ring of candlelight, one floating book "
            "glowing sickly green-black, deep shadows, dust motes in the beam"
        ),
        "grade": "extreme low-key chiaroscuro, green-black glow against warm "
                "candlelight, heavy grain",
        "dialogue": "……禁。",
        "sound": "candles hissing, pages rustling, low arcane hum, a hard snap",
        "music": "low drone with dissonant strings, ritualistic",
    },
    {
        "name": "dark_03_fog",
        "title": "03 惊悚·迷雾提灯 嘉玲",
        "char": "jialing",
        "scene": None,
        "action": (
            "Medium close-up tracking with Jialing matching Picture 1 as she "
            "walks alone through dense fog in a dark forest at night, holding a "
            "brass lantern up at chest height. The warm lantern light carves her "
            "face out of the darkness, her eyes scanning nervously ahead. Behind "
            "her, deep in the fog, a tall dark human-shaped shadow briefly appears "
            "between the trees and is gone before she turns. The camera drifts "
            "forward with her, the fog swirls around the lantern glow, her "
            "footsteps echo on wet ground. Tense, dread-building."
        ),
        "weather": (
            "Black forest at night, thick rolling fog, one warm lantern glow "
            "illuminating her face, a faint dark figure far behind in the mist"
        ),
        "grade": "deep blacks with warm lantern falloff on the face, cold blue "
                "background, grain",
        "dialogue": "……有人在看我。",
        "sound": "wet footsteps, fog-damp silence, a soft distant branch snap",
        "music": "tense low strings, sparse piano notes",
    },
    {
        "name": "dark_04_mirror",
        "title": "04 幻象·魔镜 嘉玲",
        "char": "jialing",
        "scene": None,
        "action": (
            "Close-up on an antique oval mirror standing in a dim room. Jialing "
            "matching Picture 1 approaches it and looks into the glass. Her own "
            "reflection gazes back, then the reflection slowly changes: her face "
            "starts to twist into something wrong, the eyes turning hollow and "
            "black, the mouth widening too far, the reflection smiling when she "
            "is not. She flinches and steps back, raising a hand to the glass, "
            "and in that instant the mirror shows only her normal face again. "
            "The reflection change is gradual and uncanny, not a jump cut."
        ),
        "weather": (
            "Dark dusty room, one cold beam of moonlight on the mirror, the room "
            "behind her in shadow, the reflection glowing faintly"
        ),
        "grade": "moonlit silver-blue grade, high contrast on the mirror glass, "
                "subtle grain",
        "dialogue": "……你是谁？",
        "sound": "slow creaking floorboards, a low thrum as the reflection shifts",
        "music": "high eerie strings, glissando harp",
    },
    {
        "name": "dark_05_street",
        "title": "05 夜街·雨夜黑影 小乐",
        "char": "xiaole",
        "scene": IMG_STREET,
        "action": (
            "Medium-wide shot on the rain-soaked night street matching Picture 3. "
            "Xiao Le matching Picture 1 stands alone under a streetlight, rain "
            "slanting through the neon glow, wet asphalt reflecting red and blue "
            "signs. He turns his head slowly, searching the empty street. Far at "
            "the end of the road a dark figure passes under a flickering sign, "
            "too fast, gone into the mist. Xiao Le grips his wand, frozen. "
            "Neo-noir horror atmosphere, neon reflecting on the wet ground."
        ),
        "weather": (
            "Rainy night, wet neon-reflecting asphalt, one streetlight pool of "
            "light, thin mist, a distant flickering sign"
        ),
        "grade": "cyan-red neon noir grade, wet reflections, deep shadows, grain",
        "dialogue": "……谁在那儿？",
        "sound": "steady rain, neon buzz, wet footsteps, a distant rumble",
        "music": "synth bass pulse, suspenseful",
    },
    {
        "name": "dark_06_shadow",
        "title": "06 特效·影子异变 嘉玲",
        "char": "jialing",
        "scene": None,
        "action": (
            "Medium shot, wide angle from the side. Jialing matching Picture 1 "
            "stands before a bare stone wall lit by a single overhead candle. "
            "Her shadow stretches across the wall, then begins to grow on its "
            "own: the shadow rises taller and taller, arms spreading wide until "
            "it becomes the looming silhouette of a horned giant creature, far "
            "bigger than she is. She notices and turns to look at the wall; the "
            "shadow is still the shape of a horned monster. She steps toward the "
            "wall and the shadow steps with her, back to normal. The shadow "
            "transforms smoothly on the wall surface."
        ),
        "weather": (
            "Dark bare stone wall, single warm candle flame, the wall otherwise "
            "in black shadow, high contrast"
        ),
        "grade": "extreme chiaroscuro, warm light against pure black, heavy grain",
        "dialogue": "……不是我。",
        "sound": "candle crackle, a low bass swell as the shadow grows, silence",
        "music": "low organ drone, dread-building",
    },
    {
        "name": "dark_07_giant",
        "title": "07 压迫·巨影降临 嘉玲",
        "char": "jialing",
        "scene": None,
        "action": (
            "Low-angle wide shot. Jialing matching Picture 1 stands in an open "
            "moor under a dark sky, tiny at the bottom of frame. Above her a "
            "gigantic shadowy humanoid form looms out of the cloud layer, "
            "blocking the moon, its head and shoulders towering into the sky, "
            "no face, just pure darkness with ragged edges, thin tendrils of "
            "darkness reaching down toward the ground. It descends slowly, "
            "overwhelming the frame, and she looks up at it, cloak whipping. "
            "The scale is the horror: the giant shadow dwarfs the landscape."
        ),
        "weather": (
            "Overcast night moor, dark sky, one enormous black humanoid form "
            "descending through the clouds, wind, thin fog"
        ),
        "grade": "huge scale contrast, deep blacks, cold desaturated grade, grain",
        "dialogue": "……",
        "sound": "low rumbling, wind howling across the moor, a rising sub-bass",
        "music": "massive low brass and choir, apocalyptic",
    },
    {
        "name": "dark_08_gaze",
        "title": "08 特写·黑暗凝视 嘉玲",
        "char": "jialing",
        "scene": None,
        "action": (
            "Extreme close-up on Jialing matching Picture 1's eye in darkness. "
            "Her eye is lit by a faint cold green glow from below, the iris "
            "shifts, a reflection of a candle flame flickering inside her pupil. "
            "The camera holds perfectly still, her eyelid slowly closes then "
            "opens again, and in the brief blink the green light in her eye "
            "turns black. Her expression behind the eye is calm and unreadable. "
            "A slow, oppressive final image, like the closing shot of a gothic "
            "thriller."
        ),
        "weather": (
            "Total darkness around, one faint cold green light raking across her "
            "eye and cheekbones, a candle reflection in her pupil"
        ),
        "grade": "single cold key light on the eye, rest in black, fine grain",
        "dialogue": "",
        "sound": "silence, a single slow heartbeat, faint wind",
        "music": "minimal piano note, held, fading",
    },
]


def build_subjects(sh):
    if sh["char"] == "jialing":
        base = [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    else:
        base = [
            {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/robe"},
            {"label": XIAOLE_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    if sh.get("scene") == IMG_HALL:
        base.append({"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
                     "picture_retention": "partially_preserved", "note": "the dark hall, lighting reacts to the ritual glow"})
    elif sh.get("scene") == IMG_STREET:
        base.append({"label": STREET_SUBJECT, "picture": True, "retention": "partially_preserved",
                     "picture_retention": "partially_preserved", "note": "the night street, neon reacts to the rain"})
    return base


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING if sh["char"] == "jialing" else IMG_XIAOLE
        subjects = build_subjects(sh)
        ref_list = [img, img] + ([sh["scene"]] if sh["scene"] else [])
        action = (
            f"{sh['action']}\n"
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
        if issues:
            n_bad += 1
            print(f"[FAIL] {sh['name']}  {sh['title']}")
            for it in issues:
                print("   - " + it)
        else:
            print(f"[OK]   {sh['name']}  {sh['title']}")

        sets.append({
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": img,
                    "character": img,
                    "scene": sh["scene"],
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
    out = ROOT / "shots" / "dark_film_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
