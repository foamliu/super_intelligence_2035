#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-NetlistPortMismatchDiagProduce-001 to D.jsonl."""
import json, hashlib, os

BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-NetlistPortMismatchDiagProduce-001"
CASE_SHORT = "NetlistPortMismatchDiagProduce-001"
REF_DIR = os.path.join(BASE, "reference", CASE_SHORT)

check_data = open(os.path.join(REF_DIR, "check.py"), "rb").read()
check_sha = hashlib.sha256(check_data).hexdigest()
check_size = len(check_data)

USER_VERBATIM = (
    "bin/vsim -sr wrrd_sequence  --rannum _1 -d \"USESDF LocalPower\" -q verilog -l log_pte &\n"
    "[1] 35283\n"
    "e06960@hfeg0plg102: /proj/decqa/V0/simdir/verilog/PTE/e06960/lpddr6_tb_1008>Info: voltagemode disabled, use default sdf, pls check tbconfig voltagemode if needed\n"
    "Job <3429276> is submitted to queue <verilog>.\n"
    "Job <3429282> is submitted to default queue <interactive>.\n"
    "<<Waiting for dispatch ...>>\n"
    "<<Starting on hfpdcnd016>>\n"
    "e06960_FriNov20-10:27:26wrrd_sequence_1..x24 is done.\n"
    "ncelab: *E,CUVPOM (/rundata/decqa/V0/simdir/verilog/PTE/e06960/lpddr6_tb_1008/netlist/V0_LP6TOP_2026Oct26.185525/netlist,132219|65): Port name 'RfshPulse' is invalid or has multiple connections.\n"
    "ncelab: *E,CUVPOM (/rundata/decqa/V0/simdir/verilog/PTE/e06960/lpddr6_tb_1008/netlist/V0_LP6TOP_2026Oct26.185525/netlist,132219|65): Port name 'RfshPulse' is invalid or has multiple connections."
)

prompt = (
    "你正在协助一位 EDA 工程师排查 Cadence ncelab 仿真报错。下面是用户粘贴进对话的仿真日志（逐字原文，未脱敏，"
    "真实 trace 来源：e06960 @ hfeg0pkn001，会话 1795144434219_xjdww，mc=2287，analog 1402 / verilog 341 / schematic 304 / netlist 94）：\n\n"
    "---- 用户粘贴的仿真日志开始 ----\n"
    + USER_VERBATIM +
    "\n---- 用户粘贴的仿真日志结束 ----\n\n"
    "请写一个 Python 脚本 diagnose_port_mismatch.py，接受一个必选参数 + 一个可选参数：\n"
    "    python3 diagnose_port_mismatch.py <netlist.v> [-o <report.json>]\n"
    "脚本解析 Verilog 网表，找出「实例化端口引用了但模块定义端口列表里不存在」的端口"
    "（即 ncelab *E,CUVPOM 'Port name is invalid or has multiple connections' 错误的根因），"
    "把诊断结果以 JSON 报告打印到 stdout（-o 同时写文件）。可见输入 A 为 netlist_A.v（紧凑 Verilog 网表 fixture）。"
    "判分器在隐藏输入 B（token 与 A 完全不相交，不进沙箱）上跑你的脚本并独立重算期望值逐条断言。"
    "完成后把 diagnose_port_mismatch.py 打包进 outputs/submit.zip。"
)

