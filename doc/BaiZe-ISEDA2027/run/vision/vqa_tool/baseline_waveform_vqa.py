#!/usr/bin/env python3
"""Pre-strengthening baseline for the Qwen3.5-2B VQA tool (用户令 09:1x #3/#4).

Synthesizes a small set of waveform images with KNOWN ground truth (mirroring
the waveview α/β skills: cycle counting, duty cycle, frequency compare, rise
edge, amplitude) and queries the VQA server. Records answers + correctness so
later SFT/RL strengthening (#4) can be measured against this baseline with a
paired comparison (same images, same questions).

Output: baseline_waveform_vqa_results.json (next to this script).
"""
import base64, io, json, os, sys, time, urllib.request
import numpy as np
from PIL import Image, ImageDraw, ImageFont

SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")
OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "baseline_images")


def new_canvas(w=480, h=260):
    img = Image.new("RGB", (w, h), "white")
    d = ImageDraw.Draw(img)
    # light grid: 1 division = 40px (so amplitude/period in "divisions" is well-defined)
    for gx in range(40, w, 40):
        d.line([(gx, 15), (gx, h - 15)], fill=(235, 235, 235), width=1)
    for gy in range(15, h, 15):
        if (gy - 15) % 40 == 0:
            d.line([(40, gy), (w - 15, gy)], fill=(235, 235, 235), width=1)
    d.line([(40, 15), (40, h - 15)], fill="black", width=1)   # y axis
    d.line([(40, h // 2), (w - 15, h // 2)], fill="black", width=1)  # x axis
    return img, d


def draw_signal(d, pts, color="blue", width=2):
    for i in range(len(pts) - 1):
        d.line([pts[i], pts[i + 1]], fill=color, width=width)


def sine_image(path, cycles, amp_div=3.0):
    """amp_div = peak amplitude in y-grid divisions (1 div = 40px)."""
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    pts = []
    for x in range(x0, x1):
        t = (x - x0) / (x1 - x0)
        y = mid - amp_div * 40 * np.sin(2 * np.pi * cycles * t)
        pts.append((x, y))
    draw_signal(d, pts)
    img.save(path)


def square_image(path, cycles, duty=0.5, amp_div=3.0):
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    n = 1200
    for i in range(n):
        t = (i / n) * cycles
        phase = t - int(t)
        y = mid - amp_div * 40 if phase < duty else mid + amp_div * 40
        x = x0 + (x1 - x0) * i / n
        if i == 0:
            prev = (x, y)
        else:
            d.line([prev, (x, y)], fill="blue", width=2)
            if (x, y)[1] != prev[1]:
                d.line([prev, (x, y)], fill="blue", width=2)
            prev = (x, y)
    img.save(path)


def two_sine_image(path, cycles_a, cycles_b, amp_div=2.4):
    img, d = new_canvas()
    x0, x1 = 40, 465
    pa = [(x, 70 - amp_div * 40 * np.sin(2 * np.pi * cycles_a * (x - x0) / (x1 - x0)))
          for x in range(x0, x1)]
    pb = [(x, 190 - amp_div * 40 * np.sin(2 * np.pi * cycles_b * (x - x0) / (x1 - x0)))
          for x in range(x0, x1)]
    draw_signal(d, pa, color="blue")
    draw_signal(d, pb, color="red")
    d.text((x0 + 5, 40), "A (blue)", fill="blue")
    d.text((x0 + 5, 160), "B (red)", fill="red")
    img.save(path)


def rise_edge_image(path, slow=False):
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    low_y, high_y = mid + 80, mid - 80
    edge_x = x0 + 120
    if slow:
        # gradual ramp over ~120px
        pts = [(x0, low_y)]
        for x in range(edge_x, edge_x + 120):
            f = (x - edge_x) / 120.0
            y = low_y + (high_y - low_y) * (f * f * (3 - 2 * f))  # smoothstep
            pts.append((x, y))
        pts.append((x1, high_y))
    else:
        pts = [(x0, low_y), (edge_x, low_y), (edge_x, high_y), (x1, high_y)]
    draw_signal(d, pts, width=3)
    img.save(path)


def vqa(image_path, question):
    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    body = json.dumps({"image_b64": b64, "question": question,
                       "max_new_tokens": 256}).encode()
    req = urllib.request.Request(SERVER + "/vqa", data=body,
                                 headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=120) as r:
        res = json.loads(r.read())
    res["latency_s"] = round(time.time() - t0, 2)
    return res


def extract_final(answer, kind):
    """Robustly pull the final answer out of verbose model output."""
    import re
    a = answer.strip()
    if kind == "number":
        m = re.findall(r"Final Answer:?\s*\*{0,2}\s*(\d+(?:\.\d+)?)", a, re.I)
        if m:
            return m[-1]
        m = re.findall(r"(?<![\d.])(\d+(?:\.\d+)?)(?!\d)", a)
        return m[-1] if m else ""
    if kind == "percent":
        m = re.findall(r"Final Answer:?\s*\*{0,2}\s*(\d+(?:\.\d+)?)\s*%?", a, re.I)
        if m:
            return m[-1]
        m = re.findall(r"(\d+(?:\.\d+)?)\s*%", a)
        return m[-1] if m else ""
    if kind == "ab":
        m = re.findall(r"Answer:?\s*\*{0,2}\s*\*{0,2}([AB])", a, re.I)
        if m:
            return m[-1].upper()
        m = re.findall(r"\b([AB])\b", a)
        return m[-1].upper() if m else ""
    if kind == "word":
        low = a.lower()
        for kw in ("sharp", "gradual", "vertical", "sloped"):
            if kw in low:
                return "sharp" if kw in ("sharp", "vertical") else "gradual"
        return ""
    return a


def build_cases():
    os.makedirs(OUT_DIR, exist_ok=True)
    cases = []
    # 1..3: cycle counting
    for n in (2, 3, 5):
        p = os.path.join(OUT_DIR, f"sine_{n}cyc.png")
        sine_image(p, n)
        cases.append({"id": f"sine_{n}cyc", "image": p, "skill": "cycle_count",
                      "question": "How many complete sine-wave cycles are shown? Answer with just a number.",
                      "ground_truth": str(n),
                      "check": lambda a, n=n: extract_final(a, "number") == str(n)})
    # 4: duty cycle 50%
    p = os.path.join(OUT_DIR, "sq_50.png"); square_image(p, 3, 0.5)
    cases.append({"id": "sq_50", "image": p, "skill": "duty_cycle",
                  "question": "What is the duty cycle of this square wave (high-time / period)? Answer as a percentage.",
                  "ground_truth": "50%", "check": lambda a: extract_final(a, "percent") == "50"})
    # 5: duty cycle 25%
    p = os.path.join(OUT_DIR, "sq_25.png"); square_image(p, 4, 0.25)
    cases.append({"id": "sq_25", "image": p, "skill": "duty_cycle",
                  "question": "What is the duty cycle of this square wave (high-time / period)? Answer as a percentage.",
                  "ground_truth": "25%", "check": lambda a: extract_final(a, "percent") == "25"})
    # 6: frequency compare (A=2, B=4 -> B higher)
    p = os.path.join(OUT_DIR, "two_ab.png"); two_sine_image(p, 2, 4)
    cases.append({"id": "two_ab", "image": p, "skill": "freq_compare",
                  "question": "Signal A (blue, top) and signal B (red, bottom) are shown. Which signal has the HIGHER frequency? Answer A or B.",
                  "ground_truth": "B", "check": lambda a: extract_final(a, "ab") == "B"})
    # 7: amplitude (3 divisions p-p)
    p = os.path.join(OUT_DIR, "sine_amp3.png"); sine_image(p, 2, amp_div=3.0)
    cases.append({"id": "sine_amp3", "image": p, "skill": "amplitude",
                  "question": "What is the peak-to-peak amplitude of this sine wave, in vertical grid divisions (each grid square = 1 division)? Answer with a number.",
                  "ground_truth": "6", "check": lambda a: extract_final(a, "number") == "6"})
    # 8: rise edge sharp
    p = os.path.join(OUT_DIR, "rise_sharp.png"); rise_edge_image(p, slow=False)
    cases.append({"id": "rise_sharp", "image": p, "skill": "rise_edge",
                  "question": "Is the rising edge of this signal sharp (near-vertical) or gradual (sloped)? Answer 'sharp' or 'gradual'.",
                  "ground_truth": "sharp", "check": lambda a: extract_final(a, "word") == "sharp"})
    # 9: rise edge gradual
    p = os.path.join(OUT_DIR, "rise_gradual.png"); rise_edge_image(p, slow=True)
    cases.append({"id": "rise_gradual", "image": p, "skill": "rise_edge",
                  "question": "Is the rising edge of this signal sharp (near-vertical) or gradual (sloped)? Answer 'sharp' or 'gradual'.",
                  "ground_truth": "gradual", "check": lambda a: extract_final(a, "word") == "gradual"})
    return cases


def main():
    print(f"baseline_waveform_vqa -> {SERVER}", flush=True)
    cases = build_cases()
    results = []
    correct = 0
    for c in cases:
        res = vqa(c["image"], c["question"])
        ans = res.get("answer", "") if res.get("ok") else "ERR:" + str(res.get("error"))
        ok = bool(c["check"](ans)) if res.get("ok") else False
        correct += ok
        rec = {"id": c["id"], "skill": c["skill"], "question": c["question"],
               "ground_truth": c["ground_truth"], "answer": ans, "correct": ok,
               "latency_s": res.get("latency_s")}
        results.append(rec)
        print(json.dumps(rec, ensure_ascii=False), flush=True)
    by_skill = {}
    for r in results:
        by_skill.setdefault(r["skill"], []).append(r["correct"])
    skill_acc = {k: {"n": len(v), "correct": sum(v),
                     "acc": round(sum(v) / len(v), 4)} for k, v in by_skill.items()}
    summary = {"server": SERVER, "model": "Qwen3.5-2B", "n": len(results), "correct": correct,
               "accuracy": round(correct / max(1, len(results)), 4),
               "skill_acc": skill_acc,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
               "results": results,
               "note": "pre-strengthening baseline; same images/questions reused for post-SFT/RL paired comparison (#4)",
               "instrument_fix": "v1 had (a) freq_compare checker false-negative on verbose output, (b) no grid lines -> 'divisions' unanswerable; v2 adds grid + robust final-answer extraction. duty_cycle errors are genuine model gaps retained."}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "baseline_waveform_vqa_results.json")
    with open(out, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"=== BASELINE n={summary['n']} correct={correct} acc={summary['accuracy']} -> {out}", flush=True)


if __name__ == "__main__":
    main()
