# -*- coding: utf-8 -*-
"""
"AI 高危场景" 专项测试批次生成器
输出: shots/hard_test_manifest.json
- 12 镜, 全部是视频生成模型经典翻车点: 手部/肢体细节, 人物与物体交互,
  空间一致性, 双人互动, 极端特效, 长镜头
- 720p(megapixels=0.7), 单镜 6s (对话镜 8s)
- 全部纯文字场景, 不喂 scene 参考, 测 H3 原生能力
- 双角色镜(握手/对话)用 extra_images 锁两个角色身份
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
    # ---- A. 手部/肢体细节 ----
    {
        "name": "hard_01_chopsticks",
        "title": "01 手部·筷子夹菜 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Big close-up of Jialing matching Picture 1's hand holding a pair of "
            "wooden chopsticks over a small porcelain bowl of noodles. She grips the "
            "chopsticks, pinches a few noodle strands between the tips, lifts them, "
            "and brings them to her mouth, taking a small bite. The camera stays on "
            "her hand the whole time: every finger visible, the two chopsticks "
            "crossing cleanly without passing through each other, the noodles staying "
            "gripped without sliding. Sharp focus on the hand, each finger distinct "
            "with correct count and natural joints."
        ),
        "weather": (
            "Warm indoor daylight from a window, plain wooden table, soft shallow "
            "depth of field, muted cozy tones"
        ),
        "grade": "clean realistic macro grade, sharp on the hand, blurred background",
        "dialogue": "",
        "sound": "soft chopsticks clinking on the bowl, quiet slurp, gentle room ambience",
        "music": "quiet acoustic guitar, minimal",
    },
    {
        "name": "hard_02_walk",
        "title": "02 肢体·行走跑步 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Medium shot, side view. Jialing matching Picture 1 walks steadily "
            "toward the left of frame along a plain stone path, then breaks into a "
            "gentle jog. Her legs cycle through natural walking then running strides: "
            "each leg swings forward and back smoothly, feet lift off and plant "
            "cleanly with no sliding on the ground, arms swing opposite to the legs, "
            "her robe hem swishes with each step. The gait is fluid and continuous, "
            "no float, no moonwalk, her body stays upright and stable."
        ),
        "weather": (
            "Soft overcast daylight, plain grey stone path, muted neutral tones"
        ),
        "grade": "neutral realistic grade, steady side-on tracking",
        "dialogue": "",
        "sound": "soft footsteps on stone, robe swish, gentle breathing",
        "music": "steady walking tempo percussion, calm",
    },
    {
        "name": "hard_03_handshake",
        "title": "03 双人·握手 嘉玲+小乐",
        "char": "jialing",
        "partner": "xiaole",
        "seconds": 6.0,
        "action": (
            "Medium shot. Jialing matching Picture 1 and Xiao Le matching Picture 3 "
            "face each other and shake hands: two hands meet palm-to-palm, fingers "
            "wrap around each other and clasp, pumping twice, then release. Their "
            "hands interlock naturally, the fingers weave correctly without passing "
            "through each other, neither arm bends unnaturally, both bodies stay "
            "firmly on their own side with no merging or overlapping of shoulders. "
            "A clean, crisp, physically correct handshake between the two."
        ),
        "weather": (
            "Bright school hallway, soft daylight, neutral clean background"
        ),
        "grade": "clean neutral grade, both faces and hands in sharp focus",
        "dialogue": "……那就说定了。",
        "sound": "two palms meeting with a soft clap, low voices, hallway reverb",
        "music": "light warm piano, friendly",
    },
    # ---- B. 人物与物体交互 ----
    {
        "name": "hard_04_door",
        "title": "04 交互·推门入室 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Medium shot from inside the room, facing an old wooden door. Jialing "
            "matching Picture 1's hand reaches in and grips the round brass doorknob, "
            "turns it, and pushes the door open toward the camera. The door swings "
            "open fully, she steps through the doorway and walks past the camera "
            "into the room, the door frame passing beside her. Her hand stays "
            "correctly attached to the knob then lets go, the door never passes "
            "through her body, the knob never detaches from the door."
        ),
        "weather": (
            "Soft daylight flooding in from the doorway, dim room interior, "
            "wooden floor, neutral tones"
        ),
        "grade": "realistic interior grade, warm wood tones",
        "dialogue": "……回来了。",
        "sound": "door latch clicking, hinges creaking, footsteps on wood",
        "music": "quiet ambient, subtle tension",
    },
    {
        "name": "hard_06_drink",
        "title": "06 交互·喝水 小乐",
        "char": "xiaole",
        "seconds": 6.0,
        "action": (
            "Close-up on Xiao Le matching Picture 1 at a kitchen table. He lifts a "
            "clear glass of water with both hands, tilts it to his lips and drinks: "
            "the glass rim presses against his lower lip, water pours into his "
            "mouth without spilling down his chin, his throat visibly swallows, "
            "then he lowers the glass, a small drip running down the side of his "
            "chin which he wipes with the back of his hand. The water surface "
            "tilts realistically, the glass stays intact, the liquid enters his "
            "mouth cleanly with no leaking through his face."
        ),
        "weather": (
            "Bright clean kitchen, warm daylight, calm room"
        ),
        "grade": "bright natural grade, sharp on the glass and face",
        "dialogue": "咕咚……",
        "sound": "water pouring, gulping swallow, glass clinking on table",
        "music": "light playful plucks, casual",
    },
    {
        "name": "hard_07_bike",
        "title": "07 交互·骑自行车 小乐",
        "char": "xiaole",
        "seconds": 6.0,
        "action": (
            "Medium side shot. Xiao Le matching Picture 1 rides a bicycle along a "
            "quiet lane, pedaling steadily: both feet push the pedals in smooth "
            "rotating circles, knees rise and fall in rhythm, the chain ring turns, "
            "the front wheel steers gently. His body stays balanced over the frame, "
            "he grips the handlebars with both hands, his legs never kick through "
            "the wheels, the bike stays under him the whole time, no floating, "
            "no merging of body and bicycle."
        ),
        "weather": (
            "Sunny afternoon, tree-lined lane, warm light, soft shadows"
        ),
        "grade": "bright airy grade, cheerful motion",
        "dialogue": "哈——！",
        "sound": "bicycle chain ticking, wheels on asphalt, boy's happy shout",
        "music": "bright bouncy acoustic, playful",
    },
    {
        "name": "hard_08_reenter",
        "title": "08 空间·出画再入画 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Static medium-wide shot of a quiet courtyard, camera locked off. "
            "Jialing matching Picture 1 enters from screen right, walks across the "
            "frame to the left, and exits completely out of frame. A moment later "
            "she walks back into frame from the left, retracing her path to screen "
            "right and exiting again. When she returns she is the exact same girl: "
            "same robe, same red and yellow striped scarf, same wavy auburn-red "
            "hair, same face. Her clothing and hairstyle stay perfectly consistent "
            "between the two passes, the camera never moves."
        ),
        "weather": (
            "Soft overcast daylight, plain stone courtyard, muted tones"
        ),
        "grade": "neutral realistic grade, locked-off static frame",
        "dialogue": "",
        "sound": "steady footsteps across stone, soft ambient, a bird call",
        "music": "minimal airy pad, calm",
    },
    # ---- E. 极端特效 ----
    {
        "name": "hard_13_glass",
        "title": "13 特效·玻璃破碎 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Medium shot. Jialing matching Picture 1 stands by a large window, "
            "turned halfway toward it. A rock flies in and strikes the glass: the "
            "pane shatters into a starburst of jagged shards, glass pieces spraying "
            "outward in every direction, catching the light as they tumble. Jialing "
            "flinches and shields her face with her arm a beat after the impact, "
            "eyes widening, then lowers her arm and stares at the broken frame. The "
            "glass breaks outward into pieces, the shards follow ballistic paths "
            "and fall, she is never cut, the window frame stays intact."
        ),
        "weather": (
            "Grey daylight outside the window, shards glinting as they scatter, "
            "dust motes in the light"
        ),
        "grade": "high-contrast daylight, sharp shards catching light",
        "dialogue": "啊——！",
        "sound": "sharp crack of glass, shards tinkling as they scatter and settle",
        "music": "tense sting, then hollow quiet",
    },
    {
        "name": "hard_14_umbrella",
        "title": "14 特效·雨中撑伞 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Medium shot. Jialing matching Picture 1 walks through steady rain "
            "holding a black umbrella high above her head. Rain falls in angled "
            "streaks around her, drops ping off the taut umbrella surface and roll "
            "down its edges in little streams, her shoulders stay dry, droplets "
            "splash off the wet pavement around her feet with each step. The umbrella "
            "stays stable in her grip, the rain direction stays consistent, her face "
            "stays dry beneath the canopy, her robe hem darkens where it catches "
            "spray."
        ),
        "weather": (
            "Heavy grey rain, wet reflective pavement, misty distance, overcast"
        ),
        "grade": "cool rainy grade, droplets catching light",
        "dialogue": "……雨好大。",
        "sound": "steady rain hiss, drops drumming on umbrella fabric, footsteps splashing",
        "music": "soft piano under rain, melancholic",
    },
    {
        "name": "hard_15_explosion",
        "title": "15 特效·冲击波 嘉玲",
        "char": "jialing",
        "seconds": 6.0,
        "action": (
            "Medium shot. Jialing matching Picture 1 stands in a wide empty plaza "
            "when a fireball erupts in the distance beyond her. A visible shockwave "
            "ring blasts outward across the plaza: a gust of wind hits her a beat "
            "later, her robe and scarf and hair whip backward violently, she braces "
            "and leans into the blast, one hand holding her scarf, dust and debris "
            "streaming past her. The wave passes and everything settles, she lowers "
            "her hand and looks toward the smoke. The force travels smoothly from "
            "far to near, she reacts at the right moment, nothing launches her "
            "unnaturally into the air."
        ),
        "weather": (
            "Overcast daylight, wide empty plaza, dust and smoke plume far away, "
            "wind gust across the ground"
        ),
        "grade": "gritty realistic grade, high-contrast blast light",
        "dialogue": "……！",
        "sound": "deep distant boom, wind whoosh rushing past, debris clattering, settle",
        "music": "sub-bass hit, then low drone",
    },
    {
        "name": "hard_16_shrink",
        "title": "16 特效·变大变小 小乐",
        "char": "xiaole",
        "seconds": 6.0,
        "action": (
            "Wide shot inside a normal living room. Xiao Le matching Picture 1 "
            "stands beside a floor lamp and a bookshelf, then smoothly shrinks "
            "until he is tiny, no taller than the lamp's shade, then smoothly "
            "grows back up to his normal size beside the furniture. His proportions "
            "stay correct at every size, the lamp and bookshelf stay their normal "
            "size and never distort, he scales smoothly with no morphing, no "
            "stretching, his clothes scale with his body, the scale change is "
            "one continuous motion in place."
        ),
        "weather": (
            "Warm cozy living room, soft indoor light, neutral furniture"
        ),
        "grade": "clean realistic grade, clear size contrast",
        "dialogue": "——变！",
        "sound": "soft magical hum rising and falling, gentle whoosh, quiet room",
        "music": "playful glissando harp, wondrous",
    },
    # ---- F. 长镜头 ----
    {
        "name": "hard_18_dialog",
        "title": "18 长镜·对话 8s 嘉玲+小乐",
        "char": "jialing",
        "partner": "xiaole",
        "seconds": 8.0,
        "action": (
            "Medium two-shot, over-shoulder, held steady. Jialing matching Picture 1 "
            "and Xiao Le matching Picture 3 sit facing each other at a small table "
            "and talk for the whole shot. Jialing speaks first, then Xiao Le "
            "answers, then she replies. Each one's lips move in natural speech, "
            "matching the tone of what they say, mouth shapes forming and closing "
            "smoothly with no drifting, no extra teeth, no warping over the full "
            "eight seconds. They take turns: when one speaks the other listens, "
            "gazing naturally, heads slightly tilted, neither floats or shifts "
            "position, the camera holds completely still."
        ),
        "weather": (
            "Warm indoor evening light, cozy room, soft shallow depth of field"
        ),
        "grade": "warm intimate grade, both faces softly lit",
        "dialogue": "你要走了吗？／嗯，明天一早就出发。／那……我给你写信。",
        "sound": "gentle room tone, two warm voices taking turns, subtle chair creak",
        "music": "quiet emotional piano, understated",
    },
]


def build_subjects(shot):
    if shot["char"] == "jialing":
        base = [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    else:
        base = [
            {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/cardigan"},
            {"label": XIAOLE_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    if shot.get("partner"):
        if shot["partner"] == "xiaole":
            base.append({"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
                         "picture_retention": "fully_preserved", "note": "identical boy, keep glasses/cardigan"})
        else:
            base.append({"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
                         "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"})
    return base


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING if sh["char"] == "jialing" else IMG_XIAOLE
        ref_list = [img, img]
        if sh.get("partner"):
            ref_list.append(IMG_XIAOLE if sh["partner"] == "xiaole" else IMG_JIALING)
        subjects = build_subjects(sh)
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
            print(f"[OK]   {sh['name']}  {sh['title']}  ({sh['seconds']}s)")

        sets.append({
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": img,
                    "character": img,
                    "scene": None,
                    "extra_images": [IMG_XIAOLE if sh.get("partner") == "xiaole" else IMG_JIALING]
                    if sh.get("partner") else [],
                    "seconds": sh["seconds"],
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
    out = ROOT / "shots" / "hard_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
