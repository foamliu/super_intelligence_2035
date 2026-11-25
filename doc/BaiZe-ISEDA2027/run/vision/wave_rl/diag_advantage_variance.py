#!/usr/bin/env python
"""diag_advantage_variance.py — GRPO Advantage Variance Diagnosis (CPU-only).

Loads the post-SFT step3000 LoRA checkpoint on the qwen3vl_2b_text_extracted
2B text backbone, then runs group_size=4 rollouts on 200 prompts drawn from
the same distribution as sft_pilot_balanced.jsonl / waveqa_oracle_300.json.

Purpose: diagnose *why* GRPO spins (loss~0, no improvement).  Hypothesis:
on a 9.2%-success-rate base policy, group_size=4 yields identical rewards
(usually all-0) for the vast majority of prompts  =>  intra-group normalised
advantage = 0  =>  gradient = 0  =>  no learning.

This script performs **diagnosis only** -- no training, no checkpoint writes,
no GPU.  It completely reuses grpo_train_wave.py's rollout_episode() and the
WaveformGymEnv reward (temperature 0.8 / max_turns 8 / max_new_tokens 48),
without altering the reward computation in any way.

Pre-registered decision rules (cannot be changed after seeing data):
  * std=0 groups >= 80 % AND all-0 groups are the majority  =>  NO-SIGNAL
  * std>0 groups >= 30 %                                    =>  PARAM-ISSUE
  * middle ground                                           =>  PARTIAL

Usage (CPU, nice, thread-limited per operator guardrails):
  OMP_NUM_THREADS=16 nice -n 19 python diag_advantage_variance.py
  OMP_NUM_THREADS=16 nice -n 19 python diag_advantage_variance.py --n_prompts 100

Author: vision agent (wake #838).  License: project-internal.
"""

import sys, os, json, time, argparse, tempfile, traceback
from collections import defaultdict

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from peft import PeftModel

# --- reuse existing wave-RL infrastructure (no reward rewriting) ---
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from grpo_train_wave import (  # noqa: E402
    rollout_episode,
)
from waveqa_eval import generate_eval_questions  # noqa: E402
from waveview_gym import WaveformGymEnv  # noqa: E402

# --------------------------------------------------------------------------- #
#  Constants
# --------------------------------------------------------------------------- #
MODEL_PATH = (
    "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/"
    "qwen3vl_2b_text_extracted"
)
SFT_CKPT = (
    "/nas_train/app.e0031982/datasets/baize-vision/out/wave_sft_stage1w/"
    "step3000"
)
WAVE_RL_DIR = os.path.dirname(os.path.abspath(__file__))
REPORTS_DIR = (
    "/nas_train/app.e0031982/code/super_intelligence_2035/"
    "doc/BaiZe-ISEDA2027/reports"
)

# Floating-point tolerance for "std == 0"
STD_ZERO_EPS = 1e-9


# --------------------------------------------------------------------------- #
#  CLI
# --------------------------------------------------------------------------- #
def parse_args():
    p = argparse.ArgumentParser(
        description="GRPO advantage-variance diagnosis (CPU-only, no training)")
    p.add_argument("--model_path", type=str, default=MODEL_PATH,
                   help="Base 2B text-backbone LLM path.")
    p.add_argument("--sft_ckpt", type=str, default=SFT_CKPT,
                   help="Post-SFT LoRA adapter directory (step3000).")
    p.add_argument("--n_prompts", type=int, default=200,
                   help="Number of prompts to diagnose (reduce to 100 if time "
                        "constrained).")
    p.add_argument("--group_size", type=int, default=4,
                   help="Rollouts per prompt (must match GRPO group_size).")
    p.add_argument("--seed", type=int, default=20261112,
                   help="Fixed seed for reproducible question generation.")
    p.add_argument("--temperature", type=float, default=0.8,
                   help="Sampling temperature (must match GRPO default).")
    p.add_argument("--max_turns", type=int, default=8)
    p.add_argument("--max_new_tokens", type=int, default=48)
    p.add_argument("--seq_len", type=int, default=2048)
    p.add_argument("--time_budget_s", type=int, default=2100,
                   help="Soft time budget in seconds (35 min).")
    p.add_argument("--output_dir", type=str, default=WAVE_RL_DIR)
    p.add_argument("--report_dir", type=str, default=REPORTS_DIR)
    return p.parse_args()


