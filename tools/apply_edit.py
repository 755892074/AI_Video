#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把手稿 script_edit.csv / script_edit.xlsx 的改动同步回 script.json，并重新生成正式表。

用法:
    python tools/apply_edit.py scripts/xiaole_baishi/script.json

规则：
  - 自动逐行比对手稿与 script.json 的内容差异，检测出改动镜，无需手动填标记。
  - 对白/说话人/时长/素材/动作(中)/音效(中)/音乐(中) 直接按 CSV 写入。
  - 动作(英)/音效(英)/音乐(英)：CSV 里给了新英文就用；留空则保留 json 原英文。
  - 同步后自动重跑 gen_script_table 生成正式 csv/html，并给出重出命令。

兼容 .csv(UTF-8/BOM) 和 .xlsx(Excel 另存) 两种格式，自动识别。

改完手稿后运行本工具，再把改动镜提交：
    python tools/h3_submit.py --script scripts/xiaole_baishi/script.json \
        --project xiaole_baishi --only shot01,shot03
"""
import argparse, csv, json, io, re, subprocess, sys, zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

SPEAKER_MAP = {"嘉玲": "S1", "小乐": "S2", "S1": "S1", "S2": "S2"}
M = '{http://schemas.openxmlformats.org/spreadsheetml/2006/main}'
# 列索引：0改 1镜号 2时长 3说话人 4对白 5动作中 6动作英 7音效中 8音效英 9音乐中 10音乐英 11素材
COL_CN = {'seconds': 2, 'speaker': 3, 'dialogue': 4, 'act_zh': 5, 'act_en': 6,
          'snd_zh': 7, 'snd_en': 8, 'mus_zh': 9, 'mus_en': 10, 'refs': 11}


def read_sheet(path: Path) -> list[list[str]]:
    """读取 csv 或 xlsx，返回 [表头, 行1, 行2...]"""
    data = path.read_bytes()
    if data[:2] == b'PK':  # xlsx (zip)
        z = zipfile.ZipFile(path)
        strings = []
        root = ET.fromstring(z.read('xl/sharedStrings.xml'))
        for si in root.findall(f'{M}si'):
            strings.append(''.join(t.text or '' for t in si.iter(M + 't')))
        root = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
        rows = []
        for row in root.iter(f'{M}row'):
            cells = {}
            for c in row:
                ref = c.get('r')
                col = re.match(r'([A-Z]+)', ref).group(1)
                t = c.get('t')
                v = c.find(M + 'v')
                val = strings[int(v.text)] if t == 's' and v is not None else (v.text or '' if v is not None else '')
                cells[col] = val
            rows.append([cells.get(c, '') for c in 'ABCDEFGHIJKL'])
        return rows
    # csv
    return list(csv.reader(io.StringIO(data.decode('utf-8-sig'))))


def g(r, i):
    return r[i].strip() if i < len(r) else ""


def row_to_shot(r) -> dict:
    return {
        'seconds': g(r, 2), 'speaker': g(r, 3), 'dialogue': g(r, 4),
        'act_zh': g(r, 5), 'act_en': g(r, 6),
        'snd_zh': g(r, 7), 'snd_en': g(r, 8),
        'mus_zh': g(r, 9), 'mus_en': g(r, 10),
        'refs': [x.strip() for x in g(r, 11).split('/') if x.strip()],
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="script.json 路径")
    ap.add_argument("--edit", default=None, help="手稿路径（默认 <script 同目录>/script_edit.csv 或 .xlsx）")
    args = ap.parse_args()

    script_path = Path(args.script)
    data = json.loads(script_path.read_text(encoding="utf-8"))
    edit_path = Path(args.edit) if args.edit else None
    if edit_path is None:
        for cand in (script_path.parent / "script_edit.csv", script_path.parent / "script_edit.xlsx"):
            if cand.exists():
                edit_path = cand
                break
    if edit_path is None:
        sys.exit("未找到手稿 script_edit.csv / .xlsx")

    rows = read_sheet(edit_path)
    body = [r for r in (rows[1:] if rows else []) if any(x.strip() for x in r)]
    print(f"读取手稿: {edit_path}（{len(body)} 镜）")

    shots = {s["name"]: s for s in data["shots"]}
    changed = []
    for r in body:
        name = g(r, 1)
        shot = shots.get(name)
        if not shot:
            print(f"⚠️  未找到镜头 {name}，跳过")
            continue
        new = row_to_shot(r)
        # 与 json 当前值比对，判断是否有实际改动
        is_changed = False
        if new['seconds'] and str(shot.get('seconds')) != new['seconds']:
            is_changed = True
        if new['speaker'] and shot.get('speaker') != SPEAKER_MAP.get(new['speaker'], new['speaker']):
            is_changed = True
        if new['dialogue'] and shot.get('dialogue', '') != new['dialogue']:
            is_changed = True
        z = shot.get('zh') or {}
        if new['act_zh'] and z.get('action', '') != new['act_zh']:
            is_changed = True
        if new['snd_zh'] and z.get('sound', '') != new['snd_zh']:
            is_changed = True
        if new['mus_zh'] and z.get('music', '') != new['mus_zh']:
            is_changed = True
        if new['act_en'] and shot.get('action', '') != new['act_en']:
            is_changed = True
        if new['snd_en'] and shot.get('sound', '') != new['snd_en']:
            is_changed = True
        if new['mus_en'] and shot.get('music', '') != new['mus_en']:
            is_changed = True
        if new['refs'] and shot.get('refs') != new['refs']:
            is_changed = True

        if not is_changed:
            continue

        before = f"对白:{shot.get('dialogue','')[:25]} | 中:{z.get('action','')[:25]}"
        # 写入
        if new['seconds']:
            try:
                shot['seconds'] = float(new['seconds'])
            except ValueError:
                print(f"⚠️  {name} 时长非法: {new['seconds']}，保持原值")
        sp = SPEAKER_MAP.get(new['speaker'], new['speaker'])
        if sp:
            shot['speaker'] = sp
        if new['dialogue']:
            shot['dialogue'] = new['dialogue']
        shot.setdefault('zh', {})
        if new['act_zh']:
            shot['zh']['action'] = new['act_zh']
        if new['snd_zh']:
            shot['zh']['sound'] = new['snd_zh']
        if new['mus_zh']:
            shot['zh']['music'] = new['mus_zh']
        if new['act_en']:
            shot['action'] = new['act_en']
        if new['snd_en']:
            shot['sound'] = new['snd_en']
        if new['mus_en']:
            shot['music'] = new['mus_en']
        if new['refs']:
            shot['refs'] = new['refs']

        after = f"对白:{shot.get('dialogue','')[:25]} | 中:{shot.get('zh',{}).get('action','')[:25]}"
        changed.append(name)
        print(f"✅ {name} 检测到改动，已同步")
        print(f"   before: {before}")
        print(f"   after : {after}")

    if not changed:
        print("\n未检测到任何改动（手稿与 script.json 一致）。")
        sys.exit(0)

    script_path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n✅ 已写回 {script_path}")
    subprocess.run([sys.executable, str(Path(__file__).parent / "gen_script_table.py"), str(script_path)])
    print(f"\n改动镜: {', '.join(changed)}")
    print(f"重出命令: python tools/h3_submit.py --script {args.script} --project <项目> --only {','.join(changed)}")


if __name__ == "__main__":
    main()
