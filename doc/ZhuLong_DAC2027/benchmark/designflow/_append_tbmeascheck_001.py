#!/usr/bin/env python3
import json, os, copy

REF = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference/EDA-Eval-DesignFlow-TbMeasCheck-001"
JSONL = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/EDA-Eval-DesignFlow_B.jsonl"

check_src = open(os.path.join(REF, "check.py")).read()

case = {
  "task_id": "EDA-Eval-DesignFlow-TbMeasCheck-001",
  "mode": "design_flow",
  "prompt": "/home/e0030760/Documents/Solido/test_fix.sp 帮我检查一下这个testbench，里面测试WSNM、Iread、Iwrite、Ileak的指令是否存在问题",
  "attachments": [
    {"name": "test_fix.sp", "source": "test_fix.sp",
     "desc": "hspice/Solido SRAM bitcell characterization testbench（real trace e0030760@hfeg0pkn004, Documents/Solido/test_fix.sp）。含 6 个测试单元（WNM×2/HSNM/RSNM/IREAD/IWRITE/ILEAK）.NODESET 偏置、.DC VIN 0..VVDD 10e-3 扫参、.tran 1p 10ns、5 条 .MEASURE DC（Iread/Iwrite/Ileak FIND I(VIPRB_*) AT=VVDD/2；WNM_1/2 find v(VIN_*) when v(S*-v(SB*))=0 cross=1）、.PROBE DC、corner ttg_sram_fs+pre_sim_fs、.TEMP 25、VVDD=0.675。A 档 trace-faithful：任务说明为用户原话逐字。"},
    {"name": "task_brief.md", "source": "task_brief.md",
     "desc": "交付接口说明（≤3 行）：tb_meas_check.py <testbench.sp> <out.json>，读 testbench 写 JSON 诊断 exit 0，打包 outputs/submit.zip。"},
  ],
  "entry_point": "outputs/submit.zip",
  "expected_artifacts": ["tb_meas_check.py"],
  "test": check_src,
  "budget": {"max_turns": 20},
  "metadata": {
    "trace_source": {
      "user": "e0030760", "host": "hfeg0pkn004", "ip": "10.129.32.13",
      "session_file": "1793791169909_2ka5p.messages.json",
      "match_count": 257,
      "real_task_summary": "e0030760 在 CXMT SRAM bitcell characterization 流程中用 hspice/Solido 对 6T bitcell 做 WSNM/HSNM/RSNM/Iread/Iwrite/Ileak 特征化测试。用户首轮意图：检查 test_fix.sp 里测试 WSNM/Iread/Iwrite/Ileak 的测量指令是否存在问题。trace 里 agent 读 test_fix.sp + bitcell netlist + 实测 .ms0/.mt0，逐项诊断：Iwrite 用 .MEASURE DC FIND I(VIPRB_WRITE) AT=VVDD/2 测到 ~0（-6.66pA vs MC 期望 -482nA）—— 原理性错误，写电流是瞬态量 DC 稳态必为 0；Iread AT=VVDD/2 取的是 VIN 扫参中点（与 Iread 无关），实为静态读电流 21.86µA；Ileak 待机 WL 关 31.3pA 正常；WSNM(WNM_1/2=250.5mV) 互补扫 cross=1 工作但需确认定义。本 case 抽取其「解析 testbench .MEASURE 指令 → 对 4 项测量各给 status(error/warning/ok)+problems+root_cause+fix + other_issues」这一可复用诊断子流，要求交付通用 tb_meas_check.py 并在隐藏同类 testbench（不同问题组合：Iwrite error/Iread ok/Ileak error/WSNM error，VVDD=0.9 扫参 VS .TEMP 85）上交叉校验。关键字 hspice:1251 netlist:319 spectre:94 schematic:70 spice 占比 0.774。"
    },
    "domain": "spice_sim",
    "layer": "L2",
    "layer_rationale": "check() 经 subprocess 真跑候选 tb_meas_check.py 于隐藏 testbench B（hidden/test_fix_B.sp，不同 VVDD/扫参/corner/问题组合），断言解析输出的 JSON 结构与 B ground truth；非纯文本相似，非 L1 离线复刻。",
    "test_rationale": "15 条断言：①(a) submit.zip 合法且含 tb_meas_check.py ②(b) tb_meas_check.py py_compile 通过 ③(c) 候选在隐藏 B 上 exit 0 且产出 out.json ④(d) out.json 合法 JSON 且含顶层 keys tool_version/measures/other_issues ⑤(e) measures 恰含 4 键 Iwrite/Iread/Ileak/WSNM ⑥(f) 每条 measure 含 status/problems/root_cause/fix 且 status∈{error,warning,ok} ⑦(g) B 金标准 Iwrite=error（DC FIND 测瞬态量） ⑧(h) B 金标准 Ileak=error（standby 偏置错 S_ILEAK=VVDD） ⑨(i) B 金标准 WSNM=error（crossing 引用不存在的 S9_WNM） ⑩(j) B 金标准 Iread=ok（AVG 扫程有效） ⑪(k) Iwrite root_cause 含 transient/瞬态/steady/稳态 物理关键词 ⑫(l) Iwrite fix 含 TRAN/ammeter/安培计/peak 关键词 ⑬(m) other_issues 为非空 list ⑭(n) 每条 error 状态 measure 的 problems 非空 ⑮(o) cross-input guard：候选在可见 A 上 exit 0 且 4 measures 齐全",
    "k_rationale": 15,
    "k_check": 15,
  }
}

with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended. total lines:", sum(1 for _ in open(JSONL)))
