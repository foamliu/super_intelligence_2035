#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · PC 侧家教 HTTP 服务（Android App 通过 http://10.0.2.2:PORT 调它）

接口（11:30 用户令统一 POST /tutor 口径 + 11:40 令流式/打断扩展点 + ROADMAP #1 L2 工具接 HTTP）：
  POST /tutor   入 {image_b64?, text?, student_ctx?, history?, hint_level?, tool?, params?}
                出 {reply_text, tts_text, step, hint_level, needs, question_text, vision, tutor, latency_s}
                若带 tool 字段 → 直接调用 L2 工具（等价 POST /tool）。
  POST /tool    入 {tool, params}  出 {ok, tool, result, reply, latency_s}
                工具 = calculator / question_bank / wrong_book_add / wrong_book_list / parent_report / plot_function
  POST /agent   入 {question, utterance, history?, knowledge?, use_llm?}
                出 {kind: tool|guide, tool, tool_result, reply, latency_s}   （L2 智能体多轮，确定性路由默认，可选 LLM 决策）
  POST /profile 入 {html?: bool, out_path?: str}
                出 {ok, profile}   （L3 学情：知识点画像 + 每日/每周摘要；html=true 另生成 HTML）
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
import tools       # noqa: E402  L2 工具层（ROADMAP #1）
import l2_agent    # noqa: E402  L2 智能体编排（/agent 多轮）
import l3_profile  # noqa: E402  L3 学情层（知识点画像 + 每日/每周摘要，ROADMAP L3）
import knowledge   # noqa: E402  知识点自动分类（LLM + 本地兜底，ROADMAP「下一轮候选 #5」）

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


def _tool_reply(name: str, result: dict) -> str:
    """把工具结果翻译成给学生的口语化一句（≤2 句、不泄答案，口径同 l2_agent._tool_reply）。"""
    if name == "calculator":
        return "验算结果是 %s。你自己核一下对不对？" % result["result"]
    if name == "question_bank":
        qs = result.get("questions") or []
        if not qs:
            return "没找到同类题，换个关键词试试？"
        return "给你一道同类题练练：%s 你先试试，做完告诉我。" % qs[0]["question"]
    if name == "wrong_book_add":
        return "已记入错题本，现在共 %d 道。我们回头一起复盘。" % result["total"]
    if name == "wrong_book_list":
        return "错题本里共有 %d 道，记得定期复习。" % result["total"]
    if name == "parent_report":
        return "学习报告已生成，共 %d 道错题。" % result["total_wrong"]
    if name == "plot_function":
        return "函数图像画好了，可以看图想一想走势。"
    return "好的，已处理。"


def handle_tool(body: dict):
    """直接调用 L2 工具（POST /tool 或 POST /tutor 带 tool 字段）。返回 (payload, http_status)。

    教育红线：calculator 拒绝含变量表达式（防代解方程）；题库/错题本列表剥离 answer/leak。
    """
    t0 = time.time()
    name = (body.get("tool") or "").strip()
    params = body.get("params") or {}
    if not name:
        return {"ok": False, "error": "缺少 tool 字段"}, 400
    try:
        result = tools.call_tool(name, params)
        return {
            "ok": True,
            "tool": name,
            "result": result,
            "reply": _tool_reply(name, result),
            "latency_s": round(time.time() - t0, 3),
        }, 200
    except tools.ToolError as e:
        # 工具拒绝（红线封堵 / 参数非法）——不是服务端错误，正常回 JSON 给 App 显示
        return {"ok": False, "tool": name, "error": str(e)}, 200
    except Exception as e:  # noqa: BLE001
        return {"ok": False, "tool": name, "error": str(e)}, 500


def handle_agent(body: dict):
    """智能体多轮：POST /agent {question, utterance, history?, knowledge?, use_llm?}。

    返回 {kind: tool|guide, tool, tool_result, reply, latency_s}。
    默认确定性路由（use_llm=False，离线可用）；use_llm=True 时先让 DeepSeek 选工具、失败回退路由。
    """
    t0 = time.time()
    question = (body.get("question") or "").strip()
    utterance = (body.get("utterance") or "").strip()
    if not question or not utterance:
        return {"error": "需要 question 与 utterance"}, 400
    session = l2_agent.L2Session(
        question,
        knowledge=body.get("knowledge") or "",
        use_llm=bool(body.get("use_llm")),
    )
    for s, a in (body.get("history") or []):   # 回放历史，重建多轮上下文
        session.history.append((s, a))
    r = session.respond(utterance)
    r["latency_s"] = round(time.time() - t0, 3)
    return r, 200


