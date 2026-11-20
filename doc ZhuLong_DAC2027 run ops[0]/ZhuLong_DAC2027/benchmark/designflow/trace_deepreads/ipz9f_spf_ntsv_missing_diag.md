# ipz9f 深读笔记 — SPF nTSV coupling 缺失诊断

## trace source
- session: `1793589961728_ipz9f`
- user: jianilu
- host: hfeg0pkn004
- size: 2.7MB, 224 msgs
- date: 2026-11-03 14:10 (mtime), ts=1793589961728 (2026-11-04 22:46 UTC / 11-05 06:46 BJT)
- spice keyword matches: 7136 (grep -oiE)
- domain: characterization (SPF parasitic extraction analysis)

## A-faithful 选轮
- U#0 (MSG#0) 逐字：「在/rundata/drvqa/V0/ver/pex/willl/V2B_CBCC_1029/路径下，使用脚本spf_bl_extract.py，提取spf文件CXSA_1x16x3.spf_RCC_addnTSV中各layer的coupling，使用命令如下，python spf_bl_extract.py CXSA_1x16x3.spf_RCC_addnTSV --range 16-31 --output CMOSaddnTSV_result.csv，输出的CMOSaddnTSV_result.csv文件中没有统计到$lvl=86，即nTSV层的coupling，帮我查找原因，提出修改方案」
- 用户报告症状（$lvl=86 nTSV 缺失），要求找原因 + 修改方案 → 提出需求轮 ✓
- 用户未给出根因或修复方案 → A-faithful 合格 ✓

## 金标准（assistant 调查过程 + 结论）

### 调查路径
1. read_files spf_bl_extract.py + CMOSaddnTSV_result.csv
2. head SPF file CXSA_1x16x3.spf_RCC_addnTSV
3. grep '86' in SPF → line 113: `*86 nTSV    ITF=nTSV` (layer map entry)
4. read update_RCC_layer_V2.pl → line 100: `$add_line1 = "C_$1_$C_number1 $curVal $nextVal c_ntsv \$lvl=86";`
5. grep SPF for $lvl=86 → line 2535: `C17_66 BLb<10> BLb<20> 29e-18 $lvl=86`
6. 分析 parse_cap_line 逻辑

### 根因（msg 31-49 反复确认）
- `parse_cap_line()` (lines 73-76) 严格要求 BOTH `$lvl1=` 和 `$lvl2=`：
  ```python
  l1 = re.search(r'\$lvl1=(\d+)', attr)
  l2 = re.search(r'\$lvl2=(\d+)', attr)
  if not l1 or not l2:
      return None  # ← BUG: nTSV lines dropped here
  ```
- 正常 StarRC coupling：`C17_1 BLb<10>:32 XI...DRN 6.62383e-21 $lvl1=30 $lvl2=37` → 有 $lvl1/$lvl2 → parsed ✓
- nTSV coupling：`C6_28 BLa<2> BLb<6> 100e-18 $lvl=86` → 只有单 $lvl=86 → $lvl1/$lvl2 都 None → return None → 静默丢弃
- update_RCC_layer_V2.pl 用单 `$lvl=86` 格式（非标准双 $lvl1/$lvl2），~200 行全丢

### 修复（msg 59-67）
- 在 parse_cap_line 中加 fallback：当 $lvl1/$lvl2 都缺失时，检查单 `$lvl=N`，把 N 赋给 l1 和 l2
  ```python
  if not l1 or not l2:
      ls = re.search(r'\$lvl=(\d+)', attr)
      if not ls:
          return None
      return n1..., n2..., val, ls.group(1), ls.group(1)
  ```
- 创建 spf_bl_extract_fixed.py

### 验证（msg 79-83）
- 原脚本 BLa<16> total = 0.1115（无 nTSV-nTSV 列）
- 修复后 BLa<16> total = 0.6111（5.5×），出现 `@nTSV-nTSV` 列（0.2, 0.1, 0.058, 0.0208）
- ground cap 行（n2='0'）仍被 `if n2 in ('0','GND','VSS'): return None` 过滤 ✓

## 后续话题（msg 88+）
- trace 后续转向仿真文件计数（.bisec_mt0 / .fsdb.chain / gensim_new.py），与首任务无关
- 金标准取首任务（msg 0-85）的完整闭环

## 合成
- case: EDA-Eval-DesignFlow-SpfNtsvMissingDiag-001
- A: prompt.txt(用户原话) + task_brief.md + spf_bl_extract.py(buggy) + CXSA_A.spf
- hidden B: spf_B.spf (mTSV layer 42, 不同 BL 数 6×2, 不同 normal layers 14-21)
- reference: spf_bl_extract_ref.py (含 $lvl= fallback)
- check.py: 14 断言 (a-n)
- negatives: empty_shell / print_expected_b / core_deleted(buggy) / naive_hardcode_a(硬编码 86)
