# -*- coding: utf-8 -*-
"""
嘉玲微表情近景测试批次生成器
输出: shots/jialing_microexp_manifest.json
- 11 镜: 00 基准脸 + 10 情绪 (surprise/happy/sad/tears/anger/fear/disgust/contempt/embarrass/longing)
- 全部近景特写(CU), 礼堂暖光背景虚化, 每镜独立 set(不拼接)
- 字段语义: storyboard=嘉玲主体, character=嘉玲身份, scene=礼堂背景  ← 不再错位
- 六段式 prompt 由 h3-ref2va-prompt 的 builder 生成 + check 校验
"""
import json
import re
import sys
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

# ---------- 共享 Subject 定义（所有镜头一致） ----------
# refs 顺序 = ref_images 注入顺序: [0]=嘉玲主体, [1]=嘉玲身份, [2]=礼堂背景
SUBJECTS = [
    {
        "label": "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
                 "Asian oval face, single eyelids, cool detached big-sister aura, wearing "
                 "Hogwarts style dark robe, red and yellow striped scarf, grey pleated skirt",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "identical girl in all shots, keep face/hair/scarf",
    },
    {
        "label": "the same 17-year-old girl in an extreme close-up portrait, face filling "
                 "the frame, wavy auburn-red hair, Asian oval face, single eyelids, warm "
                 "torchlight on her skin, red and yellow striped scarf",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "close-up quality reference",
    },
    {
        "label": "an old Hogwarts style magic school hall: ancient stone walls, tall arched "
                 "windows with amber stained glass, floating candles, long wooden tables, warm "
                 "torchlight, softly blurred behind the girl, NOT a plain white background",
        "picture": True,
        "retention": "fully_preserved",
        "picture_retention": "fully_preserved",
        "note": "soft blurred background",
    },
]

REFS = [
    "../characters/jialing_wizard/reference.png",   # [Picture 1] 嘉玲主体
    "../characters/jialing_wizard/reference.png",   # [Picture 2] 嘉玲身份(双重锚定)
    "../scenes/hogwarts_old_hall.png",              # [Picture 3] 礼堂背景
]

