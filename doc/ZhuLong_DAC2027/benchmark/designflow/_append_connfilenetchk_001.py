#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-ConnFileNetChk-001 to EDA-Eval-DesignFlow_A.jsonl."""
import json, os

CID = "EDA-Eval-DesignFlow-ConnFileNetChk-001"
BASE = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = os.path.join(BASE, "assets", CID)
REF_DIR = os.path.join(BASE, "reference", CID)
JSONL = os.path.join(BASE, "EDA-Eval-DesignFlow_A.jsonl")

with open(os.path.join(REF_DIR, "check.py"), encoding="utf-8") as f:
    check_py = f.read()
with open(os.path.join(ASSET_DIR, "prompt.txt"), encoding="utf-8") as f:
    prompt = f.read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_py,
    "prompt": prompt,
    "attachments": [
        "assets/%s/si.inp_A" % CID,
        "assets/%s/connectFile_A.txt" % CID,
        "assets/%s/netlist_A.sp" % CID,
        "assets/%s/netlistHeader_A" % CID,
        "assets/%s/netlistFooter_A" % CID,
        "assets/%s/model_A.sp" % CID,
        "assets/%s/stimulus_A.inc" % CID,
        "assets/%s/si.ignore_block_A" % CID,
        "assets/%s/prompt.txt" % CID,
        "assets/%s/task_brief.md" % CID,
    ],
    "metadata": {
        "trace_source": {
            "user": "taodu",
            "host": "hfeg0pfn012",
            "session_file": "1793067588685_cpv3d.messages.json",
            "match_count": 2257,
            "real_task_summary": "si.inp connectFile net-existence verification perl script (verification domain) on hfeg0pfn012 (taodu); user turn #0 verbatim: 「读取下面到si.inp文件，查找是否存在文件名以connectFile开头到，如果存在，则抓取网表到hierarchy, 判断connectFile中的net是否都存在，排除ignore的instance hierarchy,形成一个perl脚本 /rundata/ddgoa/.../si.inp」 -- clean task request (parse si.inp -> find connectFile* -> extract netlist hierarchy -> check nets exist -> exclude ignore instance hierarchy -> produce perl script), no root cause / fix given => A-grade rule 2 OK => A-grade faithful. 653-msg session; real si.inp/connectFile/netlist under /rundata/ddgoa + /proj/ddgoa permission-denied (owned by ddgoa group) => B-grade synthesized faithful bundles (real si.inp .option finesim_ignore + .include connectFile + .inc netlist .subckt structure + RConnect <fullpath>.<net> format preserved). Gold: assistant iteratively built /home/taodu/check_connectFile_nets.pl (user accepted after 7 refine turns: connectFile via .inc/.include hierarchy / .module support / comments / prompt-on-missing / timestamped report / speed). verb: si-inp-connectfile-net-verify, mutually exclusive with all existing shard-A verbs (PortCatch=netlist-port-connectivity-extract is CDL/cck port+neighbor extraction; FlatNet is hier->flat verilog; this is si.inp->connectFile RConnect->netlist .subckt net-existence check + ignore exclusion)."
        },
        "domain": "verification",
        "track": "faithful",
        "test_rationale": "15 条断言：① submit.zip 恰含一个 .pl 脚本 ② perl -c 语法校验通过 ③ 候选脚本对可见 A 的 si.inp_A 运行 exit 0 ④ A report 含 RESULT+SUMMARY 行可被正则解析 ⑤ A 的 FOUND (net,path) 集合 == 独立 python oracle(不同代码路径解析 si.inp+connectFile+网表)重算的 A found 集合 ⑥ A 的 MISSING (net,path) 集合 == oracle A missing 集合 ⑦ A 的 EXCLUDED (net,path) 集合 == oracle A excluded 集合 ⑧ A 的 SUMMARY 计数(total/found/missing/excluded) == oracle A 计数 ⑨ 候选脚本对隐藏 B 的 si.inp_B 运行 exit 0 且 B found/missing 集合 == oracle B ⑩ 跨输入守卫 B 的 SUMMARY total(18)≠A(14) 且 B found(9)≠A(8) ⑪ 跨输入守卫 B 的 missing (net,path) 集合 ≠ A 的 missing 集合(B 含 qmissing/zmiss/wmiss2，A 含 pmiss/outmiss) ⑫ 跨输入守卫 B report 含 B 顶层实例名 Xb0 且不含 A 顶层实例名 Xtop0 ⑬ 反硬编候选 .pl 源码不含 A/B 专有字面量(Xtop0/Xb0/LeafA/LeafB/MidA/MidB/IgnSubA/IgnSubB/TopA/TopB/connectFile_A/connectFile_B/XignA/XignB/XarrA/XarrB) ⑭ 随机化对 A 连跑 3 次 SUMMARY 行完全一致(确定性) ⑮ 显式实例级 sanity：A report 中 (p1, Xtop0.Xm0.Xu1) 为 FOUND 且 (i1, Xtop0.XignA) 为 EXCLUDED(证明 .subckt 层次端口解析 + .option finesim_ignore 排除均生效)"
    }
}

with open(JSONL, "a", encoding="utf-8") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended", CID, "to", JSONL)
