# -*- coding: utf-8 -*-
"""
嘉玲/小乐 景别×运镜 专项测试批次生成器
输出: shots/jialing_lens_manifest.json
- 8 镜: 每镜一个"景别+运镜"组合, 全部与 jialing_scene(电影场景)批次不重复
- 上一批已测: 中景+横摇 / 远景+缓推 / 中近景+环绕 / 近景+拉远 / 中景+跟拍 /
              特写+缓推 / 中远景+上摇 / 远景+推进
- 本批新测: 大远景+下降 / 全景+横移 / 中近景+甩镜 / 近景+手持 /
              特写+环绕 / 大特写+缓推 / 中景+下摇 / 远景+上升
- 纯文字场景(scene=None), 参考图仅锁角色身份(角色图 x2)
- 720p(megapixels=0.7) 提高细节质量(特写/大特写更需要), 6s 短镜, 一镜一个主动作
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
        "name": "lens_00_plaza",
        "title": "00 河畔广场·嘉玲 大远景+垂直下降",
        "char": "jialing",
        "action": (
            "Extreme wide aerial shot of a vast riverside city plaza at blue hour, camera "
            "slowly descending from a high crane view down toward street level, buildings "
            "and river sprawling below. Jialing matching Picture 1 stands tiny in the "
            "center of the plaza scattering birdseed to a flock of pigeons, her dark robe "
            "a small silhouette on the pale stone, the camera keeps sinking until she "
            "grows to fill the middle of the frame, pigeons lifting around her."
        ),
        "weather": (
            "Blue hour dusk, city lights flickering on, soft purple-blue gradient sky, "
            "gentle river breeze, pigeons wheeling over the plaza"
        ),
        "grade": "blue-hour cinematic grade, vast and calm",
        "dialogue": "都飞走了……",
        "sound": "pigeon wings, distant city hum, river lapping",
        "music": "soft orchestral swell, expansive and serene",
    },
    {
        "name": "lens_01_canal",
        "title": "01 湖畔枫径·嘉玲 全景+横移",
        "char": "jialing",
        "action": (
            "Full body shot, camera smoothly trucking sideways right beside Jialing "
            "matching Picture 1 as she walks along a canal path lined with autumn maples, "
            "red leaves drifting across the water, her grey skirt swaying with each step, "
            "her whole figure kept in frame as the camera glides laterally with her, "
            "falling leaves passing through the foreground."
        ),
        "weather": (
            "Clear autumn afternoon, golden sunlight filtering through red maple leaves, "
            "gentle breeze, rippling canal water, fallen leaves on the stone path"
        ),
        "grade": "warm autumn golden grade, soft and nostalgic",
        "dialogue": "秋天到了啊。",
        "sound": "footsteps on stone, water lapping, leaves rustling",
        "music": "light acoustic waltz, gentle and flowing",
    },
    {
        "name": "lens_02_whippan",
        "title": "02 路灯夜巷·嘉玲 中近景+甩镜",
        "char": "jialing",
        "action": (
            "Medium close-up on Jialing matching Picture 1 standing under an old street "
            "lamp in a rainy alley, someone calls her name from off-screen and she "
            "sharply turns her head to the right, the camera whipping around with her "
            "gaze, neon and streetlights streaking into motion blur, the whip settling "
            "to lock on her surprised face, rain still falling around her."
        ),
        "weather": (
            "Rainy night, wet asphalt, neon glow in magenta and cyan reflecting off "
            "puddles, thin mist, one warm street lamp lighting her from above"
        ),
        "grade": "cyan-magenta neon grade, punchy and dynamic",
        "dialogue": "谁？",
        "sound": "steady rain, sudden footsteps, faint neon hum",
        "music": "tense string hit, then quiet heartbeat pulse",
    },
    {
        "name": "lens_03_hutong",
        "title": "03 胡同灯笼·嘉玲 近景+手持",
        "char": "jialing",
        "action": (
            "Close-up on Jialing matching Picture 1 holding a warm paper lantern in a "
            "narrow old hutong, a subtle handheld camera sway adding a gentle restless "
            "energy, her face lit from below by the amber lantern light, warm paper glow "
            "flickering across the grey brick walls behind her, thin mist curling past "
            "the eaves."
        ),
        "weather": (
            "Clear cool night, warm lantern glow against grey stone, light mist, "
            "a thin sliver of moon over the roofline"
        ),
        "grade": "warm amber against cool blue, intimate documentary feel",
        "dialogue": "爷爷说，提着灯笼走夜路，魂就不会丢。",
        "sound": "distant dog bark, soft wind through the hutong, fabric rustle",
        "music": "single cello notes, slow and intimate",
    },
    {
        "name": "lens_04_bonfire",
        "title": "04 篝火夜林·嘉玲 特写+环绕",
        "char": "jialing",
        "action": (
            "Close-up on Jialing matching Picture 1 kneeling beside a small campfire, "
            "camera slowly arcing around her profile as sparks drift up into the dark, "
            "warm firelight flickering across her face, her eyes fixed on the flames, "
            "the slow arc revealing dark forest silhouettes closing in behind her "
            "between the orange glow."
        ),
        "weather": (
            "Clear starry night, dark pine forest, dancing campfire light, drifting "
            "sparks, cool air, faint smoke curling up"
        ),
        "grade": "warm firelight against dark teal, high contrast cinematic",
        "dialogue": "火的声音，真好听。",
        "sound": "crackling fire, night insects, distant owl call",
        "music": "warm fingerpicked acoustic, calm and meditative",
    },
    {
        "name": "lens_05_eyes",
        "title": "05 窗前静默·嘉玲 大特写+缓推",
        "char": "jialing",
        "action": (
            "Extreme close-up on Jialing matching Picture 1, the frame filled by her "
            "eyes and brow, camera slowly pushing in until only her right eye remains, "
            "a single tear catching the light at the corner of her lashes, her gaze "
            "still and deep, soft window light reflected moving across the iris, "
            "everything around her falling out of focus."
        ),
        "weather": (
            "Soft indoor window light, gentle shadows on her cheek, dust motes in a "
            "warm beam, quiet afternoon"
        ),
        "grade": "shallow focus creamy warm grade, intimate and still",
        "dialogue": "……",
        "sound": "quiet breathing, distant clock tick",
        "music": "minimal piano, sparse and suspended",
    },
    {
        "name": "lens_06_fireworks",
        "title": "06 楼顶烟火·嘉玲 中景+下摇",
        "char": "jialing",
        "action": (
            "Medium shot on a rooftop on New Year's Eve, camera starts on Jialing "
            "matching Picture 1's upturned face lit by fireworks, then slowly tilting "
            "down along her red and yellow scarf to her hands clasping a small "
            "sparkler, white-gold sparks sizzling between her fingers, distant "
            "fireworks blooming and fading in the dark sky above her."
        ),
        "weather": (
            "Cold clear winter night, fireworks bursting in the deep sky, warm breath "
            "in the cold air, city lights glittering far below"
        ),
        "grade": "deep blue night with firework color pops, celebratory",
        "dialogue": "新年快乐。",
        "sound": "distant firework booms, sparkler sizzle, cold wind",
        "music": "warm bells and soft strings, hopeful",
    },
    {
        "name": "lens_07_valley",
        "title": "07 瀑布山谷·嘉玲 远景+上升",
        "char": "jialing",
        "action": (
            "Wide shot in a misty mountain valley, camera starting at ground level "
            "beside Jialing matching Picture 1 then smoothly rising straight up like "
            "a crane lift, the waterfall and forest spreading out below, her small "
            "figure shrinking beneath the camera as it ascends above the treetops "
            "into thin morning light."
        ),
        "weather": (
            "Early morning, soft sunlight piercing thin mist, lush green valley, "
            "waterfall mist drifting, birdsong echoing"
        ),
        "grade": "fresh green-teal cinematic grade, awe-inspiring",
        "dialogue": "好高。……好像能看见整个村子。",
        "sound": "waterfall roar fading below, wind, distant birds",
        "music": "rising orchestral strings, uplifting",
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
    out = ROOT / "shots" / "jialing_lens_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s, "
          f"megapixels={sets[0]['shots'][0]['megapixels']})")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
