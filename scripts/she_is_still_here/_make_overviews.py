# -*- coding: utf-8 -*-
"""EP01 12 镜分镜图总览：分 4 组 hstack inputs=3，避免 vstack 尺寸坑"""
import subprocess, os

FF = r"C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
SB = r"D:/WorkBuddy/AI_Video/scripts/she_is_still_here/storyboard"
OUT = r"D:/WorkBuddy/AI_Video/scripts/she_is_still_here/style_test"

GROUPS = [
    (1,  ["ep01_shot01.png", "ep01_shot02.png", "ep01_shot03.png"]),
    (2,  ["ep01_shot04.png", "ep01_shot05.png", "ep01_shot06.png"]),
    (3,  ["ep01_shot07.png", "ep01_shot08.png", "ep01_shot09.png"]),
    (4,  ["ep01_shot10.png", "ep01_shot11.png", "ep01_shot12.png"]),
]

for num, files in GROUPS:
    out = os.path.join(OUT, f"sb_overview_{num}.png")
    inputs = []
    for f in files:
        inputs += ["-i", os.path.join(SB, f)]
    cmd = [FF, "-y"] + inputs + ["-filter_complex", "[0][1][2]hstack=inputs=3,scale=1248:-2", "-q:v", "2", out]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if os.path.exists(out):
        print(f"OK group {num}: {out} ({os.path.getsize(out)//1024} KB)")
    else:
        print(f"FAIL group {num}: {r.stderr[-300:]}")