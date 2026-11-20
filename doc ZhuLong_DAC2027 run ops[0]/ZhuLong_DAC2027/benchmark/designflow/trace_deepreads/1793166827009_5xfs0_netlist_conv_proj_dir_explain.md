# Deepread: 1793166827009_5xfs0 — netlist_conv_proj_dir_explain

## Trace metadata
- **session_file**: `1793166827009_5xfs0.messages.json` (directory: `1793166827009_5xfs0/`)
- **user / host / ip**: e0039602 / hfeg0plg95 / 10.129.2.11
- **match_count**: 23 (kw profile: netlist:286, drc:144, verilog:39, synopsys:11, waveview:5, lvs:4, schematic:3, rtl:3)
- **messages**: 21 (2 用户轮, 19 assistant/tool)
- **date**: 2026-10-28
- **ledger history**: parked 2026-11-14 09:15 ("directory content explanation Q&A") → revived r936 per 2026-11-15 reaudit §II

## User intent (verbatim, A-faithful)
**U#0 (msg 0)**: 「请通读这个目录下的内容，给我解释一下这里在介绍什么」

A档合规判定: ✅ 提出需求（解释目录内容）✅ 未给根因/修复 ✗ → 合规。

## Assistant tool chain (real)
1. `list_allowed_files` /home/e0039602 depth=3 → home 目录全树（Desktop/Documents/fm_run/zhuguancheng/outputs/ 等）
2. `read_files` Documents/netlist_change_v0.3/README.md + build_cell_files.py + gen_cells.py + extract_converted_sv.py
3. `list_allowed_files` fm_run/ + zhuguancheng/ → Formality 验证工作区 + 主管脚本
4. `read_files` fm_run/run_do_all.tcl + run_do_one.tcl + submit.sh + result_map_*.txt
5. `list_allowed_files` outputs/ + inst_rename_results/ + Documents/ + cross_probe_l2s_query_results/
6. `read_files` fm_run/fm_795854.out + verify_one.txt + humanworks.sv + FM_INFO/phases + outputs/_t_report.txt
7. `list_allowed_files` Documents/ depth=1 → netlist_change / verilog_lib_trans_v* / finesim-fsdb-reader / waveview-fsdb-reader 等
8. `read_files` fm_run/run_do.tcl + Documents/netlist_change_v0.31copy/config.yaml

## Assistant final answer (GOLD, msg 20)
结构化解读：
- **一、核心主线**: 网表 cell 自动转换（Documents/netlist_change_v* / verilog_lib_trans_v*）
  - 背景: schematic netlist 用了 simlib 里没有的自定义 cell（invGS/invDSx1/bufIOLVx16_Cdq_pc60/latqYx1 等）
  - 目标: 自动替换成 simlib_base.sv 已有物理单元（inv_base/inven_base/invhiz_base…），处理电源衬底脚/互补使能/trireg/死结点
  - 手段: 调 LLM（deepseek-v4-flash/glm-5.0，走内部网关 10.129.8.86:8899）一次性推理全部映射，多进程并行，输出 result_map 报告
  - 工程特点: 自包含可用 + 确定性解析器+大模型兜底 + few-shot 参考库 + prompt 监视器 + 白名单 + 429 退避
- **二、主线延伸**: Formality 等价性验证（fm_run/）
  - 输入: simlib_drcoa_stdcells.sv (golden) vs simlib_drcoa_stdcells_converted.sv (impl) + simlib_base.sv + blackbox_stub.v
  - 辅助: build_cell_files.py / gen_cells.py / extract_converted_sv.py
  - 验证: TCL 脚本 (run_do_all.tcl 等) 通过 submit.sh 提交 LSF 跑 fm_shell
  - 状态: 调试中（verify_one.txt: bufGSx48_Mrr FAILED，CMD-005/FM-236 报错）

## Domain confirmation
- kw profile netlist:286 dominant → D 域 schematic_netlist ✓
- 原 ledger domain=waveform 误标 → r936 mark --force 纠正为 schematic_netlist

## Reframe (manual-grounded howto Q&A → produce reframe)
- **A 资产**: verilog_lib_trans_v2.3.4/README.md 真实内容（CLEANPROJECT 网表转换工程说明文档，3329B）
- **A 档 seed**: U#0 verbatim「请通读这个目录下的内容，给我解释一下这里在介绍什么」
- **deliverable reframe**: produce 一个通用 project-README 解析器（markdown 结构解析 → 8 键 JSON + report.txt）
- **B 隐藏平行场景**: DRCDECKGEN（DRC rule deck 自动生成工程 README，结构同构但 token 完全不相交：calibre/svrf/layer vs simlib/netlist/cell）
- **candidate**: project_readme_parser.py（通用 markdown 解析器，regex/section based，无硬编码）
- **check.py**: 12 断言 a-l（zip/py_compile/8keys×2/DRCDECKGEN/DRC-kw/dir_struct/run_drc/deck_map/report/anti-hardcode/3-seed）
- **negatives**: empty(4/12) / print_only(6/12, k fail) / core_deleted(6/12, j fail) — 全 FAIL ✓

## Self-verify
- reference: 12/12 PASS ✓
- 3 negatives: ALL FAIL ✓
- §4.9 (a)(b)(c) 三退化提交: 全 FAIL ✓
- check_sha256: 8c72be18f16113cf01ede1b792c354591b1f5bb3e7aafa9a4a7c7cb476b9f301 == disk ✓
- cross-shard dup: 0/5 ✓
- D.jsonl: 505 → 506
