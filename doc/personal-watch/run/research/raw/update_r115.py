#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十五轮（本地 2026-10-27 06:00 AM「早 3」轮 · 新一日 AM）结果落盘。

- **公告批次未刷新**：仍 `2026-10-23`（`cat:cs.CL` 探针 `totalResults=123669` 与 r114 相同、
  最新样本 `published=2026-10-23T17:59:56Z`；广度扫描 637936）。`--fetch --seen`
  （`window_mode=daily` 72h，`generated=2026-10-26T22:01:24Z`）**15/15 查询 200、全部 attempts=1**、
  **kept 0 / dropped 600**（600 = 563 already in SEEN + 37 stale > 72h）。
- 早报 3 篇「借鉴」取自 r114 的 154 条候选池（**已在 SEEN，从「候选」改「收录」**）。
- 元数据（标题 / 作者 / 分类 / published / updated）一律取自官方 id_list XML，不手抄。
- 台账行数不变（4262）：3 行「候选」→「收录」+ 追加 SUMMARY_LINE。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-27-am-fetch-r115-seen.json"
XML = BASE / "raw" / "2026-10-27-am-idlist-r115a.xml"

RECOMMENDED = ["2610.32951", "2610.32881", "2610.32483"]

AREAS = {
    "2610.32951": ["LLM", "RL 后训练", "训练稳定性", "训练-推理数值失配", "BF16", "借鉴"],
    "2610.32881": ["LLM", "RL 后训练", "rollout 加速", "投机解码", "n-gram 缓存", "借鉴"],
    "2610.32483": ["agent harness", "评测基准", "失败归因", "token 成本", "借鉴"],
}