entry = {
    "id": CASE,
    "case_id": CASE,
    "task_id": "NetlistPortMismatchDiagProduce-001",
    "task_id_full": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        {
            "name": "netlist_A.v",
            "source": "netlist_A.v",
            "desc": (
                "可见 A 紧凑 Verilog 网表 fixture（忠实反映 trace xjdww 中 V0_LP6TOP_2026Oct26.185525/netlist 的 CUVPOM 错误结构："
                "模块 RHRCalCtrl_cqa 端口列表 [AddSub0, EmptyFlagin, EmptyRHRdbRst, PRACRst_Win, CalWin, RhrCode] 不含 RfshPulse；"
                "顶层 LP6TOP_A 实例化 RHRCalCtrl_cqa u_rhrcal 时引用 .RfshPulse(rfsh_pulse) → CUVPOM；"
                "distractor DlyChain_cqa 干净实例化无 mismatch）。"
            ),
        },
        {
            "name": "task_brief.md",
            "source": "task_brief.md",
            "desc": "交付接口说明：diagnose_port_mismatch.py 单参 CLI <netlist.v> + 可选 -o，stdout 输出 JSON 报告，submit.zip 打包。",
        },
    ],
    "test": check_data.decode("utf-8"),
    "budget": {"max_turns": 20},
    "expected_artifacts": ["outputs/submit.zip"],
    "metadata": {
        "domain": "schematic_netlist",
        "subdomain": "netlist-port-mismatch-diag-produce",
        "task_type": "produce-task / netlist-port-mismatch-diag (A-faithful verbatim + synthesized-reframe)",
        "difficulty": "L1",
        "reframe": (
            "synthesized-reframe (real V0_LP6TOP_2026Oct26.185525/netlist 132K+ 行 foundry-bound /rundata NFS 不可沙盒 -> "
            "脱敏 netlist_A.v 紧凑 fixture 保留真实模块名 RHRCalCtrl_cqa + 真实错误端口 RfshPulse + 真实 ncelab CUVPOM 错误结构 "
            "+ distractor DlyChain_cqa 干净实例化; preserves real trace diagnosis semantics: parse Verilog module 定义 + 实例化, "
            "find instance 端口引用 not in 模块端口列表 = CUVPOM 根因; A-faithful to USER#0 verbatim sim log 逐字原文)"
        ),
        "trace_source": {
            "user": "e06960",
            "host": "hfeg0pkn001",
            "session_file": "1795144434219_xjdww",
            "match_count": 2287,
            "real_task_summary": (
                "用户(e06960@hfeg0pkn001)单轮粘贴 ncelab 仿真日志：bin/vsim 跑 wrrd_sequence，ncelab 报 *E,CUVPOM "
                "(netlist,132219|65): Port name 'RfshPulse' is invalid or has multiple connections（重复 10 次）。"
                "assistant 诊断：读 /rundata/.../V0_LP6TOP_2026Oct26.185525/netlist 第 129422 行 module RHRCalCtrl_cqa 端口列表"
                "(AddSub0/EmptyFlagin/EmptyRHRdbRst/PRACRst_Win/...) 不含 RfshPulse，但第 132219 行实例化 u_rhrcal 引用 .RfshPulse(rfsh_pulse)，"
                "导致 CUVPOM 端口无效/多重连接错误。本 case 取此「网表端口失配诊断」produce 意图，用户唯一轮次为粘贴 sim log 意图陈述无根因/解法。"
            ),
        },
        "hidden_b": {
            "path": "assets/NetlistPortMismatchDiagProduce-001/hidden/",
            "description": (
                "隐藏 B：紧凑 Verilog 网表 fixture，token 与 A 完全不相交。netlist_B.v 含模块 DatPathCtrl_qbz 端口列表 "
                "[SelA, ValidIn, RdyOut, DataBus, ModeSel] 不含 AckStrobe + distractor ClkGate_qbz 干净实例化；"
                "顶层 DPETOP_B 实例化 DatPathCtrl_qbz u_dpc 引用 .AckStrobe(ack_sig) → CUVPOM。"
                "A-only=RHRCalCtrl_cqa/RfshPulse/AddSub0/EmptyFlagin/EmptyRHRdbRst/PRACRst_Win/CalWin/RhrCode/DlyChain_cqa/u_rhrcal/u_dly/LP6TOP_A; "
                "B-only=DatPathCtrl_qbz/AckStrobe/SelA/ValidIn/RdyOut/DataBus/ModeSel/ClkGate_qbz/u_dpc/u_cg/DPETOP_B。"
            ),
            "b_gold": {
                "input_file": "netlist_B.v",
                "total_modules": 3,
                "total_instances": 2,
                "total_mismatches": 1,
                "first_mismatch": {
                    "module": "DatPathCtrl_qbz",
                    "instance": "u_dpc",
                    "port": "AckStrobe",
                },
                "b_only_tokens": [
                    "DatPathCtrl_qbz", "AckStrobe", "SelA", "ValidIn", "RdyOut",
                    "DataBus", "ModeSel", "ClkGate_qbz", "u_dpc", "u_cg", "DPETOP_B",
                ],
                "a_only_tokens": [
                    "RHRCalCtrl_cqa", "RfshPulse", "AddSub0", "EmptyFlagin",
                    "EmptyRHRdbRst", "PRACRst_Win", "CalWin", "RhrCode",
                    "DlyChain_cqa", "u_rhrcal", "u_dly", "LP6TOP_A",
                ],
            },
        },
        "test_rationale": (
            "15 条断言：①submit.zip 是合法 zip 且含 diagnose_port_mismatch.py(a) ②脚本经 py_compile 通过(b) "
            "③脚本字节数 ≥600B 反空壳(c) ④在隐藏 B(netlist_B.v)上 subprocess 跑通 exit 0 且 stdout 非空(d) "
            "⑤stdout 为合法 JSON 且含 input_file/modules/instances/summary/function_summary 全部顶层键(e) "
            "⑥summary.total_mismatches == 独立 _gt 重算值(=1)(f) ⑦首个 mismatch.module == DatPathCtrl_qbz(B-only)(g) "
            "⑧首个 mismatch.port == AckStrobe(B-only)(h) ⑨首个 mismatch.instance == u_dpc(B-only)(i) "
            "⑩modules[].DatPathCtrl_qbz 端口数 == 独立 _gt_module_port_count(=5)(j) "
            "⑪DatPathCtrl_qbz 端口集合不含 AckStrobe(独立 _gt_module_ports)(k) "
            "⑫u_dpc 实例 ports_referenced 含 AckStrobe(独立 _gt_instance_ports)(l) "
            "⑬反硬编码：A-only token(RHRCalCtrl_cqa/RfshPulse/AddSub0/EmptyFlagin/EmptyRHRdbRst/PRACRst_Win/CalWin/RhrCode/DlyChain_cqa/u_rhrcal/u_dly/LP6TOP_A，word-boundary)缺席 B stdout(m) "
            "⑭反硬编码-2：B-only token(DatPathCtrl_qbz/AckStrobe/SelA/ValidIn/RdyOut/DataBus/ModeSel/ClkGate_qbz/u_dpc/u_cg/DPETOP_B)出现于 B stdout(n) "
            "⑮B 3 次重跑 stdout md5 确定性一致(o)"
        ),
        "k_rationale": 15,
        "k_check": 15,
        "negative_selftest": (
            "reference/NetlistPortMismatchDiagProduce-001/negative/negative_selftest.py: "
            "reference GOLD PASS 15/15 + empty_stub/print_only_stub/core_deleted_stub 全 FAIL, NEG_RC=0; "
            "§4.9 (a)empty->c/d/e FAIL (b)print_only->f/g/h/i/j/k/l/m FAIL (A-only 泄漏) (c)core_deleted->f/g/h/i/j/k/l FAIL (total_mismatches=0)"
        ),
        "check_sha256": check_sha,
        "check_size": check_size,
    },
}

out_path = os.path.join(BASE, "EDA-Eval-DesignFlow_D.jsonl")
with open(out_path, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("Appended to", out_path)
print("check_sha256:", check_sha)
print("check_size:", check_size)

# verify roundtrip: last line test field bytes == disk check.py bytes
with open(out_path) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
assert last["test"].encode("utf-8") == check_data, "test field byte mismatch"
assert last["metadata"]["check_sha256"] == check_sha
assert last["metadata"]["check_size"] == check_size
print("byte-sync OK: test==disk check.py, sha+size match")
print("D.jsonl lines:", len(lines))
