# -*- coding: utf-8 -*-
"""《她还在》EP01《第12个》12 镜 v10 六段式全集 manifest 生成器

12 镜分工：
- shot05(病房陪伴)/shot07(她听得到)：从 v10_test_manifest.json 整段复用 v10 已验证 prompt
- 其余 10 镜：按 v10 六段式模板（Subject Definitions/Summary/Retention Analysis/
  Detailed Description/Soundscape/Music）手写，与分镜构图图严格对齐
"""
import json, os, copy

ROOT = r"D:/WorkBuddy/AI_Video"
SB = "she_is_still_here/refs/ep01_shot{:02d}_9x16.png"          # 12 张 9:16 分镜图
JIANG = "she_is_still_here/refs/jiangche.png"
FANG = "she_is_still_here/refs/fangxu.png"
LIN_C = "she_is_still_here/refs/linmian_comatose.png"
SCENE_NS = "she_is_still_here/scenes/nightstreet_scene.png"
SCENE_CCTV = "she_is_still_here/scenes/cctv_scene.png"
SCENE_APT = "she_is_still_here/scenes/apt_scene.png"

STYLE_BASE = ("Photorealistic cinematic 3D CG render, UE5 quality, detailed skin shader "
              "with subsurface scattering, cold desaturated cinematic color grade, film grain")
STYLE_NO_LIVE = ("NOT live-action photography, NOT cartoon, NOT anime, NOT 2D illustration, "
                 "NOT painting, NOT watercolor, NOT oversaturated color, NOT warm happy lighting")

# 角色速查（描述+负向锁，统一全镜）
FANG_DEF = (
    "- **S1 Fāng Xù (the victim, IT night-shift technician, male)**: a gaunt Chinese man around 45, "
    "very short **grey-white hair** (mostly white, short), deeply hollow cheeks, hollow tired dark "
    "circles under the eyes, thin aging lips, faint stubble, slim aging frame — his face and worn "
    "**dark navy-blue work jacket over a grey hoodie** must look EXACTLY as Picture 2 shows.\n"
    "  - NEGATIVE IDENTITY: NOT a young man, NOT a smooth-faced man, NOT a different person, "
    "NOT a woman. Stays THE gaunt grey-haired 45-year-old of Picture 2.\n"
    "  - NEGATIVE HAIR: NO long hair, NO black hair, NO thick hair, NO bun, NO ponytail. "
    "Stays short grey-white as Picture 2.\n"
    "  - NEGATIVE CLOTHING: NO suit, NO tie, NO police uniform, NO different jacket color. "
    "Stays in the dark navy-blue work jacket + grey hoodie of Picture 2."
)
JIANG_DEF = (
    "- **S1 Jiāng Chè (plain-clothes detective, male)**: a weary Chinese man around 31, short "
    "**neat black hair**, light stubble, strong jaw, deep tired eye sockets with dark circles, "
    "faint nasolabial lines — his face and **dark charcoal jacket over a grey shirt** must look "
    "EXACTLY as Picture 2 shows.\n"
    "  - NEGATIVE IDENTITY: NOT a young smooth-faced man, NOT a different man, NOT a woman. "
    "Stays THE tired stubbled detective of Picture 2.\n"
    "  - NEGATIVE HAIR: NO longer hair, NO different hairstyle, NO beard growth. "
    "Stays short neat black as Picture 2.\n"
    "  - NEGATIVE CLOTHING: NO suit, NO tie, NO police uniform, NO badge, NO different jacket. "
    "Stays in the dark charcoal jacket + grey shirt of Picture 2."
)
JIANG_GLOVED = (
    "- **S1 Jiāng Chè (plain-clothes detective, male)**: a weary Chinese man around 31, short "
    "**neat black hair**, light stubble, deep tired eye sockets with dark circles, faint "
    "nasolabial lines — his face and **dark charcoal jacket** must look EXACTLY as Picture 2 "
    "shows. The hand visible in Picture 1 wears a **black glove** (forensic glove) — that glove "
    "stays throughout, NEVER removed.\n"
    "  - NEGATIVE IDENTITY: NOT a young smooth-faced man, NOT a different man, NOT a woman.\n"
    "  - NEGATIVE HAIR: NO longer hair, NO different hairstyle, NO beard growth.\n"
    "  - NEGATIVE CLOTHING: NO suit, NO tie, NO police uniform, NO badge, NO different jacket. "
    "Stays charcoal jacket + black glove of Picture 1/2."
)
LIN_C_DEF = (
    "- **S1 Lín Mián (female lead, comatose)**: a young Chinese woman around 22, very pale skin, "
    "long straight black hair, eyes closed as if asleep, faint IV line — her face and hospital "
    "attire must look EXACTLY as Picture 2 shows (lying unconscious, hospital gown, IV visible).\n"
    "  - NEGATIVE IDENTITY: NOT a man, NOT a different woman, NOT awake, NOT opening her eyes.\n"
    "  - NEGATIVE HAIR: NO bun, NO updo, NO ponytail, NO braid, NO styling change. "
    "Stays long straight black hair spread as Picture 2.\n"
    "  - NEGATIVE CLOTHING: NO street clothes, NO colored clothes, NO jewelry. "
    "Stays in hospital attire of Picture 2."
)
ONLY_FANG = "- He is the ONLY person in the shot — no other character appears at any frame."
ONLY_JIANG = "- He is the ONLY person in the shot — no other character appears at any frame."
ONLY_LIN = "- She is the ONLY person in the shot — no doctor, no visitor, no second character appears at any frame."

