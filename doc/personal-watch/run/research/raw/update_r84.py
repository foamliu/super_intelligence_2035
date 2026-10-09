#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""一次性：把第八十四轮（本地 2026-10-10 06:00 P0「早 3」轮）结果落盘。
- raw/2026-10-10-rss-r84.json 的 in_window（RSS 发现 + id_list 复核，547 条 <=72h）
  -> SEEN.md（收录 3 / 候选 544）
- 3 篇收录（借鉴）-> papers.jsonl
"""
import json, re
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
DATA = BASE / "raw" / "2026-10-10-rss-r84.json"

RECOMMENDED = ["2610.12274", "2610.11548", "2610.11214"]

SUMMARY_ZH = {
    "2610.12274": "文本到 SQL 模型通常只学「问题→静态查询」的映射，而真实数据库智能体是「有状态、多轮」地操作活库（查 schema、执行探针查询、诊断报错、修正假设），但执行 harness 只在推理时引入 → 存在训练–部署错配。提出 HarnessSQL：把完整交互结构贯穿到 SFT 与 RL 全程 —— 构造隔离、可执行的数据库环境并配隐藏执行 oracle，让 teacher 直接在目标 SQL harness 内 rollout，只保留经核验的轨迹做全序列 SFT，再做执行奖励 RL。原文报告在 Spider 2.0-SQLite 上把 Qwen3-8B 执行准确率从 15.5% 提升到 45.2%、Qwen3-14B 从 22.2% 提升到 54.8%，并有效迁移到 BIRD-Interact / LiveSQLBench 等 OOD 交互式基准。",
    "2610.11548": "针对「合成任务既被当作能力探针、又被当作预训练数据，二者都用 loss 下降来正当化」这一混淆，区分三个信号：diagnostic（loss 是否跟踪全局预训练进展）、teachable（loss 是否响应自身 token 预算）、transfer（纳入后是否改善下游目标）。在受控预训练里固定 70% 通用 Python，剩余 30% 在三类源上做单纯形配比扫描（OpenCodeInstruct / 12 个精选代码邻近合成任务 / 15 个来自文献的探针任务）。发现 27 个任务中 14 个「可教」，且两类合成族差异悬殊（精选 10/12 vs 文献 4/15）；可教性与下游迁移给出不同排序。在精选族与 OpenCodeInstruct 的配比边上，固定微调后 HumanEval pass@20 从纯精选的 15.9 升到最高 22.6（75% OpenCodeInstruct），再在纯 OpenCodeInstruct 回落到 19.5 —— 精选合成数据具「条件价值」。最后，基于 loss 的自适应调度器暴露「残余 loss 可降性」与「下游迁移」的不一致：三条 60k 步自由配比运行中，Ado 在头 5k 步就把 OpenCodeInstruct 份额压到 5% 以下、训练末到 1.2–1.4%，比匹配的固定配比对照差 2.4–11.0 个百分点。",
    "2610.11214": "KV-cache 量化把单个 KV 项压成离散码但保留全部条目，线性注意力则把多条历史 KV 递归聚成定长连续状态、但会引入干扰。原文指出二者可在单一机制内桥接：RAM-Net 通过对离散地址空间的软分配，同时做「逐 KV 压缩」与「多 KV 聚合」。在一个受限 RAM-Net 构造下证明软地址分配把硬量化匹配扩展为可分的读写重叠，局部近似全注意力相似度并支持递归聚合；该联系进一步给出基于「软量化中间构造」的 Transformer→RAM-Net 权重迁移路径。在 0.3B–7B 的 9 个预训练 Transformer 上，RAM-Net 仅用每模型 500M token 训练，即可在 6 个常识/知识任务上平均恢复教师相对随机猜测的 87.1% 准确率增益。",
}

AUTHORS = {
    "2610.12274": ["Haolin Yang", "Jipeng Zhang", "Jian Xie", "Shuaishuai Gong", "Sirui Han", "Yike Guo"],
    "2610.11548": ["Ohad Rubin"],
    "2610.11214": ["Kaicheng Xiao", "Liran Dong", "Haotian Li", "Guoliang Xing"],
}
AREAS = {
    "2610.12274": ["agent harness", "SFT", "RL"],
    "2610.11548": ["LLM", "预训练数据配比"],
    "2610.11214": ["SLM", "高效推理", "线性注意力"],
}


def clean_title(t):
    return t.replace("|", "/").strip()


def base(aid):
    return re.sub(r"v\d+$", "", aid)


def main():
    data = json.loads(DATA.read_text(encoding="utf-8"))
    rows = data["in_window"]
    by_base = {}
    for e in rows:
        b = base(e["id"])
        if b not in by_base:
            by_base[b] = e
    print("in_window raw:", len(rows), "dedup base:", len(by_base))

    for k in RECOMMENDED:
        assert k in by_base, k

    rec_rows, cand_rows = [], []
    for k in RECOMMENDED:
        e = by_base[k]
        rec_rows.append("| 2026-10-10 | %s | %s | %s | 收录 |" % (k, clean_title(e["title"]), e["primary"]))
    for k, e in sorted(by_base.items(), reverse=True):
        if k in RECOMMENDED:
            continue
        cand_rows.append("| 2026-10-10 | %s | %s | %s | 候选 |" % (k, clean_title(e["title"]), e["primary"]))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    last_idx = None
    for idx in range(len(lines) - 1, -1, -1):
        if lines[idx].startswith("| 2026-10-"):
            last_idx = idx
            break
    assert last_idx is not None, "未找到最后数据行"
    new_lines = lines[:last_idx + 1] + rec_rows + cand_rows + lines[last_idx + 1:]
    SEEN.write_text("\n".join(new_lines), encoding="utf-8")

    with PAPERS.open("a", encoding="utf-8") as f:
        for k in RECOMMENDED:
            e = by_base[k]
            rec = {
                "arxiv_id": k,
                "title": e["title"],
                "authors": AUTHORS[k],
                "submitted": e["published"][:10],
                "updated": e["published"][:10],
                "category": e["primary"],
                "areas": AREAS[k],
                "summary_zh": SUMMARY_ZH[k],
                "abs_url": "https://arxiv.org/abs/%s" % k,
                "pdf_url": "https://arxiv.org/pdf/%s" % k,
                "first_seen": "2026-10-10",
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    print("SEEN rows added:", len(rec_rows) + len(cand_rows), "(rec %d / cand %d)" % (len(rec_rows), len(cand_rows)))
    print("papers.jsonl +", len(RECOMMENDED))


if __name__ == "__main__":
    main()
