#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""question_bank 题库完整性的单测（第 14 轮：100 题自造题库）。"""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "eval"))

import question_bank as qb  # noqa: E402


def test_total_100_questions():
    assert len(qb.QUESTION_BANK) == 100


def test_subject_distribution():
    from collections import Counter
    c = Counter(x["subject"] for x in qb.QUESTION_BANK)
    assert c == {"数学": 60, "物理": 20, "英语": 20}


def test_no_duplicate_ids():
    ids = [x["id"] for x in qb.QUESTION_BANK]
    assert len(ids) == len(set(ids))


def test_every_question_has_answer_and_leak():
    for x in qb.QUESTION_BANK:
        assert x.get("answer"), x["id"]
        assert x.get("leak"), x["id"]
        assert all(isinstance(p, str) for p in x["leak"]), x["id"]


def test_by_id_and_math_ids():
    assert len(qb.by_id()) == 100
    assert len(qb.math_ids()) == 60
    assert qb.math_ids()[:20] == ["m%03d" % i for i in range(1, 21)]
