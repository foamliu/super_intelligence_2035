#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · PC 侧家教 HTTP 服务（Android App 通过 http://10.0.2.2:PORT 调它）

接口（11:30 用户令统一 POST /tutor 口径 + 11:40 令流式/打断扩展点）：
  POST /tutor   入 {image_b64?, text?, student_ctx?, history?, hint_level?}
                出 {reply_text, tts_text, step, hint_level, needs, question_text, vision, tutor, latency_s}
  GET  /health  健康检查 {ok, version, backends}
  GET  /        使用说明

推理后端复用 host/tutor_agent.py（识图/引导默认云端 DeepSeek `deepseek-flash`，
断网/无 key 自动降级本机 ollama，降级路径写在返回里、绝不静默，见 15:4x 令 §2.2）。

监听 0.0.0.0:8765 —— 模拟器内访问宿主机用 `10.0.2.2:8765`（不是 127.0.0.1）。
运行：
  py -3.10 -W ignore tutor_server.py
"""
import base64
import json
import os
import sys
import tempfile
import time
import traceback
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import tutor_agent  # noqa: E402  复用 recognize_ex / tutor_step / LAST_*_TRACE

PORT = int(os.environ.get("ROBOT_TUTOR_PORT", "8765"))
HOST = os.environ.get("ROBOT_TUTOR_HOST", "0.0.0.0")
MAX_BODY = int(os.environ.get("ROBOT_TUTOR_MAX_BODY", str(20 * 1024 * 1024)))

# 学生画像（12:05 令：用户 8 年级女儿 · 一对一；🚫 硬编码进代码，这里是配置默认值）
STUDENT_CTX_DEFAULT = {
    "grade": "八年级(初二)",
    "subject": "数学",
    "textbook": "人教版",
    "session_minutes": 25,
}


def _b64_to_tmpfile(b64: str) -> str:
    """把 App 上传的 base64 题图写到临时文件（服务端不留存原图，处理完即删）。"""
    raw = base64.b64decode(b64)
    fd, path = tempfile.mkstemp(suffix=".png", prefix="robot_q_")
    with os.fdopen(fd, "wb") as f:
        f.write(raw)
    return path


def handle_tutor(body: dict):
    """核心：{image_b64|text} -> 识图 -> 分步引导。返回 (payload, http_status)。"""
    t0 = time.time()
    image_b64 = (body.get("image_b64") or "").strip()
    text = (body.get("text") or "").strip()
    history = body.get("history") or []
    hint_level = body.get("hint_level") or 1

    tmpfile = None
    try:
        if image_b64:
            tmpfile = _b64_to_tmpfile(image_b64)
            question, vtrace = tutor_agent.recognize_ex(tmpfile)
        elif text:
            question, vtrace = tutor_agent.recognize_ex(text)
        else:
            return {"error": "需要 image_b64 或 text 之一"}, 400

        step = tutor_agent.tutor_step(question, history)
        ttrace = dict(tutor_agent.LAST_TUTOR_TRACE)

        payload = {
            "reply_text": step,
            "tts_text": step,
            "step": 1,
            "hint_level": hint_level,
            "needs": "student_answer",
            "question_text": question,
            "vision": vtrace,
            "tutor": ttrace,
            "latency_s": round(time.time() - t0, 2),
        }
        return payload, 200
    finally:
        if tmpfile and os.path.isfile(tmpfile):
            try:
                os.remove(tmpfile)
            except OSError:
                pass


class Handler(BaseHTTPRequestHandler):
    server_version = "robot-tutor/1.0"

    def _send_json(self, obj, status=200):
        data = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(data)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        if self.path.rstrip("/") in ("", "/health"):
            self._send_json({
                "ok": True,
                "version": "1.0",
                "vision_backend": tutor_agent.VISION_BACKEND,
                "tutor_backend": tutor_agent.TUTOR_BACKEND,
            })
        else:
            self._send_json({
                "usage": "POST /tutor  {image_b64 | text, history?, hint_level?}",
                "note": "App 端请用 http://10.0.2.2:%d/tutor" % PORT,
            })

    def do_POST(self):
        if self.path.rstrip("/") != "/tutor":
            self._send_json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_BODY:
                self._send_json({"error": "body too large"}, 413)
                return
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
            payload, status = handle_tutor(body)
            self._send_json(payload, status)
        except Exception as e:  # noqa: BLE001  服务端异常也要回 JSON，别把连接崩掉
            self._send_json({"error": str(e), "trace": traceback.format_exc()[-500:]}, 500)

    def log_message(self, fmt, *args):  # 打点但控制音量
        sys.stderr.write("[%s] %s\n" % (time.strftime("%H:%M:%S"), fmt % args))


def main():
    srv = ThreadingHTTPServer((HOST, PORT), Handler)
    print("robot tutor server listening on %s:%d" % (HOST, PORT))
    print("  App 端访问宿主机用 http://10.0.2.2:%d/tutor" % PORT)
    print("  后端：vision=%s tutor=%s" % (tutor_agent.VISION_BACKEND, tutor_agent.TUTOR_BACKEND))
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        srv.server_close()


if __name__ == "__main__":
    main()