# --------------------------------------------------------------------------- #
#  Model loading (eval mode, CPU, is_trainable=False)
# --------------------------------------------------------------------------- #
def load_model(args):
    """Load base 2B LLM + post-SFT LoRA adapter in eval mode on CPU."""
    device = torch.device("cpu")
    dtype = torch.float32
    t0 = time.time()
    print(f"[load] Loading base model: {args.model_path}", flush=True)
    llm = AutoModelForCausalLM.from_pretrained(
        args.model_path, torch_dtype=dtype, trust_remote_code=True,
        device_map={"": device})
    print(f"[load] Loading LoRA adapter: {args.sft_ckpt}", flush=True)
    llm = PeftModel.from_pretrained(llm, args.sft_ckpt, is_trainable=False)
    llm.eval()
    tokenizer = AutoTokenizer.from_pretrained(
        args.model_path, trust_remote_code=True)
    if tokenizer.pad_token_id is None:
        tokenizer.pad_token = tokenizer.eos_token
    print(f"[load] Done in {time.time()-t0:.1f}s "
          f"(trainable=False, eval mode, CPU float32)", flush=True)
    return llm, tokenizer, device, dtype


# --------------------------------------------------------------------------- #
#  Per-prompt group rollout
# --------------------------------------------------------------------------- #
def run_group(llm, tokenizer, q, args, device, dtype):
    """Run *group_size* rollouts for one question; return per-group dict."""
    env = WaveformGymEnv(
        circuit_type=q["circuit"],
        measure_target=q["target"],
        workdir=q["ep_wd"])
    env.spec = q["spec"]

    rewards, submitted_flags, submit_values, turns_list = [], [], [], []
    for g in range(args.group_size):
        try:
            conv, rew, info = rollout_episode(
                llm, tokenizer, env, q["spec"], q["target"], q["signal"],
                device, dtype,
                max_turns=args.max_turns,
                max_new_tokens=args.max_new_tokens,
                temperature=args.temperature,
                seq_len=args.seq_len)
        except Exception:
            conv, rew, info = [], -1.0, {"submitted": False}
        rewards.append(float(rew))
        submitted_flags.append(bool(info.get("submitted", False)))
        submit_values.append(info.get("submit_value"))
        turns_list.append(info.get("turns", 0))

    r_arr = np.array(rewards, dtype=np.float64)
    mean_r = float(r_arr.mean())
    std_r = float(r_arr.std())
    n_submit = int(sum(submitted_flags))

    is_std0 = std_r < STD_ZERO_EPS
    all_zero = is_std0 and abs(mean_r) < STD_ZERO_EPS
    all_same_pos = is_std0 and mean_r > 0
    all_same_high = is_std0 and mean_r >= 1.0
    has_partial_signal = 0.0 < mean_r < 1.0 and not is_std0

    return {
        "id": q["id"],
        "qtype": q["type"],
        "circuit": q["circuit"],
        "target": q["target"],
        "signal": q["signal"],
        "rewards": rewards,
        "mean": mean_r,
        "std": std_r,
        "n_submit": n_submit,
        "submit_values": submit_values,
        "turns": turns_list,
        "is_std0": is_std0,
        "all_zero": all_zero,
        "all_same_pos": all_same_pos,
        "all_same_high": all_same_high,
        "has_partial_signal": has_partial_signal,
    }