SUMMARY_ZH = {
    "2610.32951": (
        "LLM 的 RL 后训练通常用两套系统：vLLM 采样、另一套框架（如 Hugging Face Transformers）重算 logprob。"
        "即使权重与张量类型（BF16）完全相同，kernel 实现差异也会让「本应 on-policy」的更新变成 off-policy，"
        "并使训练崩塌。本文不改全局精度、不改学习目标、不改推理引擎与矩阵乘/attention kernel，"
        "只把三个区域的「舍入位置」对齐：RoPE 路径、SwiGLU、残差 RMSNorm —— 做法是把选定中间量保留在 FP32，"
        "到该区域输出时再舍入到 BF16。在 4 个 Qwen 系模型（DeepSeek-R1-Distill-Qwen-1.5B、Qwen3-1.7B、"
        "Qwen3-4B-Base、Qwen3-8B-Base；PPO-clipped GRPO；Sanity-Test-R1D-1.5B 训练、AIME 2025 评测）上："
        "默认 BF16 基线全部崩塌；三区域全对齐全部稳定，只对齐 RoPE 路径也足够；静态 per-token KL 只降 "
        "9.1–25.5%（RoPE 的 Shapley 贡献 81.5% / 91.8% / 76.9%，SwiGLU 在 Qwen3 两模型上为负），"
        "而训练与推理使用同一后端（Zero-mismatch）时 KL 严格为 0。⚠️ 仅 2 个数学数据集、单一架构族、最大 8B；"
        "「小 KL 也足以防崩塌」的机制作者只给出假设；数字作者自报、本线未复现；未精读全篇。"
    ),
    "2610.32881": (
        "RL 后训练的耗时主要不是前向/反向，而是自回归 rollout（作者引述可占 step 时间 70% 以上）。"
        "常规投机解码在此不适用：草稿模型要占紧张的 GPU 显存，且随策略漂移会越来越被拒。本文观察到 "
        "GRPO 类训练会反复重访同一 prompt，因此它近期的 rollout 本身就是免费、自更新的草稿源。"
        "据此提出 NgramRL：为每个 prompt 用有界历史 rollout 建 n-gram 查表（放 CPU，无需草稿模型、"
        "无需训练、不占常驻 GPU 显存），由 target 模型验证以保证输出分布不变；再加自适应 fan-out 预取器"
        "预测验证结果 (j, b)（j 为被接受的草稿长度、b 为 target 续出 token），并用因果预算分配把预取"
        "集中在高概率分支，未覆盖的分支回退到串行查表、不改已提交 token。实验为 Qwen3-8B / DeepSeek-LLM-7B "
        "在 GSM8K / Spider 1.0 / CodeContests 上用 GRPO：warm-cache 下每步提交 3.60–7.77 token，"
        "比 SuffixDecoding 高 1.2–1.99×、比 prompt-lookup 最高 7.0×；Spider 上候选预算 16 时预取器覆盖 "
        "96.6% 的 Qwen3-8B 结果，rollout 吞吐比同步版高 1.38×（重叠理论上限 1.40×），decode 迭代 "
        "26.1 ms → 19.2 ms。⚠️ 规模只到 7B/8B、单机、2 个模型族、3 个数据集；1.38× 是 rollout 吞吐而非"
        "端到端训练加速；历史窗口 w>16 后收益不再增长（GSM8K 上还会下降）；数字作者自报、本线未复现。"
    ),
    "2610.32483": (
        "agent 的跑分是「模型 × harness（执行外壳）」的联合结果，只报任务成功率会掩盖失败来源。"
        "本文提出五个互补指标：Valid Completion Rate（VCR，不论对错、是否正常结束并交出可评测结果）、"
        "Model–Harness Fit（某 harness 对某模型有效完成的支持度）、Cross-Model Fit（跨模型整体适配）、"
        "Interaction Residuals（扣掉模型与 harness 主效应后的配对专属偏差）、Token Load（含失败重试的"
        "token 消耗）。实验为 4 个通用 harness（OpenCode / Codex CLI / Pi CLI / DeepAgents）× 4 个模型"
        "（DeepSeek V4 Flash Preview、MiniMax M3、Kimi K2.7、Qwen3.6-35B-A3B）+ 2 个原生固定系统，"
        "跨 6 个基准（SWE-bench-45 / Terminal-Bench 2 / VitaBench / LOCA-Bench / ClawMark / AgentSkillOS），"
        "共 111 个评测设置、52,168 条轨迹。结论：harness 排名随模型与基准变化（同模型下最优 harness 会换）；"
        "OpenCode 在跨模型聚合上第一；DeepSeek V4 Flash Preview 在 4 个 harness 上 Mean VCR 为 "
        "91.30%–93.98%（极差 2.68 个百分点）；VitaBench 上各配置 VCR ≥ 98% 但 Mean-of-4 仍横跨 28.1 个"
        "百分点；同一模型下 Pi CLI 每 attempt 的 token 不到 Codex CLI 的一半而 Mean-of-4 只差 <0.2 个百分点。"
        "作者建议把 harness 使用能力当作可迁移能力来训练。⚠️ 面板有限（ClawMark / AgentSkillOS 因多模态"
        "缺失只跑 3×4）；作者自述 Cross-Model Fit 的领先者依赖所选模型与基准；Preprint under review；"
        "数字作者自报、本线未复现；未精读 43 页附录。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十五轮（本地 2026-10-27 06:00（CST）· P0 第 4 批「早 3」轮 · 新一日 AM）**："
    "**公告批次未刷新** —— 仍 `2026-10-23`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`cat:cs.CL` 探针 `totalResults=123669`、最新样本 `published=2026-10-23T17:59:56Z`，"
    "**与 r114 PM 逐条相同**；广度扫描 `totalResults=637936`；本轮唤醒 `UTC 2026-10-26T22:00`，"
    "早于周一 20:00 ET 公告）；`window_mode=daily`（72h，脚本自动判定、未人工放宽）⇒ "
    "**15/15 查询 `200`、全部 `attempts=1`**、**`kept 0` / `dropped 600`**"
    "（`generated=2026-10-26T22:01:24Z`；600 = 563 `already in SEEN` + 37 `stale > 72h`）。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 169 · cs.CV 205 · cs.LG 321（仅作发现）。"
    "**早报 3 篇「借鉴」取自 r114 的 154 条候选池**（均已在 SEEN、从未进过任何日报）+ "
    "**`id_list` 权威复核 3/3 返回**（`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；"
    "证据 `raw/2026-10-27-am-idlist-r115a.{xml,headers}`）："
    "`2610.32951` Where Rounding Happens Matters: Rounding-Location Alignment Stabilizes LLM RL"
    "（ByteDance Seed + PKU；4 个 Qwen 系模型、PPO-clipped GRPO；BF16 基线全崩塌、三区域对齐或仅 RoPE 对齐即稳定；"
    "静态 per-token KL 仅降 9.1–25.5%）/ "
    "`2610.32881` NgramRL（UCSD + WVU；per-prompt 历史 rollout n-gram 草稿表 + fan-out 预取；"
    "3.60–7.77 token/step、1.38× rollout 吞吐、26.1→19.2 ms）/ "
    "`2610.32483` When Agents Fail: Model or Harness--Who's to Blame?（上海人工智能实验室；五指标 VCR / Fit / "
    "Cross-Model Fit / Interaction Residuals / Token Load；4 harness × 4 模型 + 2 原生 × 6 基准、111 设置 / "
    "52,168 轨迹）⇒ **首次提交均为 `2026-10-23`（UTC）**，非「今日新提交」。"
    "台账 **4,262 行不变**（3 行「候选」→「收录」）→ 累计（**收录 259 / 候选 4,003（含 RSS 补充 507）**）；"
    "`papers.jsonl` **256 → 259**；PDF **3/3** 落地校验通过（17 / 7 / 43 页）；"
    "交付 `daily/2026-10-27.html`（32,393 B · 3/5）+ `daily/index.html`；落盘脚本 `raw/update_r115.py`。"
    "口径见 `ARXIV_API.md` §9.115。"
)


def load_official():
    NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    out = {}
    for e in ET.parse(XML).getroot().findall("a:entry", NS):
        aid = e.find("a:id", NS).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", NS).text.split()),
            "authors": [a.find("a:name", NS).text for a in e.findall("a:author", NS)],
            "published": e.find("a:published", NS).text,
            "updated": e.find("a:updated", NS).text,
            "category": e.find("x:primary_category", NS).attrib["term"],
        }
    assert len(out) == 3, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith("2026-10-23"), out[k]["published"]
    return out


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "attempts != 1"
    assert len(payload["items"]) == 0, len(payload["items"])

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^(\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| )候选( \|)$", ln)
        if m and m.group(2) in RECOMMENDED:
            lines[i] = ln[: ln.rfind("候选")] + "收录" + ln[ln.rfind("候选") + 2:]
            flipped += 1
    assert flipped == 3, flipped
    assert not any(SUMMARY_LINE[:40] in ln for ln in lines), "summary already present"
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    have = set()
    with PAPERS.open(encoding="utf-8") as f:
        for ln in f:
            if ln.strip():
                have.add(json.loads(ln)["arxiv_id"])
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            assert k not in have, "%s already in papers.jsonl" % k
            e = official[k]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": e["authors"],
                "submitted": e["published"][:10],
                "updated": e["updated"][:10],
                "category": e["category"],
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-26",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    st = {}
    for ln in lines:
        m = re.match(r"^\| [0-9-]{10} \| [0-9.]+ \| .* \| (收录|候选|候选（RSS 补充）) \|$", ln)
        if m:
            st[m.group(1)] = st.get(m.group(1), 0) + 1
    print("SEEN flipped:", flipped)
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()
