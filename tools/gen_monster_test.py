# -*- coding: utf-8 -*-
"""
怪物专项测试批次 (克苏鲁/人形怪/异形怪/动物形态怪)
输出: shots/monster_test_manifest.json
- 8 镜 × 6s × 720p(0.7MP), 单镜(无 chain)
- 规避: 双人同框(H3 分身)/orbit 运镜/大水体/文字
- 怪物本体靠文字描述(无参考图); 场景/角色图作 Picture 锚点
- ⚠️ builder 的 Picture 编号跟 Subject 序号绑定 → 带 picture 的 subject 必须排在无 picture 之前
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "workbuddy" / "h3-ref2va-prompt" / "scripts"))
from builder import build_prompt, check_prompt  # noqa: E402

IMG_JIALING = "../characters/jialing_wizard/reference.png"
IMG_HALL = "../scenes/lantern_hall_v2.png"      # 哥特厅(纵深版)
IMG_STREET = "../scenes/hk_old_street_night.png" # 夜街

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
STREET_SUBJECT = (
    "the night city street shown in Picture 1, wet asphalt reflecting neon, "
    "narrow old street with signboards, thin mist"
)

SHOTS = [
    {
        "name": "mon_01_cthulhu_rises",
        "title": "克苏鲁·苏醒 巨章面出海 (角色参照)",
        "char": "jialing",
        "scene": None,
        "monster": (
            "a colossal eldritch octopus-headed creature rising from the sea: a giant "
            "swollen head with a writhing mass of wet tentacles like a huge octopus, "
            "dimly glowing eyes, bat-like folded wings, glistening dark wet skin"
        ),
        "action": (
            "Extreme wide shot, stormy sea at night. Jialing matching Picture 1 is a "
            "tiny silhouette standing on a rocky cliff at the bottom edge of frame. Far "
            "out in the mist-covered sea a colossal mass rises slowly from the water: a "
            "huge swollen head with a mass of writhing tentacles like a giant octopus, "
            "wet glistening skin, two dimly glowing eyes, wings folded like a dark bat "
            "in the background. The sea churns, waves roll toward the cliff, the monster "
            "looms enormous over the horizon. The scale of the creature against the tiny "
            "cliff silhouette is the horror. Slow rising motion, then it stops, towering."
        ),
        "weather": "stormy sea at night, thick sea mist, huge moon, churning waves",
        "grade": "deep cold blue-black, monster lit by pale moonlight and lightning, heavy grain",
        "sound": "roaring waves, distant thunder, a low wet rumbling from the sea",
        "music": "massive low brass and deep choir, apocalyptic dread",
    },
    {
        "name": "mon_02_deep_one",
        "title": "深潜者·鱼人 自水中站起 (人形怪)",
        "char": "jialing",
        "scene": None,
        "monster": (
            "a deep-one fish-man humanoid: tall pale grey-green figure with shiny "
            "scales, a wide frog-like head with huge bulging unblinking eyes, gill "
            "slits on the neck, webbed hands, swaying as it stands"
        ),
        "action": (
            "Medium shot at a dark foggy beach at night. Jialing matching Picture 1 "
            "stands far back by a rocky wall, small in frame, lantern dim. From the "
            "shallow surf a tall humanoid figure rises upright out of the water: a "
            "deep-one fish-man, pale grey-green skin with shiny scales, a wide frog-like "
            "head with huge bulging unblinking eyes, gill slits on its neck, webbed "
            "hands, swaying slightly as it stands. It stares directly at the camera "
            "area, then slowly takes one step onto the wet sand. Water drips from its "
            "scales. The camera holds still, uneasy stillness, then the creature "
            "tilts its head."
        ),
        "weather": "dark foggy beach, low tide surf, thin moon behind clouds, cold light",
        "grade": "desaturated cold grade, pale moonlight, wet reflections on sand, grain",
        "sound": "gentle surf, water dripping, a wet sucking sound, distant fog",
        "music": "low uneasy strings, a single damp tone",
    },
    {
        "name": "mon_03_slender_hall",
        "title": "瘦长人·黑影 静立柱后 (人形怪)",
        "char": "jialing",
        "scene": IMG_HALL,
        "monster": (
            "an impossibly tall and thin humanoid figure: pitch black, no face, "
            "elongated arms hanging down to the knees, suit-like silhouette, "
            "utterly motionless"
        ),
        "action": (
            "Medium-wide shot inside the vast ruined gothic hall matching Picture 1. "
            "Jialing matching Picture 2 walks slowly between the stone columns, holding "
            "her brass lantern low. Between two columns far behind her, an impossibly "
            "tall and thin humanoid figure stands perfectly still: pitch black, no face, "
            "elongated arms hanging down to its knees, suit-like silhouette, utterly "
            "motionless. The camera dollies slowly forward past a column; when it clears, "
            "the figure is gone. Then the camera turns slightly and the figure is "
            "standing much closer, still motionless, right between two columns near "
            "Jialing. She has not noticed yet. Cold dread."
        ),
        "weather": "dim gothic hall, candlelight pools, long shadows, thin dust, black figure in the distance",
        "grade": "deep black shadows, warm candle pools, extreme contrast, heavy grain",
        "sound": "hollow footsteps, candle crackle, a low sub-bass thrum when the figure is near",
        "music": "minimal piano with long silences, creeping dread",
    },
    {
        "name": "mon_04_undead_street",
        "title": "丧尸·腐尸 雾中来 (人形怪)",
        "char": "jialing",
        "scene": IMG_STREET,
        "monster": (
            "a humanoid corpse zombie: grey rotting skin, hollow dark eye sockets, "
            "torn clothes, arms outstretched, jaw hanging, shambling with a broken stagger"
        ),
        "action": (
            "Medium-wide shot on the rain-soaked night street matching Picture 1. "
            "Jialing matching Picture 2 stands under a flickering neon sign, back to "
            "the camera, facing down the street. At the far end of the road, out of "
            "the mist, a humanoid corpse figure shambles into the light: grey rotting "
            "skin, hollow dark eye sockets, torn clothes, arms outstretched, jaw "
            "hanging, walking with a broken stagger. It gets closer, head twitching. "
            "The camera stays wide, the shambling figure grows larger in frame. Jialing "
            "slowly turns her head. The corpse stops mid-stride, staring."
        ),
        "weather": "rainy night, wet neon-reflecting asphalt, flickering sign, rolling mist",
        "grade": "cyan-red neon noir grade, wet reflections, deep shadows, grain",
        "sound": "steady rain, neon buzz, wet dragging footsteps, a wet groan",
        "music": "synth bass pulse, slow and ominous",
    },
    {
        "name": "mon_05_xenomorph",
        "title": "异形·猎手 倒挂阴影 (异形怪)",
        "char": None,
        "scene": IMG_HALL,
        "monster": (
            "a sleek jet-black xenomorph-like creature: smooth carapace, long domed "
            "head, thin trailing tail, claws, fluid inhuman movements, elongated jaws"
        ),
        "action": (
            "Wide shot inside the dark ruined gothic hall matching Picture 1. No people. "
            "High on the broken vaulted ceiling, barely visible in shadow, a sleek "
            "jet-black xenomorph-like creature crawls upside down with eerie precision: "
            "smooth carapace, long domed head, thin tail trailing, claws gripping the "
            "stone. It stops, head rotating slowly, then drops a short distance and "
            "clings to a pillar, its long head tilted, jaws slightly parting. A thin "
            "thread of drool catches the candlelight. It moves with fluid inhuman "
            "silence. The camera holds wide then drifts forward slightly."
        ),
        "weather": "dark gothic hall, only candlelight pools, black creature hidden in ceiling shadow",
        "grade": "high contrast, deep blacks, cold candle-amber, heavy grain",
        "sound": "distant candle crackle, a faint click of claws on stone, silence",
        "music": "low drone, a sharp percussive strike when it drops",
    },
    {
        "name": "mon_06_centipede_wall",
        "title": "节肢·虫怪 爬行石墙 (异形/动物)",
        "char": None,
        "scene": IMG_HALL,
        "monster": (
            "a monstrous segmented centipede-like creature: many thick jointed legs "
            "rippling, glossy dark chitin, long sweeping antennae, a head with small "
            "eyes and sharp mandibles, body following the curve of the wall"
        ),
        "action": (
            "Close-medium shot of a stone wall in the ruined gothic hall matching "
            "Picture 1. No people. A monstrous segmented centipede-like creature "
            "undulates across the wall surface: many thick jointed legs rippling, "
            "glossy dark chitin, long antennae sweeping, a head with multiple small "
            "eyes and sharp mandibles. It stops and raises its head, mandibles "
            "opening slowly, then resumes crawling toward the top of the frame. "
            "The leg motion is precise and many-legged, the body follows the curve "
            "of the wall. Camera holds a medium-close framing on the legs and head."
        ),
        "weather": "dim stone wall, one warm candlelight pool, shadows above",
        "grade": "dark chiaroscuro, glossy chitin highlights, cold grade, grain",
        "sound": "tiny clicking of legs, faint scratching on stone, a wet mandible click",
        "music": "nervous percussion, high staccato strings",
    },
    {
        "name": "mon_07_werewolf",
        "title": "狼人·变形 月光下起身 (动物形态)",
        "char": "jialing",
        "scene": None,
        "monster": (
            "a tall lupine werewolf: dark fur bristling, long muzzle, pointed ears, "
            "claws on its hind-leg hands, yellow glowing eyes, breath steaming"
        ),
        "action": (
            "Medium-wide shot on a moonlit moor at night. Jialing matching Picture 1 "
            "stands far behind, small silhouette holding her lantern. In the foreground "
            "center a human figure is crouched on all fours under the full moon, back "
            "arching, spine cracking as dark fur erupts along the arms and back, the "
            "jaw stretching into a muzzle, ears growing pointed, hands becoming claws. "
            "The transformation is smooth and gradual, not a cut. The creature lifts "
            "its head, eyes flashing yellow, and rises onto its hind legs as a tall "
            "lupine werewolf, fur bristling, breath steaming in the moonlight. It "
            "howls, head thrown back, then looks toward Jialing's distant silhouette."
        ),
        "weather": "bright full moon, open moor, thin grass, cold silver light, breath steam",
        "grade": "cold silver-blue moonlight, high contrast fur, fine grain",
        "sound": "night wind, cracking bones, tearing cloth, a long wolf howl",
        "music": "low drums building, a rising choir, then sudden silence",
    },
    {
        "name": "mon_08_great_spider",
        "title": "巨蛛·悬垂 自拱顶降下 (动物形态)",
        "char": None,
        "scene": IMG_HALL,
        "monster": (
            "a massive black spider the size of a horse: eight long hairy legs, glossy "
            "abdomen, small clustered eyes catching light, visible fangs, lowering "
            "itself on a thick strand of silk"
        ),
        "action": (
            "Wide low-angle shot inside the ruined gothic hall matching Picture 1. No "
            "people. From the broken vaulted ceiling above, a massive black spider the "
            "size of a horse lowers itself slowly on a thick strand of silk: eight "
            "long hairy legs unfolding and testing the air, a glossy abdomen, small "
            "clustered eyes catching the candlelight, fangs visible. It descends into "
            "the light, then stops and hangs motionless, legs slowly flexing. The "
            "camera tilts up slightly to keep it centered as it drops, then holds."
        ),
        "weather": "dark gothic hall, candlelight pools, huge spider hanging from the dark ceiling",
        "grade": "deep blacks, candle-amber on glossy body, high contrast, grain",
        "sound": "candle crackle, faint silk creak, a soft chittering, silence",
        "music": "low cello drone, a tense ticking pattern",
    },
]


def build_subjects(sh):
    """带 picture 的 subject 必须排最前 (Picture 编号=Subject 序号)"""
    out = []
    if sh["char"] == "jialing":
        out.append({"label": JIALING_SUBJECT, "picture": True, "retention": "fully_preserved",
                    "picture_retention": "fully_preserved", "note": "identical girl, keep face/hair/robe/lantern"})
        out.append({"label": JIALING_CU_SUBJECT, "picture": True, "retention": "fully_preserved",
                    "picture_retention": "fully_preserved", "note": "close-up quality reference"})
    if sh["scene"] == IMG_HALL:
        out.append({"label": HALL_SUBJECT, "picture": True, "retention": "partially_preserved",
                    "picture_retention": "partially_preserved", "note": "scene geometry anchor, keep the vast hall"})
    elif sh["scene"] == IMG_STREET:
        out.append({"label": STREET_SUBJECT, "picture": True, "retention": "partially_preserved",
                    "picture_retention": "partially_preserved", "note": "scene geometry anchor, keep the night street"})
    # 怪物本体: 无 picture, 纯文字 (必须放最后)
    out.append({"label": sh["monster"], "picture": False, "retention": "fully_preserved",
                "note": "the monster itself, keep its form/traits consistent"})
    return out


def main():
    sets = []
    n_bad = 0
    for sh in SHOTS:
        img = IMG_JIALING if sh["char"] == "jialing" else None
        subjects = build_subjects(sh)
        ref_list = []
        if img:
            ref_list += [img, img]
        if sh["scene"]:
            ref_list.append(sh["scene"])
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
                    "scene": sh["scene"],
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
    out = ROOT / "shots" / "monster_test_manifest.json"
    out.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\nmanifest -> {out}  (共 {len(sets)} 套)")
    print(f"校验: {len(SHOTS) - n_bad}/{len(SHOTS)} 通过")


if __name__ == "__main__":
    main()
