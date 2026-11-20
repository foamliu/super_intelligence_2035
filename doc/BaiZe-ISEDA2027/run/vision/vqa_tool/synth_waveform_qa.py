#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""synth_waveform_qa.py -- 合成「波形图-问答对」数据管线 + 基模能力自测基线（#4）。

vision 用户令 2026-11-14 10:3x · #4「准备训练/合成数据管线，先用合成数据自测能力基线」：
  (a) 合成波形图-问答对（带网格的 PNG + 问题 + GT 答案）—— 网格是关键，VLM 才能「数格读数」；
  (b) SFT 数据格式：Qwen3.5-2B VL 的多模态 chat JSONL（image + text + assistant）；
  (c) RL 奖励设计（连续化 exp(-rel_err/tau) + 二值 + group_std 零信号检测）+ 预注册判据；
  (d) 自测基线：用合成评估集查询【本机常驻的 native multimodal VQA server】
      （qwen35_vqa_server.py，GPU5:30001），落 baseline JSON —— 这是 #4 SFT/RL 前的底数。

⚠️ 架构口径（重要）：Qwen3.5-2B 是**原生多模态 VL 模型**（`Qwen3_5ForConditionalGeneration`，
config 含 `image_token_id`），**直接吃像素**。本管线因此把图喂给 VLM，**不做**「图→文本桥」降级
（用户 09:5x 令明确反对把视觉判断降级为脚本/文本）。文本桥会把「看图」偷换成「读数」，
无法度量多模态增益。#4 目标是强化基模「看图」能力，必须走原生视觉路径。

任务类型（6 种，覆盖 waveview α/β 识图技能）：
  1. type_classification : sine/square/triangle/sawtooth 哪个 -> type 名   （二值）
  2. cycle_count         : 几个完整周期 -> 整数                           （回归）
  3. amplitude_read      : 峰峰值几格 -> 整数                             （回归）
  4. freq_comparison     : A/B 哪个频率高 -> A/B                         （二值）
  5. duty_cycle          : 方波占空比 -> 百分比                           （回归）
  6. rise_edge           : 上升沿 sharp/gradual -> 词                    （二值）

RL 奖励（预注册，写在 REWARD_* 函数；🚫 禁止看结果再调判据）：
  - 回归：R = exp(-rel_err/tau)，rel_err=|pred-gt|/|gt|，tau=0.15（与 v11 TOL 对齐）
        -> 连续平滑，消除 v2-v11「全同档=无信号」病灶
  - 二值：R = 1.0/0.0（精确匹配，本任务天然可判）
  - 群体：group_std(rewards)；为 0 则该组 advantage=0（v2-v4 病灶检测）

预注册判据（实验前定，不许事后改）：
  - 成功：post-RL >= post-SFT + 5pp，McNemar p<0.05，>=3 seeds 一致，cheat_rate=0
  - 负结果同样上报；连续 3 轮无提升换方向。

