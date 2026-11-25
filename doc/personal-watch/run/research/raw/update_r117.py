#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百一十七轮（本地 2026-10-28 06:00 AM「早 3」轮 · 新一日 AM）结果落盘。

- **公告批次未刷新**：仍 `2026-10-26`（`cat:cs.CL` 探针 `totalResults=123901` 与 r116 相同、
  最新样本 `published=2026-10-26T17:59:33Z`；广度扫描 639007）。`--fetch --seen`
  （`window_mode=daily` 72h，`generated=2026-10-27T22:01:20Z`）**15/15 查询 200、全部 attempts=1**、
  **kept 0 / dropped 600**（600 = 547 already in SEEN + 53 stale > 72h）。
- 早报 3 篇「借鉴」取自 r116 的 206 条候选池（**已在 SEEN，从「候选」改「收录」**）。
- 元数据（标题 / 作者 / 分类 / published / updated）一律取自官方 id_list XML，不手抄。
- 台账行数不变（4975 + 1 状态行）：3 行「候选」→「收录」+ 追加 SUMMARY_LINE。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-28-am-fetch-r117-seen.json"
XML = BASE / "raw" / "2026-10-28-am-idlist-r117a.xml"

RECOMMENDED = ["2610.35690", "2610.35801", "2610.35309"]

AREAS = {
    "2610.35690": ["agent harness", "多智能体路由", "on-policy 蒸馏", "成本感知 RL", "推理服务", "借鉴"],
    "2610.35801": ["agent harness", "RL 后训练", "critic 学习", "信用分配", "长程 agent", "借鉴"],
    "2610.35309": ["多模态", "边缘推理", "异构 SoC", "KV 状态迁移", "存储/芯片", "借鉴"],
}


