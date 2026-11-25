#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第一百零五轮（本地 2026-10-22 06:00 AM「早 3」轮）结果落盘。

- **公告批次未刷新**：仍 `2026-10-20`（totalResults=636364，最新 published=2026-10-20T17:59:56Z）；
  `--fetch --seen`（window_mode=daily 72h，generated=2026-10-21T22:01:05Z）15/15 ok（全部 attempts=1）、
  **kept 0 / dropped 600**（整批已在上一轮 PM 入账 SEEN）。
- 早报 3 篇「借鉴」取自上一轮 PM 的 189 条候选池：
  2610.28500 BitMTP / 2610.28385 RACE / 2610.28380 OO-Harness
  -> SEEN 行数不变（4294），只把 3 行「候选」改「收录」
  -> papers.jsonl 追加 3 行（231 -> 234）
- 元数据取自 id_list 权威复核 raw/2026-10-22-idlist-r105.xml（官方 published/作者/摘要）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
XML = BASE / "raw" / "2026-10-22-idlist-r105.xml"

FIRST_SEEN = "2026-10-22"
RECOMMENDED = ["2610.28500", "2610.28385", "2610.28380"]

SUMMARY_ZH = {
    "2610.28500": (
        "超低比特主干与多 token 预测（MTP）本应互补，但直接组合在质量相当时并不加速："
        "masked drafting 缺少中间 token 输入，更宽的计算与因果 KV 更新又抵消了步数收益。"
        "BitMTP 做算法-系统协同设计：联合 NTP + MTP 目标让单模型同时具备自回归生成与 block-causal drafting；"
        "提供 confidence-only / speculative-only / hybrid 三种解码；用 accepted-prefix alignment 保持"
        "「已提交前缀 / 已物化因果 KV 边界 / CUDA Graph 重放状态」一致；再选择宽度特化的低比特执行并复用已捕获的图。"
        "NVIDIA H20 上 hybrid 解码：BitNet b1.58-2B 五任务平均 2.2×、1.7B–4B Bonsai 2.1–2.4×；"
        "RTX 3090 / Jetson Orin 上五任务平均吞吐最高 2.0×、MBPP+ 最高 3.3×。"
        "⚠️ 需超低比特主干（QAT 路线）、非后训练量化；数字作者自报、本线未复现；未做全文精读。"
    ),
    "2610.28385": (
        "KV cache 的 head-dimension 压缩能省显存，但既有方法常在推理时重建全维表示、增加 decode FLOPs。"
        "RACE 形式化「把预训练 attention 转成原生降维形式」的条件（Q/K 共享投影、投影由 Q-K 激活联合导出、兼容 RoPE），"
        "并证明：若免重建而把降维限制为坐标选择，则 RoPE 兼容当且仅当保留完整 rotary pair；"
        "据此用 Q-K 联合激活能量挑选 rotary pair，降维折进权重，无需运行时重建或专用 kernel。"
        "三个模型族、不同压缩比下在语言建模 / zero-shot / 长上下文任务上优于结构化剪枝、与重建类方法相当；"
        "50% KV 保留 + 256K 上下文时总推理 FLOPs −47.8%、吞吐 1.79×、TTFT −43.2%、分配显存 −28.1%。"
        "⚠️ 只压 attention KV（混合架构的 Mamba 支路不在范围内）；仅给 50% 一个工作点；未声明代码；数字作者自报、未复现。"
    ),
    "2610.28380": (
        "agent harness 是围绕模型、可执行的 prompts + tools + control flow 代码；单一全局 harness 难应对异构任务。"
        "OO-Harness 用面向对象设计进化出可执行 harness 类层级：训练时 evolution agent 依据执行记录创建专用 harness，"
        "每个都是基类或已有专用 harness 的子类；测试时 harness router 用训练中积累的路由经验为任务选 harness。"
        "在业务流程 / 工作区任务 / 工具使用三个 long-horizon 基准上为对比方法中最好，相对 base 绝对提升最高 15%，并给出消融。"
        "⚠️ 摘要无逐基准数字、15% 不是平均增益；三个基准不含 EDA；进化成本未给；未做全文精读。"
    ),
}

