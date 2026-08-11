#!/usr/bin/env python3
"""
ComfyUI Dispatcher — AI视频自动化调度工具
=============================================
用途：将本地素材 + 工作流JSON 提交到远程 ComfyUI（台式机），监控队列，回收结果。

用法：
  python comfy_dispatcher.py submit <workflow.json> [--assets-dir DIR] [--comfy-url URL]
  python comfy_dispatcher.py status <prompt_id> [--comfy-url URL]
  python comfy_dispatcher.py download <prompt_id> [--output-dir DIR] [--comfy-url URL]
  python comfy_dispatcher.py run <workflow.json> [--assets-dir DIR] [--output-dir DIR] [--comfy-url URL] [--poll-interval SECS]

示例：
  # 提交并等待完成，自动下载结果
  python comfy_dispatcher.py run workflows/h3_imagetovideo_test.json --assets-dir assets

依赖：仅 Python 标准库（urllib, json, os, sys, time）
"""

import argparse
import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from pathlib import Path


# ============================================================
# 配置默认值
# ============================================================
DEFAULT_COMFY_URL = "http://100.67.139.74:8188"
DEFAULT_OUTPUT_DIR = "shots/ep01/output"
DEFAULT_ASSETS_DIR = None  # 不自动上传时为None
UPLOAD_IMAGE_ENDPOINT = "/upload/image"
PROMPT_ENDPOINT = "/prompt"
QUEUE_ENDPOINT = "/queue"
HISTORY_ENDPOINT = "/history"
VIEW_ENDPOINT = "/view"  # ?filename=xxx 用于下载输出文件
TIMEOUT_SECONDS = 30
POLL_INTERVAL_DEFAULT = 15  # 秒


# ============================================================
# HTTP 工具函数
# ============================================================
def api_get(url_path, base_url=DEFAULT_COMFY_URL, timeout=TIMEOUT_SECONDS):
    """GET 请求 ComfyUI API，返回解析后的 JSON。"""
    full_url = base_url.rstrip("/") + url_path
    req = urllib.request.Request(full_url)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"API GET {url_path} → {e.code} {e.reason}: {body[:500]}")
    except Exception as e:
        raise RuntimeError(f"API GET {url_path} 失败: {e}")


def api_post(url_path, data=None, base_url=DEFAULT_COMFY_URL, timeout=TIMEOUT_SECONDS):
    """POST 请求 ComfyUI API。data 为 dict 时自动 JSON 编码；为 bytes 时直接发送。"""
    full_url = base_url.rstrip("/") + url_path
    if isinstance(data, (dict, list)):
        body = json.dumps(data).encode("utf-8")
        content_type = "application/json"
    else:
        body = data
        content_type = "application/octet-stream"

    req = urllib.request.Request(full_url, data=body, headers={"Content-Type": content_type})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            try:
                return json.loads(raw)
            except json.JSONDecodeError:
                return raw
    except urllib.error.HTTPError as e:
        body_text = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"API POST {url_path} → {e.code} {e.reason}: {body_text[:500]}")
    except Exception as e:
        raise RuntimeError(f"API POST {url_path} 失败: {e}")


