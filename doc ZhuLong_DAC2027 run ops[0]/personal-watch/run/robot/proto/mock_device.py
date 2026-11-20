#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
robot 线 · 模拟手机端（PC 端 mock，手机未连时用它跑通整条链路）

职责（对应 R3 路线里手机的「眼耳口」）：
  - 「眼」拍照：把一道题渲染成 PNG（模拟学生拍下的题目照片）
  - 「口」播放：调用 Windows SAPI 把引导文本念出来（真机由手机端播报）

真机接上后，这个文件会被手机端（HarmonyOS/Android 采集 App）替换，
但 PC 侧 agent（host/tutor_agent.py）的接口保持不变。
"""
import argparse
import os

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "C:/Windows/Fonts/msyh.ttc",      # 微软雅黑
    "C:/Windows/Fonts/simhei.ttf",    # 黑体
    "C:/Windows/Fonts/simsun.ttc",    # 宋体
]


def _font(size: int):
    for p in FONT_CANDIDATES:
        if os.path.isfile(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def snap_question(text: str, out_png: str) -> str:
    """把一道题「拍」成题图（白底黑字 PNG），模拟手机拍照。"""
    lines = text.split("\n")
    font = _font(40)
    pad = 60
    line_h = 62
    w = max(int(font.getlength(l)) for l in lines) + pad * 2
    w = max(w, 400)
    h = line_h * len(lines) + pad * 2
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    y = pad
    for l in lines:
        d.text((pad, y), l, fill="black", font=font)
        y += line_h
    img.save(out_png)
    return out_png


def play(text: str):
    from tutor_agent import speak  # 复用 PC 侧 TTS（真机时由手机端播放）
    speak(text)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="模拟手机端")
    ap.add_argument("--snap", help="要「拍」的题目文本，输出 PNG")
    ap.add_argument("--out", default="shot_question.png")
    args = ap.parse_args()
    if args.snap:
        p = snap_question(args.snap, args.out)
        print(f"[mock 手机·眼] 已拍照 -> {p}")
