#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
comfy_monitor.py — 台式机 ComfyUI 任务监控三件套

解决"指令失效报错但不知道"的问题：
  1. health_check()      提交前确认 ComfyUI 在线（GET /system_stats）
  2. submit_with_verify() 提交后确认任务真的进了队列（GET /queue）
  3. ws_watch()          WebSocket 实时监听执行事件（开始/成功/失败/中断），
                         任何异常立刻触发 on_error 回调

配合 batch_r2v.py 使用：失败时立即退出(非零码)，让后台任务快速失败，
WorkBuddy 就能通过任务通知及时收到结果，而不是干等轮询超时。

依赖: pip install websocket-client
"""
import json, time, urllib.request, socket

COMFY = "http://100.67.139.74:8188"
WS = "ws://100.67.139.74:8188/ws"
TIMEOUT = 30

def http_get(url, timeout=TIMEOUT):
    with urllib.request.urlopen(url, timeout=timeout) as r:
        return r.read().decode()

def health_check(comfy=COMFY, timeout=8):
    """提交前健康检查：确认 ComfyUI 在线 + 返回系统信息。失败抛异常。"""
    try:
        stats = json.loads(http_get(f"{comfy}/system_stats", timeout))
        dev = stats.get("devices", [{}])[0]
        name = dev.get("name", "?")
        vram = dev.get("vram_total", 0) / (1024 ** 3)
        return {"online": True, "gpu": name, "vram_gb": round(vram, 1)}
    except Exception as e:
        raise RuntimeError(f"ComfyUI 健康检查失败: {e}")

def submit_with_verify(prompt_graph, client_id, comfy=COMFY, retries=3):
    """提交任务并确认进入队列。
    返回 prompt_id；若提交后 5 秒内队列里没有它，抛异常（可能没被执行）。"""
    payload = json.dumps({"prompt": prompt_graph, "client_id": client_id}).encode()
    req = urllib.request.Request(f"{comfy}/prompt", data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    pid = None
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                pid = json.loads(r.read().decode()).get("prompt_id")
            break
        except urllib.error.HTTPError as e:
            body = e.read().decode()[:400]
            if attempt == retries - 1:
                raise RuntimeError(f"提交失败(HTTP {e.code}): {body}")
            time.sleep(2)
    if not pid:
        raise RuntimeError("提交后未返回 prompt_id")
    # 验证进入队列
    for _ in range(6):  # 5s 内确认
        try:
            q = json.loads(http_get(f"{comfy}/queue", timeout=10))
            in_q = pid in [x[1] for x in q.get("queue_running", [])] or \
                   pid in [x[1] for x in q.get("queue_pending", [])]
            if in_q:
                return pid
        except Exception:
            pass
        time.sleep(1)
    raise RuntimeError(f"提交后 {pid} 未出现在队列中（可能没被执行）")

def ws_watch(client_id, on_event=None, on_error=None, timeout_sec=3600, ws_url=None):
    """WebSocket 实时监听任务事件。
    on_event(evt_type, data): 每次事件回调（execution_start/executing/progress/executed/...）
    on_error(msg): 出错时回调（execution_error / execution_interrupted / 连接异常）
    返回: None 正常结束, 或错误信息字符串。
    """
    import websocket
    url = ws_url or WS
    try:
        ws = websocket.create_connection(url + f"?clientId={client_id}", timeout=15)
        ws.send("{}")
    except Exception as e:
        if on_error:
            on_error(f"WS连接失败: {e}")
        return f"WS连接失败: {e}"

    deadline = time.time() + timeout_sec
    try:
        while time.time() < deadline:
            ws.settimeout(15)
            try:
                raw = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            except Exception as e:
                if on_error:
                    on_error(f"WS接收异常: {e}")
                return f"WS接收异常: {e}"
            if not raw:
                continue
            try:
                msg = json.loads(raw)
            except Exception:
                continue
            mtype = msg.get("type")
            data = msg.get("data", {})
            if mtype in ("execution_start", "executing", "progress",
                         "executed", "execution_success", "execution_cached",
                         "execution_interrupted", "execution_error"):
                if on_event:
                    on_event(mtype, data)
                if mtype in ("execution_interrupted", "execution_error"):
                    err = f"任务被中断/报错: {mtype} {json.dumps(data, ensure_ascii=False)[:300]}"
                    if on_error:
                        on_error(err)
                    return err
                if mtype == "execution_success":
                    return None  # 正常完成
    except Exception as e:
        if on_error:
            on_error(f"WS监听异常: {e}")
        return f"WS监听异常: {e}"
    return "WS监听超时"

if __name__ == "__main__":
    import sys
    print("=== 健康检查 ===")
    try:
        info = health_check()
        print(f"  ComfyUI 在线: GPU={info['gpu']}, VRAM={info['vram_gb']}GB")
    except Exception as e:
        print(f"  [FAIL] {e}")
        sys.exit(1)
    print("=== 队列状态 ===")
    try:
        q = json.loads(http_get(f"{COMFY}/queue", timeout=10))
        run = len(q.get("queue_running", []))
        pend = len(q.get("queue_pending", []))
        print(f"  运行中: {run}, 排队: {pend}")
        if run == 0 and pend == 0:
            print("  队列空闲")
    except Exception as e:
        print(f"  [FAIL] {e}")