# --------------------------------------------------------------------------- #
#  Summary statistics (pre-registered categories)
# --------------------------------------------------------------------------- #
def compute_summary(results, args):
    n = len(results)
    if n == 0:
        return {"error": "no results"}

    n_std0 = sum(1 for r in results if r["is_std0"])
    n_all_zero = sum(1 for r in results if r["all_zero"])
    n_all_same_pos = sum(1 for r in results if r["all_same_pos"])
    n_all_same_high = sum(1 for r in results if r["all_same_high"])
    n_std_pos = sum(1 for r in results if not r["is_std0"])
    n_partial = sum(1 for r in results if r["has_partial_signal"])

    # Per-question-type breakdown
    by_type = {}
    for qt in ["numerical", "open_ended", "multi_choice"]:
        subset = [r for r in results if r["qtype"] == qt]
        if not subset:
            by_type[qt] = {"n": 0}
            continue
        ns = len(subset)
        by_type[qt] = {
            "n": ns,
            "n_std0": sum(1 for r in subset if r["is_std0"]),
            "pct_std0": f"{sum(1 for r in subset if r['is_std0'])/ns*100:.1f}%",
            "n_all_zero": sum(1 for r in subset if r["all_zero"]),
            "n_all_same_high": sum(1 for r in subset if r["all_same_high"]),
            "mean_of_means": float(np.mean([r["mean"] for r in subset])),
            "mean_of_stds": float(np.mean([r["std"] for r in subset])),
            "submit_rate": f"{sum(r['n_submit'] for r in subset)/(ns*args.group_size)*100:.1f}%",
        }

    # Per-measure-target breakdown
    by_target = {}
    for mt in sorted(set(r["target"] for r in results)):
        subset = [r for r in results if r["target"] == mt]
        ns = len(subset)
        by_target[mt] = {
            "n": ns,
            "pct_std0": f"{sum(1 for r in subset if r['is_std0'])/ns*100:.1f}%",
            "n_all_zero": sum(1 for r in subset if r["all_zero"]),
            "mean_reward": float(np.mean([r["mean"] for r in subset])),
            "mean_std": float(np.mean([r["std"] for r in subset])),
            "submit_rate": f"{sum(r['n_submit'] for r in subset)/(ns*args.group_size)*100:.1f}%",
        }

    # std distribution histogram
    stds = [r["std"] for r in results]
    hist_bins = [0, 0.001, 0.01, 0.05, 0.1, 0.2, 0.5, 1.0, float("inf")]
    hist_labels = ["=0", "0~.001", ".001~.01", ".01~.05",
                   ".05~.1", ".1~.2", ".2~.5", ".5+"]
    hist_counts = []
    for i in range(len(hist_bins) - 1):
        lo, hi = hist_bins[i], hist_bins[i + 1]
        if i == 0:
            c = sum(1 for s in stds if s < STD_ZERO_EPS)
        else:
            c = sum(1 for s in stds if lo <= s < hi)
        hist_counts.append(c)

    # Reward mean distribution
    means = [r["mean"] for r in results]
    mean_bins = [-2.1, -0.01, 0.01, 0.5, 1.0, 1.5, float("inf")]
    mean_labels = ["<0", "=0", "0~.5", ".5~1", "1~1.5", "1.5+"]
    mean_counts = []
    for i in range(len(mean_bins) - 1):
        lo, hi = mean_bins[i], mean_bins[i + 1]
        if i == 1:
            c = sum(1 for m in means if abs(m) < STD_ZERO_EPS)
        elif i == 0:
            c = sum(1 for m in means if m < -0.01)
        else:
            c = sum(1 for m in means if lo <= m < hi)
        mean_counts.append(c)

    all_rewards = [r2 for r in results for r2 in r["rewards"]]
    overall = {
        "mean": float(np.mean(all_rewards)),
        "std": float(np.std(all_rewards)),
        "min": float(min(all_rewards)),
        "max": float(max(all_rewards)),
        "pct_zero": f"{sum(1 for x in all_rewards if abs(x) < STD_ZERO_EPS)/len(all_rewards)*100:.1f}%",
        "pct_positive": f"{sum(1 for x in all_rewards if x > 0)/len(all_rewards)*100:.1f}%",
        "pct_ge1": f"{sum(1 for x in all_rewards if x >= 1.0)/len(all_rewards)*100:.1f}%",
    }

    # Pre-registered decision
    pct_std0_val = n_std0 / n
    pct_stdpos_val = n_std_pos / n
    all_zero_majority = n_all_zero > n_all_same_pos

    if pct_std0_val >= 0.80 and all_zero_majority:
        verdict = "NO-SIGNAL"
    elif pct_stdpos_val >= 0.30:
        verdict = "PARAM-ISSUE"
    else:
        verdict = "PARTIAL"

    return {
        "config": {
            "n_prompts": n, "group_size": args.group_size,
            "temperature": args.temperature, "max_turns": args.max_turns,
            "max_new_tokens": args.max_new_tokens, "seed": args.seed,
            "model_path": args.model_path, "sft_ckpt": args.sft_ckpt,
            "device": "cpu", "dtype": "float32",
        },
        "overall_reward": overall,
        "key_stats": {
            "n_total": n, "n_std0": n_std0,
            "pct_std0": f"{pct_std0_val*100:.1f}%",
            "n_all_zero": n_all_zero,
            "pct_all_zero": f"{n_all_zero/n*100:.1f}%",
            "n_all_same_pos": n_all_same_pos,
            "pct_all_same_pos": f"{n_all_same_pos/n*100:.1f}%",
            "n_all_same_high": n_all_same_high,
            "pct_all_same_high": f"{n_all_same_high/n*100:.1f}%",
            "n_std_pos": n_std_pos,
            "pct_std_pos": f"{pct_stdpos_val*100:.1f}%",
            "n_partial_signal": n_partial,
            "pct_partial_signal": f"{n_partial/n*100:.1f}%",
            "overall_submit_rate": f"{sum(r['n_submit'] for r in results)/(n*args.group_size)*100:.1f}%",
        },
        "std_histogram": {"labels": hist_labels, "counts": hist_counts},
        "mean_histogram": {"labels": mean_labels, "counts": mean_counts},
        "by_question_type": by_type,
        "by_measure_target": by_target,
        "verdict": verdict,
        "verdict_logic": (
            f"std=0 groups = {pct_std0_val*100:.1f}% (threshold 80%); "
            f"std>0 groups = {pct_stdpos_val*100:.1f}% (threshold 30%); "
            f"all-zero majority among std=0 = {all_zero_majority}"),
    }


