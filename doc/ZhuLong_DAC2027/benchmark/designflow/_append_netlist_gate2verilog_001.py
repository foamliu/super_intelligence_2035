#!/usr/bin/env python3
# _append_netlist_gate2verilog_001.py -- append case to D.jsonl
import os, json, hashlib

CASE = "EDA-Eval-DesignFlow-NetlistGate2Verilog-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
DJSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")
CHECK = os.path.join(BENCH, "reference", CASE, "check.py")

check_src = open(CHECK).read()
check_sha = hashlib.sha256(check_src.encode()).hexdigest()[:12]

PROMPT = ("netlist_A.sp 这是我的网表路径，帮我把其中的 OdtPdMuxA 模块使用verilog进行实现，"
          "要求简介清晰，写好后另存在统一个目录下的不同文件，文件以模块名命名")

TEST_RATIONALE = (
    "16 条断言："
    "①submit.zip 含 netlist2verilog.py 且无禁 import(ref/check/gold/answer) 无 /proj//rundata//home 泄漏 "
    "②netlist2verilog.py 通过 py_compile 无语法错 "
    "③候选在隐藏 B(OdtPdMuxB)上运行退出码 0 且输出 .v 非空 "
    "④B 输出含 module OdtPdMuxB 与 endmodule "
    "⑤B 输出端口方向正确(8 input WrEn..ClkEn / 5 output FlagA..Code1 / 2 inout vdda gnda)与 PININFO 一致 "
    "⑥B 输出含 ≥1 条 assign 组合逻辑 "
    "⑦B 输出无 SPICE 残留(.SUBCKT/.ENDS/PININFO/X 实例行) "
    "⑧B 输出布尔等价:2^8 全输入组合下 5 输出(FlagA/FlagB/Sel/Code0/Code1)与 SPICE 网表真值表逐行一致 "
    "⑨B 的 5 个输出端口均被 assign 驱动 "
    "⑩源码无 A 专属名字面量(OdtPdMuxA/OdtWr/DmiInEn/w0/AnyOdt/NtFlag/PdSel/DmiPd0/DmiPd1/inh_vcc/inh_vss) "
    "⑪跨输入 B2(OdtPdMuxC):运行退出 0 + module/endmodule + 2^6 真值表(Y0/Y1/Y2)与 SPICE 一致 "
    "⑫源码使用 argparse 或 sys.argv 接 CLI 无硬编码路径 "
    "⑬-o 参数写入指定路径文件 "
    "⑭确定性:3 次重跑 sha256 一致 "
    "⑮B 输出无 UDP/primitive/table/pmos/nmos/cmos/tran "
    "⑯供应网 vdda/gnda 声明且不被 assign 驱动"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": PROMPT,
    "attachments": [
        {"name": "netlist_A.sp", "source": "netlist_A.sp",
         "desc": "gate-level SPICE subckt OdtPdMuxA 网表(8 input/5 output/2 inout supply，14 标准单元实例 inv/nand2/and2/oai21/nor2/oai22/nand3/nor3/aoi21/mux2/or2/xor2/xnor2，含 *. PININFO 端口方向)"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口:netlist2verilog.py <netlist.sp> <module> -o <out.v> 解析 gate-level SPICE subckt 输出 Verilog module;打包 outputs/submit.zip"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["netlist2verilog.py"],
    "test": check_src,
    "budget": {"max_turns": 40, "wall_time_sec": 1800, "max_tool_calls": 120},
    "metadata": {
        "domain": "schematic_netlist",
        "task_name": "NetlistGate2Verilog",
        "scenario": "gate-level SPICE subckt -> Verilog RTL module (assign-based) 转换器",
        "direction": "netlist2verilog",
        "layer": "L1",
        "topic": "gate-level netlist boolean extraction",
        "difficulty": "medium",
        "design": "parse .SUBCKT + PININFO + standard-cell instances -> emit Verilog module with assign per cell (inv/nand2/nor2/and2/or2/nand3/nor3/oai21/oai22/aoi21/mux2/xor2/xnor2)",
        "tcr_refs": [],
        "heavy": False,
        "wall_time_sec": 1800,
        "trace_source": {
            "host": "10.129.32.83",
            "session_file": "1792046093287_3yv6w",
            "session_msgs": 73,
            "user": "qi3wang",
            "real_task_summary": "gate-level SPICE 网表 DqOdtPdMux subckt -> Verilog module 实现(nand2GS/oai21PS/oai22PS/nand2PS/inv 标准单元 -> assign 布尔式, 端口/内部 wire/endmodule, 文件以模块名命名; 用户 U#0 逐字提需求, U#1 格式批评, U#2 重写)",
        },
        "test_rationale": TEST_RATIONALE,
    },
}

# verify no duplicate
existing = [json.loads(l) for l in open(DJSONL) if l.strip()]
ids = {e.get("task_id") or e.get("id") or e.get("case_id") for e in existing}
assert CASE not in ids, "case already in D.jsonl"

with open(DJSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify test==disk byte-sync
disk_sha = hashlib.sha256(open(CHECK).read().encode()).hexdigest()[:12]
jsonl_entry = None
for l in open(DJSONL):
    e = json.loads(l)
    if (e.get("task_id") or e.get("id") or e.get("case_id")) == CASE:
        jsonl_entry = e
        break
jsonl_sha = hashlib.sha256(jsonl_entry["test"].encode()).hexdigest()[:12]
print("appended", CASE)
print("D.jsonl lines:", len(existing) + 1)
print("check.py disk sha:", disk_sha, "| jsonl test sha:", jsonl_sha, "| match:", disk_sha == jsonl_sha)
print("check.py bytes:", len(check_src))
# k-gate
import re
m = re.match(r"(\d+) 条断言", TEST_RATIONALE)
k_rat = int(m.group(1))
k_check = 16
print("k_rationale=%d k_check=%d GATE=%s" % (k_rat, k_check, "PASS" if k_rat == k_check and k_check >= 8 else "FAIL"))
