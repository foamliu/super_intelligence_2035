#!/usr/bin/env python3
"""Append EDA-Eval-DesignFlow-FsdbVerdiInteg-001 to EDA-Eval-DesignFlow_A.jsonl."""
import os, json

CASE = "EDA-Eval-DesignFlow-FsdbVerdiInteg-001"
BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
ASSET_DIR = os.path.join(BENCH, "assets", CASE)
REF_DIR = os.path.join(BENCH, "reference", CASE)
JSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_A.jsonl")

# test field = check.py source
with open(os.path.join(REF_DIR, "check.py")) as f:
    test_src = f.read()

prompt = (
    "请修改testbench和makefile，目标是生成fsdb 并使用verdi查看波形\n"
    "\n"
    "【工作目录文件】\n"
    "- top.sv: SystemVerilog 测试平台顶层（当前用 $dumpfile/$dumpvars 生成 VCD 波形）\n"
    "- makefile: VCS 编译/仿真流程（run 目标检查 dump.vcd；verdi 目标用 -ssf *.fsdb）\n"
    "- file.list: 源文件列表\n"
    "\n"
    "交付方式见 task_brief.md。"
)

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "prompt": prompt,
    "attachments": [
        {"name": "top.sv", "source": "top.sv", "desc": "SystemVerilog 测试平台顶层 (visible A, 当前 VCD 转储，待改为 FSDB)"},
        {"name": "makefile", "source": "makefile", "desc": "VCS 编译/仿真 makefile (visible A, run 检查 dump.vcd, verdi 用 -ssf *.fsdb glob)"},
        {"name": "file.list", "source": "file.list", "desc": "源文件列表 (内容: top.sv)"},
        {"name": "task_brief.md", "source": "task_brief.md", "desc": "交付接口说明 (submit.zip 含 integrate_fsdb.py, mode=design_flow/entry=outputs/submit.zip)"},
    ],
    "entry_point": "outputs/submit.zip",
    "expected_artifacts": ["integrate_fsdb.py"],
    "test": test_src,
    "budget": {"max_turns": 30, "timeout_sec": 1800},
    "metadata": {
        "domain": "verification",
        "task_name": "FSDB 波形转储 + Verdi 查看 集成 (VCS→FSDB, makefile verdi 目标修复)",
        "scenario": "A-faithful: 真实 cline trace (lorikx@hfeg0pkn001, mc=395) 中用户逐字要求把 VCS 仿真 的 VCD 波形改为 FSDB 并能用 Verdi 查看。assistant 修改 top.sv ($dumpfile/$dumpvars→$fsdbDumpfile/$fsdbDumpvars + `ifdef DUMP_VCD 逃生通道) 与 makefile (新增 OUTPUT_NAME/WAVE_FILE, 把 per-param +define+ 重构为 VCS 与 Verdi 共用的 PARAM_DEFS, run 目标 dump.vcd→$(WAVE_FILE), verdi 目标 *.fsdb glob→-ssf $(WAVE_FILE) + -sverilog + PARAM_DEFS), 并在 VCS R-2023.12 + Verdi 实跑验证 (timing.fsdb 277 信号, fsdb2vcd finished, verdi CLI 接受全部参数)。assets 交付忠实重建的 BEFORE 状态；隐藏 B (top_B.sv USER_OUTPUT_NAME=\"sram_run\"/DEPTH=256/DATA_WIDTH=32/MUX=8/CD=0/RD_DELAY, makefile_B 多 RD_DELAY 块) 结构不同, check() 在 B 上跑候选 + GNU make -n dry-run 验证, 跨输入守卫击败 \"timing\" 硬编码。",
        "difficulty": "L2-static",
        "artifacts": ["integrate_fsdb.py", "outputs/submit.zip"],
        "track": "faithful",
        "layer": "L2",
        "trace_source": {
            "user": "lorikx",
            "host": "hfeg0pkn001",
            "session_file": "1793005700370_jzlbn.messages.json",
            "match_count": 395,
            "real_task_summary": "VCS+Verdi SRAM 验证环境: 用户要求把 testbench 的 VCD 波形改为 FSDB 并能用 Verdi 查看。assistant(deepseek-v4-flash) 修改 top.sv 把 $dumpfile/$dumpvars 换成 $fsdbDumpfile/$fsdbDumpvars (加 `ifdef DUMP_VCD 逃生通道), makefile 新增 OUTPUT_NAME/WAVE_FILE, 把 per-param +define+ 重构为 VCS 与 Verdi 共用的 PARAM_DEFS, run 目标 dump.vcd 检查改为 $(WAVE_FILE), verdi 目标 *.fsdb glob 改为 verdi -sverilog -f file.list $(PARAM_DEFS) -ssf $(WAVE_FILE); VCS R-2023.12 实跑生成 timing.fsdb (277 信号, 0→7.75us), fsdb2vcd -summary 确认 finished, verdi CLI (绕过沙箱 LD_PRELOAD 污染) 接受全部参数并持续运行到超时; 后续轮次还封装了 redundancy_all_states_128x144 便捷目标并对齐 VERDI_HOME 版本。",
        },
        "test_rationale": (
            "16 条断言：①submit.zip含integrate_fsdb.py ②integrate_fsdb.py可py_compile ③CLI接受3位置参数(top.sv,makefile,out_dir)exit0并产出out top.sv+makefile ④out top.sv含$fsdbDumpfile且含$fsdbDumpvars ⑤out top.sv有`ifdef DUMP_VCD逃生通道且FSDB为默认(`else分支)、VCD $dumpfile在`ifdef DUMP_VCD分支 ⑥out makefile定义OUTPUT_NAME且用?=(可覆盖默认) ⑦out makefile定义WAVE_FILE引用$(OUTPUT_NAME)且含.fsdb ⑧out makefile verdi目标含verdi+-ssf+-sverilog+-f且无*.fsdb glob ⑨out makefile run目标用`if[ -f $(WAVE_FILE)]检查且不含dump.vcd ⑩out makefile有共享PARAM_DEFS变量且verdi目标与VCS_OPTS均使用它 ⑪make -n verdi(默认B)exit0且命令含-ssf sram_run.fsdb+-sverilog++define+USER_ ⑫make -n build exit0且vcs命令含+define+USER_(参数到达VCS) ⑬make -n verdi OUTPUT_NAME=custom exit0且命令含-ssf custom.fsdb(覆盖生效) ⑭跨输入守卫:默认make -n verdi含sram_run.fsdb且不含timing.fsdb(击败A硬编码) ⑮反stub:源含re.compile/re.sub+open(+.write((真变换) ⑯out makefile verdi目标不用-ssf *.fsdb glob(用$(WAVE_FILE)或$(OUTPUT_NAME).fsdb)"
        ),
    },
}

# sanity: k_rationale == k_check
import re
k_check = 16
# count circled-number marks in rationale
marks = len(re.findall(r'[①-⑯]', entry["metadata"]["test_rationale"]))
print("k_check=%d  circled_marks=%d  rationale_starts_with_prefix=%s"
      % (k_check, marks, entry["metadata"]["test_rationale"].startswith("16 条断言：")))
assert entry["metadata"]["test_rationale"].startswith("16 条断言："), "rationale must start with '16 条断言：'"
assert marks == k_check, "circled marks %d != k_check %d" % (marks, k_check)
assert k_check >= 8

# append
with open(JSONL, "a") as f:
    f.write(json.dumps(entry, ensure_ascii=False) + "\n")
print("appended %s to %s" % (CASE, JSONL))

# verify roundtrip: last line parses, test field == disk check.py
with open(JSONL) as f:
    lines = f.readlines()
last = json.loads(lines[-1])
assert last["task_id"] == CASE
assert last["test"] == test_src, "test field != disk check.py"
print("roundtrip OK: %d lines total, test field bytes=%d == disk check.py" % (len(lines), len(last["test"])))
