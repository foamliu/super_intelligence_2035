#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 语音链路适配层（12:20 用户令 §2/§3 + INTERACTION_SPEC.md §9 定稿）

统一接口（端侧实现为默认，云端留空实现）：
  asr_stream()   流式 ASR（端侧默认；PC 上默认 mock 流式转写，真机替换 sherpa-onnx / Core Speech Kit）
  tts_stream()   分句流式 TTS（端侧默认 Windows SAPI；句间停顿；可被 stop() 打断）
  stop()         打断：停播 + 丢弃在途回复（INTERACTION_SPEC §6，<=300ms 为真机目标，这里保 PC 逻辑正确）

口径（12:20 令）：
  - VAD / ASR / TTS 一律【端侧为主】，🚫 不引入云端语音（CloudASR/CloudTTS 只留空实现，默认 off）。
  - TTS 首字 / ASR 出字等【硬时延】在 PC 上只能测「逻辑正确性」，真机数值待真机复测（16:5x 令「能信/不能信」）。

PC 端侧事实：
  - Windows SAPI `Huihui` = 中文女声，离线免费；无音频设备（headless）时 `synthesize_to_wav` 落盘恒可用。
  - 端侧真实 ASR = `SherpaOnnxASR`（sherpa-onnx paraformer 中文离线模型，16kHz）：`transcribe_file()` 一次性识别，
    `stream()` 按块前缀增量模拟流式中间结果；模型缺失/未装时构造报明确错误，不静默。
