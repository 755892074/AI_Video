# h3-ref2va-prompt

MiniMax H3 **REF2VA**（图/视频/音频参考 → 视频）模式的**官方六段式 prompt 生成器**。
解决 H3 生成时"中英混杂、旁白乱入、角色不一致、语言不受控"的根因问题。

> 背景：v1 用中文写正文 + 只提一句"语言中文" → 模型中英混杂、乱加旁白。
> v2 按本 skill 官方规范重写 → 验收通过。这是已验证的唯一正确写法。

## 何时触发

- 需要用 H3 REF2VA / ImageToVideo 生成带角色一致性的视频
- 用户要"还原某个电影情节/镜头""角色要像""要说中文对白"
- 生成结果出现中英混杂、乱加旁白、角色漂移时，先检查是否按本规范写

## 六段式结构（正文必须全英文，对白除外）

```
<Prompt>

<Subject 1>
<Picture 1> ... [定义人物/参考图标签]

<Summary>
... 一句话概括

<Retention Analysis>
Subject 1: fully_preserved / partially_preserved ...
Picture 1: fully_preserved ...

<Detailed Description>
(场景叙事，英文，第一人称现在时)
- 参考引用: [Picture 1], [Picture 2]
- 对白: (S1) <d>[Chinese] 我养你啊！</d>
- No narration, no other language. [每镜必须写死防旁白]

<Overall Soundscape>
环境音描述 ...

<Non-Diegetic Music>
配乐描述 ...

</Prompt>
```

## 硬规则

1. **正文全英文**；只有 `<d>` 标签内的对白保留原语言。
2. **对白必须** `<d>[Chinese] 台词</d>`（或 [English] 等），并加 `(S1)` 标明说话者。
3. **参考图必须标签化**：`<Subject N>` + `<Picture N>`，且 **Picture 编号必须与工作流 ref_images 实际顺序一一对应**（生成后必须脚本校验）。
4. **每镜详细描述末尾写死**：`No narration, no other language.`（防模型自己造旁白/换语言）。
5. `detailed_description` 里引用参考图用 `[Picture N]`、引用角色用 `[Subject N]`。
6. `<d>` 标签内的对白文字尽量用目标语言原文（如 `我养你啊！`），不要翻译。

## 使用方式

```bash
python scripts/builder.py --out ./prompts --shots shots.json
```

`shots.json` 结构（每个镜头一个 dict）：
```json
[
  {
    "name": "shot05",
    "seconds": 6,
    "action": "CU of the young man, he shouts to the car",
    "dialogue": "我养你啊！",
    "speaker": "S1",
    "refs": ["ref_man_01.jpg", "ref_scene_01.jpg"],
    "sound": "distant traffic, night breeze",
    "music": "slow piano, melancholic"
  }
]
```

也可在 Python 里直接 `from builder import build_prompt` 调用。

## 生成器输出

- `prompts/shot0X.txt`：六段式完整 prompt（可直接填入 H3 节点 prompt 输入框）
- 打印校验信息：Picture 编号 ↔ 实际 refs 顺序是否一致、对白标签是否齐全

## 常见错误

| 症状 | 原因 | 修法 |
|---|---|---|
| 中英混杂 | 正文写了中文 | 正文全英文，中文只进 `<d>` |
| 乱加旁白 | 没写 No narration | 每镜补 `No narration, no other language.` |
| 语言不对 | 对白没标 `[Chinese]` | `<d>[Chinese] 我养你啊！</d>` |
| 角色漂移 | Picture 编号与 refs 顺序错位 | 跑 builder 的校验，重排 refs |
| 声音杂乱 | 缺 soundscape/music 段 | 六段齐全，音景写具体 |
| 输出文件混旧前缀 | 提交脚本深拷贝 history 模板，SaveVideo 的 filename_prefix 被继承 | 每镜显式改 `filename_prefix` 为 `video/<proj>_<shotNN>` |

## 已验证能力：物体表面文字 / 内容（2026-08-29 实测）

> ⚠️ 旧经验认为"H3 文字类内容容易糊、应规避"——**已过时**。6 镜专项测试全部成功，物体表面文字生成可用。

**测试镜头（`tools/gen_screen_text_test.py` → `shots/screen_text_test_manifest.json`）**：
- 电视屏幕新闻画面 + 底部英文大写字幕 "THE ALTAR" → 完全可读
- 电视雪花屏中央深红中文大字「祭坛」→ 完全可读（走 `<d>[Chinese] 祭坛</d>` 通道）
- 翻开的魔法书，悬浮发光的金色符文 → 电影级效果
- 旧书印刷体英文段落 → 大部分单词清晰可读
- 墙挂油画人像（黑发贵妇）→ 画中内容细节出色
- 木牌深刻字 "THE ALTAR" → 古典衬线字体清晰

**写法要点**：
1. 文字要求**短**（单词/短词），明确指定位置（"bottom of the screen" / "center of the page"）、颜色、材质（"carved grooves" / "glowing runes" / "crisp white caption bar"）。
2. **中文画面文字**：放 `<d>[Chinese] 原文</d>` 里即可（与对白同通道，但只影响画面字幕，不影响对白）；不要直接写进英文正文。
3. 物体本身也要作为 Subject 定义（"an old CRT television..."），把"表面内容"作为该镜的视觉焦点写进 Detailed Description。
4. 场景图锚定（哥特厅 lantern_hall_v2）保持空间一致，角色参考图照常给。
