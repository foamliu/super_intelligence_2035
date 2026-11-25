#!/usr/bin/env python3
# news 线临时工具：真实鼠标点击（CDP Input.dispatchMouseEvent ⇒ 可信事件流，能触发 React onClick）
# 背景：dispatchEvent(new MouseEvent) / el.click() 是「不可信事件」，头条评论区不响应；必须走 CDP Input 域。
# 用法: python3 news/toutiao/.cdp_click.py <targetId> <x> <y> [clicks]
#   x/y 可用 document.documentElement.clientWidth / clientHeight 自行换算成 CSS 像素。
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

tid, x, y = sys.argv[1], float(sys.argv[2]), float(sys.argv[3])
clicks = int(sys.argv[4]) if len(sys.argv) > 4 else 1
ws = cdp.session(tid)
try:
    for _ in range(clicks):
        ws.call("Input.dispatchMouseEvent", {"type": "mouseMoved", "x": x, "y": y, "button": "none"})
        time.sleep(0.2)
        ws.call("Input.dispatchMouseEvent", {"type": "mousePressed", "x": x, "y": y, "button": "left", "buttons": 1, "clickCount": 1})
        time.sleep(0.05)
        ws.call("Input.dispatchMouseEvent", {"type": "mouseReleased", "x": x, "y": y, "button": "left", "buttons": 0, "clickCount": 1})
        time.sleep(0.4)
finally:
    ws.close()
print("clicked", x, y, "x", clicks)
