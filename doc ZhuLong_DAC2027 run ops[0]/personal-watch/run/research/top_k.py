#!/usr/bin/env python3
"""research 线 · TOP-K 精选排序（运维指令 2026-10-03 第 2 批；第 3 批强化）。

对**近期（窗口 <=30d）**论文池按两个维度打分并排序：
- **rel（相关性，0-5）**：与两条在研论文线的相关度 ——
  · **BaiZe**：从零训练的 ~2B 模型 / Mamba-2 x attention 混合 / 规模律 / 预训练数据配比 /
    后训练（SFT/RL）/ 多模态对齐 / 高效推理；
    （第 3 批：相关面放宽到「**存储/芯片 AI 研究院**」视角 → 新增
     `BaiZe·存储/内存技术`、`BaiZe·芯片/加速器` 两组，半导体/EDA/存储相关 AI 论文 `rel` 上调）
  · **ZhuLong**：execution-grounded EDA coding agent / MCP 工具 / generate-execute-refine 闭环 /
    code agent / agent harness / 评测基准（SWE-bench 类）。
- **q（质量，0-5）**：**可操作代理**（不是主观感觉）——
  ① 有官方/作者代码 ② 提出方法或基准（非小增量）③ 社区热度：**HN Algolia** 命中/热度（本机可达）
  ④ 机构/作者（已知实验室白名单）⑤ arXiv `comment` / `journal_ref`。

⚠️ **HF Daily Papers 本机不可达（已实测）** → **不伪造 `hf_daily`**；社区热度**改用 HN Algolia**
（**替代关系**已注明）。

排序：`total = w1*rel + w2*q`（默认 w1=0.6 / w2=0.4，**偏向与本线研工作的相关性**）。

产出：`research/TOP_K.md`（人读）+ `research/TOP_K.jsonl`（机读）。
第 3 批：每条附 **`takeaway`（可借鉴点）+ `action`（建议动作）**（人工，源 `TOP_K_takeaways.json`，
经 `--takeaways-json` 注入；不参与打分）；行动清单见 `research/TAKEAWAYS.md`。

⚠️ 代理指标 != 真实影响力（局限已在 TOP_K.md 注明）。
"""
import argparse
import json
import re
import time
import urllib.parse
import urllib.request
from pathlib import Path

RESEARCH_DIR = Path(__file__).resolve().parent

# 相关性词表（rel）
BAIZE_TOPICS = [
    ("BaiZe·Mamba/混合架构", 1.5,
     ["mamba", "state space model", "state-space model", "ssm", "hybrid attention",
      "linear attention", "gated linear attention", "hybrid architecture"]),
    ("BaiZe·规模律", 1.5,
     ["scaling law", "scaling laws", "compute-optimal", "compute optimal", "chinchilla"]),
    ("BaiZe·预训练/数据配比", 1.0,
     ["pretraining", "pre-training", "pretrain", "data mixture", "data mixing",
      "data curation", "data selection", "tokenizer", "training corpus"]),
    ("BaiZe·后训练(SFT/RL)", 1.0,
     ["post-training", "post training", "supervised fine-tuning", "supervised fine-tun",
      "rlhf", "dpo", "grpo", "reinforcement learning", "reward model", "instruction tuning"]),
    ("BaiZe·小模型/端侧", 1.0,
     ["small language model", "small model", "on-device", "on device", "edge deployment",
      "from scratch", "parameter-efficient", "2b model", "1b model", "3b model"]),
    ("BaiZe·多模态对齐", 1.0,
     ["vision-language", "vision language", "multimodal", "multi-modal", "vlm", "mllm",
      "multimodal alignment", "cross-modal"]),
    ("BaiZe·高效推理", 1.0,
     ["quantization", "quantized", "kv cache", "distillation", "distill", "speculative decoding",
      "efficient inference", "inference optimization", "pruning", "low-bit"]),
    # 运维第 3 批：相关面放宽到「存储/芯片 AI 研究院」视角（半导体/存储相关 AI 论文 rel 上调）
    ("BaiZe·存储/内存技术", 1.5,
     ["memory-semantic", "flash memory", "nand flash", "solid-state drive", "persistent memory",
      "storage", "dram", "hbm", "high bandwidth memory", "memory hierarchy", "memory bandwidth",
      "memory wall", "cxl", "ssd", "memory tiering"]),
    ("BaiZe·芯片/加速器", 1.0,
     ["npu", "asic", "fpga", "tensor core", "hardware accelerator", "silicon", "semiconductor",
      "on-chip", "chip-level", "wafer", "gpu kernel", "cuda kernel", "inference chip", "chiplet"]),
]

