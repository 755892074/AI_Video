#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""生成 v5 冒烟 manifest: 镜1嘉玲开场重做 + 镜2纸鹤飞翔跟拍(新)
+ 镜4施咒(眼神/法杖指向) + 镜5公鸡跳头晨鸣(新)。镜3复用 v3/shot01.mp4。
链式: cast1(镜1,首段) / fly(镜2,首段) / cast2(镜4首段 -> 镜5续接)。"""
import json, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# ---------- 通用 Subject 定义片段 ----------
SUB_JIALING = ("<Subject 1>: a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, cool detached big-sister aura, wearing Hogwarts style dark robe, "
    "red and yellow striped scarf, grey pleated skirt, sitting in an old antique swivel chair, "
    "holding a wooden wand, [Picture 1]")
SUB_XIAOLE = ("<Subject 1>: a 7-year-old Chinese boy, second grade, short black hair, "
    "transparent-frame glasses, wearing an oversized Gryffindor style wizard robe, excited goofy face, "
    "holding a toilet brush like a wand, [Picture 1]")
SUB_HALL = ("<Subject 2>: an old Hogwarts style magic school hall: ancient stone walls, "
    "tall arched windows with amber stained glass, floating candles, long wooden tables, "
    "raised wooden podium, warm torchlight, [Picture 2]")
SUB_HALL_BG = ("<Subject 3>: the warm Hogwarts hall background reinforcing stone walls, candles, "
    "amber stained glass, NOT a plain white background, [Picture 3]")
SUB_ROOSTER = ("<Subject 3>: a realistic large farm rooster with bright red serrated comb and wattle, "
    "rich orange-red breast and neck feathers, dark green iridescent tail feathers, brown body, "
    "sturdy legs with spurs, photorealistic animal matching the photographic scene style, [Picture 3]")

RA_JIALING = ("Subject 1: fully_preserved - the senior female teacher (identical in all shots)\n"
    "Picture 1: fully_preserved - face, auburn-red wavy hair, robe, scarf\n"
    "Subject 2: fully_preserved - the scene (background)\n"
    "Picture 2: fully_preserved - stone walls, candles, tables, warm light")
RA_XIAOLE = ("Subject 1: fully_preserved - the novice apprentice (identical in all shots)\n"
    "Picture 1: fully_preserved - boy face, glasses, robe, toilet brush\n"
    "Subject 2: fully_preserved - the scene (background)\n"
    "Picture 2: fully_preserved - stone walls, candles, tables, warm light")
RA_HALL = ("Subject 1: fully_preserved - the scene (background)\n"
    "Picture 1: fully_preserved - stone walls, candles, tables, warm light\n"
    "Subject 2: fully_preserved - the scene (background)\n"
    "Picture 2: fully_preserved - stone walls, candles, tables, warm light")
RA_CAST2 = ("Subject 1: fully_preserved - the novice apprentice (identical in all shots)\n"
    "Picture 1: fully_preserved - boy face, glasses, robe, toilet brush\n"
    "Subject 2: fully_preserved - the scene (background)\n"
    "Picture 2: fully_preserved - stone walls, candles, tables, warm light\n"
    "Subject 3: fully_preserved - the realistic rooster (same rooster as previous shot)\n"
    "Picture 3: fully_preserved - red comb, orange-red neck, green tail, body shape")

# ---------- 镜1: 嘉玲开场(古董转椅 + 装饰纸鹤 + 真实大小) ----------
PROMPT_1 = f"""<Prompt>

<Subject Definitions>
{SUB_JIALING}
{SUB_HALL}
{SUB_HALL_BG}

