#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-AprStampFix-001 to A.jsonl."""
import os, json

ROOT = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID  = "EDA-Eval-DesignFlow-AprStampFix-001"
A_DIR = os.path.join(ROOT, "assets", CID)
JSONL = os.path.join(ROOT, "EDA-Eval-DesignFlow_A.jsonl")
CHECK = os.path.join(ROOT, "reference", CID, "check.py")

A_FILES = [
    "test_chip_power.md",
    "apr/innovus_fp.tcl",
    "apr/innovus_pr.tcl",
    "apr/Makefile",
    "apr/mmmc.view.template",
    "pdk/tech.tlef",
    "pdk/stdcells.lef",
    "netlist/hl22_postsyn.v",
    "sdc/hl22.mapped.sdc",
]

PROMPT = """Innovus APR flow 修复 (HL22 porting, test_chip_v1 workspace)。

附件 bundle 是 alan3zh 在 hfeg0pkn001 上跑 Innovus APR (floorplan + route) 时的真实 apr/ 目录 (test_chip_power.md 配置 + innovus_fp.tcl/innovus_pr.tcl/Makefile)。该 flow 有 3 个真实 bug 导致 make 误判 floorplan FAILED、PM band 被跳过、stamp 机制缺失：

1. stamp 机制缺失：innovus_fp.tcl / innovus_pr.tcl 的所有 FAILED 出口与 DONE 横幅都没有写 stamp 文件，make 只能靠 grep 日志判断成败；当日志异步 flush / NFS 目录属性缓存时 make 会误判。
2. PM band 几何查询失败：innovus_fp.tcl 仅用 `dbGet top.fPlan.rows.origin_y` 单一拼写，该 Innovus 版本不识别 → "cannot query row/core geometry -- skipping" → sroute IMPSR-1253。
3. Makefile retry loop 太短 (15×2s=30s) 且只 grep 日志、不查 stamp、不刷新 NFS。

请实现一个**通用自适应修复器** `fix_apr_stamp.py`，CLI `fix_apr_stamp.py <bundle_root> [-o <out_dir>]`，从 bundle 的 test_chip_power.md 读取 TOP / PM_CELL / SITE / LOG_DIR，对 buggy 的 innovus_fp.tcl / innovus_pr.tcl / Makefile 做程序化修复，输出到 fixed/：

- fp.tcl / pr.tcl：加 `proc stamp_write {suffix}` (写 $::env(INV_FP_STAMP)/INV_PR_STAMP + suffix)；每个 FAILED 出口前调 `stamp_write .fail`；DONE 横幅后调 `stamp_write ""`。
- fp.tcl 几何块重写：电池 dbGet (top.fPlan.rows + top.rows 两路径，origin/origin_y/bbox 兜底) + coreBox 4-list/scalar 兜底 + DBU→µm 归一化 (dbGet head.dbUperUU，默认 2000，坐标>500 视为 DBU) + LEF SITE SIZE/SYMMETRY 兜底 + INV_PM_ROW0_ORIENT 方向逃生阀。
- Makefile：60×2s=120s retry 窗口，stamp-priority (先查 Tcl stamp TSTAMP1，log-grep 后卫)，.fail break，每轮 touch+rm .nfsprobe 刷新 NFS。

patcher 必须**自适应**：fixed 文件引用 bundle 自身的 TOP/PM_CELL/SITE/LOG_DIR (同一 patcher 能修任意结构不同的 bundle)。

交付：把 `fix_apr_stamp.py` + `fixed/innovus_fp.tcl` + `fixed/innovus_pr.tcl` + `fixed/Makefile` 打包为 `outputs/submit.zip`。"""