AREAS = {
    "2610.28500": ["量化", "超低比特", "多 token 预测", "投机解码", "KV cache", "CUDA Graph", "端侧推理"],
    "2610.28385": ["KV cache 压缩", "RoPE", "长上下文", "高效推理", "TTFT"],
    "2610.28380": ["agent harness", "面向对象", "harness 路由", "长程任务", "ZhuLong"],
}

SUMMARY_LINE = (
    "> **第一百零五轮（本地 2026-10-22 06:00（CST）· P0 第 5 批第 3 轮「早 3」轮 · 新一日 AM 轮）**："
    "**公告批次未刷新** —— 仍为 `2026-10-20`（主源 `HTTP 200` + `application/atom+xml; charset=utf-8`，"
    "`totalResults=636364`、最新样本 `published=2026-10-20T17:59:56Z`，与上一轮 PM **完全相同**；周三 20:00 ET 的 `2026-10-21` 批尚未索引）；"
    "**15/15 查询 `ok`**（**全部 `attempts=1`，无重试无超时**）、**`kept 0` / `dropped 600`**"
    "（`window_mode=daily` 72h，`generated=2026-10-21T22:01:05Z`；600 = 15 × 40，剔除原因均为 `already in SEEN` 或 `stale > 72h`）。"
    "R1′ arXiv ✅ / HF ❌（`Errno 101`，如实记 FAIL）/ RSS cs.CL 435 · cs.CV 287 · cs.LG 817（仅作发现）。"
    "**早报 3 篇「借鉴」取自上一轮 PM 已入账的 189 条候选池** + **单条权威复核**"
    "（`id_list=2610.28619,2610.28577,2610.28500,2610.28369,2610.28380,2610.28385` → **6/6 返回**，"
    "均 `HTTP 200` + `application/atom+xml; charset=utf-8` + 含 `published`；证据 `raw/2026-10-22-idlist-r105.{xml,headers}`）："
    "`2610.28500` BitMTP: When Multi-Token Prediction Meets Low-Bit Large Language Models / "
    "`2610.28385` RACE: RoPE-Aligned Attention Compression Based on Query-Key Activation Energies / "
    "`2610.28380` Object-Oriented Harness: Evolving Agent Harnesses through Object-Oriented Design。"
    "台账 **4,294 行不变**（3 行「候选」→「收录」）→ 累计（**收录 234 / 候选 3,553 / 候选（RSS 补充）507**）；"
    "`papers.jsonl` **231 → 234**；PDF 3/3 落地校验通过；落盘脚本 `raw/update_r105.py`。口径见 `ARXIV_API.md` §9.105。"
)


def load_official():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom",
          "x": "http://arxiv.org/schemas/atom"}
    root = ET.parse(XML).getroot()
    official = {}
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        cat = e.find("x:primary_category", ns)
        com = e.find("x:comment", ns)
        official[aid] = {
            "arxiv_id": aid,
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
            "comment": com.text if com is not None else "",
            "summary": " ".join(e.find("a:summary", ns).text.split()),
        }
    assert len(official) == 6, "expected 6 entries in id_list, got %d" % len(official)
    for k in RECOMMENDED:
        assert k in official, "missing %s in id_list" % k
        assert official[k]["published"].startswith("2026-10-20"), official[k]["published"]
    return official


def main():
    official = load_official()

    # 1) SEEN: 3 行状态 候选 -> 收录（行数不变）
    text = SEEN.read_text(encoding="utf-8")
    lines = text.split("\n")
    flipped = 0
    for i, ln in enumerate(lines):
        m = re.match(r"^\| (\d{4}-\d\d-\d\d) \| ([^ |]+) \|.*\| 候选 \|$", ln)
        if m and m.group(2) in RECOMMENDED:
            lines[i] = ln[: -len("| 候选 |")] + "| 收录 |"
            flipped += 1
    assert flipped == 3, flipped
    if lines and lines[-1] != "":
        lines.append("")
    lines.append(SUMMARY_LINE)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加 3 行
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
                "first_seen": FIRST_SEEN,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    # 3) 统计
    st = {}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows flipped:", flipped)
    print("SEEN rows total:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()

