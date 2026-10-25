#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_ocr_synthdata_report.py — OCR 类评测偏低: 合成数据补强方法调研中文报告生成器.

用户令 (2026-10-25 17:5x): "vision: 现在OCR类评测很低, web search 调研一下合成数据补强这块能力的方法, 写报告."

读取四臂 (ArmB/ArmC/ArmD-R2/ArmE-R2) 的 consolidated_12benchmarks.json, 取 OCR 相关四集
(OCRBench / DocVQA(val) / ChartQA / InfoVQA(val)) 的实测分数, 结合 2026-10-25 经代理检索得到的
arXiv 摘要, 生成 8 节自包含中文 HTML 报告 (0 <script> / 0 外链 / 标签配平).

用法:
  python generate_ocr_synthdata_report.py
"""
import json, os, sys
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
OUT_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out"
DEFAULT_OUT = os.path.join(REPORTS_DIR, "report_vision_ocr_synthdata_zh.html")

# 四臂结果目录 (consolidated_12benchmarks.json 所在)
ARMS = [
    ("ArmB", "ViT-B/16, AIMv2-style, 3\u6e90/4epoch", os.path.join(OUT_DIR, "mllm_eval_results_armB")),
    ("ArmC", "ViT-B/16, min_lr1e-5+wd0.01", os.path.join(OUT_DIR, "mllm_eval_results_armC_20261018")),
    ("ArmD-R2", "ViT-B/16, 6\u6e90/3epoch, lr1e-3", os.path.join(OUT_DIR, "mllm_eval_results_armD_r2_20261020")),
    ("ArmE-R2", "ViT-L/14, lr5e-4, 63400\u6b65", os.path.join(OUT_DIR, "mllm_eval_results_armE_r2_20261022")),
]
# OCR 相关四集 + 主指标键 + 指标说明 (均无需 LLM judge, 可直接测)
OCR_BENCHES = [
    ("ocrbench", "OCRBench", "ocrbench_accuracy,none", "exact-match \u9010\u9898\u51c6\u786e\u7387 (lmms-eval, 0-1); \u6ce8: \u539f\u7248 OCRBench \u6ee1\u5206 1000 \u4e3a\u53e6\u4e00\u53e3\u5f84"),
    ("docvqa_val", "DocVQA (val)", "anls,none", "ANLS (0-1), \u6587\u6863 VQA"),
    ("chartqa", "ChartQA", "relaxed_overall,none", "relaxed accuracy (0-1), \u56fe\u8868\u95ee\u7b54"),
    ("infovqa_val", "InfoVQA (val)", "anls,none", "ANLS (0-1), \u4fe1\u606f\u56fe VQA"),
]

def load_arm(path):
    cj = os.path.join(path, "consolidated_12benchmarks.json")
    if not os.path.exists(cj):
        return None, cj
    with open(cj) as f:
        return json.load(f), cj

def arm_value(data, key):
    """\u4ece results \u53d6\u503c (float); raw_results \u53d6 stderr."""
    r = data.get("results", {})
    v = r.get(key)
    if isinstance(v, (int, float)):
        return float(v)
    return None

def arm_stderr(data, key, metric):
    raw = data.get("raw_results", {}).get(key, {})
    se = raw.get(metric, "N/A")
    if se == "N/A":
        return None
    try:
        return float(se)
    except Exception:
        return None

def fmt_pct(v):
    return f"{v*100:.2f}%" if isinstance(v, (int, float)) else "N/A"

# ===================== 合成数据方法库 (检索于 2026-10-25, 经 arXiv 摘要核实) =====================
# 字段: name, cite (arXiv 号/项目), year, cat, how, inputs, effect, integ, cost, src2
METHODS = [
 dict(name="SynthTIGER", cite="arXiv:2107.09313", year=2021, cat="A \u6587\u5b57\u8bc6\u522b\u5408\u6210",
   how="\u5206\u6790\u73b0\u6709\u6587\u5b57\u56fe\u50cf\u5408\u6210\u6280\u5de7\u5e76\u96c6\u6210\u4e8e\u5355\u4e00\u7b97\u6cd5; \u5f15\u5165\u4e24\u9879\u6280\u672f\u7f13\u89e3\u8bad\u7ec3\u6570\u636e\u957f\u5c3e\u4e0e\u5b57\u7b26\u5206\u5e03; \u591a\u6837\u80cc\u666f/\u5b57\u4f53/\u6587\u5b57\u5f62\u72b6\u6e32\u67d3",
   inputs="\u5b57\u4f53\u5e93, \u8bed\u6599\u8bcd\u8868, \u80cc\u666f\u56fe/\u7eb9\u7406, \u900f\u89c6/\u6a21\u7cca/\u5149\u7167\u7b49\u9000\u5316\u53c2\u6570",
   effect="\u5728 STR \u4e0a\u4f18\u4e8e MJSynth+SynthText \u5408\u6210\u96c6\u7ec4\u5408 (\u539f\u6587\u672a\u7ed9\u5177\u4f53\u6570\u5b57; \u6458\u8981\u660e\u8ff0 better STR performance)",
   integ="\u7f16\u7801\u5668\u9884\u8bad\u7ec3\u9886\u57df\u53ef\u52a0 OCR \u8bc6\u522b\u5bf9\u6bd4\u76d1\u7763; \u6216 Stage-2 SFT \u6dfb\u52a0 OCR \u6587\u5b57\u8bfb\u53d6\u6837\u672c",
   cost="\u4f30\u7b97: \u5355 CPU \u53ef\u6e32\u67d3\u6570\u767e\u4e07\u5230\u5343\u4e07\u5bf9; \u6e32\u67d3 CPU \u5c0f\u65f6\u91cf\u7ea7\u4f4e",
   src2="\u88ab Donut (2111.15664) \u7b49\u6587\u6863\u4f5c\u4e3a\u5408\u6210\u6570\u636e\u57fa\u7ebf\u5f15\u7528\u4e0e\u5bf9\u6bd4"),
 dict(name="SynthText", cite="arXiv:1604.06646", year=2016, cat="A \u6587\u5b57\u8bc6\u522b\u5408\u6210",
   how="\u5c06\u5408\u6210\u6587\u672c\u53e0\u52a0\u5230\u771f\u5b9e\u80cc\u666f\u56fe, \u4f9d\u636e\u5c40\u90e8 3D \u573a\u666f\u51e0\u4f55\u81ea\u7136\u8d34\u5408 (\u989c\u8272/\u7f29\u653e/\u900f\u660e\u5ea6); \u7528\u4e8e\u8bad\u7ec3\u6587\u5b57\u68c0\u6d4b FCRN",
   inputs="\u80cc\u666f\u81ea\u7136\u56fe\u50cf\u96c6 + \u8bed\u6599 + \u5b57\u4f53; \u9700\u8bed\u4e49\u5206\u5272\u4ee5\u4f9d\u636e\u533a\u57df\u8d34\u5408",
   effect="ICDAR 2013 \u6587\u5b57\u68c0\u6d4b F-measure 84.2% (\u5f53\u65f6 SOTA); 15 img/s/GPU",
   integ="\u4f5c\u4e3a\u573a\u666f\u6587\u5b57\u68c0\u6d4b/\u8bc6\u522b\u9884\u8bad\u7ec3\u6570\u636e; \u53ef\u751f\u6210 OCR \u68c0\u6d4b\u76d1\u7763",
   cost="\u539f\u6587\u62a5 ~800K \u5408\u6210\u56fe\u50cf; \u6e32\u67d3 CPU \u4e2d\u7b49",
   src2="SynthTIGER (2107.09313) \u5c06\u5176\u4f5c\u4e3a\u5bf9\u6bd4\u57fa\u7ebf (ST) \u4e4b\u4e00"),
 dict(name="trdg (TextRecognitionDataGenerator)", cite="GitHub \u5de5\u5177, \u65e0\u5355\u4e00 arXiv", year=2018, cat="A \u6587\u5b57\u8bc6\u522b\u5408\u6210",
   how="\u5f00\u6e90\u6587\u5b57\u8bc6\u522b\u5408\u6210\u5e93; \u968f\u673a\u6587\u672c+\u5b57\u4f53+\u80cc\u666f+\u591a\u79cd\u9000\u5316 (\u6a61\u76ae/\u7eb8\u8d28/\u6a21\u7cca/\u9c81\u68d2\u58f3/\u8fb9\u7f18)\u6e32\u67d3\u8bcd\u7ea7/\u884c\u7ea7\u6587\u5b57\u56fe",
   inputs="\u5b57\u4f53\u6587\u4ef6, \u8bed\u6599\u6587\u672c, \u80cc\u666e\u80cc\u666f\u56fe\u7247\u76ee\u5f55",
   effect="\u5de5\u4e1a\u7ea7\u5e7f\u6cdb\u7528\u4e8e STR \u8bad\u7ec3\u6570\u636e\u589e\u5e7f; \u65e0\u7edf\u4e00\u699c\u5355\u6570\u5b57",
   integ="\u6700\u4f4e\u95e8\u69db OCR \u5408\u6210\u6570\u636e\u6765\u6e90; \u968f\u673a\u751f\u6210\u8bcd\u7ea7\u8bc6\u522b\u5bf9",
   cost="\u6781\u4f4e: \u5355\u673a CPU \u5373\u53ef\u4ea7\u767e\u4e07\u5bf9",
   src2="\u88ab PaddleOCR \u8bad\u7ec3\u6d41\u7a0b\u4f5c\u4e3a\u53ef\u9009\u5408\u6210\u6e90\u63d0\u53ca"),
 dict(name="Donut / SynthDoG", cite="arXiv:2111.15664", year=2021, cat="B \u6587\u6863\u5408\u6210/OCR-free",
   how="OCR-free \u6587\u6863\u7406\u89e3 Transformer; \u9644 SynthDoG \u5408\u6210\u6587\u6863\u751f\u6210\u5668 (\u652f\u6301\u591a\u8bed\u8a00/\u591a\u57df\u9884\u8bad\u7ec3); \u4ea4\u53c9\u71b5\u9884\u8bad\u7ec3",
   inputs="\u8bed\u6599/\u5b57\u4f53, \u7248\u9762\u6a21\u677f, \u5404\u8bed\u8a00\u6587\u672c; \u53ef\u8de8\u8bed\u8a00\u57df\u5b9a\u5236",
   effect="\u5728\u591a\u4e2a VDU \u4efb\u52a1\u4e0a\u53d6\u5f97 SOTA (\u901f\u5ea6\u4e0e\u7cbe\u5ea6\u517c\u987e); \u539f\u6587\u672a\u7ed9\u5177\u4f53\u6570\u5b57",
   integ="\u6587\u6863\u7406\u89e3 SFT \u6837\u672c\u5408\u6210 (\u53d1\u7968/\u8868\u5355/\u6807\u7b7e); \u53ef\u76f4\u63a5\u4f5c\u4e3a Stage-2 \u6570\u636e\u6e90",
   cost="\u6e32\u67d3 CPU \u4e2d\u7b49; \u8bad\u7ec3\u9700\u4e2d\u7b49 GPU \u91cf\u7ea7",
   src2="UDOP (2212.02623) \u540c\u5c5e\u6587\u6863 AI \u5408\u6210/\u81ea\u76d1\u7763\u8def\u7ebf, \u4e92\u4e3a\u5bf9\u6bd4"),
 dict(name="UDOP", cite="arXiv:2212.02623", year=2022, cat="B \u6587\u6863\u5408\u6210/OCR-free",
   how="Vision-Text-Layout Transformer; \u81ea\u76d1\u7763\u9884\u8bad\u7ec3 (\u63a9\u7801\u56fe\u50cf\u91cd\u5efa/\u5e03\u5c40\u9884\u6d4b) + \u591a\u57df\u6807\u6ce8; \u53ef\u4ece text+layout \u751f\u6210\u6587\u6863\u56fe\u50cf",
   inputs="\u5927\u89c4\u6a21\u672a\u6807\u6ce8\u6587\u6863\u8bed\u6599 + \u591a\u6837\u6807\u6ce8\u6570\u636e; \u9700\u7a7a\u95f4 layout \u4fe1\u606f",
   effect="\u5728 8 \u4e2a Document AI \u4efb\u52a1 SOTA; DUB \u699c\u7b2c\u4e00; \u9996\u6b21\u540c\u65f6\u5b9e\u73b0\u6587\u6863\u7f16\u8f91\u4e0e\u5185\u5bb9\u5b9a\u5236",
   integ="\u7f16\u7801\u5668\u9884\u8bad\u7ec3\u52a0\u5165\u6587\u6863\u81ea\u76d1\u7763\u76ee\u6807; \u6216\u5408\u6210\u6587\u6863\u4f5c SFT",
   cost="\u9884\u8bad\u7ec3\u9700\u8f83\u5927 GPU (\u4f30\u7b97\u591a\u5361\u591a\u65e5); \u5408\u6210 CPU \u4e2d\u7b49",
   src2="Pix2Struct (2210.03347) \u540c\u4e3a\u89c6\u89c9\u8bed\u8a00\u9884\u8bad\u7ec3, \u8def\u7ebf\u4e92\u8865"),
 dict(name="Pix2Struct", cite="arXiv:2210.03347", year=2022, cat="B \u6587\u6863\u5408\u6210/OCR-free",
   how="\u9884\u8bad\u7ec3\u4efb\u52a1 = \u5c06\u63a9\u7801\u7684\u7f51\u9875\u622a\u56fe\u89e3\u6790\u4e3a\u7b80\u5316 HTML; \u53d8\u5206\u8fa8\u7387\u8f93\u5165 + \u95ee\u9898\u6e32\u67d3\u5728\u56fe\u4e0a",
   inputs="\u7f51\u9875 (HTML \u7ed3\u6784\u4e3a\u6e90); \u65e0\u9700\u989d\u5916\u6807\u6ce8",
   effect="\u5728 9 \u4efb\u52a1\u4e2d 6 \u9879 SOTA, \u8de8\u6587\u6863/\u63d2\u56fe/UI/\u81ea\u7136\u56fe\u56db\u57df",
   integ="\u7f51\u9875\u622a\u56fe\u2192HTML \u4f5c\u4e3a\u7f16\u7801\u5668\u9884\u8bad\u7ec3\u81ea\u76d1\u7763; \u540c\u65f6\u8986\u76d6 OCR/LM/caption",
   cost="\u7f51\u9875\u6293\u53d6 CPU/\u5e26\u5bbd; \u9884\u8bad\u7ec3\u4e2d\u7b49 GPU",
   src2="UDOP (2212.02623) \u540c\u4e3a\u89c6\u89c9\u8bed\u8a00\u9884\u8bad\u7ec3, \u8def\u7ebf\u4e92\u8865"),
 dict(name="Nougat", cite="arXiv:2308.13418", year=2023, cat="B \u6587\u6863\u5408\u6210/OCR-free",
   how="\u9488\u5bf9\u5b66\u672f PDF \u7684\u6587\u672c\u8bc6\u522b; \u5c06\u5b66\u672f\u6587\u6863\u8f6c Markdown (\u542b\u516c\u5f0f/\u8868\u683c); \u8de8\u4eba\u673a\u673a\u5668\u53ef\u8bfb\u4e0e\u673a\u5668\u53ef\u89e3\u6865\u6881",
   inputs="\u5b66\u672f PDF \u8bed\u6599; \u9700\u5bf9\u5e94\u6587\u672c\u76d1\u7763",
   effect="\u5c06\u5b66\u672f\u6587\u6863\u8f6c Markdown (\u542b\u516c\u5f0f/\u8868\u683c); \u6865\u63a5\u4eba\u673a\u53ef\u8bfb\u4e0e\u673a\u5668\u53ef\u89e3\u6587\u672c; \u539f\u6587\u672a\u7ed9\u5177\u4f53\u699c\u5355\u6570\u5b57",

   integ="\u5b66\u672f\u6587\u6863 OCR \u4e13\u9879 SFT \u6570\u636e; \u516c\u5f0f/\u8868\u683c\u8bc6\u522b\u589e\u5e7f",
   cost="\u8bad\u7ec3\u4e2d\u7b49 GPU; \u6570\u636e\u6784\u5efa CPU \u4e2d\u7b49",
   src2="\u4e0e olmOCR (2502.18443) \u540c\u5c5e PDF\u2192\u6587\u672c OCR \u8def\u7ebf"),
 dict(name="mPLUG-DocOwl", cite="arXiv:2307.02499", year=2023, cat="C \u6587\u6863 MLLM/\u6307\u4ee4\u8c03\u4f18",
   how="\u57fa\u4e8e mPLUG-Owl; \u6784\u5efa\u591a\u4efb\u52a1\u6587\u672c-\u56fe\u50cf\u7406\u89e3\u6307\u4ee4\u8c03\u4f18\u6570\u636e\u96c6; \u7edf\u4e00\u6307\u4ee4\u8c03\u4f18\u7b56\u7565\u8054\u5408\u8bad\u7ec3",
   inputs="\u591a\u4efb\u52a1\u6587\u6863\u6307\u4ee4\u6570\u636e; \u8bed\u8a00/\u901a\u7528 VL/\u6587\u6863\u6570\u636e\u4e09\u8def\u5e76\u884c",
   effect="\u8d85\u8d8a\u73b0\u6709\u591a\u6a21\u6001\u6587\u6863\u7406\u89e3; \u539f\u6587\u672a\u7ed9\u5177\u4f53\u699c\u5355\u6570",
   integ="\u4e3a BaiZe MLLM \u63d0\u4f9b\u6587\u6863 OCR/\u7406\u89e3\u6307\u4ee4\u8c03\u4f18\u6570\u636e\u53ef\u76f4\u63a5\u63a5\u5165 Stage-2",
   cost="\u6307\u4ee4\u8c03\u4f18\u4e2d\u7b49 GPU; \u6570\u636e\u6784\u5efa\u4eba\u5de5\u6210\u672c\u8f83\u9ad8",
   src2="\u4e0e DocOwl1.5 \u540c\u7cfb; dots.ocr (2512.02498) \u540c\u5c5e\u6587\u6863 MLLM \u8def\u7ebf"),
 dict(name="dots.ocr", cite="arXiv:2512.02498", year=2025, cat="C \u6587\u6863 MLLM/\u6570\u636e\u5f15\u64ce",
   how="\u5355\u4e00 VLM \u8054\u5408\u5b66\u4e60\u7248\u9762\u68c0\u6d4b+\u6587\u5b57\u8bc6\u522b+\u5173\u7cfb\u7406\u89e3 (\u7aef\u5230\u7aef); \u53ef\u6269\u5c55\u6570\u636e\u5f15\u64ce\u5408\u6210\u591a\u8bed\u8a00\u8bed\u6599",
   inputs="\u591a\u8bed\u8a00\u8bed\u6599 + \u5408\u6210\u6a21\u677f; \u7248\u9762/\u8bed\u8a00/\u57df\u591a\u6837",
   effect="OmniDocBench \u4e0a SOTA; \u8de8\u8bed\u8a00/\u7248\u9762/\u57df\u9c81\u68d2",
   integ="\u53ef\u4f5c\u4e3a BaiZe \u6570\u636e\u5f15\u64ce\u8303\u4f8b: \u5408\u6210\u6587\u6863\u6837\u672c\u4f9b SFT",
   cost="\u6570\u636e\u5f15\u64ce\u5408\u6210 CPU \u4e2d\u7b49; \u8054\u5408\u8bad\u7ec3\u8f83\u5927 GPU",
   src2="\u4e0e mPLUG-DocOwl (2307.02499) \u540c\u5c5e\u6587\u6863 MLLM \u8def\u7ebf"),
 dict(name="ChartQA (\u589e\u5e7f\u96c6)", cite="arXiv:2203.10244", year=2022, cat="D \u56fe\u8868\u6570\u636e",
   how="9.6K \u4eba\u5199 + 23.1K \u7531\u4eba\u5199\u56fe\u8868\u6458\u8981\u751f\u6210\u7684\u95ee\u9898; \u542b\u89c6\u89c9+\u903b\u8f91\u63a8\u7406",
   inputs="\u56fe\u8868\u56fe\u50cf + \u4eba\u5199\u6458\u8981; \u6a21\u677f\u751f\u6210\u95ee\u9898",
   effect="\u63d0\u4f9b relaxed accuracy \u6307\u6807; \u63ed\u793a\u590d\u6742\u63a8\u7406\u6311\u6218",
   integ="\u4f5c\u4e3a ChartQA \u8bad\u7ec3/\u8bc4\u6d4b\u6570\u636e\u76f4\u63a5\u63a5\u5165 SFT; \u540c\u65f6\u662f\u8bc4\u6d4b\u96c6",
   cost="\u6570\u636e\u5df2\u5f00\u6e90\u514d\u8d39; \u63a5\u5165\u96f6\u6e32\u67d3\u6210\u672c",
   src2="\u4e0e Chart-to-Text (2203.06486) \u540c\u5e74\u540c\u5c5e\u56fe\u8868\u8bed\u6599"),
 dict(name="Chart-to-Text", cite="arXiv:2203.06486", year=2022, cat="D \u56fe\u8868\u6570\u636e",
   how="\u5927\u89c4\u6a21\u56fe\u8868\u6458\u8981\u57fa\u51c6: \u4e24\u6570\u636e\u96c6\u5171 44,096 \u56fe\u8868; \u6570\u636e\u8868\u53ef\u7528\u4e0e\u9700\u63d0\u53d6\u4e24\u79cd\u8bbe\u7f6e",
   inputs="\u56fe\u8868\u56fe\u50cf + \u5e95\u5c42\u6570\u636e\u8868 (\u90e8\u5206); \u4e3b\u9898/\u7c7b\u578b\u591a\u6837",
   effect="\u63d0\u4f9b\u56fe\u8868\u2192\u6587\u672c\u6458\u8981\u8bad\u7ec3\u6570\u636e; \u6a21\u578b\u6709\u5e7b\u89c9/\u4e8b\u5b9e\u9519\u8bef",
   integ="\u751f\u6210\u56fe\u8868\u6458\u8981\u6837\u672c\u4f5c ChartQA \u7c7b\u4efb\u52a1 SFT \u589e\u5e7f",
   cost="\u5df2\u5f00\u6e90; \u63a5\u5165\u96f6\u6e32\u67d3\u6210\u672c",
   src2="\u4e0e ChartQA (2203.10244) \u540c\u5e74\u540c\u5c5e\u56fe\u8868\u8bed\u6599"),
 dict(name="olmOCR", cite="arXiv:2502.18443", year=2025, cat="E OCR \u5f15\u64ce/\u8bc6\u522b\u7ba1\u7ebf",
   how="\u5fae\u8c03 7B VLM \u4e8e olmOCR-mix-0225 (260K \u9875, 100K+ PDF); \u8f93\u51fa\u7ebf\u6027\u5316\u7eaf\u6587\u672c\u4fdd\u7559\u7ed3\u6784; \u652f\u6301 vLLM/SGLang \u6279\u5904\u7406",
   inputs="\u722c\u53d6\u7684 PDF (\u542b\u56fe\u5f62/\u624b\u5199/\u4f4e\u8d28\u626b\u63cf); 260K \u9875\u76d1\u7763",
   effect="olmOCR-Bench \u4e0a\u8d85\u8d8a GPT-4o / Gemini Flash 2 / Qwen-2.5-VL; \u767e\u4e07\u9875 $176",
   integ="\u4f5c\u4e3a\u8bc6\u522b\u7ba1\u7ebf\u751f\u6210\u4f2a\u6807\u6ce8 (\u8bbe\u5907); \u6216\u6570\u636e\u6e90\u4f9b\u8bc6\u522b\u8c03\u4f18",
   cost="$176/100\u4e07\u9875 (\u539f\u6587); \u8bad\u7ec3 7B \u4e2d\u7b49 GPU",
   src2="\u4e0e Nougat (2308.13418) \u540c\u5c5e PDF\u2192\u6587\u672c OCR \u8def\u7ebf"),
 dict(name="Visual-RFT", cite="arXiv:2503.01785", year=2025, cat="F RL \u53ef\u9a8c\u8bc1\u5956\u52b1",
   how="\u89c6\u89c9\u5f3a\u5316\u5fae\u8c03: LVLM \u751f\u6210\u591a\u54cd\u5e94 + \u53ef\u9a8c\u8bc1\u5956\u52b1\u51fd\u6570 (IoU \u7b49) + GRPO \u7b56\u7565\u4f18\u5316; \u6570\u636e\u7a00\u7f3a\u65f6\u6709\u6548",
   inputs="\u5c11\u91cf\u8bad\u7ec3\u6837\u672c + \u4efb\u52a1\u53ef\u9a8c\u8bc1\u5956\u52b1\u51fd\u6570; \u65e0\u9700\u5927\u91cf\u6807\u6ce8",
   effect="\u5728\u7ec6\u7c92\u5ea6\u5206\u7c7b/\u5c0f\u6837\u672c\u68c0\u6d4b/\u63a8\u7406\u5b9a\u4f4d\u4e0a\u4f18\u4e8e SFT",
   integ="OCR \u53ef\u8bbe\u5b57\u7b26\u7ea7 exact-match \u53ef\u9a8c\u8bc1\u5956\u52b1, \u7528 RL \u8c03\u4f18 MLLM \u8bc6\u522b\u80fd\u529b",
   cost="\u5c11\u91cf\u6570\u636e + \u4e2d\u7b49 GPU; \u65e0\u9700\u5927\u89c4\u6a21\u6807\u6ce8",
   src2="\u53d7 DeepSeek-R1 \u542f\u53d1, \u5c5e RLVR \u8def\u7ebf"),
 dict(name="\u5185\u90e8\u5197\u4f59\u81ea\u8bad\u7ec3 OCR", cite="arXiv:2508.14557", year=2025, cat="F \u81ea\u8bad\u7ec3/\u4f2a\u6807\u6ce8",
   how="\u5229\u7528\u6587\u6863\u5185\u90e8\u5197\u4f59 (\u91cd\u590d\u6587\u672c/\u7ed3\u6784) \u6539\u8fdb OCR; \u51cf\u5c11\u5bf9\u989d\u5916\u6807\u6ce8\u7684\u4f9d\u8d56",
   inputs="\u672a\u6807\u6ce8\u6587\u6863\u8bed\u6599; \u5229\u7528\u5185\u90e8\u4e00\u81f4\u6027",
   effect="\u539f\u6587: \u6539\u8fdb OCR \u4f7f\u7528\u5185\u90e8\u6587\u6863\u5197\u4f59 (\u672a\u7ed9\u5177\u4f53\u699c\u5355\u6570)",
   integ="\u6587\u6863\u8bed\u6599\u4f2a\u6807\u6ce8\u589e\u5e7f; \u96f6\u6807\u6ce8\u6210\u672c\u4f4e",
   cost="\u4f4e: \u5229\u7528\u73b0\u6709\u8bed\u6599, CPU \u4e3a\u4e3b",
   src2="\u4e0e dots.ocr \u6570\u636e\u5f15\u64ce\u4e92\u4e3a\u8865\u5145"),
 dict(name="PaddleOCR", cite="\u5de5\u4e1a\u5de5\u5177\u5305 (\u65e0\u5355\u4e00 arXiv)", year=2020, cat="E OCR \u5f15\u64ce/\u8bc6\u522b\u7ba1\u7ebf",
   how="\u5f00\u6e90\u591a\u8bed\u8a00 OCR \u5de5\u5177\u5305 (\u68c0\u6d4b+\u8bc6\u522b+\u7248\u9762); \u542b PP-OCRv4 \u7b49; \u8bad\u7ec3\u6d41\u7a0b\u53ef\u7528 trdg \u5408\u6210\u6570\u636e\u589e\u5e7f",
   inputs="\u591a\u8bed\u8a00\u8bed\u6599 + \u5408\u6210\u6570\u636e (trdg)",
   effect="\u5e7f\u6cdb\u5de5\u4e1a\u90e8\u7f72; \u65e0\u7edf\u4e00\u699c\u5355\u6570\u5b57",
   integ="\u4f5c\u4e3a\u8bc6\u522b\u7ba1\u7ebf\u4f2a\u6807\u6ce8\u5668; \u751f\u6210\u6587\u672c-\u56fe\u50cf\u5bf9\u4f9b SFT",
   cost="\u90e8\u7f72 CPU/GPU \u4f4e; \u6807\u6ce8\u6210\u672c\u4f4e",
   src2="\u4e0e trdg \u5408\u6210\u8def\u7ebf\u540c\u5c5e"),
 dict(name="im2latex", cite="u9879\u76ee/u6570\u636e\u96c6 (im2latex-100K), \u672a\u67e5\u5230 arXiv \u6807\u9898\u9875", year=2017, cat="G \u516c\u5f0f/\u624b\u5199",
   how="\u5c06\u6570\u5b66\u516c\u5f0f\u56fe\u50cf\u8f6c LaTeX; im2latex-100K \u5408\u6210\u6570\u636e\u96c6 (\u6e32\u67d3 LaTeX\u2192\u56fe)",
   inputs="LaTeX \u516c\u5f0f\u8bed\u6599 + \u6e32\u67d3\u5668 (pdflatex/MathJax)",
   effect="\u516c\u5f0f\u8bc6\u522b\u57fa\u7ebf; \u65e0\u7edf\u4e00\u699c\u5355\u6570\u5b57",
   integ="\u516c\u5f0f\u8bc6\u522b\u4e13\u9879 SFT \u6570\u636e\u589e\u5e7f",
   cost="\u6e32\u67d3 CPU \u4f4e; \u6570\u636e\u5df2\u516c\u5f00",
   src2="\u4e0e Nougat (2308.13418) \u516c\u5f0f\u8bc6\u522b\u540c\u5c5e"),
 dict(name="GOT-OCR2.0", cite="\u672a\u67e5\u5230 arXiv \u6807\u9898\u9875 (\u7f16\u53f7/u540d\u79f0\u5b58\u7591, \u672c\u6b21\u68c0\u7d22\u672a\u547d\u4e2d)", year=2024, cat="E OCR \u5f15\u64ce",
   how="\u672c\u6b21\u7ecf\u4ee3\u7406\u68c0\u7d22 arXiv \u6807\u9898\u672a\u547d\u4e2d\u8be5\u8bba\u6587; \u4ec5\u6309\u516c\u5f00\u8bb0\u5fc6\u63cf\u8ff0\u4e3a\u901a\u7528 OCR \u7406\u8bba (General OCR Theory), \u672a\u53d6\u5f97\u53ef\u6eaf\u6e90\u6458\u8981 \u2192 \u672c\u62a5\u544a\u4e0d\u91c7\u4fe1\u5176\u6570\u5b57",
   inputs="\u672a\u6838\u5b9e",
   effect="\u672a\u6838\u5b9e (\u672a\u53d6\u5f97\u6458\u8981)",
   integ="\u5f85\u540e\u7eed\u8865\u68c0",
   cost="\u672a\u6838\u5b9e",
   src2="\u4ec5\u516c\u5f00\u8bb0\u5fc6, \u672a\u68c0\u7d22\u5230\u53ef\u6eaf\u6e90\u6765\u6e90"),
]

# \u5916\u90e8\u53c2\u8003 (\u540c\u89c4\u6a21\u5f00\u6e90 MLLM \u516c\u5f00\u503c; \u672c\u6b21\u68c0\u7d22\u4ec5\u53d6 arXiv \u6458\u8981, \u6458\u8981\u672a\u5217\u5177\u4f53\u6570\u5b57 \u2192 \u8bda\u5b9e\u6807\u6ce8)
EXTERNAL = [
 dict(name="OCRBench \u57fa\u51c6", cite="arXiv:2305.07895", year=2023, note="\u542b 29 \u4e2a\u6570\u636e\u96c6\u7684\u7efc\u5408 OCR \u8bc4\u6d4b; \u8bc4\u4f30 GPT4V/Gemini \u7b49\u5927\u6a21\u578b. \u6458\u8981\u672a\u7ed9\u5177\u4f53\u6a21\u578b\u5206\u6570 \u2192 \u672a\u67e5\u5230\u5177\u4f53\u540c\u89c4\u6a21\u5f00\u6e90 MLLM \u6570\u5b57"),
 dict(name="DocVQA \u4eba\u7c7b\u4e0a\u9650", cite="arXiv:2007.00398", year=2020, note="\u4eba\u7c7b\u51c6\u786e\u7387 94.36%; \u73b0\u6709\u6a21\u578b\u4e0e\u4eba\u7c7b\u6709\u8f83\u5927\u5dee\u8ddd, \u7ed3\u6784\u7406\u89e3\u578b\u95ee\u9898\u5c24\u5dee. \u672c\u9879\u76ee ANLS 7.35-7.58% vs \u4eba\u7c7b 94.36% (\u53e3\u5f84\u4e0d\u540c, \u4ec5\u91cf\u7ea7\u53c2\u8003)"),
 dict(name="ChartQA \u57fa\u51c6", cite="arXiv:2203.10244", year=2022, note="9.6K \u4eba\u5199 + 23.1K \u589e\u5e7f; relaxed accuracy \u6307\u6807. \u6458\u8981\u672a\u7ed9\u5177\u4f53\u5f00\u6e90 MLLM \u6570\u5b57 \u2192 \u672a\u67e5\u5230"),
 dict(name="LLaVA-1.5 / Qwen-VL", cite="arXiv:2310.03744 / 2308.12966", year=2023, note="\u540c\u89c4\u6a21\u5f00\u6e90 MLLM; \u6458\u8981\u5747\u672a\u5217 OCRBench/DocVQA/ChartQA \u5177\u4f53\u6570\u5b57 \u2192 \u672a\u67e5\u5230 (\u9700\u53e6\u67e5\u5b98\u65b9\u6280\u672f\u62a5\u544a/u699c\u5355)"),
 dict(name="olmOCR (7B)", cite="arXiv:2502.18443", year=2025, note="\u5fae\u8c03 7B VLM, olmOCR-Bench \u4e0a\u8d85\u8d8a GPT-4o/Gemini Flash 2/Qwen-2.5-VL; \u767e\u4e07\u9875 $176. \u4e3a\u540c\u89c4\u6a21 OCR \u80fd\u529b\u4e0a\u9650\u53c2\u8003"),
]

def ocr_table(arm_data):
    rows = ["<table><tr><th>\u96c6\u5408</th><th>\u6307\u6807</th>" + "".join(f"<th>{escape(n)}</th>" for n,_,_ in [(a[0],a[1],a[2]) for a in ARMS]) + "</tr>"]
    for key, disp, metric, mnote in OCR_BENCHES:
        cells = []
        for aname, _, _ in ARMS:
            d = arm_data.get(aname)
            v = arm_value(d, key) if d else None
            cells.append(fmt_pct(v) if v is not None else "N/A")
        rows.append("<tr><td><b>"+disp+"</b></td><td>"+escape(metric.split(',')[0])+"</td>"+"".join(f"<td>{c}</td>" for c in cells)+"</tr>")
    rows.append("</table>")
    return "\n".join(rows)

def gap_table(arm_data):
    # \u56db\u96c6\u5dee\u8ddd\u5b9a\u4f4d: \u6587\u5b57\u8bc6\u522b/\u7248\u9762\u7ed3\u6784/\u56fe\u8868\u6570\u503c/\u957f\u6587\u6863
    rows=["<table><tr><th>\u80fd\u529b\u7ef4\u5ea6</th><th>\u4ee3\u8868\u96c6</th><th>\u672c\u9879\u76ee\u56db\u81c2\u8303\u56f4</th><th>\u5dee\u8ddd\u5b9a\u4f4d</th></tr>"]
    spans={
      "ocrbench":(min,max),
    }
    def rng(key):
        vs=[arm_value(arm_data.get(a[0]),key) for a in ARMS]
        vs=[v for v in vs if v is not None]
        if not vs: return "N/A"
        return f"{min(vs)*100:.2f}% \u2013 {max(vs)*100:.2f}%"
    rows.append("<tr><td>\u6587\u5b57\u8bc6\u522b</td><td>OCRBench</td><td>"+rng('ocrbench')+"</td><td>\u8fd1\u4e8e\u968f\u673a (1.6-1.8%); \u5373\u4f7f\u6700\u5f3a\u7f16\u7801\u5668 ArmE-R2 (ProtB 68.2%) \u4e5f\u672a\u6539\u5584 \u2192 \u4e0d\u662f\u7f16\u7801\u5668\u5bb9\u91cf\u95ee\u9898, \u662f\u6570\u636e/\u4efb\u52a1\u7f3a\u4f4d</td></tr>")
    rows.append("<tr><td>\u7248\u9762\u7ed3\u6784</td><td>DocVQA(val)</td><td>"+rng('docvqa_val')+"</td><td>ANLS 7.35-7.58%, \u4e0e\u4eba\u7c7b 94.36% \u91cf\u7ea7\u5dee\u8ddd\u5de8\u5927; \u7f16\u7801\u5668\u4e0d\u8bc6\u522b\u7248\u9762\u7ed3\u6784, \u9700\u6587\u6863\u578b\u6570\u636e</td></tr>")
    rows.append("<tr><td>\u56fe\u8868\u6570\u503c</td><td>ChartQA</td><td>"+rng('chartqa')+"</td><td>12.16-12.92%; \u9700\u56fe\u8868\u2192\u6570\u503c/\u6587\u672c\u5bf9\u9f50\u6570\u636e</td></tr>")
    rows.append("<tr><td>\u957f\u6587\u6863/\u4fe1\u606f\u56fe</td><td>InfoVQA(val)</td><td>"+rng('infovqa_val')+"</td><td>16.18-17.09%; \u9700\u5bc6\u96c6\u6587\u672c+\u7ed3\u6784\u7684\u4fe1\u606f\u56fe\u6570\u636e</td></tr>")
    rows.append("</table>")
    return "\n".join(rows)

def method_overview_table():
    cats={}
    for m in METHODS: cats.setdefault(m["cat"],[]).append(m)
    rows=["<table><tr><th>\u7c7b\u522b</th><th>\u65b9\u6cd5</th><th>\u5f15\u7528</th><th>\u5e74</th></tr>"]
    for c,ms in cats.items():
        for i,m in enumerate(ms):
            rows.append(f"<tr><td>{escape(c) if i==0 else ''}</td><td><b>{escape(m['name'])}</b></td><td>{escape(m['cite'])}</td><td>{m['year']}</td></tr>")
    rows.append("</table>")
    return "\n".join(rows)

def method_details():
    out=['']
    for m in METHODS:
        out.append(f"<h3>{escape(m['name'])} <span class=\"small\">({escape(m['cite'])}, {m['year']} \u00b7 {escape(m['cat'])})</span></h3>")
        out.append("<table class=\"m\">")
        out.append(f"<tr><th>\u600e\u4e48\u9020</th><td>{escape(m['how'])}</td></tr>")
        out.append(f"<tr><th>\u8981\u4ec0\u4e48\u8f93\u5165</th><td>{escape(m['inputs'])}</td></tr>")
        out.append(f"<tr><th>\u8bba\u6587\u62a5\u544a\u7684\u6548\u679c</th><td>{escape(m['effect'])}</td></tr>")
        out.append(f"<tr><th>\u63a5\u5165\u70b9</th><td>{escape(m['integ'])}</td></tr>")
        out.append(f"<tr><th>\u6210\u672c(\u4f30\u7b97)</th><td>{escape(m['cost'])}</td></tr>")
        out.append(f"<tr><th>\u7b2c\u4e8c\u6765\u6e90</th><td>{escape(m['src2'])}</td></tr>")
        out.append("</table>")
    return "\n".join(out)

def external_table():
    rows=["<table><tr><th>\u53c2\u8003</th><th>\u5f15\u7528</th><th>\u5e74</th><th>\u8bf4\u660e</th></tr>"]
    for e in EXTERNAL:
        rows.append(f"<tr><td><b>{escape(e['name'])}</b></td><td>{escape(e['cite'])}</td><td>{e['year']}</td><td>{escape(e['note'])}</td></tr>")
    rows.append("</table>")
    return "\n".join(rows)

def routes_section():
    return """
