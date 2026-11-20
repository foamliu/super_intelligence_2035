# trace_deepread: r6bcb — SimIncludeMissDiag-001 (digital, B-synthesized)

## 元数据
- session_id: `1792052209542_r6bcb.messages.json`
- user/host: tongfanl@hfeg0plg72 (10.129.2.13)
- mc: 60 (verilog:560;netlist:4;synopsys:2 — pure digital/sim, no drc/lvs contamination)
- size: 29 msgs / 869KB / mtime 2026-10-29 15:39
- shard: A (digital)
- status: claimed r373 → case `EDA-Eval-DesignFlow-SimIncludeMissDiag-001`

## 任务真实意图
DDR6 仿真激励生成 (gen_stimulus_ltf) 编译失败诊断：
- 用户跑 `./runsti/gen_stimulus_ltf`（vsim/xrun wrapper，3 个 job：WTM001/WTM004/WTM005）
- WTM004 因 `xmvlog *E,COFILX (dft_tasks.sv,1363|74): cannot open include file '/proj/dscqa/V0/sim/verilog/ddr6_tb/dscqa/Project/dft_table.v'` 编译中止
- agent 诊断：SOS-managed Project/ 目录缺 dft_table.v（仅有 dft_table_0630.v），local vecgen_local/Project/dft_table.v symlink 可解析
- agent 写 `/home/tongfanl/dft_diag.py` 诊断脚本（resolve symlinks + check include existence + grep xrun.log）

## A-档合规性
- USER#0 = 贴出失败命令 + 编译输出（`[COMMAND] vsim ...` + `cp: cannot stat` + COFILX error），**未给根因/修复方向** → A-faithful 合格 ✓
- USER#4 = "continue"（仅催促，无新信息）
- agent 全程 read_files/list_allowed_files/search_codebase/run_approved_command/editor → 写 dft_diag.py → run_approved_command 跑诊断

## A 不可行原因
1. trace 交付件 dft_diag.py 是一次性环境诊断（依赖真实 SOS/symlink 状态 + 绝对路径），不可移植
2. 29 msgs session 的 agent 诊断路径过短（仅 1 个 editor 写脚本，diagnosis 依赖环境上下文而非通用 spec）
3. 故 B 档 synthesized：抽同构逻辑做通用 Python 诊断器 diag_include_miss.py（parse COFILX + list Project + find alternatives + JSON report）

## case 合成 (B-synthesized)
- deliverable = `diag_include_miss.py <sim_run_dir> <report_path>`（通用，不依赖真实路径）
- A (visible) = sim_run_A/：xrun_A.log（dft_table.v 缺失，COFILX 两行格式）+ Project/dft_tasks.sv + Project/dft_table_0630.v
- hidden B = sim_run_B/：xrun_B.log（model.v 缺失，top.sv:421）+ Project/top.sv + Project/model_1105.v
- A≠B（不同缺失文件、不同源文件/行号、不同替代文件）
- reference = diag_include_miss_ref.py（COFILX 单行+两行解析 + stem-matching alternatives + 结构化 JSON）
- check.py = 13 conds (a-m)：zip/py_compile/exit0/JSON keys/missing path/source+line/project files/alternatives/summary counts/cross-input guard(A)/anti-hardcode(B token in, A token out)/3-run md5/非平凡

## 自验
- gold PASS 13/13 ✓
- 5 negatives ALL FAIL ✓ (NEG_RC=0)：fake_empty→[a]/fake_print_a→[e,k]/fake_core_deleted→[e]/naive_grep_only→[e,f]/naive_no_alternatives→[h,i]
- §4.9 三假 (fake_empty/fake_print_a/fake_core_deleted) 全 FAIL ✓
- test_sha8 = 8cbb7020 (disk check.py == jsonl test field) ✓
- 断言闸门 k_rationale=k_check=13≥8 ✓
- A.jsonl 208→209；ledger mark r6bcb→case
