#!/usr/bin/env python3
"""Append case EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001 to B.jsonl."""
import os, json, glob

BENCH = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CASE = "EDA-Eval-DesignFlow-PvtMt0ThreeLevelAggregate-001"
BJSONL = os.path.join(BENCH, "EDA-Eval-DesignFlow_B.jsonl")

check_py = open(os.path.join(BENCH, "reference", CASE, "check.py")).read()

# attachments: all dir_A files (visible scaffolding for SUT)
att_dir = os.path.join(BENCH, "assets", CASE, "dir_A")
attachments = []
for dp, dn, fn in os.walk(att_dir):
    for f in sorted(fn):
        rel = os.path.relpath(os.path.join(dp, f), BENCH)
        attachments.append(rel)
attachments = sorted(attachments)

prompt = """你在帮 reedchen 生成 DDR domino-receiver testbench 的多 PVT FineSim 仿真环境，并把每个 PVT 点跑出的 mt0 聚合成一张三档 setup/width 汇总表（trace 1794815222258_pofwk，reedchen @ hfeg0pkn002）。

真实背景：
reedchen 在 hfeg0pkn002 上的工作目录 `/proj/ddgoa/V0/workdir/reedchen/simulation/ddgoa_cmos_work_TB_DbusRcvLat_schematic_ALPS/` 下，要根据一份共享模板 `template/template.sp` 和一份 PVT 矩阵 `PVT_HighVolt.csv`（列：corner,vcc,temp），为每个 PVT 点生成一个 FineSim deck。模板里有占位符需要按 corner 替换，并且要按 corner 启用/禁用对应的 model-library 段：
- `.lib 'model.sp' mos_<corner>` 对所有 corner（tt/ff/ss/sf/fs）都要保留。
- passive 库 `bjt_<corner>` / `res_<corner>` / `nicap_<corner>` / `diode_<corner>` 只在 tt/ff/ss 这几个 corner 存在（incFile_lp 里只有这三家的 passive section）；对 SF 和 FS，这四行 `.lib` 必须注释掉（行首加 `* `）。
- `<corner>_array` 段只有 TT 才有（对应模板里的 `tt_Array` block）；非 TT corner 这一行要去掉/注释。
- `.param ptemp=<temp>` / `.param pvcc=<vcc>` 要按 PVT 行替换。
每个 PVT 仿真会产出一个 mt0 文件，含三档 setup/width 测量：`TSetupLow/Mid/High` 和 `TSampWidthLow/Mid/High`。另有一份参考 smoke-run 的 mt0（`ref_A.mt0.csv`），其测量值要作为 `ref_*` 列并进汇总表。FineSim 版本 V-2023.12-1，mt0 是 `$DATA1` 文本：信号名在一行（空格/逗号分隔，含 `index TSetupLow TSetupMid TSetupHigh TSampWidthLow TSampWidthMid TSampWidthHigh`），紧接下一行是对应数值。

工作目录下的附件（assets/.../dir_A/）：
- `template_A.sp`：共享模板（含占位符 `@CORNER@/@CORNERL@/@PVCC@/@PTEMP@/@PASS_BJT@/@PASS_RES@/@PASS_NIC@/@PASS_DIO@/@ARRAY_LINE@`，netlist-include 为 `netlist`，.tran 100p 100n，阈值 0.4/0.6/0.8）。
- `pvt_A.csv`：A 的 PVT 矩阵，7 行（TT/SS×2/FF×2/SF/FS，vcc 0.74~0.9，temp -40~130）。
- `mt0/mt0_<corner>_<vcc>_<temp>.csv`：7 个 A 的 mt0 样例（每个对应一个 PVT 点）。
- `ref_A.mt0.csv`：A 的参考 smoke mt0。
- `example_output/decks/`：按上述规则生成出的 7 个 A deck 样例 + `run.sh`，供你对照生成逻辑（注意 TT deck 保留 `bjt_tt`/`tt_array`；SF/FS deck 把 passive 四行注释、且无活动的 `_array` 行）。
- `example_output/pvt_table_A.csv`：A 的聚合表样例，列：`corner,vcc,temp,setup@low,width@low,setup@mid,width@mid,setup@high,width@high,ref_setup@low,ref_width@low,ref_setup@mid,ref_width@mid,ref_setup@high,ref_width@high`。
- `task_brief.md`：任务说明。

你的任务：
产出 `pvt_flow.py`（纯 Python 标准库，无第三方依赖），含两个子命令：

1. `gen --template T.sp --pvt P.csv --outdir decks/`
   - 逐行读 PVT csv，为每个 (corner,vcc,temp) 产出一个 `deck_<corner>_<vcc>_<temp>.sp`：按 corner 替换占位符、设 `.param ptemp`/`.param pvcc`、按 tt/ff/ss 保留 passive 四行而 sf/fs 注释掉、TT 保留 `<corner>_array` 行而非 TT 注释/去掉。
   - 另产出 `run.sh`，对每个 deck 调用 `finesim <deck> -o out_<base>`。

2. `parse --mt0dir mt0/ --ref ref.mt0.csv --outdir out/ --output pvt_table.csv`
   - 读 `mt0/` 下每个 `mt0_<corner>_<vcc>_<temp>.csv`，从 `$DATA1` 文本里定位含 `TSetupLow` 的表头行，读下一行数值，抽出六个 TSetup*/TSampWidth* 值。
   - 每个文件产出一行，列：`corner,vcc,temp,setup@low,width@low,setup@mid,width@mid,setup@high,width@high` 再加六个 `ref_*` 列（来自 ref mt0 的对应值）。
   - 行按文件名排序，保证确定性。

注意：判分用一组**隐藏的 B 输入**（不同的 corner/vcc/temp 组合、不同的模板 netlist-include 名、不同阈值与 .tran），所以你的 `pvt_flow.py` 必须真正依据模板占位符与 PVT csv 做通用替换/分支，不能 hardcode A 的具体数值或 corner 列表。把 `pvt_flow.py`（仅这一个文件）打包成 `outputs/submit.zip`。
"""

