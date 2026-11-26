#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-MinpulseRewriteRun-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-MinpulseRewriteRun-001"
REF = os.path.join(BENCH, "reference", CID)
ASSETS = os.path.join(BENCH, "assets", CID)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

check_py = open(os.path.join(REF, "check.py")).read()
prompt = open(os.path.join(ASSETS, "prompt.txt")).read().strip()

attachments = [
    "assets/%s/prompt.txt" % CID,
    "assets/%s/task_brief.md" % CID,
    "assets/%s/rc_delay" % CID,
    "assets/%s/local_model.sp" % CID,
]

test_rationale = (
    "14 条断言：①submit.zip含可执行Python脚本replace_and_run.py "
    "②脚本py_compile通过 "
    "③脚本在隐藏B上运行exit0且产出replace_report.json+submit.sh+替换后deck树 "
    "④replace_report.files_changed==18(3目录x6文件) "
    "⑤replace_report.total_replacements==72(18x4) "
    "⑥replace_report.folders==[Dlyrc_Aft,Dlyrc_r2d,Dlyrc_vpre] "
    "⑦每个替换后.sp中old路径残留计数==0 "
    "⑧每个替换后.sp中new路径计数==4 "
    "⑨submit.sh含恰好18条sim启动行 "
    "⑩submit.sh用bsub -q fqueue3包裹每条启动命令 "
    "⑪启动行匹配hspice -i <name>.sp -o <name>_TS/ -np 4模式 "
    "⑫L2 hspice真跑重写后B deck(绝对路径.inc改写为本地空模型)job concluded且无syntax/parse error "
    "⑬replace_report.per_file每条occ==4(均匀) "
    "⑭跨输入A运行files_changed==32/total_replacements==160且均≠B(18/72)防硬编码"
)

case = {
    "task_id": CID,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": attachments,
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["replace_and_run.py", "replace_report.json", "submit.sh"],
    "test": check_py,
    "budget": {"max_turns": 20},
    "metadata": {
        "domain": "spice_sim",
        "track": "faithful",
        "layer": "L2",
        "k_check": 14,
        "k_rationale": 14,
        "trace_source": {
            "user": "berylwu",
            "host": "hfeg0pkn002",
            "session_file": "1793937421846_ip3nr.messages.json",
            "match_count": 231,
            "real_task_summary": (
                "berylwu @ hfeg0pkn002 的 cline session 1793937421846_ip3nr(67 msgs, spice_sim, "
                "mtime 2026-11-06 NEW——写入于 11-05 19:28 重扫快照之后；本轮 11-06 11:5x 经 .75 run_commands "
                "对 42 个 spice-active hosts 定向重扫(threshold 2026-11-06 06:00:00)发现 111 NEW sessions "
                "(证 pool 未枯竭)后筛出。USER#0 verbatim A 档「/proj/.../rc_delay这个路径下，Dlyrc开头的几个文件夹下的"
                "minpulse_spf目录下的sp文件，替换里面的Old string:/proj/ddgoa/V0/model/current/ "
                "New string:/proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/ 并直接run所有替换后的激励」"
                "(纯需求轮,未指出根因/未给修复→A 档可用)。assistant list_allowed_files/run_commands 遍历 "
                "Dlyrc_Pre/Dlyrc_r1c/Dlyrc_vdly/Dlyrc_vint_Pre 各 minpulse_spf→editor replace_model.py 替换模型路径"
                "→run_approved 验证无 old 残留/新路径存在→editor gen_submit.py 生成 submit_minpulse.sh"
                "(cd 各 minpulse_spf, bsub -q fqueue3 finesim -i <name>.sp -o <name>_TS/ -np 4)→提交 32 jobs"
                "(1844147–1844182 PEND)→USER 接受。金标准=trace 末尾用户接受的 32 文件改写(5 处/文件=160 替换)+"
                "32 jobs LSF 提交。本 case 取 verbatim A 档需求,合成金标准:通用 replace_and_run.py 递归扫描 "
                "Dlyrc*/minpulse_spf/*.sp 替换 old→new 路径→按原结构写 out_dir→生成 submit.sh(bsub finesim/hspice)+"
                "replace_report.json。A=4 目录x8 文件=32(5 处/文件,ddgoa 路径);hidden B=3 目录x6 文件=18(4 处/文件,"
                "mtj 路径,不同目录名/计数/路径→跨输入护栏)。.75 HSPICE 真跑重写后 B deck job concluded。"
            ),
        },
        "test_rationale": test_rationale,
        "layer_rationale": (
            "L2: check.py 条件⑫用 subprocess 在隐藏 B 的替换后 deck 上真跑 hspice(judge 侧把绝对路径 .inc 改写为"
            "本地空模型),断言 job concluded 且无 syntax/parse error——验证候选的路径替换保留了 deck 结构可运行。"
        ),
    },
}

with open(JSONL, "a") as fh:
    fh.write(json.dumps(case, ensure_ascii=False) + "\n")
print("appended", CID, "to", JSONL)
# verify
n = sum(1 for _ in open(JSONL))
print("jsonl now", n, "lines")
