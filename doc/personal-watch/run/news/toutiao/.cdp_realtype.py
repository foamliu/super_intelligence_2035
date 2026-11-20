#!/usr/bin/env python3
# news 线临时工具：用 CDP Input.dispatchKeyEvent 真实敲字（会触发 React 的 onInput ⇒ 激活提交按钮）
# 用法: python3 .cdp_realtype.py <targetId> <text>
# 用法: python3 news/toutiao/.cdp_realtype.py <targetId> <text> [--enter]
#   --enter: 敲完后再真实按一次 Enter（头条评论 textarea 靠 Enter 或点亮后的「评论」按钮提交）
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

tid, text = sys.argv[1], sys.argv[2]
send_enter = "--enter" in sys.argv
ws = cdp.session(tid)


def key(name, code, vk):
    for t in ("keyDown", "keyUp"):
        ws.call(
            "Input.dispatchKeyEvent",
            {"type": t, "key": name, "code": code, "windowsVirtualKeyCode": vk, "nativeVirtualKeyCode": vk},
        )


try:
    for ch in text:
        if ch == "\n":
            key("Enter", "Enter", 13)
        else:
            ws.call("Input.dispatchKeyEvent", {"type": "keyDown", "text": ch, "unmodifiedText": ch})
            ws.call("Input.dispatchKeyEvent", {"type": "keyUp"})
        time.sleep(0.03)
    if send_enter:
        key("Enter", "Enter", 13)
finally:
    ws.close()
print("typed", len(text), "enter" if send_enter else "")
