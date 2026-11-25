#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_armE_r2_full_report.py - ArmE-R2 (2026-10-22->10-24) complete 7-section Chinese report generator.
All numbers from on-disk artifacts (train log / ProtB json / 12-bench consolidated json / 3-stage logs / config.json),
no extrapolation. Missing fields written as N/A + reason.
Output: reports/report_vision_armE_r2_20261024_zh.html (self-contained, no external CDN, no <script>, balanced tags).
"""
import os
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
OUT_PATH = os.path.join(REPORTS_DIR, "report_vision_armE_r2_20261024_zh.html")
GEN_TIME = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

TRAIN_T0 = "2026-10-22 17:52:54"
TRAIN_DONE = "2026-10-24 06:57:43"
TRAIN_HOURS = 37.07
TRAIN_ITS = "0.47-0.48"
TRAIN_PEAK_GB = 77.5
TRAIN_STEPS = 63400
MILESTONES = [
    (20, 8.7869, 7.6463, 1.1406, "3.17e-06", 0.30, 0.0005, 1.1),
    (1000, 4.0128, 3.9302, 0.0826, "1.67e-04", 0.47, 0.0196, 35.4),
    (3000, 2.7150, 2.6644, 0.0506, "5.00e-04", 0.47, 0.0696, 105.4),
    (5000, 1.0159, 0.9894, 0.0265, "4.99e-04", 0.48, 0.3718, 175.4),
    (10000, 0.5444, 0.5284, 0.0160, "4.84e-04", 0.48, 0.5895, 350.4),
    (20000, 0.3577, 0.3429, 0.0148, "4.10e-04", 0.48, 0.7097, 700.5),
    (30000, 0.4248, 0.4138, 0.0110, "2.96e-04", 0.47, 0.6611, 1052.9),
    (40000, 0.2162, 0.2076, 0.0086, "1.70e-04", 0.48, 0.8125, 1402.6),
    (45240, 0.0410, 0.0342, 0.0067, "1.11e-04", 0.47, 0.9664, 1588.8),
    (50000, 0.8143, 0.8079, 0.0064, "6.71e-05", 0.47, 0.4458, 1755.1),
    (60000, 0.1478, 0.1425, 0.0053, "1.38e-05", 0.48, 0.8672, 2104.7),
    (63400, 0.1612, 0.1570, 0.0042, "1.00e-05", 0.48, 0.8547, 2223.7),
]
SPIKE_N_EPISODES = 26
SPIKE_PEAK_LOSS = 1.4299
SPIKE_PEAK_STEP = 28520
SPIKE_TROUGH_LOSS = 0.1019
SPIKE_TROUGH_STEP = 52500
SPIKE_RECOVERY_STEPS = 760
SPIKE_C1_MAX = 0.9664
SPIKE_C1_MAX_STEP = 45240
SPIKE_C1_LOW_AFTER_WARMUP = 0
CKPT_ON_DISK = [
    "checkpoint_60000.pt (4.79 GB)", "checkpoint_63400.pt (4.79 GB)",
    "latest.pt (4.79 GB, =step 63400)", "open_clip_state_dict.pt (1.59 GB, export)",
    "predictor.pt (6.31 MB, training-time aux head)", "config.json (957 B)",
]
NAN_OOM_GREP = ("grep -inE 'nan|out of memory|oom' /tmp/armE_r2_openclip_train.log "
                "(exclude 'OOM-forced' config note) -> 0 lines matched")
ARME_DIVERGE_STEP = 29400
ARME_DIVERGE_LOSS = 8.1037
ARME_DIVERGE_C1 = 0.0007
ARME_C1_LOW_COUNT = 285
ARME_R2_SAMEPOINT_LOSS = 0.5480
ARME_R2_SAMEPOINT_C1 = 0.5841
PROTB = {"lp": 68.236, "lp_sigma": 0.0182, "knn5": 58.904,
         "per_seed": [68.212, 68.256, 68.240],
         "ckpt": "open_clip_state_dict.pt (= latest = step 63400)"}
PROTB_ARMS = [
    ("ArmE-R2 (champion)", 68.236, 0.0182, 58.904, [68.212, 68.256, 68.240]),
    ("ArmD-R2 (main control)", 64.337, 0.0034, 55.956, [64.334, 64.336, 64.342]),
    ("ArmC", 62.332, 0.014, 54.718, [62.352, 62.322, 62.322]),
    ("ArmB", 62.093, 0.012, 58.102, [62.084, 62.086, 62.110]),
]
PROTB_DELTA = {"vs_armd": {"lp": 3.899, "knn5": 2.948},
                "vs_armc": {"lp": 5.904, "knn5": 4.186},
                "vs_armb": {"lp": 6.143, "knn5": 0.802}}
STAGES = [
    {"name": "Stage-1", "full": "Projector align (1024->2560)",
     "steps": 2500, "start": "07:23:38", "end": "07:32:19", "minutes": 7.0,
     "loss_start": 8.9952, "loss_end": 4.1602, "start_step": 10, "end_step": 2500,
     "gpu": "11.0 GB", "lr": "1.0e-4 -> 1.0e-6 (cosine)", "mid": []},
    {"name": "Stage-1.5", "full": "LoRA(r=64) + Projector mid-train",
     "steps": 20000, "start": "07:32:19", "end": "09:12:30", "minutes": 99.1,
     "loss_start": 4.0140, "loss_end": 3.6814, "start_step": 50, "end_step": 20000,
     "gpu": "14.6 GB",
     "lr": "lr_lora 2.0e-5 -> 1.0e-6 / lr_proj 1.0e-5 -> 1.0e-6 (cosine)",
     "mid": [(5000, 3.7696), (10000, 3.5458), (15000, 3.7773)]},
    {"name": "Stage-2", "full": "Instruct tuning (orig LLaVA-NeXT-780k, 738588 samples)",
     "steps": 3500, "start": "09:12:30", "end": "09:35:03", "minutes": 16.7,
     "loss_start": 5.2419, "loss_end": 1.5636, "start_step": 50, "end_step": 3500,
     "gpu": "17.2 -> 19.4 GB",
     "lr": "lr_lora 1.0e-5 -> 1.0e-7 / lr_proj 5.0e-6 -> 1.0e-7 (cosine)", "mid": []},
]
EVAL_BRIDGE = {
    "root": ("lmms_eval_baize_llava.py hardcoded NUM_IMAGE_TOKENS=196 (ViT-B/16: 224/16=14x14=196); "
             "ViT-L/14 patch14 -> 224/14=16x16=256 patch tokens -> projector/LLM embed dim mismatch -> 8-GPU eval all crashed."),
    "fix": ("3 places changed to dynamic calc: (1) self.num_image_tokens = 256 if vision_backend in ('armE','armE_r2') else 196; "
            "(2) _expand_image_tokens expands by actual token count; (3) feature buffer allocated by actual shape."),
    "smoke": "ai2d --limit 32 smoke test: [inject] img_mask sum=256 OK (see /tmp/smoke_armE_r2_ai2d.log)",
}
BENCH_ROWS = [
    ("AI2D", 60.65, 60.49, "exact_match"),
    ("RealWorldQA", 45.36, 46.41, "exact_match"),
    ("MMMU (val)", 44.00, 42.67, "mmmu_acc"),
    ("BLINK", 38.88, 39.59, "blink_acc"),
    ("MMStar", 27.17, 27.07, "average"),
    ("MMMU-Pro (std)", 23.12, 22.60, "mmmu_acc"),
    ("InfographicVQA", 16.18, 16.59, "anls"),
    ("ChartQA", 12.16, 12.92, "relaxed_overall"),
    ("CountBench", 10.59, 9.98, "acc"),
    ("DocVQA (val)", 7.35, 7.44, "anls"),
    ("OCRBench", 1.60, 1.60, "ocrbench_acc"),
]
MME_ARME = 718.04
MME_ARMD = 806.45
AVG_ARME = 26.10
AVG_ARMD = 26.12
AVG_DELTA = -0.02
REPRO_CMDS = {
    "train": "setsid bash vision/run_armE_r2_openclip.sh > /tmp/armE_r2_openclip_train.log 2>&1 < /dev/null &",
    "protb": "bash vision/run_armE_r2_protb_eval.sh",
    "bench": "bash vision/mllm_bridge/launch_12benchmarks_armE_r2_offline.sh",
}
TRAIN_OUT = "/nas_train/app.e0031982/datasets/baize-vision/out/armE_r2_20261022_aimv2_openclip_vitl14_224/"
PROTB_JSON = "vision/armE_r2_20261022_protb_vitl14_224_results.json"
BENCH_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armE_r2_20261022/"
TRAIN_LOG = "/tmp/armE_r2_openclip_train.log"
ARME_ARCHIVE = "/nas_train/app.e0031982/datasets/baize-vision/out/armE_20261021_DIVERGED_archive/ (kept, not deleted)"

def milestone_rows():
    rows = ""
    for s, lo, co, pa, lr, its, c1, t in MILESTONES:
        tag = ""
        if s == 3000: tag = " (warmup end)"
        elif s == 45240: tag = " (C1 historical max)"
        elif s == 50000: tag = " (spike)"
        elif s == 63400: tag = " (endpoint)"
        rows += (f"<tr><td style='text-align:left'>{s:,}{tag}</td><td>{lo:.4f}</td><td>{co:.4f}</td>"
                 f"<td>{pa:.4f}</td><td>{lr}</td><td>{its:.2f}</td>"
                 f"<td>{c1:.4f}</td><td>{t:.1f}</td></tr>\n")
    return rows

def protb_rows():
    rows = ""
    for name, lp, sig, knn, seeds in PROTB_ARMS:
        seed_str = " / ".join(f"{x:.3f}" for x in seeds)
        rows += (f"<tr><td style='text-align:left'>{escape(name)}</td><td><b>{lp:.3f}</b></td>"
                 f"<td>\u00b1{sig:.4f}</td><td>{knn:.3f}</td><td class='small'>{seed_str}</td></tr>\n")
    return rows

def bench_rows():
    rows = ""
    for name, ae, ad, metric in BENCH_ROWS:
        d = (ae - ad)
        cls = "ok" if d > 0 else ("bad" if d < 0 else "")
        rows += (f"<tr><td style='text-align:left'>{escape(name)}</td><td>{ae:.2f}</td>"
                 f"<td>{ad:.2f}</td><td class='{cls}'>{d:+.2f}</td>"
                 f"<td class='small'>{metric}</td></tr>\n")
    d_mme = MME_ARME - MME_ARMD
    rows += (f"<tr><td style='text-align:left'>MME <span class='small'>(not in avg)</span></td>"
             f"<td>{MME_ARME:.2f}</td><td>{MME_ARMD:.2f}</td>"
             f"<td class='bad'>{d_mme:+.2f}</td><td class='small'>perception+cognition</td></tr>\n")
    rows += (f"<tr style='font-weight:700;background:#eef4fa'>"
             f"<td style='text-align:left'>avg (excl MME)</td><td>{AVG_ARME:.2f}</td>"
             f"<td>{AVG_ARMD:.2f}</td><td class='bad'>{AVG_DELTA:+.2f}</td>"
             f"<td class='small'>11-bench arithmetic mean</td></tr>\n")
    return rows

def stage_rows():
    rows = ""
    for st in STAGES:
        mid = " - "
        if st["mid"]:
            mid = " \u00b7 ".join(f"s{s}={v:.4f}" for s, v in st["mid"])
        rows += (
            f"<tr><td style='text-align:left'><b>{escape(st['name'])}</b><br><span class='small'>{escape(st['full'])}</span></td>"
            f"<td>{st['steps']:,}</td><td class='small'>{st['start']}\u2192{st['end']}<br>{st['minutes']:.1f} min</td>"
            f"<td>{st['loss_start']:.4f} (s{st['start_step']})<br>\u2192 <b>{st['loss_end']:.4f}</b> (s{st['end_step']})</td>"
            f"<td class='small'>{escape(st['lr'])}</td><td>{escape(st['gpu'])}</td>"
            f"<td class='small'>{escape(mid)}</td></tr>\n")
    return rows

# Build HTML in parts to keep each f-string manageable.

_CSS = """body { font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 1140px; margin: 0 auto; padding: 20px; color: #222; line-height: 1.6; }
h1 { color: #1a3a5c; border-bottom: 3px solid #1a3a5c; padding-bottom: 8px; }
h2 { color: #2a5a8c; margin-top: 30px; border-left: 5px solid #2a5a8c; padding-left: 10px; }
h3 { color: #345; margin-top: 18px; }
table { border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 13px; }
th, td { border: 1px solid #ccc; padding: 5px 8px; text-align: center; }
th { background: #eef4fa; font-weight: 600; }
tr:nth-child(even) { background: #f8fafc; }
td { text-align: right; }
td.l { text-align: left; }
.ok { color: #1a7a1a; font-weight: 600; } .bad { color: #c00; font-weight: 600; } .warn { color: #b80; font-weight: 600; }
.small { font-size: 12px; color: #666; }
code { background: #f0f0f0; padding: 1px 4px; border-radius: 3px; font-size: 12px; }
.kbox { background: #fffbe6; border: 1px solid #e0d090; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
.nbox { background: #f0f6fc; border: 1px solid #b0d0e8; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }
.summary { display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; }
.card { background: #f0f6fc; border: 1px solid #b0d0e8; border-radius: 8px; padding: 10px 16px; min-width: 150px; text-align: center; }
.card .l { font-size: 12px; color: #556; } .card .v { font-size: 22px; font-weight: 700; color: #1a3a5c; }
pre { background: #f5f5f5; border: 1px solid #ddd; border-radius: 5px; padding: 10px; overflow-x: auto; font-size: 12px; }
"""

def build_html():
    H = []
    H.append('<!DOCTYPE html>\n<html lang="zh-CN"><head><meta charset="utf-8">')
    H.append('<meta name="viewport" content="width=device-width, initial-scale=1">')
    H.append('<title>BaiZe ArmE-R2 vision encoder full experiment report (2026-10-22 to 10-24)</title>')
    H.append('<style>' + _CSS + '</style></head><body>')
    H.append('<h1>BaiZe ArmE-R2 \u89c6\u89c9\u7f16\u7801\u5668 \u00b7 \u5b8c\u6574\u5b9e\u9a8c\u62a5\u544a</h1>')
    H.append(f'<p class="small">\u5b9e\u9a8c\u4ee3\u53f7 ArmE-R2 \u00b7 \u65f6\u95f4 {TRAIN_T0} \u2192 {TRAIN_DONE} \u00b7 \u751f\u6210\u4e8e {GEN_TIME} \u00b7 '
             f'\u5355\u6587\u4ef6\u81ea\u5305\u542b (\u65e0\u5916\u94fe CDN / \u65e0 &lt;script&gt;) \u00b7 \u6240\u6709\u6570\u5b57\u6765\u81ea\u843d\u76d8\u4ea7\u7269</p>')
    # disclosure box
    H.append(f'<div class="kbox"><b>\u26a0\ufe0f \u53d8\u91cf\u62ab\u9732 (\u5fc5\u987b\u9010\u5b57\u5bf9\u9f50)</b><br>'
             f'ArmE-R2 = <b>ArmE \u964d LR \u91cd\u8dd1</b>\u3002ArmE(\u539f LR 1e-3) \u4e8e step~{ARME_DIVERGE_STEP:,} \u53d1\u6563 (loss={ARME_DIVERGE_LOSS}, C1~{ARME_DIVERGE_C1})\uff0c'
             f'\u6839\u56e0 = ViT-L/14(304M) \u6bd4 ViT-B/16(86M) \u5927 3.5\u00d7 \u5374\u6cbf\u7528 LR 1e-3\uff0c\u66f4\u65b0\u5e45\u5ea6\u8fc7\u5927 \u2192 spike \u53cd\u590d\u3001C1 \u6062\u590d\u6162\u3002<br>'
             f'<b>ArmE-R2 vs ArmE = \u4ec5\u4e24\u53d8\u91cf</b>\uff1apeak LR 1e-3\u2192<b>5e-4</b> + warmup 2000\u2192<b>3000</b>\uff08\u5854/\u6570\u636e/GBS/steps/loss/mask/wd/seed \u5168\u540c\uff09\u2192 \u5e72\u51c0\u5bf9\u7167\u300c\u964d LR+warmup \u662f\u5426\u6d88\u9664 spike\u300d\u3002<br>'
             f'<b>ArmE-R2 vs ArmD-R2 = \u4e09\u53d8\u91cf</b>\uff1a\u5854(B/16 86.2M \u2192 L/14 304M) + LR(1e-3\u21925e-4) + warmup(2000\u21923000) \u2192 <b>\u62a5\u544a\u4e2d\u4e0d\u5f97\u5355\u5f52\u56e0</b>\u3002<br>'
             f'<b>\u5bb9\u91cf\u6df7\u6742 (\u8fd0\u7ef4\u4ee4\u2464)</b>\uff1aArmE-R2 \u5854(304M) \u6bd4 ArmD-R2(86.2M) \u5927 ~3.5\u00d7\uff0c\u82e5 MLLM \u80dc\u51fa<b>\u4e0d\u5f97\u5355\u72ec\u5f52\u56e0"\u67b6\u6784\u66f4\u597d"</b>\uff0c\u987b\u5e76\u5217\u8bf4\u660e"\u5bb9\u91cf+\u67b6\u6784"\u590d\u5408\u53d8\u91cf\uff1b\u82e5\u6301\u5e73/\u843d\u540e\u5219\u8bf4\u660e"\u5bb9\u91cf\u4e0d\u662f\u74f6\u9888"\u3002<br>'
             f'<b>Stage-2 instruct \u6570\u636e</b>\uff1a\u540c ArmD-R2\uff0c\u7528\u539f\u7248 LLaVA-NeXT-780k quick-start \u5b50\u96c6 (pretrain-*.tar, 738588 \u6837\u672c, \u975e opt47)\u3002</div>')
    # 1. summary
    H.append('<h2>1. \u6458\u8981</h2>')
    H.append('<div class="summary">'
             f'<div class="card"><div class="l">ProtB lp \U0001f3c6 \u5168\u5b9e\u9a8c\u6700\u9ad8</div><div class="v">{PROTB["lp"]:.3f}%</div></div>'
             f'<div class="card"><div class="l">ProtB 5-NN \U0001f3c6</div><div class="v">{PROTB["knn5"]:.3f}%</div></div>'
             f'<div class="card"><div class="l">12 \u96c6 avg(\u9664 MME)</div><div class="v">{AVG_ARME:.2f}%</div></div>'
             f'<div class="card"><div class="l">vs ArmD-R2 ({AVG_ARMD:.2f}%)</div><div class="v">{AVG_DELTA:+.2f}pp</div></div>'
             '</div>')
    H.append('<div class="kbox"><b>\u6458\u8981 (\u22646 \u6761)</b><ol>'
             f'<li><b>ProtB \u5386\u53f2\u6700\u9ad8</b>\uff1aArmE-R2 lp <b>{PROTB["lp"]:.3f}\u00b1{PROTB["lp_sigma"]:.4f}%</b> / 5-NN <b>{PROTB["knn5"]:.3f}%</b>\uff0c\u5168\u5b9e\u9a8c\u6700\u9ad8\u3002vs ArmD-R2 \u0394lp=+{PROTB_DELTA["vs_armd"]["lp"]:.3f}pp / \u03945-NN=+{PROTB_DELTA["vs_armd"]["knn5"]:.3f}pp\uff08\u4e09\u53d8\u91cf\u590d\u5408\uff1a\u5854+LR+warmup\uff0c\u4e0d\u5f97\u5355\u5f52\u56e0\uff09\u3002</li>'
             f'<li><b>12 \u96c6 vs ArmD-R2</b>\uff1aavg(\u9664 MME) <b>{AVG_ARME:.2f}% vs {AVG_ARMD:.2f}% = {AVG_DELTA:+.2f}pp</b>\uff0c6 \u5347 5 \u964d \u5747 \u00b11.5pp \u5185 \u2192 <span class="warn">\u4e0d\u53ef\u5206\u8fa8\uff08\u8fb9\u754c\u503c\uff09</span>\uff0c\u843d\u5728\u9884\u6ce8\u518c 22\u201326.5% \u5e26\u3002</li>'
             f'<li><b>\u5bb9\u91cf \u2260 MLLM \u4e0b\u6e38\u74f6\u9888</b>\uff1a\u89c6\u89c9\u5854\u589e\u5927 3.5\u00d7\uff0886\u2192304M\uff09\uff0cMLLM \u4e0b\u6e38\u5b8c\u5168\u6301\u5e73 \u2192 \u5728 224px \u5355\u5757 + \u5f53\u524d MLLM \u67b6\u6784\u4e0b\uff0c\u5bb9\u91cf\u4e0d\u662f MLLM \u4e0b\u6e38\u74f6\u9888\u3002</li>'
             f'<li><b>ProtB\u2192MLLM \u4f20\u9012\u6027\u518d\u6b21\u8bc1\u4f2a\uff08\u6700\u5f3a\u70c8\u4e00\u4f8b\uff09</b>\uff1a\u7f16\u7801\u5668 +{PROTB_DELTA["vs_armd"]["lp"]:.1f}pp \u7684 ProtB \u4f18\u52bf\u5b8c\u5168\u672a\u8f6c\u5316\u4e3a MLLM \u4e0b\u6e38\u4f18\u52bf\u3002</li>'
             f'<li><b>\u964d LR \u6210\u529f\u6d88\u9664\u53d1\u6563</b>\uff1aArmE(LR 1e-3) step {ARME_DIVERGE_STEP:,} \u6c38\u4e45\u53d1\u6563 (C1~{ARME_DIVERGE_C1}, {ARME_C1_LOW_COUNT} \u6b65 C1&lt;0.01)\uff1bArmE-R2(LR 5e-4) \u5168\u7a0b\u7a33\u5b9a\uff0c0 \u6b65 C1&lt;0.01\uff08warmup \u540e\uff09\uff0cC1 \u5386\u53f2\u6700\u9ad8 {SPIKE_C1_MAX}@s{SPIKE_C1_MAX_STEP}\u3002</li>'
             f'<li><b>eval bridge \u4fee\u590d</b>\uff1aViT-L/14 \u4ea7\u51fa 256 patch tokens\uff08vs B/16 \u7684 196\uff09\uff0c\u539f\u786c\u7f16\u7801\u5bfc\u81f4 8 \u5361 eval \u5168\u5d29\uff0c\u5df2\u4fee 3 \u5904\u52a8\u6001\u8ba1\u7b97\uff0c\u5192\u70df <code>[inject] img_mask sum=256</code> \u2705\u3002</li></ol></div>')
    # 2. config
    H.append('<h2>2. \u914d\u7f6e\u4e0e\u53e3\u5f84</h2>')
    H.append('<div class="nbox"><b>ArmE-R2 vs ArmD-R2 = \u4e09\u53d8\u91cf\uff08\u4e0d\u5f97\u5355\u5f52\u56e0\uff09</b>'
             '<table>'
             '<tr><th>\u9879</th><th>ArmD-R2 (\u57fa\u7ebf)</th><th>ArmE-R2 (\u672c\u8f6e)</th><th>\u53d8\u91cf</th></tr>'
             '<tr><td class="l">\u89c6\u89c9\u5854</td><td>open_clip ViT-B/16 224 (86.2M visual / 149.6M total)</td><td><b>open_clip ViT-L/14 224 (304.0M visual / 427.6M total)</b></td><td class="ok">\u2705 \u2460</td></tr>'
             '<tr><td class="l">peak LR / min_lr</td><td>1e-3 / 1e-5</td><td><b>5e-4</b> / 1e-5</td><td class="ok">\u2705 \u2461</td></tr>'
             '<tr><td class="l">warmup</td><td>2000</td><td><b>3000</b></td><td class="ok">\u2705 \u2462</td></tr>'
             '<tr><td class="l">\u521d\u59cb\u5316</td><td>pretrained=None (\u968f\u673a)</td><td>\u540c (\u968f\u673a)</td><td>\u540c</td></tr>'
             '<tr><td class="l">\u6570\u636e</td><td colspan="2">data_snapshot_20261019_armD.txt \u00b7 6 \u6e90 \u00b7 14,589 shards \u00b7 173,124,248 \u5bf9</td><td>\u540c</td></tr>'
             '<tr><td class="l">steps / epoch</td><td colspan="2">63,400 / 3 epoch</td><td>\u540c</td></tr>'
             '<tr><td class="l">GBS</td><td colspan="2">8,192 (MBS 256 \u00d7 8 GPU \u00d7 accum 4)</td><td>\u540c</td></tr>'
             '<tr><td class="l">loss</td><td colspan="2">1.0\u00d7InfoNCE + 1.0\u00d7masked-patch-MSE, mask_ratio 0.6</td><td>\u540c</td></tr>'
             '<tr><td class="l">wd / betas / clip / seed</td><td colspan="2">0.01 / (0.9,0.98) / 1.0 / 1234</td><td>\u540c</td></tr>'
             '<tr><td class="l">\u6587\u672c\u5854</td><td colspan="2">\u51bb\u7ed3 CLIP-ViT-L/14-336 (768-d)</td><td>\u540c</td></tr>'
             '<tr><td class="l">\u8f93\u51fa\u76ee\u5f55</td><td>armD_r2_20261020_*</td><td><b>armE_r2_20261022_aimv2_openclip_vitl14_224</b></td><td>\u65b0</td></tr>'
             '</table>'
             '<p class="small"><b>\u5bf9\u7167\u8fb9\u754c</b>\uff1aArmE-R2 vs ArmC = \u56db\u53d8\u91cf\uff08\u5854 B\u2192L + LR + warmup + ArmC\u2192ArmD \u6570\u636e\u8f74\uff09\uff1bvs ArmB = \u56db\u53d8\u91cf\uff08\u5854 + LR + warmup + \u6570\u636e/epoch\uff09\u3002\u7f16\u7801\u5668\u7eaf\u5bf9\u7167\u770b \u2461ProtB\uff08\u540c Protocol B / \u540c IN-1k\uff09\u3002<br>'
             '<b>MBS \u975e\u53d8\u91cf</b>\uff1a512\u2192256 \u662f ViT-L/14 \u663e\u5b58\u7ea6\u675f\u7684\u5f3a\u5236\u56de\u9000\uff08GBS=8192 + steps=63400 \u4fdd\u6301\uff0c\u975e\u6d88\u878d\u53d8\u91cf\uff09\uff0c\u4e14\u5e26\u6765 per-microbatch \u5bf9\u6bd4 batch 4096\u21922048 \u7684\u4e0d\u53ef\u907f\u6df7\u6742\u3002<br>'
             '<b>config.json \u590d\u6838</b>\uff1alr=0.0005 / min_lr=1e-05 / warmup=3000 / wd=0.01 / seed=1234 / mask_ratio=0.6 / contrast_weight=1.0 / patch_loss_weight=1.0 / n_visual=303,966,208(304M) / n_total=427,616,513 / n_patches=256 / patch_size=14 / image_size=224 / model_name=ViT-L-14 \u2014\u2014 \u5168\u5bf9\u3002</p></div>')
    # 3. training
    H.append('<h2>3. \u2460 \u8bad\u7ec3\uff08\u7f16\u7801\u5668\u9884\u8bad\u7ec3\uff09</h2>')
    H.append(f'<p class="small">\u6570\u636e\u6765\u6e90\uff1a<code>{TRAIN_LOG}</code>\uff08538 KB, 3,178 \u6761 step \u65e5\u5fd7, \u6b21 20 \u6b65\u4e00\u6761\uff09+ <code>{TRAIN_OUT}config.json</code>\u3002</p>')
    H.append(f'<div class="nbox"><p><b>\u603b\u89c8</b>\uff1aT0 = {TRAIN_T0} \u2192 DONE {TRAIN_DONE}\uff0c\u603b\u8017\u65f6 <b>{TRAIN_HOURS} h</b>\uff08log DONE \u884c\uff1a<code>time={TRAIN_HOURS}h peak={TRAIN_PEAK_GB}GB</code>\uff09\u3002'
             f'\u7a33\u6001\u541e\u5410 <b>{TRAIN_ITS} it/s</b>\uff08ViT-L/14 \u6bd4 B/16 \u524d\u5411\u66f4\u6162\uff0cETA \u7531\u8d77\u6b65 59.6h \u6536\u655b\u5230 34h \u6863\uff09\u3002'
             f'{TRAIN_STEPS:,} \u6b65\u5168\u7a0b <b>0 nan / 0 oom</b>\uff08grep \u539f\u6587\u89c1\u4e0b\uff09\u3002GPU \u663e\u5b58\u5cf0\u503c <b>{TRAIN_PEAK_GB} GB</b>\uff088\u00d7H100 80GB\uff0cMBS 256/accum 4\uff0c\u5cf0\u503c\u51fa\u73b0\u5728\u9996\u6b65\u4e14\u5168\u7a0b\u4e0d\u53d8\uff09\u3002'
             f'\u6700\u7ec8 step {TRAIN_STEPS:,}\uff1a<code>loss=0.1612 contr=0.1570 patch=0.0042 lr=1.00e-05(=min_lr) C1~0.8547</code>\u3002</p></div>')
    H.append('<h3>3.1 \u91cc\u7a0b\u7891\u70b9\uff08loss / contr / patch / lr / it/s / C1 / \u7d2f\u8ba1\u5206\u949f\uff09</h3>')
    H.append('<table><tr><th>step</th><th>loss</th><th>contr</th><th>patch</th><th>lr</th><th>it/s</th><th>C1~</th><th>t (min)</th></tr>' + milestone_rows() + '</table>')
    H.append(f'<p class="small">C1 = \u5bf9\u6bd4\u5bf9\u9f50\u5ea6\u6307\u6807\uff08\u56fe\u6587 InfoNCE \u6536\u655b\u5224\u636e\uff0c\u8d8a\u9ad8\u8d8a\u597d\uff09\uff1bpatch = masked-patch-MSE\uff08\u8d8a\u4f4e\u8d8a\u597d\uff0c\u5168\u7a0b\u5355\u8c03\u4e0b\u964d\uff09\u3002'
             f'warmup 3,000 \u6b65\u5185 lr \u7ebf\u6027\u5347\u5230 5e-4\uff1bstep 3000 \u540e\u8fdb\u5165 cosine \u8870\u51cf\u3002<b>C1 \u5386\u53f2\u6700\u9ad8 = {SPIKE_C1_MAX}@s{SPIKE_C1_MAX_STEP}</b>\uff08\u5168 log \u786e\u8ba4\uff09\u3002</p>')
    H.append('<h3>3.2 spike \u7edf\u8ba1\uff08\u4e0e ArmE \u53d1\u6563\u5bf9\u6bd4\uff09</h3>')
    H.append('<div class="nbox"><p><b>spike \u6027\u8d28</b>\uff1a\u5bf9\u6bd4\u635f\u5931 (contr) \u7684\u5468\u671f\u6027\u8df3\u5347\uff0c<b>patch \u635f\u5931\u5168\u7a0b\u5e73\u7a33\uff08~0.005\u20130.015\uff09</b> \u2192 spike \u7531 InfoNCE \u6279\u6b21\u7edf\u8ba1\u566a\u58f0\u9a71\u52a8\uff08per-microbatch \u5bf9\u6bd4 batch = 2048\uff0c\u56e0 MBS 256 \u663e\u5b58\u56de\u9000\uff0c\u975e 4096\uff09\u3002\u6bcf\u4e2a spike \u540e\u5747<b>\u81ea\u6062\u590d</b>\uff0c\u672a\u6f14\u53d8\u4e3a\u53d1\u6563\u3002</p>'
             '<table><tr><th>\u6307\u6807</th><th>ArmE-R2 (LR 5e-4)</th><th>ArmE (LR 1e-3, \u53d1\u6563)</th></tr>'
             f'<tr><td class="l">contr&gt;0.6 \u7684\u72ec\u7acb spike \u533a\u6bb5\u6570</td><td><b>{SPIKE_N_EPISODES}</b>\uff08\u5168\u90e8\u6062\u590d\uff09</td><td>\u2014\uff08spike \u5347\u7ea7\u4e3a\u53d1\u6563\uff09</td></tr>'
             f'<tr><td class="l">\u6700\u9ad8 loss\uff08step\u226520000\uff09</td><td><b>{SPIKE_PEAK_LOSS}</b> @ s{SPIKE_PEAK_STEP}</td><td>{ARME_DIVERGE_LOSS} @ s{ARME_DIVERGE_STEP}\uff08\u53d1\u6563\u70b9\uff09</td></tr>'
             f'<tr><td class="l">\u8c37\u5e95 loss\uff08\u6700\u4f18\u70b9\uff09</td><td><b>{SPIKE_TROUGH_LOSS}</b> @ s{SPIKE_TROUGH_STEP}</td><td>\u2014</td></tr>'
             f'<tr><td class="l">\u6062\u590d\u6b65\u6570\uff08\u5178\u578b spike\uff09</td><td>~{SPIKE_RECOVERY_STEPS} \u6b65\uff08s50040 loss 0.9026 \u2192 s50800 loss 0.1279\uff09</td><td class="bad">\u6c38\u4e0d\u6062\u590d</td></tr>'
             f'<tr><td class="l">C1 \u5386\u53f2\u6700\u9ad8</td><td><b>{SPIKE_C1_MAX}</b> @ s{SPIKE_C1_MAX_STEP}</td><td>~0.37\uff08s29000 \u524d\uff09\u2192 \u5d29\u5230 {ARME_DIVERGE_C1}</td></tr>'
             f'<tr><td class="l">warmup \u540e C1&lt;0.01 \u6b65\u6570</td><td><b>{SPIKE_C1_LOW_AFTER_WARMUP}</b>\uff08\u65e0\u53d1\u6563\uff09</td><td class="bad">{ARME_C1_LOW_COUNT}\uff08\u6c38\u4e45\u53d1\u6563\uff09</td></tr>'
             f'<tr><td class="l">\u540c\u4e00\u70b9 (s29000) \u5bf9\u6bd4</td><td>loss={ARME_R2_SAMEPOINT_LOSS}, C1~{ARME_R2_SAMEPOINT_C1}\uff08\u4ece\u81ea\u8eab spike \u6062\u590d\u4e2d\uff09</td><td class="bad">loss=5.8721, C1~0.0049\uff08\u5d29\u6e83\u4e2d\uff09</td></tr>'
             '</table>'
             '<p class="small"><b>\u7ed3\u8bba</b>\uff1a\u964d LR(1e-3\u21925e-4)+warmup(2000\u21923000) <b>\u672a\u6d88\u9664 spike \u7684\u53d1\u751f</b>\uff08contr \u6279\u6b21\u566a\u58f0\u5ba2\u89c2\u5b58\u5728\uff09\uff0c\u4f46<b>\u628a spike \u4ece"\u4e0d\u53ef\u9006\u53d1\u6563"\u964d\u7ea7\u4e3a"\u53ef\u81ea\u6062\u590d\u7684\u77ed\u6682\u8df3\u5347"</b>\u3002ArmE \u5728 s29200\u201329400 \u7684 spike \u5347\u7ea7\u4e3a loss 8.1 / C1 0.0007 \u4e14\u6c38\u4e45\u4e0d\u5f52\uff1bArmE-R2 \u540c\u671f spike \u4ecd\u5728 0.5\u20131.4 \u91cf\u7ea7\u4e14\u6570\u767e\u6b65\u5185\u6062\u590d\u3002\u8fd9\u662f\u4e24\u53d8\u91cf\u5e72\u51c0\u5bf9\u7167\u7684\u6838\u5fc3\u7ed3\u8bba\u3002</p></div>')
    H.append('<h3>3.3 ckpt \u843d\u76d8\u6e05\u5355</h3>')
    H.append('<p class="small">save_every=10000, keep_ckpts=2\uff08\u6eda\u52a8\u5220\u9664\u65e7 ckpt\uff09\u3002log \u539f\u6587\uff1a<code>saved ckpt step=10000/20000/30000/40000/50000/60000/63400</code>\u3002</p>')
    H.append('<table><tr><th>\u843d\u76d8\u6587\u4ef6</th></tr>' + ''.join(f'<tr><td class="l"><code>{escape(c)}</code></td></tr>' for c in CKPT_ON_DISK) + '</table>')
    H.append(f'<p class="small">\u5df2\u6eda\u52a8\u5220\u9664\uff1acheckpoint_10000/20000/30000/40000/50000.pt\uff08keep-2 \u7b56\u7565\uff09\u3002ArmE \u53d1\u6563\u8bc1\u636e\u7559\u6863\uff1a<code>{escape(ARME_ARCHIVE)}</code>\u3002</p>')
    H.append('<h3>3.4 0 nan / 0 oom \u7684 grep \u539f\u6587</h3>')
    H.append(f'<pre>{escape(NAN_OOM_GREP)}\n$ grep -inE \'nan|out of memory|oom\' /tmp/armE_r2_openclip_train.log | grep -v \'OOM-forced\'\n(\u65e0\u8f93\u51fa \u2192 0 \u547d\u4e2d)\n$ grep -cE \'loss=\' /tmp/armE_r2_openclip_train.log\n3178</pre>')
    H.append('<p class="small">\u552f\u4e00\u542b "OOM" \u7684\u884c\u662f\u811a\u672c\u542f\u52a8\u65f6\u7684\u914d\u7f6e\u6ce8\u8bb0 <code>[ArmE-R2] UNAVOIDABLE confound ... (MBS 512-&gt;256, OOM-forced)</code>\uff0c\u975e\u8fd0\u884c\u65f6\u9519\u8bef\u3002\u7ec8\u6001\u884c\uff1a<code>[ArmE-R2] DONE step=63400 loss=0.1612 contr=0.1570 patch=0.0042 time=37.07h peak=77.5GB</code>\uff0cexit 0\u3002</p>')
    # 4. ProtB
    H.append('<h2>4. \u2461 ProtB\uff08\u7ebf\u6027\u63a2\u9488 / \u8fd1\u90bb\uff09\u8bc4\u6d4b</h2>')
    H.append(f'<p class="small">\u6570\u636e\u6765\u6e90\uff1a<code>{PROTB_JSON}</code>\u3002\u534f\u8bae = Protocol B\uff08SGD+momentum 0.9+cosine, mini-batch 1024, 90 epochs, IN-1k full train 1.28M / \u5b98\u65b9 val 50k, 3 seeds 0/1/2, feature=projected, ckpt=open_clip_state_dict.pt\uff09\u3002</p>')
    H.append(f'<div class="summary"><div class="card"><div class="l">lp mean</div><div class="v">{PROTB["lp"]:.3f}%</div></div>'
             f'<div class="card"><div class="l">lp \u03c3</div><div class="v">\u00b1{PROTB["lp_sigma"]:.4f}</div></div>'
             f'<div class="card"><div class="l">5-NN</div><div class="v">{PROTB["knn5"]:.3f}%</div></div></div>')
    H.append('<table><tr><th>\u81c2</th><th>lp (%)</th><th>lp \u03c3</th><th>5-NN (%)</th><th>\u9010 seed (lp)</th></tr>' + protb_rows() + '</table>')
    H.append('<table><tr><th>\u0394 vs</th><th>\u0394lp (pp)</th><th>\u03945-NN (pp)</th></tr>'
             f'<tr><td class="l">ArmD-R2 (\u4e3b\u5bf9\u7167)</td><td class="ok">+{PROTB_DELTA["vs_armd"]["lp"]:.3f}</td><td class="ok">+{PROTB_DELTA["vs_armd"]["knn5"]:.3f}</td></tr>'
             f'<tr><td class="l">ArmC</td><td class="ok">+{PROTB_DELTA["vs_armc"]["lp"]:.3f}</td><td class="ok">+{PROTB_DELTA["vs_armc"]["knn5"]:.3f}</td></tr>'
             f'<tr><td class="l">ArmB</td><td class="ok">+{PROTB_DELTA["vs_armb"]["lp"]:.3f}</td><td class="ok">+{PROTB_DELTA["vs_armb"]["knn5"]:.3f}</td></tr></table>')
    H.append(f'<p class="small"><b>\U0001f3c6 \u5168\u5b9e\u9a8c\u5386\u53f2\u6700\u9ad8</b>\uff1aArmE-R2 \u5728 lp \u4e0e 5-NN \u4e0a\u5747\u4e3a\u5168\u5b9e\u9a8c\u6700\u9ad8\u3002\u26a0\ufe0f <b>\u4e09\u53d8\u91cf + \u5bb9\u91cf\u6df7\u6742</b>\uff1a\u0394lp=+{PROTB_DELTA["vs_armd"]["lp"]:.3f}pp / \u03945-NN=+{PROTB_DELTA["vs_armd"]["knn5"]:.3f}pp \u662f \u5854(B\u2192L, 86\u2192304M) + LR(1e-3\u21925e-4) + warmup(2000\u21923000) \u4e09\u9879\u5171\u540c\u4f5c\u7528\uff0c<b>\u4e0d\u5f97\u5f52\u56e0\u5355\u4e00\u53d8\u91cf</b>\u3002\u5bb9\u91cf\u589e\u5927 3.5\u00d7 \u662f\u4e3b\u8981\u6df7\u6742\u56e0\u5b50\u3002\u7f16\u7801\u5668\u8d28\u91cf\u6838\u5fc3\u7ed3\u8bba\u5df2 secured\u3002</p>')
    # 5. MLLM three-stage
    H.append('<h2>5. \u2462 MLLM \u4e09\u9636\u6bb5\u5bf9\u9f50</h2>')
    H.append('<p class="small">\u6570\u636e\u6765\u6e90\uff1a<code>/tmp/armE_r2_stage1.log</code> + <code>/tmp/armE_r2_stage15.log</code> + <code>/tmp/armE_r2_stage2.log</code> + <code>/tmp/armE_r2_full_chain.log</code>\u3002\u811a\u672c\uff1a<code>vision/mllm_bridge/stage{1,15,2}_train_armE_r2.py</code>\uff0cchain = <code>vision/run_armE_r2_full_chain.sh</code>\u3002\u89c6\u89c9\u5854 ckpt \u6362\u6210 ArmE-R2\uff08projector 1024\u21922560\uff09\u3002</p>')
    H.append('<table><tr><th>\u9636\u6bb5</th><th>\u6b65\u6570</th><th>\u65f6\u95f4</th><th>loss (\u8d77\u2192\u7ec8)</th><th>lr \u8c03\u5ea6</th><th>GPU</th><th>\u4e2d\u95f4\u70b9</th></tr>' + stage_rows() + '</table>')
    H.append('<p class="small">\u4e09\u9636\u6bb5\u4e32\u884c\uff08PHASE 3: 07:23:38 \u8d77\uff09\u3002Stage-1.5 LoRA r=64\uff0cprojector 9.18M \u53c2\u6570\uff1bStage-2 \u7528\u539f\u7248 LLaVA-NeXT-780k quick-start \u5b50\u96c6\uff08pretrain-*.tar, 738588 \u6837\u672c, \u975e opt47\uff0c\u540c ArmD-R2\uff09\u3002Stage-2 loss \u4ece 5.24 \u964d\u5230 1.56\uff0c\u5065\u5eb7\u6536\u655b\u3002LLM = Qwen3-4B-Instruct\u3002</p>')
    H.append('<h3>5.1 \U0001f527 eval bridge bug\uff08\u4fee\u590d\uff09</h3>')
    H.append('<div class="nbox">'
             f'<p><b>\u6839\u56e0</b>\uff1a{escape(EVAL_BRIDGE["root"])}</p>'
             f'<p><b>\u73b0\u8c61</b>\uff1a12-\u96c6\u8bc4\u6d4b\u9996\u6b21\u8fd0\u884c\u65f6 8 \u5361\u5168\u90e8\u5d29\u6e83\uff08embedding \u7ef4\u5ea6\u4e0d\u5339\u914d\uff0c256\u2260196\uff09\u3002</p>'
             f'<p><b>\u4fee\u6cd5\uff083 \u5904\u52a8\u6001\u8ba1\u7b97\uff09</b>\uff1a{escape(EVAL_BRIDGE["fix"])}</p>'
             f'<p><b>\u5192\u70df\u9a8c\u8bc1</b>\uff1a{escape(EVAL_BRIDGE["smoke"])}</p>'
             '<pre>[inject] inputs_embeds shape=torch.Size([32, 327, 2560]), img_mask sum=256\n[inject] img_feat stats: min=-3.828, max=4.188, mean=0.013</pre>'
             '<p class="small">\u4fee\u590d\u6587\u4ef6\uff1a<code>vision/mllm_bridge/lmms_eval_baize_llava.py</code>\u3002\u6b64 bug \u4e3a ViT-L/14\uff08patch14, 256 tokens\uff09\u4e0e ViT-B/16\uff08patch16, 196 tokens\uff09\u7684 patch \u6570\u5dee\u5f02\u6240\u81f4\uff0c\u5c5e\u672c\u6b21 ArmE-R2 \u7279\u6709\u5de5\u7a0b\u95ee\u9898\uff08ArmB/C/D-R2 \u7528 B/16\uff0c\u65e0\u6b64\u95ee\u9898\uff09\u3002</p></div>')
    # 6. 12 benchmarks
    H.append('<h2>6. \u2463 12 \u96c6\u9010\u96c6\u8bc4\u6d4b</h2>')
    H.append(f'<p class="small">\u6570\u636e\u6765\u6e90\uff1a<code>{escape(BENCH_DIR)}consolidated_12benchmarks.json</code>\u3002Stage-2 step3500 checkpoint\uff0c\u6bcf\u5361\u4e00\u4e2a benchmark\uff08batch_size=32, 8 \u5361\u5e76\u884c, \u65e0 limit, \u5168\u91cf, ~10 min, 12/12 exit 0\uff09\u3002</p>')
    H.append('<table><tr><th>\u96c6</th><th>ArmE-R2 (%)</th><th>ArmD-R2 (%)</th><th>\u0394 (pp)</th><th>\u6307\u6807</th></tr>' + bench_rows() + '</table>')
    H.append(f'<p class="small"><b>\u88c1\u5b9a</b>\uff1aArmE-R2 avg(\u9664 MME) = <b>{AVG_ARME:.2f}%</b>\uff0cvs ArmD-R2 = <b>{AVG_DELTA:+.2f}pp</b>\uff086 \u5347 5 \u964d, \u5747 \u00b11.5pp \u5185\uff09\uff0c\u843d\u5728\u9884\u6ce8\u518c 22\u201326.5% \u300c\u4e0d\u53ef\u5206\u8fa8\u300d\u5e26\u3002DocVQA/ChartQA/OCRBench vs ArmD-R2 \u65e0\u4efb\u4e00 +10pp\uff08\u22120.09/\u22120.76/+0.00\uff09\u21d2 \u4e0d\u89e6\u53d1\u300c&gt;24% \u4e14\u5355\u96c6 +10pp \u6210\u529f\u300d\u5206\u652f\u3002\u6cbf\u7528 ArmB/ArmC/ArmD-R2 \u9884\u6ce8\u518c\u5224\u636e\uff0c<b>\u88c1\u5b9a = \u4e0d\u53ef\u5206\u8fa8\uff08\u8fb9\u754c\u503c\uff09</b>\u3002<br>'
             f'MME \u4e3a\u611f\u77e5\u5206 + \u8ba4\u77e5\u5206\uff08\u6ee1\u5206 2800\uff09\uff0c\u4e0d\u8ba1\u5165\u51c6\u786e\u7387\u5e73\u5747\uff1bArmE-R2 MME {MME_ARME:.2f} \u4f4e\u4e8e ArmD-R2 {MME_ARMD:.2f}\uff08\u0394{MME_ARME-MME_ARMD:+.1f}\uff09\uff0c\u4f46 MME \u4e24\u81c2\u5747\u5904\u4f4e\u4f4d\u3001\u4e14\u975e\u9884\u6ce8\u518c\u4e3b\u6307\u6807\u3002<br>'
             '\u26a0\ufe0f ArmE-R2 \u4e0e ArmD-R2 \u7684 Stage-2 instruct \u6570\u636e\u540c\u6e90\uff08\u539f\u7248 quick-start\uff09\uff0c\u6545 \u2463\u0394 \u4e0d\u542b Stage-2 \u6570\u636e\u6df7\u6742\uff0c\u4f46\u542b\u300c\u5854+LR+warmup\u300d\u4e09\u53d8\u91cf\u6df7\u6742\u3002</p>')
    # 7. conclusion + repro
    H.append('<h2>7. \u7ed3\u8bba\u4e0e\u5c40\u9650 + \u590d\u73b0\u547d\u4ee4</h2>')
    H.append(f'<div class="kbox">'
             f'<p><b>\u2460 \u7f16\u7801\u5668\uff08\u6700\u53ef\u9760\uff0cProtB\uff0c\U0001f3c6 \u5386\u53f2\u6700\u9ad8\uff09</b>\uff1alp {PROTB["lp"]:.3f}% / 5-NN {PROTB["knn5"]:.3f}%\uff0c\u5168\u5b9e\u9a8c\u6700\u9ad8\u3002vs ArmD-R2 \u0394lp=+{PROTB_DELTA["vs_armd"]["lp"]:.3f}pp / \u03945-NN=+{PROTB_DELTA["vs_armd"]["knn5"]:.3f}pp\u3002\u26a0\ufe0f \u4e09\u53d8\u91cf(\u5854+LR+warmup)+\u5bb9\u91cf\u6df7\u6742\uff0c\u4e0d\u5f97\u5f52\u56e0\u5355\u4e00\u53d8\u91cf\u3002<b>\u7f16\u7801\u5668\u8d28\u91cf\u6838\u5fc3\u7ed3\u8bba\u5df2 secured\u3002</b></p>'
             f'<p><b>\u2461 MLLM \u4e0b\u6e38\uff08\u4e0d\u53ef\u5206\u8fa8\uff09</b>\uff1a12 \u96c6 avg {AVG_ARME:.2f}%\uff0cvs ArmD-R2 {AVG_DELTA:+.2f}pp / vs ArmC +0.32pp / vs ArmB \u22120.00pp\u3002\u89c6\u89c9\u5854\u589e\u5927 3.5\u00d7\uff0cMLLM \u4e0b\u6e38\u5b8c\u5168\u6301\u5e73 \u2192 <b>\u5bb9\u91cf\u4e0d\u662f MLLM \u4e0b\u6e38\u74f6\u9888</b>\uff08\u5728 224px \u5355\u5757 + \u5f53\u524d MLLM \u67b6\u6784\u4e0b\uff09\u3002</p>'
             f'<p><b>\u2462 ProtB\u2192MLLM \u4f20\u9012\u6027\u518d\u6b21\u8bc1\u4f2a\uff08\u6700\u5f3a\u70c8\u4e00\u4f8b\uff09</b>\uff1a\u7f16\u7801\u5668 +{PROTB_DELTA["vs_armd"]["lp"]:.1f}pp \u7684 ProtB \u4f18\u52bf\u5b8c\u5168\u672a\u8f6c\u5316\u4e3a MLLM \u4e0b\u6e38\u4f18\u52bf\u3002\u8fd9\u662f\u6240\u6709\u5b9e\u9a8c\u4e2d ProtB \u5dee\u8ddd\u6700\u5927\u800c MLLM \u6301\u5e73\u6700\u660e\u786e\u7684\u4e00\u4f8b\u3002</p>'
             f'<p><b>\u2463 \u964d LR \u6548\u679c\uff08ArmE-R2 vs ArmE\uff0c\u4e24\u53d8\u91cf\u5e72\u51c0\u5bf9\u7167\uff09</b>\uff1aArmE(LR 1e-3) s29400 \u6c38\u4e45\u53d1\u6563(C1~{ARME_DIVERGE_C1})\uff1bArmE-R2(LR 5e-4) \u5168\u7a0b\u7a33\u5b9a\uff0c0 \u6b65 C1&lt;0.01\uff08warmup \u540e\uff09\uff0cC1 \u6700\u9ad8 {SPIKE_C1_MAX} \u2192 <b>\u964d LR+warmup \u628a spike \u4ece"\u4e0d\u53ef\u9006\u53d1\u6563"\u964d\u7ea7\u4e3a"\u53ef\u81ea\u6062\u590d\u8df3\u5347"</b>\u3002</p>'
             '<p><b>\u2464 \u8bda\u5b9e\u6761\u6b3e</b>\uff1a\u5185\u90e8 ProtB/MLLM \u53e3\u5f84\uff0c\u975e\u5b98\u65b9\u699c\uff1b\u5355 backbone/\u5355\u9884\u7b97\u70b9\uff1bMLLM \u4e09\u9636\u6bb5\u5355 seed\uff1b224px \u5355\u5757\uff08\u65e0 anyres\uff09\uff0c\u7ec6\u7c92\u5ea6\u4efb\u52a1\u5929\u7136\u504f\u4f4e\uff1bStage-2 \u6570\u636e\u4e3a\u539f\u7248 quick-start\uff08\u540c ArmD-R2\uff09\uff1bMBS 512\u2192256 \u662f\u663e\u5b58\u5f3a\u5236\u56de\u9000\u975e\u6d88\u878d\u53d8\u91cf\u3002</p></div>')
    H.append('<h3>7.1 \u590d\u73b0\u547d\u4ee4\uff08\u8bad\u7ec3 / ProtB / 12 \u96c6\uff09</h3>')
    H.append(f'<pre># \u2460 \u7f16\u7801\u5668\u8bad\u7ec3 (63,400 \u6b65, ~37h, 8\u00d7H100)\n{escape(REPRO_CMDS["train"])}\n\n# \u2461 Protocol B \u7ebf\u6027\u63a2\u9488\u8bc4\u6d4b (3 seeds)\n{escape(REPRO_CMDS["protb"])}\n\n# \u2463 12 \u96c6 lmms-eval (8 \u5361\u5e76\u884c, Stage-2 step3500)\n{escape(REPRO_CMDS["bench"])}</pre>')
    H.append('<h3>7.2 \u6587\u4ef6\u8def\u5f84</h3>')
    H.append('<table><tr><th>\u4ea7\u7269</th><th>\u8def\u5f84</th></tr>'
             f'<tr><td class="l">\u8bad\u7ec3\u811a\u672c</td><td class="l"><code>vision/run_armE_r2_openclip.sh</code> + <code>vision/armE_r2_aimv2_openclip_vitl14.py</code></td></tr>'
             f'<tr><td class="l">\u8bad\u7ec3\u8f93\u51fa</td><td class="l"><code>{escape(TRAIN_OUT)}</code></td></tr>'
             f'<tr><td class="l">open_clip \u6743\u91cd</td><td class="l"><code>.../open_clip_state_dict.pt</code> (1.59 GB)</td></tr>'
             f'<tr><td class="l">\u8bad\u7ec3\u65e5\u5fd7</td><td class="l"><code>{TRAIN_LOG}</code></td></tr>'
             f'<tr><td class="l">ArmE \u53d1\u6563\u8bc1\u636e</td><td class="l"><code>{escape(ARME_ARCHIVE)}</code></td></tr>'
             f'<tr><td class="l">ProtB \u7ed3\u679c</td><td class="l"><code>{PROTB_JSON}</code></td></tr>'
             '<tr><td class="l">MLLM chain</td><td class="l"><code>vision/run_armE_r2_full_chain.sh</code> + <code>vision/mllm_bridge/stage{1,15,2}_train_armE_r2.py</code></td></tr>'
             '<tr><td class="l">eval bridge (\u4fee\u590d)</td><td class="l"><code>vision/mllm_bridge/lmms_eval_baize_llava.py</code>\uff083 \u5904\u52a8\u6001 num_image_tokens\uff09</td></tr>'
             f'<tr><td class="l">12 \u96c6\u539f\u59cb\u7ed3\u679c</td><td class="l"><code>{escape(BENCH_DIR)}eval_*.json</code></td></tr>'
             f'<tr><td class="l">12 \u96c6\u5408\u5e76</td><td class="l"><code>{escape(BENCH_DIR)}consolidated_12benchmarks.json</code></td></tr>'
             f'<tr><td class="l">\u672c\u62a5\u544a</td><td class="l"><code>{escape(OUT_PATH)}</code></td></tr>'
             '<tr><td class="l">\u5b9e\u9a8c\u8bb0\u5f55</td><td class="l"><code>EXPERIMENTS_VISION.md \u00a715</code></td></tr></table>')
    H.append(f'<hr><p class="small">\u672c\u62a5\u544a\u7531 <code>vision/generate_armE_r2_full_report.py</code> \u751f\u6210 \u00b7 \u6240\u6709\u6570\u5b57\u6765\u81ea\u843d\u76d8\u4ea7\u7269\uff08\u8bad\u7ec3\u65e5\u5fd7 / ProtB json / 12\u96c6 consolidated json / \u4e09\u9636\u6bb5\u65e5\u5fd7 / config.json\uff09\uff0c\u672a\u505a\u5916\u63a8\u6216\u81c6\u9020\u3002\u751f\u6210\u65f6\u95f4 {GEN_TIME}\u3002<br>'
             '\u65e7\u7248\uff0817 KB, \u4ec5 6 \u8282, \u7f3a\u2460\u8bad\u7ec3\u4e0e\u2462MLLM\u4e09\u9636\u6bb5\uff09\uff1a<code>reports/report_vision_armE_r2_20261022_mllm_stage4_zh.html</code>\uff08\u4fdd\u7559\uff0c\u6807\u6ce8"\u65e7\u7248"\uff09\u3002</p>')
    H.append('</body></html>')
    return "\n".join(H)

def main():
    os.makedirs(REPORTS_DIR, exist_ok=True)
    html = build_html()
    with open(OUT_PATH, "w") as f:
        f.write(html)
    size = os.path.getsize(OUT_PATH)
    print(f"OK report generated: {OUT_PATH}")
    print(f"   size: {size:,} B ({size/1024:.1f} KB)")
    for tag in ("html", "head", "body", "table"):
        o, c = html.count(f"<{tag}"), html.count(f"</{tag}>")
        flag = "OK" if o == c else "WARN unbalanced"
        print(f"   <{tag}>: {o} open / {c} close  {flag}")
    print(f"   has <script>: {'YES' if '<script' in html else 'NO OK'}")
    print(f"   has external http(s) CDN: {'YES' if 'https://' in html or 'http://' in html else 'NO OK'}")

if __name__ == "__main__":
    main()
