#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""news 线临时工具（2026-10-20 新增）：纯 python 的 CDP 操作封装，替代依赖 `ws` 的 node 脚本。

为什么：2026-10-20 实测 `node -e "require('ws')"` 报 `Cannot find module 'ws'`
（node v24.23.0 · 全局 node_modules 只有 cline/corepack/npm）⇒ `eval_on_tab.js` /
`mouse_click.js` / `tt_keytype.js` 全部不可用。本文件复用 `news/fanqie/cdp.py`
里的零依赖 raw-socket WS 客户端，提供同一组动作。

用法：
  python3 news/toutiao/.cdp_tool.py eval   <targetId> <jsFile>
  python3 news/toutiao/.cdp_tool.py click  <targetId> <x> <y>
  python3 news/toutiao/.cdp_tool.py shot   <targetId> <outPng>
  python3 news/toutiao/.cdp_tool.py type   <targetId> <text> [--enter]   # 真实按键（触发 React onInput）
  python3 news/toutiao/.cdp_tool.py goto   <targetId> <url>

约定：只按 targetId 精确操作；🚫 不 pkill 9222 的 Chrome；🚫 不动 zhipin.com 标签。
"""
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402


def cmd_eval(argv):
    expr = open(argv[1], encoding="utf-8").read()
    v = cdp.evaluate(argv[0], expr)
    print(v if isinstance(v, str) else __import__("json").dumps(v, ensure_ascii=False))


def cmd_click(argv):
    tid, x, y = argv[0], float(argv[1]), float(argv[2])
    ws = cdp.session(tid)
    try:
        for t in ("mouseMoved", "mousePressed", "mouseReleased"):
            ws.call(
                "Input.dispatchMouseEvent",
                {"type": t, "x": x, "y": y, "button": "left", "clickCount": 1,
                 "buttons": 1 if t == "mousePressed" else 0},
            )
            time.sleep(0.12)
        print("CLICKED_AT %s,%s" % (x, y))
    finally:
        ws.close()


def cmd_shot(argv):
    import base64
    ws = cdp.session(argv[0])
    try:
        r = ws.call("Page.captureScreenshot", {"format": "png"}, timeout=60)
        with open(argv[1], "wb") as f:
            f.write(base64.b64decode(r["data"]))
        print("saved", argv[1], os.path.getsize(argv[1]), "bytes")
    finally:
        ws.close()


def cmd_type(argv):
    tid, text = argv[0], argv[1]
    ws = cdp.session(tid)
    try:
        for ch in text:
            if ch == "\n":
                for t in ("keyDown", "keyUp"):
                    ws.call("Input.dispatchKeyEvent",
                            {"type": t, "key": "Enter", "code": "Enter",
                             "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
            else:
                ws.call("Input.dispatchKeyEvent", {"type": "keyDown", "text": ch, "unmodifiedText": ch})
                ws.call("Input.dispatchKeyEvent", {"type": "keyUp"})
            time.sleep(0.03)
        if "--enter" in argv:
            for t in ("keyDown", "keyUp"):
                ws.call("Input.dispatchKeyEvent",
                        {"type": t, "key": "Enter", "code": "Enter",
                         "windowsVirtualKeyCode": 13, "nativeVirtualKeyCode": 13})
    finally:
        ws.close()
    print("typed", len(text), "enter" if "--enter" in argv else "")


def cmd_goto(argv):
    cdp.cmd_goto(argv)


def main():
    cmd, argv = sys.argv[1], sys.argv[2:]
    {"eval": cmd_eval, "click": cmd_click, "shot": cmd_shot,
     "type": cmd_type, "goto": cmd_goto}[cmd](argv)


if __name__ == "__main__":
    main()