SUMMARY_ZH = {
    "2610.35690": (
        "大规模多智能体系统（MAS）服务要同时决定：用哪些 LLM、什么协作模式（IO / CoT / Reflection / "
        "Chain / FullConnected / Debate）、几个 agent、几轮交互、挂哪些技能 —— 配置空间组合爆炸；"
        "而执行只回传「成功/失败 + 成本」这种稀疏结果奖励，对互相耦合的规划决策几乎没有细粒度监督。"
        "本文提出 EvoRouter：① 一个 LLM 专家周期性把跨任务的「配置—结果—成本」轨迹综合成带适用条件的"
        "洞察（任务相关的能力瓶颈、扩资源的边际收益、配置项之间的相互依赖）；② 用「带洞察条件」的 "
        "on-policy 蒸馏（OPD，MiniLLM 式 reverse KL、只作用于分析/计划段、教师带特权信息且 stop-gradient）"
        "把洞察变成 token 级稠密监督；③ 用成本感知 RL，奖励 R(τ)=Rperf−λC·Rcost、"
        "Rcost=log2(1+C(τ)/B(q)) 按任务预算归一，并把成本罚分上限压在 cmax<1 以保证成功轨迹奖励仍为正；"
        "④ 更新后的策略再产生新轨迹，形成「执行→洞察→内化」自演化闭环。实验为 21 个数据集 / 7 个领域"
        "（19 个域内：数学 / 常识 / 知识 / 检索 / 多模态；2 个域外：LiveCodeBench 代码、BBH-LD 逻辑），"
        "LLM 池 = Qwen3.5-35B-A3B / 122B-A10B / 397B-A17B + DeepSeek-V4-Flash + GLM-5。"
        "EvoRouter-4B 域内平均 68.69%（比最强基线 RCR-Router 61.46% 高 7.23 个百分点），同时平均 MAS "
        "成本降 50.95%（15,280.79 相对 FLOPs 单位）；把 router 自身开销计入后总成本 18.94k 单位，仍比 "
        "MasRouter 低 76.5%、比 RCR-Router 低 39.2%。域外平均 74.67%（4B）/ 76.80%（8B）/ 78.93%"
        "（LLaMA-8B），比最强基线高 7.74–12.00 个百分点。消融（4B）：去 insights 64.54、去 OPD 63.23、"
        "去 RL+OPD 59.77、仅 SFT 53.23。⚠️ 定位云侧 MAS（作者自述下一步才做云–边协同）；成本用相对 "
        "FLOPs 代理、非墙钟/能耗；router 只到 4B/8B；作者自报、本线未复现、未精读附录。"
    ),
    "2610.35801": (
        "长程 agent（几十到上百次工具调用）用「可验证奖励 RL」训练时，一条轨迹只给一个 0/1 终局奖励，"
        "早期动作拿不到信用；学一个 critic 给中间状态估值是常见解法，但 critic 本身不准，而在轨迹中间"
        "反复续采样来估值又很贵。本文把「用续采样改进 critic」当成主动学习问题：FOCUS 把每个 episode "
        "当作搜索树，用上下文压缩（compaction）产生的段边界作为候选状态，用 critic 的预测 + 已采样续接"
        "的证据估计「再采一条能把估值误差降多少」，把有限 rollout 预算分配给最可能降误差的状态；"
        "细化后的状态价值用 TD(λ) 给相邻状态之间的「段」打 advantage，采样得到的证据同时作为 critic 的"
        "训练目标 —— 于是「本轮信用分配」与「下轮 critic 更准」耦合起来。context management 与 rollout "
        "分配解耦，可替换压缩算子 / harness / 信用估计器。实验：Qwen3.5-9B，DeonticBench（法律推理）、"
        "BrowseComp-Plus（深度检索）、LocBench（代码定位），与 GRPO、VinePPO 在匹配的每步生成预算下各训 "
        "1 epoch、每次 rollout 都压缩：FOCUS 在三个基准上都第一 —— DeonticBench 总体 56.5（GRPO 52.4 / "
        "VinePPO 49.4）；BrowseComp-Plus 55.4（48.2 / 46.6，+7.2 个百分点）；LocBench File@1/@5 "
        "72.4/81.6（70.1/80.5、67.8/79.3）。Qwen3.5-27B（LoRA）DeonticBench 76.3（74.3 / 74.9），"
        "增益变小 —— 作者称可能因未训练的 27B 起点已达 73.4。诊断：critic MSE 随细化预算下降、"
        "Spearman 相关上升；GRPO 训练后期出现「工具调用塌缩」（压缩完就交卷，即使法规/代码还没读完），"
        "FOCUS 保持更长程探索。算力：训练 2×H200、rollout 4–6×H100、critic 精化 1×H100。"
        "⚠️ 只在 Qwen3.5 系（9B 为主、27B 仅一个基准）、3 个基准、1 epoch；「匹配每步生成预算」"
        "不等于同等墙钟/成本；压缩算子会影响结果（仅两种消融）；作者自报、本线未复现、未精读附录。"
    ),
    "2610.35309": (
        "边缘 SoC 上通常同时有 CPU / GPU / NPU，但 VLM 运行时往往只把语言生成放在一个引擎上，其余闲置；"
        "流式 VLM 又天然有并行机会：新帧在到达，旧查询还在作答。难点是各引擎算力与访存特性不同、同跑"
        "互相干扰（实测 RK3588 上共跑让 CPU 与 Mali GPU 解码分别慢 26% / 11%；QCS6490 上三引擎共享约 "
        "16 GB/s 读带宽），且每个后端把历史放在自己的 KV 布局里，别的引擎接不上。本文提出 CrossInfer："
        "把「流的历史」抽象为带版本号的已发布上下文，与各引擎私有的 KV 状态解耦 —— 任何引擎都能通过"
        "复用 / 导入 / 重建该版本继续这条流（跨引擎 KV 导入比重新计算前缀让首 token 早 4.6×）；两种执行"
        "模式：Stateful Streaming Generation（一个引擎摄取新帧、另一个按已发布版本作答，答案与串行参考"
        "一致）与 Concurrent Sequence Generation（CPU/GPU 并行服务不同就绪请求），再加按「预计完成时间」"
        "派发的调度器。三块板实测（Apple M4 Max / Rockchip RK3588 / Qualcomm QCS6490）：RK3588 双路视频"
        "流下吞吐比「单引擎 + 上下文复用」高 19.6%、比「双引擎但无共享状态」高 27.2%，首 token 时间降 "
        "34.9%；M4 Max 上 SSG 吞吐是串行的 2.48×（RK3588 +56.7%）；FastVLM-1.5B 上视觉与语言重叠使吞吐"
        "最高 +23%、平均 TTFT −22%；Qwen3.5 0.8B–9B 四个模型上相对「串行 + 上下文复用」吞吐最高 +72.4%；"
        "Qwen2.5-VL-3B 单请求能耗比 llama.cpp 低 23.6%；状态感知派发把完成时间最多降 72.7%。"
        "⚠️ 只测 3 块边缘板、模型 0.5B–9B、无数据中心 GPU 场景；能耗只报单点；作者自报、本线未复现、"
        "未精读附录。"
    ),
}