ZHULONG_TOPICS = [
    ("ZhuLong·agent harness/code agent", 1.5,
     ["agent harness", "coding agent", "code agent", "software engineering agent", "scaffold",
      "harness", "agentic coding", "repository-level"]),
    ("ZhuLong·工具/MCP", 1.5,
     ["tool use", "tool-use", "tool calling", "tool-calling", "function calling", "function-call",
      "mcp", "model context protocol", "api call", "api invocation"]),
    ("ZhuLong·执行闭环(generate-execute-refine)", 1.0,
     ["execution feedback", "execution-grounded", "generate-execute", "self-debug", "self-repair",
      "iterative refinement", "verifier", "sandbox", "execution result", "runtime feedback"]),
    ("ZhuLong·评测基准", 1.0,
     ["swe-bench", "swebench", "terminal-bench", "benchmark", "evaluation suite",
      "evaluation protocol", "test-time"]),
    ("ZhuLong·EDA/硬件", 1.5,
     ["eda", "electronic design", "verilog", "rtl", "circuit design", "hardware design",
      "chip design", "logic synthesis"]),
]

# 质量代理（q）
ORG_WHITELIST = [
    "google", "deepmind", "meta ai", "meta platforms", "microsoft", "nvidia", "openai",
    "anthropic", "alibaba", "qwen", "deepseek", "zhipu", "glm", "baidu", "tencent", "bytedance",
    "tsinghua", "peking university", "zhejiang university", "shanghai ai lab", "shanghai ailab",
    "stanford", "mit", "uc berkeley", "berkeley", "cmu", "carnegie mellon", "allen institute",
    "allen ai", "mistral", "apple", "amazon", "salesforce", "huawei", "moonshot", "minimax",
    "institute of automation", "shanghai jiao tong",
]
CODE_RE = re.compile(
    r"(github\.com/|gitlab\.com/|huggingface\.co/[\w.\-]+/|"
    r"code (is |will be )?(publicly )?(available|released)|we (release|open[- ]source)|"
    r"open[- ]sourced at)", re.I)
URL_RE = re.compile(r"https?://(?:www\.)?(?:github\.com|gitlab\.com|huggingface\.co)/[\w./\-]+", re.I)
METHOD_RE = re.compile(
    r"(we propose|we introduce|we present a|we develop|new benchmark|a benchmark for|"
    r"we design|novel (method|framework|benchmark|architecture)|we build)", re.I)
INCREMENT_RE = re.compile(r"(survey|a review of|empirical study of|we revisit|position paper)", re.I)
STOPWORDS = set(("a an the of for and or to in on with via using without towards toward at from is are be "
                 "by as into over under we our it its this that these those new large small model models").split())


def _kw_re(kw):
    """词边界匹配：避免 'harness' 误命中 'Harnessing'、'mit' 误命中 'limit' 等。"""
    return re.compile(r"\b" + re.escape(kw) + r"\b", re.I)


_TOPIC_RES = [(label, w, [_kw_re(k) for k in kws]) for label, w, kws in (BAIZE_TOPICS + ZHULONG_TOPICS)]
_ORG_RES = [(o, _kw_re(o)) for o in ORG_WHITELIST]


def _load_pool(path):
    d = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(d, dict) and "items" in d:
        return d["items"], d.get("meta", {})
    if isinstance(d, list):
        return d, {}
    raise ValueError("unknown pool format: %s" % path)


def _haystack(it):
    return " ".join([it.get("title", ""), it.get("summary", ""), it.get("comment", ""),
                     it.get("journal_ref", ""), " ".join(it.get("authors", []) or [])]).lower()


def score_rel(it):
    """相关性 0-5 + 理由。命中 topic 权重求和后封顶 5。"""
    hay = _haystack(it)
    matched = []
    raw = 0.0
    for label, w, res in _TOPIC_RES:
        if any(r.search(hay) for r in res):
            raw += w
            matched.append(label)
    rel = min(5.0, round(raw * 2) / 2.0)
    return rel, raw, matched


