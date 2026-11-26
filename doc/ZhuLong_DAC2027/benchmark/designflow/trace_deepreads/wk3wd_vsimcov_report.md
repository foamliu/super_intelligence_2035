# Deep-read: 1793078652491_wk3wd — vsim 回归报告汇总脚本优化

- session: `1793078652491_wk3wd`
- user/host: cliu @ hfeg0pkn004 (IP 10.129.2.13)
- match_count: 197 (D-domain keywords: netlist×13, hspice×7, schematic×2)
- msgs: 178 / user turns: 6
- ledger: trace_ledger_D.tsv, domain=schematic_netlist, status=case, case-id=EDA-Eval-DesignFlow-VsimCovReport-001

## 真实任务（逐字摘要）
用户要求优化一个已有的 Perl 回归报告汇总脚本 `vsim_report_summary`（807 行），新增两个功能：
1. **每个 pattern 的运行次数**（per-pattern total count）—— 统计 `regression_run/` 下有多少子目录对应每个 pattern；
2. **未被纳入回归的 pattern 报告**（missing patterns）—— 以外部全集文件 `pattern.list` 为参考，列出在 `pattern.list` 里但没有任何回归子目录匹配到的 pattern。

## 真实资产（host 10.129.2.13 可读）
- `/home/cliu/drcoa/1022/pattern.list` —— pattern 全集，170 行（含 pattern 名、注释、可能的重复）。
- `/home/cliu/drcoa/1022/vsim_report_summary` —— Perl 脚本，807 行，含关键 sub：
  - `load_pattern_list` —— 解析 pattern.list（去注释/空行/去重、保留首次顺序）
  - `collect_patterns_from_dirnames` —— 遍历 regression_run 子目录
  - `longest_prefix_pattern` —— **最长前缀匹配** dirname→pattern（核心防误配逻辑：避免 `basic_allbank_bc8` 因子串包含而误配 `basic_allbank_bc8_otf`）
  - `report_pattern_coverage` —— 汇总输出
- `/home/cliu/drcoa/1022/regression_report/` —— **空目录**（无真实 A_Summary.rpt 样本）。

## 为何采 B-grade synthesized
真实回归结果树 `regression_report/` 为空，无真实 `A_Summary.rpt` 样本可供忠实复刻 gold product；但脚本逻辑与 pattern.list 完整可读。故 B-grade synthesized：合成 A/B 两套 `pattern.list + regression_run/` 子目录树（各含已知期望值的碰撞对与 missing 集），离线验证候选 Python 脚本 `vsim_cov_report.py` 是否正确复刻核心算法（去重 / 最长前缀匹配 / missing / bytemode 汇总）。

## 合成资产设计（A/B 结构性不同，每维度反硬编码）
### A（可见）
- pattern.list_A：15 行 = 14 unique pattern + 1 注释 + 1 空行 + 1 重复（avl_catm）
- 14 patterns：avl_ca_odt / avl_catm / basic_allbank_bc8 / basic_allbank_bc8_otf / basic_allbank_bl16 / basic_allbank_rdcrc / basic_dm / cmd_cancel / ecc_entry / mrr_read / powerdown_entry / refresh_otf / sre_freq / write_leveling
- bytemodes：x4_2000 / x8_4000 / x8_8000 / x16_16000 / x8（ecc_entry=1 变体）
- 19 个 regression 子目录（移除 rdcrc + sre_freq 的子目录 → 它们 missing）
- 碰撞对：basic_allbank_bc8 (total=2) vs basic_allbank_bc8_otf (total=2)
- missing = {basic_allbank_rdcrc, sre_freq}
- bytemode x8_8000 total=400
- 含 orphan/debug 子目录（unknown_orphan / random_debug，不匹配任何 pattern）

### B（隐藏）
- pattern.list_B：19 行 = 18 unique pattern + 1 注释 + 1 重复（hpc_read）
- 18 patterns：dca_train / dca_train_long / hpc_read / hpc_write / loopback_test / mbist_full / mpc_cmd / pda_calib / ppr_full / sppr_single / tm_compress / tm_fuse / tm_topo / vref_train / write_preamble / xtalk_basic / xtalk_basic_long / zen_mode
- bytemodes：x4_1500 / x8_3000 / x16_12000 / x4（extra= 变体）
- 24 个 regression 子目录
- 碰撞对：dca_train (total=3) vs dca_train_long (total=1)；xtalk_basic (total=2) vs xtalk_basic_long (total=1)
  - `dca_train_extra=2.x4` 与 `xtalk_basic_extra=1.x4` 经最长前缀匹配分别归入 dca_train / xtalk_basic（子串法会误判）
- missing = {sppr_single, zen_mode}
- bytemode x4_1500 total=720（9 子目录 ×80）；x8_3000 total=1440 fail=6（9 子目录 ×160）
- 含 orphan/debug 子目录（orphan_sim / debug_only）

## 候选接口
```
python3 vsim_cov_report.py --pattern-list <pattern.list> --regression-run <regression_dir> --out <coverage_report.txt>
```
输出严格文本格式：`Total_Pattern_List` / `Total_Regression_Subdirs` 头 + `[BytemodeTotals]` / `[PatternTotals]` / `[MissingPatterns]` 三段。

## check.py — 12 条独立断言 a-l（k_rationale=k_check=12）
a. submit.zip 合法且含 vsim_cov_report.py
b. 脚本以 CLI 在隐藏 B 上退出码 0 且产出非空 coverage_report.txt
c. 报告含三段且可解析
d. Total_Pattern_List==18（去重/注释/空行处理）
e. Total_Regression_Subdirs==24
f. dca_train total==3（碰撞对，反硬编码）
g. dca_train_long total==1（反子串匹配）
h. xtalk_basic total==2（碰撞对）
i. xtalk_basic_long total==1（反子串匹配）
j. MissingPatterns 精确 == {sppr_single, zen_mode}（集合+顺序）
k. bytemode x4_1500==720 且 x8_3000==1440
l. 3-seed 确定性 + 无 A 特有 pattern 名泄露

## 自验
- reference vsim_cov_report.py（Python 移植 gold 逻辑）→ check PASS 12/12（A 与 B 两端均验）
- §4.9 三假：empty-submit → [a] FAIL；fake_print_only → [b..l] FAIL；fake_core_deleted → [f..j] FAIL
- 3 硬编码 neg：neg_substring_match → [f,h] FAIL（碰撞对合并）；neg_always_complete → [j] FAIL（漏报 missing）；neg_hardcode_A → [d,f,g,h,i,j,l] FAIL（A 模式泄露 + wrong missing）
- negative_selftest：全部 FAIL ✓
- 3-seed 确定性 PASS（check 条件 l 内嵌）
- byte-sync：check.py sha e78d3ea5 size 12105，jsonl test 字段一致
- 泄露隔离：check.py / vsim_cov_report.py 不引用 `benchmarks/EDA-Eval-DesignFlow/` 路径

## 流水
D.jsonl 229 → 230。ledger wk3wd mark case。WAITING: 0。
