#!/usr/bin/env python3
"""Convert a ComfyUI UI-graph workflow (.json with nodes/links) to API format
for submission via /prompt.

Handles:
- link-type inputs (MODEL/CLIP/VAE/IMAGE/...): wired from links[]
- widget inputs (STRING/INT/FLOAT/COMBO/...): taken from widgets_values
- COMFY_AUTOGROW_V3 (ref_images / values): collected as a LIST of link refs
- widget inputs that are ALSO connected (prompt/width/height/length): link wins,
  but widgets_values slot is still consumed to keep alignment
"""
import json, os, re, sys

# Data-link types (NOT widget types). STRING/INT/FLOAT/BOOLEAN/COMBO are widgets.
LINK_TYPES = {
    "MODEL", "CLIP", "VAE", "LATENT", "CONDITIONING", "IMAGE", "AUDIO", "MASK",
    "NOISE", "GUIDER", "SAMPLER", "SIGMAS", "CONTROL_NET", "GLIGEN",
    "UPSCALE_MODEL", "VIDEO", "DEPROC", "IP2P", "STYLE_MODEL", "TIMESTEP_KEYFRAME",
    "BBOX_DETECTOR", "SEGMENTATION",
}

def load_objinfo(path):
    info = {}
    if os.path.isdir(path):
        for fn in os.listdir(path):
            if fn.endswith(".json"):
                info.update(json.load(open(os.path.join(path, fn), encoding="utf-8")))
    else:
        info.update(json.load(open(path, encoding="utf-8")))
    return info

def is_link_type(typ):
    if typ == "COMFY_AUTOGROW_V3":
        return False  # handled separately
    return typ in LINK_TYPES

def convert(ui, objinfo):
    nodes = {n["id"]: n for n in ui["nodes"]}
    links = {l[0]: (l[1], l[2]) for l in ui["links"]}
    prompt = {}
    for n in ui["nodes"]:
        nid = str(n["id"])
        ct = n["type"]
        if ct == "MarkdownNote":
            continue
        defn = objinfo.get(ct, {})
        inp = defn.get("input", {})
        req = inp.get("required", {})
        opt = inp.get("optional", {})
        order = defn.get("input_order", {})
        req_order = order.get("required", list(req.keys()))
        opt_order = order.get("optional", list(opt.keys()))
        all_names = req_order + opt_order
        wv = n.get("widgets_values") or []
        ui_inputs = {i.get("name"): i for i in (n.get("inputs") or [])}

        inputs = {}
        # pass 1: assign widget values by position (consume wv for every widget input)
        wi = 0
        for name in all_names:
            spec = req.get(name) or opt.get(name)
            if not isinstance(spec, list):
                continue
            typ = spec[0]
            if isinstance(typ, list):
                typ = typ[0]
            if typ == "COMFY_AUTOGROW_V3":
                continue  # not a widget; handle below
            if is_link_type(typ):
                continue  # link type, no widget value
            if wi < len(wv):
                inputs[name] = wv[wi]
            wi += 1

        # pass 2: autogrow -> each connected sub-input becomes its own input key (full name)
        for name in all_names:
            spec = req.get(name) or opt.get(name)
            if not isinstance(spec, list):
                continue
            typ = spec[0]
            if isinstance(typ, list):
                typ = typ[0]
            if typ != "COMFY_AUTOGROW_V3":
                continue
            for k in ui_inputs:
                if k.startswith(name + "."):
                    link = ui_inputs[k].get("link")
                    if link is not None and link in links:
                        oid, oslot = links[link]
                        inputs[k] = [str(oid), oslot]

        # pass 3: override connected inputs with link references
        for name in all_names:
            spec = req.get(name) or opt.get(name)
            if not isinstance(spec, list):
                continue
            typ = spec[0]
            if isinstance(typ, list):
                typ = typ[0]
            if typ == "COMFY_AUTOGROW_V3":
                continue
            ui_in = ui_inputs.get(name)
            if ui_in and ui_in.get("link") is not None and ui_in["link"] in links:
                oid, oslot = links[ui_in["link"]]
                inputs[name] = [str(oid), oslot]

        prompt[nid] = {"class_type": ct, "inputs": inputs}
    return {"prompt": prompt}

def main():
    ui_path = sys.argv[1]
    out_path = sys.argv[2]
    objinfo_path = sys.argv[3] if len(sys.argv) > 3 else None
    ui = json.load(open(ui_path, encoding="utf-8"))
    objinfo = load_objinfo(objinfo_path) if objinfo_path else {}
    api = convert(ui, objinfo)
    json.dump(api, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print(f"converted -> {out_path}  ({len(api['prompt'])} nodes)")

if __name__ == "__main__":
    main()
