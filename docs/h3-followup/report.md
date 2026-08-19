# MiniMax H3 跟进报告

## 2026-08-15（首轮）

### 🚀 加速方案（最值得关注）

**1. W4A8 量化模型（12.5GB）+ 加速组合实测**
来源：aistudynow.com（RTX 5090 实测）
链接：https://aistudynow.com/minimax-h3-w4a8-in-comfyui-12-5-gb-model-tested
要点：
- FL2VA W4A8 仅 12.5GB，与 INT8 肉眼无明显质量差异 → **16GB 台式机友好**，值得替换试试
- 各加速项实测（15s 片段）：
  - 裸跑 ~12min
  - +Sol Attention → ~9min（但画面有运动偏差）
  - +SageAttention+EasyCache → ~5min（最快但质量/音频下降，**EasyCache 是质量元凶**）
  - +SageAttention（不开 EasyCache）→ ~9min 且质量更好
- 压缩版 Video VAE（3.17GB，Kijai 实验版）→ 无质量差异，可省显存
- Ref2VA + W4A8 + rank-256 参考 LoRA → 质量/动作/声音都 OK，很值得试
- 结论：**不要叠满所有优化**；速度快了质量会崩，宁可慢一点保住 motion/脸/音频

**2. fp16 fix（无 BF16 GPU 的救命方案）**
来源：Amduraznak / ai-primer 报道
链接：https://www.ai-primer.com/creative/stories/local-h3-comfyui-video-tuning
要点：
- H3 官方只声明 bf16/fp32 推理；无 BF16 的 GPU 会回退 fp32（慢）
- Amduraznak 的 fp16 补丁修复溢出点（原 fp16 会黑屏），V100 上约 **11x 提速**
- 老显卡（如 2060 笔记本）装上 + Spectrum 后 480p 5s 约 12min 可跑

**3. Spectrum 加速**
- 通过 Chebyshev 岭回归预测部分未来 solver 步骤的 transformer 特征，跳选求值
- 注意：部分用户反馈 ComfyUI 更新后 Spectrum 偶发失效（回归正常渲染时间）

**4. Turbo LoRA（低步数采样）**
- `MiniMax-H3-Turbo-Lora V4 step600`（larryvrh）→ 8 步高质量快速
- 关键坑：**4-6 步比 8 步动态更好、更贴 prompt**；8 步可能落入 motion 崩塌的局部最优点
- Ref2VA 场景下 Turbo 可能翻车（有用户 4 步 I2V 好、Ref2V 乱；3060 上关掉 Turbo 保质量）

**5. 注意力后端**
- ComfyUI 官方 8/11 更新：合并 comfy-kitchen attention，新增 `ModelAttentionBackend` 节点 + `--use-ck-attention` 标志
- ⚠️ **一次只能激活一个**：测试 CK 前必须禁用 Sage / Minimax MemEff Sage / Sol Attention
- Sol Attention 仅支持 SM89/90/100/120/121（3090 SM86 不支持）

### 🎛 工作流

**1. H3 I2V Dual Clock 8-Step（RunComfy 分享）**
链接：https://www.runcomfy.com/comfyui-workflows/minimax-h3-i2v-comfyui-8-step-dual-clock-audio-video
- 8 步 Dual Clock sampler：视频/音频双时钟同步采样，音画锁定
- 集成 SageAttention + Turbo LoRA，单参考图 + "Audio:" 段 prompt
- 适合：人物表演、车辆、产品展示等需音画同步的场景

### 📢 官方动态

- H3 8/3 正式开源（GitHub: MiniMax-AI/MiniMax-H3），H3-Base 33B 权重开源；Context-IR 和 Regenerate-2K 暂未开源（走官方 API）
- ComfyUI 0.30.0 起原生支持 H3，官方 I2V/T2V/R2V 模板
- Ref2VA 输入上限：9 图 + 3 视频 + 3 音频（共 12 文件）

### 💡 对现有流水线的可借鉴

