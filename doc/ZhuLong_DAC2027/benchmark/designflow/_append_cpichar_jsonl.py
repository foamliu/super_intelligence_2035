#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-CpIcpChar-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os

HERE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(HERE, "assets", "EDA-Eval-DesignFlow-CpIcpChar-001")
REF = os.path.join(HERE, "reference", "EDA-Eval-DesignFlow-CpIcpChar-001")
JSONL = os.path.join(HERE, "EDA-Eval-DesignFlow_B.jsonl")

prompt = open(os.path.join(ASSETS, "prompt.txt")).read()
check_py = open(os.path.join(REF, "check.py")).read()

test_rationale = (
    "14 条断言："
    "①submit.zip 内含 cp_char.py "
    "②cp_char.py 可 py_compile "
    "③B 经 subprocess 真跑 HSPICE（out_dir .lis 含 job concluded）"
    "④B 各档位 Iup/Idown 与 GT 偏差<10% "
    "⑤B 偏置管 mpsrc 工作区被分类为 triode(lin)（检出非饱和陷阱，反 naive_all_sat）"
    "⑥B 报告含 B 管子名(mrefp/mrefn/mpsrc/mnsrc)、不含 A 管子名(mdip/mdin/miup/midn)（name-agnostic）"
    "⑦report.tol/codes 取自 spec_B（0.08/[2,3,4,5]）非 A 硬编 "
    "⑧char_table.csv 表头含 code/iup/idown/iup_idown_match/region_*/accept 且行数≥4 "
    "⑨B report.accept==False 且 reasons 非空 "
    "⑩sat_count/lin_count/cut_count 正确（B=12/4/0）"
    "⑪交叉重跑 A → A accept==True 且 A 管子名出现（反忽略 A 输入）"
    "⑫重跑 B 各档位 Iup 在 2% 内一致（确定性）"
    "⑬≥4 档位被表征 "
    "⑭trap 管 mpsrc 含数值 vds/vgs/vth 且 derived==lin 与 region_hspice 一致（从 vds/vgs/vth 数值派生，非抄 region 字符串）"
)

entry = {
  "task_id": "EDA-Eval-DesignFlow-CpIcpChar-001",
  "mode": "design_flow",
  "prompt": prompt,
  "attachments": [
    {"name": "cp_A.sp", "source": "cp_A.sp",
     "desc": "公开输入 A：PLL 电荷泵网表（vdd=0.85V，自偏置 PMOS/NMOS 二极管参考 + UP/DOWN 电流镜，dac 档位=multiplier 占位符 MPLACE，level-1 Shichman-Hodges）。4 个偏置管全饱和、Iup≈Idown。供 SUT 开发与本地调试。"},
    {"name": "spec_A.json", "source": "spec_A.json",
     "desc": "公开 A 配置：codes=[1,2,3,4]、bias_mos=[mdip,mdin,miup,midn]、tol=0.08、sim_tool=hspice。"},
    {"name": "prompt.txt", "source": "prompt.txt", "desc": "任务说明（自然语言）。"},
    {"name": "task_brief.md", "source": "task_brief.md", "desc": "交付接口与文件位置说明（≤3 行）。"},
  ],
  "entry_point": "outputs/submit.zip",
  "expected_artifacts": ["cp_report.json", "char_table.csv"],
  "test": check_py,
  "budget": {"max_turns": 20},
  "metadata": {
    "trace_source": {
      "user": "wnyu",
      "host": "hfeg0pgn021",
      "session_file": "1792120107352_t1b5d",
      "match_count": 48,
      "real_task_summary": "wnyu 在 hfeg0pgn021 上搭并调通 PLL 电荷泵(CP)模块：验证偏置建立、各管子饱和区工作、各档位 Icp 电流，覆盖 0.85V 与 1.8V(厚氧管)双电压域，PVT 遍历。agent 用 HSPICE .op/.tran 迭代 sizing/bias，逐管判定工作区(saturation/sub-threshold/triode)，U83 用户接受 Icp 每档位电流表。trace 走 foundry PDK(cxmtG6_1C2A p25ud18_ckt/ptn_lv)+多电压域厚氧管，不可便携 .75；提取「CP Icp 表征 + 偏置管工作区分类(sat/lin/cut)+accept 判定」子技能，DUT 用 level-1 Shichman-Hodges MOS(HSPICE V-2023.12-SP1-1)。A=0.85V 全饱和 Iup≈Idown；B=1.2V 一个偏置管落 triode(linear)=trap → Iup≠Idown accept=False。"
    },
    "domain": "characterization",
    "layer": "L2",
    "layer_rationale": "check() 在隐藏 B(vdd=1.2V, codes=[2,3,4,5], 偏置管 mrefp/mrefn/mpsrc/mnsrc, PMOS 参考二极管窄 W+小 Rref 致 mpsrc 落 triode)上经 subprocess 真跑 Synopsys HSPICE(.75 EDA 沙箱 headless，.op 解析每管 region/vds/vgs/vth + .measure Iup/Idown)。B 与 A 在 vdd(1.2/0.85)、sizing、codes、管子名、节点名、trap(有/无 triode 管)全不同。level-1 无 sub-threshold，trace 的「亚阈值」在 level-1 体现为 cutoff/triode，本 case trap=triode(PMOS 电流镜 |Vds|=vdd/2 < |Vgs-Vth|=vod)。",
    "test_rationale": test_rationale,
    "track": "synthesized",
    "harness": "cline",
  },
}

with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify k_rationale == k_check == 14
k_rat = test_rationale.count("①") + sum(1 for c in "②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭" if c in test_rationale)
# count _cond calls in check.py (a-n = 14)
import re
cond_calls = len(re.findall(r"_cond\(', '[a-n]',", check_py)) + len(re.findall(r"_cond\('[a-n]',", check_py))
print("appended. lines now:", sum(1 for _ in open(JSONL)))
print("k_rationale =", k_rat, " k_check(_cond calls) =", check_py.count("_cond("))
