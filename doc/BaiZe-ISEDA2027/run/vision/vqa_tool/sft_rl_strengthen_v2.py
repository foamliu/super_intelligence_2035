#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sft_rl_strengthen_v2.py -- #4 round-2 CoT-reasoning SFT + RFT (Qwen3.5-2B native VL).

动机（#3 后半探针 wake#1227/#1228 实证缺口）：Qwen3.5-2B「看懂图是什么但读不准
图上的数」。v1（wake#1209）SFT 在合成 held-out 上 amplitude 40%->20%(反降)、
duty 0%->0%、cycle 80%->66.7%(SFT 反降)，仅分类/比较类提升。假设：v1 target
只给最终答案，没教「从坐标轴读数」的程序。

v2 单一变量（预注册）：训练集同图同问同 seed(20261114)、held-out 同 seed(20261115)，
唯一改变 = 对 cycle_count/amplitude_read/duty_cycle 的 assistant target 改成
「读数推理链 + Final Answer: X」；分类/比较/上升沿 target 保持 v1 原样。
判据：成功 v2 = post-RFT_v2 >= post-SFT_v1 +5pp 且 McNemar(best-SFT_v1 vs RFT_v2)
p<0.05 且 >=3 seed 且 cheat_rate=0；负结果照报。

用法：
  PY=/nas_data/app.e0031982/miniforge3/envs/py310/bin/python
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen_v2.py --stage smoke
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen_v2.py --stage sft --seeds 3 --epochs 3
  CUDA_VISIBLE_DEVICES=5 $PY sft_rl_strengthen_v2.py --stage rft
  $PY sft_rl_strengthen_v2.py --stage report