<Summary>
[Shot 1] Inside the warm ancient Hogwarts hall, dozens of small white paper cranes hang from the ceiling on thin threads, swaying gently like wind chimes. [Subject 1] sits in the old antique swivel chair in the center of the hall. She gently swivels the chair in a smooth, slow half-turn, her face staying front-facing and intact throughout the turn, until she faces one of the hanging paper cranes, then raises her wooden wand. She opens her mouth and chants the spell in sync with the dialogue. A golden arc of light traces from the wand and hits that one small paper crane (realistic small size, only about the size of a hand, NOT oversized). The paper crane suddenly comes alive, magical energy shimmering around it as it flaps its small paper wings and lifts off. [Subject 2] surrounds them with warm hall ambience.

<Retention Analysis>
{RA_JIALING}

<Detailed Description>
Reference: [Picture 1], [Picture 2], [Picture 3]
[Shot 1] Background: the warm ancient Hogwarts hall with amber stained glass windows, floating candles, long wooden tables, and dozens of small white paper cranes hanging from the ceiling on thin threads, swaying gently like wind chimes. The entire scene is bathed in warm torchlight and amber light. NOT a plain white background, NOT a studio backdrop. [Subject 1] sits in an old antique swivel chair with carved wooden arms and a worn velvet seat in the center of the hall. The camera stays at a fixed frontal angle facing her. She gently swivels the chair in a smooth, slow half-turn. During the turn, her face stays perfectly intact and consistent with [Picture 1] — same Asian oval face, single eyelids, auburn-red wavy hair, sharp features, no distortion, no melting, no deformed or extra facial features. She keeps her head turned toward the camera, so her face remains clearly visible and front-facing while the chair glides. When the chair stops, she faces one particular small paper crane hanging nearby. She raises her wooden wand, aims it at that paper crane, opens her mouth and chants the spell in sync with the dialogue. A golden arc of light traces from the wand tip through the air and strikes the small paper crane. The paper crane is a realistic small white origami crane, only about the size of a hand (around 15 cm), NOT a giant enlarged crane, with realistic size matching everyday life. It suddenly comes alive, magical energy shimmering around it, and it flaps its small paper wings and lifts off from where it hangs. Her expression stays cool and elegant. [Subject 2] surrounds them with warm hall ambience, [Subject 3] reinforcing the warm background.
Dialogue: (S1) <d>[Chinese] 集中精神。马里马里轰！</d>
No narration, no other language.

<Overall Soundscape>
paper cranes rustling gently, faint magical shimmer, hall ambience, chair creaking softly

<Non-Diegetic Music>
calm elegant piano, then comedic

</Prompt>"""

# ---------- 镜2: 纸鹤飞翔跟拍(纯空镜,镜头随纸鹤) ----------
PROMPT_2 = f"""<Prompt>

<Subject Definitions>
{SUB_HALL}
{SUB_HALL_BG}

<Summary>
[Shot 1] A small white origami paper crane, real hand-sized (about 15 cm, NOT oversized), brought alive by magic, flutters up and soars through the warm ancient Hogwarts hall, leaving a faint golden trail. The camera follows the paper crane in a smooth continuous tracking shot: it swoops up past the floating candles, glides between the tall arched windows with amber stained glass, circles above the long wooden tables, and rises toward the high vaulted ceiling. The small paper crane flaps its paper wings with crisp lively motion, golden magical shimmer sparkling around it. [Subject 1] the old hall fills the frame around it.

<Retention Analysis>
{RA_HALL}

<Detailed Description>
Reference: [Picture 1], [Picture 2]
[Shot 1] Camera: a smooth continuous tracking shot that follows the small paper crane through the air, sweeping and rising with it through the hall. The small white origami paper crane, real hand-sized (about 15 cm, NOT oversized), flutters up from the hall and soars through the warm ancient Hogwarts hall, its folded paper wings flapping with crisp lively motion, leaving a faint golden trail of magical shimmer. It swoops up past the floating candles, glides between the tall arched windows with amber stained glass, circles gracefully above the long wooden tables, and rises toward the high vaulted ceiling. The camera stays locked on the paper crane, drifting and rising with it, while the warm hall moves past in the background. [Subject 1] the old hall with floating candles and amber stained glass surrounds the scene, [Subject 2] reinforcing the warm background.
Dialogue: none
No narration, no other language.

