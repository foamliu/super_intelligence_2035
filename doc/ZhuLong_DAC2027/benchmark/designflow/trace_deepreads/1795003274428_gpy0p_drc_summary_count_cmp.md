# trace_deepreads/1795003274428_gpy0p_drc_summary_count_cmp.md

**session**: 1795003274428_gpy0p
**user/host**: liwan @ hfeg0plg82 (also visible on hfeg0pkn003 / 10.129.2.12)
**match_count**: 312 (drc:1047;calibre:164;pyaether:31;aether:20;netlist:7;virtuoso:6;cmos:4;hspice:3;cadence:3;binary:3;.gds:2;waveview:1;spectre:1;schematic:1;lvs:1;analog:1)
**domain**: physical_verify (DRC summary comparison)
**scan snapshot**: ssh_eda_search_20261121_151844/summary.tsv
**file path (remote)**: /home/liwan/.cline/data/sessions/1795003274428_gpy0p/1795003274428_gpy0p.messages.json (849877 bytes, 191 msgs, 91 assistant / 100 user)
**typed user_inputs**: 5 (其余 user msg 都是 tool_result)

## 真实用户意图（按 msg 序）

- **U#0 (msg 0)**: "我想实现一个自动化功能，目标是完成两个drc结果的数目对比，要逐条数目多少的对比"
  → 要做一个自动化工具对比两个 DRC summary 的逐条规则 violation 数目。
- **U#70 (msg 70)**: 给出两个 summary 路径
  - 文件1: /proj/drcpa/V0/ver/drc/drcpa_top/PERI0_wl1118 (后来用户纠正为新版)
  - 文件2: /proj/drcpa/V0/ver/drc/drcpa_top/PERI0_wl1117 (旧版)
- **U#183 (msg 183)**: "这个结论有问题，1118为新版，1117为旧版"
  → assistant 把 file1=1118(new)、file2=1117(old) 传入，diff=file2-file1=old-new，新版 violation 比旧版多却被判"改善"，方向反了。用户纠正方向。
- **U#189-190 (msg 189/190)**: "恶化以及改善的条目需要全部输出不要只取TOP5"
  → assistant 的 report 只输出 worsened_top5/improved_top5 ([:5])，用户要全部。

## assistant 的工具链

1. list_allowed_files → 找到 PERI0.drc.summary + _cluster.master_
2. read_files PERI0.drc.summary → 识别 Calibre DRC-H RULECHECK 格式
3. editor 修改 /home/liwan/Desktop/compare_drc.py 加 RULECHECK 解析
4. run_approved_command python-runner 跑 compare_drc.py
5. 反复迭代修 bug：BY CELL 段头正则、direction、top-5

## DRC summary 文件格式（Calibre DRC-H）

```
=== CALIBRE::DRC-H SUMMARY REPORT
Execution Date/Time: ...
----------------------------------------------------------------------------------
--- RUNTIME WARNINGS
---
[warnings]
----------------------------------------------------------------------------------
LAYER <name> .... TOTAL Original Geometry Count = N (M)      # layer counts, NOT rules
----------------------------------------------------------------------------------
--- RULECHECK RESULTS STATISTICS                              # 全局规则段 (要解析)
---
RULECHECK R_C_NW_L_02_L ....... TOTAL Result Count = 0      (0)
RULECHECK R_P_AT4DMY_F_01_H ....... TOTAL Result Count = 49230  (82172)
... 143 rules ...
----------------------------------------------------------------------------------
--- RULECHECK RESULTS STATISTICS (BY CELL)                    # 按 cell 拆分段 (要跳过)
---
CELL ntn_cdns_subMaster_944 ...................... TOTAL Result Count = 2 (10)
    RULECHECK R_P_AT4DMY_F_01_H .................. TOTAL Result Count = 2 (10)   # 缩进 RULECHECK 行
...
```

## 3 个 bug（assistant 在 trace 里修过的，本 case 抽取为 fix-the-bug fixture）

### Bug A — 方向（file order / diff sign）
- buggy: 位置参数 `file1 file2`，`diff = file2 - file1`，无 old/new 约定。
  用户传 file1=new(1118)、file2=old(1117) → diff=old-new<0 → "改善"，但实际 new>old 是"恶化"。
