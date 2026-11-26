#!/usr/bin/env python3
"""Build reference_submit.zip + prompt.txt + task_brief.md + run self-verify for LvsRptAnalyze-001."""
import json, os, shutil, subprocess, sys, zipfile, hashlib

REPO = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow"
CID = "EDA-Eval-DesignFlow-LvsRptAnalyze-001"
REF = os.path.join(REPO, "reference", CID)
AST = os.path.join(REPO, "assets", CID)

# ── prompt.txt ──
PROMPT = """你在帮 DRAM 物理验证组分析一份 Calibre LVS 跑完的结果报告。

## 背景
组员 fhwang 跑完一次 LVS（Layout Versus Schematic），Calibre 产出一个非常大的 `.lvs.report`（可达数百 MB）、一个 `.lvs.report.ext`（提取警告）和一个 `.erc.summary`（ERC 汇总）。报告太大了，人眼根本看不过来。他提了个需求（原话）：

> 「帮我分析一下这个结果路径下LVS的结果文件错误类型，并附带解决方案方向」

> 「把上述你的分析方案生成文本文件放到这个路径下」

## 你要做的
写一个**命令行工具 `analyze_lvs.py`**，吃三个输入文件，自动解析 LVS 报告、提取警告、ERC 汇总，分类错误类型，算出各错误数量，再生成一份**结构化的 Markdown 分析报告** + 一份**结构化 JSON 摘要**。

## 三个输入文件
1. **LVS 报告**（`--report`）：文本文件，开头是 `# Calibre <版本> LVS run` + `# Cell:` + `# Layout:` + `# Source:`，然后是一堆 `# LVS RECOGNIZE GATES = ...` 等 rule 设置行。中间有 `LVS COMPARISON RESULTS` 段，含 `Overall LVS Result: CORRECT/INCORRECT`、`Connectivity errors: YES/NO`、`Property errors: YES/NO`、`SUMMARY OF TOTAL RESULTS`、`Property Error #N: Layout W = <数字>u  Source W = <数字>u  diff = <数字>%  Device: <类型>`、`Connectivity error: ... has no similar net`、`missing smashed mosfet: <数字> occurrences`、`Short circuits found: <数字>`、`Open circuits detected: <数字>`。
2. **提取警告**（`--ext`）：文本文件，含若干段：
   - `Open circuit - Same name on different nets` 后跟 `cell "..."` + `Name: "<信号名>"`
   - `Unattached label` 后跟 `cell "...": "<信号名>" at ...`
   - `Unattached port` 后跟 `cell "...": port "<信号名>" unattached`
   - `Virtually connected label` 后跟 `cell "...": "<信号名>" at ...`
   - `Stamping conflict` 后跟 `SCONNECT stamping conflict on net "..."`
3. **ERC 汇总**（`--erc`）：文本文件，含 `ERC errors: <数字>`、`ERC warnings: <数字>` + 一堆 `- <类型>: <数字>` 明细行。

## CLI 接口
```
analyze_lvs.py --report <lvs.report> --ext <lvs.report.ext> --erc <erc.summary> --outdir <输出目录>
```

## 输出（写到 `--outdir`）
1. **`error_summary.json`**：结构化 JSON，含这些键：
   - `top_cell`：从报告 `# Cell:` 提取
   - `lvs_result`：`CORRECT` 或 `INCORRECT`
   - `tool_version`：从 `# Calibre <版本> LVS run` 提取
   - `report_lines`：从 `# Total lines in report:` 提取
   - `layout`、`source`：从 `# Layout:` / `# Source:` 提取
   - `rule_settings`：dict，含 `recognize_gates` / `filter_unused_option` / `virtual_connect_colon` / `execute_erc` 等键
   - `error_counts`：dict，含 `connectivity_errors`（1/0）/ `property_errors`（Property Error 行数）/ `missing_smashed_mosfet`（数字）/ `short_circuits` / `open_circuits` / `correct_cells` / `incorrect_cells`
   - `property_errors`：list，每个元素 `{disc, layout_w, source_w, diff_pct, device}`，`diff_pct` 必须重新计算（`|layout_w - source_w| / source_w * 100`，保留 1 位小数）
   - `ext_warnings`：dict，含 `open_circuit` / `unattached_label` / `unattached_port` / `virtually_connected` / `stamping_conflict` 计数
   - `ext_signals`：dict，每类警告涉及的信号名列表
   - `erc`：dict，含 `erc_errors` / `erc_warnings` / `detail`
2. **`lvs_analysis_report.md`**：人类可读 Markdown 报告，必须含以下章节：
   - `## 基本信息`（表格：Top Cell、LVS 结果、报告行数、Layout、Source、工具版本）
   - `### Rule 关键设置`（列出 RECOGNIZE GATES / FILTER UNUSED OPTION / VIRTUAL CONNECT COLON / EXECUTE ERC）
   - `## 总体错误摘要`（表格：Connectivity errors、Property errors、Unbalanced smashed mosfets、Overall Result）
   - `## 错误类型详细分类`（Connectivity errors 段 + Property errors 段含 W 不匹配表格 + 提取警告段含 .ext 计数表格）
   - `## 根因分析`（列出根本原因）
   - `## 解决方案方向`（针对每类错误给出可操作的修复建议，如 label 命名、svdb 可视化、VIRTUAL CONNECT 设置等）

## 真实例子（参考）
组员实际跑过这样的命令（**这只是参考格式，你交付的工具要能处理任意 LVS 报告**）：
```
python3 analyze_lvs.py \\
  --report Array3G_TOP_L.lvs.report \\
  --ext Array3G_TOP_L.lvs.report.ext \\
  --erc Array3G_TOP_L.erc.summary \\
  --outdir out/
```

## 交付
把 `analyze_lvs.py` 打包成 `outputs/submit.zip`（zip 根目录放 `analyze_lvs.py` 一个文件即可）。

## 附件
- `lvs_report_A.txt`：某次 LVS 报告（Cell: Array3G_TOP_L，INCORRECT，Calibre v2020.1，含 Property Error W=2.717u vs 1.476u、1224 missing smashed mosfet、no similar net 等）
- `lvs_report_A.txt.ext`：对应的 .ext 提取警告（Open circuit SecEnGapN/vap2!、Unattached label viso!/VncsgnEn 等）
- `erc_summary_A.txt`：对应的 ERC 汇总

附件只供你理解格式和本地试跑。判分会用**另一组隐藏的 LVS 报告**（不同 Cell 名、不同错误数量、不同信号名、甚至可能是 CORRECT 通过的 case）来验你的工具，所以**不要硬编码**附件里的 Cell 名 / W 值 / 错误数 / 信号名 / Calibre 版本。
"""
with open(os.path.join(AST, "prompt.txt"), "w") as f: f.write(PROMPT)

