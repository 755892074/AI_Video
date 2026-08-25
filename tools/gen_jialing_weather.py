# -*- coding: utf-8 -*-
"""
嘉玲天气/色调测试批次生成器
输出: shots/jialing_weather_manifest.json
- 10 镜: 同一基准中性表情(对照 00_baseline), 换 10 种天气/色调
- 全近景特写, 礼堂参考图不变, 天气光影/色调全部由 prompt 描述驱动
- 6s 短镜(seconds=6), 每镜独立 set, 字段语义正确
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

SUBJECTS = [
    {
        "label": "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
                 "Asian oval face, single eyelids, cool detached big-sister aura, wearing "
                 "Hogwarts style dark robe, red and yellow striped scarf, grey pleated skirt",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "identical girl, keep face/hair/scarf under every lighting",
    },
    {
        "label": "the same 17-year-old girl in an extreme close-up portrait, face filling "
                 "the frame, wavy auburn-red hair, Asian oval face, single eyelids, red and "
                 "yellow striped scarf",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "close-up quality reference",
    },
    {
        "label": "an old Hogwarts style magic school hall: ancient stone walls, tall arched "
                 "windows with amber stained glass, floating candles, long wooden tables, "
                 "softly blurred behind the girl, NOT a plain white background",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "blurred background, its lighting changes with weather",
    },
]

REFS = [
    "../characters/jialing_wizard/reference.png",
    "../characters/jialing_wizard/reference.png",
    "../scenes/hogwarts_old_hall.png",
]

BASE_NEUTRAL = (
    "Extreme close-up of the girl's face, face filling the frame, softly blurred hall "
    "behind her. Her neutral expression stays identical to the baseline: eyes calm and "
    "composed, eyelids at rest, lips gently closed, brows relaxed, breathing slow and even, "
    "gazing straight into the camera with a cool, detached, unreadable look. No smile, no "
    "frown, perfectly still. The weather and color tone change around her, but her identity "
    "and neutral face never change."
)

SHOTS = [
    {
        "name": "weather_00_sunny",
        "title": "00 晴天·暖金",
        "weather": (
            "Bright warm morning sunlight streams through the tall arched windows, "
            "golden sunbeams and dust motes floating in the air, the hall glowing warm "
            "amber-gold with soft highlights on her hair"
        ),
        "grade": "warm golden color grade, sunny outdoor feeling, bright and optimistic",
        "sound": "faint birdsong outside, soft warm breeze, gentle hall ambience",
        "music": "bright warm acoustic guitar, gentle",
    },
    {
        "name": "weather_01_rainy",
        "title": "01 雨天·灰蓝",
        "weather": (
            "Heavy rain patters against the tall arched windows, rain streaks running down "
            "the glass, grey overcast daylight dimming the hall, cool damp atmosphere, "
            "puddles of grey light on the stone floor"
        ),
        "grade": "overcast desaturated grey-blue color grade, melancholic rainy mood",
        "sound": "steady rain pattering on the roof and windows, distant low thunder",
        "music": "slow sparse piano, rain-soaked melancholy",
    },
    {
        "name": "weather_02_snowy",
        "title": "02 雪天·冷白",
        "weather": (
            "Soft snowflakes drift past the windows and float inside near the glass, "
            "the hall lit by cold pale winter daylight, frost-white and quiet, a hush of "
            "snowy stillness in the air"
        ),
        "grade": "cool white-blue color grade, winter cold and pure",
        "sound": "soft wind, muffled snowy quiet, faint flakes brushing the glass",
        "music": "light crystalline chimes, icy and serene",
    },
    {
        "name": "weather_03_night",
        "title": "03 夜晚·月光",
        "weather": (
            "Deep night outside the windows, pale blue moonlight spills into the dark hall, "
            "a few floating candles flicker warmly against the cool shadows, "
            "stars faintly visible through the glass"
        ),
        "grade": "deep moonlit blue color grade with warm candle accents",
        "sound": "crickets, night wind, soft candle flicker",
        "music": "quiet nocturnal strings, mysterious and calm",
    },
    {
        "name": "weather_04_foggy",
        "title": "04 雾天·青灰",
        "weather": (
            "Thick grey fog drifts through the hall, hazy and veiled, volumetric light "
            "piercing the mist in pale shafts, edges of the room dissolving into fog"
        ),
        "grade": "muted teal-grey color grade, dreamy and hazy",
        "sound": "muffled distant sounds, soft damp air, fog horn far away",
        "music": "ambient drones, slow and dreamlike",
    },
    {
        "name": "weather_05_neon",
        "title": "05 霓虹·紫红",
        "weather": (
            "Electric neon light leaks through the windows in magenta and cyan bars, "
            "colored reflections sweeping across the dark hall, a synthetic cyberpunk "
            "glow mixing with the candlelight"
        ),
        "grade": "high-contrast magenta-cyan neon color grade",
        "sound": "distant electronic hum, city buzz, soft synth ambience",
        "music": "synthesizer pads, neon-lit retro vibe",
    },
    {
        "name": "weather_06_bw",
        "title": "06 黑白·胶片",
        "weather": (
            "The whole scene rendered in pure black and white, soft window light sculpting "
            "her face, fine film grain and gentle silver-toned gradients, timeless "
            "monochrome portrait"
        ),
        "grade": "black and white film look, heavy film grain, silver print contrast",
        "sound": "room tone, faint clock tick, vintage ambience",
        "music": "soft vintage jazz, nostalgic and classic",
    },
    {
        "name": "weather_07_teal",
        "title": "07 青绿·冷调",
        "weather": (
            "Cold teal-green light fills the hall, harsh clinical shadows, desaturated "
            "skin tones, a tense thriller atmosphere, cool fluorescent-mixed daylight"
        ),
        "grade": "cold teal-green color grade, thriller tension",
        "sound": "low ominous drone, tense silence",
        "music": "dark synth pulse, suspenseful",
    },
    {
        "name": "weather_08_candle",
        "title": "08 烛光·暖红",
        "weather": (
            "Close warm candlelight flickers across her face, deep amber-red glow, "
            "firelight dancing in her eyes, soft shadows flickering on the stone walls, "
            "intimate warm darkness"
        ),
        "grade": "warm amber-red candlelight color grade, intimate and cozy",
        "sound": "crackling fire, soft air, faint wax pops",
        "music": "gentle acoustic melody, warm and intimate",
    },
    {
        "name": "weather_09_bright",
        "title": "09 极昼·白亮",
        "weather": (
            "Blinding bright daylight floods the hall, slightly overexposed, clean white "
            "light, high-key atmosphere, everything soft and airy, halo around the windows"
        ),
        "grade": "high-key bright white color grade, slightly overexposed and ethereal",
        "sound": "airy silence, light wind, faint birdsong",
        "music": "minimal ambient pad, pure and serene",
    },
]

WORKFLOW = "workflows/h3_r2v_motion_context_api.json"


def main():
    sets = []
    for sh in SHOTS:
        action = (
            f"{BASE_NEUTRAL}\nWeather and lighting: {sh['weather']}.\n"
            f"Color grade: {sh['grade']}."
        )
        shot = dict(sh)
        shot["action"] = action
        shot["sound"] = sh["sound"]
        shot["music"] = sh["music"]
        shot["dialogue"] = None
        prompt = build_prompt(shot, SUBJECTS)
        issues = check_prompt(prompt, REFS)
        status = "OK" if not issues else "; ".join(issues)
        print(f"[{status}] {sh['name']}  {sh['title']}")
        if issues:
            print("   " + " | ".join(issues))
        sets.append({
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": REFS[0],
                    "character": REFS[1],
                    "scene": REFS[2],
                    "seconds": 6.0,
                    "prompt": prompt,
                }
            ],
        })

    manifest = {
        "comfy_url": "http://100.67.139.74:8188",
        "workflow": WORKFLOW,
        "base_dir": "shots",
        "sets": sets,
    }
    out = ROOT / "shots" / "jialing_weather_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套, 每镜 {sets[0]['shots'][0]['seconds']}s)")
    n_bad = sum(1 for sh in SHOTS
                if check_prompt(build_prompt(dict(sh, action=f"{BASE_NEUTRAL}\nWeather and lighting: {sh['weather']}.\nColor grade: {sh['grade']}.",
                                              sound=sh["sound"], music=sh["music"], dialogue=None), SUBJECTS), REFS))
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
