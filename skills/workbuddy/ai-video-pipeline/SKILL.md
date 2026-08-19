# AI Video Pipeline Skill
# AI视频自动化生产流水线
---
summary: "从剧本到成片的AI视频自动化流水线：素材生成(图/音/参考) → ComfyUI工作流编译 → 远程台式机H3调度 → 结果回收。纯免费路线，支持多模态参考(Ref2VA)。"
trigger_words:
  - "生成视频"
  - "出片"
  - "排单"
  - "comfyui提交"
  - "h3生成"
  - "工作流提交"
  - "自动出片"
  - "ai视频流水线"
  - "调度台式机"
version: "1.0.0"
last_updated: "2026-08-08"
author: "WorkBuddy (auto-generated from实战)"
---

# AI Video Pipeline — 自动化生产流水线

## 适用场景

用户需要从**剧本/导演台设计**出发，自动完成：
1. 生成场景图、角色图等素材（ImageGen / 免费平台）
2. 编译 ComfyUI 工作流 JSON（H3 ImageToVideo / Ref2VA）
3. 提交到远程台式机 ComfyUI（TailScale, 100.67.139.74:8188）
4. 监控队列 + 回收 MP4 结果到本地 `shots/epXX/output/`

## 前置条件

| 条件 | 值 | 验证方式 |
|---|---|---|
| 台式机在线 | TailScale 100.67.139.74:8188 | `GET /system_stats` 返回 version |
| H3 节点已装 | MiniMaxH3ImageToVideo 等 | `GET /object_info` 含 MiniMax* |
| Python 环境 | managed venv (send2trash 已装) | `python -c "import send2trash"` |
| comfy_dispatcher.py | 工作区根目录 | `ls comfy_dispatcher.py` |

## 目录规范（每集统一）

```
shots/
  ep01/
    brief/
      director_note.md        # 导演台文档（剧情/分镜/对白/技术规格）
    assets/
      characters/             # 角色参考图（char_01.png, char_02.png...）
      scenes/                 # 场景图（scene_01.png, scene_02.png...）
      audio/                  # 音频素材（BGM/音效/TTS对白）
      reference/              # 风格/动作参考（mood_ref.png, action_ref.mp4...）
    workflows/
      h3_imagetovideo.json   # H3 图生视频工作流模板
      h3_ref2va.json         # H3 参考生视频工作流模板（角色锁定）
    output/                   # 生成的MP4结果（由dispatcher自动下载）
```

## 标准操作流程（SOP）

### Phase 1: 素材生成

#### 1A. 场景图 / 角色图（本机 ImageGen）

使用 WorkBuddy 内置 **ImageGen** 工具（Deferred Tool）：

```python
# 角色（竖版 1024x1536）
DeferExecuteTool("ImageGen", {
    "prompt": "<详细角色描述，含服装/道具/风格>",
    "size": "1024x1536",
    "quality": "high",
    "style": "concept art",
    "output_dir": "F:/WorkBuddy/AI_Video/shots/epXX/assets/characters"
})

# 场景（横版 1536x1024）
DeferExecuteTool("ImageGen", {
    "prompt": "<详细场景描述，含光影/氛围/构图>",
    "size": "1536x1024",
    "quality": "high",
    "style": "cinematic",
    "output_dir": "F:/WorkBuddy/AI_Video/shots/epXX/assets/scenes"
})
```

⚠️ **额度提醒**: 每张图约 5–10 credits。批量生成前必须告知用户。

#### 1B. 免费平台备选（零成本）

| 素材类型 | 免费平台 | 说明 |
|---|---|---|
| 场景图 | 海艺AI (4K免费不限次) | 练手首选 |
| 动漫风 | Vidu (免费) | 多主体一致性好 |
| 长视频参考 | 可灵AI (每日6次免费) | 最长2分钟 |
| 剪映集成 | 即梦AI | 和剪映深度打通 |
| 本地备选 | Flux (ComfyUI) | 台式机可跑 |

#### 1C. 音频素材

- **TTS 对白**: 剪映 TTS（免费）/ Fish Audio（有限免费）
- **BGM/音效**: 剪映素材库 / Epidemic Sound 免费区
- **本地克隆**: GPT-SoVITS（需另行部署）
- **H3 原生音频**: H3 可直接生成立体声+对白（11种语言），无需单独 TTS

### Phase 2: 导演台文档

为每集写 `brief/director_note.md`：