# ─── 12 镜 prompt 字典（仅 10 个新镜；05/07 复用） ───────────────────────────────
PROMPTS = {}

# ─── 镜01 雨夜机房开场（方旭吃面看手机苦笑）────────────────────
PROMPTS[1] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a dim IT server room corner at night, seen from a steady MEDIUM SHOT three-quarter angle: S1 Fāng Xù sits at a small desk on the RIGHT side of the frame, his body facing LEFT, holding chopsticks in one hand with a long strand of noodles lifted high ABOVE an instant-noodle bowl on the desk, a dark-grey computer monitor at left edge, single cold fluorescent tube above, dark server racks behind. The framing, camera angle, S1's seated position and the noodle-bowl layout MUST stay EXACTLY as Picture 1 shows for the whole shot.
{FANG_DEF}
{ONLY_FANG}

# Summary
A 5-second intimate night-shift scene in the same dim IT server room as Picture 1. S1 Fāng Xù is already in the middle of eating instant noodles when the shot begins — he is just lifting another bite with his chopsticks. He slowly finishes chewing the current bite, lowers the chopsticks onto the bowl edge, reaches casually for his phone with the other hand, glances down at the screen, his face registers a brief weary bitter smile, then he puts the phone back, picks up the chopsticks again and resumes eating. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a small-motion scene — NO walking, NO standing up, NO spin. Only mouth chewing, chopstick movement, hand picking up the phone, and a small facial reaction. The camera holds ONE steady framing for the whole 5 seconds: no push-in, no zoom, no pan.
EMOTION LOCK: his expression is quiet weary bitter loneliness — NOT laughing, NOT cheerful, NOT dramatic pain. Just a tired middle-aged technician on a lonely night shift.
IDENTITY LOCK: S1 stays THE gaunt grey-haired 45-year-old of Picture 2 — NEVER swap, NEVER morph.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT framing as Picture 1 for the entire 5-second shot — same distance, same angle, same desk-and-chair layout, same noodle-bowl position. NO push-in, NO zoom, NO pan, NO tilt, NO cut to close-up, NO pull back. The visible frame content stays IDENTICAL to Picture 1 from the first frame to the very last frame.
- **IDENTITY LOCK**: S1 is THE gaunt grey-haired victim of Picture 2. His face, hair, body, clothing, and worn jacket never change and no other character appears, from the first frame to the VERY LAST FRAME.
- **HAIR LOCK**: S1's short grey-white hair stays EXACTLY as Picture 2 shows — no length change, no color shift, no styling.
- **EMOTION LOCK**: his face stays quiet weary bitter throughout — eyes tired, mouth small, no smile breaking out, no laughter, no crying. The brief smile when looking at the phone is small and bitter, NOT broad.
- **CLOTHING LOCK**: he stays in the same dark navy-blue work jacket + grey hoodie as Picture 2. No clothing changes at any frame.
- **STYLE LOCK**: the photorealistic cinematic 3D CG render style stays IDENTICAL to Picture 1/2 throughout. NEVER shifts to live-action photos, cartoon, anime, or illustration.

# Detailed Description
- 0.0–1.8s: The MEDIUM SHOT of Picture 1 — S1's chopsticks hold a long noodle strand lifted above the bowl. His jaw moves slowly as he chews. Eyes half-down, tired. The single cold fluorescent tube hums above. The room is dead quiet except his small chewing.
- 1.8–3.4s: He lowers the chopsticks and rests them on the bowl's rim. His right hand reaches out and picks up his phone from the desk, lifts it just enough to see the screen, eyes drop to the screen. His mouth presses slightly, then the corner of his mouth curls up into a small bitter smile.
- 3.4–4.6s: He holds the smile for half a second, then puts the phone back down on the desk next to the bowl. His eyes lift briefly, looking into the middle distance for a moment, then drop back to the bowl.
- 4.6–5.0s: His right hand returns to the chopsticks. He lifts another bite of noodles. The frame holds Picture 1's exact composition to the very last frame.

# Soundscape
No speech, no dialogue, no narration — he does not speak. Only the small sounds of his chewing, a soft chopstick-on-bowl click, the quiet hum of the server racks, and the distant low fluorescent buzz of the room. He may let out one very small sigh when putting the phone down. No music.

