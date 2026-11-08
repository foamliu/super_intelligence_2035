#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""tutor_server.py 单测（ROADMAP #1：L2 工具/智能体接 HTTP —— /tool、/agent、/tutor 工具路由）。"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tutor_server as TS  # noqa: E402
import tools  # noqa: E402


@pytest.fixture
def tmp_wrong_book(tmp_path, monkeypatch):
    p = str(tmp_path / "wrong_book.json")
    monkeypatch.setattr(tools, "WRONG_BOOK_PATH", p)
    return p


@pytest.fixture
def tmp_practice_log(tmp_path, monkeypatch):
    p = str(tmp_path / "practice_log.json")
    monkeypatch.setattr(TS.l3_profile, "PRACTICE_LOG_PATH", p)
    return p


# ── POST /tool ─────────────────────────────────────────────────────
def test_tool_calculator():
    payload, status = TS.handle_tool({"tool": "calculator", "params": {"expr": "3*4"}})
    assert status == 200
    assert payload["ok"] is True
    assert payload["result"] == {"result": "12"}
    assert "12" in payload["reply"]


def test_tool_calculator_rejects_variable():
    # 🚫 红线：含变量 = 代解方程，工具拒绝且不泄答案
    payload, status = TS.handle_tool({"tool": "calculator", "params": {"expr": "x+3"}})
    assert status == 200
    assert payload["ok"] is False
    assert "变量" in payload["error"]
    assert "4" not in payload["error"]  # 不泄露方程的解


def test_tool_question_bank_no_answer_leak():
    payload, status = TS.handle_tool({"tool": "question_bank", "params": {"subject": "数学"}})
    assert status == 200 and payload["ok"] is True
    for q in payload["result"]["questions"]:
        assert set(q.keys()) == {"id", "subject", "knowledge", "question"}
        assert "answer" not in q and "leak" not in q


def test_tool_wrong_book_add_and_list(tmp_wrong_book):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5"}})
    payload, status = TS.handle_tool({"tool": "wrong_book_list", "params": {}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"]["total"] == 1
    for item in payload["result"]["recent"]:
        assert "student_answer" not in item  # 列表不夹带学生错答原文


def test_tool_parent_report(tmp_wrong_book):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5",
                               "knowledge": "一元一次方程"}})
    payload, status = TS.handle_tool({"tool": "parent_report", "params": {}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"]["total_wrong"] == 1
    assert os.path.isfile(payload["result"]["path"])


def test_tool_unknown():
    payload, status = TS.handle_tool({"tool": "solve_equation", "params": {}})
    assert status == 200 and payload["ok"] is False
    assert "未知工具" in payload["error"]


def test_tool_missing_tool():
    payload, status = TS.handle_tool({})
    assert status == 400 and payload["ok"] is False


# ── POST /tutor 带 tool 字段（ROADMAP #1「/tutor 增加 tool/params」）──
def test_tutor_routes_tool():
    payload, status = TS.handle_tutor({"tool": "calculator", "params": {"expr": "6*7"}})
    assert status == 200 and payload["ok"] is True
    assert payload["result"] == {"result": "42"}


# ── POST /agent（L2 智能体多轮，默认确定性路由，不调网络）───────────
def test_agent_calculator():
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "帮我算 3×4 等于多少"})
    assert status == 200
    assert payload["kind"] == "tool" and payload["tool"] == "calculator"
    assert "12" in payload["reply"]


def test_agent_guide(monkeypatch):
    monkeypatch.setattr(TS.l2_agent.ta, "tutor_step", lambda q, h: "先想想怎么把 3 消掉？")
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "我想先移项"})
    assert status == 200
    assert payload["kind"] == "guide"
    assert "消掉" in payload["reply"]


def test_agent_redline_no_answer():
    # 学生想让家教「算方程的解」→ calculator 拒绝变量 → 不泄答案
    payload, status = TS.handle_agent({"question": "解方程：2x+3=11",
                                       "utterance": "帮我算 2x+3 的解"})
    assert status == 200
    assert payload["tool"] == "calculator"
    assert "4" not in payload["reply"]


def test_agent_missing_fields():
    payload, status = TS.handle_agent({"question": "x"})
    assert status == 400
    assert "utterance" in payload["error"]


