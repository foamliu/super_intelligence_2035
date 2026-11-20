#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
test_top_k · `top_k.py` 的**离线**校验（**不联网**）
================================================
把运维指令第 2 批（TOP-K 精选排序）的关键行为变成**可回归**断言：
  1. rel 词表用**词边界**匹配：`Harnessing` 不得命中 `harness`、`limit` 不得命中机构 `mit`
  2. q 静态代理：code（github 链接）+ comment/journal_ref + 机构白名单
  3. `rank(use_hn=False)`：total 单调不增、HN 关闭时不联网
  4. `write_outputs`：jsonl 字段齐备 + md 含方法/局限/TOP 表
  5. CLI `--in ... --no-hn`：端到端写出 TOP_K.md / TOP_K.jsonl（退出码 0）
  6. （第 3 批）`takeaway`/`action`：`write_outputs(takeaways=...)` 注入 + `--takeaways-json` 加载

用法：`python3 research/test_top_k.py`   # 全 PASS 退出码 0
"""
import json
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import top_k  # noqa: E402

_RESULTS = []


def check(name, cond, extra=""):
    _RESULTS.append((name, bool(cond)))
    print("[%s] %s%s" % ("PASS" if cond else "FAIL", name, (" — %s" % extra) if extra else ""))


def _item(**kw):
    base = {"arxiv_id": "2610.00001", "version": "v1", "title": "", "authors": [],
            "published": "2026-10-01T00:00:00Z", "updated": "2026-10-01T00:00:00Z",
            "category": "cs.CL", "categories": ["cs.CL"], "summary": "", "comment": "",
            "journal_ref": "", "abs_url": "https://arxiv.org/abs/2610.00001v1",
            "pdf_url": "https://arxiv.org/pdf/2610.00001v1"}
    base.update(kw)
    return base


def test_rel_word_boundary():
    # "Harnessing" 不应命中 harness；"vision-language" 应命中多模态
    it = _item(title="Harnessing Vision-Language Models for Perceptual Quality",
               summary="A study on image quality.")
    rel, raw, matched = top_k.score_rel(it)
    check("rel.no_false_harness", all("agent harness" not in m for m in matched), str(matched))
    check("rel.has_multimodal", any("多模态" in m for m in matched), str(matched))
    # 真命中："agent harness" 应命中
    it2 = _item(title="An agent harness for coding tasks",
                summary="We build a coding agent with tool use.")
    _, _, m2 = top_k.score_rel(it2)
    check("rel.real_harness", any("agent harness" in x for x in m2), str(m2))
    check("rel.tool_use", any("工具/MCP" in x for x in m2), str(m2))


def test_org_word_boundary():
    # "limit" 内不得命中机构 "mit"
    it = _item(title="Push the limit of inference", summary="We push the limit of speed.")
    _, ev, _ = top_k.score_q_static(it)
    check("org.no_substring_mit", all("mit" not in e for e in ev), str(ev))
    it2 = _item(title="A model from MIT", summary="Authors at MIT release a model.")
    _, ev2, _ = top_k.score_q_static(it2)
    check("org.real_mit", any("（mit）" in e for e in ev2), str(ev2))


def test_q_code_and_comment():
    it = _item(title="X", summary="Code available at https://github.com/acme/x.",
               comment="Accepted at NeurIPS 2026")
    pts, ev, code_url = top_k.score_q_static(it)
    check("q.code_pts", pts >= 1.0)
    check("q.code_url", code_url.startswith("https://github.com/acme/x"), code_url)
    check("q.comment_pts", any("comment/journal_ref" in e for e in ev), str(ev))


def test_rank_monotonic_no_hn():
    items = [
        _item(arxiv_id="2610.00001", title="agent harness with tool use for coding agent",
              summary="execution feedback sandbox benchmark SWE-bench.", published="2026-10-01T00:00:00Z"),
        _item(arxiv_id="2610.00002", title="A generic image captioning model",
              summary="We caption images.", published="2026-09-20T00:00:00Z"),
        _item(arxiv_id="2610.00003", title="Small language model distillation for on-device",
              summary="We distill a small model, code at https://github.com/a/b.",
              comment="Accepted", published="2026-09-25T00:00:00Z"),
    ]
    head = top_k.rank(items, pool=10, use_hn=False)
    tots = [h["total"] for h in head]
    check("rank.count", len(head) == 3)
    check("rank.monotonic", all(tots[i] >= tots[i + 1] for i in range(len(tots) - 1)), str(tots))
    check("rank.top_is_relevant", "harness" in head[0]["it"]["title"] or "coding agent" in head[0]["it"]["title"])
    check("rank.hn_off_note", any("HN 未启用" in e for e in head[0]["ev"]))


def test_write_outputs_fields():
    items = [_item(arxiv_id="2610.00009", title="agent harness tool use",
                   summary="code at https://github.com/a/b", comment="Accepted",
                   category="cs.SE", published="2026-10-01T00:00:00Z")]
    head = top_k.rank(items, pool=5, use_hn=False)
    with tempfile.TemporaryDirectory() as d:
        md = os.path.join(d, "TOP_K.md")
        jl = os.path.join(d, "TOP_K.jsonl")
        notes = "- **#1 人工导读**：与 ZhuLong 的执行闭环相关。"
        rows = top_k.write_outputs(head, 5, md, jl, {"n_candidates": 1, "generated": "T"}, 0.6, 0.4,
                                   notes=notes)
        got = [json.loads(l) for l in open(jl, encoding="utf-8") if l.strip()]
        txt = open(md, encoding="utf-8").read()
    need = {"rank", "arxiv_id", "title", "submitted", "primary_category", "rel", "q",
            "total", "relevance_reason", "quality_evidence", "abs_url", "code_url",
            "takeaway", "action"}
    check("write.has_rows", len(got) == 1 and len(rows) == 1)
    check("write.fields", need <= set(got[0].keys()), str(sorted(set(got[0]) ^ need)))
    check("write.md_method", "排序方法" in txt and "局限" in txt and "TOP-5" in txt)
    check("write.md_notes", "TOP-5 导读" in txt and "人工导读" in txt)


def test_takeaways_injection():
    # 第 3 批 A 节：write_outputs(takeaways=...) 应写入 jsonl 并渲染进 md
    items = [_item(arxiv_id="2610.00011", title="agent harness tool use for coding agent",
                   summary="code at https://github.com/a/b", comment="Accepted",
                   category="cs.SE", published="2026-10-01T00:00:00Z")]
    head = top_k.rank(items, pool=5, use_hn=False)
    tk = {"2610.00011": {"takeaway": "可迁移到 ZhuLong 的执行闭环", "action": "试跑"}}
    with tempfile.TemporaryDirectory() as d:
        md = os.path.join(d, "TOP_K.md")
        jl = os.path.join(d, "TOP_K.jsonl")
        top_k.write_outputs(head, 5, md, jl, {"n_candidates": 1, "generated": "T"}, 0.6, 0.4,
                            takeaways=tk)
        got = [json.loads(l) for l in open(jl, encoding="utf-8") if l.strip()]
        txt = open(md, encoding="utf-8").read()
    check("takeaway.jsonl_field", got[0].get("takeaway") == "可迁移到 ZhuLong 的执行闭环",
          str(got[0].get("takeaway")))
    check("takeaway.action_field", got[0].get("action") == "试跑", str(got[0].get("action")))
    check("takeaway.md_rendered", "🎯 takeaway" in txt and "✅ action" in txt and "试跑" in txt)


def test_cli_takeaways_json():
    # 第 3 批 A 节：CLI --takeaways-json 应加载并注入
    with tempfile.TemporaryDirectory() as d:
        pool = os.path.join(d, "pool.json")
        tk = os.path.join(d, "tk.json")
        json.dump({"items": [_item(arxiv_id="2610.00012", title="agent harness",
                                   summary="tool use and code at https://github.com/a/b",
                                   comment="Accepted", published="2026-10-01T00:00:00Z")],
                   "meta": {"generated": "T"}}, open(pool, "w", encoding="utf-8"))
        json.dump({"2610.00012": {"takeaway": "TK", "action": "读原文"}},
                  open(tk, "w", encoding="utf-8"))
        md = os.path.join(d, "TOP_K.md")
        jl = os.path.join(d, "TOP_K.jsonl")
        rc = top_k.main(["--in", pool, "--top", "5", "--pool", "5", "--no-hn",
                         "--out-md", md, "--out-jsonl", jl, "--takeaways-json", tk])
        data = [json.loads(l) for l in open(jl, encoding="utf-8") if l.strip()]
    check("cli.takeaways_rc==0", rc == 0)
    check("cli.takeaways_loaded", data[0].get("takeaway") == "TK" and data[0].get("action") == "读原文")


def test_cli_no_hn():
    with tempfile.TemporaryDirectory() as d:
        pool = os.path.join(d, "pool.json")
        json.dump({"items": [_item(arxiv_id="2610.00010", title="agent harness",
                                   summary="tool use and code at https://github.com/a/b",
                                   comment="Accepted", published="2026-10-01T00:00:00Z")],
                   "meta": {"generated": "T"}}, open(pool, "w", encoding="utf-8"))
        md = os.path.join(d, "TOP_K.md")
        jl = os.path.join(d, "TOP_K.jsonl")
        rc = top_k.main(["--in", pool, "--top", "5", "--pool", "5", "--no-hn",
                         "--out-md", md, "--out-jsonl", jl])
        ok = os.path.exists(md) and os.path.exists(jl)
        data = [json.loads(l) for l in open(jl, encoding="utf-8") if l.strip()] if ok else []
    check("cli.rc==0", rc == 0)
    check("cli.outs", ok)
    check("cli.rows", len(data) == 1 and data[0]["arxiv_id"] == "2610.00010")


def main():
    tests = [test_rel_word_boundary, test_org_word_boundary, test_q_code_and_comment,
             test_rank_monotonic_no_hn, test_write_outputs_fields, test_takeaways_injection,
             test_cli_takeaways_json, test_cli_no_hn]
    for t in tests:
        print("── %s ──" % t.__name__)
        t()
    n = len(_RESULTS)
    f = sum(1 for _, ok in _RESULTS if not ok)
    print("\n[test_top_k] %d/%d PASS" % (n - f, n))
    print("[test_top_k] RESULT:", "PASS" if f == 0 else "FAIL")
    return 0 if f == 0 else 1


if __name__ == "__main__":
    sys.exit(main())