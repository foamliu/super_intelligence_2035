#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · PC 端家教 agent（R3 路线：手机只做「眼耳口」采集+播放，推理在 PC）

最小 demo 闭环：拍 1 题 -> 识别 -> 分步引导（不直接给答案）-> TTS 朗读

依赖（本机已具备，零采购 / 零外部账号）：
  - 视觉/识别   : ollama `llava:latest`（读图 + OCR，实测可用）
                  ⚠️ 首选 `qwen3-vl:32b`（更强、支持复杂公式/手写）当前 /api/chat 报 404
                  「not found」（已注册但 manifest 异常，见 P0_设备通路.md），修复后改回即可。
  - 分步引导 LLM : ollama `qwen3:8b`（循循善诱，只推进一步，不泄答案）
  - TTS 朗读     : Windows SAPI（Microsoft Huihui = 中文女声，离线免费）
  - 不依赖 ComfyUI、不依赖任何付费 API。

用法：
  python tutor_agent.py --question "解方程：2x + 3 = 11"          # 文本题
  python tutor_agent.py --image  ../eval/q1_equation.png          # 题图（手机「拍照」产物）
  python tutor_agent.py --image  ../eval/q1_equation.png --speak demo_step1.wav
  python tutor_agent.py --interactive                              # 多轮追问（学生-家教对话）
