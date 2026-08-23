import os, re, subprocess, sys, time, glob

FFMPEG = r"C:/Users/Administrator/AppData/Roaming/TRAE SOLO CN/ModularData/ai-agent/vm/tools/app/ffmpeg/ffmpeg.exe"
FONT = r"C:/Windows/Fonts/simhei.ttf"
OUTDIR = r"D:/WorkBuddy/AI_Video/shots/xiaole_naruto/output"
FINAL = r"D:/WorkBuddy/AI_Video/shots/xiaole_naruto/output/xiaole_naruto_final.mp4"
SRT = r"D:/WorkBuddy/AI_Video/shots/xiaole_naruto/output/xiaole_naruto.srt"

DIALOGUE = [("shot01", "螺旋丸！"), ("shot02", "影分身之术！")]

def log(m): print("[assemble] " + m, flush=True)

def wait_for_shots():
    for i in range(120):  # 最多 40 分钟
        files = glob.glob(os.path.join(OUTDIR, "*.mp4"))
        found = {}
        for key, _ in DIALOGUE:
            hit = [f for f in files if key in os.path.basename(f)]
            if hit:
                found[key] = max(hit, key=os.path.getmtime)
        if len(found) == len(DIALOGUE):
            log("两镜均到位: " + ", ".join(os.path.basename(v) for v in found.values()))
            return [found["shot01"], found["shot02"]]
        time.sleep(20)
    log("超时: 仍有镜头未生成, 当前文件=" + str([os.path.basename(f) for f in files]))
    sys.exit(1)

def probe_dur(path):
    r = subprocess.run([FFMPEG, "-i", path], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    if not m: return 0.0
    h, mm, s = m.groups()
    return int(h)*3600 + int(mm)*60 + float(s)

def srt_ts(sec):
    ms = int(round(sec*1000))
    h = ms//3600000; ms %= 3600000
    m = ms//60000; ms %= 60000
    s = ms//1000; ms %= 1000
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def build_srt(durs):
    lines = []
    t = 0.0
    for idx, (key, text) in enumerate(DIALOGUE, 1):
        d = durs[idx-1]
        lines.append(str(idx))
        lines.append(f"{srt_ts(t)} --> {srt_ts(t+d)}")
        lines.append(text)
        lines.append("")
        t += d
    open(SRT, "w", encoding="utf-8").write("\n".join(lines))
    log("字幕已写入: " + SRT)

def main():
    if os.path.exists(FINAL) and os.path.getsize(FINAL) > 0:
        log("成片已存在, 跳过: " + FINAL)
        return
    shots = wait_for_shots()
    durs = [probe_dur(p) for p in shots]
    log("时长: " + ", ".join(f"{os.path.basename(s)}={d:.2f}s" for s, d in zip(shots, durs)))
    build_srt(durs)

    # 1) concat (stream copy) —— 中间文件放系统临时目录, 避免并发冲突
    import tempfile
    fd, concat_txt = tempfile.mkstemp(suffix=".txt", prefix="xiao_concat_")
    os.close(fd)
    with open(concat_txt, "w", encoding="utf-8") as f:
        for p in shots:
            f.write(f"file '{p.replace(chr(92), '/')}'\n")
    fd, inter = tempfile.mkstemp(suffix=".mp4", prefix="xiao_inter_")
    os.close(fd)
    subprocess.run([FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", concat_txt,
                    "-c", "copy", inter], check=True)
    log("拼接完成 -> " + inter)

    # 2) 烧录字幕
    srt_esc = SRT.replace("\\", "/").replace(":", "\\:")
    vf = (f"subtitles='{srt_esc}':force_style="
          f"'FontName=SimHei,FontSize=28,Outline=2,PrimaryColour=&H00FFFFFF,Alignment=2'")
    subprocess.run([FFMPEG, "-y", "-i", inter,
                    "-vf", vf,
                    "-c:v", "libx264", "-crf", "18", "-preset", "medium",
                    "-pix_fmt", "yuv420p", "-c:a", "copy", FINAL], check=True)
    log("✅ 成片完成: " + FINAL)
    if os.path.exists(concat_txt): os.remove(concat_txt)
    if os.path.exists(inter): os.remove(inter)

if __name__ == "__main__":
    main()