"""
import os
import re
import threading
import time

# ── 打断控制（模块级：任意线程调 stop() 都能打断 tts_stream/asr_stream）──────
_STOP_EVENT = threading.Event()
_ACTIVE_VOICE = {"sp": None}  # 当前正在朗读的 SAPI voice，供 stop() 立即 purge


def stop() -> None:
    """打断：置停止标志 + 立即清空 SAPI 播放队列（若在播）。幂等。"""
    _STOP_EVENT.set()
    sp = _ACTIVE_VOICE.get("sp")
    if sp is not None:
        try:
            # SVSFPurgeBeforeSpeak=2：清空待播内容，立即停
            sp.Speak("", 2)
        except Exception:  # noqa: BLE001
            pass


def reset_stop() -> None:
    """新一轮开始前复位打断标志。"""
    _STOP_EVENT.clear()


# ── 分句（TTS 按句流式，句间 250ms 停顿，见 INTERACTION_SPEC §9）──────────────
_SENT_SPLIT = re.compile(r"(?<=[。！？；!?;\n])")


def split_sentences(text: str):
    """按句切分并保留句末标点。空句丢弃。"""
    parts = _SENT_SPLIT.split(text or "")
    return [p.strip() for p in parts if p and p.strip()]


def _sapi_voice():
    """惰性初始化 SAPI voice（Huihui 中文女声），返回 SpVoice。"""
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    sp = win32com.client.Dispatch("SAPI.SpVoice")
    for v in sp.GetVoices():
        if "Huihui" in v.GetAttribute("Name"):
            sp.Voice = v
            break
    return sp


def synthesize_to_wav(text: str, out_wav: str) -> str:
    """把一句文本合成 48kHz/16bit/立体声 WAV（headless 也恒可用，可证伪的「出声」产物）。"""
    import win32com.client
    sp = _sapi_voice()
    _ACTIVE_VOICE["sp"] = sp
    try:
        fs = win32com.client.Dispatch("SAPI.SpFileStream")
        try:
            fs.Format.Type = 39  # SAFT44kHz16BitStereo
        except Exception:  # noqa: BLE001
            pass
        fs.Open(out_wav, 3)  # SSFMCreateForWrite
        sp.AudioOutputStream = fs
        try:
            sp.Speak(text)
        finally:
            fs.Close()
            sp.AudioOutputStream = None
    finally:
        _ACTIVE_VOICE["sp"] = None
    return out_wav


def speak_to_device(text: str) -> None:
    """直接向音频设备朗读（headless 无设备时抛错，调用方按 12:20 令 §2.5 降级纯文字）。"""
    sp = _sapi_voice()
    _ACTIVE_VOICE["sp"] = sp
    try:
        sp.Speak(text)
    finally:
        _ACTIVE_VOICE["sp"] = None


def tts_stream(text: str, out_dir: str = None, on_sentence=None,
               inter_sentence_pause_ms: int = 250):
    """分句流式 TTS：逐句合成 WAV（可选）并回调 on_sentence(text, wav_path)；句间停顿。

    返回 dict：{sentences: n, wavs: [路径...], stopped: bool}。
    stop() 可打断：正在播的这句合成完后不再继续下一句（丢弃在途回复）。
    """
    reset_stop()
    sents = split_sentences(text)
    if out_dir:
        os.makedirs(out_dir, exist_ok=True)
    wavs = []
    stopped = False
    for i, sent in enumerate(sents):
        if _STOP_EVENT.is_set():
            stopped = True
            break
        wav_path = None
        if out_dir:
            wav_path = os.path.join(out_dir, "tts_%02d.wav" % i)
            synthesize_to_wav(sent, wav_path)
            wavs.append(wav_path)
        if on_sentence:
            on_sentence(sent, wav_path)
        if i < len(sents) - 1 and inter_sentence_pause_ms:
            time.sleep(inter_sentence_pause_ms / 1000.0)
    return {"sentences": len(sents), "wavs": wavs, "stopped": stopped}


# ── 流式 ASR ─────────────────────────────────────────────────────────────
class StreamingASR:
    """端侧流式 ASR 抽象：yield {"text", "is_final"}；端点=静音 1.2s（端侧 VAD）。"""

    def stream(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class MockStreamingASR(StreamingASR):
    """PC mock：把预先转写的句子逐字吐出，模拟「流式中间结果 + 最终结果」。

    用于在无端侧 ASR 时验证会话状态机 / 端点 / 打断的【逻辑正确性】（不是识别精度）。
    """

    def __init__(self, transcript: str = "", chunk_ms: int = 0):
        self.transcript = transcript or ""
        self.chunk_ms = chunk_ms
        self._stop = False

    def stream(self):
        self._stop = False
        for i in range(1, len(self.transcript) + 1):
            if self._stop:
                return
            yield {"text": self.transcript[:i], "is_final": False}
            if self.chunk_ms:
                time.sleep(self.chunk_ms / 1000.0)
        yield {"text": self.transcript, "is_final": True}

    def stop(self):
        self._stop = True


def load_wav_mono(wav_path: str):
    """读 WAV -> (float32 单声道 1-D numpy, 16000)。自动重采样到 16kHz（线性插值）。

    端侧 ASR 输入统一为 16kHz mono float32（sherpa-onnx 口径）。
    """
    import numpy as np
    import wave

    with wave.open(wav_path, "rb") as w:
        sr = w.getframerate()
        ch = w.getnchannels()
        sw = w.getsampwidth()
        raw = w.readframes(w.getnframes())

    if sw == 2:
        data = np.frombuffer(raw, dtype=np.int16).astype(np.float32) / 32768.0
    elif sw == 1:
        data = (np.frombuffer(raw, dtype=np.uint8).astype(np.float32) - 128.0) / 128.0
    else:
        raise ValueError("unsupported WAV sampwidth: %d" % sw)

    if ch > 1:
        data = data.reshape(-1, ch).mean(axis=1)

    if sr != 16000:
        data = _resample_linear(data, sr, 16000)
    return data.astype(np.float32), 16000


def _resample_linear(x, src_sr: int, dst_sr: int):
    import numpy as np

    n = len(x)
    if n == 0:
        return x
    t_new = np.arange(int(np.ceil(n * dst_sr / src_sr))) * (src_sr / dst_sr)
    t_new = np.clip(t_new, 0, n - 1)
    lo = np.floor(t_new).astype(np.int64)
    hi = np.minimum(lo + 1, n - 1)
    frac = (t_new - lo).astype(np.float32)
    return (x[lo] * (1.0 - frac) + x[hi] * frac).astype(np.float32)


class SherpaOnnxASR(StreamingASR):
    """端侧 sherpa-onnx **真实 ASR**（默认 paraformer 中文离线模型，16kHz）。

    - 模型目录：优先 `ROBOT_ASR_MODEL_DIR`，其次构造参数，最后 `C:\\Android\\asr-models\\paraformer-zh`。
    - 目录需含 `model.int8.onnx` + `tokens.txt`（下载见 `host/README.md` §ASR）。
    - 真机/HarmonyOS 上替换为 Core Speech Kit；本类提供 PC 端「端侧」真实识别与 CER 证据。
    """

    DEFAULT_MODEL_DIR = r"C:\Android\asr-models\paraformer-zh"

    def __init__(self, model_dir: str = None, num_threads: int = 2):
        d = (model_dir
             or os.environ.get("ROBOT_ASR_MODEL_DIR")
             or self.DEFAULT_MODEL_DIR)
        model = os.path.join(d, "model.int8.onnx")
        tokens = os.path.join(d, "tokens.txt")
        if not (os.path.isfile(model) and os.path.isfile(tokens)):
            raise RuntimeError(
                "端侧 sherpa-onnx 模型缺失：%s 需含 model.int8.onnx + tokens.txt；"
                "下载见 host/README.md §ASR" % d
            )
        try:
            import sherpa_onnx
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("端侧 sherpa-onnx 未安装：请 `pip install sherpa-onnx`") from e
        self.model_dir = d
        self._rec = sherpa_onnx.OfflineRecognizer.from_paraformer(
            paraformer=model,
            tokens=tokens,
            num_threads=num_threads,
            sample_rate=16000,
            feature_dim=80,
            decoding_method="greedy_search",
        )
        self._stop = False

    def transcribe(self, samples, sample_rate: int = 16000) -> str:
        """samples: float32 1-D numpy（mono）。返回识别文本。"""
        s = self._rec.create_stream()
        s.accept_waveform(sample_rate, samples)
        self._rec.decode_stream(s)
        return s.result.text.strip()

    def transcribe_file(self, wav_path: str) -> str:
        """读 WAV（自动转 16k mono）-> 识别文本。"""
        samples, sr = load_wav_mono(wav_path)
        return self.transcribe(samples, sr)

    def stream(self, wav_path: str = None, chunk_ms: int = 500):
        """流式接口：按块「前缀增量」识别，逐块 yield {"text","is_final"}。

        说明：paraformer 为离线模型，这里用「逐块加长再识别」模拟流式中间结果
        （非 OnlineRecognizer 真流式，真流式待接 streaming 模型，见 §9）。
        """
        if not wav_path:
            raise ValueError("SherpaOnnxASR.stream() 需要 wav_path")
        samples, sr = load_wav_mono(wav_path)
        n = len(samples)
        step = int(sr * chunk_ms / 1000.0)
        if step <= 0:
            step = n
        self._stop = False
        last = ""
        pos = step
        while pos < n:
            if self._stop:
                return
            text = self.transcribe(samples[:pos], sr)
            if text and text != last:
                last = text
                yield {"text": text, "is_final": False}
            pos += step
        text = self.transcribe(samples, sr) or last
        yield {"text": text, "is_final": True}

    def stop(self):
        self._stop = True


class StreamingSherpaOnnxASR(StreamingASR):
    """端侧 sherpa-onnx **真流式** ASR（streaming zipformer 中文 transducer，16kHz）。

    - 用 `OnlineRecognizer.from_transducer` 加载 encoder/decoder/joiner + tokens。
    - `stream(wav_path, chunk_ms=500)`：按块喂入，逐块 yield 增长中的**中间结果**
      （OnlineRecognizer 真流式 partial，非离线前缀模拟），最后 `is_final=True`。
    - 模型目录：优先 `ROBOT_STREAMING_ASR_MODEL_DIR`，其次构造参数，最后
      `C:\\Android\\asr-models\\streaming-zipformer-zh-14M`。
    - 模型缺失/未装时报明确错误，不静默。
    """

    DEFAULT_MODEL_DIR = r"C:\Android\asr-models\streaming-zipformer-zh-14M"

    def __init__(self, model_dir: str = None, num_threads: int = 2):
        d = (model_dir
             or os.environ.get("ROBOT_STREAMING_ASR_MODEL_DIR")
             or self.DEFAULT_MODEL_DIR)
        encoder = os.path.join(d, "encoder-epoch-99-avg-1.int8.onnx")
        decoder = os.path.join(d, "decoder-epoch-99-avg-1.onnx")
        joiner = os.path.join(d, "joiner-epoch-99-avg-1.int8.onnx")
        tokens = os.path.join(d, "tokens.txt")
        for f in (encoder, decoder, joiner, tokens):
            if not os.path.isfile(f):
                raise RuntimeError(
                    "端侧流式 ASR 模型缺失：%s 需含 encoder/decoder/joiner/tokens；"
                    "下载见 host/README.md §ASR" % f
                )
        try:
            import sherpa_onnx
        except ImportError as e:  # pragma: no cover
            raise RuntimeError("端侧 sherpa-onnx 未安装：请 `pip install sherpa-onnx`") from e
        self.model_dir = d
        self._rec = sherpa_onnx.OnlineRecognizer.from_transducer(
            tokens=tokens,
            encoder=encoder,
            decoder=decoder,
            joiner=joiner,
            num_threads=num_threads,
            sample_rate=16000,
            feature_dim=80,
            decoding_method="greedy_search",
        )
        self._stop = False

    def transcribe_file(self, wav_path: str) -> str:
        """一次性识别整段 WAV（内部仍走流式喂入 + input_finished），返回最终文本。"""
        samples, sr = load_wav_mono(wav_path)
        s = self._rec.create_stream()
        s.accept_waveform(sr, samples)
        s.input_finished()
        while self._rec.is_ready(s):
            self._rec.decode_stream(s)
        res = self._rec.get_result(s)
        return (res.text if hasattr(res, "text") else res).strip()

    def stream(self, wav_path: str = None, chunk_ms: int = 500):
        """真流式：按 chunk_ms 喂块，逐块 yield 增长中的中间结果，末块 is_final=True。"""
        if not wav_path:
            raise ValueError("StreamingSherpaOnnxASR.stream() 需要 wav_path")
        samples, sr = load_wav_mono(wav_path)
        n = len(samples)
        step = int(sr * chunk_ms / 1000.0)
        if step <= 0:
            step = n
        s = self._rec.create_stream()
        self._stop = False
        last = ""
        pos = 0
        while pos < n:
            if self._stop:
                s.input_finished()
                return
            s.accept_waveform(sr, samples[pos:pos + step])
            while self._rec.is_ready(s):
                self._rec.decode_stream(s)
            res = self._rec.get_result(s)
            text = (res.text if hasattr(res, "text") else res).strip()
            if text and text != last:
                last = text
                yield {"text": text, "is_final": False}
            pos += step
        s.input_finished()
        while self._rec.is_ready(s):
            self._rec.decode_stream(s)
        res = self._rec.get_result(s)
        text = (res.text if hasattr(res, "text") else res).strip() or last
        yield {"text": text, "is_final": True}

    def stop(self):
        self._stop = True


class CloudASR(StreamingASR):
    """云端 ASR 空实现（12:20 令：默认 off，🚫 不新增语音厂商账号）。"""

    def __init__(self):
        raise RuntimeError("云端语音默认关闭（12:20 令），不新增语音厂商账号。")


class CloudTTS:
    """云端 TTS 空实现（默认 off）。"""

    def __init__(self):
        raise RuntimeError("云端语音默认关闭（12:20 令），不新增语音厂商账号。")


def asr_stream(transcript: str = "", engine: StreamingASR = None, chunk_ms: int = 0):
    """统一入口：返回流式 ASR 生成器。默认 PC 端走 MockStreamingASR。"""
    reset_stop()
    eng = engine if engine is not None else MockStreamingASR(transcript, chunk_ms=chunk_ms)
    return eng.stream()


def main():
    """自测：分句 + 合成 WAV + 打断 + ASR mock。"""
    import tempfile
    text = "我们先不急着算。先回忆一下：等腰三角形里，两个底角之间有什么关系呢？"
    print("分句：", split_sentences(text))
    out = tempfile.mkdtemp(prefix="robot_tts_")
    print("合成结果：", tts_stream(text, out_dir=out))
    out2 = tempfile.mkdtemp(prefix="robot_tts2_")

    def _on(sent, wav):
        print("  [句] %s -> %s" % (sent, wav))
        if "底角" in sent:
            print("  [打断] 学生抢话 -> stop()")
            stop()

    print("打断结果：", tts_stream(text, out_dir=out2, on_sentence=_on))
    print("ASR 流式（mock）：")
    for ev in asr_stream("我想先移项", chunk_ms=0):
        print("  ", ev)


if __name__ == "__main__":
    main()