作者: vision wake#1208 · project-internal
"""
import argparse
import json
import math
import os
import time

import numpy as np
from PIL import Image, ImageDraw  # noqa: F401  (基线 new_canvas 内部用)

# 复用已验证的基线组件：网格画布、绘制、稳健答案抽取、HTTP 查询
from baseline_waveform_vqa import (
    new_canvas, draw_signal, sine_image, square_image, two_sine_image,
    rise_edge_image, extract_final, vqa,
)

HERE = os.path.dirname(os.path.abspath(__file__))
SERVER = os.environ.get("QWEN35_VQA_SERVER", "http://127.0.0.1:30001")
WAVEFORM_TYPES = ["sine", "square", "triangle", "sawtooth"]
TAU = 0.15  # 连续奖励温度（与 v11 TOL 对齐）
SKILLS = ["type_classification", "cycle_count", "amplitude_read",
          "freq_comparison", "duty_cycle", "rise_edge"]


# --- 图像生成器（基线已有 sine/square/two_sine/rise，这里补 triangle/sawtooth） --- #
def triangle_image(path, cycles, amp_div=3.0):
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    pts = []
    for x in range(x0, x1):
        t = (x - x0) / (x1 - x0)
        ph = (cycles * t) % 1.0
        y = mid - amp_div * 40 * (4.0 * ph - 1.0 if ph < 0.5 else 3.0 - 4.0 * ph)
        pts.append((x, y))
    draw_signal(d, pts)
    img.save(path)


def sawtooth_image(path, cycles, amp_div=3.0):
    img, d = new_canvas()
    x0, x1, mid = 40, 465, 130
    pts = []
    for x in range(x0, x1):
        t = (x - x0) / (x1 - x0)
        y = mid - amp_div * 40 * (2.0 * ((cycles * t) % 1.0) - 1.0)
        pts.append((x, y))
    draw_signal(d, pts)
    img.save(path)


def render_for_type(path, wtype, cycles, amp_div=3.0, duty=0.5):
    if wtype == "sine":
        sine_image(path, cycles, amp_div)
    elif wtype == "square":
        square_image(path, cycles, duty, amp_div)
    elif wtype == "triangle":
        triangle_image(path, cycles, amp_div)
    elif wtype == "sawtooth":
        sawtooth_image(path, cycles, amp_div)
    else:
        raise ValueError(wtype)


# --- 题目构造（随机参数 + GT + 问题 + 抽取类型） --- #
def _int_cycles(rng):
    return int(rng.integers(2, 6))  # 2..5 个完整周期，便于 VLM 计数


def make_case(skill, rng, img_dir, qid):
    """造一道题：渲染图、返回 case dict（含 image/gt/question/kind）。"""
    os.makedirs(img_dir, exist_ok=True)
    p = os.path.join(img_dir, f"q{qid}.png")
    if skill == "type_classification":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = _int_cycles(rng)
        render_for_type(p, wt, cyc)
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "Which waveform type is this: sine, square, "
                            "triangle, or sawtooth? Answer with the single type name.",
                "gt": wt, "kind": "word_type"}
    if skill == "cycle_count":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = _int_cycles(rng)
        render_for_type(p, wt, cyc)
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "How many complete waveform cycles are shown? "
                            "Answer with just a number.",
                "gt": str(cyc), "kind": "number", "gt_num": float(cyc)}
    if skill == "amplitude_read":
        wt = WAVEFORM_TYPES[int(rng.integers(0, len(WAVEFORM_TYPES)))]
        cyc = _int_cycles(rng)
        amp = float(rng.choice([2.0, 2.5, 3.0, 3.5]))  # 峰值格数
        render_for_type(p, wt, cyc, amp_div=amp)
        pp = 2.0 * amp  # 峰峰值（格）
        return {"id": f"q{qid}", "skill": skill, "image": p, "wtype": wt,
                "question": "What is the peak-to-peak amplitude of this waveform, "
                            "in vertical grid divisions (each grid square = 1 division)? "
                            "Answer with a number.",
                "gt": str(int(round(pp))), "kind": "number", "gt_num": float(pp)}
    if skill == "freq_comparison":
        ca, cb = _int_cycles(rng), _int_cycles(rng)
        while abs(ca - cb) < 1:  # 保证差至少 1 个周期，可判
            cb = _int_cycles(rng)
        two_sine_image(p, ca, cb)
        gt = "A" if ca > cb else "B"
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "Signal A (blue, top) and signal B (red, bottom) are shown. "
                            "Which signal has the HIGHER frequency? Answer A or B.",
                "gt": gt, "kind": "ab"}
    if skill == "duty_cycle":
        duty = float(rng.choice([0.25, 0.5, 0.75]))
        cyc = _int_cycles(rng)
        square_image(p, cyc, duty)
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "What is the duty cycle of this square wave "
                            "(high-time / period)? Answer as a percentage.",
                "gt": f"{int(round(duty * 100))}", "kind": "percent",
                "gt_num": float(duty * 100)}
    if skill == "rise_edge":
        slow = bool(rng.integers(0, 2))
        rise_edge_image(p, slow=slow)
        return {"id": f"q{qid}", "skill": skill, "image": p,
                "question": "Is the rising edge of this signal sharp "
                            "(near-vertical) or gradual (sloped)? "
                            "Answer 'sharp' or 'gradual'.",
                "gt": "gradual" if slow else "sharp", "kind": "word_rise"}
    raise ValueError(skill)


# --- 答案抽取 + 评分（自测基线用） --- #
def parse_answer(kind, answer):
    if kind == "word_type":
        low = answer.strip().lower()
        for w in WAVEFORM_TYPES:
            if w in low:
                return w
        return ""
    if kind == "word_rise":
        low = answer.strip().lower()
        for kw in ("sharp", "vertical", "gradual", "sloped"):
            if kw in low:
                return "sharp" if kw in ("sharp", "vertical") else "gradual"
        return ""
    if kind == "ab":
        return extract_final(answer, "ab")
    if kind == "percent":
        return extract_final(answer, "percent")
    if kind == "number":
        return extract_final(answer, "number")
    return answer.strip()


def is_correct(skill, kind, pred, gt, gt_num=None):
    """精确匹配（分类/比较/计数/占空比/幅值整数格）。"""
    if pred is None or pred == "":
        return False
    if kind in ("word_type", "word_rise", "ab"):
        return str(pred).strip().lower() == str(gt).strip().lower()
    if kind in ("number", "percent"):
        try:
            return abs(float(pred) - float(gt_num)) < 1e-6
        except (TypeError, ValueError):
            return False
    return False


# --- RL 奖励（预注册） --- #
def reward_regression(pred, gt_num, tau=TAU):
    try:
        p = float(pred)
    except (TypeError, ValueError):
        return 0.0
    if gt_num == 0:
        return 0.0
    return float(math.exp(-abs(p - gt_num) / abs(gt_num) / tau))


def reward_for(skill, kind, pred, gt, gt_num=None):
    if kind in ("number", "percent"):
        return reward_regression(pred, gt_num)
    return 1.0 if is_correct(skill, kind, pred, gt, gt_num) else 0.0


def group_std(rewards):
    if len(rewards) < 2:
        return 0.0
    return float(np.std(rewards))


# --- SFT 记录（Qwen3.5-2B VL 多模态 chat 格式） --- #
def make_sft_record(case):
    """一条多模态 SFT 记录：user=[image,text] / assistant=gt。"""
    img_uri = "file://" + os.path.abspath(case["image"])
    return {
        "id": case["id"], "skill": case["skill"],
        "image": os.path.abspath(case["image"]), "gt": case["gt"],
        "messages": [
            {"role": "user", "content": [
                {"type": "image", "image": img_uri},
                {"type": "text", "text": case["question"]},
            ]},
            {"role": "assistant", "content": case["gt"]},
        ],
        "meta": {k: case[k] for k in ("wtype", "kind", "gt_num") if k in case},
    }


# --- 主入口 --- #
def generate_dataset(out_dir, n_per_skill=25, seed=20261114):
    """生成 SFT 数据集：图像 + sft.jsonl + manifest。确定性（seed 固定）。"""
    img_dir = os.path.join(out_dir, "sft_images")
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    records, counts, qid = [], {s: 0 for s in SKILLS}, 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            case = make_case(skill, rng, img_dir, qid)
            records.append(make_sft_record(case))
            counts[skill] += 1
            qid += 1
    sft_path = os.path.join(out_dir, "sft.jsonl")
    with open(sft_path, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {"seed": seed, "n_per_skill": n_per_skill, "counts": counts,
            "total": len(records), "skills": SKILLS, "tau": TAU,
            "waveform_types": WAVEFORM_TYPES}
    json.dump(meta, open(os.path.join(out_dir, "dataset_meta.json"), "w"),
              ensure_ascii=False, indent=2)
    return sft_path, meta, records


def run_selftest(out_dir, n_per_skill=2, seed=20261114, server=SERVER):
    """生成小评估集 -> 查 VQA server -> 落 baseline JSON（#4 底数）。"""
    img_dir = os.path.join(out_dir, "selftest_images")
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    cases, qid = [], 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            cases.append(make_case(skill, rng, img_dir, qid))
            qid += 1
    results, correct, rewards_by_skill = [], 0, {s: [] for s in SKILLS}
    for c in cases:
        res = vqa(c["image"], c["question"])
        if not res.get("ok"):
            results.append({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                            "answer": "ERR:" + str(res.get("error")), "pred": "",
                            "correct": False, "reward": 0.0,
                            "latency_s": res.get("latency_s")})
            rewards_by_skill[c["skill"]].append(0.0)
            continue
        ans = res.get("answer", "")
        pred = parse_answer(c["kind"], ans)
        ok = is_correct(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
        rew = reward_for(c["skill"], c["kind"], pred, c["gt"], c.get("gt_num"))
        correct += int(ok)
        rewards_by_skill[c["skill"]].append(rew)
        results.append({"id": c["id"], "skill": c["skill"], "image": c["image"],
                        "question": c["question"], "gt": c["gt"], "answer": ans,
                        "pred": pred, "correct": ok, "reward": round(rew, 4),
                        "latency_s": res.get("latency_s")})
        print(json.dumps({"id": c["id"], "skill": c["skill"], "gt": c["gt"],
                          "pred": pred, "correct": ok, "reward": round(rew, 4)},
                         ensure_ascii=False), flush=True)
    by_skill = {}
    for s in SKILLS:
        rs = [r for r in results if r["skill"] == s]
        by_skill[s] = {
            "n": len(rs), "correct": sum(r["correct"] for r in rs),
            "acc": round(sum(r["correct"] for r in rs) / max(1, len(rs)), 4),
            "mean_reward": round(float(np.mean(rewards_by_skill[s])), 4)
            if rewards_by_skill[s] else 0.0}
    summary = {"server": server, "model": "Qwen3.5-2B (native VL)",
               "n": len(results), "correct": correct,
               "accuracy": round(correct / max(1, len(results)), 4),
               "mean_reward": round(float(np.mean([r["reward"] for r in results])), 4),
               "skill_acc": by_skill, "tau": TAU, "skills": SKILLS,
               "ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "results": results,
               "note": "pre-SFT/RL baseline on synthetic waveform images; native "
                       "multimodal path (no image->text bridge). Same image/question "
                       "distribution reused for post-SFT/RL paired comparison (#4).",
               "preregistered_criteria": "success: post-RL >= post-SFT + 5pp, "
                                         "McNemar p<0.05, >=3 seeds, cheat_rate=0; "
                                         "negative results reported honestly."}
    out = os.path.join(out_dir, "synth_selftest_baseline.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print(f"=== SELFTEST n={summary['n']} correct={correct} "
          f"acc={summary['accuracy']} mean_reward={summary['mean_reward']} -> {out}",
          flush=True)
    return out, summary


def main():
    ap = argparse.ArgumentParser(description="Synthetic waveform-image QA pipeline (#4)")
    ap.add_argument("--out_dir", default=HERE)
    ap.add_argument("--n_per_skill", type=int, default=25,
                    help="SFT 集每技能题数（自测用 --selftest 覆盖）")
    ap.add_argument("--seed", type=int, default=20261114)
    ap.add_argument("--selftest", action="store_true",
                    help="生成小评估集并查 VQA server，落 baseline JSON")
    ap.add_argument("--selftest_n", type=int, default=2)
    ap.add_argument("--server", default=SERVER)
    args = ap.parse_args()
    if args.selftest:
        run_selftest(args.out_dir, n_per_skill=args.selftest_n,
                     seed=args.seed, server=args.server)
    else:
        sft_path, meta, _ = generate_dataset(
            args.out_dir, n_per_skill=args.n_per_skill, seed=args.seed)
        print("sft:", sft_path)
        print("meta:", json.dumps(meta, ensure_ascii=False))


if __name__ == "__main__":
    main()