# --------------------------------------------------------------------------- #
#  HTML report helpers (Chinese, single-file, no external links/scripts)
# --------------------------------------------------------------------------- #
def _build_svgs(summary, bar_w=70, gap=12):
    """Build inline SVG chart strings for std and mean histograms."""
    sh = summary["std_histogram"]
    chart_w = len(sh["labels"]) * (bar_w + gap) + 60
    max_c = max(sh["counts"]) if sh["counts"] else 1
    bars = ""
    for i, (label, cnt) in enumerate(zip(sh["labels"], sh["counts"])):
        x = 40 + i * (bar_w + gap)
        bh = int(cnt / max_c * 160) if max_c > 0 else 0
        y = 190 - bh
        color = "#dc3545" if i == 0 else "#0d6efd"
        bars += (f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bh}" '
                 f'fill="{color}" rx="3"/><text x="{x+bar_w/2}" y="{y-6}" '
                 f'text-anchor="middle" font-size="13" font-weight="bold">'
                 f'{cnt}</text><text x="{x+bar_w/2}" y="208" '
                 f'text-anchor="middle" font-size="11">{label}</text>')
    mh = summary["mean_histogram"]
    chart_w2 = len(mh["labels"]) * (bar_w + gap) + 60
    max_c2 = max(mh["counts"]) if mh["counts"] else 1
    bars2 = ""
    for i, (label, cnt) in enumerate(zip(mh["labels"], mh["counts"])):
        x = 40 + i * (bar_w + gap)
        bh = int(cnt / max_c2 * 160) if max_c2 > 0 else 0
        y = 190 - bh
        color = "#dc3545" if i <= 1 else "#198754" if i >= 4 else "#fd7e14"
        bars2 += (f'<rect x="{x}" y="{y}" width="{bar_w}" height="{bh}" '
                  f'fill="{color}" rx="3"/><text x="{x+bar_w/2}" y="{y-6}" '
                  f'text-anchor="middle" font-size="13" font-weight="bold">'
                  f'{cnt}</text><text x="{x+bar_w/2}" y="208" '
                  f'text-anchor="middle" font-size="11">{label}</text>')
    return bars, chart_w, bars2, chart_w2


def _build_type_target_rows(summary):
    by_type = summary["by_question_type"]
    type_rows = ""
    for qt in ["numerical", "open_ended", "multi_choice"]:
        d = by_type.get(qt, {})
        if d.get("n", 0) == 0:
            type_rows += f"<tr><td>{qt}</td><td>0</td><td colspan='6'>-</td></tr>"
            continue
        type_rows += (f"<tr><td>{qt}</td><td>{d['n']}</td><td>{d['pct_std0']}"
                      f"</td><td>{d['n_all_zero']}</td><td>{d['n_all_same_high']}"
                      f"</td><td>{d['mean_of_means']:.4f}</td>"
                      f"<td>{d['mean_of_stds']:.4f}</td><td>{d['submit_rate']}"
                      f"</td></tr>")
    target_rows = ""
    for mt, d in sorted(summary["by_measure_target"].items()):
        target_rows += (f"<tr><td>{mt}</td><td>{d['n']}</td><td>{d['pct_std0']}"
                        f"</td><td>{d['n_all_zero']}</td>"
                        f"<td>{d['mean_reward']:.4f}</td>"
                        f"<td>{d['mean_std']:.4f}</td><td>{d['submit_rate']}"
                        f"</td></tr>")
    return type_rows, target_rows


def _build_sample_rows(results, group_size):
    rows = ""
    for r in results[:20]:
        rew_str = ", ".join(f"{x:.3f}" for x in r["rewards"])
        std_tag = "std=0" if r["is_std0"] else "std>0"
        zt = " 全0" if r["all_zero"] else (" 全正" if r["all_same_pos"] else "")
        rows += (f"<tr><td>{r['id']}</td><td>{r['qtype']}</td>"
                 f"<td>{r['target']}</td><td>{r['circuit']}</td>"
                 f"<td>{rew_str}</td><td>{r['mean']:.4f}</td>"
                 f"<td>{r['std']:.4f}</td>"
                 f"<td>{r['n_submit']}/{group_size}</td>"
                 f"<td>{std_tag}{zt}</td></tr>")
    return rows


