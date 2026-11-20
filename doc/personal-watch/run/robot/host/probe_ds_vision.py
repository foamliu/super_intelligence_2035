# -*- coding: utf-8 -*-
"""运维侧一次性探针：验证 DeepSeek 视觉（识图）是否可替代本地 OCR。

产出：eval/ds_vision_probe.json
只读 secrets.json 取 key（不落盘、不进日志）。
"""
import base64
import json
import os
import time

import requests
from PIL import Image, ImageDraw, ImageFont

SECRETS = os.path.expanduser(r"~\.cline\data\secrets.json")
OUT = os.path.join(os.path.dirname(__file__), "eval", "ds_vision_probe.json")

CASES = [
    ("q1_pure", "2x + 3 = 11"),
    ("q1_mixed", "解方程：2x + 3 = 11"),
    ("q2_mixed", "已知等腰三角形顶角为 40°，求底角的度数。"),
    ("q3_mixed", "化简：3(a - 2b) + 2(a + b)"),
]

PROMPT = (
    "请只把图片里的题目逐字抄写出来，一字不改，只输出题目原文。"
    "数学公式请用标准写法（例如 2x+3=11）。"
    "严格禁止解题、禁止写出答案、禁止任何讲解或多余的话。"
)


def _font(size=40):
    for name in ("msyh.ttc", "simsun.ttc", "simhei.ttf", "arial.ttf"):
        try:
            return ImageFont.truetype(name, size)
        except OSError:
            continue
    return ImageFont.load_default()


def make_img(text, path):
    img = Image.new("RGB", (900, 220), "white")
    d = ImageDraw.Draw(img)
    d.text((40, 90), text, fill="black", font=_font())
    img.save(path)


def to_b64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("ascii")


def main():
    key = json.load(open(SECRETS, encoding="utf-8"))["deepSeekApiKey"]
    base = os.environ.get("DS_BASE", "https://api.deepseek.com")
    model = os.environ.get("DS_VISION_MODEL", "deepseek-flash")
    url = base.rstrip("/") + "/chat/completions"

    tmpdir = os.path.join(os.path.dirname(__file__), "..", "eval", "_tmp_img")
    os.makedirs(tmpdir, exist_ok=True)

    report = {"model": model, "endpoint": url, "cases": []}
    for cid, truth in CASES:
        p = os.path.join(tmpdir, cid + ".png")
        make_img(truth, p)
        body = {
            "model": model,
            "messages": [{
                "role": "user",
                "content": [
                    {"type": "text", "text": PROMPT},
                    {"type": "image_url",
                     "image_url": {"url": "data:image/png;base64," + to_b64(p)}},
                ],
            }],
            "stream": False,
        }
        t0 = time.time()
        try:
            r = requests.post(url, headers={"Authorization": "Bearer " + key},
                              json=body, timeout=120)
            dt = round(time.time() - t0, 2)
            if r.status_code != 200:
                report["cases"].append({"id": cid, "truth": truth,
                                        "http": r.status_code,
                                        "error": r.text[:300], "latency_s": dt})
                print("[%s] HTTP %s  %.1fs  %s" % (cid, r.status_code, dt, r.text[:120]))
                continue
            j = r.json()
            txt = j["choices"][0]["message"]["content"].strip()
            usage = j.get("usage", {})
            ok = truth.replace(" ", "") in txt.replace(" ", "")
            report["cases"].append({"id": cid, "truth": truth, "vision": txt,
                                    "correct": ok, "latency_s": dt,
                                    "usage": usage})
            print("[%s] %.1fs 正确=%s | 识别: %s" % (cid, dt, ok, txt))
        except Exception as e:  # noqa: BLE001
            print("[%s] EXC %s" % (cid, e))
            report["cases"].append({"id": cid, "truth": truth, "exc": str(e)})

    okn = sum(1 for c in report["cases"] if c.get("correct"))
    report["summary"] = {"n": len(CASES), "correct": okn,
                         "accuracy": round(okn / len(CASES), 3)}
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    json.dump(report, open(OUT, "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    print("\n汇总: %d/%d 正确 = %.1f%%" % (okn, len(CASES), 100.0 * okn / len(CASES)))


if __name__ == "__main__":
    main()
