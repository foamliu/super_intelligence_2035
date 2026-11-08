#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""smoke_http.py — 起一个临时 tutor_server 实例，实测 /health /tool /agent 三个端点。

不依赖 App / 模拟器，纯 PC 侧冒烟：起服务（随机端口）→ urllib 打点 → 打印真实 JSON。
用法：
  py -3.10 -W ignore smoke_http.py
"""
import json
import os
import sys
import threading
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tutor_server as TS  # noqa: E402

# 静默服务端访问日志（默认写 stderr，在 PowerShell 下会被误判为错误）
TS.Handler.log_message = lambda self, fmt, *args: None


def _post(base, path, obj):
    req = urllib.request.Request(
        base + path,
        data=json.dumps(obj).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"_http_error": e.code, "body": e.read().decode("utf-8")}


def main():
    srv = TS.ThreadingHTTPServer(("127.0.0.1", 0), TS.Handler)
    port = srv.server_address[1]
    t = threading.Thread(target=srv.serve_forever, daemon=True)
    t.start()
    base = "http://127.0.0.1:%d" % port

    print("== /health ==")
    with urllib.request.urlopen(base + "/health", timeout=10) as r:
        print(json.dumps(json.loads(r.read().decode("utf-8")), ensure_ascii=False))

    print("\n== /tool calculator 3*4 ==")
    print(json.dumps(_post(base, "/tool", {"tool": "calculator", "params": {"expr": "3*4"}}),
                     ensure_ascii=False))

    print("\n== /tool calculator x+3 (红线：应拒绝，不泄解) ==")
    print(json.dumps(_post(base, "/tool", {"tool": "calculator", "params": {"expr": "x+3"}}),
                     ensure_ascii=False))

    print("\n== /tool question_bank 数学 ==")
    r = _post(base, "/tool", {"tool": "question_bank", "params": {"subject": "数学"}})
    print(json.dumps({"ok": r["ok"], "count": r["result"]["count"],
                      "first": r["result"]["questions"][0],
                      "reply": r["reply"]}, ensure_ascii=False))

    print("\n== /tool wrong_book_add + parent_report ==")
    print(json.dumps(_post(base, "/tool", {"tool": "wrong_book_add",
                                           "params": {"question": "解方程：2x+3=11",
                                                      "student_answer": "x=5",
                                                      "knowledge": "一元一次方程"}}),
                     ensure_ascii=False))
    print(json.dumps(_post(base, "/tool", {"tool": "parent_report", "params": {}}),
                     ensure_ascii=False))

    print("\n== /agent 帮我算 3×4 等于多少（确定性路由 → calculator）==")
    print(json.dumps(_post(base, "/agent", {"question": "解方程：2x+3=11",
                                            "utterance": "帮我算 3×4 等于多少"}),
                     ensure_ascii=False))

    srv.shutdown()
    srv.server_close()
    print("\nsmoke done (port %d)" % port)


if __name__ == "__main__":
    main()
