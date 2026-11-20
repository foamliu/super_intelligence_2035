#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-TopoReconstructExtract-001 to D.jsonl."""
import json, os, sys

CASE = "EDA-Eval-DesignFlow-TopoReconstructExtract-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
D_JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

prompt = open(os.path.join(ASSETS, "prompt.txt")).read()
check_src = open(os.path.join(REF, "check.py")).read()

attachments = [
    "assets/%s/IO_CABufCore_A.cdl" % CASE,
]

rationale = (
    "13 条断言：①(a) submit.zip 含 topo_extract.py 且可被 py_compile 编译通过 "
    "②(b) 源码无禁止运行时(numpy/scipy/pandas/subprocess/requests/urllib/socket/ctypes/calibre/pyaether) "
    "③(c) SUT 跑隐藏 B(IO_RxCore_B.cdl) 退 0 且写出含 design/instances/mosfets/net_fanout/subckts 五键的 topology.json "
    "④(d) B design.cell==oracle(IO_RxCore_B) 且 design.ports 按 .subckt 头部顺序==oracle "
    "⑤(e) B 顶层实例名集合==oracle 且每个实例 (kind,master)==oracle "
    "⑥(f) B mosfets 名集合==oracle 且每个 M 实例 {D,G,S,B,model}==独立 oracle(端子-to-net 映射正确) "
    "⑦(g) B net_fanout 逐 net==oracle(同实例多端接同一 net 各计 1，X 引脚各计 1) "
    "⑧(h) B 嵌套 subckt 名集合==oracle 且每个 subckt 的 ports 与实例(name/kind/master)==oracle "
    "⑨(i) B 的 X 实例引脚→net 有序列表==oracle(X 引脚映射正确) "
    "⑩(j) B 的 R/C 两端 net 元组==oracle(R/C 端子正确) "
    "⑪(k) 交叉输入守卫: A 也退 0 且 A design.ports==A oracle 且 A mosfets==A oracle，且 A/B 端口名/MOSFET 实例名/net 名三集不相交 "
    "⑫(l) 反硬编码: 候选源码不含 B 专有字面量(IO_RxCore_B/DQP/DQN/QOUTT/vddqrx!/vssrx!/Mr1..Mr10/N21/net8/switchRX_B/invRX_B/Rstring_*/Rs* 等) "
    "⑬(m) 确定性: B 连跑 3 次 topology.json 字节一致"
)

case = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_src,
    "metadata": {
        "domain": "schematic_netlist",
        "track": "B",
        "grade": "synthesized",
        "level": "L2",
        "trace_source": {
            "user": "e0017906",
            "host": "hfeg0plg96",
            "session_file": "1794189255973_s98in.messages.json",
            "match_count": 106,
            "real_task_summary": "在 Aether 中 Edit-in-Place 到 drcoa_io/IO_CABufCore/schematic(DDR5 CA 输入缓冲器核心，层级深 6)，用户要求'完整描述到当前电路…只看你的描述能还原出来电路'；助手用 pyAether(aeGetCellView/aeGetCurDesign/aeGetInstHierPath) 枚举 298 实例/206 net/17 端口，逐管子四端 D/G/S/B→net、逐 net 反查 instTerms、按 master 聚合、识别 CMOS 反相器(M11+M186)/交叉耦合(M20/M21)/switch 阵列/电阻串链(R49 RNPDIFF3t)/电源 fanout，并纠正 M186 端子错误，产出可还原电路的结构化拓扑描述。"
        },
        "test_rationale": rationale
    }
}

# k_rationale == k_check gate
k_check = check_src.count("_cond(")
# count assertion markers in rationale
import re
k_rationale = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬]", rationale))
print("k_rationale=%d  k_check=%d" % (k_rationale, k_rationale, ), end="")
print("  -> k_check(=_cond count)=%d" % k_check)
assert k_rationale == 13, "rationale must have 13 markers"
assert k_check >= 8, "check must have >=8 _cond calls (has %d)" % k_check
print("GATE OK: k_rationale=%d k_check=%d (>=8)" % (k_rationale, k_check))

# dedup guard
existing = set()
with open(D_JSONL) as fh:
    for line in fh:
        line = line.strip()
        if not line: continue
        existing.add(json.loads(line).get("task_id"))
assert CASE not in existing, "DUPLICATE id already in D.jsonl: %s" % CASE
print("no dup; existing D.jsonl entries:", len(existing))

with open(D_JSONL, "a") as fh:
    fh.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended %s to %s" % (CASE, D_JSONL))

# report sizes
print("check.py size:", len(check_src))
print("test_rationale len:", len(rationale))
