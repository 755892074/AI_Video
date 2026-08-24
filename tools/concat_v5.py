#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""拼接 v5 成片: 5 镜按剧情顺序 [镜1 cast1, 镜2 fly, 镜3 v3复用,
镜4 cast2 shot1, 镜5 cast2 shot2] -> xiaole_crane_v5_full.mp4。
统一 864x480(源同源) / 24fps / yuv420p / aac。"""
import os, subprocess, imageio_ffmpeg, argparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FF = imageio_ffmpeg.get_ffmpeg_exe()

ORDER = [
    ("shots/xiaole_crane_v5_m1fix/output/shot01.mp4", "镜1 嘉玲开场(m1fix 脸稳定)"),
    ("shots/xiaole_crane_v5_fly/output/shot01.mp4", "镜2 纸鹤飞翔跟拍"),
    ("shots/xiaole_crane_v3/output/shot01.mp4", "镜3 小乐看纸鹤(复用)"),
    ("shots/xiaole_crane_v5_cast2/output/shot01.mp4", "镜4 施咒变公鸡"),
    ("shots/xiaole_crane_v5_cast2/output/shot02.mp4", "镜5 公鸡跳头晨鸣"),
]

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="shots/xiaole_crane_v5/output/xiaole_crane_v5_full.mp4")
    ap.add_argument("--skip-missing", action="store_true", help="跳过缺失的镜头")
    args = ap.parse_args()

    out_abs = os.path.join(ROOT, args.out)
    os.makedirs(os.path.dirname(out_abs), exist_ok=True)

    clips = []
    for rel, label in ORDER:
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p) or os.path.getsize(p) < 5000:
            print(f"[skip] {label}: {rel} 不存在或为空")
            if not args.skip_missing:
                print("缺少关键镜头, 中止。加 --skip-missing 可跳过缺失镜头。")
                return 1
            continue
        clips.append((p, label))
        print(f"[use]  {label}: {rel}")

    if len(clips) < 2:
        print("可用镜头不足 2 个, 无法拼接。")
        return 1

    tmp_dir = os.path.join(os.path.dirname(out_abs), "_norm_v5")
    os.makedirs(tmp_dir, exist_ok=True)
    normed = []
    for i, (c, label) in enumerate(clips):
        t = os.path.join(tmp_dir, f"n{i}.mp4")
        cmd = [FF, "-y", "-i", c,
               "-vf", "scale=864:480:force_original_aspect_ratio=decrease,pad=864:480:(ow-iw)/2:(oh-ih)/2",
               "-r", "24", "-pix_fmt", "yuv420p", "-c:v", "libx264",
               "-c:a", "aac", "-ar", "44100", "-b:a", "128k", t]
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        if r.returncode != 0:
            print(f"[FAIL] 归一化失败: {label}")
            return 1
        normed.append(t)
        print(f"[norm] {label} -> {os.path.getsize(t)}B")

    list_txt = os.path.join(tmp_dir, "list.txt")
    with open(list_txt, "w", encoding="utf-8") as f:
        for t in normed:
            f.write(f"file '{t}'\n")
    cmd = [FF, "-y", "-f", "concat", "-safe", "0", "-i", list_txt,
           "-c:v", "libx264", "-pix_fmt", "yuv420p", "-r", "24",
           "-c:a", "aac", "-ar", "44100", out_abs]
    r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if r.returncode == 0 and os.path.getsize(out_abs) > 5000:
        print(f"[FINAL] {out_abs} ({os.path.getsize(out_abs)}B)")
        return 0
    print("[concat FAIL]")
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