SUMMARY_LINE = (
    "> **第一百一十七轮（本地 2026-10-28 06:00（CST）· P0 第 4 批「早 3」轮 · 新一日 AM）**："
    "**公告批次未刷新** —— 仍 `2026-10-26`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`cat:cs.CL` 探针 `totalResults=123901`、最新样本 `published=2026-10-26T17:59:33Z`（`2610.35865v1`），"
    "广度扫描 `639007`，**与 r116 逐条相同**）；`window_mode=daily`（72h，脚本自动判定、**未人工放宽**）⇒ "
    "**15/15 查询 `200`、全部 `attempts=1`**、**`kept 0` / `dropped 600`**（600 = **547** already in SEEN + "
    "**53** stale > 72h；`generated=2026-10-27T22:01:20Z`）—— 整批已入 SEEN，**非「无数据」**。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL · cs.CV · cs.LG **均 0 条**（本地 06:00 = "
    "UTC 前一日 22:00，当日公告尚未生成，**仅作发现、不作证据**）。"
    "**早报 3 篇「借鉴」取自 r116 的 206 条候选池**（已在 SEEN、从未进过任何日报）+ **`id_list` 权威复核 3/3**"
    "（`HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 "
    "`raw/2026-10-28-am-idlist-r117a.{xml,headers}`）：`2610.35690` *EvoRouter: Cost-Efficient Multi-Agent "
    "Routing via Insight-Guided On-Policy Distillation*（21 数据集 / 7 领域；洞察蒸馏 + 成本感知 RL；"
    "4B 域内 68.69%（+7.23 pp）而 MAS 成本 −50.95%，含 router 总成本仍低 76.5% / 39.2%；OOD 74.67–78.93%）· "
    "`2610.35801` *FOCUS: Active Critic Learning for Long-Horizon Language Model Agents*"
    "（压缩边界当候选状态 + 主动选点续采样精化 critic + TD(λ) 段级 advantage；Qwen3.5-9B 上 DeonticBench "
    "56.5 vs 52.4、BrowseComp-Plus 55.4 vs 48.2、LocBench 72.4/81.6 vs 70.1/80.5）· "
    "`2610.35309` *Shared Context, Separate Engines: Streaming Vision--Language Inference on Edge SoCs*"
    "（版本化上下文 + 跨引擎 KV 导入；RK3588 双流 +19.6% / +27.2%、TTFT −34.9%，KV 导入比前缀重算早 4.6×，"
    "SSG 2.48×）⇒ **首次提交均为 `2026-10-26`（UTC）**，非「今日新提交」。"
    "台账 **4,975 行不变**（3 行「候选」→「收录」）+ 1 行状态 ⇒（**收录 264 / 候选 4,204 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **261 → 264**；PDF **3/3** 落地校验通过（13 / 32 / 25 页）；"
    "交付 `daily/2026-10-28.html`（3/5）+ `daily/index.html`；落盘脚本 `raw/update_r117.py`。"
    "口径见 `ARXIV_API.md` §9.117。"
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
        assert out[k]["published"].startswith("2026-10-26"), out[k]["published"]
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
                "first_seen": "2026-10-28",
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