1. **优先试 W4A8 + 压缩 VAE**：省显存/提速，16GB 台式机当前最划算的一步
2. **可试 Turbo LoRA 8 步**：若 motion 崩，回退到常规步数（注意 4-6 vs 8 步差异）
3. **SageAttention 可开**（官方支持），**EasyCache 慎用**（质量/音频下降）
4. 已有 ComfyUI 版本注意：升级到 0.30+ 且只用一个 attention backend

## 2026-08-16（第二轮）

### 📢 官方动态

**1. 官方 AMA：2K 重绘模型 + 稀疏注意力即将发布**
来源：官方（Reddit r/StableDiffusion AMA，8/7）
链接：https://www.toutiao.com/article/7672144247918707252 ｜ https://agihunt.info/e/19fe455a16c54015be7c589247d
要点：
- H3-Regenerate-2K 独立重绘模型即将开源（隐空间二次生成，非传统超分），本地可交付 2K
- 稀疏注意力采用 **MoBA-style 块选择**（非 M3 的 MSA），无需训练索引器；首版目标零感知质量损失，近期出保守版参考实现
- 官方在研究 4/8-NFE 低步数 Turbo 版（回应社区第三方 Turbo LoRA）
- 官方承认：远距人脸糊（最高优先级修复）、Ref2VA 画质偏软、拼接接缝
- 许可证考虑过渡 Apache-2.0；2K 推理成本 0.8 元/秒（不到同类旗舰 1/3）

**2. 官方发布 h3-prompt-writing 提示词技能（prompt 指南的重要补充）**
来源：官方 GitHub
链接：https://github.com/MiniMax-AI/MiniMax-H3（skills/h3-prompt-writing/，npx skills add https://github.com/MiniMax-AI/MiniMax-H3 --skill h3-prompt-writing）
要点：
- 官方开源提示词写作技能，含 base-en.txt / ref-en.txt 两本手册 + 8 个风格化生成技能（3D 动画短片/品牌宣传片/双人合作游戏开场/手绘直播/极简产品广告/音乐视频字幕/纸拼贴/纸定格）
- 基础模式三段式：integrated_multimodal_description → overall_soundscape → non_diegetic_music；Ref2VA 六段式：subject_definitions → summary → retention_analysis → detailed_description → overall_soundscape → non_diegetic_music
- 本地 ComfyUI 用此格式可逼近官方 Context-IR 的出片质量

### ⚙ ComfyUI 生态

**3. w4a8 + int8 convrot VAE 已合入 ComfyUI 核心（PR #15308 / #15334）**
来源：HF（Kijai）/ GitHub
链接：https://huggingface.co/Kijai/MiniMax-H3-experimental ｜ 实测 https://www.toutiao.com/article/7672669387167040035
要点：
- Kijai 校准无关非对称 4-bit：权重 0.56 字节/元素，运行时解量化为 int8 走 CUTLASS GEMM；权重相对误差 0.073（NVFP4 为 0.094），比纯 int8 快 1.09x
- int8 convrot VAE：4.9GB → 3.2GB，解码快 1.5x；**装最新版 ComfyUI 直接可用**，16GB 台式机最优先更新项
- 注意仍是 "testing only"：跑预览/抽卡用它，正式出片回退 pruned 版

**4. Sol Engine / SolAttn CrossStep Cache 实测（Sol-Engine H3-OnDevice）**
来源：Reddit（SECourses v104）
链接：https://www.reddit.com/r/comfyui/comments/1vh5wd8/
要点：
- NVIDIA 官方宣称最高 4.52x 加速；SECourses 实测（保守质量阈值 0.08）比 Sage Attention 2.8.3 快约 1.39x
- 1344×768 362 帧 15s 仅用 20GB VRAM；提供 4 个 4x 预设（T2V/I2V/R2V/Text-With-Refs）
- 注意 Sol 仅支持 SM89/90/100/120/121（4060Ti 属 SM89 可用；3090 SM86 不行）

