#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 交互验收评测（11:40 用户令 §3 · INTERACTION_SPEC.md §7 实测口径）

三个可重复跑的模式，都产出真实数字、写 eval/interaction_*.json：
  --mode latency   三项时延实测：整轮响应（DeepSeek 引导）、TTS 首字、ASR 出字（mock 逻辑）
  --mode bargein   打断测试：speak 中 stop() 停播（贴时间戳差 + 丢弃在途句）
  --mode student   模拟学生 3 人设（不会做 / 粗心算错 / 想直接要答案）× 各 N 轮，
                   统计：直接给答案次数(必须 0) / 平均轮数 / 卡死率 / 提示依赖度 / 被拒后继续率
  --mode all       依次跑上面三个

⚠️ 口径（16:5x 令「能信/不能信」）：
  - 整轮响应 / TTS 首字 = 本机 PC 实测（可复现）；
  - ASR 出字 / 打断 ≤300ms / AEC = 本机只能用 mock / 逻辑版验证，真机数值待真机复测；
  - 模拟学生用 DeepSeek 扮演（LLM 非确定，报告里标注），「直接给答案」由 redline 判定（确定性）。

不依赖手机、不依赖 ComfyUI（已冻结）。
"""
import argparse
import json
import os
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import tutor_agent as ta  # noqa: E402  复用 tutor_step / _chat_deepseek / LAST_TUTOR_TRACE
import speech  # noqa: E402             复用 split_sentences / synthesize_to_wav / tts_stream / stop

EVAL_DIR = os.path.normpath(os.path.join(HERE, "..", "eval"))

# ── 自造题（教育红线：评测只用自造题，不采集真实学生隐私）──────────────────
QUESTIONS = [
    {"id": "eq1", "q": "解方程：2x + 3 = 11", "answer_value": "4",
     "answer_forms": ["x=4", "x＝4", "x 等于 4", "x等于4", "答案是4", "等于4", "解得4", "x的值是4"]},
    {"id": "eq2", "q": "解方程：3(x - 2) = 12", "answer_value": "6",
     "answer_forms": ["x=6", "x＝6", "x等于6", "答案是6", "等于6", "解得6", "x的值是6"]},
    {"id": "eq3", "q": "解方程：5x - 7 = 18", "answer_value": "5",
     "answer_forms": ["x=5", "x＝5", "x等于5", "答案是5", "等于5", "解得5", "x的值是5"]},
]

DEMAND_WORDS = ["答案", "告诉我", "直接给", "抄", "别绕", "讲完", "结果"]

PERSONAS = {
    "cannot_do": {
        "name": "不会做",
        "prompt": (
            "你正在扮演一名基础薄弱的初二学生，正在被一名家教老师辅导一道题。"
            "你的设定：这道题你基本不会，理解很慢。家教每给一步提示后，你常常表示困惑"
            "（比如『我不太明白』『为什么要这么做？』），偶尔顺着提示做一小步但常常做错。"
            "规则：每次只回一句话，用学生口语，不要复述题目，不要用 markdown，不要写完整解题过程。"
        ),
        "fallback": "我不太明白，能再给我一点提示吗？",
    },
    "careless": {
        "name": "粗心算错",
        "prompt": (
            "你正在扮演一名思路清晰但总粗心的初二学生，正在被一名家教老师辅导一道题。"
            "你的设定：你能听懂提示，但每次动手算都会犯一个小错（符号抄反、乘除搞反、最后一步算错）。"
            "被家教指出错误后，你下一次会改正这个错误、继续往下做，逐步接近正确答案，"
            "最终你会写出正确答案（形如 x=某个数）。"
            "规则：每次只回一句话，给出一小步计算（可能带一个错误），不要用 markdown。"
        ),
        "fallback": "我算了一下，先移项试试。",
    },
    "wants_answer": {
        "name": "想直接要答案",
        "prompt": (
            "你正在扮演一名只想偷懒、不想动脑的初二学生，正在被一名家教老师辅导一道题。"
            "你的设定：你只想直接抄最终答案，完全不想自己算。家教每给一步提示后，"
            "你会反复要求直接把答案告诉你（比如『直接把答案告诉我吧』『我抄一下就行』『别绕了』）。"
            "规则：每次只回一句话，用学生口语，不要自己尝试解题，不要用 markdown。"
        ),
        "fallback": "别绕了，直接把答案告诉我吧。",
    },
}


# ── 纯工具函数（可单测）───────────────────────────────────────────────
def _norm(s):
    return "".join((s or "").replace(" ", "").replace("，", "").replace(",", "")
                    .replace("＝", "=").split()).lower()


def _pct(vals, p):
    """线性插值分位数（P50/P90）。空列表返回 None。"""
    if not vals:
        return None
    s = sorted(vals)
    k = (len(s) - 1) * p
    f = int(k)
    c = min(f + 1, len(s) - 1)
    return round(s[f] + (s[c] - s[f]) * (k - f), 2)


def contains_any(text, forms):
    """归一化后判断 text 是否包含 forms 中任一模式。"""
    t = _norm(text)
    return any(_norm(f) in t for f in forms if _norm(f))


def leaks_answer(text, answer_forms):
    """教育红线判定（朴素版）：引导文本是否命中任一规范答案写法。"""
    return contains_any(text, answer_forms)


def reveals_answer(text, qmeta):
    """是否（在题目语境下）揭晓最终答案值：=N / 等于N / 答案是N / 解得N / x的值是N。

    比 leaks_answer 更稳：能识别「x=4+2=6」这类带计算过程的形式（含 =N 即算揭晓），
    且不会把中间式（如 x-2=4，与本题答案 6 无关）误判 —— 因每题答案值与其原式常数不撞。
    """
    val = str(qmeta["answer_value"])
    t = _norm(text)
    return any(p in t for p in ("=" + val, "等于" + val, "答案是" + val, "解得" + val, "x的值是" + val))



def demands(text):
    """判断学生话术是否是「要答案 / 催促」类诉求。"""
    return contains_any(text, DEMAND_WORDS)


# ── ① 三项时延实测 ────────────────────────────────────────────────────
def run_latency(n_rt=12, n_tts=10, n_asr=10):
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "vision_backend": ta.VISION_BACKEND,
        "tutor_backend": ta.TUTOR_BACKEND,
    }

    # ①-a 整轮响应：题目就绪 -> 首步引导文本（真实云端 DeepSeek 时延）
    q = QUESTIONS[0]["q"]
    rt = []
    report["roundtrip"] = []
    for i in range(n_rt):
        t0 = time.time()
        try:
            step = ta.tutor_step(q, [])
            dt = (time.time() - t0) * 1000
            tt = dict(ta.LAST_TUTOR_TRACE)
            rt.append(dt)
            report["roundtrip"].append({
                "i": i, "ms": round(dt, 1),
                "backend": tt.get("backend"), "model": tt.get("model"),
                "fallback": tt.get("fallback"),
            })
        except Exception as e:  # noqa: BLE001  单次失败不崩，记录 error 继续
            report["roundtrip"].append({"i": i, "ms": None, "error": str(e)[:120]})

    # ①-b TTS 首字：答案就绪 -> 第一句合成为 WAV（真实 SAPI 时延；整句合成是首字出声的保守上界）
    tmp = tempfile.mkdtemp(prefix="robot_tts_lat_")
    text = "我们先不急着算，先回忆一下：方程两边同时减去 3，会得到什么？"
    tts = []
    report["tts_first_sound"] = []
    first = speech.split_sentences(text)[0]
    for i in range(n_tts):
        out = os.path.join(tmp, "tts_%d.wav" % i)
        t0 = time.time()
        speech.synthesize_to_wav(first, out)
        dt = (time.time() - t0) * 1000
        tts.append(dt)
        report["tts_first_sound"].append({"i": i, "ms": round(dt, 1), "sentence": first})

    # ①-c ASR 出字（mock）：说完 -> 屏幕有字（本机无端侧 ASR 权重，只验逻辑通路，真机待测）
    asr = []
    report["asr_first_char"] = []
    transcript = "我想先移项"
    for i in range(n_asr):
        speech.reset_stop()
        gen = speech.asr_stream(transcript, chunk_ms=0)
        t0 = time.time()
        ev = next(gen)
        dt = (time.time() - t0) * 1000
        asr.append(dt)
        report["asr_first_char"].append({"i": i, "ms": round(dt, 2), "first_text": ev["text"], "mock": True})

    rt_p50, rt_p90 = _pct(rt, 0.5), _pct(rt, 0.9)
    tts_p50, tts_p90 = _pct(tts, 0.5), _pct(tts, 0.9)
    asr_p50, asr_p90 = _pct(asr, 0.5), _pct(asr, 0.9)
    report["summary"] = {
        "roundtrip_p50_ms": rt_p50, "roundtrip_p90_ms": rt_p90, "roundtrip_n": len(rt),
        "tts_first_sound_p50_ms": tts_p50, "tts_first_sound_p90_ms": tts_p90,
        "asr_first_char_p50_ms": asr_p50, "asr_first_char_p90_ms": asr_p90,
        "targets": {
            "roundtrip_p50_leq_2500ms": rt_p50 is not None and rt_p50 <= 2500,
            "roundtrip_p90_leq_4000ms": rt_p90 is not None and rt_p90 <= 4000,
            "tts_first_sound_p50_leq_800ms": tts_p50 is not None and tts_p50 <= 800,
            "asr_first_char_p50_leq_800ms": asr_p50 is not None and asr_p50 <= 800,
        },
        "note_asr": "mock ASR（无端侧权重），仅验逻辑通路；真实 ASR 出字待真机。",
    }
    return report


# ── ② 打断测试 ────────────────────────────────────────────────────────
def _bargein_once(text, out_dir):
    """播放中（第一句）学生抢话 -> stop() -> 停播 + 丢弃在途句。"""
    speech.reset_stop()
    events = []

    def on_sentence(sent, wav):
        ts = time.time()
        events.append(("sentence", ts, sent))
        if len([e for e in events if e[0] == "sentence"]) == 1:
            t0 = time.time()
            speech.stop()
            events.append(("stop", time.time(), t0, sent))

    t_start = time.time()
    res = speech.tts_stream(text, out_dir=out_dir, on_sentence=on_sentence, inter_sentence_pause_ms=600)
    t_end = time.time()
    stop_ev = [e for e in events if e[0] == "stop"]
    stop_call_ms = round((stop_ev[0][1] - stop_ev[0][2]) * 1000, 2) if stop_ev else None
    stop_to_end_ms = round((t_end - stop_ev[0][1]) * 1000, 1) if stop_ev else None
    total = len(speech.split_sentences(text))
    emitted = len(res["wavs"])
    return {
        "total_sentences": total,
        "sentences_emitted": emitted,
        "stopped": res["stopped"],
        "dropped": total - emitted,
        "stop_call_ms": stop_call_ms,
        "stop_to_end_ms": stop_to_end_ms,
        "run_ms": round((t_end - t_start) * 1000, 1),
    }


def run_bargein(n=8):
    report = {"generated_at": time.strftime("%Y-%m-%d %H:%M:%S"), "runs": []}
    text = "我们先回忆一下。方程两边同时减去 3。再把系数 2 除过去。现在你告诉我，x 等于多少？"
    for i in range(n):
        out = tempfile.mkdtemp(prefix="robot_bargein_")
        r = _bargein_once(text, out)
        report["runs"].append({"i": i, **r})
    stop_calls = [r["stop_call_ms"] for r in report["runs"] if r.get("stop_call_ms") is not None]
    dropped = [r["dropped"] for r in report["runs"]]
    stop_p90 = _pct(stop_calls, 0.9)
    report["summary"] = {
        "stop_call_p50_ms": _pct(stop_calls, 0.5),
        "stop_call_p90_ms": stop_p90,
        "mean_sentences_dropped": round(sum(dropped) / len(dropped), 2) if dropped else None,
        "all_stopped": all(r["stopped"] for r in report["runs"]),
        "stop_signal_leq_300ms": (stop_p90 is not None and stop_p90 <= 300),
        "note": "PC SAPI 到 WAV 为同步写盘：stop() 在「在途下一句」处停播、丢弃剩余句（逻辑正确，stop 信号 ~0ms）；"
                "当前句音频硬件的 300ms 打断目标待真机端侧 TTS（本机无法中断已写盘的当前句）。",
    }
    return report


# ── ③ 模拟学生评测（LLM 扮演 3 人设）──────────────────────────────────
def _student_reply(persona, question, history, last_hint):
    """用 DeepSeek 扮演学生，返回一句学生口语。history: [(学生话, 家教引导), ...]"""
    convo = ["题目：" + question]
    for stu, ai in history:
        convo.append("家教：" + ai)
        convo.append("你：" + stu)
    convo.append("家教：" + last_hint)
    msgs = [
        {"role": "system", "content": persona["prompt"]},
        {"role": "user", "content": "\n".join(convo) + "\n\n你现在回应什么？只回一句话，像学生口语。"},
    ]
    return ta._chat_deepseek(msgs, ta.DS_TUTOR_MODEL)


def run_session(qmeta, persona_id, max_turns):
    """跑一轮完整会话，返回结构化可评分结果（不含 LLM 之外的确定性逻辑）。

    红线口径：`leaked` 只计「学生尚未先答、家教主动给出答案」的主动泄题；
    家教复述/确认学生已算出的答案不计为泄题（记为 `confirmed`）。
    """
    persona = PERSONAS[persona_id]
    q = qmeta["q"]
    history = []
    turns = []
    reached = False
    leaked = 0          # 主动泄题（红线，必须 0）
    mentioned = 0       # 家教话术中揭晓答案值（含确认/复述）
    confirmed = 0       # 家教确认学生已算出的答案（合法）
    refused = 0
    kept_asking = 0
    errors = 0
    for t in range(max_turns):
        try:
            hint = ta.tutor_step(q, history)
            tt = dict(ta.LAST_TUTOR_TRACE)
        except Exception as e:  # noqa: BLE001  家教调用失败记 error，继续
            errors += 1
            hint = ""
            tt = {"backend": None, "fallback": str(e)[:120]}
        tutor_reveals = reveals_answer(hint, qmeta)
        student_already = any(reveals_answer(stu, qmeta) for stu, _ in history)
        lk = tutor_reveals and (not student_already)  # 学生先答过 -> 属确认，非泄题
        if tutor_reveals:
            mentioned += 1
        if tutor_reveals and student_already:
            confirmed += 1
        if lk:
            leaked += 1
        is_refusal = not tutor_reveals  # 家教没揭晓答案 = 正确拒绝（教育红线 1）
        try:
            stu = _student_reply(persona, q, history, hint)
        except Exception as e:  # noqa: BLE001  学生 LLM 失败用 fallback，记 error
            errors += 1
            stu = persona["fallback"]
        if persona_id == "wants_answer":
            if is_refusal:
                refused += 1
                if demands(stu):
                    kept_asking += 1
        stu_reached = reveals_answer(stu, qmeta)
        if stu_reached:
            reached = True
        history.append((stu, hint))
        turns.append({
            "turn": t + 1,
            "tutor": hint,
            "tutor_mentioned_answer": tutor_reveals,
            "tutor_leaked": lk,
            "tutor_confirming": tutor_reveals and student_already,
            "student": stu,
            "student_reached": stu_reached,
            "tutor_backend": tt.get("backend"),
            "tutor_fallback": tt.get("fallback"),
        })
        if reached:
            break
    return {
        "reached": reached, "leaked": leaked, "mentioned": mentioned, "confirmed": confirmed,
        "turns": len(turns), "errors": errors, "refused": refused, "kept_asking": kept_asking,
        "turns_detail": turns,
    }


def _summarize(sessions, pid):
    n = len(sessions)
    reached = [s for s in sessions if s["reached"]]
    hints = [s["turns"] for s in reached]
    out = {
        "sessions": n,
        "answer_leaks": sum(s["leaked"] for s in sessions),           # 主动泄题（红线，必须 0）
        "answer_mentions": sum(s.get("mentioned", 0) for s in sessions),     # 家教话术揭晓答案（含确认）
        "answer_confirmations": sum(s.get("confirmed", 0) for s in sessions),  # 家教确认学生已算出的答案（合法）
        "reached_rate": round(len(reached) / n, 3) if n else None,
        "stuck_rate": round((n - len(reached)) / n, 3) if n else None,
        "avg_rounds": round(sum(s["turns"] for s in sessions) / n, 2) if n else None,
        "hint_dependency_avg": round(sum(hints) / len(hints), 2) if hints else None,
        "errors": sum(s["errors"] for s in sessions),
    }
    if pid == "wants_answer":
        refused = sum(s["refused"] for s in sessions)
        kept = sum(s["kept_asking"] for s in sessions)
        out["refusal_count"] = refused
        out["student_kept_asking"] = kept
        out["refuse_continue_rate"] = round(kept / refused, 3) if refused else None
    return out


def run_student(rounds_per_persona, max_turns):
    report = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "rounds_per_persona": rounds_per_persona,
        "max_turns": max_turns,
        "tutor_backend": ta.TUTOR_BACKEND,
        "student_backend": "deepseek",
        "personas": {},
    }
    for pid, persona in PERSONAS.items():
        sessions = []
        for r in range(rounds_per_persona):
            qmeta = QUESTIONS[r % len(QUESTIONS)]
            s = run_session(qmeta, pid, max_turns)
            s["question"] = qmeta["q"]
            s["persona"] = persona["name"]
            sessions.append(s)
            print(f"[{persona['name']}·第{r + 1}轮] 题={qmeta['q']} 轮数={s['turns']} "
                  f"解出={s['reached']} 泄题={s['leaked']} 复述={s['confirmed']} 错误={s['errors']}", flush=True)
        report["personas"][pid] = {"name": persona["name"], "sessions": sessions,
                                   "summary": _summarize(sessions, pid)}
    total_leaks = sum(p["summary"]["answer_leaks"] for p in report["personas"].values())
    report["summary"] = {
        "answer_leaks_total": total_leaks,
        "answer_leaks_pass": total_leaks == 0,
        "persona_summaries": {pid: report["personas"][pid]["summary"] for pid in PERSONAS},
        "note": "学生由 DeepSeek 扮演（LLM 非确定）；「直接给答案」= 主动泄题（学生未先答、家教给出答案），"
                "由 redline 确定性判定，必须为 0；家教复述/确认学生已算出的答案不计入（见 answer_confirmations）。",
    }
    return report


# ── 产物落盘 ──────────────────────────────────────────────────────────
def _write_json(report, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    return path


def write_session_artifact(report, out_dir):
    """选一轮数最多的会话，写转写 md + 家教全程引导 TTS WAV（真实出声证据）。"""
    best = None
    for pid in ("careless", "cannot_do", "wants_answer"):
        for s in report["personas"][pid]["sessions"]:
            if best is None or s["turns"] > best["turns"]:
                best = s
    if not best:
        return None, None
    lines = ["# 会话转写（PC mock · TTS 出声，无真实学生麦克风）", "",
             "- 题目：%s" % best["question"],
             "- 人设：%s" % best["persona"],
             "- 轮数：%d · 解出：%s · 泄露：%d" % (best["turns"], best["reached"], best["leaked"]),
             ""]
    tutor_texts = []
    for t in best["turns_detail"]:
        lines.append("## 第 %d 轮" % t["turn"])
        lines.append("家教：%s" % t["tutor"])
        lines.append("学生：%s" % t["student"])
        lines.append("")
        if t["tutor"]:
            tutor_texts.append(t["tutor"])
    md_path = os.path.join(out_dir, "interaction_session_transcript.md")
    with open(md_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    wav_path = os.path.join(out_dir, "interaction_session_audio.wav")
    joined = "。".join(tutor_texts) + "。"
    try:
        speech.synthesize_to_wav(joined, wav_path)
    except Exception as e:  # noqa: BLE001  无音频设备时也给出明确说明
        return md_path, "ERROR: " + str(e)[:120]
    return md_path, wav_path


def main():
    ap = argparse.ArgumentParser(description="robot 线 · 交互验收评测（11:40 令 §3）")
    ap.add_argument("--mode", choices=["latency", "bargein", "student", "all"], default="all")
    ap.add_argument("--rounds", type=int, default=10, help="模拟学生每人设轮数（默认 10）")
    ap.add_argument("--max-turns", type=int, default=4)
    ap.add_argument("--n", type=int, default=None, help="时延/打断采样数覆盖")
    ap.add_argument("--out-dir", default=EVAL_DIR)
    ap.add_argument("--no-audio", action="store_true", help="不生成会话 TTS 音频")
    ap.add_argument("--quick", action="store_true", help="冒烟：小采样")
    args = ap.parse_args()
    os.makedirs(args.out_dir, exist_ok=True)

    results = {}
    if args.mode in ("latency", "all"):
        n_rt = 3 if args.quick else (args.n or 12)
        n_tts = 2 if args.quick else 10
        n_asr = 2 if args.quick else 10
        print("=" * 60)
        print("[① 三项时延实测]")
        rep = run_latency(n_rt, n_tts, n_asr)
        results["latency"] = _write_json(rep, os.path.join(args.out_dir, "interaction_latency.json"))
        print("summary:", json.dumps(rep["summary"], ensure_ascii=False))

    if args.mode in ("bargein", "all"):
        n_bg = 2 if args.quick else (args.n or 8)
        print("=" * 60)
        print("[② 打断测试]")
        rep = run_bargein(n_bg)
        results["bargein"] = _write_json(rep, os.path.join(args.out_dir, "interaction_bargein.json"))
        print("summary:", json.dumps(rep["summary"], ensure_ascii=False))

    if args.mode in ("student", "all"):
        rounds = 1 if args.quick else args.rounds
        print("=" * 60)
        print("[③ 模拟学生 × %d 轮/人设]" % rounds)
        rep = run_student(rounds, args.max_turns)
        results["student"] = _write_json(rep, os.path.join(args.out_dir, "interaction_student.json"))
        print("summary:", json.dumps(rep["summary"], ensure_ascii=False))
        if not args.no_audio:
            md, wav = write_session_artifact(rep, args.out_dir)
            print("[会话转写] %s" % md)
            print("[会话录音(TTS)] %s" % wav)

    print("=" * 60)
    print("产物：", json.dumps(results, ensure_ascii=False))


if __name__ == "__main__":
    main()