# ============================================================
# 素材上传
# ============================================================
def upload_image(local_path, base_url=DEFAULT_COMFY_URL, subdir="default"):
    """
    上传一张本地图片到 ComfyUI 的 /upload/image。
    返回 ComfyUI 内部使用的文件名（如 scene_01.png）。
    """
    if not os.path.isfile(local_path):
        raise FileNotFoundError(f"素材文件不存在: {local_path}")

    filename = os.path.basename(local_path)
    with open(local_path, "rb") as f:
        file_data = f.read()

    # multipart form-data 手动构建
    boundary = "----ComfyDispatcherBoundary7d4f9a2b1c8e6"
    lines = []
    lines.append(f"--{boundary}")
    lines.append(f'Content-Disposition: form-data; name="image"; filename="{filename}"')
    lines.append("Content-Type: image/png")
    lines.append("")
    # file data as raw bytes placeholder
    lines.append("__FILE_DATA__")
    lines.append(f"--{boundary}")
    lines.append('Content-Disposition: form-data; name="subdir"')
    lines.append("")
    lines.append(subdir)
    lines.append(f"--{boundary}--")

    body_str = "\r\n".join(lines)
    body = body_str.encode("utf-8").replace(b"__FILE_DATA__", file_data)

    full_url = base_url.rstrip("/") + UPLOAD_IMAGE_ENDPOINT
    req = urllib.request.Request(
        full_url,
        data=body,
        headers={
            "Content-Type": f"multipart/form-data; boundary={boundary}",
            "Content-Length": str(len(body)),
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as resp:
            result = json.loads(resp.read())
            print(f"  ✅ 已上传: {filename} → {result.get('name', '?')}")
            return result.get("name", filename)
    except urllib.error.HTTPError as e:
        err_body = e.read().decode("utf-8", errors="replace") if e.fp else ""
        raise RuntimeError(f"上传图片失败 {filename}: {e.code} {err_body[:300]}")


def upload_assets_dir(assets_dir, base_url=DEFAULT_COMFY_URL):
    """
    扫描资产目录，上传所有图片文件。
    返回 {原始文件名: ComfyUI内部名} 映射表。
    """
    mapping = {}
    extensions = {".png", ".jpg", ".jpeg", ".webp", ".gif", ".bmp"}
    for root, dirs, files in os.walk(assets_dir):
        dirs.sort()  # 保证顺序稳定
        files.sort()
        for fn in files:
            ext = os.path.splitext(fn)[1].lower()
            if ext in extensions:
                local_path = os.path.join(root, fn)
                comfy_name = upload_image(local_path, base_url)
                mapping[fn] = comfy_name
    return mapping


# ============================================================
# 提交任务
# ============================================================
def submit_workflow(workflow_json, asset_mapping=None, base_url=DEFAULT_COMFY_URL):
    """
    提交工作流 JSON 到 ComfyUI /prompt API。
    - workflow_json: dict 或 JSON 文件路径
    - asset_mapping: {local_filename: comfy_filename} 用于替换引用
    返回 prompt_id。
    """
    if isinstance(workflow_json, (str, Path)):
        with open(workflow_json, "r", encoding="utf-8") as f:
            workflow = json.load(f)
    elif isinstance(workflow_json, dict):
        workflow = workflow_json
    else:
        raise TypeError("workflow_json 必须是 dict、str 或 Path")

    # 如果有资产映射，替换工作流中 LoadImage 节点的文件名
    if asset_mapping:
        for node_id, node_data in workflow.items():
            cls = node_data.get("class_type", "")
            inputs = node_data.get("inputs", {})
            if cls == "LoadImage" and "image" in inputs:
                img_name = inputs["image"]
                if img_name in asset_mapping:
                    old = inputs["image"]
                    inputs["image"] = asset_mapping[img_name]
                    print(f"  🔄 替换引用: [{node_id}] {old} → {asset_mapping[img_name]}")

    # 提交（ComfyUI 要求外层包裹 {"prompt": {...}}）
    payload = {"prompt": workflow}
    result = api_post(PROMPT_ENDPOINT, payload, base_url)
    prompt_id = result.get("prompt_id")
    if not prompt_id:
        raise RuntimeError(f"提交失败，未返回 prompt_id: {json.dumps(result)[:300]}")

    print(f"✅ 任务已提交! prompt_id={prompt_id}")
    print(f"   查看状态: python comfy_dispatcher.py status {prompt_id}")
    return prompt_id


# ============================================================
# 队列监控
# ============================================================
def get_queue_status(base_url=DEFAULT_COMFY_URL):
    """返回当前队列状态 dict。"""
    return api_get(QUEUE_ENDPOINT, base_url)


def is_prompt_running(prompt_id, base_url=DEFAULT_COMFY_URL):
    """检查指定 prompt 是否正在运行或排队中。"""
    queue = get_queue_status(base_url)
    running = queue.get("queue_running", [])
    pending = queue.get("queue_pending", [])

    all_items = running + pending
    for item in all_items:
        # item 格式可能多样，尝试多种字段
        pid = (
            item.get("prompt_id")
            or (item.get([1], {}).get("prompt_id") if isinstance(item.get([1]), dict) else None)
            or (item[1].get("prompt_id") if isinstance(item, list) and len(item) > 1 and isinstance(item[1], dict) else None)
        )
        if pid == prompt_id:
            return True, item
    return False, None


def wait_for_completion(prompt_id, poll_interval=POLL_INTERVAL_DEFAULT, base_url=DEFAULT_COMFY_URL, timeout_secs=3600):
    """
    轮询等待任务完成。
    返回 (success: bool, history_entry: dict or None)。
    """
    start_time = time.time()

    while True:
        elapsed = int(time.time() - start_time)
        if elapsed > timeout_secs:
            print(f"\n⏰ 超时 ({timeout_secs}s)，任务可能仍在运行")
            return False, None

        # 检查队列
        queue = get_queue_status(base_url)
        running_count = len(queue.get("queue_running", []))
        pending_count = len(queue.get("queue_pending", []))

        # 检查历史记录看是否已完成
        try:
            history = api_get(HISTORY_ENDPOINT, base_url)
        except Exception as e:
            print(f"\n  ⚠️ 查询历史失败: {e}，{poll_interval}s 后重试...")
            time.sleep(poll_interval)
            continue

        if prompt_id not in history:
            if elapsed < 10:
                # 刚提交可能还没进历史
                time.sleep(poll_interval)
                continue
            else:
                print(f"\n❌ 任务 {prompt_id[:12]} 未在历史中找到（可能被拒绝或 ID 错误）")
                return False, None

        entry = history[prompt_id]
        status = entry.get("status", {})
        status_str = status.get("status_str", "")
        completed = status.get("completed", False)
        msgs = status.get("messages", [])

        # 提取错误信息
        exec_errors = []
        if isinstance(msgs, list):
            for m in msgs:
                if isinstance(m, list) and len(m) >= 2 and m[0] in ("execution_error", "error"):
                    exec_errors.append(str(m[1]) if len(m) > 1 else str(m))

        if completed or status_str == "success":
            if exec_errors:
                print(f"\n❌ 任务完成但有执行错误:")
                for err in exec_errors:
                    print(f"   !! {err}")
                return False, entry
            print(f"\n✅ 任务完成! ({elapsed}s)")
            return True, entry
        elif status_str == "error":
            msg_detail = exec_errors[0] if exec_errors else "未知错误"
            print(f"\n❌ 任务出错: {msg_detail}")
            return False, entry

        # 显示进度
        bar_len = 20
        dot = "⠋⠙⠹⠸⠼⠴⠦⠧⠇⠏"[elapsed % 10]
        progress = min(elapsed % 60, 59)
        filled = int((progress / 60.0) * bar_len)
        bar = "█" * filled + "░" * (bar_len - filled)
        sys.stdout.write(
            f"\r  {dot} 排队:{pending_count} 运行:{running_count} "
            f"[{bar}] {elapsed}s"
        )
        sys.stdout.flush()

        time.sleep(poll_interval)


# ============================================================
# 结果下载
# ============================================================
def find_output_files(history_entry):
    """
    从历史条目中提取输出文件路径列表。
    返回 [(filename, subfolder), ...]
    """
    outputs = history_entry.get("outputs", {})
    files_list = []
    for node_id, node_output in outputs.items():
        if isinstance(node_output, dict):
            images = node_output.get("images", [])
            if images:
                for img in images:
                    filename = img.get("filename", "")
                    subfolder = img.get("subfolder", "")
                    if filename:
                        files_list.append((filename, subfolder))
            # 也检查 videos / gifs
            for key in ("videos", "gifs"):
                media = node_output.get(key, [])
                if media:
                    for m in media:
                        filename = m.get("filename", "")
                        subfolder = m.get("subfolder", "")
                        if filename:
                            files_list.append((filename, subfolder))
    return files_list


def download_file(filename, subfolder="", output_dir=DEFAULT_OUTPUT_DIR, base_url=DEFAULT_COMFY_URL):
    """从 ComfyUI 下载一个输出文件到本地。"""
    os.makedirs(output_dir, exist_ok=True)

    params = {"filename": filename}
    if subfolder:
        params["subfolder"] = subfolder
    query = urllib.parse.urlencode(params)
    url = base_url.rstrip("/") + "/view?" + query

    req = urllib.request.Request(url)
    try:
        with urllib.request.urlopen(req, timeout=300) as resp:
            data = resp.read()

        local_path = os.path.join(output_dir, filename)
        with open(local_path, "wb") as f:
            f.write(data)

        size_mb = len(data) / (1024 * 1024)
        print(f"  📥 已下载: {filename} ({size_mb:.1f} MB) → {local_path}")
        return local_path
    except Exception as e:
        print(f"  ⚠️ 下载失败 {filename}: {e}")
        return None


def download_results(prompt_id, output_dir=DEFAULT_OUTPUT_DIR, base_url=DEFAULT_COMFY_URL):
    """下载指定任务的所有输出文件。"""
    history = api_get(HISTORY_ENDPOINT, base_url)
    if prompt_id not in history:
        print(f"❌ 未找到任务 {prompt_id} 的历史记录")
        return []

    entry = history[prompt_id]
    files_list = find_output_files(entry)
    if not files_list:
        print(f"⚠️ 任务 {prompt_id} 没有输出文件")
        return []

    downloaded = []
    for filename, subfolder in files_list:
        path = download_file(filename, subfolder, output_dir, base_url)
        if path:
            downloaded.append(path)

    print(f"\n📁 共下载 {len(downloaded)} 个文件到 {os.path.abspath(output_dir)}")
    return downloaded


def validate_outputs(downloaded_files, min_size_kb=10):
    """
    校验下载的输出文件。
    返回 (valid: bool, report: str)。
    - 检查文件大小（过小说明可能生成失败）
    - 对 MP4 检查文件头
    """
    if not downloaded_files:
        return False, "无输出文件"

    issues = []
    valid_count = 0

    for path in downloaded_files:
        if not os.path.exists(path):
            issues.append(f"  ❌ 文件不存在: {path}")
            continue

        size = os.path.getsize(path)
        size_kb = size / 1024
        ext = os.path.splitext(path)[1].lower()

        # 大小检查
        if size_kb < min_size_kb:
            issues.append(f"  ⚠️ 文件过小 ({size_kb:.1f} KB): {os.path.basename(path)} — 可能生成异常")

        # 格式检查
        if ext == ".mp4":
            try:
                with open(path, "rb") as f:
                    header = f.read(12)
                if header[:4] != b"ftyp":
                    issues.append(f"  ❌ 非标准MP4: {os.path.basename(path)} (头={header[:4].hex()})")
                else:
                    valid_count += 1
                    print(f"  ✅ 有效MP4: {os.path.basename(path)} ({size_kb:.1f} MB)")
            except Exception as e:
                issues.append(f"  ⚠️ 无法读取: {os.path.basename(path)} ({e})")
        else:
            valid_count += 1
            print(f"  ✅ 文件OK: {os.path.basename(path)} ({size_kb:.1f} KB)")

    if issues:
        print("\n📋 校验报告:")
        for issue in issues:
            print(issue)

    is_valid = len(issues) == 0
    status = "✅ 全部通过" if is_valid else f"⚠️ {len(issues)} 个问题"
    print(f"\n🔍 输出校验: {status}")
    return is_valid, "\n".join(issues)


# ============================================================
# CLI 入口
# ============================================================
def cmd_submit(args):
    """提交工作流（可选上传素材）。"""
    asset_mapping = None
    if args.assets_dir and os.path.isdir(args.assets_dir):
        print(f"📤 上传素材目录: {args.assets_dir}")
        asset_mapping = upload_assets_dir(args.assets_dir, args.comfy_url)

    prompt_id = submit_workflow(args.workflow, asset_mapping, args.comfy_url)
    print(f"\n提示：")
    print(f"  监控: python comfy_dispatcher.py status {prompt_id}")
    print(f"  下载: python comfy_dispatcher.py download {prompt_id}")
    return prompt_id


def cmd_status(args):
    """查看任务/队列状态。"""
    if args.prompt_id == "queue":
        queue = get_queue_status(args.comfy_url)
        running = queue.get("queue_running", [])
        pending = queue.get("queue_pending", [])
        print(f"运行中: {len(running)} | 排队中: {len(pending)}")
        for i, item in enumerate(running):
            print(f"  🔵 [{i}] {item}")
        for i, item in enumerate(pending):
            print(f"  🟡 [{i}] {item}")
        return

    # 检查特定任务
    history = api_get(HISTORY_ENDPOINT, args.comfy_url)
    if args.prompt_id in history:
        entry = history[args.prompt_id]
        status = entry.get("status", {})
        print(f"任务 {args.prompt_id}:")
        print(f"  状态: {status.get('status_str', '未知')}")
        messages = status.get("messages", [])
        if messages:
            for m in messages[-3:]:
                print(f"  消息: {m}")
        outputs = find_output_files(entry)
        if outputs:
            print(f"  输出文件 ({len(outputs)}):")
            for fn, sf in outputs:
                print(f"    - {fn} ({sf})")
    else:
        # 可能还在队列里
        running, _ = is_prompt_running(args.prompt_id, args.comfy_url)
        if running:
            print(f"任务 {args.prompt_id}: 🔄 正在运行/排队中...")
        else:
            print(f"任务 {args.prompt_id}: ❓ 未找到（可能已被清理或 ID 错误）")


def cmd_download(args):
    """下载任务结果。"""
    downloaded = download_results(args.prompt_id, args.output_dir, args.comfy_url)
    if downloaded:
        for p in downloaded:
            print(f"  → {p}")


def cmd_run(args):
    """一键提交+等待+下载（完整流水线）。"""
    print("=" * 50)
    print("🚀 ComfyUI Dispatcher — 一键运行模式")
    print("=" * 50)

    # 1. 上传素材
    asset_mapping = None
    if args.assets_dir and os.path.isdir(args.assets_dir):
        print(f"\n📤 [1/3] 上传素材...")
        asset_mapping = upload_assets_dir(args.assets_dir, args.comfy_url)
    else:
        print(f"\n📤 [1/3] 跳过素材上传（未指定 --assets-dir）")

    # 2. 提交
    print(f"\n📋 [2/3] 提交工作流...")
    prompt_id = submit_workflow(args.workflow, asset_mapping, args.comfy_url)

    # 3. 等待完成
    print(f"\n⏳ [3/3] 等待生成... (H3 视频约需 10–20 分钟)")
    success, entry = wait_for_completion(
        prompt_id,
        poll_interval=args.poll_interval,
        base_url=args.comfy_url,
    )

    if not success:
        print("\n⚠️ 任务未成功完成，尝试下载已有输出...")
        if entry:
            # 即使报错也可能有部分输出
            files_list = find_output_files(entry)
            if files_list:
                print(f"发现 {len(files_list)} 个输出文件，尝试下载...")
            else:
                print("无输出文件可下载")
                return prompt_id
        else:
            return prompt_id

    # 4. 下载
    print(f"\n📥 下载结果...")
    downloaded = download_results(prompt_id, args.output_dir, args.comfy_url)

    # 5. 校验输出
    print(f"\n🔍 校验输出文件...")
    output_ok, validation_report = validate_outputs(downloaded)
    if not output_ok:
        print(f"\n⚠️ 输出校验未通过，视频可能异常（检查工作流节点连接和参数）")

    print(f"\n{'=' * 50}")
    print(f"{'✅' if output_ok else '⚠️'} 完成! prompt_id={prompt_id}")
    if downloaded:
        print(f"📁 结果文件:")
        for p in downloaded:
            size_kb = os.path.getsize(p) / 1024
            print(f"   • {os.path.basename(p)} ({size_kb:.1f} KB)")
    print(f"{'=' * 50}")
    return prompt_id


def main():
    parser = argparse.ArgumentParser(
        description="ComfyUI Dispatcher — AI视频自动化调度工具",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s run workflows/my_flow.json --assets-dir shots/ep01/assets
  %(prog)s submit workflows/my_flow.json
  %(prog)s status <prompt_id>
  %(prog)s download <prompt_id> --output-dir my_output
        """,
    )

    parser.add_argument("--comfy-url", default=DEFAULT_COMFY_URL, help=f"ComfyUI 地址 (默认: {DEFAULT_COMFY_URL})")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")
    parser.add_argument("--assets-dir", default=None, help="资产目录（自动扫描上传所有图片）")
    parser.add_argument("--poll-interval", type=int, default=POLL_INTERVAL_DEFAULT, help="轮询间隔秒数 (默认: 15)")

    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # submit
    p_submit = subparsers.add_parser("submit", help="提交工作流")
    p_submit.add_argument("workflow", help="工作流 JSON 文件路径")
    p_submit.add_argument("--assets-dir", default=None, help="资产目录（自动扫描上传所有图片）")

    # status
    p_status = subparsers.add_parser("status", help="查看状态")
    p_status.add_argument("prompt_id", nargs="?", default="queue", help="prompt_id 或 'queue' 查看全部队列")

    # download
    p_download = subparsers.add_parser("download", help="下载结果")
    p_download.add_argument("prompt_id", help="任务的 prompt_id")
    p_download.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")

    # run
    p_run = subparsers.add_parser("run", help="一键提交+等待+下载")
    p_run.add_argument("workflow", help="工作流 JSON 文件路径")
    p_run.add_argument("--assets-dir", default=None, help="资产目录（自动扫描上传所有图片）")
    p_run.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, help=f"输出目录 (默认: {DEFAULT_OUTPUT_DIR})")
    p_run.add_argument("--poll-interval", type=int, default=POLL_INTERVAL_DEFAULT, help="轮询间隔秒数 (默认: 15)")

    args = parser.parse_args()

    if args.command == "submit":
        cmd_submit(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "download":
        cmd_download(args)
    elif args.command == "run":
        cmd_run(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