```markdown
# epXX 导演台文档 — 《标题》

## 基本信息
| 项目 | 内容 |
|---|---|
| 标题 | ... |
| 类型 | 微电影 / 短剧 / AI动漫 |
| 时长 | 目标 XX 秒 |
| 风格 | ... |
| 语言 | 中文 / 英文 / 日文（H3原生支持11种）|

## 故事梗概
（一段话概括）

## 场景分解
### Shot NN — <镜头名>
- **画面**: ...
- **动作**: ...
- **运镜**: ...
- **声音**: ...
- **时长**: N 秒
- **素材引用**: scene_NN.png, char_NN.png

## 对白脚本
> （逐句对白 + [音效] + [视觉]标注）

## 技术规格
| 项目 | 参数 |
|---|---|
| 模型 | MiniMax H3 (FL2VA / Ref2VA) |
| 分辨率 | 768p 短边 |
| 帧率 | 24 FPS |
| 音频 | 32kHz 立体声 |
```

### Phase 3: 工作流 JSON 编译

#### 3A. H3 ImageToVideo 模板（图生视频 / 首尾帧）

适用：单张场景图 → 视频（最简单路径）。

```json
{
  "1": {"class_type": "LoadImage", "inputs": {"image": "scene_01.png"}},
  "2": {"class_type": "CLIPLoader", "inputs": {
      "clip_name": "qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors", "type": "minimax"}},
  "3": {"class_type": "VAELoader", "inputs": {
      "vae_name": "minimax_h3_video_vae_fp16.safetensors"}},
  "4": {"class_type": "CLIPTextEncode", "inputs": {
      "text": "<运动/运镜提示词>", "clip": ["2", 0]}},
  "5": {"class_type": "MiniMaxH3ImageToVideo", "inputs": {
      "clip": ["2", 0], "vae": ["3", 0],
      "prompt": "<运动/运镜提示词>",
      "width": 1344, "height": 768, "length": 124,
      "first_frame": ["1", 0]}},
  "6": {"class_type": "VAEDecode", "inputs": {
      "samples": ["5", 1], "vae": ["3", 0]}},
  "7": {"class_type": "CreateVideo", "inputs": {
      "images": ["6", 0], "fps": 24}},
  "8": {"class_type": "SaveVideo", "inputs": {
      "video": ["7", 0],
      "filename_prefix": "epXX_shotNN", "format": "mp4", "codec": "auto"}}
}
```

**关键参数说明**:
- `length`: 124 = ~5秒 (24fps × 5s)，最大 362 (~15s)
- `width/height`: 默认 1344×768，必须被 32 整除
- `first_frame`: 首帧图像引用（LoadImage 的输出）
- `last_frame` (可选): 尾帧图像（用于首尾帧控制）
- H3 输出索引: `[node_id, 0]`=CONDITIONING, `[node_id, 1]`=LATENT

#### 3B. H3 ReferenceToVideo 模板（多模态参考 / 角色锁定）

适用：需要角色一致性 / 多参考素材的复杂场景。

```json
{
  "...加载器同上...",
  "R": {"class_type": "MiniMaxH3ReferenceToVideo", "inputs": {
      "clip": ["2", 0], "vae": ["3", 0],
      "audio_vae": ["AUDIO_VAE_NODE", 0],
      "prompt": "<运动提示词>",
      "width": 1344, "height": 768, "length": 124,
      "ref_image_size": "match",
      "ref_images": [
        {"ref_image": ["CHAR_LOAD_NODE", 0]},   // 角色参考（最多9张）
        {"ref_image": ["SCENE_LOAD_NODE", 0]}    // 场景参考
      ],
      "ref_audios": [
        {"ref_audio": ["AUDIO_LOAD_NODE", 0]}     // 音频参考（最多3个）
      ]
  }},
  "...解码+保存同上..."
}
```

**Ref2VA 关键参数**:
- `ref_images`: 0–9 张参考图（角色/风格/动作）
- `ref_videos`: 0–3 个参考视频（动作参考）
- `ref_audios`: 0–3 个参考音频（声音/节奏参考）
- `ref_video_audios`: 参考视频的原声音轨
- `ref_image_size`: `"match"` (快) 或 `"max"` (最佳保真度，慢)
- 需要 `audio_vae`: 用 `LTXVAudioVAELoader` 加载 `minimax_h3_audio_vae_fp32.safetensors`

### Phase 4: 提交与监控（comfy_dispatcher.py）

工具位置: `<workspace>/comfy_dispatcher.py`
运行环境: managed Python venv (`C:\Users\Lionel\.workbuddy\binaries\python\envs\default\python.exe`)

#### 4A. 一键运行（推荐）

```bash
cd F:/WorkBuddy/AI_Video
python comfy_dispatcher.py run \
  shots/epXX/workflows/h3_imagetovideo.json \
  --assets-dir shots/epXX/assets \
  --output-dir shots/epXX/output \
  --poll-interval 20
```

