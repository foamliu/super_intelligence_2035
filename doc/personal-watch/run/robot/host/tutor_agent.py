#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · PC 端家教 agent（R3 路线：手机只做「眼耳口」采集+播放，推理在 PC/云）

最小 demo 闭环：拍 1 题 -> 识别 -> 分步引导（不直接给答案）-> TTS 朗读

推理后端（11:30 用户令定稿：云端 DeepSeek 主路径 + 本机 ollama 兜底）：
  - 识图/OCR   : 默认 DeepSeek 视觉 `deepseek-flash`（实测读中文题干 4/4）
                 兜底 = 本机 ollama `llava:latest`（离线可用，算式稳、中文长题干弱）
                 ⚠️ `qwen3-vl:32b`（20GB，本机 /api/chat 报 404）**已作废**，不再等待下载
  - 分步引导   : 默认 DeepSeek `deepseek-flash`（时延低）；兜底 = ollama `qwen3:8b`
  - TTS 朗读   : Windows SAPI（Microsoft Huihui = 中文女声，离线免费）
  - 不依赖 ComfyUI（已冻结）。

后端开关（都可切纯本地，用于隐私/断网）：
  ROBOT_VISION_BACKEND = deepseek | ollama    （默认 deepseek）
  ROBOT_TUTOR_BACKEND  = deepseek | ollama    （默认 deepseek）
  DeepSeek key 只从环境变量 DEEPSEEK_API_KEY 或 ~/.cline/data/secrets.json 读，不落盘不打印。

用法：
  python tutor_agent.py --question "解方程：2x + 3 = 11"          # 文本题
  python tutor_agent.py --image  ../eval/q1_equation.png          # 题图（手机「拍照」产物）
  python tutor_agent.py --image  ../eval/q1_equation.png --speak demo_step1.wav
  python tutor_agent.py --interactive                              # 多轮追问（学生-家教对话）
  python tutor_agent.py --image q.png --vision-backend ollama      # 强制纯本地识图
