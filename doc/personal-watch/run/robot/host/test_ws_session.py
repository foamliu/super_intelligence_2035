#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ws_session.py 单测：WebSocket 流式会话编排核心（状态机 / 流式 TTS 分句 / 打断 / 静音真关麦 / 多轮上下文）。

确定性：注入 mock tutor_fn，不联网、不 IO。
"""
import os
import sys

import pytest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from vad import SessionState  # noqa: E402
import ws_session  # noqa: E402
from ws_session import TutorSession, MOCK_HINT  # noqa: E402


def _sess(tutor_fn=None, split_fn=None):
    return TutorSession(tutor_fn=tutor_fn or (lambda q, h=(): MOCK_HINT),
                        split_fn=split_fn or ws_session.speech.split_sentences)


def _types(msgs):
    return [m.get("type") for m in msgs]


# ── 控制类 ──────────────────────────────────────────────────────────────
def test_hello_returns_state():
    s = _sess()
    msgs = s.handle_control({"type": "hello"})
    assert msgs == [{"type": "state", "state": "ambient", "sid": "anon",
                     "ts": pytest.approx(msgs[0]["ts"])}]
    assert s.state == SessionState.AMBIENT


def test_mute_true_mute_then_blocks_input():
    s = _sess()
    assert s.handle_control({"type": "mute"})[0]["state"] == "muted"
    # muted 态下 asr_partial 不产生 listen、不回显
    assert s.handle_control({"type": "asr_partial", "text": "帮我看看"}) == []
    assert s.handle_control({"type": "audio_chunk", "data": "AAAA"}) == []
    assert s.state == SessionState.MUTED


def test_unmute_returns_ambient():
    s = _sess()
    s.handle_control({"type": "mute"})
    assert s.handle_control({"type": "unmute"})[0]["state"] == "ambient"


def test_reset_clears_context():
    s = _sess()
    s.begin_turn_sync("解方程：2x+3=11")
    assert s.question and s.step == 1
    assert s.handle_control({"type": "reset"})[0]["state"] == "ambient"
    assert s.question == "" and s.history == [] and s.step == 0


def test_unknown_type_errors():
    s = _sess()
    msgs = s.handle_control({"type": "wat"})
    assert msgs[0]["type"] == "error"


def test_audio_chunk_counts_bytes():
    s = _sess()
    s.handle_control({"type": "audio_chunk", "data": "abcd"})
    s.handle_control({"type": "audio_chunk", "data": "ef"})
    assert s.audio_bytes_received == 6


# ── 免唤醒：asr_partial 检测到人声 -> listen ─────────────────────────────
def test_asr_partial_from_ambient_goes_listen():
    s = _sess()
    msgs = s.handle_control({"type": "asr_partial", "text": "2x加3"})
    assert _types(msgs) == ["state", "asr"]
    assert msgs[0]["state"] == "listen"
    assert msgs[1]["text"] == "2x加3" and msgs[1]["is_final"] is False


def test_asr_partial_empty_is_ignored():
    s = _sess()
    assert s.handle_control({"type": "asr_partial", "text": "  "}) == []
    assert s.state == SessionState.AMBIENT


# ── 一轮生成（think -> hint -> speak -> 分句 -> wait_student -> done）────
def test_begin_turn_happy_path():
    s = _sess()
    msgs = s.begin_turn_sync("解方程：2x+3=11")
    assert _types(msgs) == ["state", "hint", "state"]
    assert msgs[0]["state"] == "think"
    assert msgs[1]["reply_text"] == MOCK_HINT
    assert msgs[1]["step"] == 1 and msgs[1]["hint_level"] == 1
    assert msgs[2]["state"] == "speak"
    assert s.question == "解方程：2x+3=11"
    assert s.is_speaking is True


def test_begin_turn_sets_question_only_once_and_builds_history():
    s = _sess()
    s.begin_turn_sync("解方程：2x+3=11")
    s.begin_turn_sync("我把3移到右边")
    assert s.question == "解方程：2x+3=11"      # 题干不变
    assert s.history == [("我把3移到右边", MOCK_HINT)]
    assert s.step == 2


def test_stream_two_sentences_then_done():
    s = _sess()
    s.begin_turn_sync("解方程：2x+3=11")
    sents = []
    done = None
    while True:
        msgs = s.next_sentence()
        for m in msgs:
            if m["type"] == "tts_sentence":
                sents.append(m["text"])
            elif m["type"] == "done":
                done = m
        if done is not None:
            break
    assert sents == ["我们先不急着算。", "你觉得第一步该动哪一项？"]
    assert done["type"] == "done"
    assert s.state == SessionState.WAIT_STUDENT
    assert s.is_speaking is False


def test_tts_sentence_index_total():
    s = _sess()
    s.begin_turn_sync("q")
    first = s.next_sentence()
    assert first[0]["index"] == 1 and first[0]["total"] == 2
    second = s.next_sentence()
    assert second[0]["index"] == 2 and second[0]["total"] == 2


# ── 打断（barge-in）─────────────────────────────────────────────────────
def test_barge_in_drops_inflight_and_goes_listen():
    s = _sess()
    s.begin_turn_sync("q")
    s.next_sentence()  # 已发第 1 句，剩第 2 句在途
    assert s.is_speaking is True
    msgs = s.barge_in()
    assert _types(msgs) == ["stopped", "state"]
    assert msgs[0] == {"type": "stopped", "reason": "barge_in"}
    assert msgs[1]["state"] == "listen"
    assert s.is_speaking is False
    assert s._queued == []  # 在途剩余句已丢弃


def test_barge_in_when_idle_is_noop():
    s = _sess()
    msgs = s.barge_in()
    assert msgs[0]["type"] == "state" and msgs[0]["state"] == "ambient"


# ── 异常路径 ────────────────────────────────────────────────────────────
def test_begin_turn_empty_text_errors():
    s = _sess()
    msgs = s.begin_turn_sync("   ")
    assert msgs[0]["type"] == "error"


def test_begin_turn_tutor_failure_is_explicit():
    def _boom(q, h=()):
        raise RuntimeError("LLM 不可用")
    s = _sess(tutor_fn=_boom)
    msgs = s.begin_turn_sync("q")
    assert _types(msgs) == ["state", "error", "state"]
    assert "LLM 不可用" in msgs[1]["message"]
    assert msgs[2]["state"] == "wait_student"
    assert s.is_speaking is False


# ── idle 超时：wait_student 3s 无输入 -> ambient ─────────────────────────
def test_idle_timeout_returns_to_ambient():
    s = _sess()
    s.begin_turn_sync("q")
    while s.is_speaking:
        s.next_sentence()
    assert s.state == SessionState.WAIT_STUDENT
    msgs = s.idle_timeout()
    assert msgs[0]["state"] == "ambient"


def test_idle_timeout_noop_outside_wait_student():
    s = _sess()
    assert s.idle_timeout()[0]["state"] == "ambient"
