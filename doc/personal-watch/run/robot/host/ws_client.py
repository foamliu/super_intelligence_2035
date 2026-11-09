#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · WebSocket 流式会话参考客户端（演示 + 评测）

演示完整协议：握手 -> 免唤醒(asr_partial) -> 一轮(asr_final -> 流式 TTS) -> 打断(barge_in) -> 静音/解除。
评测：对 `--eval N` 跑 N 轮，实测 hint 时延 / 首句 TTS 下行时延 / 打断停播时延（P50/P90）。

用法：
  py -3.10 ws_client.py ws://127.0.0.1:8766 --demo
  py -3.10 ws_client.py ws://127.0.0.1:8766 --eval 10 --text "解方程：2x + 3 = 11" --out ../eval/ws_session.json
"""
from __future__ import annotations

import argparse
import asyncio
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


async def _recv_until(ws, pred, timeout: float = 30.0):
    """读消息直到 pred 命中，返回 (命中消息, 途中所有消息)。"""
    seen = []
    while True:
        raw = await asyncio.wait_for(ws.recv(), timeout=timeout)
        m = json.loads(raw)
        seen.append(m)
        if pred(m):
            return m, seen


async def _demo(uri: str, question: str) -> dict:
    import websockets
    ts = {}
    async with websockets.connect(uri, max_size=64 * 1024 * 1024) as ws:
        meta, _ = await _recv_until(ws, lambda m: m["type"] == "meta")
        print("[握手] %s" % json.dumps(meta, ensure_ascii=False))

        # 免唤醒：检测到人声 -> listen
        await ws.send(json.dumps({"type": "asr_partial", "text": "帮我看看这道题"},
                                 ensure_ascii=False))
        st, _ = await _recv_until(ws, lambda m: m["type"] == "state" and m["state"] == "listen")
        print("[免唤醒] %s" % st["state"])

        # 一轮：asr_final -> think -> hint -> 流式 TTS
        t0 = time.time()
        await ws.send(json.dumps({"type": "asr_final", "text": question}, ensure_ascii=False))
        hint, _ = await _recv_until(ws, lambda m: m["type"] == "hint")
        ts["hint_latency_s"] = round(time.time() - t0, 3)
        print("[引导] %ss step=%d | %s" % (hint["latency_s"], hint["step"], hint["reply_text"]))

        s1, _ = await _recv_until(ws, lambda m: m["type"] == "tts_sentence")
        print("[TTS %d/%d] %s" % (s1["index"], s1["total"], s1["text"]))

        # 打断：学生抢话 -> 停播 + 丢弃在途句 + 翻转 listen
        tb = time.time()
        await ws.send(json.dumps({"type": "barge_in"}))
        stopped, _ = await _recv_until(ws, lambda m: m["type"] == "stopped")
        ts["barge_in_stop_latency_s"] = round(time.time() - tb, 3)
        print("[打断] %ss %s" % (ts["barge_in_stop_latency_s"],
                                json.dumps(stopped, ensure_ascii=False)))
        lst, _ = await _recv_until(ws, lambda m: m["type"] == "state" and m["state"] == "listen")
        print("[状态] %s" % lst["state"])

        # 静音真关麦 / 解除
        await ws.send(json.dumps({"type": "mute"}))
        mut, _ = await _recv_until(ws, lambda m: m["type"] == "state" and m["state"] == "muted")
        await ws.send(json.dumps({"type": "unmute"}))
        unm, _ = await _recv_until(ws, lambda m: m["type"] == "state" and m["state"] == "ambient")
        print("[静音] %s -> [解除] %s" % (mut["state"], unm["state"]))
    return ts


async def _one_turn(ws, question: str) -> dict:
    """跑一轮完整 turn，返回 hint 时延 / 首句时延 / 完整句数。"""
    t0 = time.time()
    await ws.send(json.dumps({"type": "asr_final", "text": question}, ensure_ascii=False))
    hint, _ = await _recv_until(ws, lambda m: m["type"] == "hint")
    hint_lat = time.time() - t0
    t1 = time.time()
    n_sent = 0
    while True:
        m, _ = await _recv_until(ws, lambda x: x["type"] in ("tts_sentence", "done"))
        if m["type"] == "tts_sentence":
            if n_sent == 0:
                first_lat = time.time() - t1
            n_sent += 1
        else:
            break
    return {"hint_latency_s": round(hint_lat, 3),
            "first_tts_latency_s": round(first_lat, 3),
            "sentences": n_sent}


def _p50p90(vals):
    vals = sorted(vals)
    n = len(vals)
    return round(vals[int(n * 0.5)] if n else 0.0, 3), \
           round(vals[int(n * 0.9)] if n else 0.0, 3)


async def _eval(uri: str, question: str, rounds: int, out_path: str) -> dict:
    import websockets
    hints, firsts = [], []
    async with websockets.connect(uri, max_size=64 * 1024 * 1024) as ws:
        await _recv_until(ws, lambda m: m["type"] == "meta")
        for _ in range(rounds):
            r = await _one_turn(ws, question)
            hints.append(r["hint_latency_s"])
            firsts.append(r["first_tts_latency_s"])
    hp50, hp90 = _p50p90(hints)
    fp50, fp90 = _p50p90(firsts)
    result = {"rounds": rounds, "question": question,
              "hint_latency_p50_s": hp50, "hint_latency_p90_s": hp90,
              "first_tts_latency_p50_s": fp50, "first_tts_latency_p90_s": fp90,
              "hint_latency_raw": hints, "first_tts_latency_raw": firsts}
    if out_path:
        os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
    return result


def main() -> None:
    ap = argparse.ArgumentParser(description="robot 线 · WebSocket 流式会话参考客户端")
    ap.add_argument("uri", nargs="?", default="ws://127.0.0.1:8766")
    ap.add_argument("--demo", action="store_true", help="跑一遍完整协议演示")
    ap.add_argument("--eval", type=int, default=0, help="跑 N 轮实测时延")
    ap.add_argument("--text", default="解方程：2x + 3 = 11")
    ap.add_argument("--out", default=None, help="评测结果 JSON 输出路径")
    args = ap.parse_args()

    if args.demo:
        ts = asyncio.run(_demo(args.uri, args.text))
        print("\n== 实测时延 ==")
        print(json.dumps(ts, ensure_ascii=False, indent=2))
    elif args.eval > 0:
        r = asyncio.run(_eval(args.uri, args.text, args.eval, args.out))
        print(json.dumps(r, ensure_ascii=False, indent=2))
    else:
        asyncio.run(_demo(args.uri, args.text))


if __name__ == "__main__":
    main()
