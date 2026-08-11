# ComfyUI 工作流模板库

本目录保存所有 H3 相关 ComfyUI 工作流模板，**可直接拖进台式机 ComfyUI WebUI**（`http://100.67.139.74:8188`）直观查看流程和参数。

## 模板列表

| 文件 | 用途 | 说明 |
|------|------|------|
| `h3_r2v_refvideo_v1.json` | **⭐ 主力：R2V + 视频动作参考** | 角色A/B + 场景 + 参考视频帧序列（`ref_videos` 24fps 动作迁移）+ 参考视频音轨。功夫场景 shot01 用这个 |
| `h3_r2v_canton10s_v1.json` | R2V + 粤语 10 秒 | 基于 hp 场景的工作流，10 秒长度、粤语配音链路 |
| `h3_i2v_test_v1.json` | I2V 图生视频测试 | 单图 + 提示词生成视频，最简链路 |
| `h3_r2v_original_ui.json` | R2V 官方原始模板 | 从 ComfyUI 导出的原始 UI 工作流（无视频参考，纯 ref_images） |

## 怎么用

1. 台式机打开 ComfyUI WebUI（`http://100.67.139.74:8188`）
2. 把对应 `.json` 文件**直接拖进页面**（或用菜单 Load 载入）
3. 页面会显示完整的节点流程图（节点 + 连线 + 参数）
4. 填好参考图路径后可直接 Run 测试

## 生成方式

这些 UI 格式文件由 `tools/api2ui.py` 从 API 格式（`shots/*/workflows/*.json`）自动转换生成：
- API 格式 = 程序提交用（`batch_r2v.py` 读取）
- UI 格式 = 人肉查看用（拖进 ComfyUI）

```bash
python tools/api2ui.py <api格式.json> <输出ui格式.json>
```

改过 API 模板后，重新跑一次转换即可同步更新 UI 版。

## 当前主力链路（h3_r2v_refvideo_v1）

```
LoadImage(角色A) ─┐
LoadImage(角色B) ─┼→ MiniMaxH3ReferenceToVideo ─→ SamplerCustomAdvanced ─→ SaveVideo
LoadImage(场景) ──┤        ↑
LoadVideo ─→ GetVideoComponents ─ ref_videos.ref_video_0 (帧序列动作参考)
                          └──── ref_video_audios.ref_video_audio_0 (音轨)
```
