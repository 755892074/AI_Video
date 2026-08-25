# -*- coding: utf-8 -*-
"""
嘉玲微表情测试 11 镜对比表生成
每镜提取 25% / 55% / 85% 三个时刻的帧, 拼成 11x3 网格对比图, 标注情绪名。
输出: shots/jialing_microexp_contact.png
"""
import json
import os
import subprocess
import sys
from pathlib import Path

import imageio_ffmpeg
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()

ORDER = [
    ("00_baseline", "00 基准脸(中性)"),
    ("01_surprise", "01 惊讶"),
    ("02_happy", "02 惊喜"),
    ("03_sad", "03 悲伤·强忍"),
    ("04_smile_tears", "04 含泪微笑"),
    ("05_anger", "05 愤怒·压抑"),
    ("06_fear", "06 恐惧"),
    ("07_disgust", "07 厌恶"),
    ("08_contempt", "08 轻蔑"),
    ("09_embarrass", "09 羞耻"),
    ("10_longing", "10 思念"),
]

STOP = [0.25, 0.55, 0.85]  # 提取时刻(比例)


def probe_duration(path):
    out = subprocess.run(
        [FFMPEG, "-i", str(path)], capture_output=True, text=True
    ).stderr
    for line in out.splitlines():
        if "Duration:" in line:
            t = line.split("Duration:")[1].split(",")[0].strip()
            h, m, s = t.split(":")
            return int(h) * 3600 + int(m) * 60 + float(s)
    return 6.0


def grab_frame(path, t, out_png):
    subprocess.run(
        [FFMPEG, "-y", "-ss", f"{t:.2f}", "-i", str(path),
         "-frames:v", "1", "-q:v", "2", str(out_png)],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )


def find_font(size):
    candidates = [
        r"C:/Windows/Fonts/msyh.ttc",   # 微软雅黑
        r"C:/Windows/Fonts/simhei.ttf",  # 黑体
        r"C:/Windows/Fonts/msyhbd.ttc",
        r"C:/Windows/Fonts/simsun.ttc",
    ]
    for c in candidates:
        if os.path.exists(c):
            return ImageFont.truetype(c, size)
    return ImageFont.load_default()


def main():
    tmp = ROOT / "shots" / "_microexp_contact_tmp"
    tmp.mkdir(exist_ok=True)

    rows = []  # 每镜一行: 3 帧拼好的横条
    for tag, label in ORDER:
        mp4 = ROOT / "shots" / f"jialing_microexp_{tag}" / "output" / "shot01.mp4"
        if not mp4.exists():
            print(f"[skip] {tag} 无视频")
            continue
        dur = probe_duration(mp4)
        frames = []
        for i, ratio in enumerate(STOP):
            t = min(dur * ratio, dur - 0.2)
            f = tmp / f"{tag}_{i}.png"
            grab_frame(mp4, t, f)
            frames.append(Image.open(f))
        # 统一尺寸并横排
        w = max(f.width for f in frames)
        h = max(f.height for f in frames)
        frames = [f.resize((w, h)) for f in frames]
        strip = Image.new("RGB", (w * 3, h), "black")
        for i, f in enumerate(frames):
            strip.paste(f, (i * w, 0))
        rows.append((tag, label, strip, w, h))
        print(f"[ok] {tag} dur={dur:.1f}s")

    if not rows:
        print("无任何镜头")
        return

    # 左侧标签列 + 网格
    font = find_font(20)
    label_w = 150
    cell_w = rows[0][3]
    cell_h = rows[0][4]
    cols = 3
    img_w = label_w + cell_w * cols + 20
    img_h = 20 + len(rows) * (cell_h + 6)
    canvas = Image.new("RGB", (img_w, img_h), (28, 28, 36))
    draw = ImageDraw.Draw(canvas)
    y = 10
    for tag, label, strip, w, h in rows:
        canvas.paste(strip, (label_w + 10, y))
        draw.text((12, y + h // 2 - 12), label, fill=(255, 220, 130), font=font)
        y += h + 6

    out = ROOT / "shots" / "jialing_microexp_contact.png"
    canvas.save(out)
    print(f"\n对比表 -> {out}  ({canvas.width}x{canvas.height})")
    # 清理临时帧
    for f in tmp.glob("*.png"):
        f.unlink()


if __name__ == "__main__":
    main()