def _build_recommendation(verdict):
    if verdict == "NO-SIGNAL":
        return ('<div class="rec no-signal"><h3>判定：NO-SIGNAL（无学习信号）</h3>'
                '<p>基座成功率太低（post-SFT 9.2%），group_size=4 时绝大多数 '
                'prompt 的 4 条 rollout 奖励全为 0，组内归一化 advantage=0 '
                '=> 梯度为 0 => GRPO 空转。<b>必须先提高基座成功率。</b></p>'
                '<h4>可选项（预估成本）：</h4><ol>'
                '<li><b>更多 SFT 步数</b>：step3000 -> step6000~8000。~4-6 GPU*h。'
                '风险：可能已收敛。</li>'
                '<li><b>更大 LoRA lr</b>：1e-5 -> 2e-5/3e-5 重训。~2-3 GPU*h。</li>'
                '<li><b>扩 SFT 数据</b>：9013 -> 20000+ 条。~1h CPU + ~4-6 GPU*h。'
                '最可能打破"全 0"困境。</li></ol>'
                '<p><b>建议优先级</b>：3 扩数据 &gt; 1 加步数 &gt; 2 加 lr。</p></div>')
    elif verdict == "PARAM-ISSUE":
        return ('<div class="rec param-issue"><h3>判定：PARAM-ISSUE</h3>'
                '<p>有足够 std&gt;0 组，但 GRPO 未提升 => lr/步数/group_size 不足。</p>'
                '<h4>GPU 版建议配置：</h4><ul>'
                '<li><b>lr</b>：1e-5（当前 1e-6，10x）</li>'
                '<li><b>步数</b>：500（当前 50）</li>'
                '<li><b>group_size</b>：8（当前 4）</li>'
                '<li><b>精度</b>：bf16</li></ul>'
                '<p>预估成本：~12 GPU*h。需等 GPU 释放。</p></div>')
    else:
        return ('<div class="rec partial"><h3>判定：PARTIAL（部分信号）</h3>'
                '<p>介于 NO-SIGNAL 和 PARAM-ISSUE 之间。</p>'
                '<h4>验证方案：增大 group_size 到 8</h4>'
                '<p>重跑本诊断，观察 std&gt;0 组比例是否上升。~2x 耗时。</p></div>')


def generate_html_report(results, summary, args, wall_s):
    """Generate self-contained Chinese HTML report."""
    ks = summary["key_stats"]
    verdict = summary["verdict"]
    overall = summary["overall_reward"]
    vc = {"NO-SIGNAL": "#dc3545", "PARAM-ISSUE": "#fd7e14",
          "PARTIAL": "#ffc107"}.get(verdict, "#6c757d")
    bars_svg, cw1, bars_svg2, cw2 = _build_svgs(summary)
    type_rows, target_rows = _build_type_target_rows(summary)
    sample_rows = _build_sample_rows(results, args.group_size)
    rec = _build_recommendation(verdict)
    n = ks['n_total']
    ts = time.strftime('%Y-%m-%d %H:%M:%S')
    return _html_template(ks, summary, overall, verdict, vc, args, wall_s,
                          n, ts, cw1, cw2, bars_svg, bars_svg2,
                          type_rows, target_rows, sample_rows, rec)


def _html_template(ks, summary, overall, verdict, vc, args, wall_s,
                   n, ts, cw1, cw2, bars_svg, bars_svg2,
                   type_rows, target_rows, sample_rows, rec):
    css = (
        'body{font-family:-apple-system,"PingFang SC","Microsoft YaHei",'
        'sans-serif;max-width:1100px;margin:0 auto;padding:20px;'
        'background:#f8f9fa;color:#212529}'
        'h1{color:#1a1a2e;border-bottom:3px solid #0d6efd;padding-bottom:10px}'
        'h2{color:#1a1a2e;margin-top:36px;border-left:5px solid #0d6efd;'
        'padding-left:12px}h3{color:#343a40}h4{color:#495057}'
        'table{border-collapse:collapse;width:100%;margin:16px 0;background:#fff}'
        'th,td{border:1px solid #dee2e6;padding:8px 12px;text-align:center;'
        'font-size:14px}th{background:#0d6efd;color:#fff;font-weight:600}'
        'tr:nth-child(even){background:#f8f9fa}'
        '.verdict-box{display:inline-block;padding:12px 32px;border-radius:8px;'
        'font-size:22px;font-weight:bold;color:#fff;margin:12px 0}'
        '.kpi-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:16px;'
        'margin:20px 0}.kpi{background:#fff;border-radius:8px;padding:16px;'
        'text-align:center;box-shadow:0 1px 3px rgba(0,0,0,0.1)}'
        '.kpi .val{font-size:28px;font-weight:bold;color:#0d6efd}'
        '.kpi .lbl{font-size:13px;color:#6c757d;margin-top:4px}'
        '.kpi.red .val{color:#dc3545}.kpi.green .val{color:#198754}'
        '.rec{padding:20px;border-radius:10px;margin:16px 0}'
        '.rec.no-signal{background:#fff5f5;border:2px solid #dc3545}'
        '.rec.param-issue{background:#fff8f0;border:2px solid #fd7e14}'
        '.rec.partial{background:#fffdf0;border:2px solid #ffc107}'
        '.chart{background:#fff;border-radius:8px;padding:16px;margin:16px 0}'
        'code{background:#e9ecef;padding:2px 6px;border-radius:3px;font-size:13px}'
        '.meta{color:#6c757d;font-size:13px}')
    parts = []
    parts.append(f'<!DOCTYPE html><html lang="zh-CN"><head><meta charset="UTF-8">'
                 f'<meta name="viewport" content="width=device-width,initial-scale=1.0">'
                 f'<title>GRPO Advantage 方差诊断报告</title>'
                 f'<style>{css}</style></head><body>')
    parts.append(f'<h1>GRPO Advantage 方差诊断报告</h1>'
                 f'<p class="meta">生成时间：{ts} ｜ 总耗时：{wall_s:.1f}s '
                 f'({wall_s/60:.1f} min) ｜ wake #838 ｜ vision 线</p>')
    return "\n".join(parts) + _html_body(
        ks, summary, overall, verdict, vc, args, n, cw1, cw2,
        bars_svg, bars_svg2, type_rows, target_rows, sample_rows, rec)


