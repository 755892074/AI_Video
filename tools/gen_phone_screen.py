# -*- coding: utf-8 -*-
"""
手机屏幕内容 专项测试批次生成器
输出: shots/phone_screen_manifest.json
- 4 镜 × 6s × 720p(megapixels=0.7), 默认链模式
- 测试目标: H3 能否在手机屏幕上渲染出可读文字(微信消息) 与 可辨认人脸(视频通话)
  - 00 微信聊天界面 · 中近景(正常手持场景, 文字在屏幕上的常规尺寸)
  - 01 微信消息气泡 · 屏幕特写(手机充满画面, 文字最大尺寸)
  - 02 视频通话 · 中近景(屏幕上出现小乐人脸, 含画中画窗口)
  - 03 视频通话屏幕特写(屏幕充满画面, 小乐人脸占满屏幕)
- 参考图布局:
  - 00/01: storyboard=嘉玲, character=嘉玲, scene=None  → Picture 1,2 (纯文字渲染测试)
  - 02/03: storyboard=嘉玲(持机人), character=小乐(屏幕里人脸), scene=None → Picture 1,2
- 正文保持全英文(中文只进 <d> 对白), UI 文字用英文描述内容
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
    "a plain light-grey hoodie over a white t-shirt, hair loosely tied back, "
    "holding a smartphone"
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
        "name": "phone_00_wechat",
        "title": "00 微信消息·嘉玲 中近景",
        "char": "jialing",
        "subjects": "jialing",
        "refs": ["jialing", "jialing"],
        "action": (
            "Medium close-up shot of Jialing matching Picture 1 sitting cross-legged on "
            "a bed at night, holding her smartphone in both hands with the screen tilted "
            "toward the camera, her face lit by the pale blue glow of the phone. The "
            "screen clearly shows a WeChat chat interface: a contact name in Chinese "
            "characters at the top, a row of small chat bubbles below with short Chinese "
            "text, one green bubble and two white bubbles, a small clock and battery "
            "icons in the status bar. Camera slowly pushing in, her thumb scrolling the "
            "chat, a faint smile on her face, her room softly blurred behind her."
        ),
        "weather": (
            "Dim cozy bedroom at night, warm bedside lamp glow mixing with cool blue "
            "phone screen light, soft blankets, blurred bookshelf background"
        ),
        "grade": "warm lamp glow against cool screen light, intimate night mood",
        "dialogue": "妈，我马上到家了。",
        "sound": "quiet bedroom, faint phone notification chime, distant city hum",
        "music": "soft lo-fi beat, calm and sleepy",
    },
    {
        "name": "phone_01_wechat_cu",
        "title": "01 微信消息气泡·屏幕特写",
        "char": "jialing",
        "subjects": "jialing",
        "refs": ["jialing", "jialing"],
        "action": (
            "Extreme close-up of a smartphone held in Jialing's hands matching Picture 1, "
            "the phone screen filling almost the entire frame. The WeChat chat screen is "
            "fully legible: a light grey chat background, a dark blue header with a "
            "Chinese contact name in large characters, several message bubbles stacked "
            "below with clear bold Chinese text characters in them, one green bubble on "
            "the right and two white bubbles on the left, a text input bar with a plus "
            "icon at the bottom, status bar with time and battery on top. Her thumb taps "
            "the input bar, the screen typing cursor blinks."
        ),
        "weather": (
            "Phone screen only in frame, bright clean chat UI colors, soft reflections "
            "on the glass, blurred dark room edges barely visible"
        ),
        "grade": "clean bright UI screen look, crisp and readable",
        "dialogue": None,
        "sound": "soft tapping, faint typing clicks, quiet room",
        "music": "none",
    },
    {
        "name": "phone_02_videocall",
        "title": "02 视频通话·嘉玲 中近景",
        "char": "jialing",
        "subjects": "jialing_xiaole",
        "refs": ["jialing", "xiaole"],
        "action": (
            "Medium close-up shot of Jialing matching Picture 1 holding her smartphone "
            "up in a video call, the phone screen facing the camera. On the phone screen "
            "a clear video call window shows the face of a 7-year-old boy with round "
            "glasses and a red cardigan matching Picture 2, smiling and waving, with a "
            "small self-view thumbnail of Jialing in the corner of the screen, call "
            "duration and mute icons visible. She looks at the screen and laughs softly, "
            "her face warm and relaxed, the phone screen glow lighting her cheek."
        ),
        "weather": (
            "Warm evening bedroom light, phone screen glow on her face, soft cozy "
            "background, gentle shadow play"
        ),
        "grade": "warm skin tones with screen cool accent, natural handheld look",
        "dialogue": "小乐！你看到我了吗？",
        "sound": "garbled warm voice from phone speaker, soft room ambience",
        "music": "none",
    },
    {
        "name": "phone_03_videocall_cu",
        "title": "03 视频通话屏幕·人脸特写",
        "char": "xiaole",
        "subjects": "jialing_xiaole",
        "refs": ["jialing", "xiaole"],
        "action": (
            "Extreme close-up of a smartphone screen during a video call, the phone "
            "screen filling the entire frame. The video call window shows the face of a "
            "7-year-old Chinese schoolboy with round glasses and a red printed cardigan "
            "matching Picture 2, his face clearly recognizable, waving his hand and "
            "smiling brightly, his small room visible behind him, a tiny self-view "
            "thumbnail in the top corner showing a girl with auburn hair matching "
            "Picture 1. The call UI shows elapsed time and connection icons at the top, "
            "a red end-call button at the bottom. His face is sharp and well lit, "
            "talking to the camera."
        ),
        "weather": (
            "Phone screen only in frame, bright clear video call picture, his small room "
            "with warm daylight behind him, crisp screen colors"
        ),
        "grade": "bright clean video-call screen look, sharp face focus",
        "dialogue": None,
        "sound": "warm boy voice from phone speaker, slight speaker distortion",
        "music": "none",
    },
]


def build_subjects(kind: str):
    if kind == "jialing":
        return [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
    # jialing_xiaole: 持机人=嘉玲(P1), 屏幕中人=小乐(P2)
    return [
        {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "identical girl holding the phone"},
        {"label": XIAOLE_SUBJECT, "picture": True, "retention": "fully_preserved",
         "picture_retention": "fully_preserved", "note": "boy on the phone screen, keep glasses/cardigan"},
    ]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        refs_map = {"jialing": IMG_JIALING, "xiaole": IMG_XIAOLE}
        img_list = [refs_map[r] for r in sh["refs"]]
        subjects = build_subjects(sh["subjects"])
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
        issues = check_prompt(prompt, img_list)
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
                    "storyboard": img_list[0],
                    "character": img_list[1] if len(img_list) > 1 else img_list[0],
                    "scene": None,  # 纯文字场景
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
    out = ROOT / "shots" / "phone_screen_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s, "
          f"megapixels={sets[0]['shots'][0]['megapixels']})")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
