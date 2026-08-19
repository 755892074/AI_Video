# -*- coding: utf-8 -*-
"""
MiniMax H3 REF2VA 六段式 prompt 生成器
用法:
    python builder.py --shots shots.json --out ./prompts
    python builder.py --check prompt.txt   # 校验 Picture 标签与 refs 对应
"""
import argparse
import json
import re
import sys
from pathlib import Path


def build_prompt(shot: dict, subjects: list[dict] | None = None) -> str:
    """
    生成一个镜头的六段式 REF2VA prompt。

    shot 字段:
        name: 镜头名
        action: 英文动作/画面描述
        dialogue: 对白原文(目标语言), 无对白则 None
        speaker: 说话者, 如 "S1"
        refs: 该镜实际引用的参考图文件名列表(按 ref_images 传入顺序!)
        sound: 环境音描述
        music: 配乐描述
        narration_lock: 是否强制防旁白(默认 True)
    subjects: 可选的全局 Subject/Picture 定义列表, 每项 {"label": 描述, "picture": 图片名}
              若提供, 则自动生成 <Subject N> 段并与 refs 校验。
    """
    refs = shot.get("refs", [])
    name = shot.get("name", "shot")
    action = shot["action"]
    dialogue = shot.get("dialogue")
    speaker = shot.get("speaker", "S1")
    sound = shot.get("sound", "ambient night street sounds")
    music = shot.get("music", "none")

    # ---- 1. Subject Definitions ----
    subject_lines = []
    if subjects:
        for i, sub in enumerate(subjects, 1):
            pic = sub.get("picture")
            pic_note = f", [Picture {i}]" if pic else ""
            subject_lines.append(f"<Subject {i}>: {sub['label']}{pic_note}")
    subject_block = "\n".join(subject_lines) if subject_lines else (
        "No specific subject definitions, scenes only."
    )

    # ---- 2. Summary ----
    summary = action.replace("\n", " ")

    # ---- 3. Retention Analysis ----
    retention_lines = []
    if subjects:
        for i, sub in enumerate(subjects, 1):
            sub_ret = sub.get("retention", "partially_preserved")
            pic_ret = sub.get("picture_retention", sub_ret)
            if sub.get("picture"):
                retention_lines.append(f"Subject {i}: {sub_ret} - {sub.get('note', '')}".rstrip(" -"))
                retention_lines.append(f"Picture {i}: {pic_ret}")
            else:
                retention_lines.append(f"Subject {i}: {sub_ret} - {sub.get('note', '')}".rstrip(" -"))
    retention_block = "\n".join(retention_lines) if retention_lines else (
        "Pictures: partially_preserved (style, mood, lighting)."
    )

    # ---- 4. Detailed Description ----
    desc_parts = []
    if refs:
        ref_notes = ", ".join(f"[Picture {i}]" for i in range(1, len(refs) + 1))
        desc_parts.append(f"Reference: {ref_notes}")
    desc_parts.append(action)
    if dialogue:
        desc_parts.append(f"Dialogue: ({speaker}) <d>[Chinese] {dialogue}</d>")
    if shot.get("narration_lock", True):
        desc_parts.append("No narration, no other language.")
    description = "\n".join(desc_parts)

    # ---- 5. Overall Soundscape ----
    soundscape = sound

    # ---- 6. Non-Diegetic Music ----
    nd_music = music

    prompt = f"""<Prompt>

<Subject Definitions>
{subject_block}

<Summary>
{summary}

<Retention Analysis>
{retention_block}

<Detailed Description>
{description}

<Overall Soundscape>
{soundscape}

<Non-Diegetic Music>
{nd_music}

</Prompt>"""
    return prompt


def check_prompt(prompt: str, refs: list[str] | None = None) -> list[str]:
    """校验 prompt 的规范符合度, 返回问题列表(空=通过)。"""
    issues = []
    # 中文正文检查(排除 <d> 内)
    body = re.sub(r"<d>.*?</d>", "", prompt, flags=re.S)
    if re.search(r"[\u4e00-\u9fff]", body):
        issues.append("正文含有中文(应全英文, 中文只进 <d> 对白)")
    # 对白必须有 <d>[Language] 标签
    for m in re.finditer(r"<d>(.*?)</d>", prompt, re.S):
        inner = m.group(1)
        if not re.match(r"^\s*\[[A-Za-z]+\]", inner):
            issues.append(f"对白缺少语言标签: <d>{inner}</d> → 应 <d>[Chinese] ...</d>")
    # 防旁白
    if "No narration" not in prompt:
        issues.append("缺少防旁白锁定 'No narration, no other language.'")
    # Picture 编号连续性
    pics = sorted(set(int(x) for x in re.findall(r"\[Picture (\d+)\]", prompt)))
    if pics and pics != list(range(1, max(pics) + 1)):
        issues.append(f"Picture 编号不连续: {pics}")
    if refs is not None:
        expected = list(range(1, len(refs) + 1))
        if pics != expected:
            issues.append(f"Picture 编号({pics})与 refs 数量({len(refs)})不一致 → 应为 {expected}")
    return issues


def main() -> None:
    ap = argparse.ArgumentParser(description="H3 REF2VA 六段式 prompt 生成器")
    ap.add_argument("--shots", type=Path, help="shots.json 路径")
    ap.add_argument("--out", type=Path, default=Path("./prompts"), help="输出目录")
    ap.add_argument("--check", type=Path, help="仅校验一个已生成的 prompt 文件")
    args = ap.parse_args()

    if args.check:
        text = args.check.read_text(encoding="utf-8")
        issues = check_prompt(text)
        print("✅ 通过" if not issues else "❌ 问题:\n" + "\n".join(f"  - {i}" for i in issues))
        sys.exit(0 if not issues else 1)

    if not args.shots:
        sys.exit("需要 --shots 或 --check")
    data = json.loads(args.shots.read_text(encoding="utf-8"))
    shots = data["shots"] if isinstance(data, dict) and "shots" in data else data
    subjects = data.get("subjects") if isinstance(data, dict) else None

    args.out.mkdir(parents=True, exist_ok=True)
    for shot in shots:
        prompt = build_prompt(shot, subjects)
        out = args.out / f"{shot['name']}.txt"
        out.write_text(prompt, encoding="utf-8")
        issues = check_prompt(prompt, shot.get("refs"))
        status = "✅" if not issues else "❌ " + "; ".join(issues)
        print(f"{shot['name']}: {status}")
        if not issues:
            print(f"  对白: {shot.get('dialogue') or '(无)'} | refs: {len(shot.get('refs', []))}张")
    print(f"\n输出目录: {args.out}")


if __name__ == "__main__":
    main()
