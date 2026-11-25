#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""cdp.py — 零依赖 CDP 小工具（走本机 127.0.0.1:9222 已登录 Chrome）。

为什么存在：本机无 `ws` / `websocket-client`（实测 `require('ws')` 失败、`import websocket` 失败），
而本线又要复用同一 Chrome（头条/招聘共用 9222，🚫 不许 pkill）。故用 raw socket 自己实现最小 WebSocket 客户端。

用法：
  python3 cdp.py list [urlSubstr]                     # 列页（默认全部）；打印 targetId
  python3 cdp.py open <url>                           # 新开标签 → 打印 targetId（/json/new，绕 window.open 拦截）
  python3 cdp.py close <targetId>                     # 关标签
  python3 cdp.py eval <targetId> <jsFile>             # 在指定页执行 JS 文件（返回 byValue）
  python3 cdp.py goto <targetId> <url>                # 导航并等 load
  python3 cdp.py shot <targetId> <outPng>             # 截图（存证）
  python3 cdp.py upload <targetId> <selector> <file>  # 给 <input type=file> 塞文件
  python3 cdp.py scroll <targetId> [times]            # 滚到底触发懒加载

⚠️ 约定（本线踩过的坑）：操作已登录后台页面一律「按 targetId 精确操作」，不要按 URL 关键字猜页。
"""
import base64
import json
import os
import socket
import struct
import sys
import time
import urllib.parse
import urllib.request

CDP = "http://127.0.0.1:9222"


# ---------------------------------------------------------------- HTTP side
def _get(path, timeout=10, method="GET"):
    req = urllib.request.Request(CDP + path, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")


def pages():
    return [t for t in json.loads(_get("/json/list")) if t.get("type") == "page"]


def find(target_id):
    for t in json.loads(_get("/json/list")):
        if t.get("id") == target_id:
            return t
    raise SystemExit("no target " + target_id)


# ---------------------------------------------------------------- minimal WS client
class WS:
    def __init__(self, url, timeout=30):
        u = urllib.parse.urlparse(url)
        host, port = u.hostname, u.port or 80
        path = u.path + (("?" + u.query) if u.query else "")
        self.sock = socket.create_connection((host, port), timeout=timeout)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (
            "GET %s HTTP/1.1\r\nHost: %s:%d\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            "Sec-WebSocket-Key: %s\r\nSec-WebSocket-Version: 13\r\n\r\n" % (path, host, port, key)
        )
        self.sock.sendall(req.encode())
        buf = b""
        while b"\r\n\r\n" not in buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise RuntimeError("handshake closed")
            buf += chunk
        if b" 101 " not in buf.split(b"\r\n")[0]:
            raise RuntimeError("handshake failed: " + buf.split(b"\r\n")[0].decode("latin1"))
        self.buf = buf.split(b"\r\n\r\n", 1)[1]
        self._id = 0

    def _recv_exact(self, n):
        while len(self.buf) < n:
            chunk = self.sock.recv(65536)
            if not chunk:
                raise RuntimeError("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def _send_frame(self, payload, opcode=0x1):
        data = payload.encode() if isinstance(payload, str) else payload
        header = bytearray([0x80 | opcode])
        n = len(data)
        if n < 126:
            header.append(0x80 | n)
        elif n < 65536:
            header.append(0x80 | 126)
            header += struct.pack(">H", n)
        else:
            header.append(0x80 | 127)
            header += struct.pack(">Q", n)
        mask = os.urandom(4)
        header += mask
        masked = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        self.sock.sendall(bytes(header) + masked)

    def _recv_frame(self):
        b1, b2 = self._recv_exact(2)
        opcode = b1 & 0x0F
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack(">H", self._recv_exact(2))[0]
        elif n == 127:
            n = struct.unpack(">Q", self._recv_exact(8))[0]
        mask = self._recv_exact(4) if (b2 & 0x80) else None
        data = self._recv_exact(n)
        if mask:
            data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
        return opcode, data

    def call(self, method, params=None, timeout=60):
        self._id += 1
        mid = self._id
        self._send_frame(json.dumps({"id": mid, "method": method, "params": params or {}}))
        t0 = time.time()
        while time.time() - t0 < timeout:
            opcode, data = self._recv_frame()
            if opcode == 0x9:  # ping
                self._send_frame(data, opcode=0xA)
                continue
            if opcode != 0x1:
                continue
            msg = json.loads(data.decode("utf-8", "replace"))
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError("CDP error: " + json.dumps(msg["error"])[:400])
                return msg.get("result", {})
        raise TimeoutError("CDP timeout: " + method)

    def close(self):
        try:
            self._send_frame(b"", opcode=0x8)
        except Exception:
            pass
        try:
            self.sock.close()
        except Exception:
            pass

    def call_multi(self, method, params=None, timeout=60):
        """发一条命令，收帧直到「本 id 的应答」为止；期间收到的所有消息（含事件帧）原样返回列表。

        与 call() 的区别：不丢事件。断点/暂停期间调试器事件很多，调用方需自己挑出 id 应答。
        """
        self._id += 1
        mid = self._id
        self._send_frame(json.dumps({"id": mid, "method": method, "params": params or {}}))
        out = []
        t0 = time.time()
        while time.time() - t0 < timeout:
            opcode, data = self._recv_frame()
            if opcode == 0x9:
                self._send_frame(data, opcode=0xA)
                continue
            if opcode != 0x1:
                continue
            msg = json.loads(data.decode("utf-8", "replace"))
            out.append(msg)
            if msg.get("id") == mid:
                return out
        raise TimeoutError("CDP timeout: " + method)


class Sub:
    """会话内「会话者」：转发调用，同时把事件（method，无 id）攒进 self.events。

    为什么存在：WS.call 会吞掉同连接上的事件帧；需要同时「开 Debugger 断点 + 发网络/控制命令」时
    （断点会暂停 JS，暂停期间 Runtime.evaluate 不返回），必须自己留事件队列。
    """

    def __init__(self, parent):
        self.p = parent
        self.events = []

    def call(self, method, params=None, timeout=60):
        replies = self.p.call_multi(method, params, timeout=timeout)
        for msg in replies:
            if "id" not in msg:
                self.events.append(msg)
        return replies[-1].get("result", {}) if "method" not in replies[-1] else None

    def take(self):
        ev = self.events[:]
        self.events.clear()
        return ev


def session(target_id):
    t = find(target_id)
    return WS(t["webSocketDebuggerUrl"])


def evaluate(target_id, expr, await_promise=True, timeout=90):
    ws = session(target_id)
    try:
        r = ws.call(
            "Runtime.evaluate",
            {"expression": expr, "returnByValue": True, "awaitPromise": await_promise},
            timeout=timeout,
        )
        if r.get("exceptionDetails"):
            raise RuntimeError("JSERR " + json.dumps(r["exceptionDetails"])[:600])
        return r.get("result", {}).get("value")
    finally:
        ws.close()


# ---------------------------------------------------------------- actions
def nav(tid, url):
    """切到新页面并等 load 事件（同 cmd_goto 逻辑，供脚本内复用）。"""
    ws = session(tid)
    try:
        ws.call("Page.enable")
        ws.call("Page.navigate", {"url": url})
        t0 = time.time()
        while time.time() - t0 < 45:
            opcode, data = ws._recv_frame()
            if opcode != 0x1:
                continue
            m = json.loads(data.decode("utf-8", "replace"))
            if m.get("method") == "Page.loadEventFired":
                break
        time.sleep(1.5)
    finally:
        ws.close()


def cmd_list(argv):
    pat = argv[0] if argv else ""
    for p in pages():
        if pat and pat not in (p.get("url") or ""):
            continue
        print(p["id"], "|", (p.get("url") or "")[:120], "|", (p.get("title") or "")[:40])


def cmd_open(argv):
    url = argv[0]
    # Chrome ≥ 111 要求 PUT（GET → 405 Method Not Allowed）
    print(json.loads(_get("/json/new?" + url, method="PUT"))["id"])


def cmd_close(argv):
    print(_get("/json/close/" + argv[0], method="GET").strip() or "ok")


def cmd_eval(argv):
    expr = open(argv[1], encoding="utf-8").read()
    v = evaluate(argv[0], expr)
    print(v if isinstance(v, str) else json.dumps(v, ensure_ascii=False))


def cmd_goto(argv):
    tid, url = argv[0], argv[1]
    ws = session(tid)
    try:
        ws.call("Page.enable")
        ws.call("Page.navigate", {"url": url})
        t0 = time.time()
        while time.time() - t0 < 45:
            opcode, data = ws._recv_frame()
            if opcode != 0x1:
                continue
            m = json.loads(data.decode("utf-8", "replace"))
            if m.get("method") == "Page.loadEventFired":
                break
        time.sleep(1.5)
        print(evaluate(tid, "location.href + ' || ' + document.title"))
    finally:
        ws.close()


def cmd_shot(argv):
    ws = session(argv[0])
    try:
        r = ws.call("Page.captureScreenshot", {"format": "png"}, timeout=60)
        with open(argv[1], "wb") as f:
            f.write(base64.b64decode(r["data"]))
        print("saved", argv[1], os.path.getsize(argv[1]), "bytes")
    finally:
        ws.close()


def cmd_upload(argv):
    tid, sel, path = argv[0], argv[1], os.path.abspath(argv[2])
    ws = session(tid)
    try:
        ws.call("DOM.enable")
        doc = ws.call("DOM.getDocument", {"depth": 0})
        node = ws.call("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": sel})
        if not node.get("nodeId"):
            raise SystemExit("selector not found: " + sel)
        ws.call("DOM.setFileInputFiles", {"nodeId": node["nodeId"], "files": [path]})
        print("uploaded", path, "->", sel)
    finally:
        ws.close()


def cmd_scroll(argv):
    tid = argv[0]
    times = int(argv[1]) if len(argv) > 1 else 3
    js = (
        "(async()=>{for(let i=0;i<%d;i++){window.scrollTo(0,document.body.scrollHeight);"
        "await new Promise(r=>setTimeout(r,900));}return [document.body.scrollHeight, window.scrollY];})()" % times
    )
    print(json.dumps(evaluate(tid, js), ensure_ascii=False))


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return
    cmd, argv = sys.argv[1], sys.argv[2:]
    fn = {
        "list": cmd_list,
        "open": cmd_open,
        "close": cmd_close,
        "eval": cmd_eval,
        "goto": cmd_goto,
        "shot": cmd_shot,
        "upload": cmd_upload,
        "scroll": cmd_scroll,
    }.get(cmd)
    if not fn:
        print(__doc__)
        return
    fn(argv)


if __name__ == "__main__":
    main()
