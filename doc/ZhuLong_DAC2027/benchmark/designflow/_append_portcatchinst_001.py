#!/usr/bin/env python3
"""_append_portcatchinst_001.py - append PortCatchInst-001 to D.jsonl"""
import json, os, hashlib

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench"
CASE = "EDA-Eval-DesignFlow-PortCatchInst-001"
JSONL = f"{REPO}/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_D.jsonl"
ASSETS = f"{REPO}/benchmarks/EDA-Eval-DesignFlow/assets/{CASE}"
REF = f"{REPO}/benchmarks/EDA-Eval-DesignFlow/reference/{CASE}"

# dedup guard
with open(JSONL, "rb") as f:
    for line in f:
        if not line.strip():
            continue
        o = json.loads(line)
        if o.get("task_id") == CASE:
            print(f"ALREADY PRESENT: {CASE} — aborting")
            raise SystemExit(1)

check_src = open(f"{REF}/check.py").read()
prompt = open(f"{ASSETS}/prompt.txt").read().rstrip("\n")
task_brief = open(f"{ASSETS}/task_brief.md").read()

# count k_check: distinct condition labels (a)..(p) referenced via _cond("x",...) / _fail("x",...)
import re
labels = set()
for m in re.finditer(r'_cond\(\s*"([a-z])"\s*,', check_src):
    labels.add(m.group(1))
for m in re.finditer(r'_fail\(\s*"([a-z])"\s*,', check_src):
    labels.add(m.group(1))
k_check = len(labels)
print("condition labels found:", sorted(labels), "k_check=", k_check)

disk_sha = hashlib.sha256(check_src.encode()).hexdigest()[:12]
print("check.py disk sha:", disk_sha, "len", len(check_src))

test_rationale = (
    "15 条断言："
    "①zip 含 port_catch.py 且源码无禁用 import(socket/urllib/requests/subprocess/http/pty)且不引用金标模块 "
    "②py_compile port_catch.py 通过 "
    "③在隐藏 B(norf_chain/XI1)上跑候选 exit0 且 out_B.json 非空 "
    "④out_B.json 为合法 JSON 且含 top/instance/subckt/ports/summary 五键 "
    "⑤top==norf_chain 且 instance==XI1 且 subckt==nor2LV "
    "⑥summary 计数 n_ports==7/n_input==2/n_output==1/n_bulk==4/n_instances_in_top==3 "
    "⑦ports 为 7 元列表且每项含 name/direction/net/connected/top_pin "
    "⑧各端口方向匹配 nor2LV PININFO(A:I B:I Y:O 四 bulk:B) "
    "⑨各端口 net 匹配 B 实例行(A→n_int0 B→B1 Y→n_int1 bulk→vbn!/vbp!/vcc!/vss!) "
    "⑩I/O 端口 connected 邻居正确(A→[XI0.Y/O] Y→[XI2.A/I] B→[]) "
    "⑪跨输入反硬编码：在可见 A(nand2_CPSel/XI1)重跑候选 top==nand2_CPSel 且 subckt==nand2LV 且 XI1.Y net==Y 且 connected 含 XI0.Y/O 且 n_instances_in_top==2 "
    "⑫B 输出文本不含 A-only token(nand2_CPSel/nand2LV) "
    "⑬源码无硬编码路径(/home/chengk//proj//wv_trig/port_catch/data) "
    "⑭确定性：3 次重跑 B 输出 sha256 字节一致 "
    "⑮源码不 import/引用金标模块名 port_catch_ref"
)
k_rationale = 15
assert k_rationale == k_check >= 8, f"GATE FAIL: k_rationale={k_rationale} k_check={k_check}"

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        f"assets/{CASE}/nand2_CPSel.netlist",
        f"assets/{CASE}/prompt.txt",
        f"assets/{CASE}/task_brief.md",
    ],
    "entry_point": "outputs/submit.zip",
    "test": check_src,
    "metadata": {
        "domain": "schematic_netlist",
        "track": "faithful",
        "layer": "L1",
        "k_check": k_check,
        "k_rationale": k_rationale,
        "trace_source": {
            "user": "chengk",
            "host": "10.129.35.121",
            "session_file": "1792136569651_4a8f9.messages.json",
            "match_count": 130,
            "real_task_summary": (
                "用户(chengk@10.129.35.121)逐字 U#0「参考路径/home/chengk/work/code/wv_trig/port_catch/code/下的代码，"
                "希望实现以下功能，输入网表中的一个实例化的层级结构，能够用cck的api实现抓取这个实例化的所有端口和连接的连线，"
                "通过连线关系得到这个实例的输入和输出端口链接到的实例，示例网表的位置在.../nand2_CPSel.netlist」——"
                "纯提需求未给根因/修复，符合 A 档前提。trace 演化(176 msg):agent 探索参考代码+search_apis(cck::getMasterInst/dbCrtInstTermByName)"
                "→editor PortCatch.tcl(用 cck Tcl API 抓 inst ports/nets/neighbors)+verify_portcatch.py(Python netlist 解析校验)"
                "→cck 真跑 Segfault(U#119)→用户 U#138 重贴 U#0 原话重申任务→agent 重构。真 cck 商业工具 segfault 不可附加→"
                "B-grade synthesized(金标=纯 Python netlist 解析器:parse .SUBCKT/.PININFO/X-instance→map nets→ports→"
                "找共享 net 的邻居 instance+对端 port+方向→JSON)。真实附件 nand2_CPSel.netlist(2-instance 并行 NAND 交叉连接)作 A；"
                "hidden B=norf_chain.netlist(3-instance 串联 NOR 链 XI0→XI1→XI2，结构反转)反硬编码。"
            ),
        },
        "test_rationale": test_rationale,
    },
}

# verify embedded test bytes == disk check.py bytes
embedded_sha = hashlib.sha256(entry["test"].encode()).hexdigest()[:12]
assert embedded_sha == disk_sha, f"sha mismatch embedded={embedded_sha} disk={disk_sha}"
print("embedded test sha == disk sha:", embedded_sha, "OK")

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify roundtrip
with open(JSONL, "rb") as f:
    last = [l for l in f if l.strip()][-1]
o = json.loads(last)
print("appended. task_id:", o["task_id"])
print("D.jsonl lines now:", sum(1 for l in open(JSONL, "rb") if l.strip()))
print("k_check=", o["metadata"]["k_check"], "k_rationale=", o["metadata"]["k_rationale"])
print("rationale prefix:", o["metadata"]["test_rationale"][:30])
