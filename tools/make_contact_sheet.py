# -*- coding: utf-8 -*-
"""
通用视频批次对比表生成
从 manifest 读取每镜 id/title, 对每个已完成镜头提取 25%/55%/85% 三帧拼成网格。
用法: python tools/make_contact_sheet.py --manifest shots/xxx_manifest.json --out shots/xxx_contact.png
"""
import argparse
import json
import os
import subprocess
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
STOP = [0.25, 0.55, 0.85]


def probe_duration(path):
    out = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 6.0


def grab_frame(path, t, out_png):
    subprocess.run(
        [FFMPEG, "-y", "-ss", f"{t:.2f}", "-i", str(path), "-frames:v", "1", "-q:v", "2", str(out_png)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def find_font(size):
    for c in [r"C:/Windows/Fonts/msyh.ttc", r"C:/Windows/Fonts/simhei.ttf",
              r"C:/Windows/Fonts/msyhbd.ttc", r"C:/Windows/Fonts/simsun.ttc"]:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--cols", type=int, default=3, help="每镜帧数(默认3)")
    args = ap.parse_args()

    manifest = json.load(open(ROOT / args.manifest, encoding="utf-8"))
    tmp = ROOT / "shots" / "_contact_tmp"
    tmp.mkdir(exist_ok=True)

    rows = []
    for s in manifest["sets"]:
        sid = s["id"]
        title = s.get("title", sid)
        mp4 = ROOT / "shots" / sid / "output" / "shot01.mp4"
        if not mp4.exists():
            print(f"[skip] {sid} 无视频")
            continue
        dur = probe_duration(mp4)
        frames = []
        for i in range(args.cols):
            ratio = STOP[i]
            t = min(dur * ratio, dur - 0.2)
            f = tmp / f"{sid.replace('/', '_')}_{i}.png"
            grab_frame(mp4, t, f)
            frames.append(Image.open(f))
        w = max(f.width for f in frames)
        h = max(f.height for f in frames)
        frames = [f.resize((w, h)) for f in frames]
        strip = Image.new("RGB", (w * args.cols, h), "black")
        for i, f in enumerate(frames):
            strip.paste(f, (i * w, 0))
        rows.append((title, strip, w, h))
        print(f"[ok] {sid} dur={dur:.1f}s")

    if not rows:
        print("无任何已完成镜头")
        return

    font = find_font(18)
    label_w = 170
    cell_w = rows[0][2]
    cell_h = rows[0][3]
    img_w = label_w + cell_w * args.cols + 20
    img_h = 20 + len(rows) * (cell_h + 6)
    canvas = Image.new("RGB", (img_w, img_h), (28, 28, 36))
    draw = ImageDraw.Draw(canvas)
    y = 10
    for title, strip, w, h in rows:
        canvas.paste(strip, (label_w + 10, y))
        draw.text((12, y + h // 2 - 12), title, fill=(255, 220, 130), font=font)
        y += h + 6

    out = ROOT / args.out
    canvas.save(out)
    print(f"\n对比表 -> {out}  ({canvas.width}x{canvas.height})")
    for f in tmp.glob("*.png"):
        f.unlink()


if __name__ == "__main__":
    main()
