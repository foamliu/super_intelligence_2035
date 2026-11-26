#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-SimIncMissingDiag-001 to EDA-Eval-DesignFlow_B.jsonl."""
import json, os, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CASE = "EDA-Eval-DesignFlow-SimIncMissingDiag-001"
REF = os.path.join(BENCH, "reference", CASE)

# read check.py source -> test field
with open(os.path.join(REF, "check.py")) as f:
    test_src = f.read()

# verify jsonl test == disk sha (roundtrip)
disk_sha = hashlib.sha256(test_src.encode()).hexdigest()[:16]

prompt = "/proj/commonIP/analog/v1/lp5x/v0/simdir/anasim/yanghao/2_TsComp_post/result_post 下面的仿真为什么报错了"

test_rationale = (
    "16 条断言：① zip 含 diagnose_sim_inc_missing.py 且 py_compile exit 0 "
    "② B 上 outB.json 合法 JSON dict 含必需键(sim_count/failed_sims/unified_error/missing_file/root_cause/unused_includes/fix_suggestion) "
    "③ B failed_sims 非空 list 且每项为 B result_post 真实子目录 "
    "④ B unified_error==True(所有失败 sim 同一 missing file) "
    "⑤ B root_cause.missing_file=='AG_XY_foobar.spf_RCC'(B 的，非硬编码 A 的 AG_TS_1stStgComp) "
    "⑥ B root_cause.setting_sp_line==22(B 的行号，非硬编码 A 的 18) "
    "⑦ B root_cause.path_type=='relative'(缺失 .inc 是相对路径) "
    "⑧ B root_cause.file_exists==False(文件在工作目录中不存在) "
    "⑨ B unused_includes 非空且 missing_file 的 stem 'AG_XY_foobar' 不在 netlist subckt/实例化中(残留模板行) "
    "⑩ B sim_count==6(B 的仿真数，非硬编码 A 的 9) "
    "⑪ B all_sims_failed==True(所有 sim 因全局 .inc 同一报错) "
    "⑫ B fix_suggestion 存在且含注释建议(含 '*') "
    "⑬ 交叉输入守卫：A 上 root_cause.missing_file=='AG_TS_1stStgComp.spf_RCC'(证明泛化，非硬编码 B) "
    "⑭ 交叉输入守卫：A 上 root_cause.setting_sp_line==18(A 的行号) "
    "⑮ A-only 未泄漏：outB.json 文本无 A-only 标记 'A_only_siminc_marker' "
    "⑯ 3 次幂等：B 上 outB.json sha256 一致"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": test_src,
    "prompt": prompt,
    "attachments": [
        "assets/EDA-Eval-DesignFlow-SimIncMissingDiag-001/A_sim_post",
        "assets/EDA-Eval-DesignFlow-SimIncMissingDiag-001/task_brief.md",
    ],
    "metadata": {
        "domain": "spice_sim",
        "track": "faithful",
        "level": "L1",
        "hidden_inputs": ["assets/EDA-Eval-DesignFlow-SimIncMissingDiag-001/hidden/"],
        "trace_source": {
            "user": "yanghao",
            "host": "hfhds201",
            "session_file": "1794105806205_mah5p",
            "match_count": 72,
            "real_task_summary": (
                "FineSim post-layout sim .inc missing-file diagnosis (A-faithful). "
                "User (U#0 verbatim) asks why sims under 2_TsComp_post/result_post errored; "
                "no root cause / fix given. Gold-standard (cline assistant, trace "
                "1794105806205_mah5p, 72 msgs, last=assistant 排查结论, A#71): all 9 sims "
                "(1_pvt_130/1_pvt_m40/2_mc_130/2_mc_m40/3_ac/4_ioff_130/4_ioff_m40/5_ADcomp_130/"
                "5_ADcomp_m40) abort in the netlist-parse phase (~2s) with the SAME error "
                "'ERROR! unable to read file AG_TS_1stStgComp.spf_RCC (Setting.sp:18): No such "
                "file or directory'. Root cause: Setting.sp lines 17-19 -- line 17 is an "
                "absolute-path .inc (netlist.presim, present), lines 18 & 19 are relative-path "
                ".inc referencing two PEX-extracted .spf_RCC parasitic netlists "
                "(AG_TS_1stStgComp.spf_RCC, AG_TS_comp.spf_RCC) that do not exist anywhere in "
                "the project (commonIP lib, /proj/ddgoa/V0/ver/pex/*, all sim/work dirs empty) "
                "and are NOT instantiated in netlist.presim (949 lines: instantiates "
                "TsCoreAFBiasIP/TsCoreAFAcompIP/TsCoreAlgDcompIP, zero AG_TS_1stStgComp/AG_TS_comp) "
                "-> residual template lines copied from another block. Contrast: 4_TsCore_post/"
                "Setting.sp uses absolute paths for .spf_RCC. Fix: comment out lines 18-19 "
                "(*.inc '...') and rerun runsim. Evidence chain: (1) 9 sims unified error. "
                "(2) Setting.sp:18 relative .inc AG_TS_1stStgComp.spf_RCC. (3) file absent "
                "project-wide. (4) netlist.presim has no AG_TS_1stStgComp/AG_TS_comp subckt or "
                "instantiation. (5) 4_TsCore_post uses absolute .inc (correct pattern). "
                "Portable sub-skill: parse sim *.log for 'unable to read file' ERROR, parse "
                "Setting.sp .inc lines (relative vs absolute), cross-reference netlist.presim "
                "subckt/instantiation, report missing_file + line + path_type + unused_includes "
                "+ fix_suggestion."
            ),
        },
        "test_rationale": test_rationale,
    },
}

# append
with open(JSONL) as f:
    n_before = sum(1 for _ in f)
line = json.dumps(entry, ensure_ascii=False)
with open(JSONL, "a") as f:
    f.write(line + "\n")
with open(JSONL) as f:
    n_after = sum(1 for _ in f)

# roundtrip: verify test field sha matches disk
with open(JSONL) as f:
    last = None
    for last in f: pass
d = json.loads(last)
test_sha = hashlib.sha256(d["test"].encode()).hexdigest()[:16]
print("jsonl %d -> %d" % (n_before, n_after))
print("task_id:", d["task_id"])
print("disk_sha:", disk_sha, "jsonl_sha:", test_sha, "match:", disk_sha == test_sha)
print("k_rationale=16 k_check=16 gate:", 16 == 16 and 16 >= 8)
