# -*- coding: utf-8 -*-
"""
嘉玲/小乐 单人电影场景 × 景别运镜 测试批次生成器
输出: shots/jialing_scene_manifest.json
- 8 镜: 每镜单人角色(嘉玲/小乐) + 不同天气 + 不同景别/运镜 + 纯文字描述的电影场景
- 无场景参考图(scene=None), 背景全部由文字驱动; 参考图仅锁角色身份(角色图 x2)
- 6s 短镜, 每镜独立 set, 字段语义正确
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_XIAOLE = "../characters/xiaole_daily/reference.jpg"

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
    {
        "name": "scene_00_rain_ally",
        "title": "00 雨夜街角·嘉玲 中景+横摇",
        "char": "jialing",
        "action": (
            "Medium shot, camera slowly panning right across a rain-slicked old town "
            "street at night, neon signs reflected in wet asphalt, sparse pedestrians "
            "hurrying past with umbrellas. Jialing matching Picture 1 stands alone at "
            "the street corner waiting for a bus, the cool rain dampening her hair, "
            "she pulls her scarf tighter and looks down the empty road."
        ),
        "weather": (
            "Heavy night rain, wet glistening streets, blurred neon reflections in "
            "magenta and cyan, city lights bokeh in the background"
        ),
        "grade": "cold blue night with neon accents, cinematic rain film look",
        "dialogue": "……车怎么还不来。",
        "sound": "steady rain, distant traffic, wet footsteps",
        "music": "slow sparse piano under rain noise",
    },
    {
        "name": "scene_01_snow_ally",
        "title": "01 雪原车站·嘉玲 远景+缓推",
        "char": "jialing",
        "action": (
            "Extreme wide shot of a snowbound country train station, thick snow "
            "blanketing the platform and tracks, steam hissing from the locomotive, "
            "snowflakes drifting in the still air. Jialing matching Picture 1 stands at "
            "the far end of the platform holding a small suitcase, a tiny dark figure "
            "in the white expanse, camera slowly pushing in on her as she exhales a "
            "breath of white fog."
        ),
        "weather": (
            "Heavy snowfall, thick white drifts, cold pale winter light, steam mixing "
            "with falling snow, muted frosty palette"
        ),
        "grade": "cold white-blue cinematic grade, lonely winter atmosphere",
        "dialogue": "到了。",
        "sound": "muffled snow silence, distant train steam, soft wind",
        "music": "minimal ambient strings, icy and quiet",
    },
    {
        "name": "scene_02_sunset_ling",
        "title": "02 海边日落·小乐 中近景+环绕",
        "char": "xiaole",
        "action": (
            "Medium close-up, camera slowly arcing around Xiao Le matching Picture 3 "
            "as he crouches on a golden beach at low tide, waves retreating in the "
            "background, warm sunset light catching his round glasses. He picks up a "
            "shiny seashell and looks up, mouth opening in delight, sparkling sand "
            "stuck to his knees."
        ),
        "weather": (
            "Golden hour sunset over the sea, warm orange and pink sky, gentle waves, "
            "glittering wet sand, long soft shadows"
        ),
        "grade": "warm golden-hour film grade, nostalgic seaside vibe",
        "dialogue": "哇！这个贝壳会发光！",
        "sound": "gentle waves, sea breeze, distant seagulls",
        "music": "bright ukulele, warm and playful",
    },
    {
        "name": "scene_03_fog_ally",
        "title": "03 雾中山路·嘉玲 近景+拉远",
        "char": "jialing",
        "action": (
            "Close-up on Jialing matching Picture 1, her face half-veiled in morning "
            "mist, a bicycle leaning beside her, then camera slowly pulling back to "
            "reveal a winding mountain road swallowed by thick fog, road signs fading "
            "into the whiteness. She wipes moisture from her eyelashes and looks up "
            "the invisible road."
        ),
        "weather": (
            "Thick cold morning fog on a mountain road, volumetric light through mist, "
            "dew on everything, edges dissolving into white"
        ),
        "grade": "muted pale grey-teal grade, hazy dreamlike mountain atmosphere",
        "dialogue": "起雾了……今天怕是到不了了。",
        "sound": "damp mountain silence, distant dripping, soft wind through pines",
        "music": "slow ambient pads, quiet and suspended",
    },
    {
        "name": "scene_04_neon_ling",
        "title": "04 霓虹夜市·小乐 中景+跟拍",
        "char": "xiaole",
        "action": (
            "Medium shot, camera tracking forward following Xiao Le matching Picture 3 "
            "as he weaves through a neon night market alley, colorful glowing signboards "
            "and smoking skewer stalls on both sides, steam rising into colored light. "
            "He stops at a candied hawthorn stall, pointing excitedly at the biggest red "
            "one, bouncing on his toes."
        ),
        "weather": (
            "Vivid neon signs in magenta, cyan and amber, smoke and steam catching the "
            "colored light, busy crowded night market"
        ),
        "grade": "high-saturation neon night-market grade, lively cyberpunk-tinged",
        "dialogue": "糖葫芦！我要那串最红的！",
        "sound": "sizzling skewers, chatter, faint electronic music from a stall",
        "music": "bouncy synth-pop, energetic and playful",
    },
    {
        "name": "scene_05_candle_ally",
        "title": "05 烛光书房·嘉玲 特写+缓推",
        "char": "jialing",
        "action": (
            "Extreme close-up on Jialing matching Picture 1 lit by fireplace glow in an "
            "old study, dust motes floating in the warm light, walls of old books "
            "blurred behind her. Camera slowly creeping in on her eyes as she turns a "
            "yellowed page, her expression calm and softly nostalgic."
        ),
        "weather": (
            "Deep warm candle and fireplace light, flickering amber shadows, intimate "
            "old library atmosphere, dust in the beams of light"
        ),
        "grade": "warm amber-red candlelight grade, cozy classic film look",
        "dialogue": "好久没看这么厚的书了。",
        "sound": "crackling fireplace, faint page turns, settling wood",
        "music": "soft acoustic fingerpicking, warm and intimate",
    },
    {
        "name": "scene_06_bright_ally",
        "title": "06 极昼天台·嘉玲 中远景+上摇",
        "char": "jialing",
        "action": (
            "Medium-wide shot on a blindingly bright rooftop terrace, camera slowly "
            "tilting up from her shoes to her face against the overexposed white sky, "
            "city skyline hazy below. Wind whips her hair and scarf around her, she "
            "squints and holds her scarf closed, small and graceful against the huge "
            "white sky."
        ),
        "weather": (
            "Blinding high-key white daylight, slightly overexposed sky, clean airy "
            "light, strong wind, everything soft and washed out"
        ),
        "grade": "high-key white overexposed grade, ethereal and airy",
        "dialogue": "风真大。……都吹乱了。",
        "sound": "strong wind, flapping fabric, faint city hum far below",
        "music": "minimal airy pad, bright and light",
    },
    {
        "name": "scene_07_sun_ling",
        "title": "07 金色麦田·小乐 远景+推进",
        "char": "xiaole",
        "action": (
            "Wide shot of golden wheat fields under a bright blue summer sky, camera "
            "pushing in as Xiao Le matching Picture 3 runs along a dirt path holding "
            "a red kite, the kite lifting off behind him, wheat brushing his legs, "
            "his laugh caught in the wind, tiny figure in the vast golden field."
        ),
        "weather": (
            "Bright summer day, deep blue sky with white clouds, golden wheat swaying, "
            "warm direct sunlight, clear visibility"
        ),
        "grade": "bright warm summer grade, saturated golden field, optimistic",
        "dialogue": "飞起来啦——我的风筝飞起来啦！",
        "sound": "wind in the wheat, running footsteps, kite flutter",
        "music": "cheerful acoustic folk, bright and free",
    },
]


def build_subjects(char: str):
    if char == "jialing":
        return [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    return [
        {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/cardigan"},
        {"label": XIAOLE_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "close-up quality reference"},
    ]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING if sh["char"] == "jialing" else IMG_XIAOLE
        subjects = build_subjects(sh["char"])
        ref_list = [img, img]  # storyboard + character 同一角色图, 无场景图
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
                    "scene": None,  # 纯文字场景, 无场景参考图
                    "extra_images": [],
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
    out = ROOT / "shots" / "jialing_scene_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
