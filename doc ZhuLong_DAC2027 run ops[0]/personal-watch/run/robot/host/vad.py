#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 端侧 VAD（Voice Activity Detection）纯函数模块

依据 INTERACTION_SPEC.md §9（VAD 端侧·必须）+ 11:55 令硬指标：
  - 端点判定 = 静音 >= 1.2s（「说完 -> 判定"说完" <=600ms」目标；此处给确定性逻辑）
  - 打断（barge-in）：speak 态检测到有效人声 -> 停播（<=300ms 为真机目标，此处保逻辑正确）
  - 误触发抑制：debounce（连续 N 帧能量超阈才算 speech，单帧尖峰不算）
  - 静音真关麦：muted 时丢弃全部音频、不触发任何检测（「静音必须真关麦」）
  - 自听自激规避：TTS 播放期间由上层切半双工（speak 态不喂入自身回声），本模块只提供状态机

设计：纯函数 + 零第三方依赖（输入 = 浮点样本序列），真机/模拟器/单测三处复用。
"""
from __future__ import annotations

import math
from dataclasses import dataclass, field
from enum import Enum


def rms(samples) -> float:
    """均方根能量。空序列返回 0.0。"""
    if not samples:
        return 0.0
    n = len(samples)
    return math.sqrt(sum(s * s for s in samples) / n)


def rms_db(samples, ref: float = 1.0) -> float:
    """RMS 转 dBFS（ref=1.0 时 0dB = 满量程）。纯静音返回 -100.0。"""
    r = rms(samples)
    if r <= 0.0:
        return -100.0
    return 20.0 * math.log10(r / ref)


class SessionState(str, Enum):
    """INTERACTION_SPEC §3 状态机（常听 + 四态 + 静音）。"""
    AMBIENT = "ambient"            # 常听·待机
    LISTEN = "listen"              # 听
    THINK = "think"                # 想
    SPEAK = "speak"                # 说
    WAIT_STUDENT = "wait_student"  # 等学生
    MUTED = "muted"                # 静音（麦克风真关闭）


@dataclass
class EndpointDetector:
    """端点判定：连续语音后静音 >= silence_ms（默认 1200ms）判定「说完」。"""
    silence_ms: float = 1200.0
    frame_ms: float = 30.0
    threshold_db: float = -40.0
    _silence_accum_ms: float = field(default=0.0, init=False)
    _heard_speech: bool = field(default=False, init=False)

    def reset(self) -> None:
        self._silence_accum_ms = 0.0
        self._heard_speech = False

    def feed(self, samples) -> bool:
        """喂一帧，返回是否刚判定端点（说完）。"""
        db = rms_db(samples)
        if db >= self.threshold_db:
            self._heard_speech = True
            self._silence_accum_ms = 0.0
            return False
        if self._heard_speech:
            self._silence_accum_ms += self.frame_ms
            if self._silence_accum_ms >= self.silence_ms:
                self.reset()
                return True
        return False


@dataclass
class BargeInDetector:
    """打断检测：语音超阈连续 min_frames 帧 -> 判定打断（debounce 防误触发）。

    hangover_ms：语音结束后的「保持有语音」时长，避免句间短暂停顿漏检。
    """
    threshold_db: float = -40.0
    min_frames: int = 2
    frame_ms: float = 30.0
    hangover_ms: float = 200.0
    _consecutive: int = field(default=0, init=False)
    _hangover_left_ms: float = field(default=0.0, init=False)

    def reset(self) -> None:
        self._consecutive = 0
        self._hangover_left_ms = 0.0

    def feed(self, samples) -> bool:
        """喂一帧，返回是否应打断。"""
        db = rms_db(samples)
        if db >= self.threshold_db:
            self._consecutive += 1
            self._hangover_left_ms = self.hangover_ms
            return self._consecutive >= self.min_frames
        if self._hangover_left_ms > 0.0:
            self._hangover_left_ms -= self.frame_ms
            if self._hangover_left_ms <= 0.0:
                self._consecutive = 0
        else:
            self._consecutive = 0
        return False


class MuteGate:
    """静音门：muted=True 时丢弃所有输入、不产生任何检测结果（真关麦语义）。"""

    def __init__(self) -> None:
        self.muted = False

    def set(self, muted: bool) -> None:
        self.muted = muted

    def pass_frame(self, samples):
        """返回 (allowed, samples)。muted 时返回 (False, [])。"""
        if self.muted:
            return False, []
        return True, samples


class SessionController:
    """把 VAD 结果映射到 INTERACTION_SPEC 状态机，并给出打断/端点决策。

    纯逻辑，不碰音频 IO；真机/模拟器把每帧样本喂进来即可。
    状态流转（含 11:55 令「常听 ambient 默认态」）：

        ambient --检测到人声--> listen --静音>=1.2s(端点)--> think --首步就绪--> speak
        speak --学生抢话(<=300ms)--> listen
        speak --说完--> wait_student --(3s 无输入)--> ambient
        任意态 --静音--> muted（真关麦）
    """

    def __init__(self, threshold_db: float = -40.0, silence_ms: float = 1200.0,
                 frame_ms: float = 30.0, barge_min_frames: int = 2):
        self.threshold_db = threshold_db
        self.frame_ms = frame_ms
        self.state = SessionState.AMBIENT
        self.endpoint = EndpointDetector(silence_ms=silence_ms, frame_ms=frame_ms,
                                         threshold_db=threshold_db)
        self.barge = BargeInDetector(threshold_db=threshold_db, frame_ms=frame_ms,
                                     min_frames=barge_min_frames)
        self.gate = MuteGate()
        self.events = []  # 最近事件（供单测断言）

    # ── 外部可驱动的动作 ────────────────────────────────────────────────
    def set_muted(self, muted: bool) -> None:
        """静音：真关麦（丢弃后续所有帧），解除则回 ambient。"""
        self.gate.set(muted)
        self.state = SessionState.MUTED if muted else SessionState.AMBIENT
        self.endpoint.reset()
        self.barge.reset()
        self.events.append("mute" if muted else "unmute")

    def start_speaking(self) -> None:
        """进入 speak 态（TTS 开始），复位打断检测。静音态下忽略。"""
        if self.state == SessionState.MUTED:
            return
        self.state = SessionState.SPEAK
        self.barge.reset()

    def finish_speaking(self) -> None:
        """说完 -> wait_student。"""
        if self.state == SessionState.SPEAK:
            self.state = SessionState.WAIT_STUDENT

    def timeout_to_ambient(self) -> None:
        """wait_student 3s 无输入 -> 回 ambient。"""
        self.state = SessionState.AMBIENT
        self.endpoint.reset()

    # ── 每帧喂入 ────────────────────────────────────────────────────────
    def feed(self, samples) -> dict:
        """喂一帧样本，返回事件（可能为空）。按当前状态分派。"""
        allowed, samples = self.gate.pass_frame(samples)
        if not allowed:
            return {"event": None, "state": self.state}

        # ambient：检测到人声 -> 进入 listen（不说话不算一轮）
        if self.state == SessionState.AMBIENT:
            if rms_db(samples) >= self.threshold_db:
                self.state = SessionState.LISTEN
                self.endpoint.reset()
                self.endpoint.feed(samples)  # 触发帧本身也算「已听到语音」
                return {"event": "listen_start", "state": self.state}
            return {"event": None, "state": self.state}

        # listen：静音 >= 1.2s -> 端点 -> think
        if self.state == SessionState.LISTEN:
            if self.endpoint.feed(samples):
                self.state = SessionState.THINK
                return {"event": "endpoint", "state": self.state}
            return {"event": None, "state": self.state}

        # speak：学生抢话 -> 打断 -> listen（丢弃在途回复）
        if self.state == SessionState.SPEAK:
            if self.barge.feed(samples):
                self.state = SessionState.LISTEN
                self.endpoint.reset()
                return {"event": "barge_in", "state": self.state}
            return {"event": None, "state": self.state}

        # think / wait_student 不消费 VAD
        return {"event": None, "state": self.state}