# Music
None. Pure ambience. If absolutely needed, one very low sustained cold pad note underneath, barely audible, from 2s to the end."""

# ─── 镜02 方旭倒下（僵直+胸口血+缓缓前倾伏桌）────────────────
PROMPTS[2] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — the same dim IT server room corner as the previous shot, MEDIUM SHOT three-quarter angle: S1 Fāng Xù sits at the same desk, his body slightly hunched forward in a sudden **rigid shock pose**, one hand dangling limply off the desk, the instant-noodle bowl **already tipped over** with noodles spilling onto the desk and a small pool of dark broth, and on his chest at his sternum a **dark red wet stain** (the source of the shock) is visible against his dark navy-blue work jacket. A grey monitor is at left edge. The framing, camera angle, desk layout, tipped-bowl position and the red chest stain MUST stay EXACTLY as Picture 1 shows for the whole shot.
{FANG_DEF}
{ONLY_FANG}

# Summary
A 5-second death-onset scene in the same dim server room as Picture 1. S1 Fāng Xù has just suffered a sudden internal shock at his chest — the moment is **already frozen at the start of the shot**: his body is rigid, his hand has just released the chopsticks, the bowl is tipping over, the chest stain is already visible. Over the 5 seconds, the stillness holds for a beat, then — slowly, heavily — his rigid body starts to **slump forward and down** toward the desk, as gravity wins, his head and shoulders sink until his forehead nearly touches the spilled noodles, his dangling arm goes fully slack. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a slow collapse, NOT a sudden fall — no spin, no standing, no jump. Just a rigid sitting body slowly giving way under gravity. The camera holds ONE steady MEDIUM SHOT for the whole 5 seconds: no push-in, no zoom, no pan.
EMOTION LOCK: his face goes from stunned shock to blank slack as he loses consciousness — NOT pained screaming, NOT thrashing, NOT dramatic gasping. A quiet, hollow passing.
IDENTITY LOCK: S1 stays THE gaunt grey-haired 45-year-old of Picture 2.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same desk layout, same tipped bowl, same red chest stain position. NO push-in, NO zoom, NO pan, NO cut. Visible frame content stays IDENTICAL to Picture 1 from first frame to last.
- **STAIN & BOWL LOCK (highest priority)**: the dark red wet stain on S1's sternum (Picture 1) and the tipped noodle bowl with spilled noodles on the desk MUST stay in EXACTLY the same position and look throughout the shot — no new blood, no blood drip, no blood expansion, no bowl movement, no noodle re-arrangement. The damage is frozen as Picture 1 shows.
- **IDENTITY LOCK**: S1 is THE gaunt grey-haired victim of Picture 2. His face, hair, work jacket, hoodie, and overall body never change to anyone else.
- **HAIR LOCK**: S1's short grey-white hair stays EXACTLY as Picture 2 shows — no length change, no styling.
- **EMOTION LOCK**: face transitions slowly from stunned shock (eyes wide unfocused) to slack blank (eyes half-close) — NOT screaming, NOT dramatic pain, NOT crying. The body simply gives out.
- **CLOTHING LOCK**: stays in dark navy-blue work jacket + grey hoodie of Picture 2. The red stain is on the jacket.
- **STYLE LOCK**: photorealistic cinematic 3D CG render — stays IDENTICAL to Picture 1/2 throughout. NEVER shifts to live-action, cartoon, anime, illustration.

# Detailed Description
- 0.0–1.6s: The MEDIUM SHOT of Picture 1 frozen in shock — S1 sits rigid, eyes wide and unfocused, the noodle bowl tipped with noodles spilling, the red chest stain visible. His free hand has just gone limp off the desk. He does not move. The room holds its breath.
- 1.6–3.6s: Slowly, as gravity wins, his rigid torso begins to lean forward and downward. His shoulders drop. His dangling arm sways with the lean, fingers fully loose. The stain stays fixed on his jacket. The bowl stays tipped.
- 3.6–4.8s: His body sinks further forward. His head lowers toward the spilled noodles on the desk. His eyes begin to half-close as consciousness drains. The spilled broth on the desk catches a small glint from the fluorescent tube.
- 4.8–5.0s: His forehead is now almost touching the noodles on the desk surface. His body is fully slack. The frame holds the same composition, the stain and bowl exactly as Picture 1, to the very last frame.

# Soundscape
No speech, no dialogue, no narration. A single sharp small intake of breath at the very first frame, then a slow uneven exhale that fades by 3s. The instant-noodle bowl **does not** make any sound after Picture 1's frozen moment. The room's fluorescent hum continues. A faint wet cough around 2.5s. No music.

# Music
None. The room's cold silence and the fluorescent tube hum carry the death. No score."""

# ─── 镜03 江彻推开机房门（手电扫视）──────────────────────────
PROMPTS[3] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a dim IT server room at night seen from INSIDE the room looking toward the door: S1 Jiāng Chè is framed in the open glass doorway on the RIGHT side of the frame, his body angled inward, one hand holding a small flashlight whose **cold white beam cuts across the dark room toward the LEFT** of the frame, his weary face half-lit by the beam and half by faint rack-light glow, rows of dark server racks receding to the left, dark corridor behind him through the glass door. The framing, camera angle, S1's doorway position and the flashlight beam direction MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_DEF}
{ONLY_JIANG}

# Summary
A 5-second crime-scene-entry scene in the same dim server room as Picture 1. S1 Jiāng Chè has just pushed the glass door open and is already standing in the doorway when the shot begins, flashlight raised. Over the 5 seconds, he **slowly pans the flashlight beam** leftward across the racks, his eyes following the beam, then **takes two cautious small steps inward** off the door threshold deeper into the room, sweeping the light further left. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a small-motion investigative scene — NO spin, NO turn-around, NO big walk. Just a flashlight sweep and two small forward steps. The camera holds ONE steady MEDIUM SHOT.
EMOTION LOCK: alert, focused, guarded — NOT dramatic, NOT running, NOT fearful. A tired detective doing his job.
IDENTITY LOCK: S1 stays THE tired stubbled man of Picture 2.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same door-frame composition. NO push-in, NO zoom, NO pan, NO cut. Visible frame stays IDENTICAL to Picture 1 from first frame to last.
- **IDENTITY LOCK**: S1 is THE tired stubbled detective of Picture 2. His face, hair, jacket never change.
- **HAIR LOCK**: short neat black hair stays as Picture 2 throughout.
- **EMOTION LOCK**: alert guarded focus throughout — NOT surprise, NOT fear, NOT anger. Eyes follow the beam, jaw tight.
- **CLOTHING LOCK**: dark charcoal jacket + grey shirt of Picture 2.
- **STYLE LOCK**: photorealistic cinematic 3D CG render — IDENTICAL to Picture 1/2 throughout.

