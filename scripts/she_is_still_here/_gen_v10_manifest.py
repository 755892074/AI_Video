# -*- coding: utf-8 -*-
"""《她还在》v10 双锚+中文台词测试 manifest 生成（2 镜剧情段：病房陪伴+她听得到）"""
import json, os

ROOT = r"D:/WorkBuddy/AI_Video"
OUT = os.path.join(ROOT, "shots", "she_is_still_here", "v10_test_manifest.json")

STYLE_LINE = ("Photorealistic cinematic 3D CG render, UE5 quality, detailed skin shader with subsurface "
              "scattering, cold desaturated cinematic color grade, film grain — the EXACT visual style of the "
              "reference pictures. NOT live-action photography, NOT cartoon, NOT anime, NOT 2D illustration.")

NEG_COMMON = ("NO live-action photography, NO cartoon, NO anime, NO 2D illustration, NO painting, NO watercolor, "
              "NO oversaturated color, NO warm happy lighting. ")

SHOT1_PROMPT = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a dim private hospital ICU ward at night, seen from a steady MEDIUM SHOT three-quarter angle: a young unconscious woman lies in the hospital bed on the RIGHT side of the frame under a white blanket, long black hair spread on the pillow, and a weary man in a dark charcoal jacket sits on a chair on the LEFT side of the bed leaning forward, gently holding her right hand in both of his, his head bowed toward her. Rain streaks on the window behind. The framing, camera angle, bed-and-chair layout, both characters' positions and the lighting direction MUST stay EXACTLY as Picture 1 shows for the whole shot.
- **S2 Jiāng Chè (male lead)**: a Chinese man around 31, WEATHERED TIRED face with deep eye sockets and dark circles, short neat black hair, light stubble, strong jaw, faint nasolabial lines — his face must look EXACTLY as Picture 2 shows. Wearing the same dark charcoal jacket over a grey shirt as Picture 2 (plain-clothes detective, no uniform, no badge).
  - NEGATIVE IDENTITY: NOT a young smooth-faced man, NOT a different man, NOT a woman. This is THE tired stubbled man of Picture 2.
  - NEGATIVE HAIR: NO longer hair, NO different hairstyle, NO beard growth change. Stays short and neat as Picture 2.
  - NEGATIVE CLOTHING: NO suit, NO tie, NO uniform, NO police badge, NO different jacket. Stays in the dark charcoal jacket + grey shirt of Picture 2.
- **S1 Lín Mián (female lead, unconscious)**: a young Chinese woman around 22, very pale skin, long straight black hair, eyes closed as if asleep — her face and hospital gown must look EXACTLY as Picture 3 shows (lying unconscious, hospital attire, IV line visible).
  - NEGATIVE IDENTITY: NOT a man, NOT a different woman, NOT awake, NOT opening her eyes.
  - NEGATIVE HAIR: NO bun, NO updo, NO ponytail, NO braid, NO styling change. Stays long straight hair spread on the pillow as Pictures 1 and 3.
  - NEGATIVE CLOTHING: NO street clothes, NO colored clothes, NO jewelry. Stays in the same hospital attire as Picture 3.
- The two characters' spatial relationship follows Picture 1 exactly: S2 sits at the LEFT of the bed holding S1's hand, S1 lies in bed on the RIGHT. They are the ONLY two people in the shot.

# Summary
A 5-second quiet intimate night scene in the same dim private hospital ICU ward as Pictures 1-3. S2 Jiāng Chè sits at the bedside on the LEFT, holding S1 Lín Mián's right hand in both of his, head bowed close to her. He speaks to her in a low, tender, tired voice — his words are in MANDARIN CHINESE. He begins the shot already holding her hand as Picture 1 shows, then he lifts his head slightly, looks at her sleeping face with quiet guilt and tenderness, and murmurs one gentle sentence to her, then falls silent again, holding her hand, his thumb softly stroking her knuckles. {STYLE_LINE}
This is a gentle static scene — NO walking, NO turning around, NO standing up, NO large dramatic motion. The drama comes from his soft words and stillness. The camera holds ONE steady framing for the whole 5 seconds: no push-in, no zoom, no pan, no cut, no re-framing.
EMOTION LOCK: his emotion is quiet tenderness mixed with buried guilt — NOT smiling broadly, NOT cheerful, NOT crying dramatically. From the first frame to the last.
IDENTITY LOCK: S2 stays THE tired stubbled man of Picture 2, S1 stays THE pale unconscious black-haired girl of Picture 3 — NEVER swap, NEVER morph into another person. {NEG_COMMON}

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT framing as Picture 1 for the entire 5-second shot — same distance, same angle, same bed-chair layout. NO push-in, NO zoom, NO pan, NO tilt re-framing, NO cut to another angle, NO switch to a close-up of the face or hands, NO pull back to a wide shot. The visible frame content stays IDENTICAL to Picture 1 from the first frame to the very last frame.
- **IDENTITY LOCK**: S2 is THE tired stubbled Chinese man from Picture 2; S1 is THE pale unconscious black-haired girl from Picture 3. Skin, face, hair and build never change and never swap with each other, from the first frame to the VERY LAST FRAME.
- **HAIR LOCK**: S1's long straight black hair stays spread on the pillow EXACTLY as Pictures 1 and 3 show — no bun, no updo, no ponytail, no braid, no styling change, no hair getting shorter or longer. S2's short hair stays exactly as Picture 2. Applies at EVERY camera distance.
- **EMOTION LOCK**: S2's expression is quiet tenderness with buried guilt as he speaks and after he falls silent — he does NOT smile broadly, does NOT laugh, does NOT become cheerful, does NOT cry. His face reads: five years of weekly visits, exhaustion, and a guilt he never says out loud.
- **CLOTHING LOCK**: S2 stays in the dark charcoal jacket + grey shirt of Picture 2; S1 stays in the hospital attire of Picture 3. No clothing changes at any frame.
- **STYLE LOCK**: the photorealistic cinematic 3D CG render style (UE5 / octane feel, cold desaturated night grade, rain-streaked window light) stays IDENTICAL to Pictures 1/2/3 throughout. NEVER shifts to live-action photos, cartoon, anime, or illustration.
- **AUDIO-VISUAL LOCK**: when S2 speaks, his lip movement synchronizes with the Mandarin Chinese words he says — natural soft speech, NOT shouting, NOT whispering gibberish.

