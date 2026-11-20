#!/usr/bin/env python3
import json, os, hashlib

CASE_ID = "EDA-Eval-DesignFlow-AgingStepDirSplit-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
REF_DIR = os.path.join(BENCH, "reference", CASE_ID)
CHECK = os.path.join(REF_DIR, "check.py")
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_D.jsonl")

check_src = open(CHECK).read()

prompt = """dandans 在 hfeg0pkn002 上用 FineSim 跑 matrix coverage 仿真，aging 流程分两步：step1（fresh-stress 仿真）和 step2（post-stress measure 仿真）。当前 matrixrun 仿真器脚本把每个 step1 仿真目录直接建在 $MatrixDir/<sim>_step1/ 下，再把对应的 step2 仿真嵌在 $MatrixDir/<sim>_step1/AgingStep2Sim/<sim>_step2/ 下（即每个 step2 仿真挂在各自 step1 目录的 AgingStep2Sim 子目录里）。dandans 想把 aging 这部分代码改成：所有 step1 仿真统一放进同一个目录，所有 step2 仿真统一放进另一个目录。

请基于 workdir 里提供的 matrixrun_A.pl（该仿真器的精简复刻版，保留了 aging 两步仿真目录构建逻辑与 write_runfile 子过程）和 cfg_A.tsv（仿真用例配置，每行 `regName pvt width`），写一个 Python 脚本 aging_dir_rewrite.py，命令行用法 `aging_dir_rewrite.py <input.pl> <output.pl>`：读取输入 Perl 脚本，把 aging 部分的目录布局改写为 —— 所有 step1 仿真目录放进 $MatrixDir/step1/<sim>/，所有 step2 仿真目录放进 $MatrixDir/step2/<sim>/（两个目录平铺在 MatrixDir 顶层，去掉原来 step2 嵌在 step1 下的 AgingStep2Sim 中间层），其余逻辑保持不变，把改写后的完整 Perl 脚本写到 <output.pl>。

交付：把 aging_dir_rewrite.py 打包成 outputs/submit.zip。要求：脚本只用 Python 标准库；能泛化到结构不同（matrix 目录变量名 / 仿真器名 / step 后缀 / 嵌套标记名 / sim name 字段名均不同）的同形态脚本；对同一输入多次运行输出完全一致。"""

rationale = ("15 条断言："
  "① submit.zip 含且仅含 1 个 .py 候选脚本 "
  "② 候选脚本 py_compile 编译通过 "
  "③ 候选脚本对 A 输入运行退出码 0 且 out_A.pl 非空 "
  "④ out_A.pl 通过 perl -c 语法检查 "
  "⑤ perl out_A.pl --aging 实跑退出码 0 并生成 runA 目录树 "
  "⑥ runA 顶层存在 step1/ 目录（所有 step1 仿真在同一目录） "
  "⑦ runA 顶层存在 step2/ 目录（所有 step2 仿真在另一目录） "
  "⑧ runA 全树无 AgingStep2Sim 目录（旧嵌套标记已消除） "
  "⑨ step1/ 含且仅含 N_A 个仿真子目录，每个子目录有 1 个含 'step1' 的 .run 文件 "
  "⑩ step2/ 含且仅含 N_A 个仿真子目录，每个子目录有 1 个含 'step2' 的 .run 文件 "
  "⑪ 候选脚本对隐藏 B 输入运行退出码 0 且 out_B.pl 非空（泛化） "
  "⑫ perl out_B.pl --aging 实跑退出码 0 且 runB 顶层同时存在 step1/ 与 step2/ 目录 "
  "⑬ runB 全树无 StepTwoSims 目录（B 的旧嵌套标记已消除） "
  "⑭ 反硬编码：out_B.pl 不含 A 专属 token（AgingStep2Sim/finesim/regA-regD） "
  "⑮ 3 次重跑候选脚本对 A 的输出 md5 完全一致（确定性）")

entry = {
  "task_id": CASE_ID,
  "mode": "design_flow",
  "entry_point": "outputs/submit.zip",
  "prompt": prompt,
  "attachments": [
    {"name": "matrixrun_A.pl", "source": "matrixrun_A.pl",
     "desc": "FineSim matrix coverage 仿真器精简复刻 Perl 脚本（aging 两步仿真目录构建：step1 直接挂 $MatrixDir/<sim>_step1/，step2 嵌在 $MatrixDir/<sim>_step1/AgingStep2Sim/<sim>_step2/；含 write_runfile 子过程与 GetOptions/--aging/--dryrun 接口）"},
    {"name": "cfg_A.tsv", "source": "cfg_A.tsv",
     "desc": "A 仿真用例配置：4 行 `regName pvt width`（regA TT_85 X2P6 / regB TT_85 X2P6 / regC SS_125 X3P0 / regD FF_m40 X2P6）"},
    {"name": "task_brief.md", "source": "task_brief.md",
     "desc": "交付接口与文件位置说明（≤3 行）：submit.zip 含 aging_dir_rewrite.py，CLI `<input.pl> <output.pl>`，输入 matrixrun_A.pl + cfg_A.tsv"},
  ],
  "expected_artifacts": ["outputs/submit.zip"],
  "test": check_src,
  "metadata": {
    "domain": "schematic_netlist",
    "grade": "B",
    "level": "L2",
    "track": "synthesized",
    "trace_source": {
      "user": "dandans",
      "host": "hfeg0pkn002",
      "session_file": "1791768325372_g13dw.messages.json",
      "match_count": 58,
      "real_task_summary": "dandans 用 FineSim 跑 matrix coverage 仿真（aging 两步：step1 fresh-stress / step2 post-stress measure），当前 step2 仿真嵌在各自 step1 目录的 AgingStep2Sim 下；用户要求改 aging 代码使所有 step1 仿真放同一目录、所有 step2 仿真放另一目录（msg#0 用户原话需求，未给根因/修复，agent 因 agent-policy 拒绝未完成）"
    },
    "test_rationale": rationale,
  },
}

line = json.dumps(entry, ensure_ascii=False)
# validate roundtrip
json.loads(line)
open(JSONL, "a").write(line + "\n")
print("appended:", CASE_ID)
print("check.py sha", hashlib.md5(check_src.encode()).hexdigest()[:8], "size", len(check_src))
print("rationale k=15, starts with '15 条断言：':", rationale.startswith("15 条断言："))