# Detailed Description
- 0.0–1.5s: The MEDIUM SHOT of Picture 1 — S1 stands in the doorway, flashlight beam already pointing left across the racks, his face half-lit. He breathes evenly. The corridor behind him is dark.
- 1.5–3.0s: He slowly rotates his wrist so the beam **pans leftward** across more racks. His eyes track the beam. The light catches glass and metal briefly. His head tilts a fraction to follow.
- 3.0–4.6s: He takes **two small cautious steps** inward off the door threshold, deeper into the room. His left shoulder enters slightly. The beam continues to sweep further left. His jaw sets.
- 4.6–5.0s: He pauses mid-step, beam now angled far left, eyes locked on something unseen off-frame. The frame holds Picture 1's exact composition to the very last frame.

# Soundscape
No speech, no dialogue, no narration. His shoes on the floor — two small soft scuffs when he steps inward. The faint click of the flashlight's button at the very first frame (already on). The room's deep server-rack hum. No music.

# Music
None. Pure ambient room hum. If absolutely needed, one very low sustained bass note, barely audible, from 3s."""

# ─── 镜04 墙挂老式电话 + 306 + 黑手套手 ──────────────────────────
PROMPTS[4] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — an EXTREME CLOSE-UP of an **old-fashioned wall-mounted black telephone** (vintage rotary/push-button office phone with a separate hanging handset) on a dark cold-tinted wall: the small monochrome LCD screen of the phone glows pale and displays the digits **306** clearly as the sender indicator of an unread message, and a **male hand wearing a black forensic glove** enters from the RIGHT side of the frame, reaching toward the phone's handset or keypad. The framing, camera angle, the phone's exact position on the wall and the gloved hand's entry position MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_GLOVED}
{ONLY_JIANG}

# Summary
A 5-second extreme close-up evidence moment in the same dim server room as Picture 1. The wall-mounted old phone's screen is glowing with one incoming message from "306". S1 Jiāng Chè's **black-gloved hand** (his right hand) enters from the right edge of the frame, reaches slowly and carefully toward the handset or the keypad — hesitates half a second just above the receiver, then pulls back slightly without picking up, and retreats out of frame. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a micro-motion scene — only the gloved hand moves slightly in and out. NO big arm motion, NO picking up the handset. The camera holds ONE steady EXTREME CLOSE-UP for the whole 5 seconds.
EMOTION LOCK: the hand is careful, restrained, forensic — NOT grabbing, NOT slapping, NOT dramatic. The body language of a tired detective who sees a clue he doesn't want to touch yet.
IDENTITY LOCK: only the gloved hand is visible — S1's face is NOT in this shot. His hand wears the black glove EXACTLY as Picture 1.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same EXTREME CLOSE-UP as Picture 1 for the entire 5 seconds — same distance, same angle, same phone position on the wall, same screen glow, same 306 digits visible. NO push-in, NO zoom, NO pan, NO cut.
- **PHONE & SCREEN LOCK (highest priority)**: the wall-mounted old phone, the screen position, the pale glow color and the **digits 306** MUST stay EXACTLY as Picture 1 shows — no other digits, no readable message text, no other UI elements. The digits 306 stay clearly readable throughout.
- **GLOVE LOCK**: the visible hand wears a **black forensic glove** EXACTLY as Picture 1 shows. The glove NEVER disappears, NEVER turns bare skin, NEVER changes color.
- **NO FACE**: S1's face is NOT in this shot — only the gloved hand. NO face appears, NO reflection of a face in the phone's screen.
- **STYLE LOCK**: photorealistic cinematic 3D CG render — IDENTICAL to Picture 1 throughout.

# Detailed Description
- 0.0–1.5s: The EXTREME CLOSE-UP of Picture 1 — the wall-mounted old phone glows with 306 on its small screen. The black-gloved hand is already entering from the right edge, hovering near the handset area. The room is silent except a faint hum.
- 1.5–3.2s: The gloved hand moves slowly a few centimeters closer toward the handset, fingers slightly curling inward as if about to lift it — then hesitates, holds. The 306 stays clearly readable. The pale glow catches a soft reflection on the black glove.
- 3.2–4.4s: The hand pulls back half the distance it came, retreats a few centimeters, as if deciding not to disturb the evidence yet. The 306 keeps glowing.
- 4.4–5.0s: The gloved hand leaves the frame to the right edge, almost gone. The phone screen keeps glowing with 306 alone. Frame holds Picture 1's exact composition to the very last frame.

# Soundscape
No speech, no dialogue, no narration. A single soft fabric rustle as the glove shifts. The faint electrical hum of the old phone. No music.

# Music
None. Pure silence broken by the soft hum. If absolutely needed, one very low sustained cold note from 3s, barely audible."""

