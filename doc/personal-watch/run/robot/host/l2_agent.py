#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""robot 线 · L2 智能体 · 工具编排层（会话状态 + 工具路由 + 分步引导）。

「调用大模型 / 智能体辅导」的智能体骨架：
- `route_tool()`：确定性意图路由（离线可用、可单测、不依赖 LLM）；
- `decide_tool_llm()`：让 DeepSeek 从工具清单里选工具（智能体主路径，失败回退路由）；
- `L2Session`：维持一道题的会话状态，学生说一句 → 走工具或走引导，多轮不丢上下文。

教育红线（沿用 tutor_agent.TUTOR_SYSTEM）：工具只做「验算 / 换题 / 记错题 / 报告 / 绘图」，
**不代解方程、不泄原题答案**；计算器拒绝含变量表达式即是对「代解」的硬性封堵。
"""
import json
import re
import sys

HERE = __import__("os").path.dirname(__import__("os").path.abspath(__file__))
sys.path.insert(0, HERE)
import tools  # noqa: E402
import tutor_agent as ta  # noqa: E402

# 意图路由（确定性，离线可用）。顺序 = 优先级（更具体的词在前）。
_PATTERNS = [
    ("parent_report", ("报告", "总结", "家长", "今天学", "本周学", "学习情况")),
    ("wrong_book_add", ("这题我错了", "加入错题本", "记入错题本", "记下来")),
    ("wrong_book_list", ("错题本", "看看错题", "复习错题", "我错过的")),
    ("question_bank", ("类似题", "换一题", "再出一题", "同类题", "再来一题", "举一反三")),
    ("plot_function", ("画图", "图像", "函数图", "画一下", "作图")),
    ("calculator", ("算", "计算", "验算", "等于多少", "=?", "＝?")),
]


def route_tool(utterance: str):
    """确定性路由：命中返回 {"tool": 名, "params": {...}}，否则 None。"""
    u = (utterance or "").strip()
    if not u:
        return None
    for name, kws in _PATTERNS:
        if any(k in u for k in kws):
            if name == "calculator":
                return {"tool": name, "params": {"expr": _extract_math(u)}}
            if name == "question_bank":
                return {"tool": name, "params": {"subject": _guess_subject(u), "keyword": ""}}
            if name == "plot_function":
                return {"tool": name, "params": {"expr": _extract_func(u)}}
            return {"tool": name, "params": {}}
    return None


_CH_MAP = {"乘以": "*", "除以": "/", "乘": "*", "除": "/", "加": "+", "减": "-"}


def _extract_math(utterance: str) -> str:
    """从「帮我算 3×4 等于多少」里抠出算式（只做符号归一，不做语义）。"""
    s = utterance
    for kw in ("算一下", "算一算", "帮我", "请", "你", "来", "计算", "验算", "算",
               "等于多少", "是多少", "等于几", "等于", "=?", "＝?", "？", "?"):
        s = s.replace(kw, " ")
    for k, v in _CH_MAP.items():
        s = s.replace(k, v)
    m = re.search(r"[\da-zA-Z+\-*/().^×÷\s]{2,}", s)
    return re.sub(r"\s+", "", m.group(0)) if m else ""


def _guess_subject(utterance: str) -> str:
    for sub in ("数学", "物理", "英语"):
        if sub in utterance:
            return sub
    return ""


def _extract_func(utterance: str) -> str:
    """从「画一下 x^2-1 的图像」里抠出含 x 的函数表达式。"""
    s = utterance
    for kw in ("画一下", "画一画", "画图", "画", "函数图", "作图", "图像", "的图", "一下"):
        s = s.replace(kw, " ")
    s = s.replace("＝", "=")
    m = re.search(r"[0-9a-zA-Z+\-*/().^xX\s]{2,}", s)
    return re.sub(r"\s+", "", m.group(0)) if m else ""


def decide_tool_llm(utterance: str, question: str = ""):
    """智能体主路径：让 DeepSeek 从工具清单里选工具。

    返回 {"tool": 名, "params": {...}} 或 {"tool": None}。失败抛异常 → 调用方回退 `route_tool`。
    """
    spec = tools.tool_spec()
    sys_msg = (
        "你是家教助手的工具选择器。根据学生这句话，从工具清单里选一个工具，"
        "若学生只是在讨论题目、需要分步引导，则 tool 为 null。"
        "只输出一行 JSON：{\"tool\": \"<名字或null>\", \"params\": {...}}。\n"
        "工具清单：" + spec
    )
    out = ta.chat([
        {"role": "system", "content": sys_msg},
        {"role": "user", "content": "题目：%s\n学生说：%s" % (question, utterance)},
    ])
    return _parse_decision(out)


def _parse_decision(text: str):
    s = (text or "").strip()
    s = re.sub(r"^```(json)?\s*|\s*```$", "", s)
    m = re.search(r"\{.*\}", s, re.S)
    if not m:
        raise ValueError("LLM 未返回 JSON")
    obj = json.loads(m.group(0))
    name = obj.get("tool")
    if not name:
        return {"tool": None, "params": {}}
    if name not in tools.TOOLS:
        raise ValueError("LLM 选了未知工具：%s" % name)
    return {"tool": name, "params": obj.get("params") or {}}


class L2Session:
    """一道题的家教会话：维护题干 / 历史 / 工具路由 / 引导。多轮不丢上下文。"""

    def __init__(self, question: str, knowledge: str = "", subject: str = "数学",
                 use_llm: bool = False):
        self.question = question
        self.knowledge = knowledge
        self.subject = subject
        self.use_llm = use_llm
        self.history = []          # [(学生话, 家教引导话), ...]  只喂给 tutor_step
        self.tool_log = []         # 工具轮次单独记，不进引导上下文（避免污染多轮一致性）

    def respond(self, utterance: str) -> dict:
        """学生说一句 → 返回 {"kind": "tool"|"guide", "tool", "tool_result", "reply"}。"""
        u = (utterance or "").strip()
        decision = None
        if self.use_llm:
            try:
                decision = decide_tool_llm(u, self.question)
            except Exception:      # noqa: BLE001  LLM 决策失败 → 回退确定性路由
                decision = None
        if decision is None:
            decision = route_tool(u)

        if decision and decision.get("tool"):
            name, params = decision["tool"], decision.get("params") or {}
            if name == "wrong_book_add" and not params.get("question"):
                params = {"question": self.question, "student_answer": u,
                          "knowledge": self.knowledge}
            try:
                result = tools.call_tool(name, params)
                reply = self._tool_reply(name, result, params)
            except tools.ToolError as e:
                reply = self._tool_error_reply(name, str(e))
                result = {"error": str(e)}
            self.tool_log.append({"tool": name, "utterance": u, "result": result})
            return {"kind": "tool", "tool": name, "tool_result": result, "reply": reply}

        # 默认：分步引导（不含答案，见 tutor_agent.TUTOR_SYSTEM）
        step = ta.tutor_step(self.question, self.history)
        self.history.append((u, step))
        return {"kind": "guide", "tool": None, "tool_result": None, "reply": step}

    # ── 工具结果 → 口语化回复（≤2 句、不泄答案）────────────────────
    def _tool_reply(self, name, result, params):
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

    def _tool_error_reply(self, name, msg):
        if name == "calculator":
            return "我只能帮你验算纯数字，方程要自己一步步解哦。"
        if name == "plot_function":
            return "把含 x 的表达式发给我，比如 x^2-1。"
        return "这个我没法直接做：%s" % msg

    def mark_wrong(self, student_answer: str):
        """显式把当前题记为错题（供评测/真实会话里「这题做错了」触发）。"""
        return tools.wrong_book_add(self.question, student_answer, self.knowledge)

    def report(self, out_path=None):
        return tools.parent_report(out_path=out_path)


def run_demo():
    """离线自检演示：不调网络，只走确定性路由 + 工具。"""
    s = L2Session("解方程：2x + 3 = 11", knowledge="一元一次方程")
    for u in ["帮我算 3×4 等于多少", "给我一道类似题练练", "这题我错了，记入错题本",
              "看看错题本", "生成家长报告", "帮我算 2x+3 的解"]:
        r = s.respond(u)
        print("[%s] %s\n   → %s" % (r["tool"] or "-", u, r["reply"]))
    print("\nreport:", s.report())


if __name__ == "__main__":
    run_demo()

