# -*- coding: utf-8 -*-
"""EP01 全集 12 镜参考图准备：全部分镜图 crop 9:16 + 拷贝方旭定妆图"""
import subprocess, os, shutil

FF = r"C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"D:/WorkBuddy/AI_Video"
REFS = os.path.join(ROOT, "shots", "she_is_still_here", "refs")
SB = os.path.join(ROOT, "scripts", "she_is_still_here", "storyboard")
os.makedirs(REFS, exist_ok=True)

# 1) 12 张分镜图 832x1216 -> center-crop 684x1216 (9:16) -> scale 1080x1920
for n in range(1, 13):
    src = os.path.join(SB, f"ep01_shot{n:02d}.png")
    dst = os.path.join(REFS, f"ep01_shot{n:02d}_9x16.png")
    if not os.path.exists(src):
        print("MISS", os.path.basename(src)); continue
    tmp = dst + ".tmp.png"
    r = subprocess.run([FF, "-y", "-i", src, "-filter:v", "crop=684:1216:74:0,scale=1080:1920", tmp],
                       capture_output=True, text=True)
    if os.path.exists(tmp):
        os.replace(tmp, dst)
        print("CROP", os.path.basename(dst), os.path.getsize(dst)//1024, "KB")
    else:
        print("FAIL", os.path.basename(src), r.stderr[-200:])

# 2) 拷贝角色定妆图（jiangche/linmian 已在 refs，补 fangxu）
copies = [
    (os.path.join(ROOT, "characters", "she_is_still_here", "fangxu", "bean_fangxu.png"),
     os.path.join(REFS, "fangxu.png")),
]
for src, dst in copies:
    if not os.path.exists(src):
        print("MISS", src); continue
    shutil.copy2(src, dst)
    print("COPY", os.path.basename(dst), os.path.getsize(dst)//1024, "KB")

print("REFS:", sorted(os.listdir(REFS)))