# ─── 镜06 双手相握特写（黑手套手握昏迷女手）──────────────────
PROMPTS[6] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — an EXTREME CLOSE-UP at a hospital bedside at night: a **black-gloved male hand** (rough, square knuckles, dark grey jacket sleeve visible at the wrist) gently clasping a **pale thin unconscious female hand** (with a blue-green IV-line needle taped on the back of her hand), their fingers softly interlocked, cold blue-green ward light, shallow depth of field, the rest of the frame dark. The framing, camera angle, both hands' position and the IV-tape detail MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_GLOVED}
{LIN_C_DEF}
- The two hands are the ONLY visible content — **NO face, NO body, NO second hand appears**. The shot is strictly the two hands and the IV tape.

# Summary
A 5-second tender-devotion extreme close-up at the same hospital bedside as Picture 1. The black-gloved hand of S1 Jiāng Chè holds the pale hand of S2 Lín Mián softly. Over the 5 seconds, his thumb **slowly and gently strokes** the back of her hand once or twice — that is the only motion. The unconscious hand does not move. The IV line catches the ward light. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a tiny-motion scene — only the thumb moves. The camera holds ONE steady EXTREME CLOSE-UP.
EMOTION LOCK: quiet devotion, tenderness, slow exhaustion — NOT dramatic, NOT sobbing, NOT romantic music swell.
IDENTITY LOCK: S1's hand (black glove, dark jacket sleeve) stays THE detective's hand from Picture 1; S2's hand stays THE unconscious girl's hand from Picture 2.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same EXTREME CLOSE-UP as Picture 1 for the entire 5 seconds — same distance, same angle, same hand positions, same IV-tape location. NO push-in, NO zoom, NO pan, NO cut. Visible frame stays IDENTICAL to Picture 1 from first frame to last.
- **HANDS & GLOVE LOCK (highest priority)**: S1's hand wears the **black forensic glove** of Picture 1 — NEVER bare, NEVER different color. S2's hand stays pale, thin, unconscious — NEVER moves, NEVER grasps back. The IV-tape stays in EXACTLY the same spot.
- **NO FACE**: NO face of either character appears at any frame — only hands. NO reflection of a face.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, cold blue-green ward grade — IDENTICAL to Picture 1/2 throughout.

# Detailed Description
- 0.0–1.6s: The EXTREME CLOSE-UP of Picture 1 — the black-gloved hand holds the pale unconscious hand, fingers softly interlocked, IV tape on her hand visible. The room is dead quiet.
- 1.6–3.6s: S1's thumb **slowly strokes** the back of her hand once from knuckle to wrist. Her hand does not move. The glove catches a soft pale reflection from the ward light. The IV line stills.
- 3.6–4.8s: The thumb rests on her knuckle for a long breath. Both hands still. Only the cold blue-green ward light holds the frame.
- 4.8–5.0s: The hands stay exactly as Picture 1. Frame holds to the very last frame.

# Soundscape
No speech, no dialogue, no narration. The faint slow beep of a heart monitor far in the background. A single very soft breath (his) around 2s. No music.

# Music
None. The monitor beep and silence carry the scene. If needed, one very low cold pad note barely audible from 3s."""

# ─── 镜08 智能手机骤亮 306（消息气泡）────────────────────
PROMPTS[8] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — an EXTREME CLOSE-UP in near-total darkness: a **modern smartphone** is held in a male hand, the phone's screen has just lit up cold white, displaying an incoming-message thread whose **sender label reads 306** at the top and shows **green-tinted chat bubbles** (the actual message text inside the bubbles is **deliberately blurred and unreadable**), the phone's screen is the ONLY light source in the frame, the hand holding the phone is barely visible in the screen's glow at the bottom of the frame. The framing, camera angle, phone position in the hand and the 306 sender label MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_GLOVED}
- Only the hand and the phone are visible — **NO face, NO background, NO other object appears**.

# Summary
A 5-second supernatural-pulse extreme close-up in near-total darkness as Picture 1. The smartphone screen has just lit up with one message from "306". The screen glows cold white against the dark. Over the 5 seconds, the hand holding the phone **trembles once slightly** then steadies, the screen stays lit, the green bubbles stay, no readable Chinese text appears — the message content stays impossible to read. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a micro-motion scene — only a tiny hand tremor. The camera holds ONE steady EXTREME CLOSE-UP.
EMOTION LOCK: cold unease, supernatural chill — NOT fear, NOT shock. A detective who sees a number he shouldn't be seeing.
IDENTITY LOCK: only the hand is visible, wearing the black glove as Picture 1.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same EXTREME CLOSE-UP as Picture 1 for the entire 5 seconds — same distance, same angle, same phone position, same screen glow color.
- **SCREEN & SENDER LOCK (highest priority)**: the phone screen stays **lit cold white** the entire time, the **sender label "306"** stays clearly readable at the top, the **green chat bubbles** stay visible. The actual Chinese text inside the bubbles stays **deliberately blurred and unreadable** — never rendered as readable Chinese characters.
- **GLOVE LOCK**: the holding hand wears the **black forensic glove** of Picture 1.
- **NO FACE**: NO face appears at any frame. NO readable Chinese text appears.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, dark cold blue grade, screen-only light — IDENTICAL throughout.

# Detailed Description
- 0.0–1.4s: The EXTREME CLOSE-UP of Picture 1 — the phone screen already glowing cold white with 306 at the top, green chat bubbles visible but unreadable. The gloved hand is steady at the bottom edge.
- 1.4–2.6s: The hand **trembles once** very slightly — a tiny visible shake of the phone against the darkness — then steadies. The screen glow stays. The 306 stays.
- 2.6–4.4s: The screen keeps glowing. The bubbles stay unreadable. The hand stays still. The dark around the phone stays pitch black.
- 4.4–5.0s: Frame holds Picture 1's exact composition to the very last frame. 306 still glowing.

# Soundscape
No speech, no dialogue, no narration. A single soft phone-vibration buzz at the very first frame, then silence. The room is utterly still. No music.

# Music
A single very low sustained cold synth drone from 0.5s to the end, very subtle, never louder than the silence around it."""