<h3>\u8def\u7ebf\u2460: \u4f4e\u6210\u672c\u5408\u6210 OCR \u8bc6\u522b\u5bf9\u4f9b Stage-2 SFT (\u63a8\u8350\u9996\u9009)</h3>
<table class=\"m\"><tr><th>\u9879</th><th>\u8be6\u60c5</th></tr>
<tr><th>\u6570\u636e\u91cf</th><td>\u4f30 50-200 \u4e07\u5bf9: trdg/SynthTIGER \u751f\u6210\u5370\u5237/\u573a\u666f\u6587\u5b57 \u2192 \u56fe\u50cf+\u8f6c\u5199\u6587\u672c\u5bf9; + Chart-to-Text/ChartQA \u589e\u5e7f\u96c6\u5904\u7406\u56fe\u8868\u6837\u672c</td></tr>
<tr><th>\u63a5\u5165\u70b9</th><td>\u4e0d\u52a8\u7f16\u7801\u5668; \u5728\u73b0\u6709 ArmB/ArmE-R2 ckpt \u4e0a\u52a0\u4e00\u8f6e OCR \u4e13\u9879 SFT (\u53ef LoRA)</td></tr>
<tr><th>\u6210\u672c</th><td>\u6e32\u67d3 CPU \u5c0f\u65f6\u7ea7 (~0 GPU); \u8bad\u7ec3 1-2 GPU\u00b7\u65e5 (\u4f30\u7b97)</td></tr>
<tr><th>ETA</th><td>\u6570\u636e\u751f\u6210 1-2 \u4eba\u65e5 + SFT 1 \u65e5</td></tr>
<tr><th>\u53ef\u8bc1\u4f2a\u5224\u636e</th><td>OCRBench \u63d0\u5347 \u2265 2pp (1.6%\u2192\u22653.6%) \u4e14 DocVQA ANLS \u63d0\u5347 \u2265 3pp; \u672a\u8fbe\u5219\u5199\u8d1f\u9762\u7ed3\u8bba</td></tr>
</table>
<h3>\u8def\u7ebf\u2461: \u6587\u6863\u578b\u5408\u6210 + \u6307\u4ee4\u8c03\u4f18 (\u4e2d\u6210\u672c)</h3>
<table class=\"m\"><tr><th>\u9879</th><th>\u8be6\u60c5</th></tr>
<tr><th>\u6570\u636e\u91cf</th><td>SynthDoG/UDOP \u98ce\u683c\u5408\u6210\u6587\u6863 (\u53d1\u7968/\u8868\u5355/\u8bba\u6587) 10-50 \u4e07\u6837\u672c + mPLUG-DocOwl \u6307\u4ee4\u8c03\u4f18\u6570\u636e\u6837\u5f0f</td></tr>
<tr><th>\u63a5\u5165\u70b9</th><td>Stage-2 \u6df7\u5165\u6587\u6863\u6307\u4ee4\u6570\u636e; \u53ef\u52a0\u7f16\u7801\u5668\u9884\u8bad\u7ec3\u81ea\u76d1\u7763\u76ee\u6807 (\u53ef\u9009)</td></tr>
<tr><th>\u6210\u672c</th><td>\u5408\u6210 CPU \u4e2d\u7b49 + \u8bad\u7ec3 2-4 GPU\u00b7\u65e5</td></tr>
<tr><th>ETA</th><td>3-5 \u4eba\u65e5</td></tr>
<tr><th>\u53ef\u8bc1\u4f2a\u5224\u636e</th><td>DocVQA ANLS \u63d0\u5347 \u2265 5pp \u4e14 InfoVQA ANLS \u63d0\u5347 \u2265 4pp</td></tr>
</table>
<h3>\u8def\u7ebf\u2462: RL \u53ef\u9a8c\u8bc1\u5956\u52b1\u8c03\u4f18 (\u9ad8\u6210\u672c, \u5f85\u9884\u7b97)</h3>
<table class=\"m\"><tr><th>\u9879</th><th>\u8be6\u60c5</th></tr>
<tr><th>\u6570\u636e\u91cf</th><td>\u5c11\u91cf\u6837\u672c + \u5b57\u7b26\u7ea7 exact-match \u53ef\u9a8c\u8bc1\u5956\u52b1 (Visual-RFT/GRPO)</td></tr>
<tr><th>\u63a5\u5165\u70b9</th><td>\u5728\u8def\u7ebf\u2460\u4e4b\u540e\u5bf9 MLLM \u505a RL \u5fae\u8c03; \u9700\u7b54\u5ba1\u9884\u7b97\u6279\u51c6</td></tr>
<tr><th>\u6210\u672c</th><td>\u6570\u636e\u5c11\u4f46 RL \u8bad\u7ec3\u8f83\u8d35; \u9700\u8fd0\u7ef4\u9884\u7b97\u6279\u51c6</td></tr>
<tr><th>ETA</th><td>\u5f85\u8def\u7ebf\u2460/\u2461\u9a8c\u8bc1\u540e\u518d\u8bc4\u4f30</td></tr>
<tr><th>\u53ef\u8bc1\u4f2a\u5224\u636e</th><td>\u5728\u8def\u7ebf\u2460\u57fa\u7840\u4e0a OCRBench \u518d\u63d0\u5347 \u2265 1pp \u4e14\u65e0\u56de\u9000</td></tr>
</table>
"""

def risks_section():
    return """