# Detailed Description
- 0.0–0.8s: The camera holds the MEDIUM SHOT of Picture 1 — the dim ward, S2 bowed over S1's hand at the bedside on the left, rain sliding down the window. S2 lifts his head slightly, looking at her sleeping face with tired, tender, guilty eyes.
- 0.8–3.4s: S2 speaks softly to her in Mandarin Chinese, his lips moving naturally with the words, his voice low and gentle, his thumb slowly stroking the back of her hand while he talks. (S2 Jiāng Chè) <d>[Chinese] 眠眠……你要是醒着，肯定又要嫌我胡子没刮。</d>
- 3.4–5.0s: His words trail off. He looks at her face for a moment longer, then lowers his head again toward their joined hands, holding her hand quietly. The frame stays perfectly still in the same MEDIUM SHOT. A single soft breath — almost an unheard sigh. Everything else: silent.

# Soundscape
Low ambience: soft rain against the window, the faint steady beep of the heart monitor, a distant hospital hum. In Mandarin Chinese, S2 speaks one gentle line in a low tired voice, slow and soft, half to her and half to himself: 「眠眠……你要是醒着，肯定又要嫌我胡子没刮。」 His tone is warm, exhausted, quietly self-deprecating — the words are what matters, not volume. No English. No other language. No narration. No sound effects beyond the rain, the monitor, and his voice.

