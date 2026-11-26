# Trace Deepread: 1792223414540_erhym (fhwang @ hfeg0plg108)

## Metadata
- **session**: 1792223414540_erhym
- **user**: fhwang
- **host**: hfeg0plg108
- **mc**: 353
- **keywords**: lvs:877;drc:529;mosfet:405;analog:400;calibre:190;aether:52
- **domain**: physical_verify (LVS result analysis)
- **msgs**: 134
- **file size**: 517KB

## User Intent (verbatim, A档 candidate)
- **U#1** (task): "帮我分析一下这个结果路径下LVS的结果文件错误类型，并附带解决方案方向 /proj/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L"
- **U#2**: "把上述你的分析方案生成文本文件放到 /proj/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L"
- **U#3**: "/skill-creator" (wants to create a skill from the analysis)
- **U#4**: "上面我询问你的结果中连线错误是否可能只是2个block cell 输出和下一级输入的2个信号接错了位置导致的" (hypothesis about root cause — NOT A档 suitable)

**A档 selection**: U#1 is the task — user expresses need (analyze LVS errors), does NOT give root cause or fix.

## Assistant Workflow
1. Listed files in LVS result directory: `.lvs.report` (260MB, 1.9M lines), `.lvs.report.ext`, `.gds`, `.cdl`, `.sp`, `_calibreLVS.rule_`, etc.
2. Ran `head -200`, `tail -200`, `grep` on the report to find error patterns
3. Wrote `analyze_lvs.py` — Python script that:
   - Reads last 30MB of report (for comparison results)
   - Scans for error patterns: Error, Incorrect, Discrepancy, FAIL, not match, Unmatched, Missing
   - Counts extraction warnings from `.ext` file: Open circuit, Unattached label, Unattached port, Virtually connected, Stamping conflict
   - Categorizes mismatch types: Port/Net, Device, Property, Connection, Short/Open, Missing cell
   - Generates solution directions for each error type
4. Ran the script — found:
   - Overall: **INCORRECT**
   - 1224 missing smashed mosfets
   - Cross-coupled signal swap patterns in INCORRECT OBJECTS
   - Property errors (W value mismatch)
   - Extraction warnings from .ext file
5. Generated `LVS_ANALYSIS_REPORT.md` (7.4KB, 213 lines) with sections:
   - 基本信息 (Basic info: cell name, tool version)
   - 总体错误摘要 (Overall errors: INCORRECT)
   - 错误类型详细分类 (Error type classification)
   - 根因分析 (Root cause analysis: smashed MOSFET matching chaos)
   - 解决方案方向 (Solution directions: 4 approaches)
6. U#4 follow-up: user hypothesized signal swap; assistant confirmed cross-coupled swap pattern but larger scope

## Key LVS Report Structure (from tool results)
- Calibre v2020.1_36.18
- Line 25: "OVERALL COMPARISON RESULTS"
- Line 346: "CELL COMPARISON RESULTS (TOP LEVEL)"
- "missing smashed mosfet" lines: `X3/X0/X165/X103/X31/X51/M0(-7868.014,1525.675)  ** missing smashed mosfet **`
- .ext file contains: "Open circuit - Same name on different nets", "Unattached label", "Unattached port", "Virtually connected", "Stamping conflict"

## Case Design
- **Task**: Write a Python script `analyze_lvs.py <report_path> <ext_path> <output_json>` that parses a Calibre LVS report + .ext file and outputs a structured JSON analysis
- **A (visible)**: Synthetic LVS report (Array3G_TOP_L.lvs.report, ~200 lines) + .ext file + prompt (U#1 verbatim) + task_brief
- **B (hidden)**: Different LVS report with different cell name, different error counts, different error types, different .ext warnings
- **check.py**: ≥10 conditions — run script on B, verify JSON output fields match expected values from B
- **Deliverable**: outputs/submit.zip containing analyze_lvs.py + analysis report JSON
