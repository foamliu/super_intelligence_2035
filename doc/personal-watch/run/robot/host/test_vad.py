#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""vad.py 单测：端侧 VAD 纯逻辑（能量/端点 1.2s/打断 debounce/静音真关麦/状态机）。"""
import math

import pytest

from vad import (rms, rms_db, SessionState, EndpointDetector, BargeInDetector,
                 MuteGate, SessionController)

FRAME = 480  # 30ms @ 16kHz


def silence():
    return [0.0] * FRAME


def loud(amp=0.5):
    return [amp] * FRAME


# ── 能量 ────────────────────────────────────────────────────────────────
def test_rms_empty_is_zero():
    assert rms([]) == 0.0


def test_rms_db_silence_is_floor():
    assert rms_db(silence()) == -100.0


def test_rms_db_loudness_ordering():
    assert rms_db(loud(0.5)) > rms_db(loud(0.01)) > rms_db(silence())


def test_rms_db_amplitude_halving_is_minus_6db():
    assert math.isclose(rms_db(loud(1.0)) - rms_db(loud(0.5)), 6.0206, abs_tol=0.01)


# ── 端点判定（静音 1.2s）────────────────────────────────────────────────
def test_endpoint_not_before_1200ms():
    det = EndpointDetector(silence_ms=1200.0, frame_ms=30.0, threshold_db=-40.0)
    det.feed(loud())
    for _ in range(39):  # 1170ms 静音，不够 1200ms
        assert det.feed(silence()) is False


def test_endpoint_at_1200ms():
    det = EndpointDetector(silence_ms=1200.0, frame_ms=30.0, threshold_db=-40.0)
    det.feed(loud())
    for _ in range(39):
        det.feed(silence())
    assert det.feed(silence()) is True  # 第 40 帧 = 1200ms


def test_endpoint_requires_speech_first():
    det = EndpointDetector(silence_ms=1200.0, frame_ms=30.0)
    for _ in range(100):
        assert det.feed(silence()) is False  # 全程静音，永不判端点


# ── 打断 debounce ───────────────────────────────────────────────────────
def test_barge_in_single_spike_rejected():
    det = BargeInDetector(threshold_db=-40.0, min_frames=2, frame_ms=30.0)
    assert det.feed(loud()) is False  # 单帧尖峰，min_frames=2 不触发


def test_barge_in_two_consecutive_frames():
    det = BargeInDetector(threshold_db=-40.0, min_frames=2, frame_ms=30.0)
    det.feed(loud())
    assert det.feed(loud()) is True


def test_barge_in_hangover_bridges_short_gap():
    det = BargeInDetector(threshold_db=-40.0, min_frames=2, frame_ms=30.0, hangover_ms=200.0)
    det.feed(loud())
    det.feed(silence())          # 句间停顿（hangover 内）
    assert det.feed(loud()) is True  # hangover 保持，第 2 帧语音即打断


def test_barge_in_resets_after_long_silence():
    det = BargeInDetector(threshold_db=-40.0, min_frames=2, frame_ms=30.0, hangover_ms=200.0)
    det.feed(loud())
    for _ in range(10):
        det.feed(silence())  # 300ms 静音 > hangover，连续计数归零
    assert det.feed(loud()) is False  # 重新从 0 计数，不打断


# ── 静音真关麦 ──────────────────────────────────────────────────────────
def test_mute_gate_blocks():
    g = MuteGate()
    assert g.pass_frame(loud()) == (True, loud())
    g.set(True)
    allowed, samples = g.pass_frame(loud())
    assert allowed is False and samples == []


# ── 状态机 ──────────────────────────────────────────────────────────────
def _full_listen_path(c):
    """ambient -> listen -> endpoint(think)。"""
    assert c.feed(loud())["event"] == "listen_start"
    for _ in range(39):
        c.feed(silence())
    assert c.feed(silence())["event"] == "endpoint"
    assert c.state == SessionState.THINK


def test_state_machine_happy_path():
    c = SessionController()
    assert c.state == SessionState.AMBIENT
    _full_listen_path(c)
    c.start_speaking()
    assert c.state == SessionState.SPEAK
    c.finish_speaking()
    assert c.state == SessionState.WAIT_STUDENT
    c.timeout_to_ambient()
    assert c.state == SessionState.AMBIENT


def test_state_machine_barge_in_returns_to_listen():
    c = SessionController()
    _full_listen_path(c)
    c.start_speaking()
    c.feed(loud())
    ev = c.feed(loud())
    assert ev["event"] == "barge_in"
    assert c.state == SessionState.LISTEN


def test_state_machine_muted_blocks_all_and_unmutes():
    c = SessionController()
    c.set_muted(True)
    assert c.state == SessionState.MUTED
    # muted 态下喂响亮帧也不产生任何事件、状态不变
    assert c.feed(loud())["event"] is None
    assert c.feed(loud())["state"] == SessionState.MUTED
    c.start_speaking()  # 静音态下被忽略
    assert c.state == SessionState.MUTED
    c.set_muted(False)
    assert c.state == SessionState.AMBIENT


def test_state_machine_ambient_ignores_noise():
    c = SessionController()
    assert c.feed(silence())["event"] is None
    assert c.state == SessionState.AMBIENT  # 不说话不算一轮