<Overall Soundscape>
paper wings flapping softly, magical golden shimmer, gentle hall ambience, candle flames flickering

<Non-Diegetic Music>
light magical waltz, whimsical and airy

</Prompt>"""

# ---------- 镜4: 小乐施咒变公鸡(眼神锁定纸鹤 + 法杖直指纸鹤) ----------
PROMPT_4 = f"""<Prompt>

<Subject Definitions>
{SUB_XIAOLE}
{SUB_HALL}
{SUB_ROOSTER}

<Summary>
[Shot 1] [Subject 1] the little boy keeps his eyes locked on the paper crane flying in the air, raises the toilet brush and points it directly at the paper crane, then loudly casts the spell (sync with the dialogue "马里马里轰"). A bright golden beam shoots from the brush tip straight toward the paper crane. The paper crane, enveloped in the golden light, mid-air transforms into a realistic large farm rooster matching [Picture 3] (bright red comb, orange-red neck feathers, dark green iridescent tail). The rooster flaps its wings powerfully and lets out a loud clucking crow. [Subject 1] still stares at it with eyes wide open in amazement.

<Retention Analysis>
{RA_CAST2}

<Detailed Description>
Reference: [Picture 1], [Picture 2], [Picture 3]
[Shot 1] [Subject 1] the little boy fixes his eyes directly on the paper crane flying in the warm Hogwarts hall — his gaze never leaves it — raises the toilet brush and points it straight at the paper crane, the brush tip aimed exactly at it. He opens his mouth wide and loudly says the magic words in perfect sync with the dialogue, and a bright golden beam shoots from the brush tip straight toward the paper crane. The paper crane, flying in the warm Hogwarts hall, is enveloped in the golden light and mid-air it transforms into a realistic large farm rooster matching [Subject 3] / [Picture 3] (bright red comb, orange-red neck feathers, dark green iridescent tail). The rooster flaps its wings powerfully and lets out a loud clucking crow. [Subject 1] looks at the rooster with eyes wide open in amazement, glasses slightly askew. [Subject 2] the warm ancient hall with amber stained glass and floating candles surrounds the scene.
Dialogue: (S2) <d>[Chinese] 我也来。马里马里轰！</d>
No narration, no other language.

<Overall Soundscape>
boy's spell voice (S2), golden light shimmer, paper crane rustling, rooster loud crow, hall echo

<Non-Diegetic Music>
slapstick music, silly string effect

</Prompt>"""

# ---------- 镜5: 公鸡跳到小乐头上,晨鸣(调戏镜头) ----------
PROMPT_5 = f"""<Prompt>

<Subject Definitions>
{SUB_XIAOLE}
{SUB_HALL}
{SUB_ROOSTER}

<Summary>
[Shot 1] The rooster flaps its wings hard and leaps up, landing right on top of [Subject 1]'s head, its claws gripping his hair. It throws its head back and lets out a loud triumphant crow, "cock-a-doodle-doo". [Subject 1], the little boy, is caught completely off guard: eyes wide open, mouth hanging open, wobbling and staggering under the rooster's weight, glasses askew, comically flustered. Playful teasing moment. [Subject 2] the old hall.

<Retention Analysis>
{RA_CAST2}

<Detailed Description>
Reference: [Picture 1], [Picture 2], [Picture 3]
[Shot 1] [Subject 1] the little boy stands in the warm ancient Hogwarts hall, still excited and goofy. The realistic large farm rooster matching [Subject 3] / [Picture 3] (bright red comb, orange-red neck feathers, dark green iridescent tail) flaps its wings hard and leaps up, landing right on top of the boy's head, its sturdy claws gripping his hair. It throws its head back, red comb jiggling, and lets out a loud triumphant crow, "cock-a-doodle-doo". The boy is caught completely off guard: his eyes go wide, his mouth hangs open, he wobbles and staggers under the rooster's weight, glasses knocked askew, comically flustered and waving his arms. A playful teasing moment. [Subject 2] the warm ancient hall with amber stained glass and floating candles surrounds the scene.
Dialogue: (S2) <d>[Chinese] 哎呀！快、快下来啊！</d>
No narration, no other language.

