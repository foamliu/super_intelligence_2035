#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""knowledge.py 单测（ROADMAP「下一轮候选 #5」：知识点自动分类 LLM + 本地兜底）。"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import knowledge as K  # noqa: E402


# ── 本地关键词分类（确定性，无网络）───────────────────────────────────
@pytest.mark.parametrize("question,expected", [
    # 数学
    ("解方程：2x + 3 = 11", "一元一次方程"),
    ("解方程组：x + y = 10，x - y = 4", "二元一次方程组"),
    ("因式分解：x² - 9", "因式分解"),
    ("化简：3(a - 2b) + 2(a + b)", "整式加减"),
    ("化简：(2x + 1)(x - 3)", "整式乘法"),
    ("化简：(x² - 4) / (x + 2)", "分式化简"),
    ("计算：1/2 + 1/3", "分式运算"),
    ("化简：√18", "二次根式"),
    ("计算：|-3| + √9", "实数运算"),
    ("求 9 的算术平方根", "平方根"),
    ("已知等腰三角形顶角为 40°，求底角的度数。", "等腰三角形"),
    ("已知△ABC ≌ △DEF，AB = 5 cm，求 DE 的长", "全等三角形"),
    ("直角三角形两条直角边分别为 3 和 4，求斜边", "勾股定理"),
    ("线段 AB 的垂直平分线上有一点 P，若 PA = 5，求 PB 的长", "轴对称"),
    ("在△ABC 中，∠A = 50°，∠B = 60°，求∠C 的度数", "三角形内角和"),
    ("在△ABC 中，∠A = 40°，∠B = 30°，求外角∠ACD 的度数", "三角形外角"),
    ("平行四边形四个内角的和", "平行四边形"),
    # 物理
    ("物体以 5 m/s 做匀速直线运动，求 10 s 内通过的路程", "匀速直线运动"),
    ("汽车 2 h 行驶 120 km，求平均速度", "平均速度"),
    ("声音在空气中传播速度为 340 m/s，求 2 s 内传播的距离", "声速测距"),
    ("声速 340 m/s，发出的声音经 0.2 s 返回（回声），求障碍物到声源的距离", "回声测距"),
    ("入射光线与镜面的夹角为 60°，求入射角", "光的反射"),
    ("液体压强 p = ρgh，h = 2 m，求压强", "液体压强"),
    ("物体排开水的重力为 8 N，求它受到的浮力", "阿基米德原理"),
    # 英语（选项里的 "/" 不能被误判成分式）
    ("用 in / on / at 填空：We have English class ___ Monday morning.", "介词"),
    ("选择正确的词：The movie is very ___ . (interested / interesting)", "形容词辨析"),
    ("选择正确的词：___ you like some tea? (Would / Do)", "情景交际"),
    ("用所给词的适当形式填空：She ___ (go) to school every day.", "一般现在时"),
    ("用所给词的适当形式填空：He ___ (watch) TV now.", "现在进行时"),
    ("用所给词的适当形式填空：He wants ___ (be) a doctor.", "动词不定式"),
])
def test_classify_knowledge_local(question, expected):
    assert K.classify_knowledge_local(question) == expected


def test_classify_local_unknown():
    assert K.classify_knowledge_local("") == "未分类"
    assert K.classify_knowledge_local("   ") == "未分类"
    assert K.classify_knowledge_local("完全看不出这是一道什么题 abc") == "未分类"


# ── 归一化（LLM 输出 → 规范知识点名）─────────────────────────────────
@pytest.mark.parametrize("raw,expected", [
    ("一元一次方程", "一元一次方程"),
    ("一元一次方程（解方程）", "一元一次方程"),
    (" 勾股定理。", "勾股定理"),
    ("未分类", "未分类"),
    ("数学", "未分类"),            # 学科名不是知识点 → 归一为未分类（不瞎猜）
    ("", "未分类"),
    ("这题我不会分", "未分类"),   # 整句废话 → 未分类
    ("一元二次不等式", "未分类"),  # 不在 61 类已知表 → 保守落未分类
])
def test_normalize(raw, expected):
    assert K._normalize(raw) == expected


# ── LLM 分类 + 本地兜底 ─────────────────────────────────────────────
def _fake_chat_ok(messages, backend=None):
    K.tutor_agent.LAST_TUTOR_TRACE = {"backend": "deepseek", "model": "deepseek-flash",
                                      "fallback": None, "latency_s": 0.5}
    return "因式分解"


def _fake_chat_unknown(messages, backend=None):
    K.tutor_agent.LAST_TUTOR_TRACE = {"backend": "deepseek", "model": "deepseek-flash",
                                      "fallback": None, "latency_s": 0.5}
    return "未分类"


def _fake_chat_error(messages, backend=None):
    raise RuntimeError("no network")


def test_classify_local_backend():
    label, trace = K.classify_knowledge("解方程：2x+3=11", backend="local")
    assert label == "一元一次方程"
    assert trace["kind"] == "local"


def test_classify_llm_ok(monkeypatch):
    monkeypatch.setattr(K.tutor_agent, "chat", _fake_chat_ok)
    label, trace = K.classify_knowledge("因式分解：x²-9", backend="deepseek")
    assert label == "因式分解"
    assert trace["kind"] == "llm"
    assert trace["fallback"] is None


def test_classify_llm_unknown_falls_back_local(monkeypatch):
    monkeypatch.setattr(K.tutor_agent, "chat", _fake_chat_unknown)
    label, trace = K.classify_knowledge("解方程：2x+3=11", backend="deepseek")
    assert label == "一元一次方程"      # 本地兜底兜住
    assert trace["fallback"] is not None


def test_classify_llm_error_falls_back_local(monkeypatch):
    monkeypatch.setattr(K.tutor_agent, "chat", _fake_chat_error)
    label, trace = K.classify_knowledge("因式分解：x²-9", backend="deepseek")
    assert label == "因式分解"
    assert "LLM 不可用" in trace["fallback"]


def test_classify_empty():
    label, trace = K.classify_knowledge("")
    assert label == "未分类"
    assert trace["kind"] == "empty"