# ─── 镜09 雨夜街头勘查（江彻站街边黑车旁）────────────────
PROMPTS[9] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a dim night-time residential street in light rain, seen from a MEDIUM SHOT three-quarter angle: S1 Jiāng Chè stands on the WET ASPHALT on the RIGHT side of the frame next to an **unmarked black sedan** with its driver-side door open, behind him an OLD LOW apartment building recedes to the LEFT, rain streaks slanting through cold streetlamp light, wet pavement reflecting cold white light, the whole frame cold-toned and damp. The framing, camera angle, S1's standing position next to the car and the streetlamp direction MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_DEF}
{ONLY_JIANG}

# Summary
A 5-second lonely-investigation scene in the same rainy old street as Picture 1. S1 Jiāng Chè has just stepped out of the unmarked black sedan and is already standing on the wet pavement when the shot begins. Over the 5 seconds, he slowly turns his head upward and to the LEFT, looking up at the old low apartment buildings ahead, his weary face catching the cold streetlamp, then his eyes drop back down. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a small-motion scene — only head turn and breathing. NO walking into frame, NO running, NO spin.
EMOTION LOCK: quiet, tired, lonely investigator resolve — NOT dramatic, NOT fearful, NOT surprised.
IDENTITY LOCK: S1 stays THE tired stubbled detective of Picture 2.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same car-on-right, buildings-on-left composition. NO push-in, NO zoom, NO pan.
- **RAIN LOCK**: light rain falls steadily throughout — no sudden downpour, no rain stopping.
- **CAR LOCK**: the unmarked black sedan stays with its driver door open as Picture 1.
- **IDENTITY LOCK**: S1 is THE tired stubbled detective of Picture 2.
- **HAIR & CLOTHING LOCK**: stays short black hair + dark charcoal jacket + grey shirt of Picture 2. Hair gets slightly wet from rain but stays neat black.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, cold wet street grade — IDENTICAL throughout.

# Detailed Description
- 0.0–1.8s: The MEDIUM SHOT of Picture 1 — S1 stands on the wet asphalt next to the open black sedan, looking forward. Rain slants through the streetlamp. The old low apartment building recedes to the left.
- 1.8–3.6s: He slowly tilts his head upward and to the LEFT, lifting his chin to look up at the apartment windows. His face catches the cold streetlamp light. His jaw is set.
- 3.6–4.6s: His eyes hold on something unseen up there for a beat, then his gaze slowly drops back down to street level. A faint cold breath comes out.
- 4.6–5.0s: Frame holds Picture 1's exact composition to the very last frame. Rain keeps slanting. The car door stays open.

# Soundscape
No speech, no dialogue, no narration. The steady hush of light rain on asphalt and on his jacket. A distant rumble of thunder very low and far. No music.