**5. EasyCache 提速 60%（定位：2K 场景专用）**
来源：腾讯云开发者社区
链接：https://cloud.tencent.com/developer/article/2726092
要点：
- EasyCache + Sage Attention 把 8 分钟压到 4 分钟；作者建议普通分辨率别用加速，2K 再开（可接受小质量损失）
- 与首轮"EasyCache 是质量元凶"结论一致：加速项要按场景挑，不是全叠

### 🎬 视频博主 / 工作流

**6. B站 @好奇漫步：H3 三合一工作流（T2V/I2V-FLF2V/R2V）**
来源：视频博主（B站 + RunningHub 云端双版本）
链接：https://www.runninghub.cn/post/2087029485995642882/
要点：
- 模式 1/2/3 一键切换，二次采样增强防脸崩；分辨率只改 MP 自动对齐
- 四条规则：低分辨率抽卡锁 Seed 再二采；R2V 无用素材 Ctrl+B 禁用；参考编号按实际生效顺序重排；ref_image_size 默认 match、高一致性再试 max

**7. B站 @Astral星芒：MiniMax-H3 全能生视频 V2（8/15 发布）**
来源：视频博主（B站/CivitAI）
链接：https://civitaiarchives.com/models/2860939
要点：
- comfy kitchen + 正式版 LoRA 加速；官方 skill 自动/手动优化提示词
- 三合一 + 二次采样放大防脸崩；数字人音频可锁定不变（对口型/解说场景有用）

**8. "本地草稿，云端定稿"工作流 + 52 个官方提示词库**
来源：atlascloud（基于官方第一周社区回顾）
链接：https://www.atlascloud.ai/zh-TW/blog/tips/minimax-h3-prompts ｜ 提示词库 https://github.com/AtlasCloudAI/awesome-minimax-h3-prompts
要点：
- 官方报道的创作者习惯：RTX 3060 本地 480p 迭代筛选 → 云端 2K 定稿；两端唯一资产是提示词
- 52 个官方原始提示词（16 分类、带预览视频），抽卡起步直接抄
- 对"笔记本策划 / 台式机算力"双机流水线直接可套

**9. 实测参数避坑（社区）**
来源：今日头条实测文
链接：https://www.toutiao.com/article/7673664291479765506/
要点：
- 采样 25-35 步（新手别低于 20）、CFG 7-9；超 12 秒尾帧画质下降，拆 5-8 秒段再拼
- 参考视频降帧率只留关键帧再喂；透明 PNG 参考易预处理异常，用 JPG；音频必须写进 prompt 否则电流杂音

## 2026-08-18（第三轮）

### ⚙ ComfyUI 核心更新（本轮最优先项）

**1. ComfyUI v0.32.0 发布（8/12）：H3 专项修复 + 动态显存卸载**
来源：官方（ComfyUI GitHub / AGI Hunt / 网易）
链接：https://dy.163.com/article/L48NT8KB05563UC5.html ｜ https://agihunt.info/e/19ff46900943258c6e9e6778563
要点：
- 优化 MiniMax-H3 VAE、**修复 H3 峰值显存问题**、修复 VAEDecodeTiled 嵌套张量崩溃；最低 PyTorch 升到 2.7
- 新增 comfy-aimdo 动态显存卸载机制（NVML 监控、双流异步 offload）——**16GB 卡跑 19.5GB 的 pruned_int8_convrot 不再爆显存**（日文实测峰值 15.3GB 内，无需 --reserve-vram）
- 4060Ti 台式机 ComfyUI v0.30.1 建议直接升 0.32.0，H3 稳定性/显存收益最直接

