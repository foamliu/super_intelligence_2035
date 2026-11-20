#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SaDcSweepTbGen-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os, hashlib

CASE = "EDA-Eval-DesignFlow-SaDcSweepTbGen-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
ASSETS = os.path.join(BENCH, "assets", CASE)
REF = os.path.join(BENCH, "reference", CASE)
CHECK_PY = os.path.join(REF, "check.py")

with open(CHECK_PY, 'r', encoding='utf-8') as f:
    check_src = f.read()

prompt = (
    "你是 CXMT 模拟设计团队的 SPICE 仿真工程师。同事 t0002614 在主机 hfeg0plg105 的工作目录 "
    "/home/t0002614/workspace/ZhuLong/TestSA 下维护一个 CXSA sense-amplifier（敏感放大器）的仿真验证流程。"
    "该目录含真实网表 netlist（顶层 subckt sim_sa_dc_check，含 Iso/Sel/OC/PreEq 四组控制管与 BL 位线节点、"
    "vad2! 隔离电源）以及一份参考测试网表 ref_test.sp（HSPICE/FineSim deck，含模型库 .lib 路径、"
    "netlist .inc 结构、电源/偏置与 .tran 分析）。\n\n"
    "真实轨迹里 t0002614 的原话需求（逐字）：\n"
    "「根据网表 netlist 和参考的测试网表 test.sp 帮我写仿真测试。测试设置：TT 工艺角，温度 125 摄氏度，"
    "直流仿真，vad2!=1.4V，Iso 管关闭，sel 管的栅压固定为 1.77V，OC 管和 PreEq 管的栅压扫描 1.17-1.77V，"
    "看 BL 上的电压。」\n\n"
    "请编写一个 Python 脚本 sa_dc_sweep_tb_gen.py，读取参考测试网表 ref_test.sp（提取模型库 model_lib、"
    "inc 库 inc_lib、网表 include 路径）与测试设置 spec.json（corner/temp/vad2_v/iso_gate_v/sel_gate_v/"
    "sweep_start_v/sweep_stop_v/sweep_points/sweep_src_name/observe_node/analysis_type），"
    "生成一份完整的 HSPICE/FineSim 直流扫描测试网表 out_tb.sp 及审计报告 out_report.json。\n\n"
    "CLI 用法（4 个位置参数）：\n"
    "    python3 sa_dc_sweep_tb_gen.py <ref_test.sp> <spec.json> <out_tb.sp> <out_report.json>\n\n"
    "out_tb.sp 必须是直流（.dc）扫描 deck：含 6 条 .lib（model <corner> + <corner>_Array + bjt/res/nicap/diode_<corner>）、"
    ".inc 网表、.temp <temp>、vad2! 源 dc=<vad2_v>、Iso 栅压源 dc=<iso_gate_v>（=0 关闭）、Sel 栅压源 dc=<sel_gate_v>、"
    "扫描栅压源、.dc v<sweep_src> <start> <stop> <step>（step=(stop-start)/(points-1)）、.print dc v(<observe_node>)、"
    "至少一条 .measure dc、.end；不得出现 .tran（本任务要求直流仿真）。\n"
    "out_report.json 含 case_id / spec 镜像 / extracted{model_lib,inc_lib,netlist_inc} / deck_lines / "
    "has_dc_analysis / has_tran / sweep_step / corner_applied / temp_applied。\n\n"
    "资产：ref_test.sp（参考 deck，提取模型库路径）、spec.json（A 测试设置）、netlist_stub.sp（CXSA 网表 stub）、"
    "output_format_spec.txt（输出格式规范）、task_brief.md。隐藏输入 B（不进 SUT 沙箱）使用不同 corner/temp/vad2/sel/"
    "sweep 范围的 spec，check 只跑 B1+B2。\n"
    "交付物：把 sa_dc_sweep_tb_gen.py 打包进 outputs/submit.zip。"
)

