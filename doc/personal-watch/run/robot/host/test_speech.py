#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""speech.py 单测（逻辑正确性；硬时延真机复测）。跑法：py -3.10 -m pytest test_speech.py -q"""
import os

import pytest

import speech
from speech import (asr_stream, split_sentences, stop, reset_stop, tts_stream,
                    MockStreamingASR, CloudASR, CloudTTS, SherpaOnnxASR,
                    StreamingSherpaOnnxASR, load_wav_mono, synthesize_to_wav)


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


def test_sherpa_missing_model_raises(tmp_path):
    """模型缺失时构造必须报明确错误，不静默（无参默认目录在本机存在时另测真实识别）。"""
    with pytest.raises(RuntimeError):
        SherpaOnnxASR(model_dir=str(tmp_path / "no_such_dir"))


# ── WAV 读取 / 重采样（端侧 ASR 输入预处理）─────────────────────────────────
def test_load_wav_mono_16k(tmp_path):
    import numpy as np
    import wave
    wav = str(tmp_path / "t.wav")
    sr = 16000
    x = (np.sin(2 * np.pi * 440 * np.arange(sr) / sr) * 20000).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(x.tobytes())
    samples, out_sr = load_wav_mono(wav)
    assert out_sr == 16000
    assert samples.dtype == np.float32
    assert samples.ndim == 1
    assert len(samples) == sr


def test_load_wav_mono_resamples_48k_to_16k(tmp_path):
    import numpy as np
    import wave
    wav = str(tmp_path / "t48.wav")
    sr = 48000
    x = (np.sin(2 * np.pi * 440 * np.arange(sr) / sr) * 20000).astype(np.int16)
    with wave.open(wav, "wb") as w:
        w.setnchannels(2)
        w.setsampwidth(2)
        w.setframerate(sr)
        w.writeframes(np.column_stack([x, x]).reshape(-1).tobytes())
    samples, out_sr = load_wav_mono(wav)
    assert out_sr == 16000
    assert abs(len(samples) - sr // 3) <= 2  # 48k -> 16k 约 1/3 长度


# ── 端侧真实 ASR（模型在场时端到端；无模型时 skip）──────────────────────────
_MODEL_DIR = r"C:\Android\asr-models\paraformer-zh"


@pytest.mark.skipif(not (os.path.isfile(os.path.join(_MODEL_DIR, "model.int8.onnx"))
                          and os.path.isfile(os.path.join(_MODEL_DIR, "tokens.txt"))),
                    reason="端侧 ASR 模型未下载完整（host/README.md §ASR）")
def test_sherpa_real_transcribe(tmp_path):
    asr = SherpaOnnxASR(model_dir=_MODEL_DIR, num_threads=2)
    wav = str(tmp_path / "t.wav")
    synthesize_to_wav("负二加五等于三。", wav)
    text = asr.transcribe_file(wav)
    assert isinstance(text, str) and len(text.strip()) > 0


# ── 端侧真流式 ASR（streaming zipformer transducer）────────────────────────
_STREAMING_MODEL_DIR = r"C:\Android\asr-models\streaming-zipformer-zh-14M"


def test_streaming_sherpa_missing_model_raises(tmp_path):
    with pytest.raises(RuntimeError):
        StreamingSherpaOnnxASR(model_dir=str(tmp_path / "no_such_dir"))


@pytest.mark.skipif(not os.path.isfile(os.path.join(_STREAMING_MODEL_DIR, "encoder-epoch-99-avg-1.int8.onnx")),
                    reason="端侧流式 ASR 模型未下载（host/README.md §ASR）")
def test_streaming_sherpa_real(tmp_path):
    asr = StreamingSherpaOnnxASR(model_dir=_STREAMING_MODEL_DIR, num_threads=2)
    wav = str(tmp_path / "t.wav")
    synthesize_to_wav("等腰三角形的两个底角相等。", wav)
    text = asr.transcribe_file(wav)
    assert isinstance(text, str) and len(text.strip()) > 0


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