def _html_body(ks, summary, overall, verdict, vc, args, n, cw1, cw2,
               bars_svg, bars_svg2, type_rows, target_rows, sample_rows, rec):
    gs = args.group_size
    h = []
    h.append('<h2>1. 背景与目的</h2>'
             '<p>在 2026-11-06 的 CPU GRPO pilot 中，post-GRPO（6.2%）低于 '
             'post-SFT（9.2%），50 步 loss 约 0 => GRPO 空转。假设：group_size=4 '
             '时绝大多数 prompt 的 4 条 rollout 奖励相同（全 0）=> advantage=0 '
             '=> 梯度为 0。本诊断完全复用 grpo_train_wave.py 的 rollout_episode() '
             '和 WaveformGymEnv 奖励（temp=0.8/max_turns=8/max_new_tokens=48），'
             '<b>不修改奖励口径</b>。仅 CPU，不训练/不写ckpt/不占GPU。</p>')
    h.append(f'<h2>2. 实验配置</h2><table>'
             f'<tr><th>参数</th><th>值</th><th>参数</th><th>值</th></tr>'
             f'<tr><td>基座模型</td><td>qwen3vl_2b_text_extracted (2B)</td>'
             f'<td>LoRA adapter</td><td>step3000 (post-SFT)</td></tr>'
             f'<tr><td>设备</td><td>CPU (float32, eval)</td>'
             f'<td>Prompt 数</td><td>{n}</td></tr>'
             f'<tr><td>group_size</td><td>{gs}</td>'
             f'<td>temperature</td><td>{args.temperature}</td></tr>'
             f'<tr><td>max_turns</td><td>{args.max_turns}</td>'
             f'<td>max_new_tokens</td><td>{args.max_new_tokens}</td></tr>'
             f'<tr><td>总 rollout 数</td><td>{n*gs}</td>'
             f'<td>seed</td><td>{args.seed}</td></tr></table>')
    h.append(f'<h2>3. 判定结果</h2>'
             f'<div class="verdict-box" style="background:{vc};">{verdict}</div>'
             f'<p>{summary["verdict_logic"]}</p>')
    h.append(_html_kpi_table(ks))
    h.append(_html_reward_dist(overall))
    h.append(_html_charts(cw1, cw2, bars_svg, bars_svg2))
    h.append(f'<h2>7. 按题型分组统计</h2><table>'
             f'<tr><th>题型</th><th>数量</th><th>std=0%</th><th>全0组</th>'
             f'<th>全高分</th><th>mean</th><th>std</th><th>submit率</th></tr>'
             f'{type_rows}</table>')
    h.append(f'<h2>8. 按测量目标分组统计</h2><table>'
             f'<tr><th>测量目标</th><th>数量</th><th>std=0%</th><th>全0组</th>'
             f'<th>mean</th><th>std</th><th>submit率</th></tr>'
             f'{target_rows}</table>')
    h.append(f'<h2>9. 判定与建议</h2>{rec}')
    h.append(_html_tail(n, sample_rows))
    return "\n".join(h)


