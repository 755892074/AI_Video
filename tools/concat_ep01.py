# -*- coding: utf-8 -*-
"""拼接 ep01 五镜 -> 一段连续短片，并烧录中文字幕（黑体）。"""
import os, shutil, subprocess, imageio.v2 as imageio

FF = r"C:/Users/Lionel/.workbuddy/binaries/python/envs/default/Lib/site-packages/imageio_ffmpeg/binaries/ffmpeg-win-x86_64-v7.1.exe"
FONT = r"C:/Windows/Fonts/simhei.ttf"

SRC_DIR = r"f:/WorkBuddy/AI_Video/shots/hp/output/ep01_series"
WORK = r"c:/Users/Lionel/WorkBuddy/Claw/ai_video_results/ep01"
os.makedirs(WORK, exist_ok=True)

SHOTS = ["shot01.mp4", "shot02.mp4", "shot03.mp4", "shot04.mp4", "shot05.mp4"]

# 台词（与分镜一一对应）；shot04 拆分为外婆画外 + 儿子回应两段
DIALOGUE = {
    "shot01": [("外婆家的院子……今天怎么亮晶晶的？", 1.0)],
    "shot02": [("我的手……怎么会发光？", 1.0)],
    "shot03": [("出来吧，我的小光灵！", 1.0)],
    "shot04": [("（外婆画外）宝——吃饭咯！", 0.55),
               ("等一下嘛，我在施魔法！", 0.45)],
    "shot05": [("原来，我真的是小巫师呀。", 1.0)],
}

# 1) 拷贝 + 取实测时长
durations = {}
for sh in SHOTS:
    src = os.path.join(SRC_DIR, sh)
    dst = os.path.join(WORK, sh)
    shutil.copy2(src, dst)
    r = imageio.get_reader(dst)
    meta = r.get_meta_data()
    fps = meta.get("fps", 24.0)
    n = r.count_frames()
    durations[sh] = n / float(fps)
    r.close()
    print(f"{sh}: {durations[sh]:.2f}s")

# 2) 生成 SRT（累计时间戳）
def fmt(t):
    h = int(t // 3600); m = int((t % 3600) // 60); s = int(t % 60)
    ms = int(round((t - int(t)) * 1000))
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

srt_lines = []
idx = 1
cursor = 0.0
for sh in SHOTS:
    segs = DIALOGUE[os.path.splitext(sh)[0]]
    d = durations[sh]
    for text, frac in segs:
        dur = d * frac
        start = cursor
        end = cursor + dur
        srt_lines.append(str(idx))
        srt_lines.append(f"{fmt(start)} --> {fmt(end)}")
        srt_lines.append(text)
        srt_lines.append("")
        idx += 1
        cursor = end
    cursor = end  # 衔接：下一镜从本镜结束开始

srt_path = os.path.join(WORK, "ep01_zimu.srt")
with open(srt_path, "w", encoding="utf-8-sig") as f:
    f.write("\n".join(srt_lines))
print("SRT 已写:", srt_path)

# 3) concat 列表（使用相对路径，避免盘符冒号被 ffmpeg 误解析）
list_path = os.path.join(WORK, "list.txt")
with open(list_path, "w", encoding="utf-8") as f:
    for sh in SHOTS:
        f.write(f"file '{sh}'\n")

# 4) 复制字体到工作目录，用相对 fontsdir 规避 Windows 盘符冒号
shutil.copy2(FONT, os.path.join(WORK, "simhei.ttf"))

# 5) 合成 + 烧字幕（cwd=WORK，srt 用相对名，fontsdir=.）
final = os.path.join(WORK, "ep01_连续短片_含字幕.mp4")
style = ("FontName=SimHei,FontSize=30,PrimaryColour=&H00FFFFFF,"
         "OutlineColour=&H00000000,Outline=3,Shadow=1,Bold=1,"
         "Alignment=2,MarginV=60")
sub_filter = (f"subtitles=ep01_zimu.srt:fontsdir=.:force_style='{style}'")

cmd = [
    FF, "-y", "-f", "concat", "-safe", "0", "-i", "list.txt",
    "-vf", sub_filter,
    "-c:v", "libx264", "-preset", "medium", "-crf", "20",
    "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k",
    "ep01_连续短片_含字幕.mp4",
]
print("运行 ffmpeg 合成（cwd=%s）..." % WORK)
r = subprocess.run(cmd, capture_output=True, text=True, cwd=WORK)
print("returncode:", r.returncode)
if r.returncode != 0:
    print("STDERR:", r.stderr[-2500:])
    raise SystemExit("合成失败")
print("成品:", final, os.path.getsize(final), "bytes")
