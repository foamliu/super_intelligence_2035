#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Append EDA-Eval-DesignFlow-SiInpTokenRm-001 to EDA-Eval-DesignFlow_B.jsonl."""
import os, json, hashlib

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")
CASE = "EDA-Eval-DesignFlow-SiInpTokenRm-001"
REF = os.path.join(BENCH, "reference", CASE)
ASETS = os.path.join(BENCH, "assets", CASE)

PROMPT = ('/rundata/dscqa_sim/V0/simdir/finesim/dscqaF2/MatrixRun/'
          'MatrixRun_Netlist_Vcap_20260916PM_DDR6TOP.Meta  '
          'zhegelujingxia you henduo mulu ,meige muluxia youge si.inp wenjian ,'
          'bangwo xiege mingling ,woyao shandiao si.inp zhong T_mBistOsc zifuchuan')

TASK_BRIEF = ("交付接口：outputs/submit.zip 内含 1 个脚本（.py 或 .sh），接受一个位置参数=根目录，"
              "递归找出所有 si.inp 并原地删除其中的 T_mBistOsc 标记（含其尾随空格）。\n"
              "可见示例输入：assets/EDA-Eval-DesignFlow-SiInpTokenRm-001/matrix_run_A/（8 个子目录，各含 si.inp）。\n")

RATIONALE = ("14 条断言：① submit.zip 含且仅含 1 个脚本（.py/.sh） ② 脚本语法校验通过（py_compile / bash -n） "
             "③ 脚本接受根目录位置参数（运行无 usage 错误） ④ B 上脚本 exit 0 ⑤ B 上所有 si.inp 中独立 T_mBistOsc 标记完全消失（0 处） "
             "⑥ B 上 finesim_ignore 行其他标记保留（除 T_mBistOsc 外无标记被删，B 专属标记仍在） "
             "⑦ B 上 .option finesim_ignore = \"...\" 行结构保留（前缀/闭合引号完好） ⑧ B 上非 finesim_ignore 行不变（sha256 比对 header/.tran/.meas/.end） "
             "⑨ B 上 10 个含目标子目录全部被处理 ⑩ B 上 2 个无目标 decoy si.inp 字节级未改动 "
             "⑪ B 上子串 decoy 标记 T_mBistOscTail 保留（识别朴素 s/T_mBistOsc// 子串删除） ⑫ A 泛化（A 上 T_mBistOsc 全部删除，非硬编码 B 路径） "
             "⑬ A/B 不泄漏（A/B 运行数与标记集不同，B 专属标记不泄入 A） ⑭ 3x 幂等且无孤立双空格（B 上 3 次运行产出一致，删除处无残留双空格）")

# attachments: list A tree si.inp files + prompt.txt + task_brief.md
att = []
a_root = os.path.join(ASETS, "matrix_run_A")
for d in sorted(os.listdir(a_root)):
    sd = os.path.join(a_root, d)
    if os.path.isdir(sd):
        for fn in sorted(os.listdir(sd)):
            if fn == "si.inp":
                rel = "matrix_run_A/%s/si.inp" % d
                att.append({"name": rel, "source": rel,
                            "desc": "FineSim si.inp 示例输入（A 资产，子目录 %s）：含 .option finesim_ignore 行，"
                                    "行中标记集含 T_mBistOsc（待删除）" % d})
att.append({"name": "prompt.txt", "source": "prompt.txt",
            "desc": "真实用户原话（A-faithful，mike @ hfeg0plg05，trace 1789611712575_5tdum U#0 逐字拼音）："
                    "路径下多目录各含 si.inp，写个命令删除 si.inp 中 T_mBistOsc 字符串"})
att.append({"name": "task_brief.md", "source": "task_brief.md",
            "desc": "交付接口说明：outputs/submit.zip 内含 1 个脚本，接受根目录位置参数，递归原地删除 si.inp 中 T_mBistOsc 标记"})

with open(os.path.join(REF, "check.py")) as f:
    test_src = f.read()

case = {
    "id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "prompt": PROMPT,
    "attachments": att,
    "test": test_src,
    "metadata": {
        "trace_source": {
            "user": "mike",
            "host": "hfeg0plg05",
            "session_file": "1789611712575_5tdum.messages.json",
            "match_count": 3368,
            "real_task_summary": "FineSim MatrixRun 目录下多个子目录各含 si.inp，用户要求写命令删除 si.inp 中 T_mBistOsc 字符串；"
                                 "金标准=assistant msg_MTSgZiyu（find -name si.inp -exec sed -i 's/T_mBistOsc //g'，"
                                 "从 .option finesim_ignore = \"R_RasEnOsc ... T_mBistOsc AG_TSOsc ...\" 行删除独立 T_mBistOsc 标记含尾随空格，"
                                 "其余标记/行不变；策略禁写 /rundata 故交付命令而非直接编辑）"
        },
        "domain": "spice_sim",
        "track": "faithful",
        "level": "L1",
        "test_rationale": RATIONALE,
    },
}

# verify test==disk sha
disk_sha = hashlib.sha256(test_src.encode()).hexdigest()[:12]
jsonl_sha = hashlib.sha256(case["test"].encode()).hexdigest()[:12]
assert disk_sha == jsonl_sha, "test sha mismatch: disk=%s jsonl=%s" % (disk_sha, jsonl_sha)

before = sum(1 for _ in open(JSONL))
with open(JSONL, "a") as f:
    f.write(json.dumps(case, ensure_ascii=False) + "\n")
after = sum(1 for _ in open(JSONL))
print("appended %s: jsonl %d -> %d" % (CASE, before, after))
print("test sha (disk==jsonl):", disk_sha)
# sanity: reload and confirm
with open(JSONL) as f:
    last = json.loads(f.readlines()[-1])
assert last["id"] == CASE
assert last["metadata"]["test_rationale"].startswith("14 条断言：")
print("OK: last entry id=%s, rationale starts with 14 条断言" % last["id"])
