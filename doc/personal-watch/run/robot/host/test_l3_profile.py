#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""l3_profile.py 单测（ROADMAP L3：知识点画像 + 每日/每周摘要 + 可导出 HTML）。"""
import json
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import l3_profile as LP  # noqa: E402


def _items():
    return [
        {"question": "解方程：2x+3=11", "student_answer": "x=5",
         "knowledge": "一元一次方程", "ts": "2026-11-07 20:00:00"},
        {"question": "解方程：3x-5=10", "student_answer": "x=6",
         "knowledge": "一元一次方程", "ts": "2026-11-08 09:30:00"},
        {"question": "解方程：5(x-2)=3x+6", "student_answer": "x=7",
         "knowledge": "一元一次方程", "ts": "2026-11-08 10:00:00"},
        {"question": "因式分解：x²-9", "student_answer": "x(x-3)",
         "knowledge": "因式分解", "ts": "2026-11-08 10:05:00"},
    ]


# ── 掌握等级 ────────────────────────────────────────────────────────
def test_mastery_label_bands():
    assert LP.mastery_label(0) == "待练习"
    assert LP.mastery_label(1) == "待巩固"
    assert LP.mastery_label(2) == "薄弱"
    assert LP.mastery_label(3) == "重点突破"
    assert LP.mastery_label(10) == "重点突破"


# ── 时间归一 ────────────────────────────────────────────────────────
def test_day_of_formats():
    assert LP._day_of("2026-11-07 20:00:00") == "2026-11-07"
    assert LP._day_of("2026-11-08 09:30") == "2026-11-08"
    assert LP._day_of("2026-11-09") == "2026-11-09"
    assert LP._day_of("") == ""
    assert LP._day_of("garbage") == ""


def test_week_of():
    # 2026-11-08 是周日（ISO 周），归属 2026-W45
    w = LP._week_of("2026-11-08 10:00:00")
    assert w.startswith("2026-W")
    assert LP._week_of("") == ""


# ── 知识点画像 ──────────────────────────────────────────────────────
def test_knowledge_profile_aggregation():
    prof = LP.knowledge_profile(_items())
    assert prof["total_wrong"] == 4
    # 一元一次方程错 3 题 → 重点突破，排第一
    assert prof["knowledge_points"][0]["knowledge"] == "一元一次方程"
    assert prof["knowledge_points"][0]["wrong_count"] == 3
    assert prof["knowledge_points"][0]["mastery"] == "重点突破"
    # 因式分解错 1 题 → 待巩固
    fx = [p for p in prof["knowledge_points"] if p["knowledge"] == "因式分解"][0]
    assert fx["wrong_count"] == 1 and fx["mastery"] == "待巩固"
    # 首末次时间
    assert prof["knowledge_points"][0]["first_ts"] == "2026-11-07 20:00:00"
    assert prof["knowledge_points"][0]["last_ts"] == "2026-11-08 10:00:00"


def test_knowledge_profile_weak_points():
    prof = LP.knowledge_profile(_items())
    weak = {p["knowledge"] for p in prof["weak_points"]}
    assert "一元一次方程" in weak       # 错 3 题 >= 2
    assert "因式分解" not in weak       # 错 1 题 < 2


def test_knowledge_profile_unknown_knowledge():
    prof = LP.knowledge_profile([{"question": "q", "student_answer": "a", "ts": "2026-11-07 08:00:00"}])
    assert prof["total_wrong"] == 1
    assert prof["knowledge_points"][0]["knowledge"] == "未分类"


def test_empty_profile():
    prof = LP.knowledge_profile([])
    assert prof["total_wrong"] == 0
    assert prof["knowledge_points"] == []
    assert prof["weak_points"] == []


# ── 每日 / 每周摘要 ─────────────────────────────────────────────────
def test_daily_summary():
    d = LP.daily_summary(_items())
    assert d["total_days"] == 2
    by_date = {x["date"]: x["wrong_count"] for x in d["days"]}
    assert by_date["2026-11-07"] == 1
    assert by_date["2026-11-08"] == 3


def test_weekly_summary():
    w = LP.weekly_summary(_items())
    assert w["total_weeks"] == 1
    assert w["weeks"][0]["wrong_count"] == 4
    assert w["weeks"][0]["week"].startswith("2026-W")


def test_daily_summary_ignores_bad_ts():
    d = LP.daily_summary([{"question": "q", "student_answer": "a", "ts": "bad"}])
    assert d["total_days"] == 0
    assert d["days"] == []


# ── HTML / 报告 ─────────────────────────────────────────────────────
def test_build_profile_html_self_contained():
    html = LP.build_profile_html(_items())
    assert "<!DOCTYPE html>" in html
    assert "家教学习画像" in html
    assert "一元一次方程" in html
    assert "重点突破" in html
    # 不泄露最终答案
    assert "x=4" not in html and "x=6" not in html
    # 不含学生错答原文（隐私：student_answer 不进报告）
    assert "x(x-3)" not in html


def test_profile_report_writes_file(tmp_path):
    p = str(tmp_path / "profile.html")
    rep = LP.profile_report(out_path=p, wrong_path=_write(tmp_path, _items()))
    assert rep["total_wrong"] == 4
    assert rep["knowledge_count"] == 2
    assert os.path.isfile(p)
    with open(p, encoding="utf-8") as f:
        assert "<!DOCTYPE html>" in f.read()


def test_profile_report_empty(tmp_path):
    rep = LP.profile_report(out_path=str(tmp_path / "empty.html"),
                            wrong_path=str(tmp_path / "nope.json"))
    assert rep["total_wrong"] == 0
    assert rep["weak_points"] == []


def _write(tmp_path, items):
    p = str(tmp_path / "wrong_book.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False)
    return p
