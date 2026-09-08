"""Director3D v1: 录制 10s walkscene + 角色真走 + 相机跟拍 + 物体环绕 + 配角
用 playwright page.video_path 录屏，swiftshader 软渲染（headless 必要）
- http server 在本进程子线程跑（避免被沙箱杀）
"""
import time, threading, http.server, socketserver, functools, os
from pathlib import Path
from playwright.sync_api import sync_playwright

EDGE = r"C:/Program Files (x86)/Microsoft/Edge/Application/msedge.exe"
DOCS = Path(r"D:/WorkBuddy/AI_Video/tools/director3d").resolve()
OUT = DOCS
VIDEO = OUT / "_video_record"
PORT = 8210

DURATION = 12  # 秒：2s 预热 + 10s 动画


def start_server():
    os.chdir(str(DOCS))
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(DOCS))
    httpd = socketserver.TCPServer(("127.0.0.1", PORT), handler)
    httpd.daemon_threads = True
    t = threading.Thread(target=httpd.serve_forever, daemon=True)
    t.start()
    print(f"[S] http server up on 127.0.0.1:{PORT}")
    return httpd


def main():
    VIDEO.mkdir(exist_ok=True)
    for f in VIDEO.glob("*.webm"): f.unlink()

    httpd = start_server()
    time.sleep(0.5)

    with sync_playwright() as pw:
        b = pw.chromium.launch(executable_path=EDGE, headless=False,
            args=["--use-angle=swiftshader","--enable-unsafe-swiftshader","--no-sandbox",
                  "--ignore-gpu-blocklist","--enable-webgl","--window-size=1280,720"])
        ctx = b.new_context(
            viewport={"width": 1280, "height": 720},
            record_video_dir=str(VIDEO),
            record_video_size={"width": 1280, "height": 720},
        )
        p = ctx.new_page()
        p.on("console", lambda msg: print(f"[CONSOLE.{msg.type}] {msg.text}"))
        p.on("pageerror", lambda err: print(f"[PAGEERROR] {err}"))
        p.on("requestfailed", lambda req: print(f"[REQFAIL] {req.url} - {req.failure}"))
        url = f"http://127.0.0.1:{PORT}/index.html"
        print(f"[G] goto {url}")
        p.goto(url, wait_until="load", timeout=30000)
        time.sleep(2)  # 等 three.js 加载 + 动画开跑
        # 探针：检查 three 是否加载
        probe = p.evaluate("""() => ({
            hasThree: typeof window.THREE !== 'undefined',
            bodyReady: document.body.dataset.ready || null,
            canvasSize: [document.getElementById('c')?.width, document.getElementById('c')?.height],
        })""")
        print(f"[PROBE] {probe}")
        print(f"[W] 等动画完成 (≤{DURATION}s)...")
        try:
            p.wait_for_selector("body[data-ready='1']", timeout=(DURATION+5)*1000)
            print("[OK] 动画 ready")
        except Exception as e:
            print(f"[W] 超时未 ready: {e}")
        time.sleep(0.5)
        vp = p.video.path() if p.video else None
        print(f"[V] 录像路径: {vp}")
        ctx.close(); b.close()
    httpd.shutdown()
    return vp


if __name__ == "__main__":
    p = main()
    if p and Path(p).exists():
        size = Path(p).stat().st_size
        print(f"[DONE] {p}  {size/1024:.1f} KB")
    else:
        print("[DONE] 无录像")