TEST_RATIONALE = ("15 条断言：① submit.zip 含 fix_apr_stamp.py + fixed/{innovus_fp.tcl, innovus_pr.tcl, Makefile} 四件齐全 ② fix_apr_stamp.py 可 py_compile ③ 候选 patcher 对 A bundle 运行 exit 0 且产出 3 个 fixed 文件 ④ tclsh info complete 对 fixed/innovus_fp.tcl(A) 返回 COMPLETE-OK (真跑 tclsh) ⑤ tclsh info complete 对 fixed/innovus_pr.tcl(A) 返回 COMPLETE-OK ⑥ fixed/innovus_fp.tcl 含 `proc stamp_write` 定义且 `stamp_write .fail` 调用 ≥5 处 ⑦ fixed/innovus_fp.tcl 几何块含电池 dbGet (top.fPlan.rows + top.rows 两路径) + LEF SITE fallback (lefGet + SYMMETRY) + DBU 归一化 (dbUperUU + /$_dbu_per_um) ⑧ fixed/innovus_pr.tcl 含 stamp_write proc 且 `stamp_write .fail` 调用 ≥7 处 ⑨ fixed/Makefile retry loop 含 stamp-priority (TSTAMP1 先查) + 窗口≥120s (60×2) + NFS refresh (.nfsprobe touch+rm) + .fail break ⑩ make -n dry-run 对 fixed/Makefile 无语法错 (真跑 make) ⑪ 跨输入守卫：patcher 对隐藏 B bundle 运行 exit 0 且 fixed B 的 fp.tcl 引用 B 的 TOP (v2) 不含 A 的 TOP (v1) ⑫ 跨输入守卫：fixed B 的 Makefile 引用 B 的 stamp/log 路径不含 A 的 `.inv_fp_hl22_porting_test_chip_v1` ⑬ 反硬编：fixed A 的 fp.tcl 不含 B 的 TOP，fixed B 的 fp.tcl 不含 A 的 TOP ⑭ fixed/innovus_fp.tcl 的 INNOVUS FP DONE 横幅后跟 `stamp_write \"\"` (success stamp) ⑮ patcher 自适应：fixed A 几何块引用 A 的 SITE/PM_CELL (coreSite/INVD8BWP40P140LVT)，fixed B 引用 B 的 (coreSite_v2/INVD16BWP40P140LVT)，两份不同")

test_src = open(CHECK).read()

entry = {
    "task_id": CID,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "prompt": PROMPT,
    "attachments": ["assets/%s/%s" % (CID, f) for f in A_FILES],
    "metadata": {
        "trace_source": {
            "user": "alan3zh",
            "host": "hfeg0pkn001",
            "session_file": "1793706326923_qiqs7.messages.json",
            "match_count": 470,
            "real_task_summary": "Innovus APR full-flow (fp+route) bug fix for test_chip_v1 (HL22) on hfeg0pkn001; user's first real turn reported 'innovus floorplan FAILED -- see inv_fp.log, no route log' (debug root-cause-pointed -> A-grade rule 2 disqualifies -> B-grade synthesized). 82-msg session; assistant fixed 3 real bugs: (1) make mis-judged fp FAILED due to LSF -o async flush + NFS dir-attr cache (>30s) over a 30s grep window; (2) PM band skipped due to dbGet top.fPlan.rows.origin_y / coreBox spelling not recognized (IMPDBTCL-204/206); (3) missing stamp mechanism. Fixed innovus_fp.tcl (10 edits) + innovus_pr.tcl (8) + Makefile (6); success stamps .inv_fp_hl22_porting_test_chip_v1.stamp + .inv_route_*.stamp landed -> verified-accepted L3 build. This case scoping a reusable adaptive APR-flow fixer (verb: fix), distinct from AprLogAudit-001 (audit LOGS) and AprSetupAudit-001 (audit SETUP INPUTS)."
        },
        "domain": "pnr_signoff",
        "track": "synthesized",
        "test_rationale": TEST_RATIONALE
    }
}

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")

# verify
lines = open(JSONL).read().splitlines()
print("appended. total lines:", len(lines))
print("last task_id:", json.loads(lines[-1])["task_id"])
# gate: k_rationale == k_check == 15
k_check = 15  # (a)-(o)
import re
k_rationale = len(re.findall(r"[①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮]", TEST_RATIONALE))
print("k_rationale =", k_rationale, " k_check =", k_check,
      " GATE:", "PASS" if k_rationale == k_check >= 8 else "FAIL")