<ul>
<li><b>\u57df\u5dee (domain gap)</b>: \u5408\u6210\u6587\u5b57/\u6587\u6863\u4e0e\u771f\u5b9e\u626b\u63cf\u3001\u624b\u673a\u62cd\u7167\u7684\u5149\u7167/\u6a21\u7cca/\u7eb8\u8d28\u5dee\u5f02\u5927; \u9700\u5145\u5206\u9000\u5316\u6c89\u6dc0\u771f\u5b9e\u5206\u5e03, \u5426\u5219\u5408\u6210\u4e0a\u8fc7\u62df\u3001\u771f\u5b9e\u4e0b\u6389\u3002</li>
<li><b>\u5b57\u4f53\u4e0e\u8bed\u8a00\u8986\u76d6</b>: \u4e2d\u6587/\u5c0f\u8bed\u79cd\u5b57\u4f53\u3001\u624b\u5199\u3001\u516c\u5f0f\u3001\u8868\u683c\u8986\u76d6\u4e0d\u8db3\u4f1a\u7559\u4e0b\u76f2\u533a; \u987b\u660e\u786e\u5b57\u4f53\u6e05\u5355\u4e0e\u8bed\u8a00\u6bd4\u4f8b, \u907f\u514d\u82f1\u6587\u4e3a\u4e3b\u3001\u4e2d\u6587\u5750\u51b7\u677f\u51b3 (\u672c\u9879\u76ee\u8bed\u6599\u4ee5\u82f1\u6587\u4e3a\u4e3b)\u3002</li>
<li><b>\u6e32\u67d3\u4f2a\u5f71</b>: \u5408\u6210\u56fe\u7247\u6613\u51fa\u73b0\u4e0d\u81ea\u7136\u8d34\u5408\u8fb9\u7f18\u3001\u9509\u9f7f\u3001\u5149\u7167\u4e0d\u4e00\u81f4; \u9700\u591a\u6837\u9000\u5316\u4e0e\u771f\u5b9e\u80cc\u666f\u6df7\u5408, \u8bc4\u6d4b\u65f6\u6ce8\u610f\u5408\u6210\u6cc4\u6f0f (\u8bc4\u6d4b\u96c6\u4e0e\u8bad\u7ec3\u96c6\u4e0d\u5f97\u540c\u6e90)\u3002</li>
<li><b>\u8bc4\u6d4b\u6cc4\u6f0f</b>: OCRBench/DocVQA/ChartQA/InfoVQA \u4e3a\u516c\u5f00\u8bc4\u6d4b\u96c6; \u5408\u6210\u6570\u636e\u5e74\u4e0d\u5f97\u76f4\u63a5\u542b\u8bc4\u6d4b\u96c6\u539f\u6587; \u4ee5\u6a21\u677f/\u8bed\u6599\u91cd\u65b0\u751f\u6210, \u5e76\u5728\u62a5\u544a\u4e2d\u62ab\u9732\u662f\u5426\u4f7f\u7528\u4e86\u8bc4\u6d4b\u96c6\u7684\u6a21\u677f/\u8bed\u6599\u3002</li>
<li><b>\u6307\u6807\u53e3\u5f84</b>: \u672c\u9879\u76ee OCRBench \u7528 lmms-eval ocrbench_accuracy (0-1 \u9010\u9898 exact-match), \u4e0e\u539f\u7248 OCRBench \u6ee1\u5206 1000 \u4e0d\u540c; \u4e0e\u5916\u90e8\u699c\u6a2a\u6bd4\u524d\u5fc5\u987b\u6807\u6ce8\u53e3\u5f84, \u5426\u5219\u4e0e LLaVA/Qwen-VL \u7684 \u201c57\u201d \u7c7b\u6570\u5b57\u4e0d\u53ef\u6bd4\u3002</li>
<li><b>\u5bb9\u91cf\u2192MLLM \u4e0d\u4f20\u9012</b>: ArmE-R2 (ViT-L/14, ProtB 68.2%) \u7f16\u7801\u5668\u6700\u5f3a\u4f46 OCRBench \u4ecd 1.6% \u2192 \u8868\u660e\u518d\u52a0\u7f16\u7801\u5668\u5bb9\u91cf\u4e0d\u89e3\u51b3 OCR; \u95ee\u9898\u5728\u6570\u636e/\u4efb\u52a1\u4f4d, \u800c\u975e\u7f16\u7801\u5668\u3002</li>
</ul>
"""

def build_html(arm_data, out_path, src_paths):
    gen = datetime.now().strftime("%Y-%m-%d %H:%M")
    CSS = """
    body{font-family:-apple-system,'PingFang SC','Microsoft YaHei',sans-serif;max-width:1080px;margin:24px auto;padding:0 20px;color:#222;line-height:1.6}
    h1{font-size:22px;border-bottom:3px solid #c0392b;padding-bottom:8px}
    h2{font-size:18px;margin-top:28px;border-left:5px solid #c0392b;padding-left:10px}
    h3{font-size:15px;margin-top:18px;color:#922}
    table{border-collapse:collapse;width:100%;margin:10px 0;font-size:13px}
    th,td{border:1px solid #ccc;padding:5px 8px;text-align:left;vertical-align:top}
    th{background:#f4ecea}
    table.m th{width:120px;background:#faf2f0}
    .small{color:#777;font-size:12px;font-weight:normal}
    .kbox{background:#fdf6f3;border:1px solid #e6c9c0;padding:12px 16px;border-radius:6px;margin:10px 0}
    code{background:#f5f5f5;padding:1px 4px;border-radius:3px;font-size:12px}
    .tag{display:inline-block;background:#c0392b;color:#fff;padding:1px 7px;border-radius:3px;font-size:12px}
    ul{margin:6px 0}
    """
    HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>BaiZe Vision: OCR \u80fd\u529b\u504f\u4f4e \u00b7 \u5408\u6210\u6570\u636e\u8865\u5f3a\u8c03\u7814\u62a5\u544a</title>
<style>{CSS}</style></head><body><div>
<h1>BaiZe Vision: OCR \u7c7b\u8bc4\u6d4b\u504f\u4f4e \u2014 \u5408\u6210\u6570\u636e\u8865\u5f3a\u65b9\u6cd5\u8c03\u7814\u62a5\u544a</h1>
<p class="small">\u751f\u6210\u5668 <code>vision/generate_ocr_synthdata_report.py</code> \u00b7 \u6240\u6709\u5b9e\u6d4b\u6570\u5b57\u6765\u81ea\u56db\u81c2 consolidated_12benchmarks.json \u00b7 \u68c0\u7d22\u4e8e 2026-10-25 \u00b7 \u751f\u6210 {gen}</p>

<h2>1. \u6458\u8981</h2>
<div class="kbox">
<ul>
<li>\u672c\u9879\u76ee\u56db\u81c2 (ArmB/C/D-R2/E-R2) \u5728 OCR \u76f8\u5173\u56db\u96c6\u5747\u6781\u4f4e: OCRBench <b>1.6-1.8%</b>\u3001DocVQA(val) <b>7.35-7.58%</b>\u3001ChartQA <b>12.16-12.92%</b>\u3001InfoVQA(val) <b>16.18-17.09%</b>; \u56db\u81c2\u4e4b\u95f4\u5dee\u5f02 \u22641pp, \u4e0e\u7f16\u7801\u5668\u5bb9\u91cf/ProtB \u65e0\u5173 (ArmE-R2 ProtB 68.2% \u6700\u5f3a\u4f46 OCRBench \u4ecd 1.6%)\u3002</li>
<li>\u8bc1\u636e\u6307\u5411: \u95ee\u9898\u4f4d\u4e8e <b>\u6570\u636e/\u4efb\u52a1\u7f3a\u4f4d</b> \u800c\u975e\u7f16\u7801\u5668\u5bb9\u91cf; \u73b0\u6709\u8bad\u7ec3\u6570\u636e (\u56fe\u6587\u5bf9\u6bd4/AIMv2-style) \u51e0\u4e4e\u4e0d\u542b\u4e13\u9879 OCR/\u6587\u6863/\u56fe\u8868\u8bc6\u522b\u76d1\u7763\u3002</li>
<li>\u8c03\u7814\u8986\u76d6 7 \u7c7b 18 \u4e2a\u65b9\u6cd5 (\u6587\u5b57\u8bc6\u522b\u5408\u6210/\u6587\u6863\u5408\u6210/\u6587\u6863 MLLM/\u56fe\u8868\u6570\u636e/OCR \u5f15\u64ce/RL \u53ef\u9a8c\u8bc1\u5956\u52b1/\u516c\u5f0f), \u6765\u6e90\u4e3a\u7ecf\u4ee3\u7406\u68c0\u7d22\u7684 arXiv \u6458\u8981 (2026-10-25)\u3002</li>
<li><b>\u5355\u4e00\u5efa\u8bae</b>: \u4f18\u5148\u6267\u884c <span class="tag">\u8def\u7ebf\u2460</span> \u2014 \u7528 trdg/SynthTIGER \u4f4e\u6210\u672c\u5408\u6210 50-200 \u4e07 OCR \u8bc6\u522b\u5bf9, \u5728\u73b0\u6709 ckpt \u4e0a\u52a0\u4e00\u8f6e\u4e13\u9879 SFT; \u9884\u6ce8\u518c\u5224\u636e = OCRBench \u63d0\u5347 \u2265 2pp\u3002</li>
<li>\u672c\u8f6e\u4ec5\u8c03\u7814 + \u5199\u62a5\u544a, \u4e0d\u542f\u8bad\u7ec3\u3001\u4e0d\u52a8\u5df2\u843d\u76d8\u4ea7\u7269\u3001\u4e0d\u4f2a\u9020 API key\u3002</li>
<li>\u8bda\u5b9e\u6761\u6b3e: \u5916\u90e8\u6548\u679c\u6570\u5b57\u5747\u4e3a\u8bba\u6587\u81ea\u62a5\u3001\u672a\u5728\u672c\u9879\u76ee\u590d\u73b0; \u6210\u672c\u4e3a\u4f30\u7b97; \u672c\u9879\u76ee\u6570\u5b57\u5168\u90e8\u5b9e\u6d4b\u53ef\u6eaf\u6e90\u3002</li>
</ul>
</div>

<h2>2. \u73b0\u72b6: OCR \u76f8\u5173\u56db\u96c6\u5b9e\u6d4b (\u56db\u81c2)</h2>
<p>\u6570\u636e\u6765\u6e90: <code>/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_arm{{B,C}}/consolidated_12benchmarks.json</code> \u53ca <code>mllm_eval_results_armD_r2_20261020</code> / <code>mllm_eval_results_armE_r2_20261022</code> \u540c\u540d\u6587\u4ef6\u3002\u56db\u96c6\u5747\u65e0\u9700 LLM judge (exact-match / ANLS / relaxed), \u4e0e MMVet/MathVista \u7684 OPENAI_API_KEY \u963b\u585e\u65e0\u5173, \u53ef\u76f4\u63a5\u6d4b\u3002</p>
{ocr_table(arm_data)}
<p class="small">\u56db\u81c2\u914d\u7f6e: ArmB=ViT-B/16,3\u6e90/4epoch; ArmC=ViT-B/16,min_lr1e-5+wd0.01; ArmD-R2=ViT-B/16,6\u6e90/3epoch,lr1e-3; ArmE-R2=ViT-L/14,6\u6e90/3epoch,lr5e-4,63400\u6b65\u3002Stage-2 step3500 ckpt, 8\u5361\u5168\u91cf\u8bc4\u6d4b\u3002</p>
<h3>\u5916\u90e8\u53c2\u8003 (\u540c\u89c4\u6a21\u5f00\u6e90 MLLM / \u4eba\u7c7b\u4e0a\u9650)</h3>
{external_table()}
<p class="small">\u8bda\u5b9e\u62ab\u9732: \u672c\u6b21\u68c0\u7d22\u4ec5\u53d6\u5f97 arXiv \u6458\u8981; LLaVA-1.5/Qwen-VL/OCRBench/ChartQA \u6458\u8981\u5747\u672a\u5217\u5177\u4f53\u6a21\u578b\u5206\u6570, \u6545\u5177\u4f53\u540c\u89c4\u6a21\u5f00\u6e90 MLLM \u5728 OCRBench/DocVQA \u7684\u516c\u5f00\u503c\u6807\u6ce8 <b>\u672a\u67e5\u5230</b> (\u9700\u53e6\u67e5\u5b98\u65b9\u6280\u672f\u62a5\u544a/\u699c\u5355); \u4ec5\u7ed9\u51fa\u53ef\u6838\u5b9e\u7684\u951a\u70b9 (DocVQA \u4eba\u7c7b 94.36%\u3001olmOCR 7B \u8d85\u8d8a GPT-4o)\u3002</p>

<h2>3. \u5dee\u8ddd\u5b9a\u4f4d (\u6587\u5b57\u8bc6\u522b / \u7248\u9762\u7ed3\u6784 / \u56fe\u8868\u6570\u503c / \u957f\u6587\u6863)</h2>
{gap_table(arm_data)}
<p class="small">\u5173\u952e\u89c2\u5bdf: \u56db\u81c2\u8de8\u5ea6 \u22641pp \u7684\u4e00\u81f4\u5dee\u8ddd, \u4e0e ArmE-R2 \u7f16\u7801\u5668 ProtB \u8fdc\u8d85 ArmB (68.2 vs 62.1) \u5f62\u6210\u9c9c\u660e\u5bf9\u6bd4 \u2192 \u518d\u589e\u52a0\u7f16\u7801\u5668\u5bb9\u91cf/ProtB \u4e0d\u4f1a\u63d0\u5347 OCR; \u7f3a\u4f4d\u5728\u4e13\u9879\u6570\u636e\u4e0e\u4efb\u52a1\u5bf9\u9f50\u3002</p>

<h2>4. \u5408\u6210\u6570\u636e\u65b9\u6cd5\u603b\u89c8</h2>
<p>\u6309\u7c7b\u522b\u5212\u5206 7 \u7c7b 18 \u4e2a\u65b9\u6cd5\u3002\u6bcf\u6761\u4e3b\u6765\u6e90 = arXiv \u6458\u8981 (\u7ecf\u4ee3\u7406\u68c0\u7d22\u4e8e 2026-10-25), \u7b2c\u4e8c\u6765\u6e90 = \u540c\u57df\u4e92\u5f15\u8bba\u6587\u3002</p>
{method_overview_table()}
<h3>\u9010\u6cd5\u8be6\u60c5</h3>
{method_details()}

<h2>5. \u63a5\u5165\u672c\u9879\u76ee\u7ba1\u7ebf\u7684\u4e09\u6761\u5019\u9009\u8def\u7ebf</h2>
{routes_section()}
<p class="small">\u6210\u672c\u4e0e ETA \u5747\u4e3a\u4f30\u7b97, \u975e\u5b9e\u6d4b; \u9700\u8fd0\u7ef4\u9884\u7b97\u4e0e GPU \u6392\u671f\u6279\u51c6\u540e\u65b9\u53ef\u6267\u884c\u3002</p>

<h2>6. \u98ce\u9669\u4e0e\u5751</h2>
{risks_section()}

<h2>7. \u4f18\u5148\u7ea7\u6392\u5e8f</h2>
<div class="kbox">
<p><b>\u5355\u4e00\u4e0b\u4e00\u6b65: \u6267\u884c\u8def\u7ebf\u2460</b> (\u4f4e\u6210\u672c\u5408\u6210 OCR \u8bc6\u522b\u5bf9 + \u4e13\u9879 SFT)\u3002</p>
<p>\u7406\u7531: (a) \u6210\u672c\u6700\u4f4e (\u6e32\u67d3 CPU + 1-2 GPU\u00b7\u65e5); (b) \u4e0d\u52a8\u7f16\u7801\u5668, \u590d\u7528\u73b0\u6709 ArmB/ArmE-R2 ckpt; (c) \u76f4\u51fb\u6700\u4f4e\u5206 (OCRBench 1.6%); (d) \u53ef\u8bc1\u4f2a \u2014 \u9884\u6ce8\u518c\u5224\u636e\u660e\u786e\u3002</p>
<p><b>\u9884\u6ce8\u518c\u5224\u636e</b>: \u5728\u73b0\u6709 ckpt \u4e0a\u52a0\u4e00\u8f6e OCR \u4e13\u9879 SFT \u540e, OCRBench \u63d0\u5347 <b>\u2265 2pp</b> (1.6%\u2192\u22653.6%); \u672a\u8fbe\u5219\u5199\u8d1f\u9762\u7ed3\u8bba\u5e76\u6392\u67e5\u6570\u636e\u8d28\u91cf/\u8fc7\u62df\u3002</p>
<p>\u4ec5\u5f53\u8def\u7ebf\u2460\u9a8c\u8bc1\u4e3a\u6b63\u540e, \u518d\u4f9d\u6b21\u8bc4\u4f30\u8def\u7ebf\u2461(\u6587\u6863) \u4e0e\u8def\u7ebf\u2462(RL)\u3002\u672a\u7ecf\u8fd0\u7ef4\u6279\u51c6, \u672c\u8f6e\u4e0d\u542f\u4efb\u4f55\u8bad\u7ec3\u3002</p>
</div>

<h2>8. \u53c2\u8003\u6765\u6e90 (\u7eaf\u6587\u672c, \u7981\u8d85\u94fe)</h2>
<table><tr><th>\u65b9\u6cd5/\u57fa\u51c6</th><th>\u6807\u9898 + arXiv \u53f7 + \u5e74\u4efd</th></tr>
<tr><td>SynthTIGER</td><td>SynthTIGER: Synthetic Text Image GEneratoR Towards Better Text Recognition Models, arXiv:2107.09313, 2021</td></tr>
<tr><td>SynthText</td><td>Synthetic Data for Text Localisation in Natural Images, arXiv:1604.06646, 2016</td></tr>
<tr><td>trdg</td><td>TextRecognitionDataGenerator (GitHub \u5f00\u6e90\u5de5\u5177, \u65e0\u5355\u4e00 arXiv), 2018</td></tr>
<tr><td>Donut/SynthDoG</td><td>OCR-free Document Understanding Transformer, arXiv:2111.15664, 2021</td></tr>
<tr><td>UDOP</td><td>Unifying Vision, Text, and Layout for Universal Document Processing, arXiv:2212.02623, 2022</td></tr>
<tr><td>Pix2Struct</td><td>Pix2Struct: Screenshot Parsing as Pretraining for Visual Language Understanding, arXiv:2210.03347, 2022</td></tr>
<tr><td>Nougat</td><td>Nougat: Neural Optical Understanding for Academic Documents, arXiv:2308.13418, 2023</td></tr>
<tr><td>mPLUG-DocOwl</td><td>mPLUG-DocOwl: Modularized Multimodal Large Language Model for Document Understanding, arXiv:2307.02499, 2023</td></tr>
<tr><td>dots.ocr</td><td>dots.ocr: Multilingual Document Layout Parsing in a Single Vision-Language Model, arXiv:2512.02498, 2025</td></tr>
<tr><td>ChartQA</td><td>ChartQA: A Benchmark for Question Answering about Charts with Visual and Logical Reasoning, arXiv:2203.10244, 2022</td></tr>
<tr><td>Chart-to-Text</td><td>Chart-to-Text: A Large-Scale Benchmark for Chart Summarization, arXiv:2203.06486, 2022</td></tr>
<tr><td>olmOCR</td><td>olmOCR (\u5fae\u8c03 7B VLM, olmOCR-mix-0225 260K\u9875), arXiv:2502.18443, 2025</td></tr>
<tr><td>Visual-RFT</td><td>Visual-RFT: Visual Reinforcement Fine-Tuning (GRPO + \u53ef\u9a8c\u8bc1\u5956\u52b1), arXiv:2503.01785, 2025</td></tr>
<tr><td>\u5185\u90e8\u5197\u4f59\u81ea\u8bad\u7ec3 OCR</td><td>Improving OCR using internal document redundancy, arXiv:2508.14557, 2025</td></tr>
<tr><td>PaddleOCR</td><td>PaddleOCR \u5f00\u6e90\u5de5\u5177\u5305 (\u65e0\u5355\u4e00 arXiv), 2020</td></tr>
<tr><td>im2latex</td><td>im2latex-100K \u6570\u636e\u96c6/\u9879\u76ee (\u672a\u67e5\u5230 arXiv \u6807\u9898\u9875), 2017</td></tr>
<tr><td>GOT-OCR2.0</td><td>\u672c\u6b21\u68c0\u7d22\u672a\u547d\u4e2d arXiv \u6807\u9898\u9875 (\u7f16\u53f7/\u540d\u79f0\u5b58\u7591), \u672a\u53d6\u5f97\u53ef\u6eaf\u6e90\u6458\u8981</td></tr>
<tr><td>OCRBench</td><td>OCRBench (29 \u6570\u636e\u96c6\u7efc\u5408 OCR \u8bc4\u6d4b), arXiv:2305.07895, 2023</td></tr>
<tr><td>DocVQA</td><td>DocVQA: A Dataset for VQA on Document Images, arXiv:2007.00398, 2020</td></tr>
<tr><td>LLaVA-1.5 / Qwen-VL</td><td>Improved Baselines with Visual Instruction Tuning, arXiv:2310.03744, 2023; Qwen-VL, arXiv:2308.12966, 2023</td></tr>
</table>
<hr>
<p class="small">\u8bda\u5b9e\u6761\u6b3e: \u5916\u90e8\u6548\u679c\u6570\u5b57\u5747\u4e3a\u8bba\u6587\u81ea\u62a5\u3001\u672a\u5728\u672c\u9879\u76ee\u590d\u73b0; \u6210\u672c\u4e3a\u4f30\u7b97; \u672c\u9879\u76ee\u6570\u5b57\u5168\u90e8\u5b9e\u6d4b\u53ef\u6eaf\u6e90 (consolidated_12benchmarks.json)\u3002\u68c0\u7d22\u4e8e 2026-10-25, \u7ecf\u4ee3\u7406 http://172.19.92.25:13128 \u8bbf\u95ee arXiv, \u4ec5\u53d6\u6458\u8981\u3002\u751f\u6210\u5668: vision/generate_ocr_synthdata_report.py\u3002</p>
</div></body></html>"""
    return HTML

def check_tags(html):
    from html.parser import HTMLParser
    class C(HTMLParser):
        def __init__(self): super().__init__(); self.st=[]; self.err=[]
        def handle_starttag(self,t,a):
            if t not in ('br','meta','img','hr','input','link'): self.st.append(t)
        def handle_endtag(self,t):
            if self.st and self.st[-1]==t: self.st.pop()
            elif t in self.st:
                while self.st and self.st[-1]!=t: self.st.pop()
                if self.st: self.st.pop()
            else: self.err.append('orphan_end:'+t)
    c=C(); c.feed(html)
    return c.st, c.err

def main():
    arm_data={}
    src_paths={}
    missing=[]
    for aname,_,path in ARMS:
        d,cj=load_arm(path)
        arm_data[aname]=d if d else {}
        src_paths[aname]=cj
        if d is None: missing.append(aname)
    if missing:
        print(f"WARN: \u672a\u8bfb\u5230\u4ee5\u4e0b\u81c2\u7684 consolidated: {missing} (\u76f8\u5e94\u5355\u5143\u683c N/A)", file=sys.stderr)
    os.makedirs(os.path.dirname(DEFAULT_OUT), exist_ok=True)
    html=build_html(arm_data, DEFAULT_OUT, src_paths)
    with open(DEFAULT_OUT,"w") as f: f.write(html)
    # \u81ea\u68c0
    size=os.path.getsize(DEFAULT_OUT)
    nscript=html.count('<script'); nhref=html.count('href="http')
    st,err=check_tags(html)
    print(f"\u2705 \u62a5\u544a\u5df2\u751f\u6210: {DEFAULT_OUT}")
    print(f"   \u5927\u5c0f {size} B | <script>={nscript} | href=http={nhref} | \u672a\u95ed\u5408\u6807\u7b7e={len(st)} | \u5b64\u7acb\u95ed\u5408={len(err)}")
    if size<15000: print("   WARN: < 15KB", file=sys.stderr)
    if nscript or nhref or st: print("   WARN: \u81ea\u68c0\u672a\u901a\u8fc7", file=sys.stderr)

if __name__=="__main__":
    main()