def score_q_static(it):
    """不依赖网络的 q 分项：code / method / org / comment。返回 (得分, 证据列表, code_url)。"""
    hay = _haystack(it)
    ev = []
    pts = 0.0
    code_url = ""
    if CODE_RE.search(hay):
        pts += 1.0
        m = URL_RE.search(hay)
        code_url = m.group(0) if m else ""
        ev.append("代码: 摘要/comment 提及代码或仓库%s" % ("（%s）" % code_url if code_url else ""))
    if METHOD_RE.search(it.get("title", "") + " " + it.get("summary", "")) and not INCREMENT_RE.search(it.get("title", "")):
        pts += 1.0
        ev.append("方法/基准: 提出新方法/框架/基准（非小增量）")
    hit_org = next((o for o, r in _ORG_RES if r.search(hay)), None)
    if hit_org:
        pts += 1.0
        ev.append("机构/作者: 命中已知实验室白名单（%s）" % hit_org)
    if (it.get("comment") or "").strip() or (it.get("journal_ref") or "").strip():
        pts += 1.0
        ev.append("arXiv comment/journal_ref: %s" % ((it.get("comment") or it.get("journal_ref"))[:80]))
    return pts, ev, code_url


def _title_tokens(t):
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower()) if w not in STOPWORDS and len(w) > 2}


def hn_lookup(title, timeout=15, min_interval=1.0, _state={"last": 0.0}):
    """HN Algolia 社区热度（替代 HF Daily Papers）。返回 (hn_score_0_1, 证据字符串)。"""
    wait = min_interval - (time.time() - _state["last"])
    if wait > 0:
        time.sleep(wait)
    _state["last"] = time.time()
    q = urllib.parse.urlencode({"query": title, "tags": "story", "hitsPerPage": 5,
                                "restrictSearchableAttributes": "title"})
    url = "https://hn.algolia.com/api/v1/search?" + q
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "watch-research/1.0"})
        with urllib.request.urlopen(req, timeout=timeout) as resp:  # noqa: S310
            data = json.loads(resp.read().decode("utf-8", "replace"))
    except Exception as exc:  # noqa: BLE001
        return 0.0, "HN 查询失败（%s）" % str(exc)[:60]
    mine = _title_tokens(title)
    best_ov, best_pts, best = 0.0, 0, ""
    for h in data.get("hits", []) or []:
        ht = h.get("title") or ""
        toks = _title_tokens(ht)
        if not toks:
            continue
        ov = len(mine & toks) / max(1, len(mine))
        if ov > best_ov:
            best_ov, best_pts, best = ov, int(h.get("points") or 0), ht
    if best_ov >= 0.6 and best_pts >= 5:
        return 1.0, "HN 热度: 命中《%s》(%d points, 标题重合 %.0f%%)" % (best[:70], best_pts, best_ov * 100)
    if best_ov >= 0.6:
        return 0.5, "HN 热度: 命中《%s》(%d points, 弱)" % (best[:70], best_pts)
    return 0.0, "HN 热度: 无显著命中（nbHits=%s）" % data.get("nbHits")


def rank(items, w1=0.6, w2=0.4, pool=60, use_hn=True, hn_interval=1.0):
    """两阶段：先算 base（rel + 静态 q）取前 pool，再做 HN 精修并终排。"""
    scored = []
    for it in items:
        rel, raw, matched = score_rel(it)
        qs, ev, code_url = score_q_static(it)
        base = w1 * rel + w2 * min(5.0, qs)
        scored.append({"it": it, "rel": rel, "rel_raw": raw, "matched": matched,
                       "q_static": qs, "ev": ev, "code_url": code_url, "base": base})
    # 稳定排序：先按日期降序，再按 base 降序（Python sort 稳定 -> 保留日期次序）
    scored.sort(key=lambda x: (x["it"].get("published") or ""), reverse=True)
    scored.sort(key=lambda x: -x["base"])
    head = scored[:pool]
    for s in head:
        if use_hn:
            hn, hnev = hn_lookup(s["it"].get("title", ""), min_interval=hn_interval)
        else:
            hn, hnev = 0.0, "HN 未启用（离线模式）"
        s["hn"] = hn
        s["q"] = min(5.0, s["q_static"] + hn)
        s["total"] = round(w1 * s["rel"] + w2 * s["q"], 3)
        s["ev"] = s["ev"] + [hnev]
    head.sort(key=lambda x: (x["it"].get("published") or ""), reverse=True)
    head.sort(key=lambda x: (x["total"], x["rel"]), reverse=True)
    return head


