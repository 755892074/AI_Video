#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 script.json 生成可编辑手稿 script_edit.csv（用户可直接改）。

用法:
    python tools/gen_edit_sheet.py scripts/xiaole_baishi/script.json

输出: <剧本目录>/script_edit.csv，Excel/WPS 可直接打开编辑。
每镜一行，首列【改】为版本标记：留空=未改动，填任意值(如 v2)=该镜要重出。

改完 CSV 后运行:
    python tools/apply_edit.py scripts/xiaole_baishi/script.json
即可把 CSV 改动同步回 script.json，并重新生成正式表。
"""
import argparse, csv, json, io
from pathlib import Path

HEADER = ["【改】", "镜号", "时长(s)", "说话人", "对白",
          "动作(中)", "动作(英)", "音效(中)", "音效(英)",
          "音乐(中)", "音乐(英)", "素材"]
SPEAKER_ZH = {"S1": "嘉玲", "S2": "小乐"}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="script.json 路径")
    args = ap.parse_args()
    data = json.loads(Path(args.script).read_text(encoding="utf-8"))

    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(HEADER)
    for s in data["shots"]:
        z = s.get("zh") or {}
        w.writerow([
            "", s["name"], s["seconds"],
            SPEAKER_ZH.get(s.get("speaker", ""), s.get("speaker", "")),
            s.get("dialogue", ""),
            z.get("action", ""), s.get("action", ""),
            z.get("sound", ""), s.get("sound", ""),
            z.get("music", ""), s.get("music", ""),
            "/".join(s.get("refs", [])),
        ])
    out = Path(args.script).parent / "script_edit.csv"
    out.write_text(buf.getvalue(), encoding="utf-8-sig")
    print(f"✅ 手稿已生成（Excel 可直接编辑）: {out}")
    print("改法：改动过的行，在【改】列填任意标记(如 v2)，其余留空")
    print("改完运行: python tools/apply_edit.py %s" % args.script)


if __name__ == "__main__":
    main()
