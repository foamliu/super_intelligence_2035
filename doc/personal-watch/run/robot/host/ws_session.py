#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · WebSocket 流式会话服务（11:40 令 §5 #2「WebSocket 流式会话服务」+ 11:55 令「连续对话/免唤醒」）

补齐此前唯一未交付的用户令代码项：此前 `tutor_server.py` 只有 HTTP（POST /tutor 等），
本模块提供**双向流式**会话端点，把 INTERACTION_SPEC §3 状态机 / §6 打断 / §9 语音链路落到
一条长连接上。HTTP 端点仍在 `tutor_server.py`，两者并存（本模块 = WS，不破坏 POST /tutor）。

对照 INTERACTION_SPEC：
  - 会话状态机：复用 `vad.SessionState`（ambient/listen/think/speak/wait_student/muted），
    任一时刻只处一态，状态每次流转都作为 `state` 消息下行（§2.3「状态可见」）。
  - 流式 ASR 接入位：上行 `asr_partial`（中间结果·屏幕同步）/ `asr_final`（端点判定后的最终转写）
    / `audio_chunk`（原始 PCM b64，服务端侧 ASR 的预留接入位，暂只计字节）。
  - 流式 TTS 分句：服务端把引导按句切分（`speech.split_sentences`），逐句下行 `tts_sentence`，
    App 逐句朗读，句间停顿（默认 250ms，见 §9）。
  - 打断协议（barge-in）：`speak` 态收到 `barge_in` -> 立即停播 + 丢弃在途剩余句 + 翻转 `listen`
    （§6「打断 <=300ms」为真机目标，本模块保证协议正确 + 丢弃在途回复）。
  - 静音真关麦：`mute` -> `muted`（丢弃后续所有输入，`audio_chunk`/`asr_*` 一律不处理）。
  - 常听 ambient：上电即 ambient，`asr_partial` 检测到人声 -> listen（免唤醒，11:55 令）。
  - wait_student 3s 无输入 -> 自动回 ambient（§3「不追问轰炸」）。

协议（JSON 文本帧，utf-8）：
  上行（客户端 -> 服务端）：
    {"type":"hello"}                                  握手 -> 回 state + meta
    {"type":"asr_partial","text":"..."}               流式 ASR 中间结果
    {"type":"asr_final","text":"..."}                 端点判定的最终转写 -> 触发一轮 think->speak
    {"type":"audio_chunk","data":"<b64 pcm16 16k mono>"}  原始音频接入位（预留）
    {"type":"barge_in"}                               学生抢话 -> 停播
    {"type":"mute"} / {"type":"unmute"}               静音真关麦 / 解除
    {"type":"reset"}                                  回 ambient（清历史/题干）
  下行（服务端 -> 客户端）：
    {"type":"state","state":"...","sid":...,"ts":...} 状态可见
    {"type":"meta","version":...,"vision":...,"tutor":...}
    {"type":"asr","text":"...","is_final":false}       ASR 回显
    {"type":"hint","reply_text","tts_text","step","hint_level","latency_s"}
    {"type":"tts_sentence","text","index","total","latency_s"}   逐句下行
    {"type":"done","latency_s"}
    {"type":"stopped","reason":"barge_in"}
    {"type":"error","message"}

运行：
  py -3.10 ws_session.py                    # 默认 ws://0.0.0.0:8766（真实 DeepSeek 引导）
  py -3.10 ws_session.py --mock             # 确定性 mock 引导（演示/评测，不联网）