def handle_tutor(body: dict):
    """核心：{image_b64|text} -> 识图 -> 分步引导。返回 (payload, http_status)。

    ROADMAP #1：带 tool 字段时直接路由到 L2 工具（等价 POST /tool）。
    """
    if (body.get("tool") or "").strip():
        return handle_tool(body)

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


def handle_profile(body: dict):
    """L3 学情：POST /profile {} -> 合并画像（错题本 + 练习正样本）+ 每日/每周摘要。

    入 {html?: bool, out_path?: str}；出 {ok, profile}。
    数据来自本地错题本（tools.WRONG_BOOK_PATH）+ 练习日志（l3_profile.PRACTICE_LOG_PATH），
    不上传、不含学生隐私、不泄露答案。正样本含作答次数/正确率（ROADMAP L3「补正样本」）。
    """
    if body.get("html") or body.get("out_path"):
        rep = l3_profile.profile_report_full(out_path=body.get("out_path") or None)
    else:
        prof = l3_profile.merged_profile()
        rep = {
            "total_wrong": prof["total_wrong"],
            "total_practice": prof["total_practice"],
            "knowledge_count": len(prof["knowledge_points"]),
            "weak_points": prof["weak_points"],
            "knowledge_points": prof["knowledge_points"],
            "practice": l3_profile.practice_summary(),
            "daily": l3_profile.daily_summary(),
            "weekly": l3_profile.weekly_summary(),
        }
    return {"ok": True, "profile": rep}, 200


def handle_practice(body: dict):
    """记录一次作答（正样本）：POST /practice {question, student_answer?, knowledge?, correct}。

    出 {ok, entry, knowledge, classify, total_practice, profile}。练习日志只落本地、
    不上传、不泄答案。`knowledge` 缺省时用 knowledge.classify_knowledge() 自动分类
    （LLM 优先、本地关键词兜底，绝不静默降级）——此前一律记成「未分类」。
    """
    question = (body.get("question") or "").strip()
    if not question:
        return {"ok": False, "error": "缺少 question"}, 400
    knowledge_label = (body.get("knowledge") or "").strip()
    classify_trace = None
    if not knowledge_label:
        knowledge_label, classify_trace = knowledge.classify_knowledge(question)
    entry = l3_profile.log_practice(
        question,
        student_answer=(body.get("student_answer") or "").strip(),
        knowledge=knowledge_label,
        correct=bool(body.get("correct")),
    )
    prof = l3_profile.merged_profile()
    return {
        "ok": True,
        "entry": entry,
        "knowledge": entry["knowledge"],
        "classify": classify_trace,
        "total_practice": prof["total_practice"],
        "profile": {
            "total_wrong": prof["total_wrong"],
            "total_practice": prof["total_practice"],
            "knowledge_count": len(prof["knowledge_points"]),
            "weak_points": prof["weak_points"],
            "knowledge_points": prof["knowledge_points"],
        },
    }, 200


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
                "usage": "POST /tutor {image_b64|text, history?, hint_level?, tool?, params?} · "
                         "POST /tool {tool, params} · POST /agent {question, utterance, history?} · "
                         "POST /profile {html?} · POST /practice {question, correct, knowledge?}",
                "note": "App 端请用 http://10.0.2.2:%d/tutor" % PORT,
            })

    def do_POST(self):
        path = self.path.rstrip("/")
        if path not in ("/tutor", "/tool", "/agent", "/profile", "/practice"):
            self._send_json({"error": "not found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            if length > MAX_BODY:
                self._send_json({"error": "body too large"}, 413)
                return
            raw = self.rfile.read(length)
            body = json.loads(raw.decode("utf-8"))
            fn = {"/tutor": handle_tutor, "/tool": handle_tool,
                  "/agent": handle_agent, "/profile": handle_profile,
                  "/practice": handle_practice}[path]
            payload, status = fn(body)
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
