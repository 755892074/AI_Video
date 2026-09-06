# -*- coding: utf-8 -*-
"""batch 吞吐对比测试：batch=1/2/4 同 prompt 各跑一轮，输出每张平均耗时"""
import subprocess, time, sys, os

PY = r"C:/Users/Administrator/.workbuddy/binaries/python/versions/3.13.12/python.exe"
TOOL = r"D:/WorkBuddy/AI_Video/tools/qwen_t2i.py"
OUT = r"D:/WorkBuddy/AI_Video/scripts/she_is_still_here/style_test/_batchtest"
os.makedirs(OUT, exist_ok=True)

PROMPT = ("Photorealistic cinematic 3D CG render, cold desaturated teal night grade. "
          "Interior of a dim private hospital ICU room at night, rain on window. "
          "A tired Chinese man in his thirties in a dark jacket sits at a bedside holding the hand "
          "of an unconscious young woman with long black hair lying in bed. Vertical 9:16 composition.")
NEG = "text, watermark, logo, lowres, blurry, deformed, bad anatomy, extra fingers, cartoon, anime, oversaturated"

for batch in [1, 2, 4]:
    seed = 12345  # 固定 seed 公平对比
    t0 = time.time()
    cmd = [PY, TOOL, "--prompt", PROMPT, "--negative", NEG,
           "--width", "576", "--height", "1024", "--steps", "20", "--cfg", "4",
           "--seed", str(seed), "--batch", str(batch),
           "--prefix", f"bch_{batch}", "--out", OUT]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=900)
    dt = time.time() - t0
    ok = "rc=0" if r.returncode == 0 else f"rc={r.returncode} err={r.stderr[-300:]}"
    per = dt / batch
    print(f"batch={batch}: 总耗时 {dt:.0f}s | 每张均摊 {per:.0f}s | {ok}", flush=True)
print("DONE")