**2. Ada 显卡上 fp8 vs int8 实测：int8_convrot 胜出 17%**
来源：社区实测（note.com sash_02，4070 Ti SUPER 16GB 全流程记录）
链接：https://note.com/sash_02/n/n0b141c7e6e96
要点：
- 同体积下 pruned_int8_convrot（19.53GB）比 pruned_fp8_scaled（19.52GB）**快 17%**（425s vs 498s，3 次同 seed），画质无差异——因为 ComfyUI 对 int8-convrot 有专用 kernel（convrot_w4a4/int8_linear/w4a8_int8_linear）
- NVFP4 在 Ada 上是"模拟"回退全精度运算，选它只为省 10.7GB 体积，不为速度
- 4060Ti（Ada SM89）同结论：**选 pruned_int8_convrot，别选 fp8_scaled**

### ⚙ 加速/量化新货

**3. Kijai 更新 4 步 Turbo LoRA（LightX2V 蒸馏，8/16）：新增 315MB 降秩版**
来源：HF（Kijai/MiniMax-H3_comfy，2 commits 前天）
链接：https://huggingface.co/Kijai/MiniMax-H3_comfy
要点：
- 新增 `minimax_h3_fl2v_lightx2v_turbo_4step_v0.1_comfy_resized_avg_rank_21_bf16.safetensors`（**315MB**，比标准版 1.96GB 小 80%+），低显存优先
- 专为 ComfyUI 重打包：QKV 融合 + 键名对齐，**pruned 底模直接可用**；修复低步数爆音（音频解码同步 bug）
- 用法：强度 0.75、采样器 er_sde 或 sa_solver、4 步；画质优先用 larryvrh v4_step600_ema 6-8 步
- 对 4060Ti 16GB：315MB 版 + pruned_int8 底模是最省显存组合

**4. Winnougan W4A8 pruned 模型（11.6GB）：3060 12GB 级别全分辨率可跑**
来源：社区（jurn.link 8/13 完整教程 + 工作流 JSON）
链接：https://jurn.link/dazposer/index.php/2026/08/13/success-minimax-h3-video-at-1376-x-768px-on-a-3060-12gb-card/
要点：
- `minimax_h3_fl2va_pruned-w4a8_convrot_pruned.safetensors` 与 ref2va 版各 11.6GB，编码器 qwen3vl w4a8 14.6GB，视频 VAE 用 Kijai int8_convrot（3.7GB）
- 3060 12GB + 24GB RAM 实测：1376×768（原生 1.0 分辨率）7 秒约 12-18 分钟；0.9 分辨率是性价比甜点
- 配 Kitchen Attention 低端卡再快 20-30%；注意 Q2 GGUF 提示词遵循差，别用极限压缩版处理 prompt

**5. Comfy Kitchen Attention（ModelAttentionBackend 节点）落地**
来源：社区（jurn.link 教程）
要点：
- ComfyUI 0.32.0+ 内置的 SageAttention 替代注意力后端，加一个 `ModelAttentionBackend` 节点切到 Kitchen Attention 即可，低端卡实测 20-30% 提速（50 系提升有限）
- 与 SageAttention 二选一，别叠加

### 🎬 视频博主 / 工作流

**6. 雷先生：H3 全参数速查 + 多速率分离采样（音频防爆音方案）**
来源：视频博主（公众号"雷先生"，3070Ti 8G / 5070Ti 16G 双实测）
要点：
- 黄金参数：res_multistep + simple、18-22 步（成片 20 步封顶）、CFG 7-9；**单镜头 5-7 秒铁律**，超 10 秒尾帧糊/人物漂移
- **音频 VAE 必须 fp32（fp16 直接爆音/时序错位，80% 新手坑）**，视频 VAE fp16
- 多速率分离采样（T8 双时钟）：视频 6 步 + 音频 10 步分开设，缓解 Turbo 后爆音；节点顺序：模型加载器→LoRA→SageAttention→采样器
- 组合建议：成片 SageAttention+Spectrum；预览 SageAttention+Turbo-LoRA；**三者全叠音频必崩**；Turbo 工作流切回普通流需重启 ComfyUI
- GGUF 档位参考：q4_k_m 7.6GB（8GB 极限）、pruned_int8_convrot 21GB（8-12GB）

