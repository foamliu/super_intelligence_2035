#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generator for EDA-Eval-DesignFlow-MinpulseRewriteRun-001.
Builds A assets (SUT-visible) + hidden B + reference + check + negatives.
"""
import os, json, zipfile, shutil, sys

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-MinpulseRewriteRun-001"
A_ROOT = os.path.join(BENCH, "assets", CID)
REF_ROOT = os.path.join(BENCH, "reference", CID)

PROMPT = """/proj/commonIP/analog/v1_hl/lp5/v0/simdir/anasim/berylwu/ddgoa/rc_delay这个路径下，Dlyrc开头的几个文件夹下的minpulse_spf目录下的sp文件，替换里面的Old string (raw input)    : /proj/ddgoa/V0/model/current/
  New string (raw input)    : /proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/
并直接run所有替换后的激励"""

TASK_BRIEF = """交付接口：把可执行 Python 脚本 replace_and_run.py 及运行产物打包为 outputs/submit.zip。
脚本用法：replace_and_run.py <root> <old_path> <new_path> <out_dir> [--sim hspice|finesim] [--queue Q] [--run]
功能：递归扫描 <root>/Dlyrc*/minpulse_spf/*.sp，将每个 .sp 中所有出现的 <old_path> 子串替换为 <new_path>，按原相对结构（Dlyrc_*/minpulse_spf/<name>.sp）把替换后的 deck 写入 <out_dir>；生成 submit.sh（对每个替换后 deck 执行 `<sim> -i <name>.sp -o <name>_TS/ -np 4`，若给 --queue 则用 `bsub -q <queue>` 包裹）与 replace_report.json（含 files_changed、total_replacements、folders、per_file{name:{occ,old_remain,new_present}}）。"""

# ---- stub deck generator ----
# A: old /proj/ddgoa/V0/model/current/  new /proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/
#    4 folders x 8 files = 32 files, 5 .inc occurrences each
# B: old /proj/mtj/V0/model/legacy/      new /proj/mtj/V0/model/legacy_L3_v1d1_Rev01_t08/
#    3 folders x 6 files = 18 files, 4 .inc occurrences each

INC_FILES_A = ["model.sp", "incFile_lp", "param.sp", "corner/typical.sp", "corner/ss.sp"]
INC_FILES_B = ["model.sp", "incFile_lp", "param.sp", "corner/typical.sp"]

def make_deck(name, old_path, inc_files, idx):
    lines = ["* minpulse_spf deck: %s" % name, "* auto-generated stub for model-path rewrite exercise"]
    for f in inc_files:
        lines.append(".inc %s%s" % (old_path, f))
    lines += [
        "* --- circuit (RC, model-free so hspice concludes without real model) ---",
        "vsrc in 0 pulse(0 1 0 1n 1n 10n 50n)",
        "r1 in out 1k",
        "c1 out 0 1p",
        ".tran 1n 100n",
        ".measure tran vpk max v(out)",
        ".measure tran tpd trig v(in) val=0.5 rise=1 targ v(out) val=0.5 fall=1",
        ".end",
    ]
    return "\n".join(lines) + "\n"

def build_tree(root_reltop, folders, nfiles, old_path, inc_files, name_prefix):
    # root_reltop is the dir under which Dlyrc_*/minpulse_spf/... is created
    for fi, fold in enumerate(folders):
        d = os.path.join(root_reltop, fold, "minpulse_spf")
        os.makedirs(d, exist_ok=True)
        for j in range(nfiles):
            nm = "%s_%02d.sp" % (name_prefix, j + 1)
            with open(os.path.join(d, nm), "w") as fh:
                fh.write(make_deck(nm, old_path, inc_files, j))

# ---------- A assets ----------
shutil.rmtree(A_ROOT, ignore_errors=True)
os.makedirs(A_ROOT, exist_ok=True)
with open(os.path.join(A_ROOT, "prompt.txt"), "w") as fh:
    fh.write(PROMPT + "\n")
with open(os.path.join(A_ROOT, "task_brief.md"), "w") as fh:
    fh.write(TASK_BRIEF + "\n")
A_FOLDERS = ["Dlyrc_Pre", "Dlyrc_r1c", "Dlyrc_vdly", "Dlyrc_vint_Pre"]
build_tree(os.path.join(A_ROOT, "rc_delay"), A_FOLDERS, 8,
           "/proj/ddgoa/V0/model/current/", INC_FILES_A, "minpulse")
# local empty model for any local run
with open(os.path.join(A_ROOT, "local_model.sp"), "w") as fh:
    fh.write("* local empty model stub (no devices needed for RC deck)\n")

# ---------- hidden B ----------
HIDDEN = os.path.join(REF_ROOT, "hidden")
shutil.rmtree(HIDDEN, ignore_errors=True)
B_FOLDERS = ["Dlyrc_Aft", "Dlyrc_r2d", "Dlyrc_vpre"]
B_OLD = "/proj/mtj/V0/model/legacy/"
B_NEW = "/proj/mtj/V0/model/legacy_L3_v1d1_Rev01_t08/"
build_tree(os.path.join(HIDDEN, "rc_delay"), B_FOLDERS, 6, B_OLD, INC_FILES_B, "minpulse")
with open(os.path.join(HIDDEN, "hidden_manifest.json"), "w") as fh:
    json.dump({
        "root": "rc_delay",
        "old_path": B_OLD,
        "new_path": B_NEW,
        "folders": B_FOLDERS,
        "files_per_folder": 6,
        "occurrences_per_file": 4,
        "sim": "hspice",
        "queue": "fqueue3",
        "expected_files_changed": 18,
        "expected_total_replacements": 72,
    }, fh, indent=2)
# local empty model for judge L2 rewrite
with open(os.path.join(HIDDEN, "local_model.sp"), "w") as fh:
    fh.write("* local empty model stub\n")

print("A tree built at", A_ROOT)
print("hidden B built at", HIDDEN)