"""
import argparse
import base64
import json
import os
import re
import sys
import time

import requests

# ── 推理后端（11:30 用户令定稿：云端 DeepSeek 主路径 + 本机 ollama 兜底）──────
# 识图/OCR：deepseek（默认，实测读中文题干 4/4）| ollama（本地离线兜底，llava）
VISION_BACKEND = os.environ.get("ROBOT_VISION_BACKEND", "deepseek").strip().lower()
# 分步引导（文本）：deepseek（默认，时延远低于本机 qwen3:8b）| ollama
TUTOR_BACKEND = os.environ.get("ROBOT_TUTOR_BACKEND", "deepseek").strip().lower()

OLLAMA = os.environ.get("ROBOT_OLLAMA_URL", "http://127.0.0.1:11434")
VISION_MODEL = os.environ.get("ROBOT_VISION_MODEL", "llava:latest")
TUTOR_MODEL = os.environ.get("ROBOT_TUTOR_MODEL", "qwen3:8b")
TUTOR_TIMEOUT = int(os.environ.get("ROBOT_TIMEOUT", "300"))

# 云端 DeepSeek（OpenAI 兼容）。key 只从环境变量或 secrets.json 读，
# 🚫 不写进仓库/日志/报告/截图（15:4x 令 §1）。
DS_BASE = os.environ.get("DS_BASE", "https://api.deepseek.com").rstrip("/")
DS_VISION_MODEL = os.environ.get("DS_VISION_MODEL", "deepseek-flash")
DS_TUTOR_MODEL = os.environ.get("DS_TUTOR_MODEL", "deepseek-flash")
DS_TIMEOUT = int(os.environ.get("ROBOT_DS_TIMEOUT", "60"))
SECRETS_JSON = os.path.expanduser(r"~\.cline\data\secrets.json")

# 最近一次调用实际走的路径（🚫 不许静默降级：CLI / 评测 / 报告都要能看到）
LAST_VISION_TRACE = {}
LAST_TUTOR_TRACE = {}

# ── 教育红线 1「不代写作业」：系统提示词硬性约束，只做分步引导 ──────────────
TUTOR_SYSTEM = (
    "你是一名耐心、循循善诱的初中家教，正在辅导学生做一道题。\n"
    "【铁律，违反即作废】\n"
    "1. 绝对不直接给出最终答案，不写出完整解题过程，不代写作业；\n"
    "2. 只做【分步引导】：先问学生思路 -> 给一句提示或一个中间小问 -> 让学生自己写 -> 再校验；\n"
    "3. 每次只推进【一步】，等学生回答后、根据回答对错再解锁下一步；\n"
    "4. 学生答对就肯定并进入下一步；答错就温和指出错在哪，给一个更小的提示；\n"
    "5. 不编造课本页码/定理出处；不确定就说「不确定」并给查证路径；\n"
    "6. 语气亲切、用短句；每次回复最多 2 句话，每句话不超过 20 个字，适合被转成语音朗读。\n"
    "你现在只输出【一步引导】：最多 2 句、每句 ≤20 字，不要输出答案，也不要一口气讲完全部步骤。"
)

# 句末标点/换行（11:40 令 §1.1「每次回复 ≤2 句」的确定性裁剪分句依据）
_SENT_END = "。！？!?；;\n"


def clamp_hint(text: str, max_sentences: int = 2) -> str:
    """把 LLM 引导裁剪到最多 `max_sentences` 句（11:40 令 §1.1）。

    纯函数、确定性：按句末标点（。！？!?；;）与换行切句、去掉空句、保留前 N 句。
    只做「删句」不做「硬截单句」——避免把中文半句切断导致 TTS 破音；
    单句 ≤20 字由 TUTOR_SYSTEM 提示词 + INTERACTION_SPEC 话术模板约束。
    （第 13 轮新增：交互验收实测发现 LLM 原始输出 3-6 句，超出「≤2 句」硬指标。）
    """
    if not text:
        return ""
    text = text.strip()
    sentences = [s for s in re.split(r"(?<=[%s])" % re.escape(_SENT_END), text) if s.strip()]
    if not sentences:
        return text
    return "".join(sentences[:max_sentences]).strip()


def _img_b64(path: str) -> str:
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def _img_data_url(path: str) -> str:
    """把题图包成 OpenAI 兼容的 data URL（DeepSeek 要求 image_url 形式）。"""
    ext = os.path.splitext(path)[1].lower().lstrip(".") or "png"
    if ext == "jpg":
        ext = "jpeg"
    return "data:image/%s;base64,%s" % (ext, _img_b64(path))


def _ds_key():
    """取 DeepSeek key：环境变量优先，其次 ~/.cline/data/secrets.json。返回 (key, 来源)。"""
    k = (os.environ.get("DEEPSEEK_API_KEY") or "").strip()
    if k:
        return k, "env"
    try:
        with open(SECRETS_JSON, encoding="utf-8") as f:
            k = (json.load(f).get("deepSeekApiKey") or "").strip()
        if k:
            return k, "secrets.json"
    except Exception:  # noqa: BLE001  读不到就当没有 key（走本地兜底）
        pass
    return "", "missing"


def _chat_ollama(messages, model: str, temperature=None) -> str:
    body = {"model": model, "stream": False, "messages": messages}
    if temperature is not None:
        body["options"] = {"temperature": temperature}
    r = requests.post("%s/api/chat" % OLLAMA, json=body, timeout=TUTOR_TIMEOUT)
    r.raise_for_status()
    return r.json()["message"]["content"].strip()


def _chat_deepseek(messages, model: str) -> str:
    key, _src = _ds_key()
    if not key:
        raise RuntimeError("DeepSeek key 缺失（环境变量 DEEPSEEK_API_KEY / secrets.json）")
    r = requests.post(
        "%s/chat/completions" % DS_BASE,
        headers={"Authorization": "Bearer " + key},
        json={"model": model, "stream": False, "messages": messages},
        timeout=DS_TIMEOUT,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def chat(messages, backend: str = None) -> str:
    """文本对话统一入口。deepseek 失败 -> 降级本机 ollama，并把降级原因写进 LAST_TUTOR_TRACE。"""
    global LAST_TUTOR_TRACE
    backend = (backend or TUTOR_BACKEND).strip().lower()
    if backend == "deepseek":
        t0 = time.time()
        try:
            text = _chat_deepseek(messages, DS_TUTOR_MODEL)
            LAST_TUTOR_TRACE = {"backend": "deepseek", "model": DS_TUTOR_MODEL,
                                "fallback": None, "latency_s": round(time.time() - t0, 2)}
            return text
        except Exception as e:  # noqa: BLE001
            fb = "deepseek 不可用：%s" % str(e)[:120]
    else:
        fb = "显式指定 ROBOT_TUTOR_BACKEND=ollama（纯本地模式）"
    t0 = time.time()
    text = _chat_ollama(messages, TUTOR_MODEL)
    LAST_TUTOR_TRACE = {"backend": "ollama", "model": TUTOR_MODEL,
                        "fallback": fb, "latency_s": round(time.time() - t0, 2)}
    return text


# OCR 提示词
# ① DeepSeek 视觉：显式要求「标准数学写法」（运维侧实测 4/4 用的就是这条，
#    否则模型会口述成「2x 加 3 等于 11」，既不利于下游计算也不利于比对）
OCR_PROMPT_DS = (
    "请只把图片里的题目逐字抄写出来，一字不改，只输出题目原文。"
    "数学公式请用标准写法（例如 2x+3=11）。"
    "严格禁止解题、禁止写出答案、禁止任何讲解或多余的话。"
)

# ② 本机 ollama/llava：中文提示词让它口述算式（llava 对符号输出不稳），
#    英文提示词是中文提示词拒识 / 返回空时的可靠兜底
OCR_PROMPTS = [
    "请只把图片里的题目逐字抄写出来，一字不改，只输出题目原文。"
    "公式用文字描述（例如『2x 加 3 等于 11』）。"
    "严格禁止解题、禁止写出答案、禁止任何讲解或多余的话。",
    "Transcribe the math equation in the image. Output only the equation text, "
    "one line, nothing else. Do not solve, do not explain.",
]


_REFUSAL_WORDS = ("无法", "抱歉", "不能", "看不清", "模糊", "没有看到", "未提供",
                  "cannot", "sorry", "unable", "too small", "blurry")


def _has_digit_or_math(s: str) -> bool:
    """判空/拒识：有数字或算式符号即认为读到了题；
    纯中文题干（无数字，如「求证两直线平行」）按「中文长度 + 无拒识词」判断。"""
    if any(ch.isdigit() for ch in s) or any(c in s for c in "+-=xX×÷√"):
        return True
    cjk = sum(1 for ch in s if "\u4e00" <= ch <= "\u9fff")
    low = s.lower()
    return cjk >= 8 and not any(k in low for k in _REFUSAL_WORDS)


def _ocr_ollama(prompt: str, question: str) -> str:
    return _chat_ollama(
        [{"role": "user", "content": prompt, "images": [_img_b64(question)]}],
        VISION_MODEL,
        temperature=0,  # 确定性 OCR（实测：默认随机会读成乱码，temp=0 稳定正确）
    )


def _ocr_deepseek(prompt: str, image_path: str) -> str:
    """DeepSeek 视觉读题（deepseek-flash）。content 里 image_url + text（OpenAI 兼容）。"""
    key, _src = _ds_key()
    if not key:
        raise RuntimeError("DeepSeek key 缺失")
    body = {
        "model": DS_VISION_MODEL,
        "stream": False,
        "temperature": 0,  # 与本地 OCR 同口径：确定性解码
        "messages": [{"role": "user", "content": [
            {"type": "text", "text": prompt},
            {"type": "image_url", "image_url": {"url": _img_data_url(image_path)}},
        ]}],
    }
    r = requests.post("%s/chat/completions" % DS_BASE,
                      headers={"Authorization": "Bearer " + key},
                      json=body, timeout=DS_TIMEOUT)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def recognize_ex(question: str):
    """带路径追踪版识图：返回 (题干文本, trace)。

    trace = {backend, model, image, fallback, latency_s}；`fallback` 非空 = 走了降级路径
    （🚫 不许静默降级，调用方必须能看到，见 15:4x 令 §2.2）。
    """
    global LAST_VISION_TRACE
    if not os.path.isfile(question):
        LAST_VISION_TRACE = {"backend": "text", "model": None, "image": None,
                             "fallback": None, "latency_s": 0.0}
        return question.strip(), LAST_VISION_TRACE

    fb = None
    if VISION_BACKEND == "deepseek":
        t0 = time.time()
        try:
            text = _ocr_deepseek(OCR_PROMPT_DS, question)
            if _has_digit_or_math(text):
                LAST_VISION_TRACE = {"backend": "deepseek", "model": DS_VISION_MODEL,
                                     "image": question, "fallback": None,
                                     "latency_s": round(time.time() - t0, 2)}
                return text, LAST_VISION_TRACE
            fb = "deepseek 未读出算式/数字（返回：%s）" % text[:30]
        except Exception as e:  # noqa: BLE001  网络失败 / 无 key / 429 等
            fb = "deepseek 不可用：%s" % str(e)[:120]

    # 兜底：本机 ollama（llava）。中英文提示词依次尝试（英文提示词是拒识时的可靠兜底）
    t0 = time.time()
    last = ""
    for prompt in OCR_PROMPTS:
        last = _ocr_ollama(prompt, question)
        if _has_digit_or_math(last):
            break
    LAST_VISION_TRACE = {
        "backend": "ollama", "model": VISION_MODEL, "image": question,
        "fallback": fb or ("显式指定 ROBOT_VISION_BACKEND=ollama（纯本地模式）"
                           if VISION_BACKEND != "deepseek" else "deepseek 未给出可解析结果"),
        "latency_s": round(time.time() - t0, 2),
    }
    return last, LAST_VISION_TRACE


def recognize(question: str) -> str:
    """输入：题图路径（手机「拍照」产物）或纯文本；输出：结构化题干文本。

    签名保持不变（主流程与 eval_l1 不用改）；实际走的后端见 `LAST_VISION_TRACE`。
    """
    return recognize_ex(question)[0]



def tutor_step(question: str, history=()) -> str:
    """返回当前这一步的引导文本（不含答案）。history: [(学生话, 上步引导), ...]"""
    msgs = [{"role": "system", "content": TUTOR_SYSTEM},
            {"role": "user", "content": f"题目：{question}\n请开始第一步引导（只输出一步，不给答案）。"}]
    for stu, ai in history:
        msgs.append({"role": "user", "content": stu})
        msgs.append({"role": "assistant", "content": ai})
    return clamp_hint(chat(msgs))


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
    try:
        sp.Speak(text)
    except Exception as e:  # noqa: BLE001  headless / 无音频设备时不许整个流程崩
        raise RuntimeError(
            "本机无可用音频输出（headless），请用 --speak out.wav 落盘验证出声"
        ) from e
    return None


def redline_leak_check(output: str, answer: str) -> bool:
    """教育红线自检：若引导文本里出现最终答案原文，返回 True（应判作废）。"""
    a = "".join(answer.replace(" ", "").replace("，", "").replace(",", "").split())
    o = "".join(output.replace(" ", "").replace("，", "").replace(",", "").split())
    return bool(a) and a in o


def main():
    t_start = time.time()
    ap = argparse.ArgumentParser(description="robot 线 · 最小 demo：拍题 -> 引导 -> 出声")
    src = ap.add_mutually_exclusive_group(required=True)
    src.add_argument("--question", help="题干文本")
    src.add_argument("--image", help="题图路径（模拟手机拍照）")
    src.add_argument("--interactive", action="store_true", help="多轮追问（终端模拟学生）")
    ap.add_argument("--speak", default=None, help="TTS 输出 WAV 路径（同时播放）")
    ap.add_argument("--answer", default=None, help="[评测用] 已知最终答案，用于红线自检")
    ap.add_argument("--vision-backend", choices=["deepseek", "ollama"], default=None,
                    help="识图后端（默认取 ROBOT_VISION_BACKEND，缺省 deepseek）")
    ap.add_argument("--tutor-backend", choices=["deepseek", "ollama"], default=None,
                    help="分步引导后端（默认取 ROBOT_TUTOR_BACKEND，缺省 deepseek）")
    args = ap.parse_args()

    global VISION_BACKEND, TUTOR_BACKEND
    if args.vision_backend:
        VISION_BACKEND = args.vision_backend
    if args.tutor_backend:
        TUTOR_BACKEND = args.tutor_backend

    if args.interactive:
        q = input("请粘贴题目原文：").strip()
    elif args.image:
        q, trace = recognize_ex(args.image)
        tail = f"  ⚠️ 降级：{trace['fallback']}" if trace.get("fallback") else ""
        print(f"[识别] {trace['latency_s']}s  backend={trace['backend']}({trace['model']}){tail}")
        print(f"{q}\n")
    else:
        q = args.question

    history = []
    print("=" * 60)
    print("家教（只推进一步，不给答案）：\n")
    step = tutor_step(q, history)
    tt = LAST_TUTOR_TRACE
    tail = f"  ⚠️ 降级：{tt['fallback']}" if tt.get("fallback") else ""
    print(f"[引导] {tt.get('latency_s')}s  backend={tt.get('backend')}({tt.get('model')}){tail}")
    print(step)
    # 「图产生 -> 第一句引导文本吐出」的端到端时延（16:5x 令 §3.3 口径，不含 TTS）
    print(f"\n[总时延] {time.time() - t_start:.2f}s（识别 + 首步引导，不含 TTS）")
    try:
        wav = speak(step, args.speak)
    except Exception as e:  # noqa: BLE001  无音频输出 -> 降级纯文字（12:20 令 §2.5）
        print(f"\n[出声] ⚠️ 播放失败，已降级为文字：{e}")
        wav = None
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
            try:
                speak(step, args.speak)
            except Exception as e:  # noqa: BLE001
                print(f"[出声] ⚠️ 播放失败，已降级为文字：{e}")


if __name__ == "__main__":
    main()
