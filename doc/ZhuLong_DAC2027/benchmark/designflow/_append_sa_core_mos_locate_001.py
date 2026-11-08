#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SaCoreMosLocate-001 to shard B jsonl."""
import json, os, re

HERE = os.path.dirname(os.path.abspath(__file__))
CASE_ID = "EDA-Eval-DesignFlow-SaCoreMosLocate-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSETS = os.path.join(BENCH, 'assets', CASE_ID)
REF = os.path.join(BENCH, 'reference', CASE_ID)
JSONL = os.path.join(BENCH, 'EDA-Eval-DesignFlow_B.jsonl')

with open(os.path.join(ASSETS, 'prompt.txt'), 'r', encoding='utf-8') as f:
    prompt = f.read().strip()
with open(os.path.join(REF, 'check.py'), 'r', encoding='utf-8') as f:
    test_src = f.read()

test_rationale = (
    "15 条断言：①submit.zip 含恰好 1 个 .py 脚本 ②脚本 py_compile 通过 "
    "③B 运行 exit 0 且 out.json 为含必需键的 dict ④core_mos 恰好 4 条 "
    "⑤mos_type 恰好 2 NMOS + 2 PMOS ⑥4 条 delvto_param 全匹配 delvtoBL<bit>_{NsL,NsR,PsL,PsR}*0.5 "
    "且 bit==bit_index 且 4 后缀齐全互异 ⑦bit_index==3 且 sa_subckt==CXSA1x4_die2_fbccB 且 "
    "sa_instance==XI_sa417(Blasec28<417> 经反转端口序映射到 Bla<3>) ⑧NMOS 交叉输入:L.gate 含 Blb "
    "且 R.gate 含 Bla ⑨PMOS 交叉耦合锁存:L.gate==R.drain 且 R.gate==L.drain "
    "⑩共享 SA 节点:NMOS L.drain==PMOS L.drain 且 NMOS R.drain==PMOS R.drain "
    "⑪角色接线:NMOS source==NCS/body 含 vss,PMOS source==PCS/body 含 vblhbk "
    "⑫core_mos 实例集=={XN0_b3,XN1_b3,XP0_b3,XP1_b3}(目标 bit MOS,排除他 bit 与无 delvto 诱饵) "
    "⑬A 交叉输入:exit 0 且 bit_index==2 且 sa_subckt==CXSA1x4_die2_fbcc 且 sa_instance==XI_sa562 "
    "且 delvto 前缀 delvtoBL2(泛化非硬编码) ⑭A out.json != B out.json(非单答案硬编码) "
    "⑮3 次运行 out.json 字节一致 sha256(幂等)"
)

entry = {
    "id": CASE_ID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": prompt,
    "attachments": [
        {"name": "prompt.txt", "source": "prompt.txt",
         "desc": "真实用户原话（A-faithful，yuyingc @ hfeg0pkn001，trace 1793623698314_n7w6c U#38 逐字）：查看 v(blasec28<562>) 所在 SA 中决定上拉/下拉能力的 4 个 MOS 管在网表里是哪四个"},
        {"name": "task_brief.md", "source": "task_brief.md",
         "desc": "交付接口：sa_core_mos_locate.py <网表> <顶层信号> -o out.json；out.json 含 top_signal/sa_subckt/sa_instance/bit_index/core_mos；判分只跑隐藏 B"},
        {"name": "netlist", "source": "netlist",
         "desc": "可见真实 A 网表（合成 SPICE PEX，sim_top→XI_sa562→CXSA1x4_die2_fbcc 4bit SA，Blasec28<562>→Bla<2>→bit2→delvtoBL2_*，含 he-bit 诱饵/无 delvto precharge-iso-colsel 诱饵/parasitic RC 诱饵/decoySA 实例诱饵）"},
    ],
    "test": test_src,
    "metadata": {
        "trace_source": {
            "user": "yuyingc",
            "host": "hfeg0pkn001",
            "session_file": "1793623698314_n7w6c.messages.archive.json",
            "match_count": 37,
            "real_task_summary": "yuyingc 在 hfeg0pkn001 上用 FineSim 跑 LP5X DDR SA 感放阵列(48 用例 senb/senw/mixb/mixw × Vcap/cmos/cmos_array)的 Vtarget 二分优化+失配 delvtoBL0_* 仿真。用户 U#38「帮我查看 v(blasec28<562>) 这个信号线所在的SA中决定了上拉和下拉能力的4个mos管在Netlist网表里是哪四个」。agent 追踪层次 sim_top→XI_msaq_fBCC_02→msax320_fbcc→CXSA1x4_die2_fbcc，定位每个 bit 的 4 核心管：2 NMOS 下拉(XMMN0/XMMN1,NCS 使能,交叉 bitline 栅,delvto=delvtoBL<k>_NsL/NsR*0.5)+2 PMOS 上拉交叉锁存(XMMP7/XMMP8,PCS 使能,交叉 Sa 栅,delvto=delvtoBL<k>_PsL/PsR*0.5)。本 case 抽取「SPICE 网表 SA 核心 MOS 定位」可复用子流，关键 trap 为顶层信号→SA bit 的层次端口位置映射、反转端口序、交叉耦合结构辨识、他 bit/无 delvto/decoySA 诱饵排除。关键字 finesim/spice/sa/sense-amp/delvto/mismatch 高密。"
        },
        "domain": "spice_sim",
        "layer": "L1",
        "layer_rationale": "check() 在隐藏 B 网表(与 A 同 SPICE SA 结构但反转端口序/重命名 subckt+实例+模型/不同 bit/2 个 decoy SA)上跑候选脚本，离线解析 SPICE 网表做层次端口映射+核心 MOS 定位，subprocess 调候选 CLI，无需 EDA 工具。L1 离线 Python 复刻。",
        "track": "faithful",
        "test_rationale": test_rationale,
    },
}

# verify roundtrip: test field == disk check.py
disk_check = open(os.path.join(REF, 'check.py'), 'r', encoding='utf-8').read()
assert test_src == disk_check, "test field != disk check.py"

# count existing lines + unique ids
with open(JSONL, 'r', encoding='utf-8') as f:
    lines = f.readlines()
ids = set()
for ln in lines:
    try:
        ids.add(json.loads(ln)['id'])
    except Exception:
        pass
assert CASE_ID not in ids, "case id already in jsonl"
print("before: %d lines, %d unique ids" % (len(lines), len(ids)))

with open(JSONL, 'a', encoding='utf-8') as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

with open(JSONL, 'r', encoding='utf-8') as f:
    after = f.readlines()
print("after: %d lines" % len(after))
last = json.loads(after[-1])
k_rat = len(re.findall(r'[①-⑯⑰⑱⑲⑳⓪]', last['metadata']['test_rationale']))
k_chk = len(re.findall(r'raise AssertionError\("([a-o]):', last['test']))
print("k_rationale=%d  k_check=%d  GATE=%s" % (k_rat, k_chk, "PASS" if k_rat == k_chk and k_chk >= 8 else "FAIL"))
print("appended:", last['id'])