def test_agent_replay_history(monkeypatch):
    # 回放历史后，引导上下文应包含之前轮次
    seen = {}

    def fake_step(q, h):
        seen["n"] = len(h)
        return "第%d轮引导" % (len(h) + 1)

    monkeypatch.setattr(TS.l2_agent.ta, "tutor_step", fake_step)
    payload, status = TS.handle_agent({
        "question": "解方程：2x+3=11",
        "utterance": "再然后呢？",
        "history": [["第一步？", "先移项"], ["然后？", "两边除以2"]],
    })
    assert status == 200 and payload["kind"] == "guide"
    assert seen["n"] == 2  # 两轮历史已回放进上下文
    assert "第3轮引导" in payload["reply"]


# ── POST /profile（ROADMAP L3：知识点画像 + 每日/每周摘要）──────────
def test_profile_summary(tmp_wrong_book, tmp_practice_log):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5",
                               "knowledge": "一元一次方程"}})
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：3x-5=10", "student_answer": "x=6",
                               "knowledge": "一元一次方程"}})
    payload, status = TS.handle_profile({})
    assert status == 200 and payload["ok"] is True
    prof = payload["profile"]
    assert prof["total_wrong"] == 2
    assert prof["total_practice"] == 0
    assert prof["knowledge_count"] == 1
    assert prof["weak_points"][0]["knowledge"] == "一元一次方程"
    assert prof["weak_points"][0]["mastery"] == "薄弱"
    assert prof["daily"]["total_days"] >= 1
    assert prof["weekly"]["total_weeks"] >= 1


def test_profile_no_answer_leak(tmp_wrong_book, tmp_practice_log):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=4",
                               "knowledge": "一元一次方程"}})
    payload, status = TS.handle_profile({})
    assert status == 200
    blob = json.dumps(payload["profile"], ensure_ascii=False)
    assert "x=4" not in blob      # 不泄露最终答案 / 不夹带学生错答


def test_profile_html(tmp_wrong_book, tmp_practice_log, tmp_path):
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "因式分解：x²-9", "student_answer": "x(x-3)",
                               "knowledge": "因式分解"}})
    out = str(tmp_path / "profile.html")
    payload, status = TS.handle_profile({"html": True, "out_path": out})
    assert status == 200 and payload["ok"] is True
    assert os.path.isfile(out)
    with open(out, encoding="utf-8") as f:
        html = f.read()
    assert "<!DOCTYPE html>" in html and "家教学习画像" in html
    assert "(x+3)(x-3)" not in html  # 不泄答案


def test_profile_empty(tmp_wrong_book, tmp_practice_log):
    payload, status = TS.handle_profile({})
    assert status == 200 and payload["ok"] is True
    assert payload["profile"]["total_wrong"] == 0
    assert payload["profile"]["weak_points"] == []


# ── POST /practice（ROADMAP L3 补正样本：作答次数 + 正确率）────────
def test_practice_logs_and_merges(tmp_wrong_book, tmp_practice_log):
    # 先记 1 道错题（负样本）
    TS.handle_tool({"tool": "wrong_book_add",
                    "params": {"question": "解方程：2x+3=11", "student_answer": "x=5",
                               "knowledge": "一元一次方程"}})
    # 再记 2 次作答（正样本）：1 对 1 错，同一知识点
    p1, s1 = TS.handle_practice({"question": "解方程：2x+3=11", "student_answer": "x=4",
                                 "knowledge": "一元一次方程", "correct": True})
    p2, s2 = TS.handle_practice({"question": "解方程：4x+1=9", "student_answer": "x=3",
                                 "knowledge": "一元一次方程", "correct": False})
    assert s1 == 200 and p1["ok"] is True
    assert s2 == 200 and p2["ok"] is True
    assert p1["total_practice"] == 1
    assert p2["total_practice"] == 2

    prof_payload, status = TS.handle_profile({})
    assert status == 200
    prof = prof_payload["profile"]
    assert prof["total_wrong"] == 1
    assert prof["total_practice"] == 2
    kp = prof["knowledge_points"][0]
    assert kp["knowledge"] == "一元一次方程"
    assert kp["wrong_count"] == 1
    assert kp["attempt_count"] == 2
    assert kp["correct_count"] == 1
    assert kp["correct_rate"] == 0.5


def test_practice_no_answer_leak(tmp_wrong_book, tmp_practice_log):
    TS.handle_practice({"question": "解方程：2x+3=11", "student_answer": "x=4",
                        "knowledge": "一元一次方程", "correct": False})
    payload, status = TS.handle_profile({})
    assert status == 200
    blob = json.dumps(payload["profile"], ensure_ascii=False)
    assert "x=4" not in blob      # 画像不夹带学生作答原文 / 答案


def test_practice_requires_question(tmp_practice_log):
    payload, status = TS.handle_practice({})
    assert status == 400 and payload["ok"] is False
    assert "question" in payload["error"]

