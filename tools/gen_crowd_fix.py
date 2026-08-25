# -*- coding: utf-8 -*-
"""
群演缓解策略验证批次生成器
输出: shots/crowd_fix_manifest.json
- 6 镜: 验证 H3 人群三大问题(静止雷同/脸糊/漂移)能否被缓解
- 全部叠缓解策略: 中近景(不拍远景人头海) / 人数 10-20 / 慢速移动(leisurely stroll) /
  前景 2-4 人差异化动作 / 背景人群静止当环境 / 一个镜头一个主动作
- 每镜一个侧重维度: 近景群演 / 中景差异化 / 静态人群+镜头动 / 慢速人流 / 静态人群 / 前景清晰背景虚化
- megapixels=0.7(720p 级) 改善脸糊; 6s 短镜
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

# 缓解策略通用约束
RELIEF = (
    "Crowd control: NO giant distant crowds, keep the crowd count between 8 and 20 "
    "people total and keep most of them in the middle ground, NOT far away in the "
    "background. Background people mostly stand still or drift VERY slowly, acting as "
    "living environment. Only 2 to 4 foreground people move, and each of them has a "
    "DIFFERENT small action. All movement is SLOW and gentle: people stroll at a "
    "leisurely pace, never walk briskly or run. No one crosses the frame in a blur. "
    "Faces stay clear and sharp, keep eye contact or readable facial expressions on "
    "nearby people. No duplicated faces, no identical poses, no synchronized motion."
)

SHOTS = [
    {
        "name": "fix_00_cafe",
        "title": "00 街角咖啡馆·近景群演",
        "focus": "近景+少量前景群演, 镜头静止",
        "action": (
            "Static medium-close shot at a sidewalk cafe in late afternoon. In the "
            "foreground three people sit at small tables: a woman sipping coffee and "
            "looking down the street, a man reading a newspaper, a girl scrolling her "
            "phone and smiling. Behind them, about ten people stroll past VERY slowly "
            "along the sidewalk or sit in the background, softly out of focus. Warm "
            "golden light, gentle breeze, leaves drifting."
        ),
        "grade": "warm golden-hour cafe look, shallow depth of field, foreground sharp",
        "sound": "clinking cups, soft chatter, distant street ambience",
        "music": "soft acoustic jazz, unhurried",
    },
    {
        "name": "fix_01_market",
        "title": "01 集市摊位·中景差异化",
        "focus": "中景+15人+前景差异化动作",
        "action": (
            "Medium shot of a corner of an open-air market with about fifteen people, "
            "camera very slowly pushing in. Foreground: a stall owner arranging fruit, "
            "a customer haggling and holding up an apple, a kid tugging his mother's "
            "sleeve. In the middle ground people stroll leisurely or stop to look at "
            "stalls, a few sit on stools chatting. Everyone moves slowly and naturally, "
            "no one hurries."
        ),
        "grade": "natural daylight market grade, warm and lively but unhurried",
        "sound": "market chatter, fruit crate sounds, distant bargaining",
        "music": "none",
    },
    {
        "name": "fix_02_station",
        "title": "02 车站候车·静态人群+镜头横移",
        "focus": "人群静止当环境, 镜头横向缓移",
        "action": (
            "Medium shot of a small train station waiting area, camera panning slowly "
            "to the left. About a dozen waiting passengers are mostly still: a man "
            "reading on a bench, an old couple sitting side by side, a woman checking "
            "her ticket, a student leaning against a pillar with headphones on, a "
            "sleeping child in a stroller. Only one person slowly walks into frame from "
            "the right carrying a small bag. Calm, almost still atmosphere."
        ),
        "grade": "soft window-lit interior, muted warm tones, quiet documentary feel",
        "sound": "faint platform announcement, soft footsteps, distant train rumble",
        "music": "gentle ambient piano, quiet",
    },
    {
        "name": "fix_03_crossing",
        "title": "03 人行道·慢速人流",
        "focus": "8人 leisurely stroll 慢速通过",
        "action": (
            "Medium-close shot of a tree-lined sidewalk, camera static. About eight "
            "people stroll across the frame at an easy, unhurried pace: an old man "
            "with a cane, a woman pushing a stroller, two friends chatting and "
            "laughing, a delivery rider waiting on his scooter at the edge. In the "
            "foreground a girl stops to tie her shoelace, then rises slowly. Everyone "
            "moves gently, feet planted naturally, faces visible and clear."
        ),
        "grade": "soft daylight, gentle contrast, relaxed urban scene",
        "sound": "rustling leaves, soft footsteps, distant birds, light traffic",
        "music": "light folk guitar, easygoing",
    },
    {
        "name": "fix_04_schoolgate",
        "title": "04 学校门口·放学静态",
        "focus": "静态人群+慢动作, 时间停滞感",
        "action": (
            "Medium shot in front of a primary school gate after dismissal, camera "
            "nearly still with a tiny slow drift. About twelve people: parents standing "
            "and waiting quietly, a few kids walking out slowly carrying backpacks, a "
            "teacher at the gate nodding to parents, a vendor with a candy cart standing "
            "still. The scene is calm and warm, people hardly move, a child waves "
            "goodbye slowly. Everything feels like a gentle pause."
        ),
        "grade": "soft late-afternoon light, warm nostalgic schoolyard tone",
        "sound": "children's voices, gentle chatter, distant school bell",
        "music": "soft music-box melody, nostalgic",
    },
    {
        "name": "fix_05_park",
        "title": "05 公园长椅·前景清晰背景虚化",
        "focus": "近景主体 + 人群散景",
        "action": (
            "Medium-close shot on a park bench by a pond, camera slowly pushing in "
            "very gently. Foreground sharp: two people sit on the bench, one feeding "
            "ducks, the other sketching on a pad. Behind them, about ten people stroll "
            "along the path in soft bokeh, blurred and slow, their faces not required "
            "to be in focus. Ducks glide on the pond, leaves drift down, warm "
            "afternoon sun through the trees."
        ),
        "grade": "warm backlit park grade, creamy bokeh background, foreground crisp",
        "sound": "ducks quacking, gentle water, distant children laughing",
        "music": "soft acoustic plucking, serene",
    },
]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        action = f"{sh['action']}\n{RELIEF}\nColor grade: {sh['grade']}."
        shot = dict(sh)
        shot["action"] = action
        shot["sound"] = sh["sound"]
        shot["music"] = sh["music"]
        shot["dialogue"] = None
        prompt = build_prompt(shot, subjects=[])
        issues = check_prompt(prompt, refs=[])
        if issues:
            n_bad += 1
            print(f"[FAIL] {sh['name']}  {sh['title']}")
            for it in issues:
                print("   - " + it)
        else:
            print(f"[OK]   {sh['name']}  {sh['title']}")

        sets.append({
            "id": f"crowd_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": None,
                    "character": None,
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
    out = ROOT / "shots" / "crowd_fix_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s, "
          f"megapixels={sets[0]['shots'][0]['megapixels']})")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
