# -*- coding: utf-8 -*-
"""
物体表面内容/文字专项测试批次 (电视机 / 书本 / 画)
输出: shots/screen_text_test_manifest.json
- 6 镜 × 6s × 720p(0.7MP), 单镜(无 chain)
- 目标: 测 H3 在"物体表面显示指定内容与文字"的生成边界:
    scr_01 电视·CRT 新闻画面 + 英文字幕条
    scr_02 电视·雪花屏中央中文大字「祭坛」(屏幕文字走 <d> 通道, 测试中文文字)
    scr_03 书本·翻开的魔法书 发光符文
    scr_04 书本·旧书印刷体英文段落
    scr_05 画·墙上油画人像
    scr_06 画·木牌刻字 "THE ALTAR"
- 全部镜头: 嘉玲 + 哥特厅(lantern_hall_v2) 场景锚, 物体 subject 无 picture 排最后
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_HALL = "../scenes/lantern_hall_v2.png"

JIALING_SUBJECT = (
    "a 17-year-old Chinese high school girl with wavy auburn-red hair, "
    "Asian oval face, single eyelids, solemn reserved expression, wearing a "
    "black floor-length hooded robe, carrying a small old brass lantern"
)
JIALING_CU_SUBJECT = (
    "the same 17-year-old girl in a close-up portrait, wavy auburn-red hair, "
    "Asian oval face, single eyelids, solemn determined eyes, black hooded robe"
)
HALL_SUBJECT = (
    "the vast ruined gothic castle great hall shown in Picture 1: carved stone "
    "altar in center foreground, deep perspective with two rows of stone columns "
    "vanishing into distant background, towering vaulted ceiling with broken dome, "
    "gothic arched windows on left wall, broken stone pillar on right with candelabras"
)

# 物体 subject (无 picture, 必须排在有 picture 的 subject 之后)
OBJECT_SUBJECTS = {
    "tv": (
        "an old CRT television set: thick grey boxy body, short antenna, standing "
        "on a wooden table in the dark hall, its screen is the main light source"
    ),
    "book": (
        "an ancient leather-bound grimoire lying open on a wooden table, yellowed "
        "pages, the open spread of the book is the visual focus"
    ),
    "book2": (
        "an old tattered book lying open on the wooden table, aged yellow pages "
        "densely covered with printed text"
    ),
    "painting": (
        "a huge oil painting in an ornate gilded frame hanging on the stone wall, "
        "the painted scene inside the frame is the visual focus"
    ),
    "plaque": (
        "an old carved wooden plaque mounted on the stone wall, with engraved "
        "capital letters on its surface"
    ),
}

SHOTS = [
    {
        "name": "scr_01_tv_crt_news",
        "title": "电视·CRT 新闻画面+英文字幕条",
        "object": "tv",
        "action": (
            "Medium-wide shot inside the dark ruined gothic hall matching Picture 1. "
            "Jialing matching Picture 2 stands in front of an old CRT television set "
            "on a wooden table, the cold glow of the screen lighting her face. "
            "The television screen is on and shows a black-and-white news broadcast: "
            "a news anchor talking in the center of the frame, and at the bottom of "
            "the screen a clear white caption bar with bold capital letters reading "
            "'THE ALTAR'. The screen content is crisp and clearly readable, the TV "
            "frame and screen surface are distinct. Jialing watches the screen, "
            "her eyes reflecting the moving pictures. Slow dolly in toward the "
            "television, the caption text stays centered and readable."
        ),
        "weather": "dark gothic hall, only the TV glow cuts through the darkness, faint dust",
        "grade": "cold blue TV light against warm darkness, high contrast, subtle grain",
        "sound": "thin speaker voice murmur, electric hum of the CRT, dust in the air",
        "music": "low uneasy drone, a faint distant static",
    },
    {
        "name": "scr_02_tv_static_chinese",
        "title": "电视·雪花屏中文大字「祭坛」",
        "object": "tv",
        "action": (
            "Close-medium shot of the CRT television screen inside the dark gothic hall "
            "matching Picture 1. Jialing matching Picture 2 leans close to the screen, "
            "her face lit by flickering static. The screen is filled with glitchy "
            "television static noise, and in the center of the screen, dark crimson "
            "Chinese characters appear, large and clear, slowly pulsing: "
            "<d>[Chinese] 祭坛</d>. The static flickers but the two large characters "
            "remain centered and readable. The camera holds still on the screen, "
            "then slowly pushes in toward the glowing characters."
        ),
        "weather": "dark hall, static glow as the only light, flickering shadows on Jialing's face",
        "grade": "grey-blue static, deep red text, heavy grain, high contrast",
        "sound": "loud TV static, electric crackle, faint room silence beneath",
        "music": "pulsing low synth, a rising tension tone",
    },
    {
        "name": "scr_03_book_rune",
        "title": "书本·魔法书发光符文",
        "object": "book",
        "action": (
            "Close-up over-the-shoulder shot of an ancient leather-bound grimoire lying "
            "open on a wooden table inside the hall matching Picture 1. Jialing matching "
            "Picture 2 sits behind the book, her hands resting at the page edges, "
            "candlelight flickering. On the open pages, ornate golden runic characters "
            "glow with a soft inner light, the symbols floating gently above the yellowed "
            "pages. The glowing runes are clearly visible, intricate and luminous, "
            "shifting slightly like breathing. The camera holds on the glowing text, "
            "then drifts slowly downward along the page. No one speaks."
        ),
        "weather": "dark hall, one candle, warm glow mixing with the golden light of the runes",
        "grade": "warm candle amber + golden rune light, deep shadows, fine grain",
        "sound": "candle crackle, faint paper rustle, a low hum from the glowing runes",
        "music": "soft mysterious strings, a single bell tone",
    },
    {
        "name": "scr_04_book_print",
        "title": "书本·旧书印刷英文段落",
        "object": "book2",
        "action": (
            "Close-up shot of an old tattered book lying open on the wooden table inside "
            "the hall matching Picture 1. Jialing matching Picture 2 reaches in and turns "
            "a page slowly, the paper rustling. The aged yellow pages are densely covered "
            "with small black printed text in regular lines, the letters clearly defined "
            "and readable, filling the page from top to bottom. The camera holds close on "
            "the printed lines, the text surface occupying most of the frame, sharp and "
            "detailed, then racks focus slightly as her hand crosses into the frame. "
            "The printed words are the visual subject."
        ),
        "weather": "dark hall, warm candlelight falling on the page, dust motes",
        "grade": "warm yellowed paper, brown-black ink, soft focus edges, fine grain",
        "sound": "paper rustling, candle crackle, a soft breath",
        "music": "quiet piano, a low held note",
    },
    {
        "name": "scr_05_painting_portrait",
        "title": "画·墙上油画人像",
        "object": "painting",
        "action": (
            "Medium-wide shot of a huge oil painting hanging on the stone wall of the "
            "hall matching Picture 1, its ornate gilded frame catching candlelight. "
            "Jialing matching Picture 2 stands before the painting, looking up at it. "
            "The painting shows a life-size portrait of a mysterious noblewoman in a dark "
            "dress: detailed face with pale skin and dark hair, dramatic chiaroscuro "
            "lighting, the painted surface clearly a canvas texture distinct from the "
            "stone wall. The painted content is crisp and detailed, clearly visible as "
            "a painting inside the frame. The camera slowly dollies toward the painting, "
            "Jialing's silhouette in the lower foreground."
        ),
        "weather": "dark hall, two candelabras casting warm light on the painting's surface",
        "grade": "warm candlelight on canvas, dark hall shadows, rich texture, grain",
        "sound": "candle crackle, cloth rustle, a faint ticking echo",
        "music": "somber string quartet, low and slow",
    },
    {
        "name": "scr_06_painting_plaque",
        "title": "画·木牌刻字 THE ALTAR",
        "object": "plaque",
        "action": (
            "Close-medium shot of an old carved wooden plaque mounted on the stone wall "
            "inside the hall matching Picture 1. Jialing matching Picture 2 reaches up "
            "and touches the plaque with her fingertips. The plaque has deeply engraved "
            "capital letters 'THE ALTAR' running across its surface, the carved grooves "
            "catching the candlelight with visible depth and shadow, the letters clear "
            "and readable, aged wood grain around them. The camera holds on the engraved "
            "letters, the engraved text as the visual subject, then tilts slightly as "
            "her fingers trace the carving."
        ),
        "weather": "dark hall, a single candlelight pool on the plaque, long shadows",
        "grade": "warm amber on aged wood, deep carved shadows, high contrast, grain",
        "sound": "candle crackle, fingertips scraping wood, a soft wind echo",
        "music": "low drone with a slow wood percussion tick",
    },
]


def build_subjects(sh):
    """带 picture 的 subject 排最前 (Picture 编号=Subject 序号); 物体无 picture 排最后"""
    out = []
    out.append({"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
                "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/robe/lantern"})
    out.append({"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
                "picture_retention": "fully_preserved", "note": "close-up quality reference"})
    out.append({"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
                "picture_retention": "partially_preserved", "note": "scene geometry anchor, keep the vast hall"})
    out.append({"label": OBJECT_SUBJECTS[sh["object"]], "picture": False, "retention": "fully_preserved",
                "note": "the object and its surface content, keep its form and the displayed content"})
    return out


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING
        subjects = build_subjects(sh)
        ref_list = [img, img, IMG_HALL]
        action = (
            f"{sh['action']}\n"
            f"Scene and weather: {sh['weather']}.\n"
            f"Color grade: {sh['grade']}."
        )
        shot = dict(sh)
        shot["action"] = action
        shot["dialogue"] = None
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
            "id": sh["name"],
            "title": sh["title"],
            "shots": [
                {
                    "shot": 1,
                    "storyboard": img,
                    "character": img,
                    "scene": IMG_HALL,
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
    out = ROOT / "shots" / "screen_text_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
