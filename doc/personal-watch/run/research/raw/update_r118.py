#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百一十八轮（本地 2026-10-28 18:00 PM「晚 2」轮 · 当日 5/5 收口）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-28-pm-fetch-r118-seen.json`（`--fetch --seen`，`generated=2026-10-28T10:06:31Z`）
  - `raw/2026-10-28-pm-idlist-r118a.xml`（官方 Atom 元数据）

动作：
  1) 断言：15 查询全 200、`kept 162` / `dropped 400`、`window_mode=daily`；
     13 条 `attempts=1`、2 条 `attempts=2`（真实网络重试：llm-scaling-law / mm-csmm）。
  2) SEEN.md：把 162 条新候选按「首次提交」倒序插入表格末尾（首次收录 = 2026-10-28）；
     其中 2 条推荐论文直接记「收录」（它们此前不在 SEEN）。
  3) papers.jsonl：追加 2 条（元数据取自官方 id_list XML）。
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-28-pm-fetch-r118-seen.json"
XML = BASE / "raw" / "2026-10-28-pm-idlist-r118a.xml"

RECOMMENDED = ["2610.37649", "2610.36668"]
FIRST_SEEN = "2026-10-28"

AREAS = {
    "2610.37649": ["LLM", "自主科学发现", "反事实物理世界", "工具构建", "多智能体评测", "科普"],
    "2610.36668": ["LLM", "行为评测", "Asch 从众", "分布对比", "多智能体一致性", "科普"],
}

SUMMARY_ZH = {
    "2610.37649": (
        "把「科学发现」做成可自动运行、无人干预的闭环：LongChang 造 15 个 MuJoCo 虚拟世界"
        "（1 个普通物理对照 + 14 个各改一条物理定律，例如「越重的球落得越慢」），LLM 当探索者，"
        "不给研究任务、不透露被改的定律，只能自己操纵物体、造工具、提问题、做实验；另由 LLM 代理"
        "生成与演化场景、审查工具设计、并按「改动后的真实定律」判定报告是否既正确又有实验支撑。"
        "12 个前沿 LLM × 15 场景 × 最多 100 轮：仅 GPT-6-Astra 发现率 16.7%（其余 11 个 0%），"
        "其证据支撑率 97.6%、定律正确率 19.0%；任务提示 + 场景线索把发现率抬到 28.6%（证据支撑率不变）；"
        "预算 100 → 500 轮反而降到 14.3%（约 40 轮即自停）；关闭造工具降到 4.8%。"
        "⚠️ 判分与场景演化也是 LLM（GPT-6.1-Sol / GPT-6-Astra）；15 场景属小样本；作者自报、本线未复现。"
    ),
    "2610.36668": (
        "把 Asch 从众实验搬进 LLM，但用「采样分布」替代「社会压力」：同一道 SAT 式填空题对同一模型采样 "
        "100 次（temperature 1）得到答案分布（出现率 ≥5% 记 preferred-model-words），再构造四选一问题，"
        "先单独问 100 次，然后告知「另外 n 个参与者都选了你最少选的那个词」（n∈{1,2,5,10}），每个条件再问 100 次。"
        "10 句 × 6 个前沿模型：6 个模型全部向多数偏移；与自身另一个常用词配对时，偏移由 n=1 的 22 点升到 "
        "n=10 的 49 点；与「意思近但自己没说过的词」配对时 n=10 为 30 点（近）/ 24 点（中）/ 0 点（远）；"
        "n 从 5 到 10 变化 <3 点（部分模型回落）。n=10 时 (w1,wp) 偏移 33 点（Claude-Opus-5.5）→ 73 点（Gemini-3.8-Flash）。"
        "⚠️ 6 模型 / 10 句英文填空题 / temperature 1；「从众」为行为学类比；作者自报、本线未复现。"
    ),
}

NS = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}



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
    assert len(out) == 2, out.keys()
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith("2026-10-27"), out[k]["published"]
    return out


ROW_RE = re.compile(r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| (?:收录|候选|候选（RSS 补充）) \|$")
ANY_ROW_RE = re.compile(r"^\| [0-9-]{10} \| [0-9.]+ \| .* \| (收录|候选|候选（RSS 补充）) \|$")


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 162, meta["n_kept"]
    assert meta["n_dropped"] == 400, meta["n_dropped"]
    assert meta["window_mode"] == "daily", meta["window_mode"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    retried = sorted(q["name"] for q in meta["per_query"] if q["attempts"] != 1)
    assert retried == ["llm-scaling-law", "mm-csmm"], retried
    assert len(items) == 162, len(items)
    ids = [i["arxiv_id"] for i in items]
    assert len(set(ids)) == 162, "duplicate ids in kept"
    assert set(RECOMMENDED) <= set(ids), "recommended id not in kept set"

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    before = set()
    for ln in lines:
        m = ROW_RE.match(ln)
        if m:
            before.add(m.group(1))
    assert not (set(ids) & before), "kept id already in SEEN"
    assert not any(RECOMMENDED[0] in ln for ln in lines), "recommended already present"

    last_row = max(i for i, ln in enumerate(lines) if ANY_ROW_RE.match(ln))
    new_rows = []
    for it in sorted(items, key=lambda x: x["published"], reverse=True):
        aid = it["arxiv_id"]
        title = " ".join(it["title"].split()).replace("|", "\\|")
        status = "收录" if aid in RECOMMENDED else "候选"
        new_rows.append("| %s | %s | %s | %s | %s |" % (FIRST_SEEN, aid, title, it["category"], status))
    lines[last_row + 1:last_row + 1] = new_rows
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
                "first_seen": FIRST_SEEN,
            }
            f.write(json.dumps(rec, ensure_ascii=False) + "\n")

    st = {}
    for ln in lines:
        m = ANY_ROW_RE.match(ln)
        if m:
            st[m.group(1)] = st.get(m.group(1), 0) + 1
    print("SEEN rows added:", len(new_rows), "(收录 2 + 候选 160)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()