<Overall Soundscape>
rooster triumphant crow, boy yelp (S2), flapping feathers, hall echo

<Non-Diegetic Music>
playful teasing comedic music

</Prompt>"""

HALL = "../scenes/hogwarts_old_hall.png"

man = {
    "comfy_url": "http://100.67.139.74:8188",
    "workflow": "workflows/h3_r2v_motion_context_api.json",
    "base_dir": "shots",
    "sets": [
        {
            "id": "xiaole_crane_v5_cast1",
            "title": "镜1_嘉玲开场_古董转椅+装饰纸鹤+真实大小",
            "shots": [
                {
                    "shot": 1,
                    "storyboard": "../characters/jialing_wizard/reference.png",
                    "character": HALL,
                    "scene": HALL,
                    "extra_images": [HALL],
                    "prompt": PROMPT_1,
                }
            ],
        },
        {
            "id": "xiaole_crane_v5_fly",
            "title": "镜2_纸鹤飞翔跟拍_镜头随纸鹤",
            "shots": [
                {
                    "shot": 1,
                    "storyboard": HALL,
                    "character": HALL,
                    "scene": HALL,
                    "extra_images": [HALL],
                    "prompt": PROMPT_2,
                }
            ],
        },
        {
            "id": "xiaole_crane_v5_cast2",
            "title": "镜4/5_施咒变公鸡(眼神+法杖指向)+公鸡跳头晨鸣",
            "shots": [
                {
                    "shot": 1,
                    "storyboard": "../characters/xiaole_wizard/reference_new.png",
                    "character": HALL,
                    "scene": "../characters/rooster/reference.png",
                    "extra_images": [HALL],
                    "prompt": PROMPT_4,
                },
                {
                    "shot": 2,
                    "storyboard": "../characters/xiaole_wizard/reference_new.png",
                    "character": HALL,
                    "scene": "../characters/rooster/reference.png",
                    "extra_images": [HALL],
                    "prompt": PROMPT_5,
                },
            ],
        },
    ],
}

out = os.path.join(ROOT, "shots", "_smoke_crane_v5_manifest.json")
with open(out, "w", encoding="utf-8") as f:
    json.dump(man, f, ensure_ascii=False, indent=2)
print("written:", out, os.path.getsize(out), "bytes")
for s in man["sets"]:
    for sh in s["shots"]:
        print(f"  {s['id']} shot{sh['shot']} prompt={len(sh['prompt'])}")

# ---- m1fix: 仅镜1(嘉玲转椅, 脸稳定重跑) ----
man1 = {
    "comfy_url": "http://100.67.139.74:8188",
    "workflow": "workflows/h3_r2v_motion_context_api.json",
    "base_dir": "shots",
    "sets": [
        {
            "id": "xiaole_crane_v5_m1fix",
            "title": "镜1fix_嘉玲转椅_面部稳定(半转+正面朝向)",
            "shots": [
                {
                    "shot": 1,
                    "storyboard": "../characters/jialing_wizard/reference.png",
                    "character": HALL,
                    "scene": HALL,
                    "extra_images": [HALL],
                    "prompt": PROMPT_1,
                }
            ],
        },
    ],
}
out1 = os.path.join(ROOT, "shots", "_smoke_crane_v5_m1fix_manifest.json")
with open(out1, "w", encoding="utf-8") as f:
    json.dump(man1, f, ensure_ascii=False, indent=2)
print("written:", out1, os.path.getsize(out1), "bytes")