def _row(s, rank, takeaways=None):
    it = s["it"]
    tw = (takeaways or {}).get(it.get("arxiv_id"), {}) or {}
    return {
        "rank": rank,
        "arxiv_id": it.get("arxiv_id"),
        "title": it.get("title"),
        "submitted": it.get("published"),
        "primary_category": it.get("category"),
        "rel": s["rel"],
        "q": s["q"],
        "total": s["total"],
        "relevance_reason": "；".join(s["matched"]) or "无明显命中（弱相关）",
        "quality_evidence": "；".join(s["ev"]),
        "abs_url": it.get("abs_url"),
        "pdf_url": it.get("pdf_url"),
        "code_url": s["code_url"] or "",
        # 运维第 3 批：可借鉴点 + 建议动作（人工填写，见 TOP_K_takeaways.json）
        "takeaway": tw.get("takeaway", ""),
        "action": tw.get("action", ""),
    }


def write_outputs(head, top, out_md, out_jsonl, meta, w1, w2, notes=None, takeaways=None):
    rows = [_row(s, i + 1, takeaways) for i, s in enumerate(head[:top])]
    with open(out_jsonl, "w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(r, ensure_ascii=False) + "\n")
    L = []
    L.append("# TOP-K 精选论文（研究相关性 x 质量）")
    L.append("")
    L.append("> research 线 · 运维指令 2026-10-03 第 2 批（第 3 批强化）。窗口 **<=30d**（`published` 首次提交）。")
    L.append("> 候选池：%s 篇（生成于 %s）｜ TOP-%d ｜ 权重 **w1(rel)=%s / w2(q)=%s**。" %
             (meta.get("n_candidates", "?"), meta.get("generated", "?"), top, w1, w2))
    L.append("> 第 3 批新增：① 相关面放宽到「**存储/芯片 AI 研究院**」视角（新增 `BaiZe·存储/内存技术`、")
    L.append("> `BaiZe·芯片/加速器` 两组，半导体/EDA/存储相关 AI 论文 `rel` 上调）；② 每条附 **`takeaway`（可借鉴点）+ `action`（建议动作）**，")
    L.append("> 源 `TOP_K_takeaways.json`；③ 行动清单见 `TAKEAWAYS.md`。")
    L.append("")
    L.append("## 排序方法")
    L.append("")
    L.append("- **rel（0-5）**：关键词命中 BaiZe / ZhuLong 主题词表后按权重（1.0/1.5）求和、封顶 5（0.5 粒度）。")
    L.append("- **q（0-5）**：`min(5, code + method + org + comment + hn)`，五项代理各 +1；")
    L.append("  · **code** = 摘要/comment 提及代码或仓库（github/gitlab/huggingface）")
    L.append("  · **method** = 提出新方法/框架/基准（非综述/小增量）")
    L.append("  · **org** = 命中已知实验室白名单")
    L.append("  · **comment** = arXiv `comment` 或 `journal_ref` 非空")
    L.append("  · **hn** = **HN Algolia**（`https://hn.algolia.com/api/v1/search`）标题命中且 points>=5（+1）/ 弱命中（+0.5）")
    L.append("- **total = %s·rel + %s·q**（偏向与本线研工作的相关性）。" % (w1, w2))
    L.append("- **takeaway / action（人工，不参与打分）**：每条给「对我们工作的**可借鉴点**」与**建议动作**")
    L.append("  （`试跑` / `读原文` / `仅备忘`），源 `TOP_K_takeaways.json`。")
    L.append("")
    L.append("## 局限（诚实声明）")
    L.append("")
    L.append("- 代理指标 **!=** 真实影响力：词表命中会**高估**同名但不同义的工作；`q` 的 org 白名单只看文本、拿不到 arXiv affiliations，**可能漏判/误判**。")
    L.append("- **HF Daily Papers 本机不可达（已实测 `Network is unreachable`）** → 社区热度**改用 HN Algolia 替代**；HN 以英文技术圈为主，**中文/冷门方向会低估**。")
    L.append("- `q` 的 code 代理只看摘要/comment 文本，**未逐个打开项目页核验**（避免犯 `200 != 有料` 的错）。")
    L.append("- 排序对 `w1/w2` 敏感；本文给出明确权重，便于复核与调整。")
    L.append("")
    if notes and notes.strip():
        L.append("## TOP-5 导读（人工撰写 · 3-5 句/条）")
        L.append("")
        L.append(notes.strip())
        L.append("")
    L.append("## TOP-%d" % top)
    L.append("")
    L.append("| # | rel | q | total | 标题 | arXiv | 主分类 | 提交 |")
    L.append("|--:|--:|--:|--:|:--|:--|:--|:--|")
    for r in rows:
        L.append("| %d | %s | %s | %s | %s | [%s](%s) | %s | %s |" % (
            r["rank"], r["rel"], r["q"], r["total"], r["title"].replace("|", "\\|"),
            r["arxiv_id"], r["abs_url"], r["primary_category"], (r["submitted"] or "")[:10]))
    L.append("")
    L.append("## 逐条：相关性理由 + 质量证据")
    L.append("")
    for r in rows:
        L.append("- **#%d %s**（arXiv:%s）" % (r["rank"], r["title"], r["arxiv_id"]))
        L.append("  · 🔗 rel=%s（%s）" % (r["rel"], r["relevance_reason"]))
        L.append("  · 🏅 q=%s（%s）" % (r["q"], r["quality_evidence"]))
        if r.get("takeaway") or r.get("action"):
            L.append("  · 🎯 takeaway: %s" % (r.get("takeaway") or "（待填）"))
            L.append("  · ✅ action: %s" % (r.get("action") or "（待填）"))
        L.append("  · abs: %s ｜ pdf: %s%s" % (
            r["abs_url"], r["pdf_url"], (" ｜ 💻 %s" % r["code_url"]) if r["code_url"] else ""))
    L.append("")
    Path(out_md).write_text("\n".join(L) + "\n", encoding="utf-8")
    return rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="TOP-K 精选排序（research 线）")
    ap.add_argument("--in", dest="inp", required=True, help="候选池 JSON（fetch --json --out 产物）")
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--pool", type=int, default=60, help="HN 精修的候选数")
    ap.add_argument("--w1", type=float, default=0.6, help="相关性权重")
    ap.add_argument("--w2", type=float, default=0.4, help="质量权重")
    ap.add_argument("--no-hn", action="store_true", help="离线：跳过 HN Algolia")
    ap.add_argument("--hn-interval", type=float, default=1.0)
    ap.add_argument("--out-md", default=str(RESEARCH_DIR / "TOP_K.md"))
    ap.add_argument("--out-jsonl", default=str(RESEARCH_DIR / "TOP_K.jsonl"))
    ap.add_argument("--notes-md", default=str(RESEARCH_DIR / "TOP_K_notes.md"),
                    help="可选：人工 TOP-5 导读（markdown），存在则嵌入 TOP_K.md")
    ap.add_argument("--takeaways-json", default=str(RESEARCH_DIR / "TOP_K_takeaways.json"),
                    help="可选：人工 takeaway/action 映射（arxiv_id -> {takeaway, action}）")
    args = ap.parse_args(argv)

    items, meta = _load_pool(args.inp)
    meta["n_candidates"] = len(items)
    notes = None
    if args.notes_md and Path(args.notes_md).exists():
        notes = Path(args.notes_md).read_text(encoding="utf-8")
    takeaways = None
    if args.takeaways_json and Path(args.takeaways_json).exists():
        takeaways = json.loads(Path(args.takeaways_json).read_text(encoding="utf-8"))
    head = rank(items, w1=args.w1, w2=args.w2, pool=args.pool,
                use_hn=not args.no_hn, hn_interval=args.hn_interval)
    rows = write_outputs(head, args.top, args.out_md, args.out_jsonl, meta, args.w1, args.w2,
                         notes=notes, takeaways=takeaways)
    print("[top_k] 候选 %d 篇 -> TOP-%d（w1=%s w2=%s）；写 %s / %s" %
          (len(items), len(rows), args.w1, args.w2, args.out_md, args.out_jsonl))
    for r in rows[:5]:
        print("  #%d total=%s rel=%s q=%s %s" % (r["rank"], r["total"], r["rel"], r["q"], r["title"][:80]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())