attachments = [
    {"name": "ref_test.sp", "source": "ref_test.sp",
     "desc": "可见 A：参考测试网表（HSPICE/FineSim deck，含模型库 .lib 路径与 netlist .inc 结构、.tran 分析，供提取 model_lib/inc_lib/netlist_inc）"},
    {"name": "spec.json", "source": "spec.json",
     "desc": "可见 A：直流扫描测试设置（corner=tt/temp=125/vad2=1.4/iso=0/sel=1.77/sweep 1.17-1.77/61pts/observe BL）"},
    {"name": "netlist_stub.sp", "source": "netlist_stub.sp",
     "desc": "可见 A：CXSA sense amplifier 网表 stub（顶层 subckt sim_sa_dc_check：Iso/Sel/OC/PreEq 管 + BL + vad2!）"},
    {"name": "output_format_spec.txt", "source": "output_format_spec.txt",
     "desc": "out_tb.sp（直流扫描 deck 8 节）与 out_report.json（审计字段）格式规范"},
    {"name": "task_brief.md", "source": "task_brief.md",
     "desc": "交付接口与文件位置说明（≤3 行）"},
]

task_brief = (
    "编写 sa_dc_sweep_tb_gen.py（CLI: <ref_test.sp> <spec.json> <out_tb.sp> <out_report.json>），"
    "从 ref_test.sp 提取模型库路径、按 spec.json 生成 HSPICE 直流扫描 deck out_tb.sp + 审计 out_report.json。"
    "交付：sa_dc_sweep_tb_gen.py 打包进 outputs/submit.zip。"
)

test_rationale = (
    "15 条断言：①submit.zip 含 sa_dc_sweep_tb_gen.py ②候选脚本通过 py_compile ③候选在隐藏 B1 上 exit 0 且产出 out_tb.sp+out_report.json "
    "④B1 out_tb.sp 含 .lib ... ff（corner 正确）⑤B1 out_tb.sp 含 .temp -40（温度正确）⑥B1 out_tb.sp 含 vad2 源 dc=1.2（vad2 正确）"
    "⑦B1 out_tb.sp 含 Iso 栅压源 dc=0.0（Iso 关闭）⑧B1 out_tb.sp 含 Sel 栅压源 dc=1.5（Sel 固定栅压）"
    "⑨B1 out_tb.sp 含 .dc vOcPreeq 1.0 1.6 扫描（扫描范围正确）⑩B1 out_tb.sp 含 .print dc v(BL)（观测节点正确）"
    "⑪B1 out_tb.sp 不含 .tran（必须直流非瞬态）⑫B1 out_tb.sp 含至少一条 .measure dc（量测语句）"
    "⑬B1 out_report.json 合法且 has_dc_analysis=true/has_tran=false/corner=ff/temp=-40 "
    "⑭反硬编码 B2 out_tb.sp 含 ss/85/1.6/1.9/1.3-1.9 且与 B1 不同（非硬编码 A/B1）⑮确定性 B1 连跑 2 次输出字节一致"
)

entry = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "task_brief": task_brief,
    "test": check_src,
    "metadata": {
        "trace_source": {
            "user": "t0002614",
            "host": "hfeg0plg105",
            "session_file": "1794290579357_trnx0",
            "match_count": 35,
            "real_task_summary": "根据网表与参考测试网表编写 CXSA sense-amplifier 直流扫描仿真测试（TT 工艺角、125°C、vad2=1.4V、Iso 关闭、Sel 栅压 1.77V、OC/PreEq 栅压扫描 1.17-1.77V、观测 BL 电压）"
        },
        "domain": "spice_sim",
        "track": "synthesized",
        "level": "L1",
        "test_rationale": test_rationale,
    }
}

# byte-sync sanity: test field == check.py on disk
sha_disk = hashlib.sha1(check_src.encode('utf-8')).hexdigest()
sha_field = hashlib.sha1(entry["test"].encode('utf-8')).hexdigest()
assert sha_disk == sha_field, "test field not byte-synced with check.py"

with open(JSONL, 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

print(f"appended {CASE} to {JSONL}")
print(f"test sha1: {sha_disk}  ({len(check_src)} bytes)")
# count assertions in rationale
import re
k = len(re.findall(r'[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]', test_rationale))
print(f"k_rationale = {k}")
# count check conditions (a-o)
conds = re.findall(r'_fail\("[a-o]:', check_src)
print(f"k_check (a-o) = {len(conds)}  labels={[c[7] for c in conds]}")
