#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第九十七轮（本地 2026-10-18 06:00 P0「早 3」轮 · AM）结果落盘。

- 本轮 AM：**无新公告批次**（周日 arXiv 不公告；批次仍 2026-10-15；
  `--fetch` window_mode=weekend_batch 120h → kept 0 / dropped 600）
  -> 早报 3 篇「借鉴」取自**前轮（第九十四轮 PM）已入账的窗口内候选池**
  -> SEEN.md 对应 2026-10-16「候选」行改为「收录」
- 3 篇推荐（均「借鉴」）：2610.22353 MirrorMoE / 2610.21755 DeciCAD / 2610.20980 Little Dragon
  -> papers.jsonl 追加 3 行（211 -> 214）
- 元数据取自 id_list 权威复核 raw/2026-10-18-idlist-shortlist-r97.xml（含官方 published/作者）
"""
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"

FIRST_SEEN = "2026-10-18"
RECOMMENDED = ["2610.22353", "2610.21755", "2610.20980"]

SUMMARY_ZH = {
    "2610.22353": "作者指出现代 MoE 同时采用**细粒度专家切分**与**共享专家**时存在「**探索困境**」：共享专家降低了 token 表示的多样性，使路由探索变少；而细粒度切分把路由空间组合性放大、本应需要更多探索 ⇒ 细粒度带来的额外表达力可能无法真正兑现。为此提出 **MirrorMoE**：通过**按 token 自适应抑制不必要的专家**来缩小探索空间，从而调和该困境；作者称其在多个模型规模上**一致提升**表现。⚠️ 结论为作者自报、本线未复现。",
    "2610.21755": "作者研究**agent harness 所定义的决策空间**如何塑造 LLM agent 的行为与策略学习，聚焦 **CAD**（具有持久状态、几何约束、长时程流程的专业领域）。提出 **DeciCAD**：领域原生 harness，暴露**语义 CAD 动作、面向决策的观测、环境反馈与持久状态转移**；并从交互轨迹中抽取**因果决策监督**，用 **SFT + 几何约束在线 RL** 改进策略。作者称在 4 个 CAD 基准上取得最佳 F1 / IoU，且相对通用编码 harness **减少 45–88% 模型输出 token**；SFT 将 F1 从 0.6883 提升到 0.7437，在线 RL 进一步把几何可用率 66.5%→73.5%、F1→0.7880。⚠️ 数字为作者自报、本线未复现。",
    "2610.20980": "作者指出 GPU kernel 优化本质是**编译器变换组合的搜索**，于是训练**小语言模型**直接**构造完整优化脚本**并**改进已有脚本**（而非排序候选或生成 kernel 代码）：设计**紧凑无损表示**，其确定性解码可重建精确的编译器 trace（含变换参数与依赖）；用 TVM MetaSchedule 在 54,116 个 workload 上构建 108,594 条样本（60,236 条构造 / 48,358 条改进）；先 SFT，再加**形状化奖励的 RL**（正确性与实测性能结合，仅对数值正确的 kernel 给延迟奖励）。8B 模型达到**单次尝试正确率** 91.27%（构造）/ 92.01%（改进）；RL 在 88/102 个构造任务与 145/170 个改进提示上产出比 SFT 更快的 kernel；作者称其单次正确率与 kernel 性能优于 6 个前沿 LLM（含 GPT-6 Astra、Opus 5、Kimi-K3、GLM-5.3）。⚠️ 数字与对比为作者自报、本线未复现。",
}

AREAS = {
    "2610.22353": ["MoE", "路由", "预训练", "模型架构"],
    "2610.21755": ["agent harness", "CAD", "SFT", "在线RL", "评测"],
    "2610.20980": ["SLM", "编译器", "GPU kernel", "SFT", "RL"],
}


def main():
    import xml.etree.ElementTree as ET

    ns = {"a": "http://www.w3.org/2005/Atom"}
    root = ET.parse(BASE / "raw" / "2026-10-18-idlist-shortlist-r97.xml").getroot()
    by = {}
    for e in root.findall("a:entry", ns):
        aid = re.sub(r"v\d+$", "", e.find("a:id", ns).text.rsplit("/", 1)[-1])
        cat = e.find("{http://arxiv.org/schemas/atom}primary_category")
        by[aid] = {
            "arxiv_id": aid,
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [x.find("a:name", ns).text for x in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": cat.get("term") if cat is not None else e.find("a:category", ns).get("term"),
        }
    for k in RECOMMENDED:
        assert k in by, "missing %s" % k

    # 1) SEEN: 候选 -> 收录（行数不变）
    lines = SEEN.read_text(encoding="utf-8").split("\n")
    changed = 0
    for i, ln in enumerate(lines):
        for k in RECOMMENDED:
            if ln.startswith("| 2026-10-16 | %s |" % k) and ln.rstrip().endswith("| 候选 |"):
                lines[i] = ln[: -len("| 候选 |")] + "| 收录 |"
                changed += 1
    assert changed == len(RECOMMENDED), "expected %d changed, got %d" % (len(RECOMMENDED), changed)
    SEEN.write_text("\n".join(lines), encoding="utf-8")

    # 2) papers.jsonl 追加
    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by[k]
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
    st = {"收录": 0, "候选": 0, "候选（RSS补充）": 0}
    for ln in lines:
        if ln.startswith("| 2026-"):
            cell = ln.rstrip().split("|")[-2].strip()
            st[cell] = st.get(cell, 0) + 1
    print("SEEN rows:", sum(st.values()), st)
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()
