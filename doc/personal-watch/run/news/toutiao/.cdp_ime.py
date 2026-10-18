#!/usr/bin/env python3
# news 线临时工具：真实「输入法」录入（CDP Input.insertText）——React 能感知（state 会同步），
# 但不会点亮 submit-btn；提交请用 .cdp_reactsubmit.py。
# 用法: python3 news/toutiao/.cdp_ime.py <targetId> <selector> <text>
import os
import sys
import time

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "fanqie"))
import cdp  # noqa: E402

tid, sel, text = sys.argv[1], sys.argv[2], sys.argv[3]
ws = cdp.session(tid)
try:
    ws.call("DOM.enable")
    doc = ws.call("DOM.getDocument", {})
    q = ws.call("DOM.querySelector", {"nodeId": doc["root"]["nodeId"], "selector": sel})
    if not q.get("nodeId"):
        raise SystemExit("NO_NODE " + sel)
    ws.call("DOM.describeNode", {"nodeId": q["nodeId"]})
    ws.call("DOM.focus", {"nodeId": q["nodeId"]})
    ws.call("Input.insertText", {"text": text})
    time.sleep(1.2)
finally:
    ws.close()
print("inserted", len(text))