**7. ComfyUI-H3-FaceRefine 节点 + 远景脸崩修复工作流**
来源：社区（AGI HUNT 8/14 日报）
链接：https://agihunt.info/daily/2026-08-14
要点：
- 远景人脸崩坏传统放大工具救不了：先裁剪面部区域→低重噪重生成→合成回原帧，社区开源了 ComfyUI 工作流并被封装成 `ComfyUI-H3-FaceRefine` 即用节点
- 对短剧/长镜头很实用：官方承认脸糊是系统级问题（最高优先级修复中），开源版短期内靠这个兜底

**8. ComfyUI-MiniMax-H3-Studio 工作流：H3 当图像模型用**
来源：社区（AGI HUNT 8/17 日报）
链接：https://agihunt.info/daily/latest
要点：
- 集成文生图/图生图/参考图编辑/Qwen3-VL 提示词分析/面部优化/显存优化——H3 指令遵循强，社区实测风格还原优于 GPT Image 2
- 配合官方路线图"专用图像模型开发中"，现阶段可先用 H3 5 帧抽首帧当 T2I 用，再交给 I2VA 成片

**9. 生态盘点（AGI HUNT 8/17 日报）**
来源：资讯聚合
链接：https://agihunt.info/daily/latest
要点：
- 8GB 显存可行流程：ref2va + turbo lora + 6 步 + 0.5MP；4070 Ti Super 16GB：1.6MP 30 步 6 秒约 38 分钟
- FL2VA+REF2VA **混合模型**（b20-49 保参考一致性 / b30-49 保画质）：解决官方无法"锁首帧 + 额外参考图"同时用的问题
- ClipProj v3.1：把 15GB 大文本编码器换成 4B/8B 小矩阵，11 种语言语音表现改进
- RTX Pro 6000 突破 324 帧上限出 42 秒（画质下降）；H3-Motion-Context 项目用复用 latent 链式接长片段

**10. RedCraft REDMIX Hybrid A2A beta1（Civitai）：单模型"三通"**
来源：Civitai（红潮制作组）
链接：https://civitai.red/models/958009/redcraft-or-2-or-3-int8int4fp8-scaled
要点：
- 整合 LightX2V Turbo + Kijai Ref2V 权重分离 + Astral 星芒 ContextIR A2A 节点 + 美学 LoRA，单工作流实现首帧/尾帧/上下文参考三通 + 多模态一步生成
- beta 阶段，正式版将集成 LTX 2.5 蒸馏作 2K 方案；适合喜欢"一个节点包搞定所有模式"的用法

### 📢 官方路线图（确认无新落地）

- H3-Regenerate-2K、稀疏注意力（MoBA-style 块选择）参考实现、官方 4/8-NFE 版**截至 8/18 均未发布**，AMA（8/7）承诺的"不会太久"尚无下文；h3-prompt-writing 技能无修订
- 本地 2K 现实路径不变：本地出 768p → 超分/重生成（Ultimate SD Upscale H3 分支实测：4080S 初生 1152×640 约 5 分钟、超分 2560×1472 约 20 分钟）

### 💡 对 4060Ti 16GB 流水线的行动项（按优先级）

1. **ComfyUI 升级 0.32.0**（H3 峰值显存修复 + 动态卸载 + Kitchen Attention），别停在 0.30.1
2. 底模选 **pruned_int8_convrot（19.5GB）**，0.32.0 动态卸载下 16GB 可跑；显存紧再换 Winnougan w4a8 11.6GB
3. 加速 LoRA 用 **Kijai 315MB 降秩 4 步版**（pruned 友好、修了爆音），成片 6-8 步 larryvrh v4 兜底
4. 音频 VAE 锁 fp32；加速后爆音开多速率采样（视频 6/音频 10 步）
5. 脸崩兜底装 ComfyUI-H3-FaceRefine；2K 用 Ultimate SD Upscale H3 分支替代 API
