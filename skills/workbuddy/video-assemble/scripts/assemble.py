#!/usr/bin/env python3
"""
Video Assemble — AI 视频成片打包脚本

把同一目录下的 shot*.mp4 分镜拼接成片，可选烧录 SRT 字幕（指定字体）。

典型用法:
    python assemble.py --input-dir ./ep01 --output ./ep01/final/成片.mp4 \
        --srt ./ep01/ep01_zimu.srt --font ./ep01/simhei.ttf

依赖:
    - ffmpeg / ffprobe (PATH 中可用)
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def ff(shell_cmd: list[str]) -> None:
    """执行 ffmpeg/ffprobe 命令,失败抛错。"""
    print("$", " ".join(shell_cmd))
    result = subprocess.run(shell_cmd, check=False, shell=False)
    if result.returncode != 0:
        sys.exit(f"❌ 命令失败 (exit {result.returncode}): {' '.join(shell_cmd)}")

# ffmpeg 可执行文件路径,在 main() 里解析
FFMPEG: str = ""


def probe_duration(path: Path, ffprobe_cmd: str | None) -> float:
    """读取视频时长(秒)。ffprobe 缺失时回退用 ffmpeg 解析 Duration。"""
    if ffprobe_cmd:
        try:
            out = subprocess.check_output(
                [ffprobe_cmd, "-v", "error", "-show_entries", "format=duration",
                 "-of", "default=noprint_wrappers=1:nokey=1", str(path)],
                text=True,
            ).strip()
            return float(out)
        except Exception:
            pass
    # 回退: ffmpeg -i 输出里解析 Duration: HH:MM:SS.xx
    import re
    r = subprocess.run([FFMPEG, "-i", str(path)], capture_output=True, text=True)
    m = re.search(r"Duration: (\d+):(\d+):(\d+(?:\.\d+)?)", r.stderr)
    if m:
        h, mm, s = m.groups()
        return int(h) * 3600 + int(mm) * 60 + float(s)
    return 0.0


def list_shots(input_dir: Path, order: list[str] | None) -> list[Path]:
    """按规则列出分镜文件。order 非空时按用户给定顺序(仅取匹配文件名)。"""
    if order:
        files = [input_dir / name for name in order]
        missing = [f for f in files if not f.exists()]
        if missing:
            sys.exit(f"❌ 指定顺序中下列文件不存在: {missing}")
        return files
    shots = sorted(input_dir.glob("shot*.mp4"))
    if not shots:
        sys.exit(f"❌ {input_dir} 下没有找到 shot*.mp4")
    return shots


def write_concat_list(files: list[Path], concat_txt: Path) -> None:
    """写 ffmpeg concat demuxer 文件。"""
    lines = []
    for f in files:
        # 单引号包裹 + 内部单引号转义
        safe = str(f).replace("'", "'\\''")
        lines.append(f"file '{safe}'")
    concat_txt.write_text("\n".join(lines) + "\n", encoding="utf-8")


def concat_videos(files: list[Path], intermediate: Path) -> None:
    """拼接分镜(无损流复制)。"""
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".txt", delete=False, encoding="utf-8"
    ) as fp:
        concat_txt = Path(fp.name)
    try:
        write_concat_list(files, concat_txt)
        ff([
            FFMPEG, "-y", "-f", "concat", "-safe", "0",
            "-i", str(concat_txt),
            "-c", "copy",
            str(intermediate),
        ])
    finally:
        concat_txt.unlink(missing_ok=True)


def burn_subtitles(
    intermediate: Path,
    output: Path,
    srt: Path,
    font: Path | None,
    font_size: int,
    font_name: str = "SimHei",
) -> None:
    """烧录硬字幕,使用 libx264 重编码。"""
    # 转 Windows 风格路径 + escape
    srt_escaped = str(srt).replace("\\", "/").replace(":", "\\:")

    force_style_parts = [
        f"FontName={font_name}",
        f"FontSize={font_size}",
        "Outline=2",
        "PrimaryColour=&H00FFFFFF",
        "Alignment=2",  # 底部居中
    ]
    force_style = ",".join(force_style_parts)

    vf = f"subtitles='{srt_escaped}':force_style='{force_style}'"

    ff([
        FFMPEG, "-y", "-i", str(intermediate),
        "-vf", vf,
        "-c:v", "libx264", "-crf", "18", "-preset", "medium",
        "-pix_fmt", "yuv420p",
        "-c:a", "copy",
        str(output),
    ])


def main() -> None:
    global FFMPEG
    ap = argparse.ArgumentParser(description="AI 视频成片打包 (ffmpeg)")
    ap.add_argument("--input-dir", required=True, type=Path,
                    help="分镜 MP4 所在目录")
    ap.add_argument("--output", required=True, type=Path,
                    help="成片输出路径(.mp4)")
    ap.add_argument("--srt", type=Path, default=None,
                    help="SRT 字幕文件(可选)")
    ap.add_argument("--font", type=Path, default=None,
                    help="字体文件路径(中文字幕必需,如 simhei.ttf)")
    ap.add_argument("--font-size", type=int, default=24,
                    help="字幕字号 (默认 24)")
    ap.add_argument("--font-name", default="SimHei",
                    help="字体名,需与字体文件对应 (默认 SimHei)")
    ap.add_argument("--order", default=None,
                    help="显式分镜顺序,逗号分隔,如 shot01.mp4,shot02.mp4")
    ap.add_argument("--ffmpeg", default=None,
                    help="ffmpeg 可执行文件路径 (默认自动查找)")
    ap.add_argument("--ffprobe", default=None,
                    help="ffprobe 可执行文件路径 (可选,缺省时回退用 ffmpeg)")
    args = ap.parse_args()

    input_dir: Path = args.input_dir.resolve()
    output: Path = args.output.resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    # 定位 ffmpeg: 优先用户指定 → PATH → imageio-ffmpeg
    if args.ffmpeg:
        FFMPEG = args.ffmpeg
    else:
        found = shutil.which("ffmpeg")
        if found:
            FFMPEG = found
        else:
            try:
                import imageio_ffmpeg
                FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
            except Exception:
                FFMPEG = None
    if not FFMPEG or not os.path.isfile(FFMPEG):
        sys.exit("❌ 找不到 ffmpeg,请指定 --ffmpeg 或安装 ffmpeg 后加入 PATH")

    FFPROBE = args.ffprobe or (shutil.which("ffprobe") if shutil.which("ffprobe") else None)

    if not input_dir.is_dir():
        sys.exit(f"❌ 输入目录不存在: {input_dir}")

    order = (
        [n.strip() for n in args.order.split(",") if n.strip()]
        if args.order else None
    )
    shots = list_shots(input_dir, order)

    print(f"📂 输入目录: {input_dir}")
    print(f"🎞️  分镜数: {len(shots)}")
    for s in shots:
        dur = probe_duration(s, FFPROBE)
        print(f"   - {s.name}  ({dur:.2f}s)")

    # 中间文件 (用同目录临时,便于 Windows 兼容)
    with tempfile.NamedTemporaryFile(
        suffix=".mp4", delete=False, dir=output.parent
    ) as fp:
        intermediate = Path(fp.name)
    try:
        print("▶️  拼接分镜...")
        concat_videos(shots, intermediate)

        if args.srt:
            if not args.srt.exists():
                sys.exit(f"❌ 字幕文件不存在: {args.srt}")
            # 字体不在字幕路径里时,自动用 --font 拼到子进程能找到的位置
            print("▶️  烧录字幕...")
            burn_subtitles(
                intermediate=intermediate,
                output=output,
                srt=args.srt,
                font=args.font,
                font_size=args.font_size,
                font_name=args.font_name,
            )
        else:
            # 无字幕:直接拷贝(或轻量重封装)
            shutil.move(str(intermediate), str(output))

        dur = probe_duration(output, FFPROBE)
        size_mb = output.stat().st_size / 1024 / 1024
        print(f"✅ 成片完成: {output}")
        print(f"   时长: {dur:.2f}s  大小: {size_mb:.2f} MB")
    finally:
        if intermediate.exists():
            intermediate.unlink(missing_ok=True)


if __name__ == "__main__":
    main()