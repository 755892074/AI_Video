# -*- coding: utf-8 -*-
"""v10 测试镜参考图准备：分镜图 crop 成 9:16 + 拷贝定妆图到 refs"""
import subprocess, os, shutil

FF = r"C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
ROOT = r"D:/WorkBuddy/AI_Video"
REFS = os.path.join(ROOT, "shots", "she_is_still_here", "refs")
os.makedirs(REFS, exist_ok=True)

# 1) 分镜图 crop 832x1216 -> 684x1216 (9:16) -> scale 1080x1920
crops = [
    (os.path.join(ROOT, "scripts", "she_is_still_here", "storyboard", "ep01_shot05.png"),
     os.path.join(REFS, "ep01_shot05_9x16.png")),
    (os.path.join(ROOT, "scripts", "she_is_still_here", "storyboard", "ep01_shot07.png"),
     os.path.join(REFS, "ep01_shot07_9x16.png")),
]
for src, dst in crops:
    tmp = dst + ".tmp.png"
    # center-crop width 684 from 832
    r = subprocess.run([FF, "-y", "-i", src, "-filter:v", "crop=684:1216:74:0,scale=1080:1920", tmp],
                       capture_output=True, text=True)
    if os.path.exists(tmp):
        os.replace(tmp, dst)
        print("CROPPED", os.path.basename(dst), os.path.getsize(dst)//1024, "KB")
    else:
        print("FAIL crop", os.path.basename(src), r.stderr[-300:])

# 2) 拷贝定妆/场景图
copies = [
    (os.path.join(ROOT, "characters", "she_is_still_here", "jiangche", "bean_jiangche.png"),
     os.path.join(REFS, "jiangche.png")),
    (os.path.join(ROOT, "characters", "she_is_still_here", "linmian_comatose", "bean_linmian_comatose.png"),
     os.path.join(REFS, "linmian_comatose.png")),
    (os.path.join(ROOT, "shots", "she_is_still_here", "scenes", "bean_ward_cg.png"),
     os.path.join(REFS, "ward_cg.png")),
]
for src, dst in copies:
    shutil.copy2(src, dst)
    print("COPIED", os.path.basename(dst), os.path.getsize(dst)//1024, "KB")

print("REFS:", sorted(os.listdir(REFS)))
