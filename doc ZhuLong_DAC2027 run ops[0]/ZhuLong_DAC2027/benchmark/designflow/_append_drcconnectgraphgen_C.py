#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-DrcConnectGraphGen-001 to EDA-Eval-DesignFlow_C.jsonl."""
import json, os, re

CASE = "EDA-Eval-DesignFlow-DrcConnectGraphGen-001"
REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = f"{REPO}/EDA-Eval-DesignFlow_C.jsonl"
REF = f"{REPO}/reference/{CASE}"
AST = f"{REPO}/assets/{CASE}"

check_py = open(f"{REF}/check.py").read()

rationale = (
    "16 条断言："
    "①(a) submit.zip 合法且含 drc_connect_graph.py "
    "②(b) py_compile 通过 "
    "③(c) 仅标准库(禁 gdspy/calibre/numpy/pandas/sklearn/scipy/matplotlib/aether/pyAether/lxml/bs4/requests) "
    "④(d) 隐藏 B 运行 exit0 且 out_B.html 非空 "
    "⑤(e) HTML 结构完整(含 <html></html> 与 <svg></svg>) "
    "⑥(f) 头部 design 与 generated 出现且与 config_B 一致 "
    "⑦(g) layer-band 数量 == len(layers) "
    "⑧(h) layer-band 的 data-layer 文档顺序 == layers 列表顺序(top→bottom) "
    "⑨(i) 一层一条 band：无重复层 band、无缺失层(集合与 layers 名集合一致且 band 数==唯一层数) "
    "⑩(j) via-edge 数量与 (via,upper,lower) 三元组集合与 kind==via 边完全一致(每条 via 单独画线，非总线合并) "
    "⑪(k) direct-edge 数量与 (upper,lower) 与 kind==direct 边一致(无 data-via) "
    "⑫(l) soft-edge 数量与 (via,upper,lower) 与 kind==soft 边一致(虚线) "
    "⑬(m) shield-arrow 数量与 (via,target) 与 shields 一致，且 shield-label 文本 == label(如 shieldCT/shieldPC) "
    "⑭(n) 各 band 的 y 坐标随层序严格递增(top→bottom) "
    "⑮(o) 每条 via-edge 的 upper band y < lower band y(连接关系正确，上 band 在下 band 之上) "
    "⑯(p) 跨输入守卫：隐藏 B2(层栈/边集/shield 与 A/B 均不同)重跑候选，B2 的 band 数/顺序、via/direct/soft 边、shield 箭头与标签、design/generated 均与参考一致(反硬编码 A/B)"
)

# verify rationale prefix and circled-marker count
assert rationale.startswith("16 条断言："), "rationale must start with '16 条断言：'"
circles = [c for c in rationale if c in "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯"]
assert len(circles) == 16, f"expected 16 circled markers, got {len(circles)}"
labels = sorted(set(re.findall(r'cond\("([a-z])"', check_py)))
assert len(labels) == 16 and labels == list("abcdefghijklmnop"), f"k_check labels={labels}"
print(f"GATE: k_rationale=16 == k_check=16 >= 8 OK")

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": open(f"{AST}/prompt.txt").read(),
    "attachments": [
        f"assets/{CASE}/config_A.json",
        f"assets/{CASE}/task_brief.md",
    ],
    "test": check_py,
    "metadata": {
        "domain": "physical_verify",
        "level": "L2",
        "track": "synthesized",
        "trace_source": {
            "user": "xxchen",
            "host": "hfeg0pkn002",
            "ip": "10.129.2.11",
            "session_file": "1792733394521_26h7a.messages.json",
            "match_count": 262,
            "real_task_summary": (
                "xxchen 自建 DRC 连通性图绘制工具 drcConnect/build_graphV2，让 agent 把 calibreDRC3d_expand.rule 的连接图绘制出来。"
                "U#3 用工具把文档连接图绘制出来；U#4/5/6 反馈层序 top→bottom、一层一条 band(不共用)、不画总线(每 via 单独)、分支加额外 layer box。"
                "agent 深读 build_graphV2.py(CONN 边 (kind,upper,lower,by-label,[lines]) kind∈{via,direct,soft}、一层一 band) 与 drawConnect/query.py(shield_pairs: CTUnet→CT shields M0U=shieldCT、ND_SD→PG shields AT4/NDnet=shieldPC)，"
                "渲染 SVG 带状 HTML(层 band top→bottom、via 线、shield 虚线箭头+标签)，verify_graphV2 计 band/box/conn/statement。"
                "本 B 档重定义为离线渲染器 drc_connect_graph.py(rule_deck.json→out.html)，保留层 band/边/shield 渲染逻辑。"
            ),
        },
        "test_rationale": rationale,
    },
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

n = sum(1 for _ in open(JSONL))
print(f"appended {CASE}; jsonl_C now {n} lines")
print(f"test field size: {len(check_py)} bytes")

# verify the embedded test field byte-equals disk check.py
re_loaded = json.loads(open(JSONL).read().strip().splitlines()[-1])
assert re_loaded["test"] == check_py, "embedded test field != disk check.py"
print("VERIFIED: embedded test field byte-equals disk check.py")
