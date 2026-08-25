# -*- coding: utf-8 -*-
"""
群演/多人场景 专项测试批次生成器
输出: shots/crowd_test_manifest.json
- 8 镜: 纯文字驱动的多人群场景(无角色参考图, 不锁角色库)
- 目标: 检验 H3 对"群演/配角/人群"的渲染质量(多样性/自然感/无 AI 伪影)
- 每镜不同人群场景 + 景别/运镜, 6s 短镜
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

# 人群质量通用约束：注入到每镜 action 尾部
CROWD_QUALITY = (
    "The crowd must look natural and alive: people of varied ages, heights, outfits and "
    "skin tones, each with different poses and directions of movement, some looking around, "
    "some talking, some on phones, natural random spacing and overlapping, NO duplicated "
    "faces or identical repeated people, NO robotic synchronized motion, NO malformed hands "
    "or blank hollow expressions. Treat every extra as a real background performer."
)

SHOTS = [
    {
        "name": "crowd_00_metro",
        "title": "00 早高峰地铁站台",
        "action": (
            "Medium shot, camera slowly panning along a crowded rush-hour subway platform. "
            "A dense flow of commuters moves in both directions: office workers in suits "
            "checking phones, a student with a backpack rushing past, an old woman carrying "
            "a shopping bag, a couple holding hands, people queuing near the yellow safety "
            "line as the train lights approach in the tunnel. Fluorescent station lights, "
            "tiled walls, ad panels."
        ),
        "grade": "cool fluorescent urban realism, slightly desaturated, documentary film look",
        "sound": "echoing station announcements, train rumble approaching, shuffling footsteps, chatter",
        "music": "none",
    },
    {
        "name": "crowd_01_concert",
        "title": "01 夏日音乐节现场",
        "action": (
            "Wide shot from the crowd level of a huge outdoor summer music festival, camera "
            "slowly pushing forward over thousands of raised hands and phones. The crowd "
            "surges and jumps together, beach balls bounce over heads, colorful flags wave, "
            "dazzling stage lights and confetti fall from the dark sky, sweat and energy "
            "everywhere, faces lit by changing colors."
        ),
        "grade": "high-contrast festival grade, vivid stage lights magenta and amber against deep night blue",
        "sound": "thumping bass and guitar feedback, thousands cheering, singing along",
        "music": "energetic rock anthem under the crowd roar",
    },
    {
        "name": "crowd_02_nightmarket",
        "title": "02 老街夜市小吃街",
        "action": (
            "Medium shot, camera tracking forward through a packed old-town night market "
            "street at dinner time. Thick crowds drift between food stalls, steam and "
            "smoke rising from grills, skewers sizzling, a kid on a father's shoulders "
            "pointing at candy, a cook tossing wok flames, tables of diners squeezed "
            "together, paper lanterns and string lights overhead."
        ),
        "grade": "warm amber tungsten mixed with neon sign colors, lively street photography look",
        "sound": "sizzling oil, clinking woks, vendor shouts, overlapping conversations, laughter",
        "music": "none",
    },
    {
        "name": "crowd_03_springfestival",
        "title": "03 春运火车站候车厅",
        "action": (
            "Medium-wide shot, camera slowly panning across a vast railway waiting hall "
            "packed with Spring Festival travelers. Crowds sit on luggage, squat by "
            "pillars, mothers feed children, old men smoke near the door, a young man "
            "talks loudly on the phone, luggage carts wheel past, red lanterns and "
            "Spring Festival banners overhead, tired but warm faces."
        ),
        "grade": "warm tungsten interior with cool window light, slightly hazy air, cinematic realism",
        "sound": "echoing station noise, rolling luggage wheels, baby crying, muffled announcements",
        "music": "none",
    },
    {
        "name": "crowd_04_crosswalk",
        "title": "04 城市十字路口过街",
        "action": (
            "High-angle shot looking down at a busy city crosswalk at morning rush, camera "
            "slowly descending. A dense river of pedestrians crosses the zebra crossing "
            "from all four directions when the light turns, umbrellas and backpacks bobbing, "
            "bicycles weaving through, a delivery rider zigzagging, an elderly couple "
            "walking arm in arm, cars waiting at the stop line, buildings and billboards "
            "surrounding the intersection."
        ),
        "grade": "clean modern city daylight, slightly high-key, realistic urban grade",
        "sound": "crosswalk beeping signal, car engines, city hum, footsteps and bicycle bells",
        "music": "none",
    },
    {
        "name": "crowd_05_beach",
        "title": "05 夏日海滩游客群",
        "action": (
            "Medium-wide shot, camera tracking sideways along a crowded summer beach. "
            "Sunbathers on towels, kids splashing at the waterline, a volleyball game in "
            "the middle, families under striped umbrellas, a vendor carrying a cooler "
            "between blankets, seagulls circling, people walking dogs and playing frisbee, "
            "bright swimsuits scattered across the golden sand."
        ),
        "grade": "bright saturated summer daylight, warm golden sand, cheerful commercial look",
        "sound": "crashing waves, children laughing, distant music from a speaker, seagull cries",
        "music": "light upbeat pop, summery",
    },
    {
        "name": "crowd_06_schoolyard",
        "title": "06 小学课间操场",
        "action": (
            "Medium shot, camera slowly arcing around a crowded primary school playground "
            "during recess. Dozens of kids in identical blue-and-white tracksuits run, "
            "jump rope, chase each other and play catch, a few huddle around a marble "
            "game on the ground, two girls swing on the swingset, a whistle blows in the "
            "distance, autumn trees and a red teaching building at the edge."
        ),
        "grade": "warm afternoon sunlight, soft nostalgic grade, lively school atmosphere",
        "sound": "children shouting and laughing, jumprope slapping concrete, distant whistle, birds",
        "music": "light cheerful folk, playful",
    },
    {
        "name": "crowd_07_stadium",
        "title": "07 足球场观众席",
        "action": (
            "Wide shot of a packed football stadium during a heated match, camera slowly "
            "pulling back from a roaring section. Tens of thousands of fans in team colors "
            "stand and cheer, a Mexican wave ripples through the stands, scarves and flags "
            "wave wildly, a few fans in face paint hug and jump, the bright green pitch "
            "tiny far below, floodlights blazing."
        ),
        "grade": "high-contrast floodlit night, team colors saturated, epic live-sports grade",
        "sound": "tens of thousands roaring, drums and horns, chanting, vuvuzela buzz",
        "music": "epic orchestral swell under the crowd",
    },
]


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        action = f"{sh['action']}\n{CROWD_QUALITY}\nColor grade: {sh['grade']}."
        shot = dict(sh)
        shot["action"] = action
        shot["sound"] = sh["sound"]
        shot["music"] = sh["music"]
        shot["dialogue"] = None  # 纯人群环境, 无主角对白
        # 无 subjects/refs: 纯文字场景, 不锁任何角色
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
    out = ROOT / "shots" / "crowd_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
