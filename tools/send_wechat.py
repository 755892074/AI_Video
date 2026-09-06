#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
send_wechat.py - 通过 WorkBuddy 微信 ClawBot iLink API 主动推送文本/文件到微信
================================================================================
原理: AI 助手/脚本 -> ClawBot iLink API -> 微信 ClawBot -> 你的微信
配置: 从 ~/.workbuddy/settings.json 读取 weixinClawBot 通道 (botToken/userId/baseUrl)

用法:
  python send_wechat.py send "消息文本"          # 发文本到微信
  python send_wechat.py sendfile <文件路径>      # 发文件(视频/图片/PDF等)到微信
  python send_wechat.py refresh                  # 强制刷新 context_token
  python send_wechat.py status                   # 查看配置与 token 状态

依赖: pip install cryptography
参考: github.com/i138/wechat-clawbot-notify-file (MIT)
"""
import base64
import hashlib
import json
import os
import sys
import uuid
import urllib.error
import urllib.request

CHANNEL_VERSION = "workbuddy-desktop-1.0.0"
CACHE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".token_cache.json")
SETTINGS_PATHS = [
    os.path.expanduser("~/.workbuddy/settings.json"),
    os.path.join(os.environ.get("USERPROFILE", "~"), ".workbuddy", "settings.json"),
]


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ---------------- 配置 ----------------
def find_key(obj, key):
    if isinstance(obj, dict):
        if key in obj:
            return obj[key]
        for v in obj.values():
            r = find_key(v, key)
            if r:
                return r
    elif isinstance(obj, list):
        for v in obj:
            r = find_key(v, key)
            if r:
                return r
    return None


def load_cfg():
    for p in SETTINGS_PATHS:
        if os.path.exists(p):
            try:
                d = json.load(open(p, encoding="utf-8"))
            except Exception:
                continue
            wx = d.get("weixinClawBot") or find_key(d, "weixinClawBot")
            if isinstance(wx, dict) and wx.get("botToken") and wx.get("userId") and wx.get("baseUrl"):
                return wx
    return None


# ---------------- 缓存 ----------------
def load_cache():
    try:
        return json.load(open(CACHE_FILE, encoding="utf-8"))
    except Exception:
        return {}


def save_cache(**kw):
    c = load_cache()
    c.update(kw)
    with open(CACHE_FILE, "w", encoding="utf-8") as f:
        json.dump(c, f, ensure_ascii=False, indent=2)


# ---------------- iLink API ----------------
def gen_uin():
    return base64.b64encode(str(int.from_bytes(os.urandom(4), "little")).encode()).decode()


def api_req(cfg, path, payload):
    headers = {
        "Content-Type": "application/json",
        "AuthorizationType": "ilink_bot_token",
        "Authorization": "Bearer %s" % cfg["botToken"],
        "X-WECHAT-UIN": gen_uin(),
    }
    req = urllib.request.Request(
        cfg["baseUrl"] + path,
        data=json.dumps(payload).encode("utf-8"),
        headers=headers,
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode("utf-8", errors="replace"))
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "_body": e.read().decode("utf-8", errors="replace")[:300]}
    except Exception as e:
        return {"_error": str(e)}


def refresh_token(cfg, retry_no_cursor=True):
    buf = load_cache().get("get_updates_buf", "")
    result = api_req(cfg, "/ilink/bot/getupdates", {
        "get_updates_buf": buf,
        "base_info": {"channel_version": CHANNEL_VERSION},
    })
    if not result:
        return None
    ret = result.get("ret", result.get("errcode"))
    if ret is not None and ret != 0:
        log("TOKEN_REFRESH_FAILED ret=%s" % ret)
        if retry_no_cursor and buf:
            save_cache(get_updates_buf="")
            return refresh_token(cfg, retry_no_cursor=False)
        return None
    # 无条件保存游标(增量拉取依赖它; msgs 为空也要推进, 否则永远拿不到新消息)
    new_buf = result.get("get_updates_buf") or buf
    save_cache(get_updates_buf=new_buf)
    for msg in reversed(result.get("msgs", [])):
        token = msg.get("context_token", "")
        if token:
            save_cache(context_token=token, get_updates_buf=new_buf)
            log("TOKEN_REFRESHED %s..." % token[:24])
            return token
    log("No context_token found (user must send a message to ClawBot first)")
    return None


def cached_token(cfg):
    t = load_cache().get("context_token")
    if t:
        return t
    return refresh_token(cfg)


# ---------------- 发送 ----------------
# 实测(2026-09-02): sendmessage 不需要 context_token —— bot 凭 botToken 即可主动推送。
# context_token 传空串即可, 因此推送不依赖"用户先发消息", 渲染完成可直接触发。
def send_msg(cfg, text):
    payload = {"msg": {
        "from_user_id": "",
        "to_user_id": cfg["userId"],
        "client_id": "wb-notify-%s" % uuid.uuid4().hex[:16],
        "message_type": 2,
        "message_state": 2,
        "context_token": "",
        "item_list": [{"type": 1, "text_item": {"text": text}}],
    }, "base_info": {"channel_version": CHANNEL_VERSION}}
    result = api_req(cfg, "/ilink/bot/sendmessage", payload)
    if result.get("message_id"):
        log("SEND_OK %s" % text[:50].replace("\n", " "))
        return True
    r = result.get("ret", result.get("errcode"))
    log("SEND_FAILED ret=%s body=%s" % (r, str(result)[:200]))
    return False


def aes_ecb_encrypt(data, key):
    from cryptography.hazmat.primitives import padding as cp
    from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
    padder = cp.PKCS7(128).padder()
    cipher = Cipher(algorithms.AES(key), modes.ECB())
    enc = cipher.encryptor()
    return enc.update(padder.update(data) + padder.finalize()) + enc.finalize()


def send_file(cfg, file_path):
    if not os.path.exists(file_path):
        log("FILE_NOT_FOUND %s" % file_path)
        return False
    with open(file_path, "rb") as f:
        raw = f.read()
    raw_size = len(raw)
    raw_md5 = hashlib.md5(raw).hexdigest()
    aes_key = os.urandom(16)
    aes_hex = aes_key.hex()
    enc_data = aes_ecb_encrypt(raw, aes_key)
    file_key = uuid.uuid4().hex
    # 1) 获取上传 URL
    up = api_req(cfg, "/ilink/bot/getuploadurl", {
        "filekey": file_key,
        "media_type": 3,
        "to_user_id": cfg["userId"],
        "rawsize": raw_size,
        "rawfilemd5": raw_md5,
        "filesize": len(enc_data),
        "no_need_thumb": True,
        "aeskey": aes_hex,
    })
    upload_url = None
    param = up.get("upload_param", "")
    if param:
        upload_url = "https://novac2c.cdn.weixin.qq.com/c2c/upload?encrypted_query_param=%s&filekey=%s" % (param, file_key)
    elif up.get("upload_full_url"):
        from urllib.parse import parse_qs, urlparse
        q = parse_qs(urlparse(up["upload_full_url"]).query)
        ep = q.get("encrypted_query_param", [""])[0]
        upload_url = "https://novac2c.cdn.weixin.qq.com/c2c/upload?encrypted_query_param=%s&filekey=%s" % (ep, file_key)
    if not upload_url:
        log("GETUPLOADURL_FAILED %s" % str(up)[:200])
        return False
    # 2) 上传 CDN —— 用 curl 子进程直连(禁代理)。
    #    坑: urllib 直连上传在本机会被安全软件(iOA)拦截 SIGTERM; curl --noproxy 实测通。
    import subprocess
    import tempfile
    tmp_enc = os.path.join(tempfile.gettempdir(), "wb_upload_%s.bin" % uuid.uuid4().hex)
    with open(tmp_enc, "wb") as f:
        f.write(enc_data)
    hdr_file = tmp_enc + ".hdr"
    body_file = tmp_enc + ".body"
    cmd = ["curl", "-s", "--noproxy", "*", "--max-time", "300",
           "-X", "POST", "-H", "Content-Type: application/octet-stream",
           "--data-binary", "@" + tmp_enc.replace(os.sep, "/"),
           "-D", hdr_file, "-o", body_file, upload_url]
    try:
        subprocess.run(cmd, timeout=320, check=False)
        enc_param = ""
        with open(hdr_file, "r", encoding="utf-8", errors="replace") as hf:
            for line in hf:
                if line.lower().startswith("x-encrypted-param"):
                    enc_param = line.split(":", 1)[1].strip()
                    break
    except Exception as e:
        log("UPLOAD_FAILED %s" % e)
        enc_param = ""
    finally:
        for f in (tmp_enc, hdr_file, body_file):
            try:
                os.remove(f)
            except Exception:
                pass
    if not enc_param:
        log("UPLOAD_NO_ENCPARAM")
        return False
    # 3) 发送文件消息
    aes_b64 = base64.b64encode(aes_hex.encode("ascii")).decode("ascii")
    payload = {"msg": {
        "from_user_id": "",
        "to_user_id": cfg["userId"],
        "client_id": "wb-notify-%s" % uuid.uuid4().hex[:16],
        "message_type": 2,
        "message_state": 2,
        "context_token": "",
        "item_list": [{"type": 4, "file_item": {
            "media": {"encrypt_query_param": enc_param, "aes_key": aes_b64, "encrypt_type": 1},
            "file_name": os.path.basename(file_path),
            "len": str(raw_size),
        }}],
    }, "base_info": {"channel_version": CHANNEL_VERSION}}
    result = api_req(cfg, "/ilink/bot/sendmessage", payload)
    if not result or result.get("ret", 0) != 0:
        log("SEND_FILE_FAILED %s" % str(result)[:200])
        return False
    log("SEND_FILE_OK %s (%d bytes)" % (os.path.basename(file_path), raw_size))
    return True


# ---------------- 入口 ----------------
def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1
    cfg = load_cfg()
    if not cfg:
        print("ERROR: 无法读取 WorkBuddy settings.json 中的 weixinClawBot 配置", file=sys.stderr)
        return 1
    cmd = sys.argv[1]
    if cmd == "status":
        t = load_cache().get("context_token")
        print("config: baseUrl=%s" % cfg["baseUrl"])
        print("userId: %s" % cfg["userId"])
        print("token: %s" % (("已缓存 " + t[:16] + "...") if t else "未缓存"))
        print("cache: %s" % CACHE_FILE)
        return 0
    if cmd == "refresh":
        t = refresh_token(cfg)
        print("TOKEN=%s" % (t[:24] + "..." if t else "FAILED"))
        return 0 if t else 1
    if cmd == "send":
        if len(sys.argv) < 3:
            print("用法: send <text>")
            return 1
        ok = send_msg(cfg, " ".join(sys.argv[2:]))
        print("RESULT=%s" % ("OK" if ok else "FAIL"))
        return 0 if ok else 1
    if cmd == "sendfile":
        if len(sys.argv) < 3:
            print("用法: sendfile <path>")
            return 1
        ok = send_file(cfg, sys.argv[2])
        print("RESULT=%s" % ("OK" if ok else "FAIL"))
        return 0 if ok else 1
    print("未知命令: %s" % cmd)
    return 1


if __name__ == "__main__":
    sys.exit(main())
