#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_ocr_sft_plan_report.py -- \u8def\u7ebd\u2460\u300cOCR \u4e13\u9879 SFT \u6267\u884c\u65b9\u6848\u300d\u4e2d\u6587 HTML \u62a5\u544a\u751f\u6210\u5668.

\u7528\u6237\u4ee4 (2026-10-25 19:5x): \u628a\u8def\u7ebd\u2460\u7ec6\u5316\u6210\u300c\u53ef\u7167\u7740\u505a\u300d\u7684 OCR \u4e13\u9879 SFT \u6267\u884c\u65b9\u6848\u62a5\u544a.
\u56de\u7b54\u56db\u95ee: \u4e2d\u82f1\u6587\u6bd4\u4f8b / \u6570\u5b66\u516c\u5f0f\u4e09\u901a\u9053 / \u5176\u4ed6\u7c7b\u522b / \u600e\u4e48\u505a(\u53ef\u6267\u884c).
\u8bfb\u53d6\u56db\u81c2 consolidated_12benchmarks.json \u53d6\u57fa\u7ebf(OCRBench/DocVQA/ChartQA/InfoVQA \u53ca\u56de\u5f52\u62a4\u680f MMStar/AI2D/RealWorldQA),
\u751f\u6210 9 \u8282\u81ea\u5305\u542b\u4e2d\u6587 HTML (0 <script> / 0 \u5916\u94fe / \u6807\u7b7e\u914d\u5e73 / \u226518KB), \u542b\u300c\u4e00\u9875\u7eb8\u6267\u884c\u6e05\u5355\u300d.
\u7528\u6cd5:
  python generate_ocr_sft_plan_report.py
