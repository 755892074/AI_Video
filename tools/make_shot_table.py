#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""从 manifest + state + 日志 生成「每场景一张镜头档案表」（Markdown + HTML）。

一个场景(= manifest 里一个 set)生成一张表，每行包含该镜：
  镜头Key | 角色A素材 | 角色B素材 | 场景素材 | 提示词(摘要+全文折叠) |
  视频长度 | 生成耗时 | 分辨率 | 输出文件
表头区块列出本场景共用的「工作流参数」（H3 节点参数）。

用途：后期查阅 / 总体预览 / 定位并重出某一镜。
"""
import json, os, re, sys, subprocess, datetime, html, glob
import imageio_ffmpeg

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

# ---------- 工作流参数提取（H3 节点 + 关联节点） ----------
def extract_workflow_params(wf):
    p = {}
    nodes = wf.get("prompt", wf) if isinstance(wf, dict) and "prompt" in wf else wf
    for nid, n in nodes.items():
        ct = n.get("class_type", "")
        inp = n.get("inputs", {})
        if ct == "ResolutionSelector":
            p["aspect_ratio"] = inp.get("aspect_ratio")
            p["megapixels"] = inp.get("megapixels")
        elif ct == "CreateVideo":
            p["fps"] = inp.get("fps")
        elif ct == "BasicScheduler":
            p["steps"] = inp.get("steps")
            p["scheduler"] = inp.get("scheduler")
            p["denoise"] = inp.get("denoise")
        elif ct == "KSamplerSelect":
            p["sampler"] = inp.get("sampler_name")
        elif ct == "RandomNoise":
            p["seed"] = inp.get("noise_seed")
        elif ct == "UNETLoader":
            p["unet"] = inp.get("unet_name")
        elif ct == "CLIPLoader":
            p["clip"] = inp.get("clip_name")
        elif ct == "MiniMaxH3ReferenceToVideo":
            p["ref_image_size"] = inp.get("ref_image_size")
    return p

# ---------- 日志耗时解析 ----------
def parse_log(log_path):
    res = {}
    if not os.path.exists(log_path):
        return res
    for line in open(log_path, encoding="utf-8", errors="ignore"):
        m = re.match(r"\[(\d{2}:\d{2}:\d{2})\]\s+\[(submit|done)\]\s+(\S+)", line)
        if not m:
            continue
        ts, kind, key = m.group(1), m.group(2), m.group(3)
        t = datetime.datetime.strptime(ts, "%H:%M:%S")
        res.setdefault(key, {})[kind + "_ts"] = t
    for k, v in res.items():
        if "submit_ts" in v and "done_ts" in v:
            v["elapsed"] = (v["done_ts"] - v["submit_ts"]).total_seconds()
    return res

# ---------- 探测 mp4 实际分辨率/时长 ----------
def probe_video(path):
    try:
        out = subprocess.run([FFMPEG, "-i", path], capture_output=True,
                             text=True, errors="ignore").stderr
        dur = None
        m = re.search(r"Duration:\s*(\d+):(\d+):(\d+\.\d+)", out)
        if m:
            hh, mm, ss = map(float, m.groups())
            dur = hh * 3600 + mm * 60 + ss
        res = None
        m2 = re.search(r"Stream.*Video.*?(\d{2,4})x(\d{2,4})", out)
        if m2:
            res = f"{m2.group(1)}x{m2.group(2)}"
        return dur, res
    except Exception:
        return None, None

def fmt_dur(sec):
    return "—" if sec is None else f"{sec:.1f}s"

def fmt_elapsed(sec):
    if sec is None:
        return "—"
    if sec < 60:
        return f"{sec:.0f}s"
    return f"{int(sec // 60)}m{int(sec % 60):02d}s"

def prompt_summary(shot):
    if shot.get("ref2va"):
        dd = shot["ref2va"].get("detailed_description", "")
        if isinstance(dd, list):
            dd = " ".join(dd)
        return dd.strip()[:60]
    return shot.get("prompt", "").strip()[:60]

def prompt_full(shot):
    if shot.get("ref2va"):
        sys.path.insert(0, os.path.join(ROOT, "tools"))
        import batch_r2v
        return batch_r2v.assemble_ref2va_prompt(shot["ref2va"])
    return shot.get("prompt", "")

def workflow_param_line(wp):
    parts = []
    if wp.get("aspect_ratio"):
        parts.append(f"比例 {wp['aspect_ratio']}")
    if wp.get("megapixels"):
        parts.append(f"{wp['megapixels']}MP")
    if wp.get("fps"):
        parts.append(f"{wp['fps']}fps")
    if wp.get("steps"):
        parts.append(f"步数 {wp['steps']}")
    if wp.get("sampler"):
        parts.append(f"sampler {wp['sampler']}")
    if wp.get("scheduler"):
        parts.append(f"scheduler {wp['scheduler']}")
    if "denoise" in wp:
        parts.append(f"denoise {wp['denoise']}")
    if wp.get("seed"):
        parts.append(f"seed {wp['seed']}")
    if wp.get("ref_image_size"):
        parts.append(f"ref_size {wp['ref_image_size']}")
    if wp.get("unet"):
        parts.append(f"模型 {os.path.basename(str(wp['unet']))}")
    if wp.get("clip"):
        parts.append(f"CLIP {os.path.basename(str(wp['clip']))}")
    return " · ".join(parts)

def render_set(s, sid, rows, wp, prefix):
    name = s.get("name") or s.get("desc") or sid
    # Markdown
    md = [f"# 镜头档案 · {name}（{sid}）\n",
          f"**工作流参数**：{workflow_param_line(wp)}\n",
          "| # | 镜头Key | 角色A(素材) | 角色B(素材) | 场景(素材) | 提示词(摘要) | 视频长度 | 生成耗时 | 分辨率 | 输出文件 |",
          "|---|---|---|---|---|---|---|---|---|---|"]
    for r in rows:
        sb = os.path.basename(r["sb"]); ch = os.path.basename(r["ch"]); sc = os.path.basename(r["sc"])
        outname = os.path.basename(r["out"]) if r["exists"] else "（生成中）"
        size = f"{r['size']//1024}KB" if r["exists"] else "—"
        res = r["res"] or "—"
        md_out = f"[{outname}](file:///{r['out'].replace(chr(92),'/')}) ({size})" if r["exists"] else f"{outname} ({size})"
        md.append(f"| {r['shot']} | {r['key']} | {sb} | {ch} | {sc} | {r['sum']}… | {fmt_dur(r['dur'])} | {fmt_elapsed(r['elapsed'])} | {res} | {md_out} |")
    md.append("")
    md.append(f"> **修改重出**：编辑 `shots/{prefix}_manifest.json` 中该镜头字段后运行\n"
              f"> `python tools/batch_r2v.py --manifest shots/{prefix}_manifest.json --state shots/{prefix}_state.json --log shots/{prefix}_r2v.log`\n"
              f"> 已存在的 `shotXX.mp4` 会被跳过；删掉对应文件即可强制重出该镜。")
    md_path = os.path.join(ROOT, "shots", sid, "shot_table.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(md))

    # HTML（可预览）
    h = ["<!doctype html><html lang='zh'><head><meta charset='utf-8'>",
         "<style>body{font-family:-apple-system,Segoe UI,Roboto,sans-serif;margin:24px;color:#222;}",
         "h1{font-size:20px;} .wp{background:#f5f5f5;padding:10px 14px;border-radius:8px;margin:10px 0;font-size:13px;color:#444;}",
         "table{border-collapse:collapse;width:100%;font-size:13px;margin-top:8px;}",
         "th,td{border:1px solid #ddd;padding:6px 8px;text-align:left;vertical-align:top;}",
         "th{background:#2c3e50;color:#fff;} tr:nth-child(even){background:#fafafa;}",
         ".ok{color:#1a7f37;} .pending{color:#b35900;font-weight:bold;}",
         ".btn{display:inline-block;padding:4px 10px;background:#1565c0;color:#fff;border-radius:6px;text-decoration:none;font-size:12px;}",
         ".btn:hover{background:#0d47a1;}",
         ".vid{color:#1565c0;text-decoration:none;font-weight:bold;} .vid:hover{text-decoration:underline;}",
         ".out{font-size:12px;}",
         "details summary{cursor:pointer;color:#1565c0;font-size:12px;}",
         "pre{background:#f8f8f8;padding:8px;border-radius:6px;white-space:pre-wrap;font-size:12px;}",
         "</style></head><body>"]
    out_dir_abs = os.path.join(ROOT, "shots", sid, "output")
    folder_url = "file:///" + out_dir_abs.replace("\\", "/")
    h.append(f"<h1>镜头档案 · {html.escape(name)}（{html.escape(sid)}）</h1>")
    h.append(f"<div class='wp'><b>工作流参数：</b>{html.escape(workflow_param_line(wp))} "
             f"&nbsp; <a class='btn' href='{folder_url}'>📂 打开输出文件夹</a></div>")
    h.append("<table><tr><th>#</th><th>镜头Key</th><th>角色A</th><th>角色B</th><th>场景</th>"
             "<th>提示词(摘要)</th><th>长度</th><th>耗时</th><th>分辨率</th><th>输出</th></tr>")
    for r in rows:
        sb = html.escape(os.path.basename(r["sb"])); ch = html.escape(os.path.basename(r["ch"])); sc = html.escape(os.path.basename(r["sc"]))
        cls = "ok" if r["exists"] else "pending"
        outname = os.path.basename(r["out"]) if r["exists"] else "生成中"
        size = f"{r['size']//1024}KB" if r["exists"] else "—"
        res = r["res"] or "—"
        full = html.escape(r["full"])
        if r["exists"]:
            video_url = "file:///" + r["out"].replace("\\", "/")
            out_cell = f"<a class='vid' href='{video_url}' target='_blank'>{html.escape(outname)}</a> ({size})"
        else:
            out_cell = f"{html.escape(outname)} ({size})"
        h.append(f"<tr class='{cls}'><td>{r['shot']}</td><td>{html.escape(r['key'])}</td>")
        h.append(f"<td title='{sb}'>{sb}</td><td title='{ch}'>{ch}</td><td title='{sc}'>{sc}</td>")
        h.append(f"<td>{html.escape(r['sum'])}… <details><summary>全文</summary><pre>{full}</pre></details></td>")
        h.append(f"<td>{fmt_dur(r['dur'])}</td><td>{fmt_elapsed(r['elapsed'])}</td><td>{res}</td>")
        h.append(f"<td class='out'>{out_cell}</td></tr>")
    h.append("</table></body></html>")
    html_path = os.path.join(ROOT, "shots", sid, "shot_table.html")
    with open(html_path, "w", encoding="utf-8") as f:
        f.write("".join(h))
    print(f"[table] {sid} -> {md_path} | {html_path}")

def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--state", default=None)
    ap.add_argument("--log", default=None)
    ap.add_argument("--workflow", default=None)
    args = ap.parse_args()
    man = load_json(args.manifest)
    mdir = os.path.dirname(os.path.abspath(args.manifest))
    prefix = os.path.basename(args.manifest)
    if prefix.endswith("_manifest.json"):
        prefix = prefix[:-len("_manifest.json")]
    state_path = args.state or os.path.join(mdir, prefix + "_state.json")
    log_path = args.log or os.path.join(mdir, prefix + "_r2v.log")
    wf_path = args.workflow or os.path.join(ROOT, man.get("workflow", ""))
    if not os.path.isabs(wf_path):
        wf_path = os.path.join(ROOT, wf_path)
    wf = load_json(wf_path)
    if "prompt" in wf:
        wf = wf["prompt"]
    wp = extract_workflow_params(wf)
    # 合并读取目录下所有 *.log，避免续跑新建的 log 覆盖原始趟的 submit/done 记录
    loginfo = {}
    for lf in sorted(glob.glob(os.path.join(mdir, "*.log"))):
        for k, v in parse_log(lf).items():
            loginfo.setdefault(k, {}).update(v)
    state = load_json(state_path) if os.path.exists(state_path) else {}

    for s in man["sets"]:
        sid = s["id"]
        out_dir = os.path.join(ROOT, "shots", sid, "output")
        rows = []
        for sh in s["shots"]:
            key = f"{sid}_{sh['shot']:02d}"
            rel_sb = sh.get("storyboard", ""); rel_ch = sh.get("character", ""); rel_sc = sh.get("scene", "")
            out_path = os.path.join(out_dir, f"shot{sh['shot']:02d}.mp4")
            exists = os.path.exists(out_path) and os.path.getsize(out_path) > 5000
            dur, res = probe_video(out_path) if exists else (None, None)
            st = state.get(key, {})
            el = loginfo.get(key, {}).get("elapsed")
            mt = os.path.getmtime(out_path) if exists else None
            rows.append({
                "key": key, "shot": sh["shot"],
                "sb": rel_sb, "ch": rel_ch, "sc": rel_sc,
                "sum": prompt_summary(sh), "full": prompt_full(sh),
                "dur": dur, "res": res, "elapsed": el,
                "exists": exists, "out": out_path, "mtime": mt,
                "size": os.path.getsize(out_path) if exists else 0,
                "done": st.get("done", exists),
            })
        # 单镜实际生成耗时：
        #  - 有效完成时间 efdone = 日志 done_ts，缺失则用文件 mtime 兜底
        #  - 优先取全局时间线上「上一完成 → 本完成」的相邻差（准确反映单镜渲染，避免同批提交累计偏差）
        #  - 相邻差缺失/超界时，回退到「submit → done」墙钟差
        #  - 相邻差或墙钟差超出 [60s, 900s] 视为续跑/断档，记 None（不显示假耗时）
        timeline = []
        for r in rows:
            li = loginfo.get(r["key"], {})
            dt = li.get("done_ts")
            if dt is None and r["mtime"] is not None:
                dt = datetime.datetime.fromtimestamp(r["mtime"])
            if dt is not None:
                timeline.append((dt, r))
        timeline.sort(key=lambda x: x[0])
        prev_of = {}
        for i, (dt, r) in enumerate(timeline):
            prev_of[r["key"]] = timeline[i-1][0] if i > 0 else None
        TH = 900
        for r in rows:
            li = loginfo.get(r["key"], {})
            done_ts = li.get("done_ts"); submit_ts = li.get("submit_ts")
            efdone = done_ts if done_ts is not None else (
                datetime.datetime.fromtimestamp(r["mtime"]) if r["mtime"] is not None else None)
            prev = prev_of.get(r["key"])
            diff_adj = (efdone - prev).total_seconds() if (efdone is not None and prev is not None) else None
            if diff_adj is not None and 60 <= diff_adj <= TH:
                r["elapsed"] = diff_adj
            elif done_ts is not None and submit_ts is not None:
                d1 = (done_ts - submit_ts).total_seconds()
                r["elapsed"] = d1 if 60 <= d1 <= TH else None
            else:
                r["elapsed"] = None
        render_set(s, sid, rows, wp, prefix)

if __name__ == "__main__":
    main()
