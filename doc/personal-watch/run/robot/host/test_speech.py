#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""speech.py 单测（逻辑正确性；硬时延真机复测）。跑法：py -3.10 -m pytest test_speech.py -q"""
import os

import pytest

import speech
from speech import (asr_stream, split_sentences, stop, reset_stop, tts_stream,
                    MockStreamingASR, CloudASR, CloudTTS, SherpaOnnxASR)


# ── 分句 ────────────────────────────────────────────────────────────────
def test_split_sentences_basic():
    assert split_sentences("先想一步。再往下。") == ["先想一步。", "再往下。"]


def test_split_sentences_mixed_punct():
    parts = split_sentences("你看这一步对吗？继续。")
    assert parts == ["你看这一步对吗？", "继续。"]


def test_split_sentences_single():
    assert split_sentences("只有一个整句") == ["只有一个整句"]


def test_split_sentences_empty():
    assert split_sentences("") == []


# ── 打断标志（模块级 stop / reset_stop）──────────────────────────────────
def test_stop_flag_roundtrip():
    reset_stop()
    assert speech._STOP_EVENT.is_set() is False
    stop()
    assert speech._STOP_EVENT.is_set() is True
    reset_stop()
    assert speech._STOP_EVENT.is_set() is False


# ── 流式 ASR（mock）─────────────────────────────────────────────────────
def test_asr_stream_mock_partial_then_final():
    evs = list(asr_stream("移项", chunk_ms=0))
    # 逐字 partial + 最终 final
    assert evs[0] == {"text": "移", "is_final": False}
    assert evs[1] == {"text": "移项", "is_final": False}
    assert evs[-1] == {"text": "移项", "is_final": True}


def test_asr_stream_mock_stop():
    eng = MockStreamingASR("我想先移项")
    gen = eng.stream()
    got = []
    for i, ev in enumerate(gen):
        got.append(ev["text"])
        if i == 1:  # 第二个字符后打断
            eng.stop()
    # 打断后立即停止，不应吐完整句
    assert "我想先移项" not in got
    assert len(got) < len("我想先移项")


# ── 云端 / 端侧未装 接入位：明确报错，不静默 ───────────────────────────────
def test_cloud_asr_off():
    with pytest.raises(RuntimeError):
        CloudASR()


def test_cloud_tts_off():
    with pytest.raises(RuntimeError):
        CloudTTS()


def test_sherpa_stub_informative():
    with pytest.raises(RuntimeError):
        SherpaOnnxASR()


# ── TTS 分句流式 + 落盘产物（可证伪的「出声」）──────────────────────────────
def test_tts_stream_generates_wav(tmp_path):
    reset_stop()
    r = tts_stream("我们先不急着算。先回忆一下关系。", out_dir=str(tmp_path))
    assert r["sentences"] == 2
    assert r["stopped"] is False
    assert len(r["wavs"]) == 2
    for w in r["wavs"]:
        assert os.path.isfile(w)
        assert os.path.getsize(w) > 0


def test_tts_stream_interrupt_stops_remaining(tmp_path):
    reset_stop()
    seen = []

    def _on(sent, wav):
        seen.append(sent)
        if "不急着算" in sent:
            stop()  # 第一句播完就抢话

    r = tts_stream("我们先不急着算。先回忆一下关系。第三步要做什么。",
                   out_dir=str(tmp_path), on_sentence=_on, inter_sentence_pause_ms=0)
    assert r["stopped"] is True
    assert len(seen) == 1  # 只有第一句被播，其余被丢弃