def _html_kpi_table(ks):
    return (f'<h2>4. 核心指标</h2><div class="kpi-grid">'
            f'<div class="kpi red"><div class="val">{ks["pct_std0"]}</div>'
            f'<div class="lbl">std=0 组占比</div></div>'
            f'<div class="kpi red"><div class="val">{ks["pct_all_zero"]}</div>'
            f'<div class="lbl">全 0 组占比</div></div>'
            f'<div class="kpi green"><div class="val">{ks["pct_std_pos"]}</div>'
            f'<div class="lbl">std&gt;0 组占比</div></div>'
            f'<div class="kpi"><div class="val">{ks["overall_submit_rate"]}</div>'
            f'<div class="lbl">submit 成功率</div></div></div>'
            f'<table><tr><th>指标</th><th>数量</th><th>占比</th><th>含义</th></tr>'
            f'<tr><td>std=0 组</td><td>{ks["n_std0"]}</td><td>{ks["pct_std0"]}</td>'
            f'<td>4 条 rollout 奖励相同 =&gt; advantage=0 =&gt; 无梯度</td></tr>'
            f'<tr><td>全 0 组</td><td>{ks["n_all_zero"]}</td><td>{ks["pct_all_zero"]}</td>'
            f'<td>模型完全不会做 =&gt; 学不到信号</td></tr>'
            f'<tr><td>全正一致组</td><td>{ks["n_all_same_pos"]}</td>'
            f'<td>{ks["pct_all_same_pos"]}</td><td>奖励相同且为正 =&gt; 亦无梯度</td></tr>'
            f'<tr><td>全高分一致</td><td>{ks["n_all_same_high"]}</td>'
            f'<td>{ks["pct_all_same_high"]}</td><td>均&gt;=1.0 =&gt; 已完全掌握</td></tr>'
            f'<tr><td>std&gt;0 组</td><td>{ks["n_std_pos"]}</td>'
            f'<td>{ks["pct_std_pos"]}</td><td>组内有方差 =&gt; 有学习信号</td></tr>'
            f'<tr><td>部分信号组</td><td>{ks["n_partial_signal"]}</td>'
            f'<td>{ks["pct_partial_signal"]}</td>'
            f'<td>0&lt;mean&lt;1 且 std&gt;0 =&gt; 最适合 GRPO</td></tr></table>')


def _html_reward_dist(overall):
    return (f'<h2>5. 整体奖励分布</h2><table>'
            f'<tr><th>统计量</th><th>值</th></tr>'
            f'<tr><td>所有 rollout 奖励均值</td><td>{overall["mean"]:.4f}</td></tr>'
            f'<tr><td>所有 rollout 奖励标准差</td><td>{overall["std"]:.4f}</td></tr>'
            f'<tr><td>最小 / 最大奖励</td><td>{overall["min"]:.4f} / {overall["max"]:.4f}</td></tr>'
            f'<tr><td>奖励 = 0 占比</td><td>{overall["pct_zero"]}</td></tr>'
            f'<tr><td>奖励 &gt; 0 占比</td><td>{overall["pct_positive"]}</td></tr>'
            f'<tr><td>奖励 &gt;= 1.0 占比</td><td>{overall["pct_ge1"]}</td></tr></table>')


def _html_charts(cw1, cw2, bars_svg, bars_svg2):
    return (f'<h2>6. 图表</h2><div class="chart"><h3>6.1 组内 std 分布直方图</h3>'
            f'<svg width="{cw1}" height="220" xmlns="http://www.w3.org/2000/svg">'
            f'<line x1="38" y1="30" x2="38" y2="190" stroke="#999"/>'
            f'<line x1="38" y1="190" x2="{cw1-10}" y2="190" stroke="#999"/>'
            f'<text x="10" y="35" font-size="11">组数</text>{bars_svg}</svg>'
            f'<p class="meta">红色=std=0组（无梯度）；蓝色=std&gt;0组（有学习信号）</p></div>'
            f'<div class="chart"><h3>6.2 组内奖励均值分布直方图</h3>'
            f'<svg width="{cw2}" height="220" xmlns="http://www.w3.org/2000/svg">'
            f'<line x1="38" y1="30" x2="38" y2="190" stroke="#999"/>'
            f'<line x1="38" y1="190" x2="{cw2-10}" y2="190" stroke="#999"/>'
            f'<text x="10" y="35" font-size="11">组数</text>{bars_svg2}</svg>'
            f'<p class="meta">红色=0/负；橙色=低正；绿色=高奖励</p></div>')


def _html_tail(n, sample_rows):
    return (f'<h2>10. 前 20 个 prompt 详细记录</h2><table>'
            f'<tr><th>ID</th><th>题型</th><th>目标</th><th>电路</th>'
            f'<th>奖励(4条)</th><th>mean</th><th>std</th><th>submit</th>'
            f'<th>分类</th></tr>{sample_rows}</table>'
            f'<p class="meta">完整 {n} 条记录见 '
            f'<code>waveqa_advantage_diag_{n}.jsonl</code></p>'
            f'<h2>11. 预注册决策规则</h2><table>'
            f'<tr><th>条件</th><th>判定</th><th>含义</th></tr>'
            f'<tr><td>std=0&gt;=80% 且全0组占多数</td>'
            f'<td style="color:#dc3545;font-weight:bold">NO-SIGNAL</td>'
            f'<td>基座太弱，先提成功率</td></tr>'
            f'<tr><td>std&gt;0&gt;=30%</td>'
            f'<td style="color:#fd7e14;font-weight:bold">PARAM-ISSUE</td>'
            f'<td>调 lr/步数/group_size</td></tr>'
            f'<tr><td>中间地带</td>'
            f'<td style="color:#ffc107;font-weight:bold">PARTIAL</td>'
            f'<td>增大 group_size 验证</td></tr></table>'
            f'<h2>12. 交付物清单</h2><ul>'
            f'<li><code>vision/wave_rl/diag_advantage_variance.py</code></li>'
            f'<li><code>vision/wave_rl/waveqa_advantage_diag_{n}.jsonl</code></li>'
            f'<li><code>vision/wave_rl/waveqa_advantage_diag_summary.json</code></li>'
            f'<li><code>reports/report_vision_wave_rl_advantage_diag_zh.html</code></li>'
            f'</ul><hr><p class="meta">BaiZe vision 线 ｜ wake #838 ｜ '
            f'{time.strftime("%Y-%m-%d %H:%M")} ｜ CPU-only ｜ '
            f'不训练/不写ckpt/不占GPU</p></body></html>')


