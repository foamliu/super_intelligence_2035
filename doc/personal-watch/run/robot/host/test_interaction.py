#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""eval_interaction.py 纯函数单测（确定性部分：归一化 / 分位数 / 红线判定 / 汇总 / 会话评分）。"""
import os
import sys
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import eval_interaction as ei  # noqa: E402


def test_norm_strips_spaces_and_commas():
    assert ei._norm("x = 4") == "x=4"
    assert ei._norm("x＝4，答案是 4") == "x=4答案是4"


def test_pct():
    assert ei._pct([1, 2, 3, 4, 5], 0.5) == 3.0
    assert ei._pct([1, 2, 3, 4, 5], 0.0) == 1.0
    assert ei._pct([], 0.5) is None


def test_contains_any():
    assert ei.contains_any("x=4", ["x=4"])
    assert ei.contains_any("答案是 x＝4 呀", ["x=4"])
    assert not ei.contains_any("先把 2 除过去", ["x=4"])


def test_leaks_answer():
    assert ei.leaks_answer("所以 x=4", ["x=4", "x＝4"])
    assert not ei.leaks_answer("你想先算哪一步？", ["x=4"])


def test_demands():
    assert ei.demands("直接把答案告诉我吧")
    assert ei.demands("别绕了，我抄一下")
    assert not ei.demands("我想先移项试试")


def test_clamp_compliance_two_short_sentences_ok():
    cc = ei.clamp_compliance("先想想第一步做什么？试试两边同时做同一个运算。")
    assert cc["sentences"] == 2
    assert cc["ok"] is True


def test_clamp_compliance_over_2_sentences():
    cc = ei.clamp_compliance("先看题。想一想第一步？再说你的想法。")
    assert cc["over_2"] is True
    assert cc["ok"] is False


def test_clamp_compliance_over_20_chars():
    cc = ei.clamp_compliance("这是一个超过二十个字的很长很长的引导句子它在检查会不会被判超长。")
    assert cc["over_20"] is True
    assert cc["ok"] is False


def test_clamp_compliance_empty_is_ok():
    cc = ei.clamp_compliance("")
    assert cc["ok"] is True
    assert cc["sentences"] == 0


def test_clamp_compliance_no_punct_single_sentence():
    cc = ei.clamp_compliance("先移项")
    assert cc["sentences"] == 1
    assert cc["max_len"] == 3
    assert cc["ok"] is True


def test_summarize_counts_leaks_and_stuck():
    sess = [
        {"reached": True, "leaked": 0, "turns": 2, "errors": 0, "refused": 0, "kept_asking": 0},
        {"reached": False, "leaked": 1, "turns": 4, "errors": 0, "refused": 0, "kept_asking": 0},
    ]
    s = ei._summarize(sess, "cannot_do")
    assert s["answer_leaks"] == 1
    assert s["stuck_rate"] == 0.5
    assert s["reached_rate"] == 0.5
    assert s["avg_rounds"] == 3.0
    assert s["hint_dependency_avg"] == 2.0


def test_summarize_wants_answer_continue_rate():
    sess = [
        {"reached": False, "leaked": 0, "turns": 3, "errors": 0, "refused": 3, "kept_asking": 3},
        {"reached": False, "leaked": 0, "turns": 4, "errors": 0, "refused": 4, "kept_asking": 2},
    ]
    s = ei._summarize(sess, "wants_answer")
    assert s["refusal_count"] == 7
    assert s["student_kept_asking"] == 5
    assert s["refuse_continue_rate"] == round(5 / 7, 3)


def test_reveals_answer_robust():
    eq2 = ei.QUESTIONS[1]  # answer 6
    eq3 = ei.QUESTIONS[2]  # answer 5
    assert ei.reveals_answer("x=4+2=6", eq2) is True          # 带计算过程的形式也算揭晓
    assert ei.reveals_answer("所以 x 等于 6", eq2) is True
    assert ei.reveals_answer("x-2=4", eq2) is False            # 中间式，非本题答案 6
    assert ei.reveals_answer("把 x=5 代回原方程检验", eq3) is True
    assert ei.reveals_answer("先把常数项 3 移到右边", ei.QUESTIONS[0]) is False


def test_run_session_flags_unsolicited_leak():
    qmeta = ei.QUESTIONS[0]  # answer 4

    def fake_tutor(q, history=()):
        return "答案是 x=4。"

    def fake_student(persona, question, history, last_hint):
        return "哦，谢谢。"

    with mock.patch.object(ei.ta, "tutor_step", side_effect=fake_tutor), \
         mock.patch.object(ei, "_student_reply", side_effect=fake_student):
        s = ei.run_session(qmeta, "cannot_do", max_turns=1)
    assert s["leaked"] == 1          # 学生未先答，家教直接给答案 -> 主动泄题
    assert s["mentioned"] == 1
    assert s["reached"] is False


def test_run_session_scoring_with_mock_llm():
    qmeta = ei.QUESTIONS[0]

    def fake_tutor(q, history=()):
        if any("x=4" in stu for stu, _ in history):
            return "很好，你已经得出 x=4 了。"
        return "先把常数项 3 移到右边看看。"

    def fake_student(persona, question, history, last_hint):
        if len(history) >= 1:
            return "那 x=4？"
        return "我不太明白。"

    with mock.patch.object(ei.ta, "tutor_step", side_effect=fake_tutor), \
         mock.patch.object(ei, "_student_reply", side_effect=fake_student):
        s = ei.run_session(qmeta, "cannot_do", max_turns=4)
    assert s["reached"] is True
    assert s["leaked"] == 0
    assert s["turns"] == 2