# Music
None. Pure rain ambience."""

# ─── 镜10 走廊尽头白衣影子 ────────────────────────────
PROMPTS[10] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — an old apartment-building corridor at night, WIDE SHOT: S1 Jiāng Chè is seen FROM BEHIND, standing in the **right foreground** facing INWARD down the corridor, while at the FAR END of the dim corridor a faint, blurred, **semi-transparent female silhouette** in a white garment flickers — a ghost-like translucent figure whose face is unreadable and whose outline is soft. Cold pale fluorescent light from a corridor ceiling tube, big empty negative space around both figures. The framing, camera angle, S1's back-facing position on the right and the silhouette's position at the corridor end MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_DEF}
- **Silhouette (the ghostly female figure)**: NOT a real solid person — translucent, blurred edges, face unreadable, the body faintly luminous as if made of cold light, white garment merging with the corridor's pale glow.
  - NEGATIVE: NOT a clearly visible solid face, NOT a sharp photographic person, NOT someone with distinct identity features. Stays translucent and unreadable throughout.

# Summary
A 5-second supernatural-encounter wide shot in the same corridor as Picture 1. S1 Jiāng Chè has just entered the corridor and is already standing with his back to the camera, while the faint white silhouette at the far end flickers once and is gone. Over the 5 seconds, the silhouette **lingers for the first 2 seconds, then fades out completely**; S1 stays still, his head perhaps turning a fraction toward the end but not stepping. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a near-static scene — only the silhouette fades. The camera holds ONE steady WIDE SHOT.
EMOTION LOCK: S1 is unaware for the first 3s, then a slow cold chill registers — NOT dramatic fear, NOT screaming, NOT running.
IDENTITY LOCK: S1 stays THE tired stubbled detective of Picture 2 (seen from behind). The silhouette stays translucent and unreadable.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same WIDE SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same corridor-end composition. NO push-in, NO zoom, NO pan.
- **SILHOUETTE LOCK (highest priority)**: the faint female silhouette appears AT THE FAR END of the corridor — translucent, blurred, face unreadable, white garment. NEVER becomes a clear solid person. NEVER shows a distinct face. NEVER sharpens.
- **SILHOUETTE FADE**: the silhouette is visible (Picture 1) at 0–2s, fading by 3s, gone by 4s.
- **JIANG LOCK**: S1 is seen from BEHIND on the right, in the dark charcoal jacket + grey shirt of Picture 2 — face NOT visible.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, cold pale fluorescent corridor grade — IDENTICAL throughout.

# Detailed Description
- 0.0–2.0s: The WIDE SHOT of Picture 1 — S1 stands with his back to the camera on the right, the faint white silhouette flickers at the corridor end, translucent and unreadable.
- 2.0–3.4s: The silhouette **begins to fade**, edges dissolving into the corridor's fluorescent pale glow. S1 still hasn't noticed, his posture unchanged.
- 3.4–4.4s: The silhouette is almost gone, a faint wisp remaining. S1's head turns a tiny fraction, just beginning to register something at the corridor end.
- 4.4–5.0s: The silhouette is gone. S1 stands still, his head half-turned. Frame holds Picture 1's exact composition to the very last frame.

# Soundscape
No speech, no dialogue, no narration. The corridor's silent fluorescent hum. A single very faint distant chime or breath around 2.5s, almost not audible. No music.

# Music
A single very low sustained cold synth drone from 0.5s, swelling very slightly when the silhouette fades at 3s, fading out by 5s."""

# ─── 镜11 书桌发现半张名单 ─────────────────────────────
PROMPTS[11] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — a cluttered cramped apartment study desk at night, MEDIUM SHOT: S1 Jiāng Chè stands half in shadow BESIDE the desk on the right side of the frame, one hand holding a **folded yellowing paper** (a torn half-list of names, handwriting visible but the actual characters **deliberately blurred and unreadable**), an OLD CRT monitor and stacks of instant-noodle cups and documents on the desk, cold fluorescent light from a desk lamp. The framing, camera angle, S1's standing position and the yellow paper in his hand MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_DEF}
{ONLY_JIANG}