"""
from __future__ import annotations

import asyncio
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import speech       # noqa: E402  split_sentences / StreamingSherpaOnnxASR（流式 ASR 接入位）
import tutor_agent  # noqa: E402  tutor_step（分步引导，默认云端 DeepSeek + 本机 ollama 兜底）
import websockets   # noqa: E402  WebSocket 服务端/客户端（异步层）
from vad import SessionState  # noqa: E402  会话状态机枚举（INTERACTION_SPEC §3）

WS_PORT = int(os.environ.get("ROBOT_WS_PORT", "8766"))
WS_HOST = os.environ.get("ROBOT_WS_HOST", "0.0.0.0")
INTER_SENTENCE_PAUSE_MS = int(os.environ.get("ROBOT_WS_PAUSE_MS", "250"))
IDLE_TO_AMBIENT_MS = int(os.environ.get("ROBOT_WS_IDLE_MS", "3000"))
HISTORY_LIMIT = int(os.environ.get("ROBOT_WS_HISTORY", "12"))

# 确定性 mock 引导（演示/评测用，不联网、不泄答案，符合 INTERACTION_SPEC §2「一次只推进一步」）
MOCK_HINT = "我们先不急着算。你觉得第一步该动哪一项？"


def _mock_tutor(question: str, history=()) -> str:
    """确定性 mock 引导：两句话、每句 ≤20 字，不含最终答案（红线安全）。"""
    return MOCK_HINT


class TutorSession:
    """WebSocket 会话编排核心（同步、无 IO、可确定性单测）。

    把上行协议消息映射到 INTERACTION_SPEC 状态机 + 一轮「think -> 分句 TTS -> wait_student」。
    真实网络/LLM 在 `WsTutorServer` 层处理，本类保持纯逻辑、注入 `tutor_fn` 即可测。
    """

    def __init__(self, tutor_fn=None, split_fn=None, sid: str = "anon",
                 history_limit: int = HISTORY_LIMIT):
        self.sid = sid
        self._tutor = tutor_fn if tutor_fn is not None else tutor_agent.tutor_step
        self._split = split_fn if split_fn is not None else speech.split_sentences
        self.history_limit = history_limit

        self.state = SessionState.AMBIENT
        self.history = []          # [(学生话, 上一步引导), ...]，多轮上下文
        self.question = ""         # 本轮题干（首个 asr_final 建立）
        self.step = 0              # 引导步数（每生成一步 +1）
        self.hint_level = 1
        self._last_hint = ""
        self._last_latency_s = 0.0

        # 流式 TTS 分句在途状态
        self._queued = []          # 待逐句下发的句子
        self._total_sentences = 0
        self._sent_count = 0
        self._speaking = False

        # 原始音频接入位累计字节（预留服务端侧 ASR，暂不转写）
        self.audio_bytes_received = 0

    # ── 状态辅助 ────────────────────────────────────────────────────────
    @property
    def is_speaking(self) -> bool:
        return self._speaking

    def _state_msg(self) -> dict:
        return {"type": "state", "state": self.state.value, "sid": self.sid,
                "ts": round(time.time(), 3)}

    def _set(self, state: SessionState) -> dict:
        self.state = state
        return self._state_msg()

    def _drop_inflight(self) -> None:
        """丢弃在途回复（打断/静音时调用）。"""
        self._queued = []
        self._speaking = False

    # ── 控制类消息（hello / mute / unmute / reset / asr_partial / audio_chunk / barge_in）──
    def handle_control(self, msg: dict) -> list:
        t = (msg or {}).get("type")
        if t == "hello":
            return [self._state_msg()]
        # 静音真关麦：muted 态丢弃所有输入类消息（仅 unmute/reset 可改变状态，见 11:55 令 §1.5）
        if self.state == SessionState.MUTED and t in ("asr_partial", "audio_chunk", "barge_in"):
            return []
        if t == "mute":
            self._drop_inflight()
            return [self._set(SessionState.MUTED)]
        if t == "unmute":
            return [self._set(SessionState.AMBIENT)]
        if t == "reset":
            self._drop_inflight()
            self.history = []
            self.question = ""
            self.step = 0
            self.hint_level = 1
            self._last_hint = ""
            return [self._set(SessionState.AMBIENT)]
        if t == "asr_partial":
            return self._on_asr_partial((msg or {}).get("text", ""))
        if t == "audio_chunk":
            return self._on_audio_chunk((msg or {}).get("data", ""))
        if t == "barge_in":
            return self.barge_in()
        return [{"type": "error", "message": "未知消息类型: %r" % t}]

    def _on_asr_partial(self, text: str) -> list:
        text = (text or "").strip()
        if not text:
            return []
        out = []
        # 免唤醒：ambient / wait_student 下检测到人声 -> listen（11:55 令）
        if self.state in (SessionState.AMBIENT, SessionState.WAIT_STUDENT):
            out.append(self._set(SessionState.LISTEN))
        out.append({"type": "asr", "text": text, "is_final": False})
        return out

    def _on_audio_chunk(self, data: str) -> list:
        """原始音频接入位：只累计字节（真机/PC 流式 ASR 见 speech.StreamingSherpaOnnxASR）。"""
        self.audio_bytes_received += len(data or "")
        return []

    def barge_in(self) -> list:
        """打断：停播 + 丢弃在途剩余句 + 翻转 listen（§6）。非 speak 态为幂等空操作。"""
        if self._speaking:
            self._drop_inflight()
            return [{"type": "stopped", "reason": "barge_in"},
                    self._set(SessionState.LISTEN)]
        if self.state == SessionState.SPEAK:
            return [self._set(SessionState.LISTEN)]
        return [self._state_msg()]

    def idle_timeout(self) -> list:
        """wait_student 3s 无输入 -> 回 ambient（§3「不追问轰炸」）。"""
        if self.state == SessionState.WAIT_STUDENT:
            return [self._set(SessionState.AMBIENT)]
        return [self._state_msg()]

    # ── 一轮生成（同步，分步下发）──────────────────────────────────────
    def begin_turn_sync(self, text: str) -> list:
        """`asr_final` -> think -> 生成引导 -> speak。返回 [state think, hint, state speak]。

        同步方法（内部调 `tutor_fn`，可能走网络），由上层放入 executor 跑，避免阻塞事件循环。
        """
        text = (text or "").strip()
        if not text:
            return [{"type": "error", "message": "空转写，无法开始一轮"}]

        # 首轮：以学生转写建立题干；后续轮：把 (学生本轮话, 上一步引导) 记入多轮上下文
        if not self.question:
            self.question = text
        else:
            if self._last_hint:
                self.history.append((text, self._last_hint))
            self.history = self.history[-self.history_limit:]

        t0 = time.time()
        out = [self._set(SessionState.THINK)]
        try:
            hint = self._tutor(self.question, self.history)
        except Exception as e:  # noqa: BLE001  引导失败要显式报，不静默
            self._drop_inflight()
            out.append({"type": "error", "message": "引导生成失败: %s" % str(e)[:200]})
            out.append(self._set(SessionState.WAIT_STUDENT))
            return out

        hint = (hint or "").strip()
        self._last_hint = hint
        self._last_latency_s = round(time.time() - t0, 3)
        self.step += 1
        self._queued = self._split(hint)
        self._total_sentences = len(self._queued)
        self._sent_count = 0
        self._speaking = bool(self._queued)

        out.append({"type": "hint", "reply_text": hint, "tts_text": hint,
                    "step": self.step, "hint_level": self.hint_level,
                    "latency_s": self._last_latency_s})
        out.append(self._set(SessionState.SPEAK))
        return out

    def next_sentence(self) -> list:
        """下发下一句 TTS 句子；句队列空 -> wait_student + done。返回下行消息列表。"""
        if self._queued:
            self._sent_count += 1
            text = self._queued.pop(0)
            return [{"type": "tts_sentence", "text": text,
                     "index": self._sent_count, "total": self._total_sentences,
                     "latency_s": self._last_latency_s}]
        self._speaking = False
        return [self._set(SessionState.WAIT_STUDENT),
                {"type": "done", "latency_s": self._last_latency_s}]

# ── WebSocket 异步服务层 ────────────────────────────────────────────────
async def _sender(ws, outq: asyncio.Queue) -> None:
    """唯一写 ws 的任务（websockets 不允许并发 send），从 outq 逐条下发。"""
    while True:
        m = await outq.get()
        if m is None:
            break
        await ws.send(json.dumps(m, ensure_ascii=False))


async def _stream_turn(outq: asyncio.Queue, sess: TutorSession, text: str,
                       pause_ms: int, stop_evt: asyncio.Event) -> None:
    """异步下发一轮：begin_turn（executor 里跑同步 LLM）-> 逐句 tts_sentence，句间可被打断。

    打断由主循环（barge_in 分支）作为唯一 emitter 处理（stop_evt.set() + sess.barge_in()），
    本任务只负责在 stop 被置位时尽快退出、不再下发任何在途句，避免重复/竞态。
    """
    loop = asyncio.get_running_loop()
    for m in await loop.run_in_executor(None, sess.begin_turn_sync, text):
        if stop_evt.is_set():
            return
        await outq.put(m)
    while True:
        for m in sess.next_sentence():
            if m.get("type") == "done":
                await outq.put(m)
                return
            if stop_evt.is_set():
                return
            await outq.put(m)
        # 还有下一句 -> 句间停顿（期间可被 barge_in 打断）
        try:
            await asyncio.wait_for(stop_evt.wait(), timeout=pause_ms / 1000.0)
            return
        except asyncio.TimeoutError:
            pass



class WsTutorServer:
    """WebSocket 流式会话服务（asyncio）。每个连接一个 TutorSession。"""

    def __init__(self, host: str = WS_HOST, port: int = WS_PORT,
                 tutor_fn=None, split_fn=None,
                 pause_ms: int = INTER_SENTENCE_PAUSE_MS,
                 idle_ms: int = IDLE_TO_AMBIENT_MS):
        self.host = host
        self.port = port
        self.tutor_fn = tutor_fn
        self.split_fn = split_fn
        self.pause_ms = pause_ms
        self.idle_ms = idle_ms
        self.server = None

    async def _handler(self, ws) -> None:
        sess = TutorSession(tutor_fn=self.tutor_fn, split_fn=self.split_fn, sid=str(ws.id))
        outq = asyncio.Queue()
        sender = asyncio.create_task(_sender(ws, outq))
        stop_evt = asyncio.Event()
        turn_task = None
        try:
            # 握手：回 state + meta（后端可见，不静默）
            await outq.put(sess._state_msg())
            await outq.put({"type": "meta", "version": "1.0",
                            "vision": tutor_agent.VISION_BACKEND,
                            "tutor": tutor_agent.TUTOR_BACKEND,
                            "pause_ms": self.pause_ms, "idle_ms": self.idle_ms})
            while True:
                # wait_student 态 3s 无输入 -> 自动回 ambient（不追问轰炸）
                timeout = (self.idle_ms / 1000.0) if sess.state == SessionState.WAIT_STUDENT else None
                try:
                    raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
                except asyncio.TimeoutError:
                    for m in sess.idle_timeout():
                        await outq.put(m)
                    continue
                except websockets.exceptions.ConnectionClosed:
                    break  # 客户端正常/异常断开，静默退出（不打印 handler failed）

                msg = json.loads(raw)
                t = (msg or {}).get("type")
                if t == "asr_final":
                    if sess.state == SessionState.MUTED:
                        continue  # 静音真关麦：丢弃输入
                    # 新一轮：若仍在说，先打断旧轮再开新轮
                    if turn_task and not turn_task.done():
                        stop_evt.set()
                        await asyncio.gather(turn_task, return_exceptions=True)
                    stop_evt = asyncio.Event()
                    turn_task = asyncio.create_task(
                        _stream_turn(outq, sess, msg.get("text", ""), self.pause_ms, stop_evt))
                elif t == "barge_in":
                    stop_evt.set()
                    for m in sess.barge_in():
                        await outq.put(m)
                else:
                    for m in sess.handle_control(msg):
                        await outq.put(m)
        finally:
            if turn_task and not turn_task.done():
                stop_evt.set()
                await asyncio.gather(turn_task, return_exceptions=True)
            await outq.put(None)
            await sender

    async def start(self) -> None:
        self.server = await websockets.serve(self._handler, self.host, self.port)
        print("robot ws session server listening on ws://%s:%d" % (self.host, self.port))
        print("  App 端访问宿主机用 ws://10.0.2.2:%d" % self.port)
        print("  后端：vision=%s tutor=%s" % (tutor_agent.VISION_BACKEND, tutor_agent.TUTOR_BACKEND))
        print("  句间停顿=%dms  idle->ambient=%dms" % (self.pause_ms, self.idle_ms))

    async def serve_forever(self) -> None:
        await self.start()
        await self.server.wait_closed()


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="robot 线 · WebSocket 流式会话服务")
    ap.add_argument("--host", default=WS_HOST)
    ap.add_argument("--port", type=int, default=WS_PORT)
    ap.add_argument("--pause-ms", type=int, default=INTER_SENTENCE_PAUSE_MS)
    ap.add_argument("--idle-ms", type=int, default=IDLE_TO_AMBIENT_MS)
    ap.add_argument("--mock", action="store_true",
                    help="用确定性 mock 引导（演示/评测，不联网）")
    args = ap.parse_args()

    srv = WsTutorServer(host=args.host, port=args.port,
                        tutor_fn=_mock_tutor if args.mock else None,
                        pause_ms=args.pause_ms, idle_ms=args.idle_ms)
    try:
        asyncio.run(srv.serve_forever())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