# Music
Very low, sparse solo piano — a few quiet notes underneath his speech, never louder than his voice, fading out in the last second. Cold, tender, restrained. No drums, no strings swell. If it risks covering the Mandarin words, it stays barely audible."""

SHOT2_PROMPT = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a private hospital ICU ward at night seen from a HIGH-ANGLE (slightly above) MEDIUM SHOT: the young unconscious woman lies alone in the white bed at the center of the frame, long black hair spread on the pillow, a glowing heart monitor beside the bed on the right showing a steady green curve, rain-streaked window behind. The framing, camera angle, bed position and monitor placement MUST stay EXACTLY as Picture 1 shows for the whole shot.
- **S1 Lín Mián (female lead, unconscious)**: a young Chinese woman around 22, very pale skin, long straight black hair, eyes closed as if asleep — her face and hospital attire must look EXACTLY as Picture 2 shows (lying unconscious in the same bed, same blanket and hospital gown, same ward as Picture 3).
  - NEGATIVE IDENTITY: NOT a man, NOT a different woman, NOT awake, NOT opening her eyes, NOT sitting up.
  - NEGATIVE HAIR: NO bun, NO updo, NO ponytail, NO braid, NO styling change. Stays long straight hair spread on the pillow as Pictures 1 and 2.
  - NEGATIVE CLOTHING: NO street clothes, NO colored clothes, NO jewelry. Stays in the hospital attire of Picture 2.
- She is the ONLY person in the shot — no doctor, no visitor, no second character appears at any frame.

# Summary
A 5-second still night scene in the same dim ICU ward as Pictures 1-3. S1 Lín Mián lies alone and unconscious in the bed, seen from the same high-angle MEDIUM SHOT as Picture 1. She does not move — her eyes stay closed, her face peaceful, like a person simply sleeping. The only life in the frame comes from the small details: the steady green curve of the heart monitor, the slow rhythm of rain on the window, the faint rise and fall of the blanket as she breathes. The silence is heavy and meaningful — this is a girl who cannot hear anything in the outside world… or so everyone believes. {STYLE_LINE}
This is a pure static scene — NO movement of the body, NO camera move. The drama is in the stillness and the watching. The camera holds ONE steady framing for the entire 5 seconds: no push-in, no zoom, no pan, no re-framing.
EMOTION LOCK: her expression is completely calm, unconscious, neutral — NOT frowning, NOT smiling, NOT reacting to anything. She is not awake and shows no emotion.
IDENTITY LOCK: S1 stays THE pale unconscious black-haired girl of Picture 2 — NEVER swap, NEVER morph. {NEG_COMMON}

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same high-angle MEDIUM SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same composition. NO push-in, NO zoom, NO pan, NO cut, NO re-framing, NO switch to a close-up. The visible frame content stays IDENTICAL to Picture 1 from the first frame to the very last frame.
- **IDENTITY LOCK**: S1 is THE pale unconscious black-haired girl from Picture 2, in the ward of Picture 3. Her face, hair and body never change and no other character appears, from the first frame to the VERY LAST FRAME.
- **HAIR LOCK**: S1's long straight black hair stays spread on the pillow EXACTLY as Pictures 1 and 2 show — no bun, no updo, no ponytail, no braid, no styling change, no hair movement beyond the natural stillness. Applies at EVERY camera distance.
- **EMOTION LOCK**: her face stays completely calm and unconscious — eyes closed, no frown, no smile, no eyelid movement, no reaction. She is unresponsive, like deep sleep.
- **CLOTHING LOCK**: she stays in the same hospital attire and blanket as Picture 2 / Picture 3. No clothing changes at any frame.
- **STYLE LOCK**: the photorealistic cinematic 3D CG render style (cold desaturated night grade, faint green monitor glow) stays IDENTICAL to Pictures 1/2/3 throughout. NEVER shifts to live-action photos, cartoon, anime, or illustration.

# Detailed Description
- 0.0–1.5s: The high-angle MEDIUM SHOT of Picture 1 — S1 lies unconscious in the bed, long black hair spread on the pillow, face calm, eyes closed. The heart monitor beside the bed traces a steady green curve. Rain falls slowly on the window behind.
- 1.5–3.5s: Nothing moves in the frame except the subtle glow of the monitor and the very faint rise and fall of the blanket with her breathing. The stillness is almost unnatural — too quiet, too patient, as if the room itself is waiting.
- 3.5–5.0s: The same stillness holds. One last soft beep of the monitor. Her face remains peaceful and unresponsive. The frame holds Picture 1's exact composition to the very last frame.

# Soundscape
No speech, no dialogue, no narration in this shot — the character is unconscious and silent. Only low ambience: the soft steady beep of the heart monitor, gentle rain against the window, a faint distant hospital hum. The quiet feels heavy, as if something in the room is listening. No music.

# Music
None. The raw silence, rain and monitor beep carry the scene. If a pad is needed at all, it is one very low sustained cold note, barely audible, from 2.5s to the end."""

SHOT1 = {
    "shot": 1,
    "storyboard": "she_is_still_here/refs/ep01_shot05_9x16.png",
    "character": "she_is_still_here/refs/jiangche.png",
    "scene": "she_is_still_here/refs/linmian_comatose.png",
    "seconds": 5,
    "megapixels": 1.0,
    "aspect_ratio": "9:16 (Portrait Widescreen)",
    "prompt": SHOT1_PROMPT,
}
SHOT2 = {
    "shot": 2,
    "storyboard": "she_is_still_here/refs/ep01_shot07_9x16.png",
    "character": "she_is_still_here/refs/linmian_comatose.png",
    "scene": "she_is_still_here/refs/ward_cg.png",
    "seconds": 5,
    "megapixels": 1.0,
    "aspect_ratio": "9:16 (Portrait Widescreen)",
    "prompt": SHOT2_PROMPT,
}

manifest = {
    "workflow": "workflows/h3_r2v_motion_context_api.json",
    "comfy_url": "http://100.67.139.74:8188",
    "base_dir": "shots",
    "sets": [{
        "id": "shestill_v10_test",
        "title": "她还在·v10双锚+中文台词测试(病房陪伴+她听得到) 竖屏9:16",
        "aspect_ratio": "9:16 (Portrait Widescreen)",
        "target_w": 720,
        "target_h": 1280,
        "shots": [SHOT1, SHOT2],
    }]
}

json.dump(manifest, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print("WROTE", OUT)
print("shot1 chars:", len(SHOT1_PROMPT), "| shot2 chars:", len(SHOT2_PROMPT))

# 校验关键点
p1, p2 = SHOT1_PROMPT, SHOT2_PROMPT
checks = {
    "shot1 Mandarin": "MANDARIN CHINESE" in p1,
    "shot1 台词嵌入": "眠眠……你要是醒着" in p1,
    "shot1 Chinese tag": "[Chinese] 眠眠" in p1,
    "shot1 no English ban": "No English. No other language." in p1,
    "shot1 CAMERA LOCK": "CAMERA LOCK" in p1 and "no push-in" in p1,
    "shot1 STYLE LOCK": "STYLE LOCK" in p1,
    "shot2 无台词": "No speech, no dialogue" in p2,
    "shot2 CAMERA LOCK": "high-angle MEDIUM SHOT as Picture 1" in p2,
    "shot2 STYLE LOCK": "STYLE LOCK" in p2,
}
miss = [k for k, v in checks.items() if not v]
print("checks:", "ALL OK" if not miss else f"MISSING {miss}")