# Summary
A 5-second clue-discovery scene in the same cramped apartment study as Picture 1. S1 Jiāng Chè has just pulled the folded yellow paper out of a drawer and is already standing beside the desk, holding it. Over the 5 seconds, his eyes slowly scan down the paper, his head tilting slightly, registering what he reads (or can't read), his face tightening just a fraction. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a small-motion scene — only eyes scanning and head tilt. The camera holds ONE steady MEDIUM SHOT.
EMOTION LOCK: quiet recognition, cold focus — NOT surprise, NOT anger, NOT dramatic reveal. A detective reading a clue.
IDENTITY LOCK: S1 stays THE tired stubbled detective of Picture 2.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same MEDIUM SHOT as Picture 1 for the entire 5 seconds — same distance, same angle, same desk layout, same CRT monitor, same stacks. NO push-in, NO zoom, NO pan.
- **PAPER LOCK (highest priority)**: the folded yellowing paper stays in S1's hand, the handwriting stays **deliberately blurred and unreadable** — no readable Chinese characters, no sharp text rendering. The paper may shift slightly but never folds differently.
- **IDENTITY LOCK**: S1 stays THE tired stubbled detective of Picture 2.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, cold fluorescent desk-lamp grade — IDENTICAL throughout.

# Detailed Description
- 0.0–1.6s: The MEDIUM SHOT of Picture 1 — S1 stands beside the desk holding the yellow paper, eyes already on it. The CRT and instant-noodle stacks glow faintly.
- 1.6–3.2s: His eyes **slowly scan downward** along the paper, his head tilting a fraction to follow. The fluorescent desk light catches the paper's edge.
- 3.2–4.4s: He pauses mid-paper, eyes fixed on a specific (blurred) line for a beat. His jaw tightens just a fraction.
- 4.4–5.0s: Frame holds Picture 1's exact composition to the very last frame. The yellow paper stays in his hand, the writing still unreadable.

# Soundscape
No speech, no dialogue, no narration. A single soft paper-rustle when his thumb shifts on the paper. The faint CRT buzz. No music.

# Music
None. Pure room ambience. If absolutely needed, one very low sustained bass note from 2.5s."""

# ─── 镜12 短信钩子（微信对话 306）─────────────────────────
PROMPTS[12] = f"""# Subject Definitions
- **Picture 1 (composition reference)**: the full frame from Picture 1 — an EXTREME CLOSE-UP in PURE DARKNESS: a **modern smartphone** is held in a male hand, the screen glowing as the ONLY light source in the frame, displaying a WeChat-style chat conversation with a sender labeled **306** at the top and several **green outgoing/received message bubbles** below (the actual Chinese characters inside the bubbles are **deliberately blurred and unreadable green text blocks**), the holding hand slightly out of focus at the bottom, huge black negative space above the phone. The framing, camera angle, phone position and the 306 sender label MUST stay EXACTLY as Picture 1 shows for the whole shot.
{JIANG_GLOVED}
- Only the hand and the phone screen are visible — **NO face, NO background object**.

# Summary
A 5-second final-hook extreme close-up in pure darkness as Picture 1. The phone screen is already lit with the 306 WeChat chat open. Over the 5 seconds, the hand holds the phone steady, the screen keeps glowing, the green bubbles stay unreadable. A single new message bubble from 306 **appears at the bottom of the conversation** around 3s — still unreadable Chinese text. {STYLE_BASE}. {STYLE_NO_LIVE}.
This is a near-static scene — only one new message bubble appears. The camera holds ONE steady EXTREME CLOSE-UP.
EMOTION LOCK: cold finality, the episode ends in suspense — NOT shock, NOT panic, NOT drama.
IDENTITY LOCK: the gloved hand stays THE detective's hand from Picture 1.

# Retention Analysis
- **CAMERA LOCK (highest priority)**: the camera holds the EXACT same EXTREME CLOSE-UP as Picture 1 for the entire 5 seconds — same distance, same angle, same phone position, same screen-as-only-light composition.
- **SCREEN & SENDER LOCK (highest priority)**: the WeChat chat stays open with **306** clearly readable at the top. The existing green bubbles stay. All Chinese text inside the bubbles stays **deliberately blurred and unreadable green text blocks** — never rendered as readable Chinese characters.
- **NEW BUBBLE EVENT**: a single new green bubble appears at the bottom of the conversation around 3s — still unreadable Chinese text.
- **GLOVE LOCK**: the holding hand wears the **black forensic glove** of Picture 1 throughout.
- **NO FACE**: NO face appears at any frame.
- **STYLE LOCK**: photorealistic cinematic 3D CG render, pitch-dark frame with screen-only glow — IDENTICAL throughout.

# Detailed Description
- 0.0–1.6s: The EXTREME CLOSE-UP of Picture 1 — phone screen glowing with 306 at top and existing unreadable green bubbles below. The black-gloved hand is steady at the bottom edge.
- 1.6–3.0s: The screen holds. The bubbles stay. The 306 stays. The hand doesn't move. The dark around the phone stays pitch black.
- 3.0–3.6s: A single new **green chat bubble** fades in at the bottom of the conversation — the actual Chinese text inside is blurred and unreadable.
- 3.6–5.0s: The new bubble stays. The screen holds. The frame holds Picture 1's exact composition to the very last frame. The episode's hook lands in silence.

# Soundscape
No speech, no dialogue, no narration. A single soft phone-message tone at 3s (the new bubble arrival), then silence. No music.

# Music
A single very low sustained cold synth drone from 0.5s, swelling very slightly when the new bubble appears at 3s, holding to the end. No score, no percussion."""


# ─── 复用 v10 镜05/镜07 prompt ──────────────────────────────
def load_v10_prompts():
    src = os.path.join(ROOT, "shots", "she_is_still_here", "v10_test_manifest.json")
    d = json.load(open(src, encoding="utf-8"))
    sh = d["sets"][0]["shots"]
    return {5: sh[0]["prompt"], 7: sh[1]["prompt"]}


# ─── 组装全集 manifest ──────────────────────────────────────
def build_manifest():
    v10 = load_v10_prompts()
    # 槽映射
    char_map = {1: FANG, 2: FANG, 3: JIANG, 4: JIANG,
                5: JIANG, 6: JIANG, 7: LIN_C,
                8: JIANG, 9: JIANG, 10: JIANG, 11: JIANG, 12: JIANG}
    scene_map = {9: SCENE_NS, 10: SCENE_CCTV, 11: SCENE_APT}

    shots = []
    for n in range(1, 13):
        if n == 5 or n == 7:
            prompt = v10[n]
            sb = SB.format(n)
            # v10 镜05 char=jiangche scene=linmian_c; 镜07 char=linmian_c scene=ward_cg
            if n == 5:
                ch, sc = JIANG, LIN_C
            else:
                ch, sc = LIN_C, "she_is_still_here/refs/ward_cg.png"  # 复用 v10 Picture3=ward_cg
        else:
            prompt = PROMPTS[n]
            sb = SB.format(n)
            ch = char_map[n]
            sc = scene_map.get(n)
        shots.append({
            "shot": n,
            "storyboard": sb,
            "character": ch,
            "scene": sc,
            "seconds": 5,
            "megapixels": 1.0,
            "aspect_ratio": "9:16 (Portrait Widescreen)",
            "prompt": prompt,
        })

    manifest = {
        "workflow": "workflows/h3_r2v_motion_context_api.json",
        "comfy_url": "http://100.67.139.74:8188",
        "base_dir": "shots",
        "sets": [{
            "id": "shestill_ep01_full",
            "title": "她还在·EP01《第12个》全集12镜 v10 六段式 竖屏9:16",
            "aspect_ratio": "9:16 (Portrait Widescreen)",
            "target_w": 720,
            "target_h": 1280,
            "shots": shots,
        }],
    }
    return manifest


if __name__ == "__main__":
    out = os.path.join(ROOT, "shots", "she_is_still_here", "ep01_full_manifest.json")
    m = build_manifest()
    json.dump(m, open(out, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("WRITTEN", out, "shots=", len(m["sets"][0]["shots"]))
    print("total chars prompts:", sum(len(s["prompt"]) for s in m["sets"][0]["shots"]))