"""
import argparse
import base64
import os
import sys
import time

import requests

OLLAMA = os.environ.get("ROBOT_OLLAMA_URL", "http://127.0.0.1:11434")
VISION_MODEL = os.environ.get("ROBOT_VISION_MODEL", "llava:latest")
TUTOR_MODEL = os.environ.get("ROBOT_TUTOR_MODEL", "qwen3:8b")
TUTOR_TIMEOUT = int(os.environ.get("ROBOT_TIMEOUT", "300"))

# ── 教育红线 1「不代写作业」：系统提示词硬性约束，只做分步引导 ──────────────
TUTOR_SYSTEM = (
    "你是一名耐心、循循善诱的初中家教，正在辅导学生做一道题。\n"
    "【铁律，违反即作废】\n"
    "1. 绝对不直接给出最终答案，不写出完整解题过程，不代写作业；\n"
    "2. 只做【分步引导】：先问学生思路 -> 给一句提示或一个中间小问 -> 让学生自己写 -> 再校验；\n"
    "3. 每次只推进【一步】，等学生回答后、根据回答对错再解锁下一步；\n"
    "4. 学生答对就肯定并进入下一步；答错就温和指出错在哪，给一个更小的提示；\n"
    "5. 不编造课本页码/定理出处；不确定就说「不确定」并给查证路径；\n"
    "6. 语气亲切、用短句，适合被转成语音朗读。\n"
    "你现在只输出【一步引导】，不要输出答案，也不要一口气讲完全部步骤。"
)


def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


# OCR 提示词（第 4 轮实测：llava 读「纯算式」用中英文都能对，读「中文+算式混合」都会失败；
# 英文提示词在中文提示词返回空/拒识时是可靠兜底）
OCR_PROMPTS = [
    "请只把图片里的题目逐字抄写出来，一字不改，只输出题目原文。"
    "公式用文字描述（例如『2x 加 3 等于 11』）。"
    "严格禁止解题、禁止写出答案、禁止任何讲解或多余的话。",
    "Transcribe the math equation in the image. Output only the equation text, "
    "one line, nothing else. Do not solve, do not explain.",
]


def _has_digit_or_math(s: str) -> bool:
    """判空/拒识：连一个数字或常见算式符号都没有，视为未识别出题目。"""
    return any(ch.isdigit() for ch in s) or any(c in s for c in "+-=xX×÷√")


def _ocr_once(prompt: str, question: str) -> str:
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={
            "model": VISION_MODEL,
            "stream": False,
            "options": {"temperature": 0},  # 确定性 OCR（实测：默认随机会读成乱码，temp=0 稳定正确）
            "messages": [{"role": "user", "content": prompt,
                          "images": [_img_b64(question)]}],
        },
        timeout=TUTOR_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def recognize(question: str) -> str:
    """输入：题图路径（手机「拍照」产物）或纯文本；输出：结构化题干文本。"""
    if not os.path.isfile(question):
        return question.strip()
    last = ""
    for prompt in OCR_PROMPTS:
        last = _ocr_once(prompt, question)
        if _has_digit_or_math(last):
            return last
    # 中英文提示词都未识别出算式，返回最后一次结果（诚实交给下游，不硬编）
    return last


def tutor_step(question: str, history=()) -> str:
    """返回当前这一步的引导文本（不含答案）。history: [(学生话, 上步引导), ...]"""
    msgs = [{"role": "system", "content": TUTOR_SYSTEM},
            {"role": "user", "content": f"题目：{question}\n请开始第一步引导（只输出一步，不给答案）。"}]
    for stu, ai in history:
        msgs.append({"role": "user", "content": stu})
        msgs.append({"role": "assistant", "content": ai})
    r = requests.post(
        f"{OLLAMA}/api/chat",
        json={"model": TUTOR_MODEL, "stream": False, "messages": msgs},
        timeout=TUTOR_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def speak(text: str, out_wav: str = None) -> str:
    """Windows SAPI TTS 朗读。out_wav 给则另存一份 WAV（可证伪的「出声」产物）。"""
    import pythoncom
    import win32com.client
    pythoncom.CoInitialize()
    sp = win32com.client.Dispatch("SAPI.SpVoice")
    for v in sp.GetVoices():
        if "Huihui" in v.GetAttribute("Name"):
            sp.Voice = v
            break
    if out_wav:
        fs = win32com.client.Dispatch("SAPI.SpFileStream")
        try:
            fs.Format.Type = 39  # SAFT44kHz16BitStereo
        except Exception:
            pass
        fs.Open(out_wav, 3)  # SSFMCreateForWrite
        sp.AudioOutputStream = fs
        try:
            sp.Speak(text)
        finally:
            fs.Close()
            sp.AudioOutputStream = None
        return out_wav
    sp.Speak(text)
    return None


def redline_leak_check(output: str, answer: str) -> bool:
    """教育红线自检：若引导文本里出现最终答案原文，返回 True（应判作废）。"""
    a = "".join(answer.replace(" ", "").replace("，", "").replace(",", "").split())
    o = "".join(output.replace(" ", "").replace("，", "").replace(",", "").split())
    return bool(a) and a in o


def main():
    ap = argparse.ArgumentParser(description="robot 线 · 最小 demo：拍题 -> 引导 -> 出声")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--question", help="题干文本")
    src.add_argument("--image", help="题图路径（模拟手机拍照）")
    src.add_argument("--interactive", action="store_true", help="多轮追问（终端模拟学生）")
    ap.add_argument("--speak", default=None, help="TTS 输出 WAV 路径（同时播放）")
    ap.add_argument("--answer", default=None, help="[评测用] 已知最终答案，用于红线自检")
    args = ap.parse_args()

    if args.interactive:
        q = input("请粘贴题目原文：").strip()
    elif args.image:
        t0 = time.time()
        q = recognize(args.image)
        print(f"[识别] {time.time()-t0:.1f}s\n{q}\n")
    else:
        q = args.question

    history = []
    print("=" * 60)
    print("家教（只推进一步，不给答案）：\n")
    step = tutor_step(q, history)
    print(step)
    wav = speak(step, args.speak)
    if wav:
        print(f"\n[出声] 已朗读并保存 WAV：{wav}")
    if args.answer and redline_leak_check(step, args.answer):
        print("⚠️ 红线自检：引导文本疑似泄露最终答案，需重写提示词/重试！")

    if args.interactive:
        history.append(("（题目）" + q, step))
        while True:
            stu = input("\n学生：").strip()
            if stu.lower() in ("quit", "exit", "退出", "q"):
                break
            step = tutor_step(q, history)
            history.append((stu, step))
            print(f"\n家教：{step}")
            speak(step, args.speak)


if __name__ == "__main__":
    main()