# ---------- 每镜数据 ----------
# action: 详细英文面部/微表情描述(近景特写, 表情时序), 对白单独给 dialogue
SHOTS = [
    {
        "name": "microexp_00_baseline",
        "title": "00 基准脸(中性)",
        "dialogue": None,
        "sound": "faint crackling of floating candles in the warm hall, soft air",
        "music": "none, pure silence baseline",
        "action": (
            "Extreme close-up of the girl's face, her face filling the frame, warm torchlight "
            "and softly blurred amber hall behind her. Neutral expression: eyes calm and "
            "composed, eyelids at rest, lips gently closed, brows relaxed, breathing slow and "
            "even. She gazes straight into the camera with a cool, detached, unreadable look, "
            "no smile, no frown, perfectly still. This is the emotional zero point."
        ),
    },
    {
        "name": "microexp_01_surprise",
        "title": "01 惊讶(意外)",
        "dialogue": "你来干什么？不是说好了不来吗。",
        "sound": "a sudden soft pop like a tiny firework in the hall, then quiet",
        "music": "light suspenseful string plucks",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, softly blurred amber hall "
            "behind. She is neutral for a split second, then surprise flashes: eyelids snap "
            "upward, eyes widen, pupils dilate slightly, eyebrows lift high, lips part in a "
            "quick gasp. The surprise peaks for one beat, then she catches herself, the "
            "expression tightening back into cool composure with a small guarded blink. She "
            "says with faint disbelief: (S1) <d>[Chinese] 你来干什么？不是说好了不来吗。</d>"
        ),
    },
    {
        "name": "microexp_02_happy",
        "title": "02 惊喜(压不住的开心)",
        "dialogue": "哼，居然还记得我生日。……行吧，谢了。",
        "sound": "a soft suppressed giggle, gentle hall ambience",
        "music": "warm cheerful light piano",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "She first presses her lips into a stern line to hold back a smile, but the corners "
            "of her mouth curl up anyway, eyes crinkling and brightening with a genuine warm "
            "sparkle, cheeks flushing faint pink. She tilts her head away slightly to hide the "
            "smile, then turns back toward camera with a soft, barely-contained joyful smile. "
            "She says teasingly: (S1) <d>[Chinese] 哼，居然还记得我生日。……行吧，谢了。</d>"
        ),
    },
    {
        "name": "microexp_03_sad",
        "title": "03 悲伤·强忍",
        "dialogue": "没事，我挺好的。……真的，你放心吧。",
        "sound": "slow quiet breaths, faint hall echo",
        "music": "melancholic low piano, sparse",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "Her eyes slowly grow red and watery, lower lip trembling slightly, jaw tight as she "
            "swallows hard to hold back tears. She forces a small brave smile that does not "
            "reach her eyes, blinking rapidly to keep the tears in. Her voice is steady but "
            "strained as she says: (S1) <d>[Chinese] 没事，我挺好的。……真的，你放心吧。</d> "
            "At the end one tear glistens but does not fall."
        ),
    },
    {
        "name": "microexp_04_smile_tears",
        "title": "04 含泪微笑(释然)",
        "dialogue": "替我照顾好它。……也不用想我。",
        "sound": "one deep breath, quiet hall, soft candle crackle",
        "music": "soft resolved piano, gentle and warm",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "A single tear slides down her cheek, but her mouth curves into a genuine soft "
            "smile, eyes warm and peaceful, brow relaxed. She exhales slowly, as if letting "
            "something go, looking gently past the camera with quiet acceptance. She says "
            "softly and sincerely: (S1) <d>[Chinese] 替我照顾好它。……也不用想我。</d>"
        ),
    },
    {
        "name": "microexp_05_anger",
        "title": "05 愤怒·压抑",
        "dialogue": "我再说一遍——别跟着我了。",
        "sound": "tense silence, a faint distant rumble",
        "music": "low ominous drone",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "Her brow lowers sharply, eyes turning cold and sharp like knives, jaw muscle "
            "visibly clenching, jawline tight, nostrils flaring slightly. She keeps her voice "
            "low, controlled and dangerous, breathing heavier through her nose. She says with "
            "cold finality: (S1) <d>[Chinese] 我再说一遍——别跟着我了。</d>"
        ),
    },
    {
        "name": "microexp_06_fear",
        "title": "06 恐惧/惊慌",
        "dialogue": "别、别过来。你别过来！",
        "sound": "quick shallow breaths, heartbeat-like thumping",
        "music": "dissonant high string tremolo",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "Her pupils suddenly contract, more white of the eye showing, lips pale and "
            "slightly parted, brows raised and drawn together, body leaning back a little as if "
            "stepping away, breath caught in her chest. Her voice comes out trembling, "
            "breaking mid-sentence: (S1) <d>[Chinese] 别、别过来。你别过来！</d>"
        ),
    },
    {
        "name": "microexp_07_disgust",
        "title": "07 厌恶/嫌弃",
        "dialogue": "拿开。你那一套，留着糊弄别人去。",
        "sound": "a soft dismissive exhale, quiet hall",
        "music": "none, cold silence",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "Her nose wrinkles slightly, corners of her mouth pull down, brows knit in "
            "displeasure, head tilting back a fraction as if distancing herself from something "
            "unpleasant, gaze flat and dismissive. She says with cool disdain, each word "
            "deliberate: (S1) <d>[Chinese] 拿开。你那一套，留着糊弄别人去。</d>"
        ),
    },
    {
        "name": "microexp_08_contempt",
        "title": "08 轻蔑/不屑",
        "dialogue": "就这？我还以为你有多大本事。",
        "sound": "faint hall ambience, slow candle crackle",
        "music": "light nonchalant jazz plucks",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "A single corner of her mouth lifts into a slow cold smirk, eyelids drooping "
            "slightly, looking down at the camera from a half-lidded gaze, chin up, "
            "unhurried and perfectly composed. She drawls with mock appreciation: "
            "(S1) <d>[Chinese] 就这？我还以为你有多大本事。</d>"
        ),
    },
    {
        "name": "microexp_09_embarrass",
        "title": "09 羞耻/尴尬",
        "dialogue": "……刚才那句话，你当我没说。",
        "sound": "a nervous swallow, quiet hall",
        "music": "shy gentle plucked strings",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "She glances away first, eyes darting sideways then down, cheeks flushing visibly "
            "red with heat, biting her lower lip, mouth opening as if to speak then closing "
            "again. Finally she speaks in a small mumbling voice, barely audible, avoiding the "
            "camera: (S1) <d>[Chinese] ……刚才那句话，你当我没说。</d>"
        ),
    },
    {
        "name": "microexp_10_longing",
        "title": "10 思念(温柔底色)",
        "dialogue": "要是你还在，肯定会笑我今天的傻样吧。",
        "sound": "soft hall breeze, distant candle flames",
        "music": "tender nostalgic piano, warm and slow",
        "action": (
            "Extreme close-up of the girl's face, warm torchlight, blurred amber hall behind. "
            "Her gaze drifts past the camera to a distant point, eyes softening and going "
            "dreamy, a faint warm smile settling on her lips, fingers unconsciously stroking "
            "the end of her red and yellow striped scarf. She speaks in a low, gentle, "
            "yearning voice, as if talking to a memory: "
            "(S1) <d>[Chinese] 要是你还在，肯定会笑我今天的傻样吧。</d>"
        ),
    },
]

WORKFLOW = "workflows/h3_r2v_motion_context_api.json"


def strip_inline_dialogue(action: str) -> str:
    """剥离 action 中内嵌的对白标签(避免与 builder 的 Dialogue 行重复),
    'She says with disbelief: (S1) <d>[Chinese] ...</d>' -> 'She says with disbelief.'"""
    return re.sub(r":\s*\(S1\) <d>\[Chinese\].*?</d>", ".", action, flags=re.S)


def main():
    sets = []
    for sh in SHOTS:
        shot = dict(sh)
        shot["action"] = strip_inline_dialogue(sh["action"])
        prompt = build_prompt(shot, SUBJECTS)
        issues = check_prompt(prompt, REFS)
        status = "OK" if not issues else "; ".join(issues)
        print(f"[{status}] {sh['name']}  dialogue={sh['dialogue'] or '(无)'}")
        if issues:
            print("   " + " | ".join(issues))
        sets.append({
            "id": f"jialing_{sh['name']}",
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": REFS[0],   # ref_image_0 嘉玲主体
                    "character": REFS[1],    # ref_image_1 嘉玲身份
                    "scene": REFS[2],        # ref_image_2 礼堂背景
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
    out = ROOT / "shots" / "jialing_microexp_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    n_bad = sum(1 for sh in SHOTS
                if check_prompt(build_prompt(dict(sh, action=strip_inline_dialogue(sh["action"])), SUBJECTS), REFS))
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
