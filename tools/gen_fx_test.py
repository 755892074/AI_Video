# -*- coding: utf-8 -*-
"""
物理 × 特效 专项测试批次生成器
输出: shots/fx_test_manifest.json
- 8 镜: 物理类 4 镜(布料/掉落/液体/抛体) + 特效类 4 镜(火球/闪电/星尘/变形)
- 720p(megapixels=0.7), 6s 短镜, 一镜一个核心物理/特效事件
- 规避已知弱项: 不用 orbit; 液体只用小规模(水花/水球), 避免大水体; 无文字要求
- 部分镜头带 scene 参考图(hogwarts_old_hall / hk_old_street_night)测"场景+特效"融合,
  部分纯文字, 对比 scene ref 对特效镜头的作用
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_XIAOLE = "../characters/xiaole_daily/reference.jpg"
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
    "curious face, wearing a red printed cardigan over a shirt, dark jeans, sneakers"
)
XIAOLE_CU_SUBJECT = (
    "the same 7-year-old boy in a close-up portrait, short black hair, round glasses, "
    "red printed cardigan"
)

SHOTS = [
    # ================= 物理类 =================
    {
        "name": "fx_00_cloth",
        "title": "00 物理·布料风 嘉玲/礼堂",
        "char": "jialing",
        "scene": IMG_HALL,
        "action": (
            "Medium shot inside an old candle-lit Hogwarts hall matching Picture 3. "
            "A sudden gust of magical wind sweeps through the hall: Jialing matching "
            "Picture 1 stands still while her dark robe hem, her red and yellow scarf "
            "and her wavy auburn hair all billow and stream sideways in the wind, "
            "fabric rippling and fluttering naturally, candle flames along the walls "
            "leaning and flickering, then the wind dies down and everything settles "
            "back. The cloth movement is smooth and continuous, driven by the same "
            "single gust."
        ),
        "weather": (
            "Dim candle-lit stone hall, dust motes in the air, one strong gust of "
            "wind passing through, warm amber glow"
        ),
        "grade": "warm candlelit amber grade, old-magic atmosphere",
        "dialogue": "……风好大。",
        "sound": "wind whoosh through stone corridors, fabric flapping, candles sputtering",
        "music": "low ambient drone with airy flute, mysterious",
    },
    {
        "name": "fx_01_drop",
        "title": "01 物理·重力掉落 嘉玲/无场景",
        "char": "jialing",
        "scene": None,
        "action": (
            "Close-up on Jialing matching Picture 1 standing in a plain grey stone "
            "courtyard, she lifts a small brass key ring with two keys on a metal "
            "ring and lets it go. The keys fall straight down under gravity, "
            "turning slightly and glinting as they tumble, then hit the stone "
            "ground with a small clatter and bounce once before lying still. The "
            "camera follows the keys down, the fall is smooth and continuous with "
            "natural acceleration, Jialing's hand stays in frame at the top."
        ),
        "weather": (
            "Overcast soft daylight, plain grey courtyard, no wind, muted tones"
        ),
        "grade": "neutral realistic grade, clean and simple",
        "dialogue": "……掉了。",
        "sound": "small metal jingle as it falls, a clear clatter on stone, one bounce",
        "music": "minimal empty air, quiet ticking",
    },
    {
        "name": "fx_02_water",
        "title": "02 物理·水花溅起 小乐/无场景",
        "char": "xiaole",
        "scene": None,
        "action": (
            "Medium shot of a bright kitchen counter. Xiaole matching Picture 1 sits "
            "at the table holding a clear glass of water, he pokes the surface with "
            "one finger and a small crown of water leaps up around his fingertip, "
            "droplets flying in a clean arc and splashing back into the glass and "
            "onto the table, the liquid moves with natural surface tension, ripples "
            "expanding across the glass then calming. Xiaole giggles, pulling his "
            "finger back. The water physics is the whole focus: small, sharp, crisp."
        ),
        "weather": (
            "Bright clean kitchen, warm daylight from a window, no wind, calm room"
        ),
        "grade": "clean bright natural grade, close and crisp",
        "dialogue": "哇——！",
        "sound": "bright water plinks, small splashes, boy giggling",
        "music": "playful plucked strings, light and bouncy",
    },
    {
        "name": "fx_03_proj",
        "title": "03 物理·抛体弧线 小乐/无场景",
        "char": "xiaole",
        "scene": None,
        "action": (
            "Medium shot on a grassy schoolyard. Xiaole matching Picture 1 winds up "
            "and throws a paper airplane forward, the plane launches off his fingers "
            "and glides in a long smooth arc across the frame, dipping and gliding "
            "with real momentum, then lands softly on the grass ahead, he grins and "
            "runs after it. The flight path is one continuous smooth parabola, "
            "never jerky, the camera stays still and follows the plane through the "
            "air."
        ),
        "weather": (
            "Sunny afternoon, soft green grass, light warm breeze, clear blue sky"
        ),
        "grade": "bright airy daylight grade, playful",
        "dialogue": "飞吧！",
        "sound": "paper plane whoosh, grass swish, boy's footsteps, happy laugh",
        "music": "bright ukulele strums, cheerful",
    },
    # ================= 特效类 =================
    {
        "name": "fx_04_fireball",
        "title": "04 特效·火球凝聚 嘉玲/礼堂",
        "char": "jialing",
        "scene": IMG_HALL,
        "action": (
            "Medium shot inside the candle-lit hall matching Picture 3. Jialing "
            "matching Picture 1 holds out her open palm and a fireball ignites "
            "above it: first a small spark, then orange-gold flames swirling and "
            "growing into a glowing orb of fire the size of a fist, tongues of "
            "flame licking and rotating, heat shimmer distorting the air around it, "
            "warm light flickering across her face and the stone walls. The fireball "
            "hovers steadily above her palm, flames constantly in motion but the orb "
            "stable, then she closes her fist and it snuffs out in a puff of smoke."
        ),
        "weather": (
            "Dim candle-lit stone hall, warm amber glow, one blazing fireball "
            "casting moving orange light on the walls"
        ),
        "grade": "high-contrast warm firelight against shadow, magical",
        "dialogue": "……烧起来了。",
        "sound": "soft crackling fire hum, rising whoosh, a puff as it goes out",
        "music": "swelling strings with low brass, dramatic and warm",
    },
    {
        "name": "fx_05_lightning",
        "title": "05 特效·闪电迸发 小乐/老街夜",
        "char": "xiaole",
        "scene": IMG_STREET,
        "action": (
            "Medium shot on a wet night street matching Picture 3. Xiaole matching "
            "Picture 1 points a short toy wand at a metal signpost and a jagged "
            "bolt of blue-white lightning leaps from the wand tip to the signpost, "
            "branching electric arcs crackling and flickering, sparks spraying "
            "onto the wet pavement, the signpost flashes bright for a moment then "
            "the lightning dies with a last few sparks. The electricity is sharp, "
            "branching and fast, ending cleanly."
        ),
        "weather": (
            "Rainy night, wet asphalt reflecting neon, thin mist, one dazzling "
            "blue-white lightning bolt, flickering signpost glow"
        ),
        "grade": "cyan-blue neon grade, electric and punchy",
        "dialogue": "电！",
        "sound": "sharp electric crackle, buzz, sizzling on wet ground",
        "music": "electric guitar stab, then tense synth pulse",
    },
    {
        "name": "fx_06_stardust",
        "title": "06 特效·星尘环绕 嘉玲/无场景",
        "char": "jialing",
        "scene": None,
        "action": (
            "Medium shot of Jialing matching Picture 1 standing on a plain dark "
            "stage, she raises both arms and golden star-dust particles pour out of "
            "her palms, spiraling up around her body in a smooth helix, thousands of "
            "tiny glowing specks swirling faster and higher until they fill the air "
            "above her head like a glittering nebula, then slowly fading like "
            "spent sparks. The particles stream continuously along a spiral path, "
            "never erratic, her robe and hair barely moving."
        ),
        "weather": (
            "Dark empty stage, one soft spotlight on her, golden particles glowing "
            "against pure black, gentle haze"
        ),
        "grade": "black and gold grade, magical and dreamy",
        "dialogue": "真漂亮……",
        "sound": "soft crystalline shimmer, airy chime, gentle hum",
        "music": "celestial harp arpeggios, ethereal",
    },
    {
        "name": "fx_07_transform",
        "title": "07 特效·南瓜变形 小乐/无场景",
        "char": "xiaole",
        "scene": None,
        "action": (
            "Close-up on a small orange pumpkin sitting on a wooden table. Xiaole "
            "matching Picture 1 leans in and waves his hand over it; the pumpkin "
            "begins to glow and morph, its skin rippling, then it transforms into a "
            "small glassy blue orb that hovers an inch above the table, pulsing "
            "with soft light, then settles back down onto the wood and dims to a "
            "faint glow. The transformation is continuous and smooth, one object "
            "shifting into another without a jump cut, Xiaole's face lit blue in "
            "the light."
        ),
        "weather": (
            "Cozy dim room, warm wooden table, one glowing blue orb casting cool "
            "light on Xiaole's face and hands"
        ),
        "grade": "warm wood tones against cool blue magic light, cozy and wondrous",
        "dialogue": "变！",
        "sound": "soft magical hum rising, a gentle shimmering chime, quiet thud as it lands",
        "music": "magical celesta melody, wondrous",
    },
]


HALL_SUBJECT = (
    "the old candle-lit Hogwarts-style hall shown in Picture 3, dark stone walls, "
    "long wooden tables, floating candles, warm amber lighting"
)
STREET_SUBJECT = (
    "the night city street shown in Picture 3, wet asphalt reflecting neon, "
    "narrow old street with signboards, thin mist"
)


def build_subjects(char: str, scene: str = None):
    base = [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
        {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
    ] if char == "jialing" else [
        {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/cardigan"},
        {"label": XIAOLE_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
    ]
    if scene == IMG_HALL:
        base.append({"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
                     "picture_retention": "partially_preserved", "note": "blurred background, lighting changes with the magic"})
    elif scene == IMG_STREET:
        base.append({"label": STREET_SUBJECT, "picture": True, "retention": "partially_preserved",
                     "picture_retention": "partially_preserved", "note": "background street, lighting reacts to the lightning"})
    return base


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING if sh["char"] == "jialing" else IMG_XIAOLE
        subjects = build_subjects(sh["char"], sh.get("scene"))
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
    out = ROOT / "shots" / "fx_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s, "
          f"megapixels={sets[0]['shots'][0]['megapixels']})")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
