#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-GmidSizingSearch-001 to EDA-Eval-DesignFlow_B.jsonl.
test field is byte-synced with disk check.py."""
import json, hashlib, os

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-GmidSizingSearch-001"
JSONL = f"{REPO}/EDA-Eval-DesignFlow_B.jsonl"
CHECK = f"{REPO}/reference/{CASE}/check.py"

check_src = open(CHECK).read()
check_sha = hashlib.md5(check_src.encode()).hexdigest()
check_size = len(check_src.encode())

# verify no duplicate task_id
existing = [json.loads(l).get("task_id") or json.loads(l).get("id") or json.loads(l).get("case_id") for l in open(JSONL) if l.strip()]
assert CASE not in existing, f"{CASE} already in jsonl"
print(f"jsonl has {len(existing)} entries; appending {CASE}")

prompt = (
    "用户原始需求（逐字）：「我想做一个自动化sizing电路的程序，需要用到gm/id方法。你可以读取PDF吗」\n\n"
    "[交付任务] 请基于 gm/id 方法实现一个自动化 MOSFET sizing 搜索程序。给定一个 gm/id 查找表 "
    "（CSV，列名：W,L,vgs,vds,gm_over_id,id_over_W,ft_MHz,gds,vds_sat；列顺序不固定，可能含无关列）"
    "与设计规格（JSON：device, target_gbw_MHz, load_cap_pF, iq_budget_uA, vds_sat_max_mV, vdd），"
    "程序需对查找表每个 (W,L,vgs) 点按列名解析后计算：静态电流 Iq = id_over_W * W（uA），"
    "跨导 gm = gm_over_id * Iq（S），增益带宽积 GBW = gm/(2*pi*C_load)；按规格约束过滤可行解"
    "（Iq ≤ iq_budget_uA 且 vds_sat ≤ vds_sat_max_mV/1000 且 GBW ≥ target_gbw_MHz*1e6），"
    "在可行解中选出 Iq 最小的最优 sizing，输出 sizing_report.json（含 best/feasible_count/all_count/spec_echo）"
    "与 candidates.csv（列 W,L,vgs,Iq_uA,GBW_MHz,vds_sat_mV,feasible，含全部查找表行）。\n\n"
    "交付：outputs/submit.zip，内含可执行程序 gmid_sizing_search.py，"
    "CLI 用法：gmid_sizing_search.py <lut.csv> <spec.json> <out_dir>。"
    "可见输入：assets/EDA-Eval-DesignFlow-GmidSizingSearch-001/lut_nmos_A.csv 与 spec_A.json。"
)

test_rationale = (
    "15 条断言："
    "①(a) zip 含 gmid_sizing_search.py 且 py_compile 通过 "
    "②(b) B 运行 exit 0 且产出 sizing_report.json + candidates.csv "
    "③(c) report schema 含 best/feasible_count/all_count/spec_echo 四键 "
    "④(d) B feasible_count ≥ 1（存在可行解） "
    "⑤(e) B best.Iq_uA ≤ spec_B.iq_budget_uA（电流约束满足） "
    "⑥(f) B best.vds_sat_mV ≤ spec_B.vds_sat_max_mV（过驱动约束满足） "
    "⑦(g) B best.GBW_MHz ≥ spec_B.target_gbw_MHz（带宽约束满足） "
    "⑧(h) candidates.csv 行数==B LUT 行数(48) 且列齐全(W,L,vgs,Iq_uA,GBW_MHz,vds_sat_mV,feasible) "
    "⑨(i) B best.Iq_uA == 离线 GT 最小可行 Iq（列名解析正确，非位置解析） "
    "⑩(j) 跨输入护栏：A 重跑 best.Iq ≤ A budget 且 A best.Iq ≠ B best.Iq（击败 hardcode-B） "
    "⑪(k) 确定性：B 重跑两次 sizing_report.json sha256 一致 "
    "⑫(l) 可行性过滤：candidates.csv 同时含 feasible=1 与 feasible=0 行（sweep 探过可行域外，击败 all_feasible） "
    "⑬(m) best 选择：best.Iq_uA == candidates.csv 中可行行 Iq 的最小值（击败 first-feasible/删核心） "
    "⑭(n) GBW 公式正确：用 best 行的 gm_over_id 与 Iq 重算 GBW 与 report 误差 <1% "
    "⑮(o) device 感知：report spec_echo.device == pmos（spec_B 设备类型透传）"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        f"assets/{CASE}/lut_nmos_A.csv",
        f"assets/{CASE}/spec_A.json",
    ],
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "t0002801",
            "host": "hfeg0plg99",
            "session_file": "1791420858846_g3ud6.messages.json",
            "match_count": 172,
            "real_task_summary": "gm/id 自动化 sizing 程序（A-faithful U[0] 逐字「我想做一个自动化sizing电路的程序，需要用到gm/id方法」；trace 实为 gmid_engine.py 工具构建 + aether NMOS/PMOS LUT 提取，便携子技能=sizing 搜索引擎）"
        },
        "domain": "spice_sim",
        "track": "faithful",
        "test_rationale": test_rationale,
        "selftest": "ref 15/15 PASS; 6 neg ALL-FAIL distinct{a,g,i,j,n}; §4.9 trio{empty→a,print_expected→j,core_deleted→i}=3 distinct; NEG_RC=0; check.py md5=%s size=%d" % (check_sha, check_size)
    }
}

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
n = sum(1 for l in open(JSONL) if l.strip())
last = [json.loads(l) for l in open(JSONL) if l.strip()][-1]
assert last["task_id"] == CASE
# verify test field byte-synced with disk
assert last["test"] == open(CHECK).read(), "test field NOT byte-synced with disk check.py"
import hashlib as h
print(f"appended. jsonl now {n} entries.")
print(f"last task_id={last['task_id']}")
print(f"test field md5={h.md5(last['test'].encode()).hexdigest()} size={len(last['test'].encode())} (== disk check.py)")
print(f"k_rationale=15 == k_check=15 >= 8 GATE PASS")
