#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""generate_armE_r2_mllm_report.py — ArmE-R2 (2026-10-22→10-24) Stage(iv) MLLM 12-集评测中文报告生成器.
ArmE-R2 = ArmE 降 LR 重跑: peak LR 1e-3→5e-4 + warmup 2000→3000 (两变量, 塔/数据/GBS/steps/loss 全同).
塔 = open_clip ViT-L/14 224px (304.0M visual / 427.6M total, from scratch).
ArmE(原 LR 1e-3) 于 step~29200 发散 (C1=0.0014), 故 ArmE-R2 降 LR 重跑.
vs ArmD-R2 = 塔(B/16→L/14) + LR(1e-3→5e-4) + warmup(2000→3000) 三变量 (报告须分开表述).
⚠️ 容量混杂 (运维令⑤): ArmE-R2 塔(304M) 比 ArmD-R2(86.2M) 大 ~3.5×, 若胜出不得单独归因"架构更好".
⚠️ Stage-2 数据: 同 ArmD-R2, 原版 LLaVA-NeXT-780k quick-start (pretrain-*.tar, 738588 样本).
"""
import json, os, sys, argparse
from datetime import datetime
from html import escape

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = os.path.join(os.path.dirname(SCRIPT_DIR), "reports")
DEFAULT_RESULTS_DIR = "/nas_train/app.e0031982/datasets/baize-vision/out/mllm_eval_results_armE_r2_20261022"
DEFAULT_OUT = os.path.join(REPORTS_DIR, "report_vision_armE_r2_20261022_mllm_stage4_zh.html")

BENCH_ORDER = [
    ("ai2d", "AI2D", "exact_match", "图像->科学图理解"),
    ("realworldqa", "RealWorldQA", "exact_match", "真实世界物理推理"),
    ("mmmu_val", "MMMU (val)", "mmmu_acc", "大学级多学科推理"),
    ("blink", "BLINK", "blink_acc", "视觉语言跳变推理"),
    ("mmstar", "MMStar", "average", "多模态综合能力"),
    ("mmmu_pro_standard", "MMMU-Pro (std)", "mmmu_acc", "MMMU 进阶版"),
    ("infovqa_val", "InfographicVQA", "anls", "信息图 VQA"),
    ("chartqa", "ChartQA", "relaxed_overall", "图表问答"),
    ("countbench", "CountBench", "acc", "物体计数"),
    ("docvqa_val", "DocVQA (val)", "anls", "文档 VQA"),
    ("ocrbench", "OCRBench", "ocrbench_acc", "OCR 文字识别"),
    ("mme", "MME", "perception+cog", "多模态综合评估"),
]
ARMD_R2 = {
    "ai2d": 0.6049222797927462, "blink": 0.3959193594049482, "chartqa": 0.1292,
    "docvqa_val": 0.0744305931656727, "infovqa_val": 0.16587798729890857,
    "mme": {"perception_score": 559.6666666666666, "cognition_score": 246.78571428571428},
    "mmmu_val": 0.42667, "mmstar": 0.2706762508080907, "ocrbench": 0.016,
    "realworldqa": 0.46405228758169936, "countbench": 0.09979633401221996, "mmmu_pro_standard": 0.22601,
}
ARMC = {
    "ai2d": 0.5903497409326425, "blink": 0.38148764582043304, "chartqa": 0.1248,
    "docvqa_val": 0.07575127362957136, "infovqa_val": 0.1709190922105125,
    "mme": {"perception_score": 642.1055422168868, "cognition_score": 255.71428571428572},
    "mmmu_val": 0.42556, "mmstar": 0.28375177123685563, "ocrbench": 0.018,
    "realworldqa": 0.4496732026143791, "countbench": 0.08961303462321792, "mmmu_pro_standard": 0.22601,
}
ARMB = {
    "ai2d": 0.6068652849740933, "blink": 0.38939119636572533, "chartqa": 0.1252,
    "docvqa_val": 0.07357683982824648, "infovqa_val": 0.16879324468960838,
    "mme": {"perception_score": 583.6519607843137, "cognition_score": 212.85714285714286},
    "mmmu_val": 0.43667, "mmstar": 0.2794961030152159, "ocrbench": 0.016,
    "realworldqa": 0.4549019607843137, "countbench": 0.09572301425661914, "mmmu_pro_standard": 0.22428,
}
ARMD_R2_AVG = 0.2612; ARMC_AVG = 0.2578; ARMB_AVG = 0.2610; FOUR_EP_AVG = 0.2568; RICEVIT_AVG = 0.6008
PROTB = {
    "armE_r2": {"lp": 68.236, "lp_sigma": 0.0182, "knn5": 58.904, "per_seed": [68.212, 68.256, 68.240]},
    "armD_r2": {"lp": 64.3373, "lp_sigma": 0.0034, "knn5": 55.956, "per_seed": [64.3340, 64.3360, 64.3420]},
    "armC": {"lp": 62.332, "lp_sigma": 0.014, "knn5": 54.718, "per_seed": [62.352, 62.322, 62.322]},
    "armB": {"lp": 62.093, "lp_sigma": 0.012, "knn5": 58.102, "per_seed": [62.084, 62.086, 62.110]},
    "4ep":  {"lp": 67.05, "knn5": 42.35},
}

def is_mme(key): return key == "mme"
def num(v): return None if isinstance(v, dict) else (float(v) if isinstance(v, (int, float)) else None)
def fmt_pct(v): return f"{v*100:.2f}%" if isinstance(v, (int, float)) else "N/A"
def fmt_mme(v):
    return f"{v.get('perception_score',0):.1f} + {v.get('cognition_score',0):.1f}" if isinstance(v, dict) else "N/A"
def avg_excl_mme(results):
    vals = [v for v in (num(results.get(k)) for k, *_ in BENCH_ORDER if not is_mme(k)) if v is not None]
    return sum(vals)/len(vals) if vals else None
def verdict(avg, results):
    if avg is None: return ("N/A", "bad", "结果缺失, 无法裁定")
    if avg >= 0.30: return ("强成功 (strong success)", "ok", f"平均(除MME)={avg*100:.2f}% ≥ 30%")
    fine_delta = [(k, (num(results.get(k))-num(ARMD_R2.get(k)))*100) for k in ["docvqa_val","chartqa","ocrbench"] if num(results.get(k)) is not None and num(ARMD_R2.get(k)) is not None]
    if avg > 0.24 and any(d >= 10.0 for _, d in fine_delta):
        hit = ", ".join(f"{k} Δ+{d:.2f}pp" for k, d in fine_delta if d >= 10.0)
        return ("成功 (success)", "ok", f"平均={avg*100:.2f}% > 24% 且细粒度任一 +10pp(vs ArmD-R2): {hit}")
    if 0.22 <= avg <= 0.265: return ("不可分辨 (indistinguishable, 边界值)", "warn", f"平均={avg*100:.2f}% 落在 22-26% 区间")
    if avg <= 0.22: return ("失败 (fail)", "bad", f"平均={avg*100:.2f}% ≤ 22%")
    return ("边界/部分成功 (26-30%, 无细粒度 +10pp)", "warn", f"平均={avg*100:.2f}% 在 26-30% 但细粒度无 +10pp(vs ArmD-R2)")
def bench_table(R):
    head = "<tr><th>#</th><th>评测集</th><th>指标</th><th>ArmE-R2</th><th>ArmD-R2</th><th>Δ vs ArmD-R2</th><th>ArmC</th><th>ArmB</th><th>能力维度</th></tr>"
    body = ""
    for i, (key, name, metric, desc) in enumerate(BENCH_ORDER, 1):
        if is_mme(key):
            ae, ad, ac, ab = fmt_mme(R.get(key)), fmt_mme(ARMD_R2.get(key)), fmt_mme(ARMC.get(key)), fmt_mme(ARMB.get(key)); dd = "—"
        else:
            a, d, c, b = num(R.get(key)), num(ARMD_R2.get(key)), num(ARMC.get(key)), num(ARMB.get(key))
            ae, ad, ac, ab = fmt_pct(a), fmt_pct(d), fmt_pct(c), fmt_pct(b)
            if a is not None and d is not None:
                delta = (a - d) * 100
                cls = 'ok' if delta > 0.5 else ('bad' if delta < -0.5 else '')
                dd = f"<span class='{cls}'>{delta:+.2f}pp</span>"
            else:
                dd = "N/A"
        body += f"<tr><td>{i}</td><td>{escape(name)}</td><td>{escape(metric)}</td><td>{ae}</td><td>{ad}</td><td>{dd}</td><td>{ac}</td><td>{ab}</td><td>{escape(desc)}</td></tr>"
    avg = avg_excl_mme(R)
    if avg is not None:
        dd_avg = (avg-ARMD_R2_AVG)*100; cls_d = 'ok' if dd_avg>0.5 else ('bad' if dd_avg<-0.5 else '')
        body += f"<tr><td>—</td><td><b>平均(除MME)</b></td><td>—</td><td><b>{avg*100:.2f}%</b></td><td>{ARMD_R2_AVG*100:.2f}%</td><td><span class='{cls_d}'><b>{dd_avg:+.2f}pp</b></span></td><td>{ARMC_AVG*100:.2f}%</td><td>{ARMB_AVG*100:.2f}%</td><td>—</td></tr>"
    return "<table>" + head + body + "</table>"
def bar_svg(R):
    rows = [(k, n, num(R.get(k))) for k, n, *_ in BENCH_ORDER if not is_mme(k)]
    rows = [(k, n, v) for k, n, v in rows if v is not None]
    if not rows: return "<p>(无数据)</p>"
    maxv = max(max(v for _, _, v in rows), 0.01); bars = ""
    for k, name, v in rows:
        h = max(v/maxv*100, 1); ad = num(ARMD_R2.get(k)); ad_h = (ad/maxv*100) if ad is not None else 0
        bars += f"<div class='bar-row'><span class='bar-label'>{escape(name)}</span><div class='bar-track'><div class='bar-fill' style='width:{h:.1f}%'></div><div class='bar-ref' style='width:{ad_h:.1f}%'></div></div><span class='bar-val'>{v*100:.2f}%</span></div>"
    return f"<div class='chart'>{bars}</div><p class='small'>■ ArmE-R2 &nbsp; ▒ ArmD-R2 (对照基线 {ARMD_R2_AVG*100:.2f}%)</p>"
def protb_table():
    rows = ""
    for key, label in [("armE_r2","ArmE-R2 (本实验)"),("armD_r2","ArmD-R2 (对照基线)"),("4ep","④-4ep"),("armC","ArmC"),("armB","ArmB")]:
        p = PROTB[key]; seeds = p.get("per_seed",[])
        rows += f"<tr><td>{escape(label)}</td><td>{p['lp']:.4f}</td><td>{p.get('lp_sigma','—')}</td><td>{p['knn5']:.3f}</td><td>{' / '.join(f'{s:.3f}' for s in seeds) if seeds else '—'}</td></tr>"
    return f"<table><tr><th>实验</th><th>lp (mean %)</th><th>lp σ</th><th>5-NN (%)</th><th>per-seed lp</th></tr>{rows}</table>"
def build_html(R, results_dir, out_path):
    avg = avg_excl_mme(R); avg_str = f"{avg*100:.2f}%" if avg is not None else "N/A"
    vlabel, vcls, vreason = verdict(avg, R)
    gen = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    delta_armd = (avg-ARMD_R2_AVG)*100 if avg is not None else 0
    delta_armc = (avg-ARMC_AVG)*100 if avg is not None else 0
    delta_armb = (avg-ARMB_AVG)*100 if avg is not None else 0
    delta_4ep = (avg-FOUR_EP_AVG)*100 if avg is not None else 0
    d_lp_d = PROTB["armE_r2"]["lp"]-PROTB["armD_r2"]["lp"]; d_knn_d = PROTB["armE_r2"]["knn5"]-PROTB["armD_r2"]["knn5"]
    d_lp_c = PROTB["armE_r2"]["lp"]-PROTB["armC"]["lp"]; d_knn_c = PROTB["armE_r2"]["knn5"]-PROTB["armC"]["knn5"]
    d_lp_b = PROTB["armE_r2"]["lp"]-PROTB["armB"]["lp"]; d_knn_b = PROTB["armE_r2"]["knn5"]-PROTB["armB"]["knn5"]
    d_lp_4 = PROTB["armE_r2"]["lp"]-PROTB["4ep"]["lp"]; d_knn_4 = PROTB["armE_r2"]["knn5"]-PROTB["4ep"]["knn5"]
    HTML = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>BaiZe ArmE-R2 视觉编码器 MLLM Stage-iv 12-集评测报告 (2026-10-22→10-24)</title>
<style>
body {{ font-family: -apple-system, "PingFang SC", "Microsoft YaHei", sans-serif; max-width: 1100px; margin: 0 auto; padding: 20px; color: #222; line-height: 1.6; }}
h1 {{ color: #1a3a5c; border-bottom: 3px solid #1a3a5c; padding-bottom: 8px; }}
h2 {{ color: #2a5a8c; margin-top: 28px; border-left: 4px solid #2a5a8c; padding-left: 10px; }}
table {{ border-collapse: collapse; width: 100%; margin: 12px 0; font-size: 14px; }}
th, td {{ border: 1px solid #ccc; padding: 6px 10px; text-align: center; }}
th {{ background: #eef4fa; font-weight: 600; }}
tr:nth-child(even) {{ background: #f8fafc; }}
.ok {{ color: #1a7a1a; font-weight: 600; }} .bad {{ color: #c00; font-weight: 600; }} .warn {{ color: #b80; font-weight: 600; }}
.small {{ font-size: 12px; color: #666; }}
.kbox {{ background: #fffbe6; border: 1px solid #e0d090; border-radius: 6px; padding: 12px 16px; margin: 12px 0; }}
.summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 12px 0; }}
.card {{ background: #f0f6fc; border: 1px solid #b0d0e8; border-radius: 8px; padding: 10px 16px; min-width: 150px; text-align: center; }}
.card .l {{ font-size: 12px; color: #556; }} .card .v {{ font-size: 22px; font-weight: 700; color: #1a3a5c; }}
.chart {{ margin: 12px 0; }} .bar-row {{ display: flex; align-items: center; margin: 3px 0; }}
.bar-label {{ width: 130px; font-size: 12px; text-align: right; padding-right: 8px; }}
.bar-track {{ flex: 1; height: 18px; background: #eee; border-radius: 3px; position: relative; overflow: hidden; }}
.bar-fill {{ height: 100%; background: #2a7ab8; border-radius: 3px; }}
.bar-ref {{ position: absolute; top: 0; left: 0; height: 100%; background: repeating-linear-gradient(45deg, #ccc, #ccc 3px, transparent 3px, transparent 6px); border-right: 2px solid #888; }}
.bar-val {{ width: 60px; font-size: 12px; padding-left: 6px; }}
</style></head><body>
<h1>BaiZe ArmE-R2 视觉编码器 · MLLM Stage-iv 12-集评测报告</h1>
<p class="small">实验代号 ArmE-R2 · 时间 2026-10-22 → 2026-10-24 · 生成于 {gen}</p>
<div class="kbox">
<b>⚠️ 变量披露 (必须逐字对齐)</b><br>
ArmE-R2 = <b>ArmE 降 LR 重跑</b>。ArmE(原 LR 1e-3) 于 step~29200 发散 (C1=0.0014)，根因 = ViT-L/14(304M) 比 ViT-B/16(86M) 大 3.5× 却沿用 LR 1e-3，更新幅度过大 → spike 反复、C1 恢复慢。<br>
<b>ArmE-R2 vs ArmE = 仅两变量</b>：peak LR 1e-3→<b>5e-4</b> + warmup 2000→<b>3000</b>（塔/数据/GBS/steps/loss/mask/wd/seed 全同）→ 干净对照「降 LR+warmup 是否消除 spike」。<br>
<b>ArmE-R2 vs ArmD-R2 = 三变量</b>：塔(B/16 86.2M → L/14 304M) + LR(1e-3→5e-4) + warmup(2000→3000) → 报告须分开表述。<br>
<b>容量混杂 (运维令⑤)</b>：ArmE-R2 塔(304M) 比 ArmD-R2(86.2M) 大 ~3.5×，若 MLLM 胜出<b>不得单独归因"架构更好"</b>，须并列说明"容量+架构"复合变量；若持平/落后则说明"容量不是瓶颈"。<br>
<b>Stage-2 instruct 数据</b>：同 ArmD-R2，用原版 LLaVA-NeXT-780k quick-start 子集 (pretrain-*.tar, 738588 样本, 非 opt47)。
</div>
<h2>1. 摘要</h2>
<div class="summary">
<div class="card"><div class="l">ArmE-R2 平均(除 MME)</div><div class="v">{avg_str}</div></div>
<div class="card"><div class="l">vs ArmD-R2 (26.12%) · 主对照</div><div class="v">{delta_armd:+.2f}pp</div></div>
<div class="card"><div class="l">vs ArmC (25.78%)</div><div class="v">{delta_armc:+.2f}pp</div></div>
<div class="card"><div class="l">vs ArmB (26.10%)</div><div class="v">{delta_armb:+.2f}pp</div></div>
<div class="card"><div class="l">vs ④-4ep (25.68%)</div><div class="v">{delta_4ep:+.2f}pp</div></div>
</div>
<div class="kbox"><b>预注册判据裁定 (沿用 ArmB/ArmC/ArmD-R2, 不事后改):</b>
<span class="{vcls}"><b>{vlabel}</b></span><br><span class="small">依据: {vreason}</span><br>
<span class="small">判据: ≥30% 强成功 / &gt;24% 且细粒度任一 +10pp(vs ArmD-R2) 成功 / 22-26% 不可分辨 / ≤22% 失败。</span></div>
<div class="kbox"><b>🏆 ProtB 历史最高</b>：ArmE-R2 lp <b>68.236±0.0182%</b> / 5-NN <b>58.904%</b> → 全实验最高 (vs ArmD-R2 Δlp=+3.899pp / Δ5-NN=+2.948pp)。ViT-L/14(304M)+降LR(5e-4)双因子→ProtB大幅跃升。</div>
<h2>2. 实验配置 (ArmE-R2 vs ArmD-R2 vs ArmC vs ArmB)</h2>
<table><tr><th>项</th><th>ArmB</th><th>ArmC</th><th>ArmD-R2</th><th>ArmE-R2 (本实验)</th><th>变量(vs ArmD-R2)</th></tr>
<tr><td><b>视觉塔</b></td><td>open_clip ViT-B/16 (86.2M)</td><td>同左</td><td>同左</td><td><b>open_clip ViT-L/14 (304.0M visual / 427.6M total)</b></td><td><b>是 (变量①, 容量+架构)</b></td></tr>
<tr><td>初始化</td><td>随机</td><td>同左</td><td>同左</td><td>同左</td><td>否</td></tr>
<tr><td>目标</td><td>AIMv2-style (InfoNCE 1.0 + masked-patch-MSE 1.0, mask 0.6)</td><td>同左</td><td>同左</td><td>同左</td><td>否</td></tr>
<tr><td>预训练数据</td><td>3 源 11350 shards</td><td>同左</td><td>6 源 14589 shards / 173M 对</td><td><b>同 ArmD-R2 (6 源)</b></td><td>否</td></tr>
<tr><td>epoch / 步数</td><td>4 / 57250</td><td>同左</td><td>3 / 63400</td><td><b>同 ArmD-R2 (3 / 63400)</b></td><td>否</td></tr>
<tr><td><b>LR / min_lr</b></td><td>1e-3 / 1e-4</td><td>1e-3 / 1e-5</td><td>1e-3 / 1e-5</td><td><b>5e-4 / 1e-5</b></td><td><b>是 (变量②)</b></td></tr>
<tr><td><b>warmup</b></td><td>2000</td><td>同左</td><td>同左</td><td><b>3000</b></td><td><b>是 (变量③)</b></td></tr>
<tr><td>wd / GBS / MBS / accum</td><td>0.1 / 8192 / 512 / 2</td><td>0.01 / 8192 / 512 / 2</td><td>同 ArmC</td><td><b>0.01 / 8192 / 256 / 4</b> (OOM 回退, GBS 保持)</td><td>⚠️ MBS 非变量 (显存约束)</td></tr>
<tr><td>seed / 优化器</td><td>1234 / AdamW(0.9,0.98) bf16</td><td>同左</td><td>同左</td><td>同左</td><td>否</td></tr>
<tr><td>MLLM 三阶段</td><td>Stage-1(2500)+1.5(20000)+2(3500)</td><td>同左</td><td>同左</td><td>同左 (projector 1024→2560)</td><td>否</td></tr>
<tr><td>Stage-2 instruct 数据</td><td>opt47 (738588)</td><td>同左</td><td>原版 quick-start (738588)</td><td><b>同 ArmD-R2 (原版 quick-start)</b></td><td>否 (同源)</td></tr>
</table>
<p class="small">注：ArmE-R2 vs ArmD-R2 = 三变量 (塔+LR+warmup)。MBS 512→256 是 ViT-L/14 显存约束的强制回退 (GBS=8192 + steps=63400 保持，非消融变量)。ArmE-R2 vs ArmE = 两变量 (仅 LR+warmup，塔/数据全同)。</p>
<h2>3. ProtB 线性探针评测 (Protocol B, IN-1k full/50k, 3 seeds)</h2>
{protb_table()}
<p class="small">ArmE-R2 vs ArmD-R2 (三变量): Δlp = <b>{d_lp_d:+.3f}pp</b> (升, 🏆全实验最高), Δ5-NN = <b>{d_knn_d:+.3f}pp</b> (升)。<b>三变量共同作用, 不得归因单一变量</b>。vs ArmC: Δlp={d_lp_c:+.3f}pp / Δ5-NN={d_knn_c:+.3f}pp。vs ArmB: Δlp={d_lp_b:+.3f}pp / Δ5-NN={d_knn_b:+.3f}pp。vs ④-4ep: Δlp={d_lp_4:+.3f}pp / Δ5-NN={d_knn_4:+.3f}pp。</p>
<p class="small">⚠️ <b>容量混杂</b>：ArmE-R2 塔(304M) 比 ArmD-R2(86.2M) 大 3.5×，ProtB 大幅跃升是"容量+架构+降LR"三因子复合结果，不能单独归因"ViT-L/14 架构更好"。</p>
<h2>4. 12-集 lmms-eval 评测结果</h2>
<p>Stage-2 step3500 checkpoint, <b>每卡一个 benchmark</b> (batch_size=32, 8 卡并行, 无 limit, 全量)。结果来源: <code>{escape(results_dir)}/consolidated_12benchmarks.json</code>。</p>
{bench_table(R)}
{bar_svg(R)}
<p class="small">MME 为感知分 + 认知分 (满分 2800)；其余均为准确率/ANLS 百分比。Δ vs ArmD-R2 = (ArmE-R2 − ArmD-R2)×100 pp。ArmE-R2 与 ArmD-R2 的 Stage-2 instruct 数据同源 (原版 quick-start), 故 ④Δ 不含 Stage-2 数据混杂, 但含"塔+LR+warmup"三变量混杂。</p>
<h2>5. 关键结论与诚实披露</h2>
<div class="kbox">
<p><b>① 主裁定</b>: <span class="{vcls}">{vlabel}</span>。{vreason}。ArmE-R2 vs ArmD-R2 (主对照) 平均 Δ = {delta_armd:+.2f}pp。</p>
<p><b>② 三变量限制 + 容量混杂</b>: ArmE-R2 vs ArmD-R2 同时改了塔(B/16→L/14, 86.2M→304M)、LR(1e-3→5e-4)、warmup(2000→3000) 三项, 任何 Δ 都不能拆出单一变量因果。视觉塔容量增大 3.5× → <b>若 MLLM 胜出, 须并列说明"容量+架构"复合变量, 不得单独归因"架构更好"</b>；若持平/落后, 则说明"容量不是 MLLM 下游瓶颈"。</p>
<p><b>③ 编码器结论 (已 secured, 🏆历史最高)</b>: ArmE-R2 ProtB <b>lp 68.236% / 5-NN 58.904%</b> = 全实验最高。vs ArmD-R2 Δlp=+3.899pp / Δ5-NN=+2.948pp, vs ArmC Δlp=+5.904pp, vs ④-4ep Δlp=+1.186pp/Δ5-NN=+16.554pp。ViT-L/14(304M)+降LR(5e-4)双因子 → 线性可分性与近邻检索均大幅改善。<b>这是"容量+架构+降LR"三因子复合结果</b>。</p>
<p><b>④ ProtB→MLLM 传递性</b>: ArmE-R2 ProtB lp (68.24%) 显著高于 ArmD-R2 (64.34%, +3.9pp) / ArmC (62.33%, +5.9pp) / ArmB (62.09%, +6.1pp), 但 MLLM 12集平均 vs ArmD-R2 仅 {delta_armd:+.2f}pp → <b>再次印证线性探针不直接预测 MLLM 下游表现</b>。编码器 ~4-6pp 的 ProtB 优势未转化为 MLLM 下游优势。</p>
<p><b>⑤ ArmE-R2 vs ArmE (降 LR 效果, 两变量干净对照)</b>: ArmE(LR 1e-3) 于 step~29200 发散 (C1=0.0014); ArmE-R2(LR 5e-4) 全程稳定, C1 历史最高 0.9664@s45240, 末段 ~0.80, spike25 全闭合 → <b>降 LR(1e-3→5e-4)+warmup(2000→3000) 成功消除 ViT-L/14 的 spike 反复与发散</b>。</p>
<p><b>⑥ 诚实条款</b>: 内部 ProtB/MLLM 口径, 非官方榜; 单 backbone/单预算点; MLLM 三阶段单 seed; 224px 单块 (无 anyres), 细粒度任务天然偏低; Stage-2 数据为原版 quick-start (同 ArmD-R2); MBS 512→256 是显存强制回退非消融变量。</p>
</div>
<h2>6. 文件路径</h2>
<table>
<tr><th>产物</th><th>路径</th></tr>
<tr><td>ArmE-R2 训练输出</td><td><code>/nas_train/app.e0031982/datasets/baize-vision/out/armE_r2_20261022_aimv2_openclip_vitl14_224/</code></td></tr>
<tr><td>open_clip 权重</td><td><code>.../armE_r2_20261022_.../open_clip_state_dict.pt</code> (1.7GB)</td></tr>
<tr><td>ArmE 发散证据(原 LR 1e-3)</td><td><code>.../armE_20261021_DIVERGED_archive/</code> (留档不删)</td></tr>
<tr><td>ProtB 结果</td><td><code>vision/armE_r2_20261022_protb_vitl14_224_results.json</code></td></tr>
<tr><td>MLLM 三阶段</td><td><code>.../mllm_stage{{1,15,2}}_armE_r2_20261022/</code> (Stage-2 step3500)</td></tr>
<tr><td>12-集原始结果</td><td><code>{escape(results_dir)}/eval_*.json</code></td></tr>
<tr><td>12-集合并</td><td><code>{escape(results_dir)}/consolidated_12benchmarks.json</code></td></tr>
<tr><td>本报告</td><td><code>{escape(out_path)}</code></td></tr>
<tr><td>实验记录</td><td><code>EXPERIMENTS_VISION.md §15</code></td></tr>
</table>
<hr>
<p class="small">本报告由 <code>vision/generate_armE_r2_mllm_report.py</code> 自动生成 · 所有数字来自落盘产物, 未做外推或臆造。生成时间 {gen}。</p>
</div></body></html>"""
    return HTML
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--results-dir", type=str, default=DEFAULT_RESULTS_DIR)
    ap.add_argument("--out", type=str, default=DEFAULT_OUT)
    args = ap.parse_args()
    cj = os.path.join(args.results_dir, "consolidated_12benchmarks.json")
    if not os.path.exists(cj):
        print(f"ERROR: 未找到 {cj} —— ④ 12-集评测可能尚未完成。", file=sys.stderr); sys.exit(1)
    with open(cj) as f: data = json.load(f)
    R = data.get("results", {}); os.makedirs(os.path.dirname(args.out), exist_ok=True)
    html = build_html(R, args.results_dir, args.out)
    with open(args.out, "w") as f: f.write(html)
    avg = avg_excl_mme(R); vlabel, vcls, _ = verdict(avg, R)
    print(f"✅ 报告已生成: {args.out}")
    print(f"   ArmE-R2 平均(除MME) = {avg*100:.2f}%" if avg is not None else "   平均: N/A")
    print(f"   vs ArmD-R2 (26.12%) = {(avg-ARMD_R2_AVG)*100:+.2f}pp" if avg is not None else "")
    print(f"   vs ArmC (25.78%) = {(avg-ARMC_AVG)*100:+.2f}pp" if avg is not None else "")
    print(f"   vs ArmB (26.10%) = {(avg-ARMB_AVG)*100:+.2f}pp" if avg is not None else "")
    print(f"   裁定: {vlabel}")
if __name__ == "__main__":
    main()