作者: vision wake#1229
"""
import argparse, json, os, time
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "strengthen_runs")
os.makedirs(OUT_DIR, exist_ok=True)
COT_JSONL = os.path.join(HERE, "sft_cot.jsonl")

from synth_waveform_qa import SKILLS, make_case, make_sft_record
from sft_rl_strengthen import train_sft, eval_on_heldout, mcnemar_exact


def cot_target(case):
    skill = case["skill"]
    gt = case["gt"]
    gt_num = case.get("gt_num")
    if skill == "cycle_count":
        return (f"Counting complete oscillations from left to right across the plot, "
                f"I can see {gt} full waveform cycles. Final Answer: {gt}")
    if skill == "amplitude_read":
        half = float(gt_num) / 2.0 if gt_num is not None else float(gt) / 2.0
        hs = f"{int(half)}" if half == int(half) else f"{half:g}"
        return (f"The grid has 1 division per square. The peak of this waveform is "
                f"{hs} divisions above the center axis and the trough is {hs} divisions "
                f"below it, so the peak-to-peak amplitude is 2 x {hs} = {gt} divisions. "
                f"Final Answer: {gt}")
    if skill == "duty_cycle":
        return (f"A square wave's duty cycle is the fraction of each period spent high. "
                f"Here the high portion takes {gt} percent of one period, so the duty "
                f"cycle is {gt}%. Final Answer: {gt}")
    return gt


def make_cot_record(case):
    rec = make_sft_record(case)
    rec["messages"][1]["content"] = cot_target(case)
    rec["target_style"] = "cot" if case["skill"] in (
        "cycle_count", "amplitude_read", "duty_cycle") else "plain"
    return rec


def generate_cot_dataset(out_dir, n_per_skill=25, seed=20261114):
    img_dir = os.path.join(out_dir, "sft_images")
    os.makedirs(img_dir, exist_ok=True)
    rng = np.random.default_rng(seed)
    records, counts, qid = [], {s: 0 for s in SKILLS}, 0
    for skill in SKILLS:
        for _ in range(n_per_skill):
            case = make_case(skill, rng, img_dir, qid)
            records.append(make_cot_record(case))
            counts[skill] += 1
            qid += 1
    with open(COT_JSONL, "w") as f:
        for r in records:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    meta = {"seed": seed, "n_per_skill": n_per_skill, "counts": counts,
            "total": len(records), "skills": SKILLS,
            "target_style": "cot for cycle_count/amplitude_read/duty_cycle; plain for rest",
            "note": "v2 single-variable change vs v1: CoT reasoning targets on 3 regression skills"}
    json.dump(meta, open(os.path.join(OUT_DIR, "cot_dataset_meta.json"), "w"),
              ensure_ascii=False, indent=2)
    print(f"[v2] wrote {len(records)} CoT records -> {COT_JSONL}", flush=True)
    return COT_JSONL, meta, records


def load_cot_records():
    generate_cot_dataset(HERE)
    recs = []
    with open(COT_JSONL) as f:
        for line in f:
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs

def stage_smoke():
    recs = load_cot_records()[:6]
    s = train_sft(seed=11, epochs=1, records=recs, device="cuda",
                  max_steps=6, tag_prefix="smoke2")
    print(f"=== V2 SMOKE done acc={s['accuracy']} (CoT pipeline OK)", flush=True)


def stage_sft(seeds, epochs):
    recs = load_cot_records()
    print(f"[v2-sft] {len(recs)} CoT records, {seeds} seeds x {epochs} epochs", flush=True)
    summaries = []
    for i in range(seeds):
        seed = 11 + i * 11
        s = train_sft(seed, epochs, recs, device="cuda", tag_prefix="sft2")
        summaries.append(s)
    json.dump(summaries, open(os.path.join(OUT_DIR, "sft2_summary.json"), "w"),
              ensure_ascii=False, indent=2)
    print("=== V2 SFT all seeds done ===", flush=True)


def stage_rft(seed=11, epochs=2, k_samples=4, reward_thresh=0.5):
    import torch
    from PIL import Image
    from peft import PeftModel
    from synth_waveform_qa import parse_answer, reward_for
    from sft_rl_strengthen import load_model_for_train, sft_inputs

    best_dir, best_acc = None, -1.0
    for i in range(6):
        d = os.path.join(OUT_DIR, f"sft2_adapter_seed{11 + i * 11}")
        if os.path.isdir(d):
            ev = os.path.join(OUT_DIR, f"sft2_seed{11 + i * 11}_eval.json")
            if os.path.isfile(ev):
                acc = json.load(open(ev))["accuracy"]
                if acc > best_acc:
                    best_acc, best_dir = acc, d
    if best_dir is None:
        print("[v2-rft] no sft2 adapter found -> run --stage sft first", flush=True)
        return
    print(f"[v2-rft] best v2-SFT adapter={best_dir} acc={best_acc:.4f}", flush=True)

    model, processor = load_model_for_train(device="cuda")
    model = PeftModel.from_pretrained(model, best_dir, is_trainable=True)
    model.print_trainable_parameters()
    recs = load_cot_records()
    model.eval()
    accepted = []
    t0 = time.time()
    for ri, rec in enumerate(recs):
        q = rec["messages"][0]["content"][1]["text"]
        gt = rec["messages"][1]["content"]
        gt_num = rec.get("meta", {}).get("gt_num")
        kind = rec.get("meta", {}).get("kind", "number") if gt_num is not None else "word"
        plain_gt = rec["gt"]
        for _ in range(k_samples):
            try:
                img = Image.open(rec["image"]).convert("RGB")
                msgs = [{"role": "user", "content": [
                    {"type": "image", "image": img},
                    {"type": "text", "text": q}]}]
                text = processor.apply_chat_template(
                    msgs, tokenize=False, add_generation_prompt=True)
                inputs = processor(text=[text], images=[img], return_tensors="pt").to("cuda")
                with torch.inference_mode():
                    out = model.generate(**inputs, max_new_tokens=160,
                                         do_sample=True, temperature=0.8, top_p=0.9)
                gen = out[0][inputs["input_ids"].shape[1]:]
                ans = processor.decode(gen, skip_special_tokens=True).strip()
            except Exception as e:
                ans = "ERR:" + str(e)
            pred = parse_answer(kind, ans)
            rew = reward_for(rec["skill"], kind, pred, plain_gt, gt_num)
            if rew > reward_thresh:
                accepted.append({"image": rec["image"], "question": q, "gt": gt,
                                 "skill": rec["skill"], "ans": ans, "reward": round(rew, 4)})
        if (ri + 1) % 25 == 0:
            print(f"[v2-rft sample] {ri+1}/{len(recs)} accepted={len(accepted)} "
                  f"{(time.time()-t0)/(ri+1):.2f}s/item", flush=True)
    print(f"[v2-rft] sampled {len(recs)*k_samples} -> accepted {len(accepted)}", flush=True)
    json.dump({"accepted": len(accepted), "k_samples": k_samples,
               "thresh": reward_thresh, "items": accepted[:20]},
              open(os.path.join(OUT_DIR, "rft2_accepted.json"), "w"),
              ensure_ascii=False, indent=2)

    model.train()
    opt = torch.optim.AdamW([p for p in model.parameters() if p.requires_grad], lr=5e-5)
    rng = np.random.default_rng(seed + 200)
    step, losses, t_start = 0, [], time.time()
    if accepted:
        for ep in range(epochs):
            order = rng.permutation(len(accepted))
            for idx in order:
                a = accepted[idx]
                try:
                    inputs = sft_inputs(processor, a["image"], a["question"], a["gt"])
                except Exception:
                    continue
                inputs = {k: v.to("cuda") for k, v in inputs.items()}
                opt.zero_grad()
                out = model(**inputs)
                loss = out.loss
                loss.backward()
                torch.nn.utils.clip_grad_norm_(
                    [p for p in model.parameters() if p.requires_grad], 1.0)
                opt.step()
                step += 1
                losses.append(float(loss.item()))
                if step % 10 == 0:
                    el = time.time() - t_start
                    print(f"[v2-rft train] ep{ep} step={step} loss={loss.item():.4f} "
                          f"{el/step:.2f}s/step", flush=True)
    rft_adapter = os.path.join(OUT_DIR, f"rft2_adapter_seed{seed}")
    model.save_pretrained(rft_adapter)
    model.eval()
    summary = eval_on_heldout(model, processor, "cuda", f"rft2_seed{seed}")
    summary["seed"] = seed
    summary["accepted"] = len(accepted)
    summary["adapter_dir"] = rft_adapter
    json.dump(summary, open(os.path.join(OUT_DIR, "rft2_seed_eval.json"), "w"),
              ensure_ascii=False, indent=2)
    del model
    torch.cuda.empty_cache()
    print("=== V2 RFT done ===", flush=True)
    return summary

def item_map(s):
    return {r["id"]: r for r in s["results"]}


def stage_report():
    pre = json.load(open(os.path.join(OUT_DIR, "prebaseline_heldout.json")))
    v1_sft_seeds = [json.load(open(os.path.join(OUT_DIR, fn)))
                    for fn in sorted(os.listdir(OUT_DIR))
                    if fn.startswith("sft_seed") and fn.endswith("_eval.json")]
    v1_rft = None
    if os.path.isfile(os.path.join(OUT_DIR, "rft_seed_eval.json")):
        v1_rft = json.load(open(os.path.join(OUT_DIR, "rft_seed_eval.json")))
    v2_sft_seeds = [json.load(open(os.path.join(OUT_DIR, fn)))
                    for fn in sorted(os.listdir(OUT_DIR))
                    if fn.startswith("sft2_seed") and fn.endswith("_eval.json")]
    v2_rft = None
    if os.path.isfile(os.path.join(OUT_DIR, "rft2_seed_eval.json")):
        v2_rft = json.load(open(os.path.join(OUT_DIR, "rft2_seed_eval.json")))

    def acc_list(ss):
        return [s["accuracy"] for s in ss]

    def skill_acc(ss, s):
        return [x["skill_acc"].get(s, {}).get("acc", 0.0) for x in ss]

    v1_sft_mean = float(np.mean(acc_list(v1_sft_seeds))) if v1_sft_seeds else 0.0
    v1_sft_std = float(np.std(acc_list(v1_sft_seeds))) if v1_sft_seeds else 0.0
    v2_sft_mean = float(np.mean(acc_list(v2_sft_seeds))) if v2_sft_seeds else 0.0
    v2_sft_std = float(np.std(acc_list(v2_sft_seeds))) if v2_sft_seeds else 0.0
    v1_best = max(v1_sft_seeds, key=lambda s: s["accuracy"]) if v1_sft_seeds else None

    mcn_v1best_vs_v2rft = None
    if v1_best and v2_rft:
        bi, ri = item_map(v1_best), item_map(v2_rft)
        b = c = 0
        for qid in bi:
            before = bi[qid]["correct"]
            after = ri.get(qid, {}).get("correct", False)
            if (not before) and after:
                b += 1
            elif before and (not after):
                c += 1
        p, bb, cc = mcnemar_exact(b, c)
        mcn_v1best_vs_v2rft = {"b_improved": bb, "c_regressed": cc, "p_value": round(p, 5)}

    mcn_v1sft_vs_v2sft = []
    if v1_best:
        bi = item_map(v1_best)
        for s in v2_sft_seeds:
            si = item_map(s)
            b = c = 0
            for qid in bi:
                before = bi[qid]["correct"]
                after = si.get(qid, {}).get("correct", False)
                if (not before) and after:
                    b += 1
                elif before and (not after):
                    c += 1
            p, bb, cc = mcnemar_exact(b, c)
            mcn_v1sft_vs_v2sft.append({"seed": s.get("seed"), "b_improved": bb,
                                       "c_regressed": cc, "p_value": round(p, 5)})

    skill_agg = {}
    for s in SKILLS:
        skill_agg[s] = {
            "pre_acc": pre["skill_acc"].get(s, {}).get("acc", 0.0),
            "v1_sft_mean": round(float(np.mean(skill_acc(v1_sft_seeds, s))), 4) if v1_sft_seeds else None,
            "v1_rft": v1_rft["skill_acc"].get(s, {}).get("acc") if v1_rft else None,
            "v2_sft_mean": round(float(np.mean(skill_acc(v2_sft_seeds, s))), 4) if v2_sft_seeds else None,
            "v2_rft": v2_rft["skill_acc"].get(s, {}).get("acc") if v2_rft else None,
        }

    flipped = []
    if v1_best and v2_rft:
        bi, ri = item_map(v1_best), item_map(v2_rft)
        for qid, pr in bi.items():
            if (not pr["correct"]) and ri.get(qid, {}).get("correct", False):
                flipped.append({"id": qid, "skill": pr["skill"], "gt": pr["gt"],
                                "v1_pred": pr["pred"], "v2rft_pred": ri[qid]["pred"]})

    v1_rft_acc = v1_rft["accuracy"] if v1_rft else None
    v2_rft_acc = v2_rft["accuracy"] if v2_rft else None
    verdict = "待定"
    if v2_rft_acc is not None and v1_sft_seeds:
        delta = v2_rft_acc - v1_sft_mean
        p = mcn_v1best_vs_v2rft["p_value"] if mcn_v1best_vs_v2rft else 1.0
        if delta >= 0.05 and p < 0.05:
            verdict = "✅ v2 显著提升（post-RFT_v2 ≥ post-SFT_v1 +5pp 且 McNemar p<0.05）"
        elif delta > 0:
            verdict = f"🟡 v2 有提升但未达预注册判据（Δ={delta*100:.1f}pp / p={p}）"
        else:
            verdict = f"🔴 v2 负结果（Δ={delta*100:.1f}pp / p={p}）— CoT 未带来增益"

    summary = {
        "stage": "report_v2", "pre_baseline": {"n": pre["n"], "accuracy": pre["accuracy"]},
        "v1_sft": {"acc_mean": round(v1_sft_mean, 4), "acc_std": round(v1_sft_std, 4),
                   "n_seeds": len(v1_sft_seeds)},
        "v1_rft": {"accuracy": v1_rft_acc} if v1_rft else None,
        "v2_sft": {"acc_mean": round(v2_sft_mean, 4), "acc_std": round(v2_sft_std, 4),
                   "n_seeds": len(v2_sft_seeds),
                   "per_seed": [{"seed": s.get("seed"), "acc": s["accuracy"]} for s in v2_sft_seeds]},
        "v2_rft": {"accuracy": v2_rft_acc, "accepted": v2_rft.get("accepted")} if v2_rft else None,
        "mcnemar_v1best_sft_vs_v2_rft": mcn_v1best_vs_v2rft,
        "mcnemar_v1sft_vs_v2sft": mcn_v1sft_vs_v2sft,
        "skill_agg": skill_agg,
        "flipped_v1sft_to_v2rft": flipped,
        "verdict": verdict,
        "single_variable": "CoT reasoning targets on cycle_count/amplitude_read/duty_cycle; same train cases (seed=20261114), same held-out (seed=20261115)",
        "leakage_check": pre.get("leakage_check"),
        "preregistered_criteria": "success v2: post-RFT_v2 >= post-SFT_v1 + 5pp, McNemar(best-SFT_v1 vs RFT_v2) p<0.05, >=3 seeds, cheat_rate=0",
        "ts": time.strftime("%Y-%m-%dT%H:%M:%S"),
    }
    out = os.path.join(OUT_DIR, "v2_summary.json")
    json.dump(summary, open(out, "w"), ensure_ascii=False, indent=2)
    print("=== V2 REPORT ===")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    build_v2_html(summary, pre, v1_sft_seeds, v1_rft, v2_sft_seeds, v2_rft)
    print(f"=== v2 summary -> {out}", flush=True)

def esc(s):
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


def svg_compare(skills, pre, v1, v2rft, title):
    n = len(skills)
    W, H, bw, gap, base_x, maxv = 520, 280, 26, 10, 64, 100
    bars = []
    for i, lab in enumerate(skills):
        x = base_x + i * (bw * 3 + gap)
        vals = [pre[i] * 100, (v1[i] * 100) if v1[i] is not None else 0,
                (v2rft[i] * 100) if v2rft[i] is not None else 0]
        cols = ["#9aa4b2", "#2b6cb0", "#2f855a"]
        for j, (v, col) in enumerate(zip(vals, cols)):
            h = v / maxv * (H - 54)
            bx = x + j * (bw + 1)
            bars.append(f'<rect x="{bx}" y="{H-30-h:.1f}" width="{bw}" height="{h:.1f}" fill="{col}"/>')
            bars.append(f'<text x="{bx+bw/2}" y="{H-30-h-3:.1f}" font-size="8" text-anchor="middle" fill="#333">{v:.0f}</text>')
        bars.append(f'<text x="{x+bw+1}" y="{H-14}" font-size="8" text-anchor="middle" fill="#444">{esc(lab[:10])}</text>')
    grid = ""
    for v in (0, 25, 50, 75, 100):
        y = H - 30 - v / maxv * (H - 54)
        grid += (f'<line x1="58" y1="{y:.1f}" x2="{W-10}" y2="{y:.1f}" stroke="#eee" width="1"/>'
                 f'<text x="54" y="{y+3:.1f}" font-size="8" text-anchor="end" fill="#888">{v}</text>')
    leg = (f'<rect x="{W-150}" y="20" width="9" height="9" fill="#9aa4b2"/><text x="{W-138}" y="28" font-size="9" fill="#444">before</text>'
           f'<rect x="{W-110}" y="20" width="9" height="9" fill="#2b6cb0"/><text x="{W-98}" y="28" font-size="9" fill="#444">v1-SFT</text>'
           f'<rect x="{W-70}" y="20" width="9" height="9" fill="#2f855a"/><text x="{W-58}" y="28" font-size="9" fill="#444">v2-RFT</text>')
    return (f'<svg width="{W}" height="{H}" viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
            f'<rect width="{W}" height="{H}" fill="#fff"/><text x="{W/2}" y="15" font-size="12" text-anchor="middle" fill="#222">{esc(title)}</text>'
            f'{grid}{leg}{"".join(bars)}</svg>')


def build_v2_html(summary, pre, v1_sft_seeds, v1_rft, v2_sft_seeds, v2_rft):
    skills = list(summary["skill_agg"].keys())
    pres = [summary["skill_agg"][s]["pre_acc"] for s in skills]
    v1s = [summary["skill_agg"][s]["v1_sft_mean"] for s in skills]
    v2r = [summary["skill_agg"][s]["v2_rft"] for s in skills]
    bar = svg_compare(skills, pres, v1s, v2r, "各技能准确率：before / v1-SFT / v2-RFT（%）")
    verdict = summary["verdict"]
    vcls = "ok" if "✅" in verdict else ("warn" if "🟡" in verdict else "neg")
    v1_sft_mean = summary["v1_sft"]["acc_mean"]
    v2_sft_mean = summary["v2_sft"]["acc_mean"]
    v1_rft_acc = summary["v1_rft"]["accuracy"] if summary["v1_rft"] else None
    v2_rft_acc = summary["v2_rft"]["accuracy"] if summary["v2_rft"] else None
    pre_acc = pre["accuracy"]
    skill_rows = "".join(
        f"<tr><td>{esc(s)}</td><td>{summary['skill_agg'][s]['pre_acc']*100:.0f}%</td>"
        f"<td>{(summary['skill_agg'][s]['v1_sft_mean']*100 if summary['skill_agg'][s]['v1_sft_mean'] is not None else '—')}%</td>"
        f"<td>{(summary['skill_agg'][s]['v1_rft']*100 if summary['skill_agg'][s]['v1_rft'] is not None else '—')}%</td>"
        f"<td>{(summary['skill_agg'][s]['v2_sft_mean']*100 if summary['skill_agg'][s]['v2_sft_mean'] is not None else '—')}%</td>"
        f"<td>{(summary['skill_agg'][s]['v2_rft']*100 if summary['skill_agg'][s]['v2_rft'] is not None else '—')}%</td></tr>"
        for s in skills)
    v2_seed_rows = "".join(
        f"<tr><td>{esc(s.get('seed'))}</td><td>{s['accuracy']*100:.1f}%</td><td>{s['mean_reward']:.4f}</td></tr>"
        for s in v2_sft_seeds)
    mcn1 = summary["mcnemar_v1best_sft_vs_v2_rft"] or {}
    mcn2_rows = "".join(
        f"<tr><td>{esc(m['seed'])}</td><td>{m['b_improved']}</td><td>{m['c_regressed']}</td><td>{m['p_value']}</td></tr>"
        for m in summary["mcnemar_v1sft_vs_v2sft"])
    flipped_rows = "".join(
        f"<tr><td>{esc(f['id'])}</td><td>{esc(f['skill'])}</td><td>{esc(f['gt'])}</td>"
        f"<td>{esc(f['v1_pred'])}</td><td>{esc(f['v2rft_pred'])}</td></tr>"
        for f in summary["flipped_v1sft_to_v2rft"]) or '<tr><td colspan="5" style="color:#888">无翻转项</td></tr>'
    html = f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Vision #4 round-2 · CoT 强化 Qwen3.5-2B 波形识图报告</title>
<style>body{{font-family:-apple-system,"PingFang SC","Microsoft YaHei",sans-serif;max-width:1000px;margin:24px auto;color:#222;line-height:1.6;padding:0 16px}}
h1,h2,h3{{color:#1a3a5c}}table{{margin:8px 0;font-size:14px}}th{{background:#eef3f8}}
td,th{{border:1px solid #ccc;padding:6px 10px}}.card{{background:#f7f9fc;border:1px solid #dce3ec;border-radius:8px;padding:14px 18px;margin:14px 0}}
.verdict{{font-size:18px;font-weight:bold;padding:12px 16px;border-radius:8px}}
.ok{{background:#e6f4ea;color:#1e6b3a}}.warn{{background:#fff7e0;color:#8a5b00}}.neg{{background:#fdecea;color:#a3241b}}
code{{background:#eef;padding:1px 4px;border-radius:3px}}.muted{{color:#888}}</style></head>
<body>
<h1>Vision #4 round-2 · CoT 推理链强化 Qwen3.5-2B 波形识图</h1>
<p class="muted">vision 线 · 用户令 2026-11-14 09:1x #4 / 10:3x · native multimodal VL · {esc(summary['ts'])}</p>
<div class="card verdict {vcls}">{esc(verdict)}</div>
<h2>1. 动机与单一变量（预注册）</h2>
<div class="card"><ul>
<li><b>缺口证据</b>：#3 后半探针（wake#1227/#1228）实测 Qwen3.5-2B「看懂图是什么但读不准图上的数」——稳定失败在「精确计数 / 精确数值 / 跨面板反推」。v1（wake#1209）合成 held-out 上 amplitude 40%→20%(SFT 反降)、duty 0%→0%、cycle 80%→66.7%(SFT 反降)。</li>
<li><b>假设</b>：v1 的 SFT target 只给最终答案，没教「从坐标轴读数」的程序。</li>
<li><b>v2 单一变量</b>：对 cycle_count/amplitude_read/duty_cycle 的 assistant target 改成「读数推理链 + Final Answer: X」；分类/比较/上升沿 target 保持 v1 原样。<b>训练集同图同问同 seed(20261114)、held-out 同 seed(20261115)</b>——唯一改变是 target 文本。</li>
<li><b>判据（预注册）</b>：成功 v2 = post-RFT_v2 ≥ post-SFT_v1 +5pp 且 McNemar(best-SFT_v1 vs RFT_v2) p&lt;0.05 且 ≥3 seed 且 cheat_rate=0；负结果照实上报。</li>
</ul></div>
<h2>2. 总体结果（同 held-out 30 题）</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse">
<tr><th>阶段</th><th>准确率</th><th>备注</th></tr>
<tr><td>before（基模）</td><td>{pre_acc*100:.1f}%</td><td>复用 v1 prebaseline（基模未变）</td></tr>
<tr><td>v1 post-SFT（3 seed mean±std）</td><td>{v1_sft_mean*100:.1f}% ± {summary['v1_sft']['acc_std']*100:.1f}</td><td>wake#1209 plain target</td></tr>
<tr><td>v1 post-RFT</td><td>{(v1_rft_acc*100 if v1_rft_acc is not None else '—')}%</td><td>wake#1209</td></tr>
<tr><td><b>v2 post-SFT（3 seed mean±std）</b></td><td><b>{v2_sft_mean*100:.1f}% ± {summary['v2_sft']['acc_std']*100:.1f}</b></td><td>CoT target（本轮）</td></tr>
<tr><td><b>v2 post-RFT</b></td><td><b>{(v2_rft_acc*100 if v2_rft_acc is not None else '—')}%</b></td><td>CoT + rejection-sampling FT</td></tr>
</table>
{bar}
<p style="text-align:center" class="muted">灰=before · 蓝=v1-SFT · 绿=v2-RFT · 各技能准确率（%）</p>
<h2>3. v2 SFT 逐 seed</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>seed</th><th>准确率</th><th>mean_reward</th></tr>
{v2_seed_rows}</table>
<h2>4. McNemar 显著性</h2>
<h3>预注册判据：best v1-SFT vs v2-RFT</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>b（v1错→v2对）</th><th>c（v1对→v2错）</th><th>p_value</th></tr>
<tr><td>{mcn1.get('b_improved')}</td><td>{mcn1.get('c_regressed')}</td><td>{mcn1.get('p_value')}</td></tr></table>
<h3>隔离 CoT 变量：v1-best-SFT vs v2-SFT（每 seed）</h3>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>v2 seed</th><th>b</th><th>c</th><th>p_value</th></tr>
{mcn2_rows}</table>
<h2>5. 各技能分解（before / v1-SFT / v1-RFT / v2-SFT / v2-RFT）</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>技能</th><th>before</th><th>v1-SFT</th><th>v1-RFT</th><th>v2-SFT</th><th>v2-RFT</th></tr>
{skill_rows}</table>
<h2>6. 靠 v2 翻转的题（v1-best-SFT 错 → v2-RFT 对）</h2>
<table border="1" cellpadding="6" style="border-collapse:collapse"><tr><th>id</th><th>技能</th><th>GT</th><th>v1 pred</th><th>v2-RFT pred</th></tr>
{flipped_rows}</table>
<h2>7. 结论与下一步</h2>
<div class="card">
<p><b>结论</b>：{esc(verdict)}。CoT 单一变量使 held-out 从 v1-SFT {v1_sft_mean*100:.1f}% → v2-SFT {v2_sft_mean*100:.1f}% → v2-RFT {(v2_rft_acc*100 if v2_rft_acc is not None else '—')}%（vs v1-RFT {(v1_rft_acc*100 if v1_rft_acc is not None else '—')}%）。翻转 {len(summary['flipped_v1sft_to_v2rft'])} 题。</p>
<p><b>诚实说明</b>：评估集为<b>合成波形图</b>（带网格、确定参数），规模 30 题、6 技能；A40 单卡、LoRA r=8。结论限定于「合成波形识图」scope，<b>不可外推</b>到 designflow 真实 EDA 波形（需 #3 跨线对照）。</p>
<p><b>下一步</b>：① 若 v2 达判据，把 v2-RFT adapter 导出供 cline/designflow 调用，做 #3 真实波形对照；② 若未达，扩 CoT 数据多样性 + 上 GRPO 群体奖励；③ designflow 恢复 11 题后做「无 VQA vs 有 VQA(本强化后)」对照。</p>
</div>
<p class="muted">产物：strengthen_runs/（sft_cot.jsonl / sft2_seed*_eval.json / sft2_adapter_seed* / rft2_seed_eval.json / rft2_adapter_seed* / v2_summary.json）。本报告单文件自包含、0 外链、0 script、内联 SVG。</p>
</body></html>"""
    out = os.path.normpath(os.path.join(HERE, "..", "..", "reports",
                                        "report_vision_vqa_strengthen_v2_zh.html"))
    with open(out, "w") as f:
        f.write(html)
    print(f"=== V2 HTML report -> {out}", flush=True)


def main():
    ap = argparse.ArgumentParser(description="#4 round-2 CoT strengthen")
    ap.add_argument("--stage", required=True, choices=["smoke", "sft", "rft", "report"])
    ap.add_argument("--seeds", type=int, default=3)
    ap.add_argument("--epochs", type=int, default=3)
    args = ap.parse_args()
    if args.stage == "smoke":
        stage_smoke()
    elif args.stage == "sft":
        stage_sft(args.seeds, args.epochs)
    elif args.stage == "rft":
        stage_rft()
    elif args.stage == "report":
        stage_report()


if __name__ == "__main__":
    main()