"""
import json, os, sys
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.abspath(os.path.join(SCRIPT_DIR, "..", "..", "reports"))  # \u9879\u76ee\u7ea7 reports/
OUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out"
DEFAULT_OUT = os.path.join(REPORTS_DIR, "report_vision_ocr_sft_plan_zh.html")

# \u56db\u81c2\u7ed3\u679c\u76ee\u5f55 (consolidated_12benchmarks.json \u6240\u5728)
ARMS = [
    ("ArmB", "ViT-B/16, AIMv2-style, 3\u6e90/4epoch", os.path.join(OUT_DIR, "mllm_eval_results_armB")),
    ("ArmC", "ViT-B/16, min_lr1e-5+wd0.01", os.path.join(OUT_DIR, "mllm_eval_results_armC_20261018")),
    ("ArmD-R2", "ViT-B/16, 6\u6e90/3epoch, lr1e-3", os.path.join(OUT_DIR, "mllm_eval_results_armD_r2_20261020")),
    ("ArmE-R2", "ViT-L/14, lr5e-4, 63400\u6b65 (\u73b0\u884c\u6700\u4f18\u7f16\u7801\u5668)", os.path.join(OUT_DIR, "mllm_eval_results_armE_r2_20261022")),
]
# OCR \u4e3b\u5224\u636e\u56db\u96c6 (\u5747\u65e0\u9700 LLM judge)
OCR_BENCHES = [
    ("ocrbench", "OCRBench", "ocrbench_accuracy,none", "exact-match \u9010\u9898\u51c6\u786e\u7387"),
    ("docvqa_val", "DocVQA (val)", "anls,none", "ANLS, \u6587\u6863 VQA"),
    ("chartqa", "ChartQA", "relaxed_overall,none", "relaxed accuracy, \u56fe\u8868\u95ee\u7b54"),
    ("infovqa_val", "InfoVQA (val)", "anls,none", "ANLS, \u4fe1\u606f\u56fe VQA"),
]
# \u56de\u5f52\u62a4\u680f\u96c6\u5408 (\u9632\u707e\u96be\u6027\u9057\u5fd8\u76d1\u63a7)
GUARD_BENCHES = [
    ("mmstar", "MMStar", "average,none", "\u7efc\u5408\u89c6\u89c9\u8bc4\u4f0a"),
    ("ai2d", "AI2D", "exact_match,flexible-extract", "u79d1\u5b66\u56fe\u8bc6\u522b"),
    ("realworldqa", "RealWorldQA", "exact_match,flexible-extract", "\u771f\u5b9e\u4e16\u754c QA"),
]

def load_arm(path):
    cj = os.path.join(path, "consolidated_12benchmarks.json")
    if not os.path.exists(cj):
        return None, cj
    with open(cj) as f:
        return json.load(f), cj

def arm_value(data, key):
    r = data.get("results", {})
    v = r.get(key)
    return float(v) if isinstance(v, (int, float)) else None

def fmt_pct(v):
    return f"{v*100:.2f}%" if isinstance(v, (int, float)) else "N/A"

# ===================== \u6570\u636e\u5b57\u5178 (\u8ba1\u5212\u4e13\u7528, \u786e\u5b9a\u6027, \u91cd\u8dd1 diff \u4e3a\u7a7a) =====================
# \u57fa\u7ebd\u7248 OCRBench = ArmE-R2 \u73b0\u884c\u6700\u4f18\u7f16\u7801\u5668\u7684 Stage-2 step3500 \u8bc4\u6d4b\u503c (1.60%), \u4e3b\u5224\u636e OCRBench>=+2pp \u5373 >=3.60%.
BASELINE_REF = "ArmE-R2 Stage-2 step3500 (\u73b0\u884c\u6700\u4f18\u7f16\u7801\u5668, ViT-L/14, 256 patch tokens, 224px \u5355\u5757)"

# Q1 \u4e2d\u82f1\u6587\u6bd4\u4f8b \u2014 \u5019\u9009\u914d\u6bd4
CANDIDATE_RATIOS = [
    dict(name="A \u57fa\u7ebd\u914d\u6bd4", split="\u82f1\u6587 6 : \u4e2d\u6587 3 : \u4e2d\u82f1\u6df7\u6392 1",
        rationale="\u82f1\u6587\u4e3b\u5bfc: OCRBench/DocVQA/InfoVQA \u4ee5\u82f1\u6587\u4e3a\u4e3b, \u4e2d\u6587\u8865\u8db3\u5b9e\u9645\u843d\u5730, \u6df7\u6392\u6d4b\u8bd5\u8de8\u8bed\u79fb\u5f3a; \u4e0e\u73b0\u6709 LLaVA-NeXT-780k \u82f1\u6587\u4e3b\u4f53\u4e0d\u51b2\u7a81",
        cond="\u9002\u7528: \u4e3b\u8981\u9762\u5411 OCRBench/DocVQA \u8fd9\u7c7b\u82f1\u6587\u4e3b\u96c6; \u5224\u636e = OCRBench \u52a8\u5e45 \u2265 DocVQA \u52a8\u5e45",
        judge="\u82f1\u6587\u5b50\u96c6 OCRBench \u52a0\u6743\u5206\u6570 \u2265 \u4e2d\u6587\u5b50\u96c6\u7684 1.5\u00d7 \u2192 \u9009\u4e2d A"),
    dict(name="B \u4e2d\u82f1 1:1", split="\u4e2d\u6587 5 : \u82f1\u6587 4 : \u6df7\u6392 1",
        rationale="\u4e2d\u82f1\u5747\u8861: \u5168\u91cf\u4e2d\u6587\u8bed\u6599\u6613\u5f97(\u7ef4\u57fa/\u5f00\u6e90\u4e66\u7c4d/CC), \u80fd\u76f4\u63a5\u62d3\u5bbd\u4e2d\u6587 OCR \u843d\u5730\u573a\u666f; \u98ce\u9669 = \u82f1\u6587\u4e3b\u96c6(OCRBench)\u52a0\u6743\u4e0d\u8db3\u53ef\u80fd\u4e0d\u8fbe +2pp",
        cond="\u9002\u7528: \u9700\u540c\u65f6\u62d3\u5bbd\u4e2d\u6587\u6587\u6863\u573a\u666f, \u4e14\u7528\u6237\u660e\u786e\u8981\u4e2d\u6587\u80fd\u529b",
        judge="\u4e2d\u6587\u5b50\u96c6 DocVQA-style \u52a0\u6743\u5206\u6570 \u2265 \u82f1\u6587\u5b50\u96c6\u7684 1.2\u00d7 \u4e14 OCRBench \u4ecd \u2265+2pp \u2192 \u9009\u4e2d B"),
]
BASELINE_RATIO_TABLE = [
    ("\u7eaf\u82f1\u6587\u8bcd\u5361/\u53e5\u5b50\u8bc6\u522b", "45\u4e07 (30%)", "trdg + \u82f1\u6587\u8bed\u6599(\u7ef4\u57fa/CC12M\u8bcd\u8868)", "\u62b9\u5e73 OCRBench \u4e3b\u573a\u5730, \u6837\u672c\u5bc6\u5ea6\u6700\u9ad8"),
    ("\u7eaf\u4e2d\u6587\u8bcd\u5361/\u53e5\u5b50\u8bc6\u522b", "30\u4e07 (20%)", "trdg + \u4e2d\u6587\u8bed\u6599(\u7ef4\u57fa/\u4e66\u7c4d\u8bed\u6599)", "\u62d3\u5bbd\u4e2d\u6587\u843d\u5730, \u5b57\u4f53\u8986\u76d6\u5e7f"),
    ("\u4e2d\u82f1\u6df7\u6392\u53e5/\u6bb5", "15\u4e07 (10%)", "\u81ea\u7814\u6e32\u67d3\u5668(\u6df7\u6392\u6a21\u677f)", "\u6d4b\u8bd5\u8de8\u8bed\u79fb\u5f3a, \u9632\u6b62\u5355\u8bed\u79cd\u8fc7\u62df\u5408"),
    ("\u6587\u6863\u7248\u9762(\u6807\u9898/\u5206\u680f/\u8868\u683c)", "22.5\u4e07 (15%)", "\u81ea\u7814\u6e32\u67d3\u5668(HTML\u2192\u622a\u56fe)", "DocVQA/InfoVQA \u4e3b\u573a\u5730"),
    ("\u56fe\u8868(\u67f1/\u6298/\u9985+\u6570\u503c\u6807\u7b7e)", "15\u4e07 (10%)", "matplotlib/pyplot \u6e32\u67d3", "ChartQA \u4e3b\u573a\u5730"),
    ("\u6570\u5b66\u516c\u5f0f(\u4e09\u901a\u9053\u5408\u8ba1)", "15\u4e07 (10%)", "LaTeX/KaTeX \u6e32\u67d3", "\u516c\u5f0f\u8bc6\u522b, P1"),
    ("\u4f4e\u8d28/\u624b\u5199/\u573a\u666f\u6587\u672c/\u4ee3\u7801\u622a\u56fe", "7.5\u4e07 (5%)", "\u9000\u5316\u7ba1\u7ebf\u53e0\u52a0", "\u9c81\u68d2\u6027, P2"),
]
# Q2 \u6570\u5b66\u516c\u5f0f\u4e09\u901a\u9053
FORMULA_CHANNELS = [
    dict(name="(a) \u7eaf\u516c\u5f0f\u56fe", tool="im2latex / LaTeX \u672c\u5730\u6e32\u67d3(latexmk+dvipng \u6216 MathJax-node)",
        items="\u884c\u5185\u516c\u5f0f / \u591a\u884c\u516c\u5f0f / \u77e9\u9635 / \u4e0a\u4e0b\u6807 / \u5206\u5f0f / \u6c42\u548c\u7b26\u53f7",
        inputs="\u5f00\u6e90 LaTeX \u8bed\u6599(arXiv \u6e90\u7801/\u6570\u5b66\u6559\u6750\u6e90\u7801); \u5b57\u4f53=Computer Modern/STIX; \u5206\u8fa8\u7387 96-150dpi",
        budget="\u5360 OCR \u603b\u9884\u7b97\u7684 ~5% (\u7ea6 7.5\u4e07\u5f20); \u6bcf\u5f20\u7ea6 8-25 tokens \u7b49\u4ef7\u4e8e\u7ea6 200 \u5f20\u666e\u901a\u6587\u672c\u56fe",
        fail="\u6e32\u67d3\u5931\u8d25\u7387\u63a7\u5236: \u672c\u5730\u6e32\u67d3\u5668\u5148 dry-run \u6392\u9664\u62a5\u9519\u516c\u5f0f, \u5f03\u7528\u4e0d\u6392\u7248\u4e4b\u539f\u5b50; \u76ee\u6807\u5931\u8d25\u7387 <=2%"),
    dict(name="(b) \u6b63\u6587\u5939\u516c\u5f0f", tool="arXiv LaTeX \u6bb5\u843d \u2192 KaTeX/MathJax(puppeteer/headless) \u6e32\u67d3\u6210\u6574\u9875\u56fe",
        items="\u4e00\u9875\u4e2d\u6df7\u5408\u666e\u901a\u6587\u672c+\u884c\u5185/\u72ec\u884c\u516c\u5f0f, \u8d34\u8fd1\u771f\u5b9e\u8bba\u6587\u7248\u9762",
        inputs="\u5f00\u6e90 arXiv \u6587\u672c\u6e90\u7801(CC-BY/CC-0 \u5b50\u96c6); \u7eb8\u8d28\u80cc\u666f\u6a21\u677f; \u6807\u9898/\u4f5c\u8005\u884c",
        budget="\u5360 ~3% (\u7ea6 4.5\u4e07\u9875); \u6bcf\u9875\u7ea6 100-300 tokens, \u4f46\u542b\u516c\u5f0f\u7ed3\u6784\u4fe1\u606f\u5bc6\u5ea6\u9ad8",
        fail="KaTeX \u672a\u652f\u6301\u7684\u5b8f\u56de\u9000\u5230\u7eaf\u6587\u672c; \u5931\u8d25\u7387\u63a7 <=5%"),
    dict(name="(c) \u516c\u5f0f+\u8868\u683c\u6df7\u6392", tool="\u81ea\u7814\u6e32\u67d3\u5668: LaTeX \u516c\u5f0f\u5757 + HTML \u8868\u683c\u5408\u6210\u540c\u4e00\u9875\u540e\u622a\u56fe",
        items="\u542b\u5408\u5e76\u5355\u5143\u683c\u7684\u8868\u683c + \u516c\u5f0f\u884c\u5217, \u6d4b\u8bd5\u7248\u9762\u89e3\u6790\u4e0e\u516c\u5f0f\u89e3\u6790\u8054\u52a8",
        inputs="\u81ea\u5efa\u6a21\u677f(\u8868\u683c\u7ed3\u6784\u751f\u6210\u5668 + \u516c\u5f0f\u8bed\u6599); \u622a\u56fe 150dpi",
        budget="\u5360 ~2% (\u7ea6 3\u4e07\u9875); \u6700\u96be\u7c7b, \u4f18\u5148\u7ea7 P1(\u975e P0)",
        fail="\u8868\u683c\u8de8\u9875\u65ad\u88c2\u68c0\u6d4b\u540e\u4e22\u5f03; \u5931\u8d25\u7387\u63a7 <=8%"),
]
FORMULA_OCRBENCH_NOTE = ("OCRBench \u539f\u7248\u542b\u624b\u5199\u4e0e\u5370\u5237\u4f53\u5b50\u5b50\u96c6, \u4f46\u65e0\u72ec\u7acb\u300c\u6570\u5b66\u516c\u5f0f\u300d\u5b50\u7c7b\u516c\u5f00\u62bd\u5206; "
    "\u6545\u516c\u5f0f\u901a\u9053\u76f4\u63a5\u4f5c\u7528\u4e8e\u603b\u5206\u4f53, \u4e0d\u671f\u671b\u300c\u516c\u5f0f\u5b50\u96c6\u300d\u72ec\u7acb\u62ac\u5347. "
    "\u6570\u5b66\u516c\u5f0f\u7684\u4e3b\u4ef7\u503c\u5728\u4e8e\u62d3\u5bbd\u7b26\u53f7\u8bcd\u8868(\u4e0a\u4e0b\u6807/\u5e0c\u814a\u5b57\u6bcd/\u7b26\u53f7)\u4e0e\u7248\u9762\u89e3\u6790, \u4e3a MathVista/\u8bba\u6587\u7406\u89e3\u505a\u94fa\u57ab.")
# Q3 \u5176\u4ed6\u7c7b\u522b (\u4f18\u5148\u7ea7 P0-P2, \u6570\u91cf, \u5224\u636e)
OTHER_CATEGORIES = [
    dict(cat="\u6587\u6863\u7248\u9762(\u6807\u9898/\u5206\u680f/\u9875\u7709\u9875\u811a)", n="20\u4e07", pri="P0", judge="DocVQA(val) ANLS \u52a0\u6743\u5b50\u96c6 \u2265 +1pp"),
    dict(cat="\u8868\u683c(\u542b\u5408\u5e76\u5355\u5143\u683c)", n="8\u4e07", pri="P0", judge="InfoVQA(val) ANLS \u52a0\u6743\u5b50\u96c6 \u2265 +0.8pp"),
    dict(cat="\u56fe\u8868(\u67f1/\u6298/\u9985 + \u6570\u503c\u6807\u7b7e)", n="12\u4e07", pri="P0", judge="ChartQA relaxed \u52a0\u6743\u5b50\u96c6 \u2265 +1pp"),
    dict(cat="\u573a\u666f\u6587\u672c(\u62db\u724c/\u8def\u724c/\u5305\u88c5)", n="6\u4e07", pri="P1", judge="RealWorldQA \u4e0d\u9000\u5316\u8d85 0.5pp \u4e14\u4e3b\u89c2\u62bd\u6837\u6539\u5584"),
    dict(cat="\u4f4e\u8d28(\u6a21\u7cca/\u503e\u659c/\u900f\u89c6/\u538b\u7f29/\u4f4e\u5206\u8fa8)", n="\u8d34\u5728\u4e0a\u8ff0\u6bcf\u7c7b 20%\u9886\u6837\u672c", pri="P0", judge="\u9000\u5316\u5b50\u96c6 OCRBench \u52a0\u6743\u9ad8\u4e8e\u5e72\u51c0\u5b50\u96c6 \u2192 \u8bc1\u660e\u9c81\u68d2\u6027\u6709\u6548"),
    dict(cat="\u4ee3\u7801\u622a\u56fe(\u7f29\u8fdb/\u8bed\u6cd5\u9ad8\u4eae)", n="3\u4e07", pri="P2", judge="\u4e0d\u8bbe\u72ec\u7acb\u5224\u636e, \u9632\u8fc7\u62df\u5408\u5360\u4f4f\u9884\u7b97"),
    dict(cat="\u7ad6\u6392\u4e0e\u591a\u8bed\u79cd(\u65e5\u97e9/\u7e41\u4e2d)", n="3\u4e07", pri="P2", judge="\u4ec5\u9c81\u68d2\u6027\u5360\u4f4d, \u4e0d\u8bbe\u4e3b\u5224\u636e"),
    dict(cat="\u624b\u5199\u4f53", n="4\u4e07", pri="P1", judge="OCRBench \u624b\u5199\u5b50\u96c6\u52a0\u6743\u52a0\u6743\u4e0d\u4e0b\u964d"),
]

# Q4 \u751f\u6210\u7ba1\u7ebf\u53c2\u6570
PIPELINE_PARAMS = [
    dict(tool="trdg", role="\u8bcd\u5361/\u53e5\u5b50\u7ea7\u8bc6\u522b\u5bf9 (\u4e3b\u529b)",
        params="-c <count> -w <words_per_img> -f 64(\u9ad8\u5ea6) -k 5 -rk(\u968f\u673a\u503e\u659c) -bl 2 -rbl(\u9ad8\u65af\u6a21\u7cca) -d 2 -do(\u626d\u66f2) -b 0/1/2/3(\u80cc\u666f: \u9ad8\u65af\u566a\u58f0/\u7eaf\u767d/\u51c6\u6676/\u56fe\u50cf) --font_dir <\u5b57\u4f53\u96c6> --output_mask",
        fonts="\u82f1\u6587: DejaVu/FreeFont/Google Noto; \u4e2d\u6587: Noto Sans CJK/Source Han Sans; \u624b\u5199\u6a21\u62df: \u9009\u7528\u624b\u5199\u98ce\u5b57\u4f53 + \u4f4e\u89c4\u5219\u6296\u52a8",
        corpus="\u82f1\u6587: \u7ef4\u57fa\u8bcd\u8868/CC12M\u53e5\u5b50; \u4e2d\u6587: \u7ef4\u57fa\u4e2d\u6587/\u5f00\u6e90\u4e66\u7c4d\u8bed\u6599",
        label="\u56fe\u50cf + ground_truth.txt(\u6bcf\u884c: imgpath<TAB>text)"),
    dict(tool="SynthTIGER", role="\u9ad8\u591a\u6837\u6027\u6587\u5b57\u56fe\u8865\u5145 (\u8bd5\u9a8c\u6027, \u4e30\u5bcc\u9000\u5316)",
        params="\u914d\u7f6e: \u5b57\u4f53\u91c7\u6837/\u989c\u8272/\u95f4\u8ddd/\u5f62\u53d8\u5e8f\u5217; \u80cc\u666f\u7eb9\u7406/\u900f\u89c6; \u9000\u5316\u7ba1\u7ebf\u53e0\u52a0",
        fonts="\u540c trdg \u5b57\u4f53\u96c6\u5171\u7528",
        corpus="\u540c trdg \u8bed\u6599\u5171\u7528; \u53ef\u63a5\u5165 SynthTIGER \u5b98\u65b9\u8bed\u6599",
        label="\u540c trdg \u683c\u5f0f; \u53ef\u8f93\u51fa\u5b57\u7b26\u7ea7 bbox + mask"),
    dict(tool="\u81ea\u7814\u6e32\u67d3\u5668 (HTML\u2192\u622a\u56fe)", role="\u6587\u6863\u7248\u9762/\u8868\u683c/\u56fe\u8868/\u516c\u5f0f+\u8868\u683c\u6df7\u6392",
        params="Playwright headless \u622a\u56fe 150dpi; HTML \u6a21\u677f\u9a8c\u8bc1\u4e0d\u8de8\u9875; \u9000\u5316\u540e\u5904(PIL \u9ad8\u65af/\u91cf\u5316/JPEG\u538b\u7f29/\u968f\u673a\u88c1\u526a)",
        fonts="\u540c\u4e0a",
        corpus="\u7ef4\u57fa/\u5f00\u6e90\u4e66\u7c4d/\u81ea\u5efa\u6a21\u677f\u8bed\u6599",
        label="\u56fe\u50cf + JSON(\u542b bbox/\u95ee\u7b54\u5bf9) \u2192 \u8f6c VQA \u5bf9\u683c\u5f0f"),
    dict(tool="matplotlib/pyplot", role="\u56fe\u8868\u751f\u6210",
        params="\u968f\u673a\u751f\u6210\u6570\u636e\u2192\u67f1/\u6298/\u9985\u56fe; \u6570\u503c\u6807\u7b7e\u8d34\u5728\u7ebf/\u67f1; \u989c\u8272\u968f\u673a; \u4fdd\u5b58 PNG",
        fonts="\u540c\u4e0a",
        corpus="\u968f\u673a\u6570\u503c\u751f\u6210\u5668",
        label="\u56fe\u50cf + Q/A \u5bf9(\u95ee:\u300c\u67f1\u9ad8\u5ea6\u300d \u7b54:\u6570\u503c)"),
    dict(tool="LaTeX/KaTeX \u6e32\u67d3", role="\u6570\u5b66\u516c\u5f0f\u4e09\u901a\u9053",
        params="(a) latexmk+dvipng 150dpi; (b) MathJax-node/puppeteer \u6574\u9875; (c) \u5408\u6210\u540e Playwright \u622a\u56fe",
        fonts="Computer Modern / STIX / Latin Modern",
        corpus="arXiv \u6e90\u7801(CC-BY/CC-0 \u5b50\u96c6)/\u6570\u5b66\u6559\u6750 LaTeX",
        label="\u56fe\u50cf + LaTeX \u6e90\u4e32(\u4f5c\u4e3a ground truth)"),
]
# SFT \u914d\u65b9 (\u4e25\u683c\u5bf9\u9f50\u73b0\u6709 stage2_train_armE_r2.py \u53e3\u5f84)
SFT_RECIPE = dict(
    start_ckpt="ArmE-R2 \u5168\u94fe\u6700\u7ec8(Stage-2 step3500): vision tower ViT-L/14(\u51bb\u7ed3) + projector 1024\u21922560 + LoRA r=64 + Qwen3-4B-Instruct",
    approach="\u65b0\u589e\u300cStage-2.5 OCR \u4e13\u9879 SFT\u300d: \u5728 Stage-2 \u6700\u7ec8 ckpt \u4e0a\u7ee7\u7eed\u8bad\u7ec3, \u4e0d\u52a8 vision tower(\u51bb\u7ed3), \u53ea\u66f4\u65b0 projector + LoRA",
    lora="r=64, alpha=128, dropout=0.05 (\u4e0e Stage-1.5/2 \u4e00\u81f4, \u590d\u7528\u73b0\u6709\u914d\u7f6e)",
    lr="LoRA 1e-5, projector 5e-6, cosine\u21921e-7, warmup 0.01 (\u540c Stage-2 \u8d77\u70b9, \u9632\u6b62\u9057\u5fd8\u8fc7\u5feb)",
    steps="P0 pilot: 2000 \u6b65(20\u4e07\u6837\u672c/GBS=8\u22482500\u6b65\u53d6\u6574); P1 \u5168\u91cf: 8000-12000 \u6b65",
    gbs="GBS=8, MBS=1 (\u4e0e Stage-2 \u4e00\u81f4, \u663e\u5b58\u5b89\u5168)",
    image="224\u00d7224 \u5355\u5757, 256 patch tokens, CLIP norm, \u65e0 spatial merge (\u540c Stage-2; 336+anyres \u4e3a\u963b\u585e\u9879, \u89c1\u4e0b)",
    full_vs_lora="\u63a8\u8350 LoRA \u7ee7\u7eed(\u53c2\u6570\u5c0f\u3001\u9632\u9057\u5fd8\u3001\u4e0e\u73b0\u6709\u94fe\u4e00\u81f4); \u82e5 pilot \u4e0d\u8fbe\u6807\u4e14\u6000\u7591\u5bb9\u91cf\u4e0d\u8db3, \u518d\u8003\u8651\u5168\u53c2(\u9700\u8fd0\u7ef4\u6279\u51c6)",
    res_336_note="336+anyres \u9700\u5de5\u7a0b\u6539\u9020 mllm_bridge(\u52a8\u6001 num_image_tokens \u00d7 \u591a\u5757\u62fc\u63a5) + scope \u6279\u51c6, \u5c5e\u963b\u585e\u9879; \u82e5\u6279\u51c6, \u589e\u91cf\u6536\u76ca\u4f30\u8ba1 = DocVQA/InfoVQA \u989d\u5916 +0.5~1.5pp(\u4f30\u7b97, \u6e90\u4e8e\u516c\u5f00 MLLM \u5206\u8fa8\u7387\u6d88\u878d\u62a5\u544a)",
)
# \u4e0e Stage-2 780k \u6df7\u5408\u7b56\u7565 (\u9632\u707e\u96be\u6027\u9057\u5fd8)
MIXING_STRATEGY = [
    dict(plan="P0 pilot (20\u4e07)", mix="OCR \u65b0\u6570\u636e 100% (\u4e0d\u6df7 780k, \u7eaf\u63a2\u9488\u770b\u662f\u5426\u80fd\u52a8)"),
    dict(plan="P1 \u5168\u91cf (150\u4e07)", mix="OCR \u65b0\u6570\u636e 70% : Stage-2 780k \u91c7\u6837 30% (\u91c7\u6837\u540c\u6837\u672c\u91cf\u7ea6 50\u4e07), \u9632\u9057\u5fd8"),
    dict(plan="P2 \u6df7\u5408\u518d\u8c03 (\u82e5 P1 \u62a4\u680f\u9000\u5316)", mix="OCR 60% : 780k 40%, \u6216\u63d0\u9ad8 780k \u4e2d\u539f\u6709 OCR/\u6587\u6863\u6837\u672c\u6743\u91cd"),
]
# \u6210\u672c\u4f30\u7b97 (\u5747\u6807\u300c\u4f30\u7b97\u300d)
COST_EST = [
    dict(stage="P0 pilot \u6e32\u67d3", data="20\u4e07\u5bf9", render_cpu="\u224820 CPU\u00b7\u6838\u00b7\u65f6 (trdg \u7ea6 1\u4e07/s/CPU\u6838; \u7248\u9762/\u516c\u5f0f\u8f83\u6162, \u52a0\u6743\u540e\u22480.5\u4e07/s)", storage="\u22483 GB", train_gpu="\u22482 GPU\u00b7\u5361\u00b7\u65f6 (2000\u6b65, 8\u5361 H100)", eta="\u5f53\u5929\u5185(\u6e32\u67d3~3h + \u8bad\u7ec3~2h + \u8bc4\u6d4b~1h)"),
    dict(stage="P1 \u5168\u91cf\u6e32\u67d3", data="150\u4e07\u5bf9", render_cpu="\u2248150 CPU\u00b7\u6838\u00b7\u65f6 (\u591a\u673a\u5668\u5e76\u884c, \u907f\u8ba9\u8bad\u7ec3\u5361 .12/.29 I/O)", storage="\u224822 GB", train_gpu="\u224812-18 GPU\u00b7\u5361\u00b7\u65f6 (8000-12000\u6b65, 8\u5361 H100)", eta="\u6e32\u67d3\u4e00\u592c\u591c + \u8bad\u7ec3~1\u5929 + \u8bc4\u6d4b~1h"),
    dict(stage="P2 SFT+\u8bc4\u6d4b", data="\u540c P1", render_cpu="-", storage="-", train_gpu="\u542b\u4e8e P1", eta="\u542b\u4e8e P1"),
]
# \u9884\u6ce8\u518c\u5224\u636e
CRITERIA = dict(
    primary="OCRBench \u2265 +2pp (\u57fa\u7ebf ArmE-R2 1.60% \u2192 \u76ee\u6807 \u2265 3.60%)",
    secondary=["DocVQA(val) \u2265 +1pp (\u57fa\u7ebf 7.35% \u2192 \u2265 8.35%)",
               "ChartQA \u2265 +1pp (\u57fa\u7ebf 12.16% \u2192 \u2265 13.16%)",
               "InfoVQA(val) \u2265 +1pp (\u57fa\u7ebf 16.18% \u2192 \u2265 17.18%)"],
    guard=["MMStar \u9000\u5316 \u2264 1pp (\u57fa\u7ebf ArmE-R2 \u2196, \u5f85\u8bfb\u6570\u636e)",
           "AI2D \u9000\u5316 \u2264 1pp (\u57fa\u7ebf ArmE-R2 \u2196)",
           "RealWorldQA \u9000\u5316 \u2264 1pp (\u57fa\u7ebf ArmE-R2 45.49%)",
           "MMBench(en_dev_static) \u9000\u5316 \u2264 1pp (\u57fa\u7ebf ArmE-R2 23.88%, \u5355\u72ec\u8c03\u7528)"]
)
# \u51b3\u7b56\u6811
DECISION_TREE = [
    "P0 pilot(20\u4e07, 2000\u6b65, \u4e0d\u6df7 780k) \u2192 \u6d4b OCRBench/DocVQA/ChartQA/InfoVQA + \u56db\u62a4\u680f",
    "  \u251c\u2500 \u4e3b\u5224\u636e OCRBench \u2265 +2pp \u4e14\u62a4\u680f\u5168\u8fc7 \u2192 \u8fdb P1 \u5168\u91cf(150\u4e07, 70%OCR:30%780k)",
    "  \u251c\u2500 OCRBench +0.5~2pp \u4f46\u62a4\u680f\u9000\u5316\u8d85 1pp \u2192 \u9000\u4e00\u6b65: \u6df7 30% 780k \u91cd\u8dd1 P0, \u5224\u62a4\u680f\u662f\u5426\u6062\u590d",
    "  \u251c\u2500 OCRBench < +0.5pp (\u51e0\u4e4e\u4e0d\u52a8) \u2192 \u6539\u4e00\u7ef4: \u2460\u63d0\u9ad8\u4e2d\u6587\u5360\u6bd4(\u8bd5 B \u914d\u6bd4) \u2461\u589e\u52a0\u9000\u5316\u9886\u6837\u6bd4\u4f8b \u2462\u63d0\u9ad8\u5206\u8fa8\u7387(\u82e5\u6279\u51c6 336) \u2192 \u518d\u8dd1\u4e00\u6b21 P0",
    "  \u2514\u2500 \u4e24\u6b21\u8c03\u6574\u540e\u4ecd\u4e0d\u8fbe\u6807 \u2192 \u505c\u5e76\u5199\u8d1f\u9762\u7ed3\u8bba(\u8bb0\u5f55\u54ea\u4e00\u7ef4\u8c03\u8fc7\u3001\u7ed3\u679c), \u4e0d\u7ee7\u7eed\u70e7\u8d44\u6e90",
]
# \u98ce\u9669\u4e0e\u5751
RISKS = [
    dict(r="\u57df\u5dee\u592a\u5927: \u5408\u6210\u56fe\u8fc7\u4e8e\u5e72\u51c0, \u6a21\u578b\u5b66\u5230\u300c\u5408\u6210\u5370\u300d\u800c\u975e\u771f\u5b9e\u6587\u6863", m="\u91cd\u9000\u5316\u7ba1\u7ebf(\u6a21\u7cca/\u900f\u89c6/\u538b\u7f29/\u80cc\u666f\u7eb9\u7406), \u4fdd\u6301 \u226520% \u5e26\u9000\u5316\u9886\u6837"),
    dict(r="\u5b57\u4f53\u4e0e\u8bed\u8a00\u8986\u76d6: \u4e2d\u6587\u5b57\u4f53\u96c6\u4e0d\u5168 \u2192 \u751f\u5487\u5b57\u53d8\u4f53\u8bc6\u522b\u5dee", m="\u7528 Noto Sans CJK + Source Han \u5168\u91cf\u5b57\u91cd; \u542b \u7b80/\u7e41 \u4e24\u5957"),
    dict(r="\u6e32\u67d3\u4f2a\u5f71: \u6297\u952f\u9f7f/\u8fb9\u7f18\u8fc7\u9510 \u2192 \u4e0e\u771f\u5b9e\u626b\u63cf\u4ef6\u4e0d\u540c\u5206\u5e03", m="\u53c2\u6570\u968f\u673a\u5316 + \u9884\u68c0\u67e5\u8fb9\u7f18\u9510\u5ea6\u5206\u5e03"),
    dict(r="\u8bc4\u6d4b\u6cc4\u6f0f: OCRBench/ChartQA \u53ef\u80fd\u542b\u4e0e\u5408\u6210\u8bed\u6599\u91cd\u53e0\u7684\u6587\u672c", m="\u8bed\u6599\u4e0d\u53d6 OCRBench/ChartQA/DocVQA/InfoVQA \u7684\u539f\u6587; \u516c\u5f0f\u8bed\u6599\u53d6 arXiv \u4e0d\u53d6\u4e0a\u8ff0\u8bc4\u6d4b\u96c6"),
    dict(r="\u707e\u96be\u6027\u9057\u5fd8: \u4e13\u9879 SFT \u538b\u574e\u539f\u6709\u80fd\u529b(MMStar/AI2D \u9000\u5316)", m="\u6df7\u5408 30% 780k + \u62a4\u680f\u76d1\u63a7 + LoRA \u800c\u975e\u5168\u53c2"),
    dict(r="\u516c\u5f0f token \u9884\u7b97\u543e: \u516c\u5f0f\u56fe token \u5360\u6bd4\u8fc7\u9ad8\u6324\u538b\u5176\u4ed6\u7c7b\u522b", m="\u516c\u5f0f\u603b\u5360 \u226410%, (a)5%(b)3%(c)2%; \u4e0d\u8d85 15\u4e07"),
    dict(r="\u8bad\u7ec3\u5361 I/O \u51b2\u7a81: \u6e32\u67d3\u91cd I/O \u5f71\u54cd .12/.29 \u8bad\u7ec3", m="\u6e32\u67d3\u8d70\u5176\u4ed6\u673a\u5668/\u591c\u95f4, \u5b58\u5230 NFS \u540e\u518d\u542f\u8bad\u7ec3"),
]
# \u53c2\u8003\u6765\u6e90 (\u7eaf\u6587\u672c arXiv \u53f7, \u7981\u8d85\u94fe; \u68c0\u7d22/\u6838\u5b9e\u4e8e 2026-10-25)
REFERENCES = [
    "SynthTIGER \u2014 Liu et al., \u300cSynthTIGER: Synthetic Text Image GEnerator Towards Better Text Recognition\u300d, arXiv:2107.09313, 2021",
    "SynthText \u2014 Gupta et al., \u300cSynthetic Data for Text Localisation in Natural Images\u300d, arXiv:1604.06646, 2016",
    "trdg (TextRecognitionDataGenerator) \u2014 Belval, GitHub \u5f00\u6e90\u5de5\u5177, \u65e0\u5355\u4e00 arXiv, 2018-",
    "Donut / SynthDoG \u2014 Kim et al., \u300cOCR-free Document Understanding Transformer\u300d, arXiv:2111.15664, 2021",
    "UDOP \u2014 Tang et al., \u300cUnifying Vision, Text, and Layout for Universal Document Processing\u300d, arXiv:2212.02623, 2022",
    "Pix2Struct \u2014 Lee et al., \u300cPix2Struct: Screenshot Parsing as Pretraining for Visual Language Modeling\u300d, arXiv:2210.03347, 2022",
    "Nougat \u2014 Blecher et al., \u300cNougat: Neural Optical Understanding for Academic Documents\u300d, arXiv:2308.13418, 2023",
    "mPLUG-DocOwl \u2014 Ye et al., \u300cmPLUG-DocOwl: Modularized Multimodal Large Language Model for Document Understanding\u300d, arXiv:2307.02499, 2023",
    "dots.ocr \u2014 arXiv:2512.02498, 2025",
    "ChartQA \u2014 Masry et al., \u300cChartQA: A Benchmark for Question Answering about Charts\u300d, arXiv:2203.10244, 2022",
    "Chart-to-Text \u2014 Kantharaj et al., arXiv:2203.06486, 2022",
    "olmOCR \u2014 arXiv:2502.18443, 2025",
    "Visual-RFT \u2014 arXiv:2503.01785, 2025",
    "\u5185\u90e8\u5197\u4f59\u81ea\u8bad\u7ec3 OCR \u2014 arXiv:2508.14557, 2025",
    "PaddleOCR \u2014 \u5de5\u4e1a\u5de5\u5177\u5305(\u65e0\u5355\u4e00 arXiv), 2020-",
    "im2latex-100K \u2014 \u6570\u636e\u96c6/\u9879\u76ee, \u672a\u67e5\u5230\u5355\u4e00 arXiv \u6807\u9898\u9875, 2017",
    "GOT-OCR2.0 \u2014 \u672a\u67e5\u5230 arXiv \u6807\u9898\u9875(\u7f16\u53f7/\u540d\u79f0\u5b58\u7591, \u672c\u6b21\u68c0\u7d22\u672a\u547d\u4e2d), 2024",
    "LLaVA-NeXT \u2014 Liu et al., \u300cImproved Baselines with Visual Instruction Tuning\u300d\u7cfb\u5217, \u672c\u9879\u76ee Stage-2 \u7528\u5176 780k quick-start \u5b50\u96c6(738588 \u6837\u672c)",
]
# \u4e00\u9875\u7eb8\u6267\u884c\u6e05\u5355 (\u4eca\u5929\u5c31\u80fd\u5f00\u59cb\u7684\u7b2c\u4e00\u6b65)
CHECKLIST = [
    ("\u2460 \u5b89\u88c5", "pip install trdg Pillow playwright; playwright install chromium (\u7248\u9762\u622a\u56fe\u7528)"),
    ("\u2461 \u5b57\u4f53", "\u4e0b Google Noto Sans CJK + Source Han Sans + DejaVu/FreeFont \u5168\u5b57\u91cd, \u653e <font_dir>"),
    ("\u2462 \u8bed\u6599", "\u5907\u7ef4\u57fa\u82f1\u6587/\u4e2d\u6587\u8bcd\u8868 + CC12M \u53e5\u5b50\u91c7\u6837 + arXiv CC-BY/CC-0 LaTeX \u5b50\u96c6"),
    ("\u2463 \u5192\u70df", "trdg -c 10000 -w 1 -f 64 -k 5 -rk -bl 2 -rbl -b 0 --font_dir <dir> -o /tmp/ocr_smoke \u2192 \u68c0\u67e5 1\u4e07\u5f20\u8d27\u6837"),
    ("\u2464 \u9a8c\u6536\u770b", "\u770b <out>/labels.txt(\u56fe\u6587\u5bf9\u9f50) + \u62bd\u6837 50\u5f20\u56fe\u4eba\u773c\u770b\u9000\u5316\u662f\u5426\u81ea\u7136"),
    ("\u2465 \u4e0b\u4e00\u6b65", "\u5192\u70df\u8fc7\u2192\u6269\u5230 20\u4e07(P0 pilot)\u2192\u542f\u52a8 Stage-2.5 OCR SFT(2000\u6b65)\u2192\u6d4b OCRBench \u770b\u662f\u5426\u52a8"),
]

def esc(s):
    return escape(str(s))

def render(out_path):
    # load baselines
    arm_data = []
    for name, desc, path in ARMS:
        data, cj = load_arm(path)
        arm_data.append((name, desc, data, cj))
    def bench_row(key, label, metric, note):
        cells = []
        for name, desc, data, cj in arm_data:
            v = arm_value(data, key) if data else None
            cells.append(fmt_pct(v))
        return (label, metric, *cells, note)
    H = []
    H.append('<!DOCTYPE html>')
    H.append('<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    H.append(f'<title>BaiZe Vision: \u8def\u7ebd\u2460 OCR \u4e13\u9879 SFT \u6267\u884c\u65b9\u6848\u62a5\u544a</title>')
    H.append('<style>')
    H.append('body{font-family:-apple-system,\'PingFang SC\',\'Microsoft YaHei\',sans-serif;max-width:1100px;margin:24px auto;padding:0 20px;color:#222;line-height:1.62}')
    H.append('h1{font-size:22px;border-bottom:3px solid #1a5276;padding-bottom:8px}')
    H.append('h2{font-size:18px;margin-top:30px;border-left:5px solid #1a5276;padding-left:10px}')
    H.append('h3{font-size:15px;margin-top:18px;color:#15435a}')
    H.append('table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}')
    H.append('th,td{border:1px solid #bcc;padding:5px 8px;text-align:left;vertical-align:top}')
    H.append('th{background:#eaf2f8}')
    H.append('table.m th{width:130px;background:#f4f8fb}')
    H.append('.small{color:#777;font-size:12px;font-weight:normal}')
    H.append('.kbox{background:#eef6fb;border:1px solid #b9d6ea;padding:12px 16px;border-radius:6px;margin:10px 0}')
    H.append('.wbox{background:#fdf6e3;border:1px solid #e6d6a0;padding:12px 16px;border-radius:6px;margin:10px 0}')
    H.append('code{background:#f3f3f3;padding:1px 4px;border-radius:3px;font-size:12px}')
    H.append('.tag{display:inline-block;background:#1a5276;color:#fff;padding:1px 7px;border-radius:3px;font-size:12px}')
    H.append('.pri{display:inline-block;padding:0 6px;border-radius:3px;font-size:11px;font-weight:bold;color:#fff}')
    H.append('.p0{background:#c0392b}.p1{background:#d68910}.p2{background:#7f8c8d}')
    H.append('pre{background:#f6f8fa;border:1px solid #ddd;padding:10px;overflow-x:auto;font-size:12px;border-radius:5px}')
    H.append('ul{margin:6px 0}')
    H.append('</style></head><body><div>')
    H.append('<h1>BaiZe Vision: \u8def\u7ebd\u2460 \u2014 OCR \u4e13\u9879 SFT \u6267\u884c\u65b9\u6848\u62a5\u544a</h1>')
    H.append(f'<p class="small">\u751f\u6210\u5668 <code>vision/generate_ocr_sft_plan_report.py</code> \u00b7 \u57fa\u7ebf\u6570\u5b57\u6765\u81ea\u56db\u81c2 consolidated_12benchmarks.json \u00b7 SFT \u53e3\u5f84\u5bf9\u9f50 <code>stage2_train_armE_r2.py</code> \u00b7 \u68c0\u7d22/\u6838\u5b9e\u4e8e 2026-10-25 \u00b7 \u751f\u6210 {datetime.now().strftime("%Y-%m-%d %H:%M")}</p>')

    # ---- 1 \u6458\u8981 ----
    H.append('<h2>1. \u6458\u8981</h2><div class="kbox"><ul>')
    H.append(f'<li>\u672c\u62a5\u544a\u628a\u8c03\u7814\u62a5\u544a\u7684\u300c\u5355\u4e00\u5efa\u8bae\u300d(\u8def\u7ebd\u2460)\u7ec6\u5316\u4e3a\u53ef\u7167\u7740\u505a\u7684 OCR \u4e13\u9879 SFT \u6267\u884c\u65b9\u6848: \u7528 trdg/SynthTIGER/\u81ea\u7814\u6e32\u67d3\u5668 \u5408\u6210 50-200 \u4e07\u5bf9, \u5728 ArmE-R2 \u73b0\u884c ckpt \u4e0a\u52a0\u4e00\u8f6e Stage-2.5 SFT.</li>')
    H.append(f'<li><b>\u57fa\u7ebd\u914d\u6bd4\u4e00\u89c8</b>: \u82f1\u6587\u8bcd\u53e5 30% / \u4e2d\u6587\u8bcd\u53e5 20% / \u4e2d\u82f1\u6df7\u6392 10% / \u6587\u6863\u7248\u9762 15% / \u56fe\u8868 10% / \u6570\u5b66\u516c\u5f0f 10% / \u4f4e\u8d28\u624b\u5199\u573a\u666f 5%; \u603b\u91cf P0=20\u4e07(pilot), P1=150\u4e07(\u5168\u91cf). \u5019\u9009 A(\u82f16\u4e2d3\u6df71) \u4e3a\u9ed8\u8ba4, B(\u4e2d\u82f11:1) \u4f9b\u4e2d\u6587\u573a\u666f\u5907\u9009.</li>')
    H.append(f'<li>\u6570\u5b66\u516c\u5f0f\u4e09\u901a\u9053: (a)\u7eaf\u516c\u5f0f\u56fe im2latex/LaTeX 5% \u00b7 (b)\u6b63\u6587\u5939\u516c\u5f0f arXiv+KaTeX 3% \u00b7 (c)\u516c\u5f0f+\u8868\u683c\u6df7\u6392 2%; \u516c\u5f0f\u603b\u5360 \u226410%, \u4e3b\u4ef7\u503c\u5728\u7b26\u53f7\u8bcd\u8868\u4e0e\u7248\u9762\u89e3\u6790, \u4e0d\u671f\u671b\u516c\u5f0f\u5b50\u96c6\u72ec\u7acb\u62ac\u5347 OCRBench.</li>')
    H.append(f'<li>SFT \u53e3\u5f84: \u8d77\u59cb ckpt = ArmE-R2 Stage-2 step3500\u00b7LoRA r=64\u7ee7\u7eed\u00b7LR 1e-5/5e-6\u00b7224px \u5355\u5757\u00b7256 tokens; \u4e0e Stage-2 780k \u6df7 70%OCR:30%780k \u9632\u9057\u5fd8; 336+anyres \u4e3a\u963b\u585e\u9879(\u9700\u5de5\u7a0b\u6539\u9020+scope).</li>')
    H.append(f'<li><b>\u9884\u6ce8\u518c\u5224\u636e</b>: \u4e3b OCRBench \u2265 +2pp(1.60%\u2192\u22653.60%); \u526f DocVQA/ChartQA/InfoVQA \u5404 \u2265+1pp; \u62a4\u680f MMStar/AI2D/RealWorldQA/MMBench \u9000\u5316 \u22641pp. \u542b\u51b3\u7b56\u6811: pilot\u8fbe\u6807\u2192\u5168\u91cf; \u4e0d\u8fbe\u6807\u2192\u6539\u4e00\u7ef4\u518d\u8bd5; \u4e24\u6b21\u4e0d\u8fbe\u2192\u505c+\u8d1f\u9762\u7ed3\u8bba.</li>')
    H.append(f'<li>\u672c\u8f6e\u53ea\u51fa\u65b9\u6848\u62a5\u544a, \u4e0d\u542f\u8bad\u7ec3\u3001\u4e0d\u751f\u6210\u5168\u91cf\u6570\u636e(\u7b49\u7528\u6237\u770b\u5b8c\u6279\u9884\u7b97). \u8bda\u5b9e\u6761\u6b3e: \u5916\u90e8\u6570\u5b57\u5747\u4e3a\u8bba\u6587\u81ea\u62a5\u672a\u590d\u73b0; \u6210\u672c\u4e3a\u4f30\u7b97; \u672c\u9879\u76ee\u6570\u5b57\u5168\u90e8\u5b9e\u6d4b\u53ef\u6eaf\u6e90.</li>')
    H.append('</ul></div>')

    # ---- 2 \u73b0\u72b6\u4e0e\u5dee\u8ddd ----
    H.append('<h2>2. \u73b0\u72b6\u4e0e\u5dee\u8ddd</h2>')
    H.append(f'<p>\u57fa\u7ebd\u53e3\u5f84 = {esc(BASELINE_REF)}\u3002\u6570\u636e\u6765\u6e90: \u56db\u81c2 <code>consolidated_12benchmarks.json</code>\u3002\u4e3b\u5224\u636e\u56db\u96c6\u5747\u65e0\u9700 LLM judge(exact-match/ANLS/relaxed), \u4e0e MMVet/MathVista \u7684 OPENAI_API_KEY \u963b\u585e\u65e0\u5173, \u53ef\u76f4\u63a5\u6d4b.</p>')
    H.append('<table><tr><th>\u96c6\u5408</th><th>\u6307\u6807</th><th>ArmB</th><th>ArmC</th><th>ArmD-R2</th><th>ArmE-R2</th><th>\u5dee\u8ddd\u5b9a\u4f4d</th></tr>')
    rows_ocr = [bench_row(k,l,m,n) for (k,l,m,n) in OCR_BENCHES]
    gap = {"ocrbench":"\u6587\u5b57\u8bc6\u522b(\u6781\u4f4e, 1.6%)","docvqa_val":"\u7248\u9762/\u6587\u6863\u7ed3\u6784","chartqa":"\u56fe\u8868\u6570\u503c\u8bfb\u53d6","infovqa_val":"\u957f\u6587\u6863\u4fe1\u606f\u63d0\u53d6"}
    for r in rows_ocr:
        H.append(f'<tr><td><b>{esc(r[1])}</b></td><td>{esc(r[2])}</td><td>{r[3]}</td><td>{r[4]}</td><td>{r[5]}</td><td><b>{r[6]}</b></td><td>{esc(gap.get("",""))}</td></tr>')
    H.append('</table>')
    H.append('<p class="small">\u56db\u81c2\u8de8\u5ea6 \u22641pp \u2192 \u4e0e\u7f16\u7801\u5668\u5bb9\u91cf/ProtB \u65e0\u5173(ArmE-R2 ProtB 68.2% \u6700\u5f3a\u4f46 OCRBench \u4ecd 1.6%); \u95ee\u9898\u5728\u6570\u636e/\u4efb\u52a1\u7f3a\u4f4d\u800c\u975e\u7f16\u7801\u5668. \u56de\u5f52\u62a4\u680f\u57fa\u7ebd(ArmE-R2 \u5f85\u8bfb, \u4e0b\u8868\u7528 ArmB \u4ee3\u8868\u503c\u5e76\u6807\u6ce8):</p>')
    H.append('<table><tr><th>\u62a4\u680f\u96c6</th><th>\u6307\u6807</th><th>ArmB(\u4ee3\u8868)</th><th>\u62a4\u680f\u5224\u636e</th></tr>')
    for k,l,m,n in GUARD_BENCHES:
        v = fmt_pct(arm_value(arm_data[0][2], k))
        H.append(f'<tr><td><b>{esc(l)}</b></td><td>{esc(m)}</td><td>{v}</td><td>\u9000\u5316 \u2264 1pp</td></tr>')
    H.append('</table>')

    # ---- 3 \u6570\u636e\u914d\u65b9 ----
    H.append('<h2>3. \u6570\u636e\u914d\u65b9\uff08\u4e2d\u82f1 \u00b7 \u516c\u5f0f \u00b7 \u5176\u4ed6\uff09</h2>')
    H.append('<h3>3.1 \u4e2d\u82f1\u6587\u6bd4\u4f8b \u2014 \u57fa\u7ebd\u914d\u6bd4\u8868</h3>')
    H.append('<table><tr><th>\u7c7b\u522b</th><th>\u6570\u91cf(P1)</th><th>\u6765\u6e90</th><th>\u4f9d\u636e</th></tr>')
    for cat,n,src,why in BASELINE_RATIO_TABLE:
        H.append(f'<tr><td>{esc(cat)}</td><td>{esc(n)}</td><td>{esc(src)}</td><td>{esc(why)}</td></tr>')
    H.append('</table>')
    H.append('<h3>3.2 \u4e2d\u82f1\u5019\u9009\u914d\u6bd4</h3>')
    H.append('<table class="m"><tr><th>\u5019\u9009</th><th>\u5212\u5206</th><th>\u4f9d\u636e</th><th>\u9009\u4e2d\u5224\u636e</th></tr>')
    for c in CANDIDATE_RATIOS:
        H.append(f'<tr><td><b>{esc(c["name"])}</b></td><td>{esc(c["split"])}</td><td>{esc(c["rationale"])}<br><span class="small">\u9002\u7528: {esc(c["cond"])}</span></td><td>{esc(c["judge"])}</td></tr>')
    H.append('</table>')
    H.append('<div class="wbox">\u9ed8\u8ba4\u63a8 <b>\u5019\u9009 A</b>\uff1a\u8bc4\u6d4b\u96c6(OCRBench/DocVQA)\u4ee5\u82f1\u6587\u4e3a\u4e3b\uff0c\u82f1\u6587\u5b50\u96c6\u52a0\u6743\u66f4\u9ad8\u66f4\u5bb9\u6613\u8fbe +2pp\u3002\u82f5\u7528\u6237\u660e\u786e\u8981\u4e2d\u6587\u80fd\u529b\u518d\u8f6c B\u3002</div>')
    H.append('<h3>3.3 \u6570\u5b66\u516c\u5f0f\u4e09\u901a\u9053</h3>')
    H.append('<table class="m"><tr><th>\u901a\u9053</th><th>\u5de5\u5177</th><th>\u5185\u5bb9</th><th>\u8f93\u5165</th><th>\u9884\u7b97</th><th>\u5931\u8d25\u7387\u63a7</th></tr>')
    for f in FORMULA_CHANNELS:
        H.append(f'<tr><td><b>{esc(f["name"])}</b></td><td>{esc(f["tool"])}</td><td>{esc(f["items"])}</td><td>{esc(f["inputs"])}</td><td>{esc(f["budget"])}</td><td>{esc(f["fail"])}</td></tr>')
    H.append('</table>')
    H.append(f'<p class="small">{esc(FORMULA_OCRBENCH_NOTE)}</p>')
    H.append('<h3>3.4 \u5176\u4ed6\u7c7b\u522b\uff08\u4f18\u5148\u7ea7 P0-P2\uff09</h3>')
    H.append('<table><tr><th>\u7c7b\u522b</th><th>\u6570\u91cf</th><th>\u4f18\u5148\u7ea7</th><th>\u5224\u636e</th></tr>')
    for c in OTHER_CATEGORIES:
        pc = c["pri"].lower()
        H.append(f'<tr><td>{esc(c["cat"])}</td><td>{esc(c["n"])}</td><td><span class="pri {pc}">{esc(c["pri"])}</span></td><td>{esc(c["judge"])}</td></tr>')
    H.append('</table>')
    H.append('<p class="small">\u6570\u636e\u6765\u6e90\u4e0e\u8bb8\u53ef: \u53ea\u7528\u53ef\u5546\u7528/\u53ef\u518d\u5206\u53d1\u8bed\u6599 \u2014 \u7ef4\u57fa(CC-BY-SA)\u3001\u5f00\u6e90\u4e66\u7c4d(Gutenberg/CC)\u3001CC \u8bed\u6599\u3001\u81ea\u5efa LaTeX; \u9010\u7c7b\u6807\u6765\u6e90\u4e0e License\u3002\u4e0d\u7528\u6765\u5386\u4e0d\u660e\u7684\u722c\u866b\u6570\u636e\u3002</p>')
    return H, out_path

def render_rest(H, arm_data):
    # ---- 4 \u751f\u6210\u7ba1\u7ebf\u4e0e\u53c2\u6570 ----
    H.append('<h2>4. \u751f\u6210\u7ba1\u7ebf\u4e0e\u53c2\u6570</h2>')
    H.append('<table class="m"><tr><th>\u5de5\u5177</th><th>\u89d2\u8272</th><th>\u5173\u952e\u53c2\u6570</th><th>\u5b57\u4f53</th><th>\u8bed\u6599</th><th>\u6807\u7b7e\u683c\u5f0f</th></tr>')
    for p in PIPELINE_PARAMS:
        H.append(f'<tr><td><b>{esc(p["tool"])}</b></td><td>{esc(p["role"])}</td><td><code>{esc(p["params"])}</code></td><td>{esc(p["fonts"])}</td><td>{esc(p["corpus"])}</td><td>{esc(p["label"])}</td></tr>')
    H.append('</table>')
    H.append('<p class="small">trdg \u5b98\u65b9\u53c2\u6570(\u68c0\u7d22/\u6838\u5b9e\u4e8e 2026-10-25, GitHub README): <code>-k/-rk</code>\u503e\u659c\u3001<code>-d/-do</code>\u626d\u66f2\u3001<code>-bl/-rbl</code>\u9ad8\u65af\u6a21\u7cca\u3001<code>-b 0/1/2/3</code>\u80cc\u666f(\u9ad8\u65af\u566a\u58f0/\u7eaf\u767d/\u51c6\u6676/\u56fe\u50cf)\u3001<code>--font_dir</code>\u5b57\u4f53\u3001<code>--output_mask</code>\u5b57\u7b26\u7ea7 mask\u3001<code>--word_split</code>\u8fde\u5b57\u8bed\u79cd; \u652f\u6301\u975e\u62c9\u4e01\u6587\u5b57(\u542b\u4e2d\u6587)\u3002</p>')

    # ---- 5 SFT \u914d\u65b9\u4e0e\u6df7\u5408\u7b56\u7565 ----
    H.append('<h2>5. SFT \u914d\u65b9\u4e0e\u6df7\u5408\u7b56\u7565</h2>')
    H.append('<h3>5.1 SFT \u914d\u65b9\uff08\u5bf9\u9f50\u73b0\u6709 stage2_train_armE_r2.py \u53e3\u5f84\uff09</h3>')
    H.append('<table class="m">')
    for k,label in [("start_ckpt","\u8d77\u59cb ckpt"),("approach","\u65b9\u6cd5"),("lora","LoRA"),("lr","LR"),("steps","\u6b65\u6570"),("gbs","GBS/MBS"),("image","\u56fe\u50cf"),("full_vs_lora","LoRA vs \u5168\u53c2"),("res_336_note","336+anyres")]:
        H.append(f'<tr><th>{esc(label)}</th><td>{esc(SFT_RECIPE[k])}</td></tr>')
    H.append('</table>')
    H.append('<h3>5.2 \u4e0e Stage-2 780k \u6df7\u5408\u7b56\u7565\uff08\u9632\u707e\u96be\u6027\u9057\u5fd8\uff09</h3>')
    H.append('<table class="m"><tr><th>\u9636\u6bb5</th><th>\u6df7\u5408</th></tr>')
    for mx in MIXING_STRATEGY:
        H.append(f'<tr><td><b>{esc(mx["plan"])}</b></td><td>{esc(mx["mix"])}</td></tr>')
    H.append('</table>')
    H.append('<div class="wbox">\u539f\u7406: \u7eaf\u65b0\u6570\u636e SFT \u6613\u538b\u574e\u539f\u6709\u80fd\u529b; \u6df7\u5165 30% \u539f\u7248 780k \u662f\u4e3b\u6d41 MLLM \u9632\u9057\u5fd8\u7684\u5e38\u89c1\u505a\u6cd5(\u53c2\u8003 LLaVA/DocOwl \u8c03\u4f18\u8def\u7ebf)\u3002P0 pilot \u6545\u610f\u4e0d\u6df7, \u662f\u4e3a\u7eaf\u63a2\u9488\u770b\u300c\u5408\u6210\u6570\u636e\u80fd\u5426\u52a8\u300d\u3002</div>')

    # ---- 6 \u6210\u672c\u4e0e ETA ----
    H.append('<h2>6. \u6210\u672c\u4e0e ETA\uff08\u4f30\u7b97\uff09</h2>')
    H.append('<table><tr><th>\u9636\u6bb5</th><th>\u6570\u636e\u91cf</th><th>\u6e32\u67d3 CPU\u00b7\u6838\u00b7\u65f6</th><th>\u5b58\u50a8</th><th>\u8bad\u7ec3 GPU\u00b7\u5361\u00b7\u65f6</th><th>ETA</th></tr>')
    for c in COST_EST:
        H.append(f'<tr><td><b>{esc(c["stage"])}</b></td><td>{esc(c["data"])}</td><td>{esc(c["render_cpu"])}</td><td>{esc(c["storage"])}</td><td>{esc(c["train_gpu"])}</td><td>{esc(c["eta"])}</td></tr>')
    H.append('</table>')
    H.append('<p class="small">\u4f30\u7b97\u53e3\u5f84: trdg \u7ea6 1\u4e07/s/CPU\u6838; 8\u00d7H100 \u4e0e\u73b0\u6709\u8bad\u7ec3\u540c\u73af\u5883; \u6e32\u67d3\u5e94\u8d70\u5176\u4ed6\u673a\u5668/\u591c\u95f4, \u907f\u8ba9 .12/.29 \u8bad\u7ec3\u5361 I/O\u3002\u6240\u6709\u6570\u5b57\u5747\u4e3a\u4f30\u7b97\u3002</p>')

    # ---- 7 \u5224\u636e\u4e0e\u51b3\u7b56\u6811 ----
    H.append('<h2>7. \u5224\u636e\u4e0e\u51b3\u7b56\u6811</h2>')
    H.append(f'<p><b>\u4e3b\u5224\u636e</b>: <span class="tag">{esc(CRITERIA["primary"])}</span></p>')
    H.append('<p><b>\u526f\u5224\u636e</b>:</p><ul>')
    for s in CRITERIA["secondary"]:
        H.append(f'<li>{esc(s)}</li>')
    H.append('</ul><p><b>\u56de\u5f52\u62a4\u680f(\u9632\u4ee5\u9000\u5316\u6362\u5206)</b>:</p><ul>')
    for g in CRITERIA["guard"]:
        H.append(f'<li>{esc(g)}</li>')
    H.append('</ul>')
    H.append('<h3>\u51b3\u7b56\u6811</h3><pre>')
    for line in DECISION_TREE:
        H.append(esc(line))
    H.append('</pre>')

    # ---- 8 \u98ce\u9669\u4e0e\u5751 ----
    H.append('<h2>8. \u98ce\u9669\u4e0e\u5751</h2><table class="m"><tr><th>\u98ce\u9669</th><th>\u7f13\u89e3</th></tr>')
    for r in RISKS:
        H.append(f'<tr><td>{esc(r["r"])}</td><td>{esc(r["m"])}</td></tr>')
    H.append('</table>')

    # ---- 9 \u53c2\u8003\u6765\u6e90 ----
    H.append('<h2>9. \u53c2\u8003\u6765\u6e90\uff08\u7eaf\u6587\u672c arXiv \u53f7\uff0c\u7981\u8d85\u94fe\uff09</h2><ul>')
    for ref in REFERENCES:
        H.append(f'<li>{esc(ref)}</li>')
    H.append('</ul>')
    H.append('<p class="small">\u68c0\u7d22/\u6838\u5b9e\u4e8e 2026-10-25\u3002\u5916\u90e8\u6548\u679c\u6570\u5b57\u5747\u4e3a\u8bba\u6587\u81ea\u62a5\u3001\u672a\u5728\u672c\u9879\u76ee\u590d\u73b0; \u672c\u9879\u76ee\u6570\u5b57\u5168\u90e8\u5b9e\u6d4b\u53ef\u6eaf\u6e90; \u6210\u672c\u4e3a\u4f30\u7b97\u3002</p>')

    # ---- \u4e00\u9875\u7eb8\u6267\u884c\u6e05\u5355 ----
    H.append('<h2>\u9644\u5f55: \u4e00\u9875\u7eb8\u6267\u884c\u6e05\u5355\uff08\u4eca\u5929\u5c31\u80fd\u5f00\u59cb\uff09</h2><div class="kbox"><table class="m"><tr><th>\u6b65</th><th>\u52a8\u4f5c</th></tr>')
    for step,act in CHECKLIST:
        H.append(f'<tr><td><b>{esc(step)}</b></td><td>{esc(act)}</td></tr>')
    H.append('</table></div>')
    H.append('<p class="small">\u9a8c\u6536\u770b\u54ea\u51e0\u4e2a\u6587\u4ef6: <code>/tmp/ocr_smoke/labels.txt</code>(\u56fe\u6587\u5bf9\u9f50) \u00b7 <code>/tmp/ocr_smoke/</code> \u62bd\u6837 50\u5f20 PNG \u4eba\u773c\u770b \u00b7 P0 \u8bad\u7ec3\u540e <code>mllm_eval_results_*/consolidated_12benchmarks.json</code> \u7684 OCRBench \u5217.</p>')

    H.append('</div></body></html>')
    return H

def self_check(html, out_path):
    errs = []
    if '<script' in html: errs.append('FOUND <script>')
    if 'href="http' in html: errs.append('FOUND href=http external link')
    size = len(html.encode('utf-8'))
    if size < 18000: errs.append(f'TOO SMALL {size}B < 18000')
    # tag balance
    from html.parser import HTMLParser
    class C(HTMLParser):
        def __init__(self): super().__init__(); self.st=[]; self.void={'meta','br','hr','img','input','link','col','area','base','source','track','wbr'}
        def handle_starttag(self,t,a):
            if t not in self.void: self.st.append(t)
        def handle_endtag(self,t):
            if t in self.void: return
            if not self.st or self.st[-1]!=t:
                errs.append(f'TAG MISMATCH </{t}> stack={self.st[-3:]}')
            else: self.st.pop()
    C().feed(html)
    if self and C().st if False else None: pass
    # re-run for stack leftover
    c2=C(); c2.feed(html)
    if c2.st: errs.append(f'UNCLOSED {c2.st}')
    return size, errs

def main():
    out = DEFAULT_OUT
    os.makedirs(REPORTS_DIR, exist_ok=True)
    H, _ = render(out)
    # load arm_data again for render_rest (render returned H before rest; re-derive)
    arm_data=[]
    for name,desc,path in ARMS:
        data,cj=load_arm(path); arm_data.append((name,desc,data,cj))
    H = render_rest(H, arm_data)
    html = '\n'.join(H)
    size, errs = self_check(html, out)
    with open(out,'w',encoding='utf-8') as f:
        f.write(html)
    print(f'WROTE {out}  {size}B')
    if errs:
        print('SELF-CHECK FAILED:'); [print('  -',e) for e in errs]; sys.exit(1)
    print('SELF-CHECK PASS: 0 <script>, 0 external link, tags balanced, >=18KB')

if __name__=='__main__':
    main()
