# -*- coding: utf-8 -*-
"""
嘉玲 人物互动 × 天气色调 测试批次生成器
输出: shots/jialing_cast_manifest.json
- 6 镜: 在天气/色调氛围基础上加入第二角色(小乐/公鸡)或单人独白, 配简单中文对白
- 每镜独立 set, 6s 短镜, 字段语义正确, Picture N 与 refs 按位对应
- 参考图布局:
    单人镜: storyboard=嘉玲主图, character=嘉玲特写, scene=礼堂
    双人镜: storyboard=嘉玲主图, character=小乐,     scene=礼堂
    公鸡镜: storyboard=嘉玲主图, character=嘉玲特写, scene=礼堂, extra=[公鸡]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

# 角色/场景参考图 (相对 base_dir=shots, 需 ../ 前缀)
IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_XIAOLE = "../characters/xiaole_daily/reference.jpg"
IMG_ROOSTER = "../characters/rooster/reference.png"
IMG_HALL = "../scenes/hogwarts_old_hall.png"

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
ROOSTER_SUBJECT = (
    "a realistic large red rooster, big jagged bright red comb, orange-red chest and "
    "neck feathers, deep green metallic tail feathers, sturdy legs with spurs"
)
HALL_SUBJECT = (
    "an old Hogwarts style magic school hall: ancient stone walls, tall arched windows "
    "with amber stained glass, floating candles, long wooden tables, softly blurred "
    "behind the characters, NOT a plain white background"
)

# 单镜配置: 互动类型, 天气色调描述, 动作画面, 对白, 音效, 配乐
SHOTS = [
    {
        "name": "cast_00_rain_xiaole",
        "title": "00 雨天·躲雨(嘉玲+小乐)",
        "weather": (
            "Heavy rain patters against the tall arched windows, rain streaks running "
            "down the glass, grey overcast daylight dimming the hall, cool damp "
            "atmosphere, puddles of grey light on the stone floor"
        ),
        "grade": "overcast desaturated grey-blue color grade, melancholic rainy mood",
        "cast": "duo",
        "action": (
            "Medium shot. Xiao Le, the small boy with glasses in a red cardigan matching "
            "Picture 2, bursts in from the rain-soaked doorway, shaking water from his "
            "hair, breathless. Jialing stands by the door, arms crossed, cool detached "
            "face matching Picture 1, watching him, then pulls out a handkerchief and "
            "offers it. Her face stays cold but her eyes soften just a little."
        ),
        "dialogue": "小乐：嘉玲姐！淋湿了淋湿了！\n嘉玲：……毛毛躁躁的。拿着擦擦。",
        "sound": "steady rain pattering on the roof and windows, distant low thunder",
        "music": "slow sparse piano, rain-soaked but warm at the edges",
    },
    {
        "name": "cast_01_sunny_solo",
        "title": "01 晴天·窗边独白(嘉玲单人)",
        "weather": (
            "Bright warm morning sunlight streams through the tall arched windows, "
            "golden sunbeams and dust motes floating in the air, the hall glowing "
            "warm amber-gold"
        ),
        "grade": "warm golden color grade, sunny and optimistic",
        "cast": "solo",
        "action": (
            "Close-up. Jialing leans beside the sunlit window, golden light washing "
            "over her face matching Picture 1, her cool eyes drifting to the far "
            "distance, a rare hint of softness and missing someone crossing her face "
            "as she murmurs quietly to herself, lips moving slightly."
        ),
        "dialogue": "嘉玲：天气这么好……你要是还在，该多好。",
        "sound": "faint birdsong outside, soft warm breeze, gentle hall ambience",
        "music": "bright warm acoustic guitar, gentle and nostalgic",
    },
    {
        "name": "cast_02_snow_xiaole",
        "title": "02 雪天·雪球偷袭(嘉玲+小乐)",
        "weather": (
            "Soft snowflakes drift past the windows and float inside near the glass, "
            "the hall lit by cold pale winter daylight, frost-white and quiet, "
            "a hush of snowy stillness in the air"
        ),
        "grade": "cool white-blue color grade, winter cold and playful",
        "cast": "duo",
        "action": (
            "Medium shot. Xiao Le matching Picture 2 sneaks up behind a window holding "
            "a fluffy snowball, grinning mischievously, arm raised ready to throw. "
            "Jialing matching Picture 1 slowly turns her head, one eyebrow raised, "
            "cold gaze pinning him in place. Xiao Le freezes mid-throw with an awkward "
            "sheepish smile, snowball dripping in his hand."
        ),
        "dialogue": "小乐：嘿……嘉玲姐，你先别动啊——\n嘉玲：……你敢。",
        "sound": "soft wind, muffled snowy quiet, faint flakes brushing the glass",
        "music": "light crystalline chimes, icy and mischievous",
    },
    {
        "name": "cast_03_candle_rooster",
        "title": "03 烛光·纸鹤变身(嘉玲+公鸡)",
        "weather": (
            "Close warm candlelight flickers across the room, deep amber-red glow, "
            "firelight dancing, soft shadows flickering on the stone walls, "
            "intimate warm darkness"
        ),
        "grade": "warm amber-red candlelight color grade, intimate and cozy",
        "cast": "rooster",
        "action": (
            "Close-up. On a candlelit wooden table, a paper crane suddenly transforms "
            "into a big realistic red rooster matching Picture 4, which crows loudly "
            "and flaps onto the tabletop, feathers ruffled. Jialing matching Picture 1 "
            "watches with one eyebrow raised, half amused half exasperated, cool and "
            "unfazed."
        ),
        "dialogue": "公鸡：喔喔喔——\n嘉玲：……又是你。变回去。",
        "sound": "crackling fire, soft air, a loud rooster crow",
        "music": "gentle vintage jazz, playful and intimate",
    },
    {
        "name": "cast_04_neon_solo",
        "title": "04 霓虹雨夜·独白(嘉玲单人)",
        "weather": (
            "Electric neon light leaks through rain-streaked windows in magenta and "
            "cyan bars, colored reflections sweeping across the dark hall, synthetic "
            "cyberpunk glow mixing with the candlelight, rain sliding down the glass"
        ),
        "grade": "high-contrast magenta-cyan neon color grade",
        "cast": "solo",
        "action": (
            "Close-up. Jialing matching Picture 1 looks out a rain-streaked window, "
            "magenta and cyan neon reflections sliding across her cool face, eyes "
            "slightly unfocused, voice low and quiet as she speaks one line to herself."
        ),
        "dialogue": "嘉玲：这城市真吵。……可也比一个人待着强。",
        "sound": "steady rain on glass, distant electronic hum, city buzz",
        "music": "synthesizer pads, neon-lit melancholic vibe",
    },
    {
        "name": "cast_05_fog_xiaole",
        "title": "05 雾天·雾中呼唤(嘉玲+小乐)",
        "weather": (
            "Thick grey fog drifts through the hall, hazy and veiled, volumetric light "
            "piercing the mist in pale shafts, edges of the room dissolving into fog"
        ),
        "grade": "muted teal-grey color grade, dreamy and hazy",
        "cast": "duo",
        "action": (
            "Medium shot. Thick fog swirls through the hall, Xiao Le matching Picture 2 "
            "runs ahead, his small silhouette already fading into the mist, laughing. "
            "Jialing matching Picture 1 stands behind, calling after him, cool tone "
            "with a hint of worry beneath."
        ),
        "dialogue": "嘉玲：小乐，别跑远了。雾这么大。\n小乐：知道啦——马上回来！",
        "sound": "muffled distant sounds, soft damp air, echo in the fog",
        "music": "ambient drones, slow and dreamlike",
    },
]


def build_subjects(cast: str):
    """按互动类型组装 subjects 列表(顺序 = Picture N = refs 顺序)。"""
    if cast == "duo":
        return [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/cardigan"},
            {"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
             "picture_retention": "partially_preserved", "note": "blurred background, lighting changes with weather"},
        ]
    if cast == "rooster":
        return [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
            {"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
             "picture_retention": "partially_preserved", "note": "blurred background, lighting changes with weather"},
            {"label": ROOSTER_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "realistic rooster matching Picture 4"},
        ]
    # solo
    return [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
        {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        {"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
         "picture_retention": "partially_preserved", "note": "blurred background, lighting changes with weather"},
    ]


def build_refs(cast: str):
    """storyboard/character/scene/extra 映射, 顺序必须与 subjects/Picture 对齐。"""
    if cast == "duo":
        return {"storyboard": IMG_JIALING, "character": IMG_XIAOLE, "scene": IMG_HALL, "extra": []}
    if cast == "rooster":
        return {"storyboard": IMG_JIALING, "character": IMG_JIALING, "scene": IMG_HALL, "extra": [IMG_ROOSTER]}
    return {"storyboard": IMG_JIALING, "character": IMG_JIALING, "scene": IMG_HALL, "extra": []}


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        subjects = build_subjects(sh["cast"])
        refs = build_refs(sh["cast"])
        ref_list = [refs["storyboard"], refs["character"], refs["scene"]] + refs["extra"]
        action = (
            f"{sh['action']}\n"
            f"Weather and lighting: {sh['weather']}.\n"
            f"Color grade: {sh['grade']}."
        )
        shot = dict(sh)
        shot["action"] = action
        shot["sound"] = sh["sound"]
        shot["music"] = sh["music"]
        shot["dialogue"] = sh["dialogue"]
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
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": refs["storyboard"],
                    "character": refs["character"],
                    "scene": refs["scene"],
                    "extra_images": refs["extra"],
                    "seconds": 6.0,
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
    out = ROOT / "shots" / "jialing_cast_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
