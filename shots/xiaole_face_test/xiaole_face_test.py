# -*- coding: utf-8 -*-
"""
小乐法师 v2 图 还原度测试：双人近景对话拜师片段
- 参考图：xiaole_wizard_v2.png (新小乐), jialing_ref.png (嘉玲), hogwarts_hall.png (礼堂)
- 镜头：近景双人对话，嘉玲教小乐念咒，两人同框，脸部特写级
- 提交后下载到 F:/WorkBuddy/AI_Video/shots/xiaole_face_test/output/
用法:
    python xiaole_face_test.py
"""
import copy
import json
import sys
import urllib.request
from pathlib import Path

sys.path.insert(0, "C:/Users/Lionel/.workbuddy/skills/h3-ref2va-prompt/scripts")
from builder import build_prompt, check_prompt  # noqa: E402

BASE = "http://100.67.139.74:8188"
WORK = Path(r"F:/WorkBuddy/AI_Video/shots/xiaole_face_test")
TEMPLATE = Path(r"c:/Users/Lionel/WorkBuddy/Claw/.tmp_frames_zhou2/shots/shot05.json")

# 台式机 ComfyUI input 目录中已上传的文件名
XIAOLE_V2 = "xiaole_wizard_v2.png"
JIALING = "jialing_ref.png"
HALL = "hogwarts_hall.png"

# ---------- 角色定义（顺序 = refs 顺序） ----------
XIAOLE_SUB = dict(
    label="a 7-year-old Chinese boy, second grade, short black hair, transparent round-frame "
          "glasses, wearing a navy-blue wizard robe with a maroon inner cloak, white shirt and "
          "grey knitted vest, red-and-yellow striped tie, holding a wooden wand, innocent "
          "excited face",
    retention="fully_preserved",
    picture_retention="fully_preserved - boy face, round glasses, navy robe, wand",
    note="the novice apprentice, identical in this shot",
    picture=True,
)
JIALING_SUB = dict(
    label="a 17-year-old Chinese high school girl with wavy auburn-red hair, Asian oval face, "
          "single eyelids, cool detached big-sister aura, wearing Hogwarts style dark robe, "
          "red and yellow striped scarf, grey pleated skirt, holding a wooden wand",
    retention="fully_preserved",
    picture_retention="fully_preserved - face, auburn-red wavy hair, robe, scarf",
    note="the senior female teacher, identical in this shot",
    picture=True,
)
HALL_SUB = dict(
    label="an old Hogwarts style magic school hall: ancient stone walls, tall arched "
          "windows with amber stained glass, floating candles, long wooden tables, "
          "warm torchlight, soft bokeh",
    retention="fully_preserved",
    picture_retention="fully_preserved - stone walls, candles, warm light, bokeh",
    note="the scene (background)",
    picture=True,
)

# ---------- 单镜剧本：近景双人对话 ----------
SHOTS = [
    dict(
        name="shot01", seconds=6, refs=[XIAOLE_V2, JIALING, HALL],
        subjects=[XIAOLE_SUB, JIALING_SUB, HALL_SUB],
        dialogue="手腕放松，挥杖要干脆。",
        speaker="S2",
        action=(
            "[Shot 1] Medium close-up two-shot inside the old Hogwarts hall. [Subject 1], the "
            "little boy wizard, stands facing [Subject 2], the senior girl wizard, who bends "
            "down slightly to his eye level. She gently adjusts his wand grip with her hand; "
            "he looks up at her with a serious earnest face, then tries again, wand pointed "
            "forward. Both faces clearly visible, warm candlelight, soft bokeh background. "
            "She teaches, he learns, eye contact throughout."
        ),
        sound="quiet hall ambience, faint candle flicker, soft fabric rustle",
        music="light playful piano, comedic but warm",
    ),
]

# ---------- 工作流编译（复用 xiaole_baishi.py 逻辑） ----------
def build_workflow(shot: dict, tpl: dict) -> dict:
    wf = copy.deepcopy(tpl)
    load_ids = sorted(
        nid for nid, n in wf.items() if n.get("class_type") == "LoadImage"
    )
    h3_id = next(
        nid for nid, n in wf.items() if n.get("class_type") == "MiniMaxH3ReferenceToVideo"
    )
    float_id = next(
        nid for nid, n in wf.items() if n.get("class_type") == "PrimitiveFloat"
    )
    save_id = next(
        nid for nid, n in wf.items() if n.get("class_type") == "SaveVideo"
    )
    max_id = max(int(n) for n in wf)

    refs = shot["refs"]
    if len(refs) <= len(load_ids):
        keep = load_ids[: len(refs)]
        for nid, fname in zip(keep, refs):
            wf[nid]["inputs"]["image"] = fname
        for nid in load_ids[len(refs):]:
            del wf[nid]
        load_map = {i: nid for i, nid in enumerate(keep)}
    else:
        for nid, fname in zip(load_ids, refs[: len(load_ids)]):
            wf[nid]["inputs"]["image"] = fname
        load_map = {i: nid for i, nid in enumerate(load_ids)}
        nxt = max_id + 1
        for i in range(len(load_ids), len(refs)):
            new_id = str(nxt)
            wf[new_id] = {
                "class_type": "LoadImage",
                "_meta": {"title": f"LoadImage {i+1}"},
                "inputs": {"image": refs[i]},
            }
            load_map[i] = new_id
            nxt += 1

    h3 = wf[h3_id]
    for k in list(h3["inputs"]):
        if k.startswith("ref_images"):
            del h3["inputs"][k]
    for i, nid in load_map.items():
        h3["inputs"][f"ref_images.ref_image_{i}"] = [nid, 0]

    h3["inputs"]["prompt"] = shot["prompt"]
    wf[float_id]["inputs"]["value"] = float(shot["seconds"])
    wf[save_id]["inputs"]["filename_prefix"] = f"video/xiaole_face_{shot['name']}"

    for nid, n in wf.items():
        if n.get("class_type") == "ResolutionSelector":
            n["inputs"]["megapixels"] = 1.0
    return wf


def main() -> None:
    tpl = json.loads(TEMPLATE.read_text(encoding="utf-8"))
    print("模板加载完成, LoadImage 节点:", len([n for n in tpl.values() if n.get('class_type')=='LoadImage']))

    shots_dir = WORK / "shots"
    shots_dir.mkdir(exist_ok=True)

    pids = []
    for shot in SHOTS:
        prompt = build_prompt(shot, shot["subjects"])
        shot["prompt"] = prompt
        issues = check_prompt(prompt, shot["refs"])
        status = "OK" if not issues else "FAIL: " + "; ".join(issues)
        print(f"{shot['name']}: {status}  ({shot['seconds']}s, refs={len(shot['refs'])}, 对白={shot.get('dialogue')})")
        if issues:
            sys.exit(1)

        wf = build_workflow(shot, tpl)
        out = shots_dir / f"{shot['name']}.json"
        out.write_text(json.dumps(wf, ensure_ascii=False), encoding="utf-8")
        print(f"  workflow -> {out}")

        body = json.dumps({"prompt": wf}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(
            f"{BASE}/prompt", data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                resp = json.load(r)
            pid = resp.get("prompt_id")
            print(f"  -> 提交成功 prompt_id: {pid}")
            pids.append({"name": shot["name"], "pid": pid, "seconds": shot["seconds"]})
        except Exception as e:
            print(f"  -> 提交失败: {e}")

    if pids:
        (WORK / "pids.json").write_text(
            json.dumps(pids, ensure_ascii=False, indent=1), encoding="utf-8"
        )
        print("\npid 已保存到 pids.json")


if __name__ == "__main__":
    main()