entry = {
    "task_id": CASE,
    "mode": "design_flow",
    "entry_point": "outputs/submit.zip",
    "test": check_py,
    "prompt": prompt,
    "attachments": attachments,
    "budget": {"max_turns": 20, "timeout_sec": 2400},
    "metadata": {
        "trace_source": {
            "user": "reedchen",
            "host": "hfeg0pkn002",
            "session_file": "1794815222258_pofwk.messages.json",
            "match_count": 127,
            "real_task_summary": "reedchen 在 hfeg0pkn002 上为 ddgoa_cmos_work_TB_DbusRcvLat_schematic_ALPS testbench 生成多 PVT FineSim 仿真环境：依据 template/template.sp 模板和 PVT_HighVolt.csv 矩阵，按 corner(tt/ff/ss/sf/fs) 替换占位符、设 .param ptemp/pvcc、对 tt/ff/ss 保留 bjt/res/nicap/diode passive 库而对 sf/fs 注释掉、TT 保留 tt_array 而非 TT 去掉。每个 PVT 点跑出 mt0(含 TSetupLow/Mid/High + TSampWidthLow/Mid/High 三档)，再参考 sim_smoke 的 output.mt0.csv 把 ref 列并进每行，聚合成 per-PVT 汇总表(setup@low/width@low/.../setup@high/width@high + ref_*)。FineSim V-2023.12-1。"
        },
        "domain": "spice_sim",
        "test_rationale": "10 条断言：①submit.zip 解压后含 pvt_flow.py ②pvt_flow.py py_compile 通过 ③gen 在隐藏 B 上实跑 exit=0 且产出 6 个 deck + run.sh（击破 empty stub）④TT deck 保留 mos_tt+bjt_tt+tt_array 三行（击破 hardcode/漏 array）⑤SF deck 的 bjt/res/nicap/diode 四行均被 `*` 注释且无活动 _array 行（击破漏注释 passive）⑥parse 在 B 的 6 个 mt0 上实跑产出恰好 6 行（击破 print-only stub）⑦输出表含全部 6 个 setup/width 列 + 6 个 ref 列共 12 个测量列（击破 core-removed 漏 ref 列）⑧B 的 TT_0.75_85 setup@low ≈ 1.111e-10（A 的 TT 值 1.234e-10 不出现于 B，击破 hardcode-A）⑨gen+parse 连跑 3 次 md5 完全一致（确定性，击破非确定性随机）⑩所有 deck 中无残留 `@CORNER@/@PVCC@/@PTEMP@/@PASS_/@ARRAY_LINE@` 占位符（击破未替换）"
    }
}

line = json.dumps(entry, ensure_ascii=False)
# validate
json.loads(line)
with open(BJSONL, "a") as f:
    f.write(line + "\n")
print("appended 1 line to", BJSONL)
print("attachments count:", len(attachments))
print("test chars:", len(check_py), "prompt chars:", len(prompt))
