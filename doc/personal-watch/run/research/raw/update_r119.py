#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十九轮（本地 2026-10-29 06:00 AM「早 3」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-29-am-fetch-r119-seen.json`（`--fetch --seen`，`generated=2026-10-28T22:00:40Z`）
  - `raw/2026-10-29-am-idlist-r119a.xml`（官方 Atom 元数据）

动作：
  1) 断言：15 查询全 200 / `attempts=1`、`kept 0` / `dropped 600`、`window_mode=daily`；
  2) `SEEN.md`：3 个推荐 ID 原为「候选」，本轮只翻成「收录」（**不新增行**）；
  3) `papers.jsonl`：追加 3 条（元数据取自官方 id_list XML）；
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-29-am-fetch-r119-seen.json"
XML = BASE / "raw" / "2026-10-29-am-idlist-r119a.xml"

RECOMMENDED = ["2610.37647", "2610.37609", "2610.36114"]
FIRST_SEEN = "2026-10-29"

AREAS = {
    "2610.37647": ["LLM", "预训练", "优化器", "Muon", "权重范数", "MoE"],
    "2610.37609": ["agent harness", "agentic RL", "rollout 效率", "数据调度", "GRPO"],
    "2610.36114": ["agent harness", "上下文工程", "工具输出截断", "可观测性", "评测"],
}

SUMMARY_ZH = {
    "2610.37647": (
        "把 Muon 系优化器的「权重范数控制」换成可分析的累积有效学习率 C_T = Σ η_t/‖W_t‖_F："
        "证明 vanilla Muon 全程只能按对数累积（Θ(log T)），MuonW / MuonH 在给定条件下至少线性；"
        "并提出 MuonGS —— 用 Gram–Schmidt 投影去掉每次 Muon 更新的径向分量、但不固定范数，"
        "在恒定名义学习率与有界更新方向下证明范数至多按 √t 增长、C_T=Ω(√T)，光滑尺度不变目标有 O(T^-1/2) 平稳性保证。"
        "预训练实验：160M/400M 稠密 GPT 式模型（FineWeb 100B-token 子集，3–25B / 8–63B tokens）"
        "与 135M active/1B total 的 MoE（Ultra-FineWeb，10.8B / 21.6B tokens）；长训练 horizon 下验证困惑度低于 MuonH，"
        "稠密模型在等验证 loss 下估计 token 等效加速最高约 15%（正文口径 7–15%）。⚠️ 未到 2B 级验证；15% 为拟合反推估计；作者自报、本线未复现。"
    ),
    "2610.37609": (
        "Agentic RL 的 rollout 成本高，本文把调度粒度从「题」换成「环境–任务对」：把环境–任务对建成双关系图"
        "（同环境内连边抓任务语义与共享工具/状态/验证器结构，跨环境连边抓抽象执行与奖励拓扑），沿边传播历史 rollout 统计量、"
        "预测任务内奖励方差；按 exploitation（高奖励方差）+ coverage（欠观察环境）排批，并用环境配额与相似度惩罚防集中，无需额外 pilot rollout。"
        "在 EnvScaler 池（2,550 任务 / 51 可执行环境）上对 Qwen3-Thinking 1.7B/4B/8B/30B-A3B 做 GRPO（每批 B=64 对、每对 K=8 条轨迹、200 步）；"
        "Qwen3-8B 在 BFCL-v3 / τ-Bench / ACEBench-Agent 上 40 步平均 48.81，超过随机选题 120 步的最高分；"
        "200 步时各规模三基准一致优于随机（4B +3.05/+3.23/+2.00；8B +4.00/+3.03/+3.34）；"
        "仅按 prompt 信息量调度的 DPS / LEEPS 整体不如它，个别维度低于随机。⚠️ 绑定单一环境池与固定 GRPO 配方；作者自报、本线未复现。"
    ),
    "2610.36114": (
        "指出 agent 评估漏掉的第三个量：工具输出在到达模型前的损耗。提出五阶段上下文流水线"
        "（S1 产生→投递、S2 投递→行动、S3 行动→保留、S4 保留→交接、S5 交接→跨运行持久；S5 为保持运行独立而故意关闭）。"
        "在「读 Linux 内核 trace 定位注入故障」的 tool-using agent 上实测 720 次运行：最大 prompt 仅占 400k 窗口 5.75%（≈23k tokens），"
        "但 11,189 条工具结果中 3,827 条（≈1/3）在到达模型前被按 JSON 文本固定长度前缀截断且全部成为坏 JSON；"
        "同一 payload 中一个列表仅 4.7% 的调用到达（742 次）、相邻列表 99.3% 到达；诊断准确率沿「证据在早/晚字段」分裂（40–55/60 vs 0–24/60）。"
        "受控实验（864 条真实结果回放）显示代价先体现为更多工作：工具调用 +43%（53→76）、计算量翻倍（18→36）、yield 0.61→0.31，findings 始终 11。"
        "另读代码调查 7 个 agent 框架：2 个按位置截断（langchain-core 保留前 500 字符；smolagents 删超 20k 字符观察的中间），3 个不截断，1 个只截 tracing，1 个按整行截断。"
        "⚠️ 作者明确称「截断是否真的导致准确率下降」仍为开放问题；样本小；作者自报、本线未复现。"
    ),
}


NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
EXPECT_PUB = {
    "2610.37647": "2026-10-27",
    "2610.37609": "2026-10-27",
    "2610.36114": "2026-10-26",
}


def load_official():
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
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return out


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    assert all(q["attempts"] == 1 for q in meta["per_query"]), "unexpected retry"
    assert items == [], len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    assert (n_seen, n_stale) == (557, 43), (n_seen, n_stale)

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    rows = {}
    for i, ln in enumerate(lines):
        m = ANY_ROW_RE.match(ln)
        if m:
            rows.setdefault(m.group(1), []).append((i, m.group(2)))
    before_lines = len(lines)
    for k in RECOMMENDED:
        assert k in rows, "%s not in SEEN" % k
        assert len(rows[k]) == 1, (k, rows[k])
        idx, status = rows[k][0]
        assert status == "候选", (k, status)
        lines[idx] = lines[idx].replace("| 候选 |", "| 收录 |")

    SEEN.write_text("\n".join(lines), encoding="utf-8")
    assert len(lines) == before_lines, "SEEN line count changed"

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

    st = {}
    for ln in lines:
        m = ANY_ROW_RE.match(ln)
        if m:
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN lines:", len(lines), "(unchanged)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()
