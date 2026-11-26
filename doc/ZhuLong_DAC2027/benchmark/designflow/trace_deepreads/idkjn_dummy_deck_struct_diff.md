# Deepread: idkjn — dummy deck 0.2.9 vs 0.3.3 structural diff (xinqiaoz@10.129.2.11)

- **session**: 1793871277459_idkjn.messages.json (mc=86, 52 msgs, 3 real user turns, 374KB)
- **host/user**: 10.129.2.11 / xinqiaoz
- **domain**: physical_verify (drc:337, pdk:327, calibre:34)
- **tools used**: editor×50, run_approved_command×26, read_files×16, list_allowed_files×11, ask_question×3

## User turns (verbatim intent)

### U#0 (msg0, len=978) — 本 case reframe 目标
dummy deck 两个版本的【结构骨架层】差异对比 (0.2.9 vs 0.3.3)，只做文件结构层面不读代码。5 项产出：
1. 顶层目录树对比 (新增/独有/共有标注)
2. init.tcl 加载顺序对比 (scriptDirList 是否不同)
3. 文件清单 diff (仅0.2.9 / 仅0.3.3 / 疑似改名配对，各给文件数)
4. 文件总数对比
5. 各子目录文件数对比表 (子目录|0.2.9数|0.3.3数|差值)

路径：0.2.9=/apps/imctf/develop/dummy/script/data/Vx/0.2.9/，0.3.3=/apps/imctf/develop/dummy/script/data/0.3.3/。
0.3.3 子目录：common / output / defineBLK / drc / genDummy / typeFlow (共 159 个 tcl)。

### U#1 (msg26, len=1603) — 接口层 (不在本 case 范围)
继续做【接口层】差异：zipInfo.tcl 全文对比、KEY_* 默认值清单、TYPE_* 流程文件清单、核心 proc 签名、common/ 内容 diff 概览。

### U#2 (msg47, len=131)
stable→local 路径映射 (DRC/common)。

## Reframe 决策

- **选 U#0**：单意图、5 项结构化可验证产出，适合 mock-behavioral data-analysis reframe (承 r725-r728 family)。
- **reframe = `dummy-deck-struct-diff`**：真实 find/sort/comm 在 PDK 仓库 (path-dependent on /apps/imctf/develop/dummy/) → 纯 stdlib：给定两个 file_index + 两个 init.tcl → 结构化 JSON 报告 (subdir_comparison / init_load_order / file_diff / total_counts / per_subdir_counts)。
- **distinct vs r726 FractureTableSchemaReport=schema / r725 PdkQaSyncWorkflowAnalyze=workflow**：本例 = 跨版本文件树结构 diff (new/removed/renamed 三分类)。
- **11-15 令§二 analysis-Q&A 合法** ✓

## Case 产出

- **case_id**: EDA-Eval-DesignFlow-DummyDeckStructDiff-001 (physical_verify L1, mock-behavioral struct-diff)
- **k=15 (a-o)**, ref PASS, 3 negatives FAIL distinct (empty→b / print→c / core→n), NEG_RC=0, determinism 3x identical
- **asset A** (visible): file_index_v029/v033 (103/159 files, 5/6 subdirs) + init_v029/v033 + prompt(U#0逐字) + task_brief
- **hidden B**: file_index_v029/v033_B (109+3renamed/178+3renamed, 6/7 subdirs incl verify/compat) + init_B + B2 (minimal 35/52, 3/3 subdirs) for cross-input guard
- **check.py**: reference-compute (ref solve 跑 B 得 expected, candidate 跑 B 比较 12 字段 + B2 cross-input guard)
