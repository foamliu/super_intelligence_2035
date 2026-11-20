#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十六轮（本地 2026-11-01 18:00 PM「晚 2」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-11-01-pm-fetch-r126-seen.json`（`--fetch --seen`，`generated=2026-11-01T10:02:14Z`）
  - `raw/2026-11-01-pm-idlist-r126a.xml`（官方 Atom 元数据，4 条短名单中取 2 条）

动作：断言 fetch 结果 → SEEN 状态「候选」→「收录」（不新增行）→ `papers.jsonl` 追加 2 条。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-11-01-pm-fetch-r126-seen.json"
XML = BASE / "raw" / "2026-11-01-pm-idlist-r126a.xml"

RECOMMENDED = ["2610.37796", "2610.40588"]
FIRST_SEEN = "2026-11-01"
EXPECT_PUB = {"2610.37796": "2026-10-27", "2610.40588": "2026-10-29"}

AREAS = {
    "2610.37796": ["机制可解释性", "表征流形", "星期环", "扰动敏感度", "steering", "科普"],
    "2610.40588": ["agent 安全", "多智能体", "线性探针", "activation probing", "科普"],
}

SUMMARY_ZH = {
    "2610.37796": (
        "已有工作发现「星期几」在语言模型激活空间里排成一个**圆环**，并据此认为沿圆环移动等于日期/时间的**连续**变化。"
        "本文检验这个「连续流形假设」：① 以恒定角速度沿拟合圆环做 steering（层 2 注入、层 28 读出），"
        "**行为与残差的变化在星期附近极慢、在相邻星期之间的弧段很快**，呈**台阶状**；"
        "② 用 Jacobian 的 Frobenius 范数画极坐标敏感度图，得到**七个以星期为中心的低敏感「辐条」**"
        "（且向外径向延伸，说明不是「只沿切向走」造成的假象）；"
        "③ 「一天中的时刻」几乎不在环上：时刻修饰词在环平面内造成的角位移 **≤6.30°**，"
        "远小于相邻星期质心的 **44.33°–59.81°**，且与「very rainy」这类非时间修饰词同量级；"
        "沿环 steering 对预测小时的改变 **<0.02h**，而沿「late–early」平面外方向同范数 steering 改变 **−1.8h / +1.1h**；"
        "④ 「不确定性」不填充两星期之间的弧段，而是让表示**沿两根星期辐条向内收缩**；"
        "⑤ FineWeb 的 **49,678 条**（574,217 篇文档）以星期结尾的 16-token 片段显示："
        "上下文主要**整体平移**七个星期表示（减去每段均值后，段内 RMS 半径从 **0.65** 降到 **0.23** 个环半径），"
        "而不是把它们旋转到中间区。主实验模型 Llama-3.1-8B，另在 Mistral-7B-v0.1 / GPT-2 XL 复核。⚠️ 作者自报、本线未复现。"
    ),
    "2610.40588": (
        "多智能体共享通道与凭据时，一个 agent 可能被同伴**招募**去违规（例：套出部署 token）。"
        "输出过滤只能查**已经写出来**的内容，本文问：**能不能在它「即将让步」之前就预警**？"
        "受控设定：六个场景，peer 最多施压 **20 轮**要目标吐出一个秘密；目标常常先拒绝、后让步。"
        "作者在**每次模型调用、输出落笔之前**读激活，用**线性探针**判断这一次是否会泄密。"
        "在 held-out 的 Qwen3-32B episode 上，把阈值设到只标记 **5%** 的良性调用时，探针抓住 **82%** 的泄密调用；"
        "同样标记率下，零样本「决策模型」监控器只抓 **26%**。在 gpt-oss-20b 的**推理**激活上，探针 **AUROC 0.91**。"
        "⚠️ 作者如实给出三条限制：① 用同一批调用训练的 **bag-of-words 分类器**表现接近 ⇒ 增益主要来自**有标签训练**，"
        "而非「激活」本身；② 探针也会标记**被允许的披露**（更像在读「即将披露」而非「是否违规」）；"
        "③ 预警是**短程**的，且「一报警就停机」会停掉大多数良性 episode（加一道文本检查也修不好）。⚠️ 作者自报、本线未复现。"
    ),
}


def load_official():
    root = ET.parse(XML).getroot()
    ns = {"a": "http://www.w3.org/2005/Atom", "x": "http://arxiv.org/schemas/atom"}
    out = {}
    for e in root.findall("a:entry", ns):
        aid = e.find("a:id", ns).text.split("/abs/")[-1].split("v")[0]
        out[aid] = {
            "title": " ".join(e.find("a:title", ns).text.split()),
            "authors": [a.find("a:name", ns).text for a in e.findall("a:author", ns)],
            "published": e.find("a:published", ns).text,
            "updated": e.find("a:updated", ns).text,
            "category": e.find("x:primary_category", ns).attrib["term"],
        }
    assert len(out) == 4, len(out)
    for k in RECOMMENDED:
        assert k in out, "missing %s in id_list" % k
        assert out[k]["published"].startswith(EXPECT_PUB[k]), (k, out[k]["published"])
    return out


ANY_ROW_RE = re.compile(
    r"^\| [0-9-]{10} \| ([0-9.]+) \| .* \| [^|]+ \| (收录|候选|候选（RSS 补充）) \|$"
)
ROW_RE = re.compile(r"^\| [0-9-]{10} \| ([0-9.]+) \|")


def main():
    official = load_official()
    payload = json.load(FETCH.open(encoding="utf-8"))
    meta = payload["meta"]
    items = payload["items"]
    assert meta["n_queries"] == 15, meta["n_queries"]
    assert meta["n_kept"] == 0, meta["n_kept"]
    assert meta["n_dropped"] == 600, meta["n_dropped"]
    assert meta["window_mode"] == "weekend_batch", meta["window_mode"]
    assert float(meta["window_hours"]) == 120.0, meta["window_hours"]
    assert all(q["ok"] and q["status"] == 200 for q in meta["per_query"]), "query not clean"
    attempts = [q["attempts"] for q in meta["per_query"]]
    assert attempts == [1] * 6 + [2] + [1] * 8, attempts
    assert len(items) == 0, len(items)
    dropped = meta["dropped"]
    n_seen = sum(1 for d in dropped if d[1] == "already in SEEN")
    n_stale = len(dropped) - n_seen
    assert (n_seen, n_stale) == (558, 42), (n_seen, n_stale)
    print("dropped: already_in_SEEN=%d stale=%d" % (n_seen, n_stale))

    lines = SEEN.read_text(encoding="utf-8").split("\n")
    hit = {}
    for i, ln in enumerate(lines):
        m = ROW_RE.match(ln)
        if m and m.group(1) in RECOMMENDED:
            hit[m.group(1)] = i
    assert set(hit) == set(RECOMMENDED), hit
    for aid, i in hit.items():
        assert lines[i].rstrip().endswith("| 候选 |"), lines[i]
        lines[i] = lines[i].rstrip()[: -len("候选 |")] + "收录 |"
        assert lines[i].endswith("| 收录 |"), lines[i]
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
            st[m.group(2)] = st.get(m.group(2), 0) + 1
    print("SEEN lines:", len(lines), "(+0)")
    print("SEEN status:", st, "sum", sum(st.values()))
    print("papers.jsonl lines:", sum(1 for _ in PAPERS.open(encoding="utf-8")))


if __name__ == "__main__":
    main()
