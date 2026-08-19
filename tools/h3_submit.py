#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""通用 H3 REF2VA 提交工具（数据驱动）。

读取剧本数据 script.json，对每镜：
  1. 上传 refs 引用的素材到台式机 ComfyUI input（remote 名，覆盖幂等）
  2. 用 h3-ref2va-prompt/builder 编译六段式 prompt
  3. 基于工作流模板编译出该镜 workflow
  4. 校验并提交到台式机，记录 prompt_id

用法:
    python tools/h3_submit.py --script scripts/xiaole_baishi/script.json --project xiaole_baishi
    python tools/h3_submit.py --script ... --project ... --gen-only   # 只生成不提交
"""
import argparse, copy, json, sys, urllib.request, urllib.error, uuid
from pathlib import Path

BASE = "http://100.67.139.74:8188"
SKILL_DIR = Path(r"C:/Users/Lionel/.workbuddy/skills/h3-ref2va-prompt/scripts")
sys.path.insert(0, str(SKILL_DIR))
from builder import build_prompt, check_prompt  # noqa: E402


def upload_file(local: Path, remote_name: str) -> str:
    """上传素材到台式机 input，返回实际远程文件名。同名覆盖是幂等的。"""
    data = local.read_bytes()
    ext = local.suffix.lower() or ".png"
    name = remote_name if remote_name.lower().endswith(ext) else remote_name + ext
    boundary = uuid.uuid4().hex
    body = b""
    body += f"--{boundary}\r\n".encode()
    body += f'Content-Disposition: form-data; name="image"; filename="{name}"\r\n'.encode()
    body += f"Content-Type: image/{ext.lstrip('.')}\r\n\r\n".encode()
    body += data + b"\r\n"
    body += f"--{boundary}\r\nContent-Disposition: form-data; name=\"type\"\r\n\r\ninput\r\n".encode()
    body += f"--{boundary}--\r\n".encode()
    req = urllib.request.Request(
        f"{BASE}/upload/image", data=body, method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.load(r)["name"]
    except urllib.error.HTTPError as e:
        print(f"  ❌ 上传失败 {name}: HTTP {e.code} {e.read().decode()[:200]}")
        raise


def build_workflow(shot: dict, prompt: str, remote_refs: list[str],
                   tpl: dict, project: str) -> dict:
    wf = copy.deepcopy(tpl)
    load_ids = sorted(nid for nid, n in wf.items() if n.get("class_type") == "LoadImage")
    h3_id = next(nid for nid, n in wf.items() if n.get("class_type") == "MiniMaxH3ReferenceToVideo")
    float_id = next(nid for nid, n in wf.items() if n.get("class_type") == "PrimitiveFloat")
    save_id = next(nid for nid, n in wf.items() if n.get("class_type") == "SaveVideo")
    max_id = max(int(n) for n in wf)

    # 1) LoadImage 节点与 refs 一一对应
    n_refs = len(remote_refs)
    if n_refs <= len(load_ids):
        keep = load_ids[:n_refs]
        for nid, fname in zip(keep, remote_refs):
            wf[nid]["inputs"]["image"] = fname
        for nid in load_ids[n_refs:]:
            del wf[nid]
        load_map = {i: nid for i, nid in enumerate(keep)}
    else:
        for nid, fname in zip(load_ids, remote_refs[:len(load_ids)]):
            wf[nid]["inputs"]["image"] = fname
        load_map = {i: nid for i, nid in enumerate(load_ids)}
        nxt = max_id + 1
        for i in range(len(load_ids), n_refs):
            new_id = str(nxt)
            wf[new_id] = {"class_type": "LoadImage", "_meta": {"title": f"LoadImage {i+1}"},
                          "inputs": {"image": remote_refs[i]}}
            load_map[i] = new_id
            nxt += 1

    # 2) 重建 ref_images
    h3 = wf[h3_id]
    for k in list(h3["inputs"]):
        if k.startswith("ref_images"):
            del h3["inputs"][k]
    for i, nid in load_map.items():
        h3["inputs"][f"ref_images.ref_image_{i}"] = [nid, 0]

    # 3) prompt / 秒数 / 输出名
    h3["inputs"]["prompt"] = prompt
    wf[float_id]["inputs"]["value"] = float(shot["seconds"])
    wf[save_id]["inputs"]["filename_prefix"] = f"video/{project}_{shot['name']}"

    # 4) 分辨率统一 1MP (1376x768)
    for nid, n in wf.items():
        if n.get("class_type") == "ResolutionSelector":
            n["inputs"]["megapixels"] = 1.0

    return wf


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True, help="script.json 路径")
    ap.add_argument("--project", required=True, help="项目名，如 xiaole_baishi")
    ap.add_argument("--gen-only", action="store_true", help="只生成 workflow，不提交")
    ap.add_argument("--only", default=None, help="只处理指定镜，逗号分隔，如 shot01,shot03")
    ap.add_argument("--template", default="F:/WorkBuddy/AI_Video/workflows/h3_ref2va_v1_api.json")
    args = ap.parse_args()

    script = json.loads(Path(args.script).read_text(encoding="utf-8"))
    tpl = json.loads(Path(args.template).read_text(encoding="utf-8"))
    print(f"加载剧本: {script.get('title', '')} | {len(script['shots'])} 镜")

    # 上传所有用到的 refs（一次性）
    refs_meta = script["refs"]
    remote_names = {}
    for key, meta in refs_meta.items():
        local = Path(meta["local"])
        remote = meta.get("remote") or local.name
        if args.gen_only:
            remote_names[key] = remote
        else:
            print(f"上传 {key}: {local.name} → {remote}")
            remote_names[key] = upload_file(local, remote)

    results = []
    only_set = {x.strip() for x in args.only.split(",")} if args.only else None
    for shot in script["shots"]:
        if only_set and shot["name"] not in only_set:
            continue
        remote_refs = [remote_names[r] for r in shot["refs"]]
        subjects = [script["subjects"][r] for r in shot["refs"]]
        prompt = build_prompt(shot, subjects)
        issues = check_prompt(prompt, shot["refs"])
        wf = build_workflow(shot, prompt, remote_refs, tpl, args.project)

        out_dir = Path(args.script).parent / "shots"
        out_dir.mkdir(exist_ok=True)
        (out_dir / f"{shot['name']}.json").write_text(
            json.dumps(wf, ensure_ascii=False), encoding="utf-8")

        status = "✅" if not issues else "❌ " + "; ".join(issues)
        print(f"{shot['name']} ({shot['seconds']}s): {status} refs={remote_refs}")
        if issues:
            continue
        if args.gen_only:
            continue
        body = json.dumps({"prompt": wf}, ensure_ascii=False).encode("utf-8")
        req = urllib.request.Request(f"{BASE}/prompt", data=body, method="POST",
                                     headers={"Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                pid = json.load(r)["prompt_id"]
            print(f"  → 提交成功 prompt_id: {pid}")
            results.append({"name": shot["name"], "pid": pid, "seconds": shot["seconds"]})
        except Exception as e:
            print(f"  → 提交失败: {e}")

    if results:
        pids_path = Path(args.script).parent / "pids.json"
        pids_path.write_text(json.dumps(results, ensure_ascii=False, indent=1), encoding="utf-8")
        print(f"\n{len(results)} 镜已提交, pid 记录: {pids_path}")


if __name__ == "__main__":
    main()
