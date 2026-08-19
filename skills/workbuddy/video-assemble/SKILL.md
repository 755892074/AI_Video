---
summary: "AI 视频成片打包工具：把同一集的所有分镜 MP4 拼接成片，可选烧录 SRT 字幕（指定字体），输出最终 MP4。基于 ffmpeg，零依赖（外部工具齐全即可）。"
trigger_words:
  - "拼片"
  - "拼视频"
  - "拼成片"
  - "字幕烧录"
  - "硬字幕"
  - "成片打包"
  - "concat"
  - "ffmpeg拼接"
  - "合片"
  - "video assemble"
version: "1.0.0"
last_updated: "2026-08-13"
author: "WorkBuddy (auto-generated from ep01 实战)"
---

# Video Assemble — AI 视频成片打包工具

## 适用场景

AI 视频流水线的**最后一公里**：把同一集 (`epXX`) 的若干分镜 MP4 拼成一条完整成片，并按需烧录 SRT 字幕。

典型来源：`ai-video-pipeline` 生成的分镜 → 本 skill 拼成片。

## 适用版本 / 前置

| 项目 | 值 |
|---|---|
| 系统 | Windows / macOS / Linux |
| 依赖 | `ffmpeg`（`ffmpeg -version` 可用） |
| 依赖 | `ffprobe`（ffmpeg 自带） |
| 输入 | 同一目录下若干 `shot*.mp4` + 可选 `*.srt` |
| 字体 | 中文字幕需要 `simhei.ttf` 或同类黑体（与 MP4 同目录） |

---

## 标准操作流程（SOP）

### 调用方式

```bash
python scripts/assemble.py \
  --input-dir <分镜目录> \
  --output <成片路径.mp4> \
  --srt <字幕.srt，可选> \
  --font <字体.ttf，可选> \
  --font-size <字号，可选> \
  [--shuffle | --order shot01,shot02,...]
```

### 工作流

1. **扫描输入目录** — 按 `shot*.mp4` 字典序排序；如指定 `--order` 则按显式顺序
2. **生成 concat list** — 临时 `concat.txt`（ffmpeg concat demuxer 格式）
3. **拼接分镜** — `ffmpeg -f concat -safe 0 -i concat.txt -c copy intermediate.mp4`
4. **烧录字幕（可选）** — 若提供 `--srt`：用 `subtitles=` filter + `force_style` 指定字体
5. **产出最终 MP4** — `--output` 路径，H.264 + AAC，yuv420p 兼容

### 默认参数

| 参数 | 默认 |
|---|---|
| `--font-size` | 24 |
| `--font-color` | white |
| `--font-outline` | 2 |
| `--font-name` | SimHei |
| 视频编码 | H.264 (`libx264`, crf 18, preset medium) |
| 音频编码 | AAC 192k |
| 像素格式 | yuv420p |

---

## 关键设计

### 字幕烧录的 ffmpeg 命令

```bash
ffmpeg -i intermediate.mp4 \
  -vf "subtitles='${SRT}':force_style='FontName=${FONT},FontSize=${SIZE},Outline=${OL},PrimaryColour=&H00FFFFFF'" \
  -c:v libx264 -crf 18 -preset medium -pix_fmt yuv420p \
  -c:a copy \
  final.mp4
```

**Windows 路径注意**：路径含空格或中文时需要转义；脚本内用 `subprocess.run(list, shell=False)` 传数组，避免引号问题。

### 为什么不用 `c copy` 直接拼

`c copy` 拼接虽快，但：
- 各分镜编码参数可能不一致（fps、gop、profile）
- 字幕烧录必须重新编码

所以：拼接阶段用 `c copy`（无损、快），烧字幕阶段再编码一次。

---

## 输出目录建议

```
epXX/
  shot01.mp4, shot02.mp4, ...        # 输入分镜
  epXX_zimu.srt                      # 字幕（可选）
  simhei.ttf                         # 字体（可选）
  final/
    epXX_连续短片.mp4                # 仅拼接
    epXX_连续短片_含字幕.mp4         # 含字幕（默认产出）
```

---

## 常见错误

| 错误 | 原因 | 解决 |
|---|---|---|
| `concat: not found` | 输入文件名含特殊字符未转义 | 用 demuxer（`concat.txt`）+ 单引号包裹文件名 |
| 字幕中文方框 | 缺中文字体或字体名错 | 确认 `simhei.ttf` 同目录；`force_style` 指定 `FontName=SimHei` |
| 音画不同步 | 分镜 fps 不一致 | 统一为 24fps，或脚本内重编码阶段 `-r 24` |
| 字幕显示位置错 | 默认底部居中 | `force_style` 加 `Alignment=2`（底部）/ `Alignment=6`（顶部） |
| ffmpeg not found | 未装 ffmpeg 或不在 PATH | 提示用户安装或提供 ffmpeg 路径 |

---

## 配套技能

- **`ai-video-pipeline`** — 上游（生成素材 + 调度 ComfyUI 出分镜）
- **`video-frames`** — 可选（从分镜抽帧做验收拼图）

---

## 示例

```bash
# 最简：只拼片
python scripts/assemble.py \
  --input-dir ./shots/ep01 \
  --output ./shots/ep01/final/ep01_连续短片.mp4

# 含字幕 + 字体
python scripts/assemble.py \
  --input-dir ./shots/ep01 \
  --output ./shots/ep01/final/ep01_连续短片_含字幕.mp4 \
  --srt ./shots/ep01/ep01_zimu.srt \
  --font ./shots/ep01/simhei.ttf \
  --font-size 28
```