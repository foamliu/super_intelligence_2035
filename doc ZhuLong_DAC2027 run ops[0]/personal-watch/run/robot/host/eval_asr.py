#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 端侧 ASR 实测（12:20 令 §5 + ROADMAP「下一轮候选」#1）

链路：SAPI TTS 合成「已知文本」的 48kHz WAV -> 端侧 ASR 识别 -> 与真值逐字比对，
算 CER（字错率）。两套引擎（在场才跑，缺失则标注 skip）：

  - offline   `speech.SherpaOnnxASR`          sherpa-onnx paraformer 中文离线（模型 243MB）
  - streaming `speech.StreamingSherpaOnnxASR` sherpa-onnx streaming-zipformer 中文流式（模型 31MB）

输出：`eval/asr_paraformer_zh.json`（离线）/ `eval/asr_streaming_zipformer_zh.json`（流式）。

能信/不能信（16:5x 令）：测的是「端侧离线识别能否落地 + 合成语音的回读字错率」，
属 PC 端真实推理证据；真机麦克风近场 CER 待真机复测（麦克风/AEC 不在本链路内）。
"""
import json
import os
import re
import time

import speech

# 自然中文 + 简单数学口述（SAPI 友好、可被 TTS 稳定朗读）
_CASES = [
    ("我们先把三移到右边看看。", "easy"),
    ("等腰三角形的两个底角相等。", "easy"),
    ("先合并同类项，再移项。", "easy"),
    ("这一步移项是对的。", "easy"),
    ("负二加五等于三。", "easy"),
    ("你打算先处理哪一项。", "easy"),
    ("x的平方加三x等于零。", "hard"),
    ("二分之根号三。", "hard"),
]

OUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "eval")
_PARA_DIR = r"C:\Android\asr-models\paraformer-zh"
_STREAM_DIR = r"C:\Android\asr-models\streaming-zipformer-zh-14M"


def _norm(text: str) -> str:
    """CER 归一化：去空白与标点，保留 CJK/ASCII 字母/数字。"""
    return re.sub(r"[^\u4e00-\u9fffA-Za-z0-9]", "", text or "")


def char_error_rate(ref: str, hyp: str) -> float:
    """字符级编辑距离 CER（Levenshtein）。"""
    ref = _norm(ref)
    hyp = _norm(hyp)
    if not ref:
        return 0.0 if not hyp else 1.0
    m, n = len(ref), len(hyp)
    prev = list(range(n + 1))
    for i in range(1, m + 1):
        cur = [i] + [0] * n
        for j in range(1, n + 1):
            cur[j] = min(
                prev[j] + 1,
                cur[j - 1] + 1,
                prev[j - 1] + (0 if ref[i - 1] == hyp[j - 1] else 1),
            )
        prev = cur
    return prev[n] / m


def _run_engine(name, engine, out_wav_dir):
    """engine: 有 transcribe_file() 的对象。返回 summary dict。"""
    results = []
    total_cer = 0.0
    for idx, (ref, tag) in enumerate(_CASES):
        wav = os.path.join(out_wav_dir, "%s_%02d.wav" % (name, idx))
        speech.synthesize_to_wav(ref, wav)
        t0 = time.time()
        hyp = engine.transcribe_file(wav)
        dt = time.time() - t0
        cer = char_error_rate(ref, hyp)
        total_cer += cer
        results.append({
            "id": idx, "ref": ref, "hyp": hyp,
            "cer": round(cer, 4), "latency_s": round(dt, 3), "tag": tag, "wav": wav,
        })
        print("[%s][%02d] %s\n        ref=%r\n        hyp=%r  CER=%.3f  %.3fs" % (name, idx, tag, ref, hyp, cer, dt))
    n = len(results)
    easy = [r["cer"] for r in results if r["tag"] == "easy"]
    return {
        "engine": name,
        "cases": n,
        "mean_cer": round(total_cer / n, 4),
        "easy_mean_cer": round(sum(easy) / max(1, len(easy)), 4),
        "results": results,
    }


def _dump(summary, filename):
    out = os.path.join(OUT_DIR, filename)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print("\n[%s] mean_cer=%.4f  easy_mean_cer=%.4f -> %s" % (
        summary["engine"], summary["mean_cer"], summary["easy_mean_cer"], out))


def main():
    out_wav_dir = os.path.join(OUT_DIR, "asr_wavs")
    os.makedirs(out_wav_dir, exist_ok=True)

    if os.path.isfile(os.path.join(_PARA_DIR, "model.int8.onnx")) and os.path.isfile(os.path.join(_PARA_DIR, "tokens.txt")):
        print("== 离线 paraformer ==")
        eng = speech.SherpaOnnxASR(model_dir=_PARA_DIR, num_threads=4)
        _dump(_run_engine("paraformer", eng, out_wav_dir), "asr_paraformer_zh.json")
    else:
        print("== 离线 paraformer 模型未就绪，跳过（%s）==" % _PARA_DIR)

    if os.path.isfile(os.path.join(_STREAM_DIR, "encoder-epoch-99-avg-1.int8.onnx")):
        print("\n== 流式 zipformer ==")
        eng = speech.StreamingSherpaOnnxASR(model_dir=_STREAM_DIR, num_threads=2)
        _dump(_run_engine("streaming_zipformer", eng, out_wav_dir), "asr_streaming_zipformer_zh.json")

        # 流式中间结果演示（第 1 条 easy case）
        ref0 = _CASES[0][0]
        wav0 = os.path.join(out_wav_dir, "stream_demo.wav")
        speech.synthesize_to_wav(ref0, wav0)
        print("\n== 流式中间结果演示（%s）==" % ref0)
        for ev in eng.stream(wav0, chunk_ms=400):
            print("   ", ev)
    else:
        print("\n== 流式 zipformer 模型未就绪，跳过（%s）==" % _STREAM_DIR)


if __name__ == "__main__":
    main()