- gold fix: `--old FILE --new FILE` 显式 flag；`diff = new - old`；worsened=diff>0，improved=diff<0。
- 用户原话 U#183: "1118为新版，1117为旧版"。

### Bug B — BY CELL 段重复解析
- buggy: `SECTION_PATTERN = r'---\s*RULECHECK\s+RESULTS\s+STATISTICS'` 同时匹配 general 段头和 (BY CELL) 段头（因为 BY CELL 段头含子串 "RULECHECK RESULTS STATISTICS"）。
  → in_section 一直 True，BY CELL 段内缩进的 `RULECHECK` 行被 RULE_PATTERN 匹配并覆盖全局计数（同名规则 dict 赋值覆盖）。
- gold fix: 先检测 `BY_CELL_PATTERN = r'---\s*RULECHECK\s+RESULTS\s+STATISTICS\s*\(BY\s+CELL\)'`，命中则 in_section=False，跳过整段。
- assistant 在 trace msg 174-176 发现此 bug："大量重复规则警告"。

### Bug C — Top-5 截断
- buggy: report 只输出 `worsened_top5 = sorted(...)[:5]` 和 `improved_top5 = sorted(...)[:5]`。
- gold fix: 去掉 `[:5]`，输出完整 `worsened` / `improved` 列表。
- 用户原话 U#189-190: "恶化以及改善的条目需要全部输出不要只取TOP5"。

## case 抽取决策

- **A 档不可行**: live workspace READ-ONLY + 远程 host 文件 e0031982 无读权限（Permission denied on /rundata/drcpa/...）。
- **B 档 reframe ACCEPT**: fix-the-bug fixture。把 trace 的 3 个 bug 抽成 self-contained buggy compare_drc.py + spec + 样本 summary（含 BY CELL 段触发 bug B）→ 交付修好的 compare_drc.py + report.json。SUT 无需运行 Calibre，只需让产出的脚本在 B 上正确解析 + 输出完整对比报告。
- **反硬编码**: B 用 R_B_ 前缀规则名（A 用 R_A_），B 规则数 17（A 9），B 总数 1031/988（A 415/465），全不同。

## check.py 16 teeth (a-p)

a submit.zip 有效含 compare_drc.py+report.json
b compare_drc.py 非空
c py_compile + ast.parse
d env_B_extracted 含 sample_old_B.summary / sample_new_B.summary / hidden_manifest.json
e report.json 非空 (>10 bytes) 且可 parse
f report 顶层是 dict
g report 含 old_total/new_total/worsened/improved/unchanged/new_only/fixed_only/old_label/new_label，不含 worsened_top5/improved_top5/total_file1/total_file2
h 反硬编码：report 规则集 == B 真值 17 条且全 R_B_ 前缀
i 核心修复 A：R_B_AT4DMY_S_07_H (old=200,new=250,diff=+50) 在 worsened 且 diff>0
j 核心修复 A：R_B_V3_F_01_H (old=300,new=200,diff=-100) 在 improved 且 diff<0
k 核心修复 B：worsened+improved+unchanged+new_only+fixed_only 总数 == 17 (无 BY CELL 重复)
l 核心修复 C：worsened 共 7 条 (不截断 Top 5)
m 核心修复 C：improved 共 6 条 (不截断 Top 5)
n 反硬编码：old_total==1031, new_total==988 (不硬编码 A 的 415/465)
o 3-seed 字节一致
p 源码反硬编码：无 [:5]/top5/head(5)，无 file1/file2，含 --old/--new，含 BY_CELL_PATTERN

## 自验

- ref solve.py (string-replace 3 处) → fixed compare_drc.py PASS 16/16 teeth on B
- 4 negatives (only_print/hardcode_A/empty_report/buggy_unfixed) 全 FAIL distinct
- §4.9 三假 (a)空壳→e / (b)只print→h / (c)删核心→i 全 FAIL distinct teeth
- roundtrip sha256 disk==jsonl==metadata = 0ad2b7df20cef322483099fb4f09bad2b3fd56e2a3ae135dba6300200b7f4ad8
- k_rationale=k_check=16 ✓ (≥8)

## 落库

- append EDA-Eval-DesignFlow_C.jsonl 568→569
- trace_ledger.py --shard C claim+mark 1795003274428_gpy0p → case (EDA-Eval-DesignFlow-DrcSummaryCountCmp-001)
- stats: case 581→582, physical_verify 282→283
