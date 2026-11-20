#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""第一百二十四轮（本地 2026-10-31 18:00 PM「晚 2」轮）台账落盘。

输入（全部为实测原始文件，不手抄）：
  - `raw/2026-10-31-pm-fetch-r124-seen.json`（`--fetch --seen`，`generated=2026-10-31T10:02:24Z`）
  - `raw/2026-10-31-pm-idlist-r124.xml`（官方 Atom 元数据，2 条）

动作：
  1) 断言：15 查询全 `ok` / `HTTP 200`、`kept 0` / `dropped 600`、
     `window_mode=weekend_batch`（120h，周六自动放宽）、`items==0`；
  2) `SEEN.md`：**不新增行**（本批 217 条已在 r122 入账）；只把 2 篇推荐论文的
     状态由「候选」翻为「收录」；
  3) `papers.jsonl`：追加 2 条（元数据取自官方 id_list XML）；
  4) 打印台账统计，供心跳引用。
"""
import json
import re
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent  # research/
SEEN = BASE / "SEEN.md"
PAPERS = BASE / "papers.jsonl"
FETCH = BASE / "raw" / "2026-10-31-pm-fetch-r124-seen.json"
XML = BASE / "raw" / "2026-10-31-pm-idlist-r124.xml"

RECOMMENDED = ["2610.40530", "2610.38957"]
FIRST_SEEN = "2026-10-31"
EXPECT_PUB = {"2610.40530": "2026-10-29", "2610.38957": "2026-10-28"}
EXPECT_ATTEMPTS = [1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, 1]

AREAS = {
    "2610.40530": ["多模态", "MLLM 评测", "视觉计数", "appearance–entity", "镜面反射 / 玻璃", "科普"],
    "2610.38957": ["多模态", "MLLM 评测", "多实例多物体", "视觉定位 / 属性绑定", "科普"],
}

SUMMARY_ZH = {
    "2610.40530": (
        "照片里的「看见几次」和「有几个东西」不是一回事：一个物体在镜子里出现三次，实体仍只有一个；"
        "隔着玻璃看见的也是同一个实体。作者建 **PhysCount**：546 张真实照片、651 个目标组、4,595 道人工题、"
        "137 类目标（7,086 个目标出现 = 2,416 直接 + 3,996 镜面反射 + 674 隔玻璃；475 组里有实体只能通过反射/玻璃看到；"
        "422 组里至少一个实体出现多次），四类问题分别考「数出现」「数实体」「数成像方式」「把多次出现归到同一实体」。"
        "40 个 MLLM 上：数「出现」明显容易，数「实体」与跨出现匹配明显更难；最强 Gemini 3.7 Flash 整体 **Score 36.45**、"
        "**全组全对率仅 13.36%**（5 位人类 97.10 / 95.98）。提高分辨率只改善「看得见」（Score 21.04→28.84，全组正确率在 1,024 px 后不再涨）；"
        "把同组问题一起给出，Qwen3.8-27B 全组正确率 **7.37% → 23.96%**。⚠️ 作者自报、本线未复现。"
    ),
    "2610.38957": (
        "「找威利」式的场景：一张图里同类物体有多个实例（多实例 × 多类别），模型要在大量相似干扰项中"
        "把「哪一个」唯一指认出来，而不是只认出「这类东西在不在」。作者建 **MIMO-Bench**：**3,802** 个图像–问题对，"
        "覆盖属性绑定与计数两类任务；每个指代表达都要组合多个视觉子任务才能唯一定位。"
        "结果：在既有基准上表现亮眼的开源（InternVL、QwenVL）与闭源（Gemini、GPT-5）模型在 MIMO 设置下**显著掉分**，"
        "说明「认出类别」与「在同类多实例中定位到唯一目标」是两种能力。⚠️ 数字与结论均作者自报、本线未复现。"
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
    assert len(out) == 2, out.keys()
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
    assert attempts == EXPECT_ATTEMPTS, attempts
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
