# -*- coding: utf-8 -*-
"""给 10 秒广州塔飞行视频烧录中文字幕（黑体白边，避开盘符冒号坑）。"""
import os, shutil, subprocess, imageio.v2 as imageio

FF = (r"C:/Users/Lionel/.workbuddy/binaries/python/envs/default"
      r"/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe")
FONT = r"C:/Windows/Fonts/simhei.ttf"

WORK = os.path.dirname(os.path.abspath(__file__))
SRC = "MiniMax_H3_00096_.mp4"
DST = "canton_fly_含字幕.mp4"

# 1) 实测时长
r = imageio.get_reader(os.path.join(WORK, SRC))
fps = r.get_meta_data().get("fps", 24.0)
n = r.count_frames()
dur = n / float(fps)
r.close()
print("时长 %.2fs" % dur)

# 2) 对白字幕（女孩先说，男孩接）
# 女孩：好漂亮的夜景  | 男孩：哪有你漂亮
def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

split = dur * 0.52  # 男孩那句稍长，作收尾
lines = [
    ("女孩：好漂亮的夜景。", 0.0, split),
    ("男孩：哪有你漂亮。", split, dur),
]
srt = []
for i, (txt, a, b) in enumerate(lines, 1):
    srt.append(str(i))
    srt.append(f"{fmt(a)} --> {fmt(b)}")
    srt.append(txt)
    srt.append("")
srt_path = os.path.join(WORK, "canton_fly_zimu.srt")
with open(srt_path, "w", encoding="utf-8-sig") as f:
    f.write("\n".join(srt))
print("SRT:", srt_path)

# 3) 字体拷到工作目录，相对路径规避 Windows 盘符冒号
shutil.copy2(FONT, os.path.join(WORK, "simhei.ttf"))

# 4) 烧字幕（cwd=WORK，相对名，fontsdir=.）
style = ("FontName=SimHei,FontSize=34,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&H00000000,Outline=4,Shadow=1,Bold=1,"
         "Alignment=2,MarginV=70")
sub_filter = f"subtitles=canton_fly_zimu.srt:fontsdir=.:force_style='{style}'"
cmd = [
    FF, "-y", "-i", SRC,
    "-vf", sub_filter,
    "-c:v", "libx264", "-preset", "medium", "-crf", "18",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k",
    DST,
]
print("运行 ffmpeg（cwd=%s）..." % WORK)
res = subprocess.run(cmd, capture_output=True, text=True, cwd=WORK)
print("returncode:", res.returncode)
if res.returncode != 0:
    print("STDERR:", res.stderr[-3000:])
    raise SystemExit("烧字幕失败")
out = os.path.join(WORK, DST)
print("成品:", out, os.path.getsize(out), "bytes")
