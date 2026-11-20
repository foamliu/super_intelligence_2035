# Deepread: dfv2z — RON mismatch from .md0 MC files

**SID**: 1793174136126_dfv2z · **User**: clarawu · **Host**: hfeg0pkn003 (10.129.2.12) · **mc**: 39 · **Domain**: analog_context
**Keywords**: schematic:58;netlist:58;hspice:58;pyaether:40;aether:40;spectre:24
**Session**: 107 msgs, 210KB

## User intent (trace-faithful)
USER#0: 「从 @.../Ron_linMC#4.md0 中得到 RON_PU_mismatch，其定义为 6 倍 rpu_50 的标准差 std 除以 230，用百分数表示；还有 RON_PD_mismatch，其定义为 6 倍 rpd_50 的标准差 std 除以 230，用百分数表示」

Refinements:
- USER#16: 只有 500 个样本，最后四行 avg/std/min/max 是汇总行
- USER#24: 直接用最后四行里系统自己得到的 std 计算即可
- USER#26: 扩展到 5 个 .md0 文件 (Ron_linMC.md0 ~ Ron_linMC#4.md0)
- USER#46: 输出表格需要 CSV 格式
- USER#54: 去掉 Samples/std_rpu_50/std_rpd_50 列，mismatch 列直接用百分号表示
- USER#62: 列标题去掉 %，输出文件名 RON_mismatch.csv
- USER#86: terminal 只输出一行 "CSV written to: <path>"

## .md0 file format
Columns: `mc_index rpu_50 rpd_50 rpu_lin50 rpd_lin50 temper alter#`
- 500 data rows: mc_index = 1..500, rpu_50/rpd_50 ≈ 230 ± std
- 4 summary rows: avg / std / min / max (first col = label string, not number)
- std row: `std <std_rpu_50> <std_rpd_50> <std_rpu_lin50> <std_rpd_lin50> ...`

## Gold standard (from session MSG#31, MSG#69)
| File | std(rpu_50) | std(rpd_50) | RON_PU_mismatch | RON_PD_mismatch |
|------|-------------|-------------|-----------------|-----------------|
| Ron_linMC.md0   | 1.2491 | 2.3944 | 3.2585% | 6.2463% |
| Ron_linMC#1.md0 | 1.1345 | 2.0346 | 2.9596% | 5.3077% |
| Ron_linMC#2.md0 | 1.1841 | 2.1088 | 3.0890% | 5.5012% |
| Ron_linMC#3.md0 | 1.5040 | 2.5453 | 3.9235% | 6.6399% |
| Ron_linMC#4.md0 | 1.2397 | 2.1902 | 3.2340% | 5.7136% |

Formula: RON_PU_mismatch = 6 × std(rpu_50) / 230 × 100 (%)
         RON_PD_mismatch = 6 × std(rpd_50) / 230 × 100 (%)

## Final deliverable spec
- Python script: reads all .md0 files in sim_MC/ dir
- Extracts std from the "std" summary row (NOT computing std manually)
- Computes RON_PU_mismatch and RON_PD_mismatch
- Outputs `RON_mismatch.csv` with columns: `File,RON_PU_mismatch,RON_PD_mismatch`
- Values formatted with % sign (e.g., `3.2585%`)
- Terminal only prints: `CSV written to: <csv_path>`

## Synthesis plan
- **A (visible)**: 5 .md0 files with the real statistics above → assets/
- **B (hidden)**: 3 .md0 files with different statistics (different std values, different file names) → hidden/
- **SUT**: `ron_mismatch_md0.py` — pure stdlib, reads .md0, extracts std row, computes mismatch, writes CSV
- **check.py**: verify CSV format (columns, % values, file count, value correctness with tolerance), run on B
- **negatives**: empty_shell, print_only, hardcode_A (will fail on B's different values)
- Domain: analog_context (MC data analysis)
- L1 (pure stdlib parsing, no real tool)
