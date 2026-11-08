#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-GrDecPwrSwitchTbGen-001 to EDA-Eval-DesignFlow_D.jsonl."""
import json, os, hashlib

CASE_ID = "EDA-Eval-DesignFlow-GrDecPwrSwitchTbGen-001"
EDA_BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = os.path.join(EDA_BENCH, "assets", CASE_ID)
REF_DIR = os.path.join(EDA_BENCH, "reference", CASE_ID)
JSONL = os.path.join(EDA_BENCH, "EDA-Eval-DesignFlow_D.jsonl")

with open(os.path.join(ASSET_DIR, "prompt.txt")) as f:
    prompt = f.read()
with open(os.path.join(REF_DIR, "check.py")) as f:
    check_src = f.read()
check_sha = hashlib.sha256(check_src.encode()).hexdigest()
check_size = len(check_src.encode())

attachments = [
    "assets/%s/switch_dut.cdl" % CASE_ID,
    "assets/%s/sim_top_netlist.cdl" % CASE_ID,
    "assets/%s/task_brief.md" % CASE_ID,
    "assets/%s/prompt.txt" % CASE_ID,
]

test_rationale = (
    "12 条断言：①submit.zip 合法且含候选 .py 工具脚本 ②脚本以 --netlist/--sim-netlist/--out CLI 在隐藏 B(同结构开关 CDL 网表,不同 cell/net/MOS/信号名)上 subprocess 退出码 0 且产出 analysis.json+tb.sp "
    "③analysis.json 的 top_subckt 精确等于 R_WlPwrGateSwitch(隐藏 B 的子电路名,非 A 的 R_GidlAryCtrl_switch,反硬编码) "
    "④ports 集合精确等于 {WlDecPwr,wl_sw_total,wlsw,gnd!,vplz!}(B 的 5 端口,非 A 的 GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!) "
    "⑤端口角色精确:dec_pwr_port=WlDecPwr 且 well_supply_port=vplz! 且 ground_port=gnd!(非 A 的 GrDecPwr/vwlp!/vss!) "
    "⑥pmos_pullup_chain 实例名集合精确等于 {M_PU0,M_PU1,M_PU2}(B 的 PMOS 上拉链,非 A 的 MMP0/MMP1/MMP2,集合无关顺序) "
    "⑦nmos_pull_down.inst 精确等于 M_PD0(B 的 NMOS 下拉管,非 A 的 MMN0) "
    "⑧control_signals 排序后精确等于 [wl_sw_total,wlsw](B 的控制信号,非 A 的 cm1_sw_total/cm1sw) "
    "⑨phase_signal 精确等于 WlPhase(从 sim_top 的 NAND2 自动识别出的非开关端口/非电源输入,非 A 的 SecHv) "
    "⑩truth_table 的 NAND 逻辑正确:ACT(phase=1,ctrl=1)→D=0→action=pull_up 且 PRE(phase=0,ctrl=1)→D=1→action=pull_down "
    "⑪tb.sp 结构齐备:含 .tran 且含 .print 或 .probe 且含 PULSE(相位 WlPhase) 且含供电 vplz!/gnd! 且含负载电容 cgr 且含被测例化 R_WlPwrGateSwitch 且含 WlDecPwr 观测节点 "
    "⑫确定性+反硬编码:同隐藏 B 重跑 3 次 analysis.json 完全一致 且 analysis.json+tb.sp 全文不含 A 特有名(R_GidlAryCtrl_switch/GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!/MMP0/MMP1/MMP2/MMN0/SecHv)泄露"
)

entry = {
    "case_id": CASE_ID,
    "task_id": "GrDecPwrSwitchTbGen-001",
    "task_id_full": CASE_ID,
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": attachments,
    "test": check_src,
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 20},
    "metadata": {
        "trace_source": {
            "user": "dsgao",
            "host": "hfhds234",
            "session_file": "1793935013447_wmzu1.messages.json",
            "match_count": 1429,
            "real_task_summary": (
                "用户(dsgao@hfhds234)分析 DRAM 行译码电源控制开关 R_GidlAryCtrl_switch(CDL 网表,AETHER-SE 抽取):"
                "在 ACT(激活)/PRE(预充电)阶段对行译码电源 GrDecPwr 的上拉/下拉影响。agent 解析网表识别 PMOS 上拉链(MMP2/MMP1/MMP0→vwlp!)与 NMOS 下拉管(MMN0→vss!),"
                "推导 NAND 控制逻辑 D=NAND(secHV,cm1_sw_total)/NAND(secHV,cm1sw),因 cm1 在开关窗口内恒定高而退化为 NOT(secHV):secHV 上升沿(ACT)→D=0→PMOS 链导通→GrDecPwr 上拉,secHV 下降沿(PRE)→D=1→NMOS 导通→GrDecPwr 下拉。"
                "随后读 ALPS 仿真顶层网表(顶层已含 nand2Y_Xdecx1 把 SecHv+cm1sw 做 NAND 得 net0 驱动 cm1_sw_total=cm1sw=net0,GrDecPwr=内部 net2),写验证测试台 R_GidlAryCtrl_switch_sim_tb.sp(.lib 模型库/.option finesim_mode=spicead/vsec PULSE/vcm1sw 恒高/cgr net2 负载/.tran/.print/.probe)。"
                "会话 228 msgs 1429 D-domain 命中(netlist:265 schematic:186 hspice:19),模型 glm-5.1-cloud。真实资产 /proj/drcpa/V0/workdir/dsgao/ 下网表为 dsgao 私有不可读(Permission denied,DEBT④ 同 #413/#416),但 agent 在 /home/dsgao/Desktop/ 写的 tb.sp 经 NFS 共享可读 -> 获完整 subckt 结构(MMP0-4/MMN0-1 + 端口)+ NAND 逻辑 + tb 格式 -> B-grade synthesized:依据 trace 真实结构与 tb 格式合成 A/B 两套同结构开关网表 + sim_top(含 NAND2),离线验证候选 Python 脚本 dec_pwr_switch_tb_gen.py 的网表解析+路径识别+NAND 推导+tb 生成逻辑(反硬编码+确定性+结构断言)。"
            ),
        },
        "domain": "schematic_netlist",
        "grade": "B synthesized",
        "track": "synthesized",
        "level": "L2",
        "test_rationale": test_rationale,
        "check_sha256": check_sha,
        "check_size": check_size,
    },
}

line = json.dumps(entry, ensure_ascii=False)
with open(JSONL, "a") as f:
    f.write(line + "\n")
print("appended:", CASE_ID)
print("check_sha256:", check_sha, "check_size:", check_size)
print("rationale_k:", test_rationale.count("①") + 1 if "①" in test_rationale else 0)
