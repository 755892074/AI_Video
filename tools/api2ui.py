#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
api2ui.py — 把 H3 的 API 格式工作流 ({"prompt": {...}}) 转成 ComfyUI UI 格式
（带 nodes/links/pos，可直接拖进 ComfyUI WebUI 直观看到流程图）。

用法:
    python api2ui.py <input_api.json> <output_ui.json> [--comfy http://ip:8188]

原理:
    1. 从台式机 ComfyUI /object_info 拉取每个节点类型的输入/输出定义
    2. 按 API 里的实际输入值生成节点槽位（widget 或 link）
    3. 自动网格排布节点位置，生成 links 数组
"""
import json, os, sys, urllib.request

COMFY = "http://100.67.139.74:8188"
_cache = {}

def get_object_info():
    if "info" not in _cache:
        resp = urllib.request.urlopen(f"{COMFY}/object_info", timeout=30).read()
        _cache["info"] = json.loads(resp)
    return _cache["info"]

def get_node_def(class_type):
    info = get_object_info()
    return info.get(class_type, {})

def is_link_val(v):
    """API 输入值 -> 是否连线 (["node_id", slot])"""
    if isinstance(v, list) and len(v) == 2 and isinstance(v[0], str):
        try:
            int(v[0])
            return True, (str(v[0]), int(v[1]))
        except ValueError:
            pass
    return False, None

def collect_input_defs(node_def):
    """收集节点所有输入定义: name -> (type_str, is_combo, is_dynamic)"""
    defs = {}
    inp = node_def.get("input", {})
    for gname in ("required", "optional"):
        for k, v in inp.get(gname, {}).items():
            t = "UNKNOWN"
            dyn = False
            combo = False
            if isinstance(v, list) and v:
                if isinstance(v[0], str):
                    if v[0] == "COMFY_AUTOGROW_V3" or v[0].startswith("COMFY_AUTOGROW"):
                        dyn = True
                        t = "IMAGE"
                    elif v[0] == "COMBO":
                        combo = True
                        t = "STRING"
                    else:
                        t = v[0]
            defs[k] = (t, combo, dyn)
    return defs

def build_ui_node(api_id, api_node, node_def, inputs_defs):
    """构建一个 UI 节点，返回 (node, input_slots)
    input_slots: [(ui_index, input_name, from_node, from_slot)] 或 None
    """
    api_inputs = api_node.get("inputs", {})
    ui_inputs = []
    ui_outputs = []
    widgets = []
    slots = []  # (ui_index, name, from_node, from_slot)

    # 静态输入（不含 . 前缀）
    for name, val in api_inputs.items():
        if "." in name:
            continue
        t, combo, dyn = inputs_defs.get(name, ("UNKNOWN", False, False))
        link, link_info = is_link_val(val)
        entry = {"name": name, "type": t if not combo else "STRING"}
        if combo:
            entry["widget"] = {"name": name}
        if link:
            entry["link"] = None
            slots.append((len(ui_inputs), name, link_info[0], link_info[1]))
        else:
            entry["link"] = None
            if not combo:
                widgets.append(val)
            else:
                widgets.append(val)
        ui_inputs.append(entry)

    # 动态键（ref_images.ref_image_0 等）
    dyn_groups = {}
    for name, val in api_inputs.items():
        if "." in name:
            prefix = name.split(".")[0]
            dyn_groups.setdefault(prefix, []).append((name, val))
    for prefix, items in sorted(dyn_groups.items()):
        for name, val in items:
            t = "IMAGE"
            link, link_info = is_link_val(val)
            entry = {"name": name, "type": t}
            if link:
                entry["link"] = None
                slots.append((len(ui_inputs), name, link_info[0], link_info[1]))
            else:
                entry["link"] = None
                widgets.append(val)
            ui_inputs.append(entry)

    # 输出槽位
    outs = node_def.get("output", [])
    out_names = node_def.get("output_name", [])
    for i, t in enumerate(outs):
        nm = out_names[i] if i < len(out_names) else f"output_{i}"
        ui_outputs.append({"name": nm, "type": t if isinstance(t, str) else "UNKNOWN", "links": None})

    node = {
        "id": int(api_id),
        "type": api_node["class_type"],
        "pos": [0, 0],
        "size": [300, 100],
        "flags": {},
        "order": 0,
        "mode": 0,
        "inputs": ui_inputs,
        "outputs": ui_outputs,
        "properties": {"Node name for S&R": api_node["class_type"]},
        "widgets_values": widgets if widgets else None,
    }
    return node, slots

def convert(api_json, comfy=COMFY):
    global COMFY
    COMFY = comfy
    prompt = api_json["prompt"] if "prompt" in api_json else api_json
    ids = list(prompt.keys())

    # 第一遍：构建所有节点，记录 input 槽位映射
    nodes = []
    slots_map = {}  # api_id -> [(ui_index, in_name, from_api, from_slot)]
    id_set = set(ids)
    for api_id in ids:
        api_node = prompt[api_id]
        node_def = get_node_def(api_node["class_type"])
        inputs_defs = collect_input_defs(node_def)
        node, slots = build_ui_node(api_id, api_node, node_def, inputs_defs)
        nodes.append(node)
        slots_map[api_id] = slots

    # 网格布局（拓扑粗排：被依赖的节点放前面）
    order = {}
    visited = set()
    def visit(api_id):
        if api_id in visited:
            return
        visited.add(api_id)
        for _, _, from_api, _ in slots_map.get(api_id, []):
            if from_api in id_set:
                visit(from_api)
        order[api_id] = len(order)
    for api_id in ids:
        visit(api_id)

    # 根据 order 分配位置
    nx, ny = 0, 0
    for api_id in sorted(order, key=order.get):
        node = next(n for n in nodes if n["id"] == int(api_id))
        node["pos"] = [nx, ny]
        node["order"] = order[api_id]
        nx += 340
        if nx > 1500:
            nx = 0
            ny += 240

    # 第二遍：生成 links
    links = []
    link_id = 1
    # 建立 node_id -> node 索引
    node_by_id = {n["id"]: n for n in nodes}
    # 建立 (node_id, in_name) -> ui_input_index
    input_idx = {}
    for n in nodes:
        for i, inp in enumerate(n["inputs"]):
            input_idx[(n["id"], inp["name"])] = i
    # 建立 (node_id, out_slot) -> 输出类型
    out_type = {}
    for n in nodes:
        for i, o in enumerate(n["outputs"]):
            out_type[(n["id"], i)] = o["type"]

    for api_id in ids:
        ui_src = int(api_id)  # 目标节点（输入方）
        for ui_in_idx, in_name, from_api, from_slot in slots_map.get(api_id, []):
            if from_api not in id_set:
                continue
            ui_dst = int(from_api)  # 源节点（输出方）
            ltype = out_type.get((ui_dst, from_slot), "IMAGE")
            links.append([link_id, ui_dst, from_slot, ui_src, ui_in_idx, ltype])
            # 回填
            node_by_id[ui_src]["inputs"][ui_in_idx]["link"] = link_id
            if node_by_id[ui_dst]["outputs"][from_slot]["links"] is None:
                node_by_id[ui_dst]["outputs"][from_slot]["links"] = []
            node_by_id[ui_dst]["outputs"][from_slot]["links"].append(link_id)
            link_id += 1

    return {
        "id": None,
        "revision": 0,
        "last_node_id": max(int(i) for i in ids),
        "last_link_id": link_id - 1,
        "nodes": nodes,
        "links": links,
        "groups": [],
        "config": {},
        "extra": {},
        "version": 0.4,
    }

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    ap.add_argument("--comfy", default="http://100.67.139.74:8188")
    args = ap.parse_args()
    with open(args.input, encoding="utf-8") as f:
        api = json.load(f)
    ui = convert(api, args.comfy)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(ui, f, ensure_ascii=False, indent=1)
    print(f"OK: {len(ui['nodes'])} 节点, {len(ui['links'])} 连线 -> {args.output}")
