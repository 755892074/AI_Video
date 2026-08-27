# -*- coding: utf-8 -*-
"""
lens_04/lens_07 修复验证批次生成器
输出: shots/lens_fix_manifest.json
- 2 镜 × 6s × 720p, 针对用户反馈的两个问题:
  - lens_04 特写+环绕(篝火): H3 把 orbit 误读为场景自转 → 改为 30° 短弧 + 相机路径描述 + 固定参照物锚点
  - lens_07 远景+上升(瀑布山谷): 大尺度纵向运镜人物丢失 + 动态水难处理 → 缩小运镜幅度(低幅度缓升) + 瀑布换静湖 + 人物保持前景可见 + 固定参照物锚点
- 关键提示词技巧: 显式声明 "only the camera moves / the world does not rotate",
  给画面加"固定不动"的参照物(a pine tree stays at screen-right), 用位移路径代替 orbit 词
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"

JIALING_SUBJECT = (
    "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, cool detached big-sister aura, wearing "
    "Hogwarts style dark robe, red and yellow striped scarf, grey pleated skirt"
)
JIALING_CU_SUBJECT = (
    "the same 17-year-old girl in a close-up portrait, wavy auburn-red hair, "
    "Asian oval face, single eyelids, red and yellow striped scarf"
)

SHOTS = [
    {
        "name": "lens_fix_04_bonfire",
        "title": "04fix 篝火夜林·嘉玲 特写+30°短弧",
        "action": (
            "Close-up on Jialing matching Picture 1 kneeling beside a single campfire "
            "in a dark forest clearing. Only the camera moves: it makes one short slow "
            "arc of about 30 degrees, starting from her right side and gliding to "
            "slightly in front of her, then gently holds still. The world does not "
            "rotate at all: Jialing stays kneeling and facing the campfire the whole "
            "time without turning her body, and one large dark pine tree remains firmly "
            "fixed at the right edge of the frame throughout the entire shot. Warm "
            "firelight flickers steadily across her face, sparks drifting up from that "
            "same single fire."
        ),
        "weather": (
            "Clear starry night, dark pine forest, one steady campfire, drifting "
            "sparks, cool air, faint smoke curling upward"
        ),
        "grade": "warm firelight against dark teal, high contrast cinematic",
        "dialogue": "火的声音，真好听。",
        "sound": "crackling fire, night insects, distant owl call",
        "music": "warm fingerpicked acoustic, calm and meditative",
    },
    {
        "name": "lens_fix_07_lake",
        "title": "07fix 晨湖静谧·嘉玲 远景+低幅缓升",
        "action": (
            "Wide shot on the shore of a calm mountain lake at sunrise. Jialing "
            "matching Picture 1 stands at the water's edge on the left side of the "
            "frame, seen from her side profile. Only the camera moves: it rises very "
            "slowly and by only a small amount, staying at a modest height so Jialing "
            "remains clearly visible in the lower left of the frame at all times. The "
            "lake surface stays perfectly calm and still, reflecting the sky, distant "
            "forested hills behind her. A large grey boulder stays fixed at the "
            "bottom-right corner of the frame throughout the entire shot. Nothing in "
            "the world rotates or moves except the gentle mist drifting over the water."
        ),
        "weather": (
            "Sunrise, soft golden-pink light over a still mirror-like lake, thin mist "
            "on the water surface, quiet forested hills, calm and peaceful"
        ),
        "grade": "soft dawn pastel grade, serene and airy",
        "dialogue": "好安静啊。",
        "sound": "still water, faint birdsong, soft morning breeze",
        "music": "minimal ambient piano, quiet and vast",
    },
]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING
        subjects = [
            {"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/scarf"},
            {"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
             "picture_retention": "fully_preserved", "note": "close-up quality reference"},
        ]
        ref_list = [img, img]
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
                    "scene": None,
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
    out = ROOT / "shots" / "lens_fix_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s, "
          f"megapixels={sets[0]['shots'][0]['megapixels']})")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
