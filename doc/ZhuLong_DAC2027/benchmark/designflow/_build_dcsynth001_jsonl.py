#!/usr/bin/env python3
"""Build the EDA-Eval-DesignFlow-DCSynth-001 jsonl entry and append to A.jsonl."""
import json, os, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-DCSynth-001"
A_JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)

prompt = open(os.path.join(ASSETS, "prompt.txt")).read().rstrip("\n") + "\n"
test = open(os.path.join(REF, "check.py")).read()

# confirm test == disk sha roundtrip
test_sha_disk = hashlib.sha256(open(os.path.join(REF, "check.py"), "rb").read()).hexdigest()

attachments = [
    {"name": "task_brief.md", "source": "task_brief.md",
     "desc": "交付接口与文件位置说明（≤3 行，A 档 trace-faithful：只写接口不写要做什么）"},
    {"name": "rtl/addr_to_rowcol_region.v", "source": "rtl/addr_to_rowcol_region.v",
     "desc": "待综合 RTL：addr_to_rowcol_region 顶层 + 6 个子模块（纯组合 9-bit 地址译码）"},
    {"name": "lib/stdcells_ac_FF_1p3_m40c.db", "source": "lib/stdcells_ac_FF_1p3_m40c.db",
     "desc": "本地标准单元库 stub（FF 1.3V -40C，库名 stdcells_ac_FF_1p3_m40c）"},
]

test_rationale = (
    "16 条断言："
    "①(a) zip 含 SDC(含 create_clock) + synth.tcl(含 analyze/compile) + run_dc.sh(含 dc_shell) 三个核心文件 "
    "②(b) SDC 创建时钟(create_clock)且设输入/输出延迟(set_input_delay/set_output_delay) "
    "③(c) SDC 设驱动单元(set_driving_cell)与负载(set_load)及 DRC(set_max_transition + set_max_capacitance 或 set_max_fanout) "
    "④(d) SDC 引用的端口与 A 顶层端口一致(输入 RA;输出 row/col/region/valid) "
    "⑤(e) synth.tcl 设 target_library 与 link_library 且取自 $TARGET_DB 环境变量 "
    "⑥(f) synth.tcl 经 analyze + elaborate + current_design + link 读入设计 "
    "⑦(g) synth.tcl 保层次: compile_enable_register_merging=false 且 compile_ultra -no_autoungroup(或 set_dont_touch 子设计) 且 write -hierarchy "
    "⑧(h) synth.tcl source $SDC_FILE 应用约束且生成前后报告(report_timing + report_area + report_constraint 或 check_design) "
    "⑨(i) synth.tcl 写出映射结果: write -format ddc -hierarchy + write -format verilog -hierarchy + write_sdc "
    "⑩(j) run_dc.sh 定义可覆盖环境变量 TARGET_DB/TOP_DESIGN/RTL_FILE/SDC_FILE/OUTPUT_DIR(${VAR:-default}) "
    "⑪(k) run_dc.sh 有健全性检查(dc_shell 在 PATH + 必需文件存在)并以 dc_shell -f synth.tcl 启动 "
    "⑫(l) run_dc.sh 有综合后检查(mapped netlist 与 ddc 存在,缺失则 exit 非 0) "
    "⑬(m) 泛型: synth.tcl 用 $TARGET_DB/$RTL_FILE/$SDC_FILE/$TOP_DESIGN 环境变量而非硬编码 A 字面量(库名/顶层不出现) "
    "⑭(n) B 执行: 以 B 环境(TOP_DESIGN=pri_enc_16to4/RTL_FILE=B/TARGET_DB=B/SDC_FILE=B)bash -n run_dc.sh 通过且 tcl 结构确认 synth.tcl source $SDC_FILE 与读 $RTL_FILE "
    "⑮(o) 随机化: 3 seed 打乱 B 环境取值后 bash -n + tcl 结构结论一致 "
    "⑯(p) 鲁棒: run_dc.sh 遇必需文件缺失(RTL_FILE 指向不存在文件)退出非 0"
)

case = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": [
        "outputs/submit.zip 含 SDC 约束文件 + Design Compiler synth.tcl + run_dc.sh 运行脚本（三者同目录）",
    ],
    "test": test,
    "budget": {"max_turns": 40},
    "metadata": {
        "trace_source": {
            "user": "johnl",
            "host": "hfeg0pfn119",
            "session_file": "1790217607403_2xcr9",
            "match_count": 68,
            "real_task_summary": (
                "在 /home/johnl/spiceTdc/primelib_char_T_IsmTop/dc_addr_to_region 用 Design Compiler "
                "对 addr_to_rowcol_region.v 做层次保留综合：编写 SDC 约束 + synth.tcl 综合脚本 + run_dc.sh "
                "运行脚本，使用本地库 stdcells_ac_FF_1p3_m40c.db"
            ),
        },
        "domain": "digital",
        "track": "faithful",
        "level": "L1-boundary",
        "test_rationale": test_rationale,
        "judge": "static-structural (no dc_shell launch; bash -n + python tcl structural pass on hidden B)",
        "hidden_B": "pri_enc_16to4 (16-bit priority encoder, 4 sub-modules) + stdcells_TT_0p8_25c.db, differs from A in design/ports/library/corner",
    },
}

# append (avoid duplicate)
existing = []
if os.path.exists(A_JSONL):
    for line in open(A_JSONL):
        d = json.loads(line)
        if d.get("task_id") == CASE:
            print("ALREADY PRESENT, replacing")
            existing = [d for d in (json.loads(l) for l in open(A_JSONL)) if d.get("task_id") != CASE]
            break
    else:
        existing = [json.loads(l) for l in open(A_JSONL)]
with open(A_JSONL, "w") as f:
    for d in existing:
        f.write(json.dumps(d, ensure_ascii=False) + "\n")
    f.write(json.dumps(case, ensure_ascii=False) + "\n")

# verify roundtrip: test field == disk
test_sha_field = hashlib.sha256(test.encode("utf-8")).hexdigest()
print("appended", CASE)
print("test sha disk :", test_sha_disk)
print("test sha field:", test_sha_field)
print("roundtrip OK   :", test_sha_disk == test_sha_field)
print("A.jsonl lines  :", sum(1 for _ in open(A_JSONL)))

# gate triple check
import re
_CIRCLED = ["①","②","③","④","⑤","⑥","⑦","⑧","⑨","⑩","⑪","⑫","⑬","⑭","⑮","⑯","⑰","⑱","⑲","⑳"]
kr = sum(1 for m in _CIRCLED if m in test_rationale)
labels = set(re.findall(r"\"\(([a-z])\)", test))
alphabet = "abcdefghijklmnopqrstuvwxyz"
kc = 0
for ch in alphabet:
    if ch in labels: kc += 1
    else: break
print("gate_triple: k_rationale=%d k_check=%d consistent=%s" % (kr, kc, "✓" if kr == kc and kc >= 8 else "✗"))
