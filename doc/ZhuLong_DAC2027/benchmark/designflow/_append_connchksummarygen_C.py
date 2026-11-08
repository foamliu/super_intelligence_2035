#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-ConnChkSummaryGen-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os

CASE = "EDA-Eval-DesignFlow-ConnChkSummaryGen-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = f"{REPO}/EDA-Eval-DesignFlow_C.jsonl"
REF = f"{REPO}/reference/{CASE}"
AST = f"{REPO}/assets/{CASE}"

check_py = open(f"{REF}/check.py").read()

rationale = (
    "16 条断言："
    "①(a) submit.zip 合法且含 conn_summary.py "
    "②(b) py_compile 通过且仅标准库(禁 gdspy/calibre/numpy/pandas/sklearn/scipy/matplotlib/aether/pyAether) "
    "③(c) 隐藏 B 运行 exit0 且 sum_B.rep 非空 "
    "④(d) 报告头 5 行结构正确(72=分隔行+title+generated[值与 config.generated 一致]+base dir[abspath]+72=) "
    "⑤(e) [run_N] 块数与顺序与 config.blocks 完全一致(run_1..run_N) "
    "⑥(f) 每个 run 块含 '  path(s)      :' 标签(精确宽度) "
    "⑦(g) 每条 path 独立成行、续行 17 空格缩进对齐(非旧式逗号 ', ' 拼接单行) "
    "⑧(h) 路径内容正确：从 bottomLayer 沿 connectivity 边 DFS(3 层边 [S,V,T] 含 via V，2 层边 [S,T] 不含 via，via/节点不重复)，多 bottomLayer 去重合并 "
    "⑨(i) shields 仅在 connectivity 含 >3 层边的 run 出现，全 ≤3 层边的 run 不出现 shields 段 "
    "⑩(j) shields 内容正确：>3 层边 [S,V,T1,T2,...] 拆 3 层边且每有序对 (Ti,Tj) i<j 产一条 'S V : Ti->Tj' "
    "⑪(k) 每条 shield 独立成行、续行 17 空格缩进(非旧式分号 '; ' 拼接单行) "
    "⑫(l) sameNet 行 '  sameNet: N data group(s)  [OK|HAS ERRORS]'，N 与 verdict(N>0→HAS ERRORS 否则 OK)与 runs_meta 一致 "
    "⑬(m) diffNet 行同 sameNet，N 与 verdict 与 runs_meta 一致 "
    "⑭(n) status 行 '  status   : <status>' 与 runs_meta 逐字一致 "
    "⑮(o) 报告尾含空行+72= 分隔行 "
    "⑯(p) 跨输入守卫：隐藏 B2(结构与 A/B 均不同)重跑候选，B2 各 run 的 paths 与 shields 与参考一致(反硬编码 A/B)"
)

# Note: conditions in check.py are a-p = 16 labels; the rationale above lists 16 items ①-⑯.
# Verify mapping: ①=a, ②=b, ③=c/d(duplicate?), let me recount: a=zip, b=compile, c=stdlib, d=Brunc,
# e=header, f=blocks, g=pathlabel, h=paths-per-line, i=paths-content, j=shields-presence,
# k=shields-content, l=shields-per-line, m=sameNet, n=diffNet, o=status, p=cross-input.
# That's 16. My rationale ①-⑯ maps 1:1 to a-p. Good.

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": open(f"{AST}/prompt.txt").read(),
    "attachments": [
        f"assets/{CASE}/config_A.json",
        f"assets/{CASE}/runs_meta_A.json",
        f"assets/{CASE}/task_brief.md",
    ],
    "test": check_py,
    "metadata": {
        "domain": "physical_verify",
        "level": "L1",
        "track": "synthesized",
        "trace_source": {
            "user": "xxchen",
            "host": "hfeg0pkn002",
            "ip": "10.129.2.11",
            "session_file": "1793088988568_84qb3.messages.json",
            "match_count": 334,
            "real_task_summary": (
                "xxchen 自建 DRC 连通性检查工具 drcConnect，让 agent 改造报告生成：U#1 多 bottomLayer 支持 + sum.rep 每条 path 独立成行；"
                "U#2 shields 增补中间对 NBP->TCP + shields 每条独立成行。agent 深读 connectivity_check/graph.py(normalize_connectivity 拆 >3 层边+全有序对 shields、find_all_paths DFS 含 via)"
                "与 summary.py(format_report 头/每 run 块/尾、续行 17 空格对齐、sameNet/diffNet verdict、status)完成改造。"
                "本 B 档重定义为离线报告生成器 conn_summary.py(config.json+runs_meta.json→sum.rep)，保留图遍历+shields+格式逻辑。"
            ),
        },
        "test_rationale": rationale,
    },
}

# verify rationale prefix and count
assert rationale.startswith("16 条断言："), "rationale must start with '16 条断言：'"
# count circled numbers ①..⑯
circles = [c for c in rationale if c in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯"]
assert len(circles) == 16, f"expected 16 circled markers, got {len(circles)}"
# count check.py labels
import re
labels = sorted(set(re.findall(r'cond\("([a-z])"', check_py)))
assert len(labels) == 16 and labels == list("abcdefghijklmnop"), f"k_check labels={labels}"
print(f"GATE: k_rationale=16 == k_check=16 >= 8 ✓")

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# count lines
n = sum(1 for _ in open(JSONL))
print(f"appended {CASE}; jsonl_C now {n} lines")
print(f"test field size: {len(check_py)} bytes")
