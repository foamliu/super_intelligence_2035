#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十一轮（本地 2026-10-30 06:00 AM「早 3」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-30-am-fetch-r121-seen.json`（`--fetch --seen`，`generated=2026-10-29T22:01:07Z`）
  - `raw/2026-10-30-am-idlist-r121a.xml`（官方 Atom 元数据，3 条）

动作：
  1) 断言：15 查询全 200 / 全 `attempts=1`、`kept 0` / `dropped 600`、`window_mode=daily`、`items==[]`；
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
FETCH = BASE / "raw" / "2026-10-30-am-fetch-r121-seen.json"
XML = BASE / "raw" / "2026-10-30-am-idlist-r121a.xml"

RECOMMENDED = ["2610.37648", "2610.37553", "2610.37631"]
FIRST_SEEN = "2026-10-28"  # 三条均来自 r118 候选池（当日入 SEEN，状态=候选）

AREAS = {
    "2610.37648": ["agent harness", "工具使用", "合成环境", "数据配比", "规模律", "SFT"],
    "2610.37553": ["LLM", "RLVR", "无标签强化学习", "后训练稳定性", "自强化", "群体动力学"],
    "2610.37631": ["LLM", "预训练", "评测诊断", "知识获取", "规模律", "checkpoint 分析"],
}


SUMMARY_ZH = {
    "2610.37648": (
        "提出 SynthAPI —— 一条可**显式控制多样性**的可执行工具环境合成管线：沿「应用/工具数 A、每应用任务数 T、"
        "每任务数据档案数 S、数据库干扰深度 D」四轴生成带真实 Python API 与初始数据库状态的工具环境，"
        "并为每个任务生成可执行的成功校验器。作者用 458,752 个合成任务、849 个训练模型（2B/4B/9B/27B 级别的 Qwen3.5 学生）"
        "系统扫描这些控制维度，得到一条**数据组成感知的规模律** P̂ = σ(c0 + cA·log2(A·S·D))·σ(b0 + bT·log2 T)^ν："
        "在留出的最高 25% 训练 FLOPs 区间（16× 外推）上 MAE 0.0285，而只看「数据量」的规模律 MAE 0.1706。"
        "结论：任务预算较小时（64–512 任务）**少应用多任务**更好（A=8 最优），预算超过 4096 任务后 **A=64 明显更好**；"
        "每任务的数据档案数 S 随预算从 1 → 2 → 4 递增最优；干扰数据 D=4 在高预算下优于 D=1/2。"
        "按这套配方训练的 SynthAPI-Big 在 AppWorld Test-C 达 66.4%（4B）/ 77.0%（9B），比 SimSAT 高 7.6 / 11.6 个百分点；"
        "BFCL 上比最强基线高 2.0 个百分点（4B，对 EnvFactory）/ 3.7 个百分点（8B，对 EnvScaler）——"
        "⚠️ 作者自承：基线用「小数据 SFT+RL」、本文用「大数据纯 SFT」，**该对比不隔离合成方法本身、也不证明数据效率**。"
        "合成语料共 5.9B tokens；作者自报、本线未复现。"
    ),
    "2610.37553": (
        "解释「无标签 RLVR（用多数投票当奖励）先涨后崩」的**数据集规模依赖性**：在「多题共享参数」的可解模型里，"
        "当单题自强化漂移 F 的群体平均斜率 ⟨F′⟩ > 0（题目仍不确定时成立；K=3 时即答案 logit |z| < ln(2+√3) ≈ 1.32），"
        "任何**共享扰动**都会被放大，形成 Curie–Weiss 型顺磁不稳定性。单题锐化速度按 1/N 变慢，"
        "而共享模式按 ∝λ² 增长（与 N 无关）⇒ 得到闭式临界题量 N_c ≃ ln(1/δ)/(λ²·ln[F*/F(a)])，"
        "并把 λ²·N·ln[F*/F(a)] 收敛到单一临界值 Λc ≈ 2.6。随机模拟（REINFORCE, K=3, 二值答案, 普通 SGD）复现四条可证伪预测："
        "相变陡峭、Nc ∝ λ^−2（拟合斜率 −2.22，含对数修正）、λ=0.1/a=0.5 时 Nc ≈ 536、GRPO 同 Nc（548）、更大 K 抬高 Nc。"
        "小 Transformer 实验（6 位数字比较题 x1+x2+x3 > x4+x5+x6；22 个条件 × 7 个数据集规模 × 6 seeds）："
        "**去掉共享方向（反对称网络）则永不坍缩**；把共享耦合通过 bias 加回 ⇒ 剂量依赖地恢复坍缩（ρb ≥ 1 时几乎全部坍缩）；"
        "边际熵奖励在 βc ≈ 12 以上能阻止坍缩，**但救不回准确率** —— 不稳定转移到下一个「与任务无关」的集体核模式。"
        "⚠️ 证据在玩具模型 + 小型合成任务网络上，**未在真实 LLM 的 RLVR 上验证**；单作者自报、本线未复现。"
    ),
    "2610.37631": (
        "提出 **TVS（temporal variability score）= 一条样本在各年份「时点模型」上的 per-token NLL 变异系数**"
        "（PIT-4B 系列：8 个 4B 基座、2017–2024 逐年 FineWeb 快照、同架构/分词器/训练配方）。"
        "在 6 个多选题基准（HellaSwag / PIQA / WinoGrande / ARC-Easy / ARC-Challenge / MMLU，共 16,239 条；"
        "按 token 长度分箱、箱内按 TVS 三分位分组）上，跟踪 6 个模型（Pythia 1.4B / 6.9B、TinyLlama 1.1B、SmolLM3 3B、"
        "OLMo 1B / 7B；checkpoint 覆盖 0.54B → 11.1T tokens）的**机会归一化准确率**。"
        "发现：训练早期低/高 TVS 组几乎无差（24 个设置中低 TVS 赢 13 个，均值 −0.8 分），但后半程高 TVS 组每 10 倍 token 多涨 2.0 分；"
        "**最终高 TVS 组在 34/36 个「模型×基准」设置上胜出，平均 +7.3 分（95% CI [5.5, 9.2]；按 4 个模型家族平均后 CI [4.8, 10.2]，p=.003）**，"
        "每个基准均为正向（WinoGrande +1.7 → PIQA +16.1）。知识密集型 ARC/MMLU 上，控制平均 NLL 后 18 个设置全部为正（+6.9 分）；"
        "再控制「金答案 vs 干扰项 margin」后仅剩 +1.4 分（22/36 为正）⇒ **7.3 分不是「独立的 TVS 效应」**。"
        "反向对照：直接按**平均 NLL** 分组，高 NLL 组在全部 36 个设置里更差；用未归一化的 NLL 标准差分组则效应反转。"
        "⚠️ 每个设置只有 1 条训练轨迹（区间反映设置间差异，不是 run-to-run 方差）；TVS 度量的是「likelihood 随年份的波动」，不是知识流行度的直接测量。"
    ),
}

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
EXPECT_PUB = {
    "2610.37648": "2026-10-27",
    "2610.37553": "2026-10-27",
    "2610.37631": "2026-10-27",
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
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert all(a == 1 for a in attempts), attempts
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
