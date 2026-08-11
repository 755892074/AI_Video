#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
PhotoMaker 身份注入：用真实照片生成"巫师版角色表"。
  输入：真实小孩照片(harry_original.jpg)
  输出：巫师造型角色表（脸=照片本人，衣服=格兰芬多长袍+眼镜）
  前提：台式机已安装 SDXL Base checkpoint + PhotoMaker 模型
"""
import json, os, sys, time, uuid, urllib.request, urllib.error

COMFY = "http://100.67.139.74:8188"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def http_post(url, data, headers=None):
    req = urllib.request.Request(url, data=data, method="POST")
    if headers:
        for k,v in headers.items(): req.add_header(k,v)
    with urllib.request.urlopen(req, timeout=180) as r:
        return r.read().decode()

def upload_image(abs_path, name):
    ext = os.path.splitext(abs_path)[1].lower() or ".png"
    with open(abs_path,"rb") as f: data=f.read()
    b="----wb"
    body=(f"--{b}\r\nContent-Disposition: form-data; name=\"image\"; filename=\"{name}{ext}\"\r\n"
          f"Content-Type: image/{ext[1:]}\r\n\r\n").encode()+data+f"\r\n--{b}--\r\n".encode()
    r=http_post(f"{COMFY}/upload/image",body,{"Content-Type":f"multipart/form-data; boundary={b}"})
    return json.loads(r)["name"]

def main():
    # ---- 配置 ----
    ckpt_name = "sd_xl_base_1.0.safetensors"   # SDXL Base（用户需先装）
    pm_name   = "photomaker-v1.bin"              # PhotoMaker（用户需先装）
    photo_rel = "hp/assets/characters/harry_original.jpg"
    out_dir   = os.path.join(ROOT,"shots","hp","assets","characters")
    os.makedirs(out_dir, exist_ok=True)

    # 多个角度/姿势的提示词
    prompts = [
        ("front",  "character reference sheet, front view of a young East Asian boy wearing round glasses and a dark blue Gryffindor robe with red lining and crest, white shirt and striped tie underneath, warm magical lighting, detailed face, photorealistic, white background"),
        ("side",   "character reference sheet, left side profile view of a young East Asian boy with round glasses in a dark blue Gryffindor robe with red lining, holding a magic wand, warm lighting, photorealistic, white background"),
        ("back",   "character reference sheet, back view of a young boy in a dark blue Gryffindor robe with red lining, round glasses visible from behind, wand tucked into belt, photorealistic, white background"),
        ("full",   "full body shot of a young East Asian boy in complete Gryffindor uniform with round glasses, dark blue robe with red lining and house crest, white shirt, striped tie, black trousers, black shoes, standing pose, confident smile, warm studio lighting, photorealistic, plain background"),
    ]

    photo_abs = os.path.join(ROOT, "shots", photo_rel)
    print(f"uploading photo: {photo_abs}")
    img_name = upload_image(photo_abs, "pm_harry")

    client_id = uuid.uuid4().hex
    for angle, prompt_text in prompts:
        print(f"\n--- generating {angle} ---")
        # 构建 PhotoMaker 工作流
        wf = {
            "1": {"class_type":"CheckpointLoaderSimple",
                 "inputs":{"ckpt_name":ckpt_name}},
            "2": {"class_type":"PhotoMakerLoader",
                 "inputs":{"photomaker_model_name":pm_name}},
            "3": {"class_type":"LoadImage",
                 "inputs":{"image":img_name}},
            "4": {"class_type":"PhotoMakerEncode",
                 "inputs":{
                     "photomaker":["2",0],
                     "image":["3",0],
                     "clip":["1",1],
                     "text":prompt_text,
                 }},
            "5": {"class_type":"CLIPTextEncode",
                 "inputs":{
                     "text":prompt_text,
                     "clip":["1",1],
                 }},
            "6": {"class_type":"KSamplerSelect",
                 "inputs":{"sampler_name":"euler_ancestral"}},
            "7": {"class_type":"BasicScheduler",
                 "inputs":{
                     "scheduler":"normal",
                     "steps":30,
                     "denoise":0.75,
                     "model":["1",0],
                 }},
            "8": {"class_type":"BasicGuider",
                 "inputs":{
                     "mode":"fixed",
                     "guidance_scale":7.5,
                     "model":["1",0],
                 }},
            "9": {"class_type":"RandomNoise",
                 "inputs":{"seed":int(time.time()*1000)%2**32}},
            "10":{"class_type":"SamplerCustomAdvanced",
                 "inputs":{
                     "noise":["9",0],
                     "guider":["8",0],
                     "sampler":["6",0],
                     "sigmas":["7",0],
                     "latent_image":["4",0],  # PhotoMakerEncode outputs latent
                 }},
            "11":{"class_type":"VAEDecode",
                  "inputs":{"samples":["10",0],"vae":["1",2]}},
            "12":{"class_type":"SaveImage",
                  "inputs":{"images":["11",0],
                            "filename_prefix":f"pm_wizard_{angle}"}},
        }

        payload = json.dumps({"prompt":wf,"client_id":client_id}).encode()
        try:
            r = http_post(f"{COMFY}/prompt",payload,{"Content-Type":"application/json"})
            pid = json.loads(r).get("prompt_id")
            print(f"  submitted pid={pid}")
        except urllib.error.HTTPError as e:
            err = e.read().decode()[:500]
            print(f"  SUBMIT FAIL: {err}")
            if "checkpoint" in err.lower() or "not found" in err.lower():
                print("  ⚠️  模型未找到！请确认已安装:")
                print(f"     - SDXL: checkpoints/{ckpt_name}")
                print(f"     - PhotoMaker: photomaker/{pm_name}")
            continue

        # 轮询等待
        for _ in range(360):
            try:
                h=json.load(urllib.request.urlopen(f"{COMFY}/history/{pid}",timeout=30))
            except: h={}
            if pid not in h: time.sleep(5); continue
            st=h[pid].get("status",{})
            if st.get("status_str")=="error":
                print(f"  ERROR: {json.dumps(h[pid].get('messages',[]),ensure_ascii=False)[:300]}"); break
            outs=h[pid].get("outputs",{})
            if any(isinstance(o,dict) and o.get("images") for o in outs.values()):
                print(f"  done! angle={angle}")
                break
            time.sleep(5)

    print("\n全部完成！查看输出:", out_dir)

if __name__ == "__main__":
    main()