#### 4B. 分步操作

```bash
# 仅提交
python comfy_dispatcher.py submit workflows/flow.json --assets-dir assets

# 查看状态
python comfy_dispatcher.py status <prompt_id>
python comfy_dispatcher.py status queue          # 查看全部队列

# 下载结果
python comfy_dispatcher.py download <prompt_id> --output-dir output/
```

#### 4C. API 直接调用（高级 / 自定义脚本）

如果 dispatcher 不满足需求，可直接用 API:

```python
import json, urllib.request
BASE = "http://100.67.139.74:8188"

# 1. 上传图片
# POST /upload/image (multipart form-data)

# 2. 提交工作流
workflow = {...}  # 你的节点图
resp = urllib.request.urlopen(
    f"{BASE}/prompt",
    data=json.dumps({"prompt": workflow}).encode(),
)
prompt_id = json.loads(resp.read())["prompt_id"]

# 3. 轮询状态
# GET /queue → 看 queue_running / queue_pending
# GET /history → 看 prompt_id 是否出现且 status_str == "success"

# 4. 下载结果
# GET /view?filename=xxx&subfolder=yyy
```

### Phase 5: 结果验收与迭代

1. **查看输出**: `shots/epXX/output/` 中的 MP4 文件
2. **质量检查**: 角色一致性、运镜流畅度、口型同步、音频质量
3. **迭代调整**:
   - 画面问题 → 调整 prompt / 换参考图 / 调 length
   - 角色漂移 → 切换到 Ref2VA 模板 + 更多参考图
   - 音频问题 → 单独生成 TTS 后用 ref_audios 注入
4. **存档**: 通过的镜头标记为 `final/`, 失败的进 `retry/`

## 台式机模型清单（当前可用）

| 类型 | 文件名 | 用途 |
|---|---|---|
| 文本编码器(CLIP) | `qwen3vl_32b_minimax_h3_nvfp4_awq.safetensors` | Qwen3-VL-32B (H3专用) |
| 扩散模型(UNET) | `minimax_h3_fl2va_pruned_int8_convrot.safetensors` | FL2VA (图生视频) |
| 扩散模型(UNET) | `minimax_h3_ref2va_pruned_int8_convrot.safetensors` | Ref2VA (参考生视频) |
| 视频VAE | `minimax_h3_video_vae_fp16.safetensors` | 视频解码 |
| 音频VAE | `minimax_h3_audio_vae_fp32.safetensors` | 音频解码(Ref2VA用) |
| 通用VAE | `ae.safetensors` | 备用 |

## 常见错误排查

| 错误 | 原因 | 解决 |
|---|---|---|
| `no_prompt` | JSON 未包 `{"prompt": {...}}` | 外层加 prompt key |
| `received_type(IMAGE) mismatch input_type(VIDEO)` | 缺 CreateVideo 节点 | VAEDecode → CreateVideo → SaveVideo |
| `Required input is missing: fps` | CreateVideo 缺 fps 参数 | 加 `"fps": 24` |
| `connection refused` | 台式机离线 / TailScale 断开 | 检查 TailScale 连接 |
| `timeout` | H3 生成超时（16GB卡较慢） | 增大 poll-interval 或 timeout |
| 角色不一致 | FL2VA 无角色记忆 | 切换 Ref2VA + 提供 1–9 张角色参考图 |
| 中英混杂/乱旁白/语言不对 | prompt 未按官方六段式规范 | 用 `h3-ref2va-prompt` skill 生成 prompt |
| 输出文件名混到旧项目前缀下 | 从 history 模板深拷贝时 **SaveVideo filename_prefix 被继承**（如 `video/zhou_v2_shot02`） | 每镜显式改 `filename_prefix` 为当前项目名 `video/<proj>_<shotNN>`；勿直接用模板节点 |
| history 被清/重启后找不到输出 | ComfyUI 重启清空内存 history，prompt_id 全部失效 | 用 `GET /view?filename=...&subfolder=<SaveVideo子目录>&type=output` 探测 output/video 目录，下载后按**时长**与分镜秒数匹配识别（并校验参考图/内容） |

## 注意事项

1. **H3 本地限制**: 分辨率封顶 768p 短边；2K 需走云端 Regenerate-2K API
2. **Context-IR 不在本地**: 复杂多素材理解需接云端 API 或自建预处理
3. **社区许可排除 US/EU/UK/韩国**, 中国不在排除区
4. **商用门槛**: 年营收 > 2000 万美元需 MiniMax 书面授权（现阶段远不需要）
5. **笔记本不跑 H3**: 4GB 显存不够，仅做编排端