# ── task_brief.md (≤3 lines, only delivery interface + file location) ──
BRIEF = """## 交付接口
- 交付物：`outputs/submit.zip`，zip 根目录含 `analyze_lvs.py` 一个文件。
- 工具签名：`analyze_lvs.py --report <file> --ext <file> --erc <file> --outdir <dir>`
- 输出：`<outdir>/error_summary.json` + `<outdir>/lvs_analysis_report.md`
- 判分会用隐藏的 LVS 报告（含一个 INCORRECT case 和一个 CORRECT case）跑你的工具，独立于附件。
"""
with open(os.path.join(AST, "task_brief.md"), "w") as f: f.write(BRIEF)

# ── reference_submit.zip (analyze_lvs_ref.py renamed to analyze_lvs.py) ──
ref_py = os.path.join(REF, "analyze_lvs_ref.py")
submit_zip = os.path.join(REF, "reference_submit.zip")
if os.path.exists(submit_zip): os.remove(submit_zip)
with zipfile.ZipFile(submit_zip, "w", zipfile.ZIP_DEFLATED) as z:
    z.write(ref_py, arcname="analyze_lvs.py")
print("reference_submit.zip built:", submit_zip)

# ── self-verify: ref PASS ──
import importlib.util
spec = importlib.util.spec_from_file_location("check_mod", os.path.join(REF, "check.py"))
check_mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(check_mod)
res = check_mod.check(submit_zip, AST)
print("REF CHECK:", res)
if not res.startswith("PASS"):
    print("!!! REF FAILED — aborting"); sys.exit(1)
print("self-verify ref PASS OK")
