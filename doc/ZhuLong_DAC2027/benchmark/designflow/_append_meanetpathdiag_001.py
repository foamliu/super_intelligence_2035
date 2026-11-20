# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-MeaNetPathDiag-001 to B.jsonl (shard B / spice_sim)."""
import os, json, re

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-MeaNetPathDiag-001"
AST = os.path.join(BENCH, "assets", CID)
REF = os.path.join(BENCH, "reference", CID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

prompt = open(os.path.join(AST, "prompt.txt")).read()
check_py = open(os.path.join(REF, "check.py")).read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        "assets/" + CID + "/prompt.txt",
        "assets/" + CID + "/task_brief.md",
        "assets/" + CID + "/io_d0_template_A/io_d0_template.sp",
        "assets/" + CID + "/io_d0_template_A/dspf_fragment.sp",
    ],
    "expected_artifacts": ["outputs/submit.zip"],
    "budget": {"max_turns": 25},
    "test": check_py,
    "metadata": {
        "domain": "spice_sim",
        "grade": "B",
        "track": "faithful",
        "harness": "cline",
        "L_level": "L1",
        "trace_source": {
            "user": "shanliny",
            "host": "hfeg0pkn001",
            "session_file": "1793234226913_xtse5.messages.json",
            "match_count": 43,
            "real_task_summary": (
                "shanliny @ pkn001(10.129.2.10) 的 SRAM sense-amp .sp 中 .measure 提不出数值。"
                "USER#0 原话「为什么我sp文件中的mea语句没法提取相应的数值？」+ io_d0_template.sp + HD1P_CXN4S1P1024X144M2B2C1R1W1BW1RE1.dspf.TYPICAL_25 附件 "
                "—— 纯症状轮(只给现象+反问, 未给根因/修复) ⇒ CLEAN A-档。trace 56 msgs/3.5MB(含 3MB DSPF 内嵌), "
                "spice_c=43(hspice 6/netlist 7/schematic)。assistant 解析 DSPF 发现 *|I 互连行 net 名用单 x(XSA[1].MPMYRC:s) "
                "而器件实例行用双 x(XXSA[1].MPMYRC), 用户 .mea v(xtop.xxsa[1].mpmyrc:s) 用双 x 器件实例路径而非 net 名 ⇒ 名字不匹配 ⇒ 提不出数值; "
                "修复=6 条 .mea 节点路径双 x→单 x。"
            ),
        },
        "test_rationale": (
            "12 条断言："
            "①submit.zip 含一个 .py 脚本(mea_netpath_diag.py) "
            "②该 .py 脚本经 py_compile 通过 "
            "③无参数/参数数错/参数过多时均非零退出 "
            "④在隐藏 B(broken_sp_B+dspf_B)上运行 exit 0 且同时产出 io_d0_template_fixed.sp 与 diagnosis.md 两文件 "
            "⑤fixed.sp 保留 B 全部 8 条 .measure 名(t_outb_r/v_blb_fall2/v_bl_fall2/v_dv2/v_df_sat_sac2/v_df_bl_blb2/v_df_b_s2/v_extra) "
            "⑥fixed.sp 的 .measure v() 内不再含双 x 实例前缀 xxsb[2] "
            "⑦fixed.sp 的 .measure v() 节点路径(含差分 v(a,b) 拆分)用单 x net 前缀 xsb[2] 的条数>=7 "
            "⑧真跑候选:解析 dspf_B 的 *|I 行建 net 集, fixed.sp 每条 'find v()' 节点路径(小写)均在 net 集中 "
            "⑨.measure 的 param 算术行(v_dv2='v_blb_fall2 - v_bl_fall2'; v_df_b_s2='v_df_bl_blb2 - v_df_sat_sac2')逐字保留 "
            "⑩控制语句 .tran 0.1n 1800n / .temp 125 / .param high=0.700 diff=0.05 / .lib ff_mos_varactor_fs / .inc 'dspf_fragment.sp' 逐字保留 "
            "⑪diagnosis.md 提及 *|I 行、'net' 且阐明单 x net 名 vs 双 x 实例名的双重命名根因 "
            "⑫随机化:对 fixed.sp 的 'find v()' 路径随机抽 3 子集 x 3 seed, net-in-DSPF 结论一致(全 True) "
            "外加反硬编码守卫:脚本在可见 A(xsa[1]/ss/-40/2100n)上也须同样修正且 find v() 路径落 DSPF_A *|I net 集"
        ),
    },
}

# assertion gate: k_rationale == k_check >= 8
rat = entry["metadata"]["test_rationale"]
marks = re.findall(r"[①-⑿]", rat)
cond_in_check = 12  # a..l in check.py
print("k_rationale (circled marks):", len(marks))
print("k_check (conditions a-l):", cond_in_check)
assert len(marks) == cond_in_check == 12, "ASSERTION GATE FAILED"
assert cond_in_check >= 8
print("ASSERTION GATE: k_rationale == k_check == 12 OK (>=8)")

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended to", JSONL)

n = sum(1 for _ in open(JSONL))
print("B.jsonl now", n, "lines")