# --------------------------------------------------------------------------- #
#  Main
# --------------------------------------------------------------------------- #
def main():
    args = parse_args()
    t_start = time.time()

    os.environ.setdefault("OMP_NUM_THREADS", "16")
    os.environ.setdefault("MKL_NUM_THREADS", "16")
    if torch.cuda.is_available():
        print("[guard] CUDA detected but forcing CPU "
              "(no GPU, pretrain occupies .12/.29)", flush=True)
    torch.set_num_threads(16)

    llm, tokenizer, device, dtype = load_model(args)

    print(f"\n[gen] Generating {args.n_prompts} questions "
          f"(seed={args.seed})...", flush=True)
    t_gen = time.time()
    questions = generate_eval_questions(args.n_prompts, args.seed)
    print(f"[gen] Got {len(questions)} questions in "
          f"{time.time()-t_gen:.1f}s", flush=True)
    if len(questions) < args.n_prompts:
        print(f"[gen] WARNING: only {len(questions)} questions generated "
              f"(requested {args.n_prompts})", flush=True)

    print(f"\n[run] {len(questions)} prompts x {args.group_size} rollouts = "
          f"{len(questions)*args.group_size} total", flush=True)
    results = []
    for i, q in enumerate(questions):
        t0 = time.time()
        r = run_group(llm, tokenizer, q, args, device, dtype)
        results.append(r)
        rew_str = ", ".join(f"{x:.3f}" for x in r["rewards"])
        tag = "std=0" if r["is_std0"] else "std>0"
        print(f"  [{i+1}/{len(questions)}] {r['qtype']}/{r['target']}/"
              f"{r['circuit']} rewards=[{rew_str}] "
              f"mean={r['mean']:.3f} std={r['std']:.3f} "
              f"submit={r['n_submit']}/{args.group_size} "
              f"{tag} ({time.time()-t0:.1f}s)", flush=True)
        total_elapsed = time.time() - t_start
        if total_elapsed > args.time_budget_s and i + 1 >= 50:
            print(f"\n[run] TIME BUDGET ({total_elapsed/60:.1f} min > "
                  f"{args.time_budget_s/60:.1f} min), stopping at {i+1}",
                  flush=True)
            break

    n_actual = len(results)
    jsonl_path = os.path.join(
        args.output_dir, f"waveqa_advantage_diag_{n_actual}.jsonl")
    with open(jsonl_path, "w") as f:
        for r in results:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    print(f"\n[save] JSONL -> {jsonl_path}", flush=True)

    summary = compute_summary(results, args)
    summary["config"]["actual_n_prompts"] = n_actual
    summary["wall_seconds"] = time.time() - t_start
    summary_path = os.path.join(
        args.output_dir, "waveqa_advantage_diag_summary.json")
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)
    print(f"[save] Summary -> {summary_path}", flush=True)

    ks = summary["key_stats"]
    print(f"\n{'='*60}")
    print(f"  VERDICT: {summary['verdict']}")
    print(f"  std=0 groups: {ks['n_std0']}/{ks['n_total']} ({ks['pct_std0']})")
    print(f"  all-zero:     {ks['n_all_zero']}/{ks['n_total']} "
          f"({ks['pct_all_zero']})")
    print(f"  std>0 groups: {ks['n_std_pos']}/{ks['n_total']} "
          f"({ks['pct_std_pos']})")
    print(f"  submit rate:  {ks['overall_submit_rate']}")
    print(f"  reward mean={summary['overall_reward']['mean']:.4f} "
          f"std={summary['overall_reward']['std']:.4f}")
    print(f"  Total: {time.time()-t_start:.1f}s")
    print(f"{'='*60}")

    wall_s = time.time() - t_start
    html = generate_html_report(results, summary, args, wall_s)
    os.makedirs(args.report_dir, exist_ok=True)
    report_path = os.path.join(
        args.report_dir, "report_vision_wave_rl_advantage_diag_zh.html")
    with open(report_path, "w") as f:
        f.write(html)
    print(f"[save] HTML -> {report_path}", flush=True)
    print(f"[save] size: {os.path.getsize(report_path)} bytes", flush=True)


if __name__ == "__main__":
    sys.exit(main())
