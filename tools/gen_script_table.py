#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从剧本数据(script.json)生成人读表格：script.csv + script.html。

用法:
    python tools/gen_script_table.py scripts/xiaole_baishi/script.json

一个剧本 = 一份 script.json（数据），本工具把数据渲染成 CSV(Excel 可开)和
HTML(浏览器预览, 方便对视频比对完成度)。工具与数据分离：后续新剧本只需
写 script.json，本工具直接复用。

中文字段约定：script.json 每镜可带 "zh" 字典 {"action":..,"sound":..,"music":..}
供人读（中文意译）。提交用英文原文（action/sound/music 必须英文，六段式规范），
中文只进对白 <d>[Chinese]</d>。表格优先显示中文，英文原文折叠/并列保留。
"""
import argparse, csv, html, json, io, os
from pathlib import Path

SPEAKER_ZH = {"S1": "嘉玲", "S2": "小乐"}


def zh_of(s: dict, field: str):
    """优先返回中文字段，否则英文原文。"""
    z = s.get("zh") or {}
    return z.get(field) or s.get(field, "")


def gen_csv(data: dict) -> str:
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(["镜号", "时长(s)", "说话人", "对白",
                "动作(中)", "动作(英)", "音效(中)", "音效(英)",
                "音乐(中)", "音乐(英)", "素材"])
    for s in data["shots"]:
        w.writerow([
            s["name"], s["seconds"],
            SPEAKER_ZH.get(s.get("speaker", ""), s.get("speaker", "")),
            s.get("dialogue", ""),
            zh_of(s, "action"), s["action"],
            zh_of(s, "sound"), s.get("sound", ""),
            zh_of(s, "music"), s.get("music", ""),
            "/".join(s.get("refs", [])),
        ])
    return buf.getvalue()


def cell_zh_en(zh: str, en: str) -> str:
    """HTML 单元格：中文优先，英文原文折叠显示。"""
    zh_e = html.escape(zh)
    if not en or en == zh:
        return zh_e
    en_e = html.escape(en)
    return (f"{zh_e} <details><summary>原文</summary><pre>{en_e}</pre></details>")


def gen_html(data: dict) -> str:
    h = ["<!doctype html><html lang='zh'><head><meta charset='utf-8'>",
         "<style>body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#222;}"
         "h1{font-size:20px;margin-bottom:4px;} .meta{color:#666;font-size:13px;margin-bottom:12px;}"
         "table{border-collapse:collapse;width:100%;font-size:13px;}"
         "th,td{border:1px solid #ddd;padding:8px;text-align:left;vertical-align:top;}"
         "th{background:#2c3e50;color:#fff;} tr:nth-child(even){background:#fafafa;}"
         ".dia{font-weight:600;color:#1565c0;} .act{color:#555;font-size:12px;}"
         "details summary{cursor:pointer;color:#888;font-size:11px;} "
         "details pre{background:#f8f8f8;padding:6px;border-radius:4px;white-space:pre-wrap;font-size:11px;color:#666;}</style></head><body>"]
    h.append(f"<h1>{html.escape(data.get('title', ''))}</h1>")
    h.append(f"<div class='meta'>{len(data['shots'])} 镜 · 分辨率 {html.escape(str(data.get('resolution', '')))} · "
             f"fps {data.get('fps', '')} · 创建 {html.escape(str(data.get('created', '')))}</div>")
    h.append("<table><tr><th>#</th><th>镜号</th><th>时长</th><th>说话人</th><th>对白</th>"
             "<th>动作/画面</th><th>音效</th><th>音乐</th><th>素材</th></tr>")
    for i, s in enumerate(data["shots"], 1):
        sp = SPEAKER_ZH.get(s.get("speaker", ""), s.get("speaker", ""))
        h.append(f"<tr><td>{i}</td><td>{html.escape(s['name'])}</td><td>{s['seconds']}s</td>"
                 f"<td>{html.escape(sp)}</td>"
                 f"<td class='dia'>{html.escape(s.get('dialogue', ''))}</td>"
                 f"<td class='act'>{cell_zh_en(zh_of(s, 'action'), s['action'])}</td>"
                 f"<td>{cell_zh_en(zh_of(s, 'sound'), s.get('sound', ''))}</td>"
                 f"<td>{cell_zh_en(zh_of(s, 'music'), s.get('music', ''))}</td>"
                 f"<td>{html.escape('/'.join(s.get('refs', [])))}</td></tr>")
    h.append("</table></body></html>")
    return "".join(h)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("script", help="script.json 路径")
    args = ap.parse_args()
    data = json.loads(Path(args.script).read_text(encoding="utf-8"))
    out_dir = Path(args.script).parent
    (out_dir / "script.csv").write_text(gen_csv(data), encoding="utf-8-sig")
    (out_dir / "script.html").write_text(gen_html(data), encoding="utf-8")
    print(f"✅ {out_dir/'script.csv'}  {out_dir/'script.html'}")


if __name__ == "__main__":
    main()
