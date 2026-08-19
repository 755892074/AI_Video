#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sync_assets.py — AI_Video 双机资产同步工具

用途：笔记本(策划端) / 台式机(渲染端) 之间通过 GitHub 同步
  1. 用户级 WorkBuddy 技能快照  ~/.workbuddy/skills/<name>/  ->  skills/workbuddy/
  2. H3 跟进简报                 Claw/.workbuddy/automations/h3-followup/report.md  ->  docs/h3-followup/

用法（在仓库根目录 F:\\WorkBuddy\\AI_Video 下）：
  python tools/sync_assets.py             # 笔记本用：pull -> 快照 -> commit(如有变更) -> push
  python tools/sync_assets.py --pull      # 仅拉取远端（台式机切机后先跑这个）
  python tools/sync_assets.py --push      # 仅快照+提交+推送
  python tools/sync_assets.py --restore   # 台式机用：pull -> 从仓库恢复技能到 ~/.workbuddy/skills/ + 报告到 Claw 工作区

注意：
  - 本机历史遗留的 git 全局代理(socks5://127.0.0.1:4781)已于 2026-08-19 清除；
    若某台机器 push 失败提示连不上，检查 `git config --global -l | grep proxy`。
  - snapshot 是单向的（用户目录 -> 仓库）；新机器用 --restore 反向恢复技能。
"""
import argparse
import datetime
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent  # 仓库根 F:/WorkBuddy/AI_Video
HOME = Path.home()

# ---- 同步清单（新增资产时往这里加）----
SKILLS = ["ai-video-pipeline", "h3-ref2va-prompt", "video-assemble"]  # ~/.workbuddy/skills/ 下
REPORTS = [  # (源路径, 仓库内相对路径)
    (Path(r"C:/Users/Lionel/WorkBuddy/Claw/.workbuddy/automations/h3-followup/report.md"),
     "docs/h3-followup/report.md"),
]


def run(cmd, check=True):
    """跑 git 命令，失败时打印输出。"""
    r = subprocess.run(cmd, cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode != 0 and check:
        print(f"[FAIL] {' '.join(cmd)}\n{r.stdout}\n{r.stderr}")
        sys.exit(1)
    return r


def snapshot():
    """把用户级资产复制进仓库，返回是否有变更。"""
    import shutil
    changed = []
    for name in SKILLS:
        src = HOME / ".workbuddy" / "skills" / name
        if not src.is_dir():
            print(f"[skip] 技能不存在: {src}")
            continue
        dst = REPO / "skills" / "workbuddy" / name
        if dst.exists():
            shutil.rmtree(dst)
        shutil.copytree(src, dst)
        changed.append(f"skills/workbuddy/{name}")
    for src, rel in REPORTS:
        if not src.is_file():
            print(f"[skip] 报告不存在: {src}")
            continue
        dst = REPO / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        changed.append(rel)
    return changed


def restore():
    """台式机用：从仓库快照反向恢复到用户目录。返回恢复列表。"""
    import shutil
    restored = []
    for name in SKILLS:
        src = REPO / "skills" / "workbuddy" / name
        if not src.is_dir():
            print(f"[skip] 仓库无技能快照: {src}")
            continue
        dst = HOME / ".workbuddy" / "skills" / name
        if dst.exists():
            shutil.rmtree(dst)
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copytree(src, dst)
        restored.append(f"~/.workbuddy/skills/{name}")
    # H3 报告恢复到 Claw 自动化工作区（与笔记本同构）
    report_rel = "docs/h3-followup/report.md"
    src = REPO / report_rel
    if src.is_file():
        dst = HOME / "WorkBuddy" / "Claw" / ".workbuddy" / "automations" / "h3-followup" / src.name
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        restored.append(str(dst))
    return restored


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pull", action="store_true", help="仅拉取远端")
    ap.add_argument("--push", action="store_true", help="仅快照+提交+推送")
    ap.add_argument("--restore", action="store_true", help="台式机用：pull后从仓库恢复技能与报告")
    args = ap.parse_args()

    if args.restore:
        print("== git pull ==")
        run(["git", "pull", "--ff-only", "origin", "main"])
        restored = restore()
        print(f"== 恢复 {len(restored)} 项 ==")
        for r in restored:
            print(f"  + {r}")
        print("恢复完成")
        return

    if args.pull or (not args.push):
        print("== git pull ==")
        run(["git", "pull", "--ff-only", "origin", "main"])
        if args.pull:
            return

    changed = snapshot()
    if not changed:
        print("无资产变更，跳过提交")
    else:
        print(f"== 快照 {len(changed)} 项 ==")
        for c in changed:
            run(["git", "add", c])
        status = run(["git", "status", "--short"])
        if status.stdout.strip():
            msg = f"chore: 资产同步({'/'.join(changed)}) {datetime.date.today()}"
            run(["git", "commit", "-m", msg])
        else:
            print("内容与上次快照一致，跳过提交")

    print("== git push ==")
    run(["git", "push", "origin", "main"])
    print("同步完成")


if __name__ == "__main__":
    main()
