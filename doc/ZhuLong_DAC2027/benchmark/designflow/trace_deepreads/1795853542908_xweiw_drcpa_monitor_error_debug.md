# Deepread: 1795853542908_xweiw — DDR5 Verilog sim monitor-error analysis script debug

- **session**: `1795853542908_xweiw.messages.json` (163 msgs)
- **trace_source**: user `jkxu` @ hfhds206 (10.129.32.80) [shared home: also hfhds206/hfeg0pkn005/hfeg0pfn087]
- **match_count**: 143 (keywords drc:2679 + verilog:2648 — **drc=false-pos from `drcpa` toolname, NOT PV-DRC**; verilog=DDR5 testbench sim context)
- **domain**: verification (digital) — DDR5 Verilog simulation regression monitor-error analysis
- **found**: r1569 fullscan 164430 (vs 160229 baseline, fresh in 15:14→16:46 window)
- **claimed**: r1569 (ledger A, session 1795853542908_xweiw)
- **status**: DEEPREAD DONE → case DEBT next round (r1570)

## User intent (7 user turns)
1. **msg[0]**: 在 `/rundata/drcpa/V0/simdir/verilog/jkxu/verilog.ddr5.drcpa.newcp.local` 执行 `python3.7 /proj/drcpa/V0/sim/verilog/ddr5_tb/proj_script/analyze_monitor_errors.py random.1127` 报错。
2. **msg[45]**: 给我修正版路径。
3. **msg[55]**: `/rundata/drcpa/V0/simdir/verilog/jkxu/verilog.ddr5.drcpa.post_2nd_rev/RAN_ALL` 这种里面是 link 文件夹的它可以扫描吗？
4. **msg[77]**: `/proj/drcpa/V0/sim/verilog/ddr5_tb/proj_script/vsim_report_new` 这个脚本也是同样的问题。
5. **msg[95]**: 对 RAN_ALL 目录使用后的结果如下…（指出 3 个日期 random.1118/1125/1126 被合并到同一 Group）。
6. **msg[111]**: `/home/jkxu/agent_generated_scripts/run_analyze_fixed.sh` 这个能打印 error 矩阵吗？
7. **msg[157]**: 回退修改，然后统计的格式是什么，有那些信息。

## 3 bugs + 1 feature found

### Bug 1 (core, cleanest to test): `ValueError: max() arg is an empty sequence`
- **location**: `write_report()` line 145: `cw = max(len(t) for t in all_error_types) + 2`
- **trigger**: `random.1127/` 下 15 个 sim 目录的 `Internal_Monitor.rpt` **全是空报告**（只有一行 `============================[Internal Monitor Report Done]=====` header，无 `@timestamp [TAG] message` 错误记录）→ `all_error_types = []` → `max()` 收空序列崩溃。
- **traceback** (msg[43] tool_result):
  ```
  File ".../analyze_monitor_errors.py", line 284, in <module> → main()
  File "...", line 267, in main → write_report(sim_errors, all_types, rpt_path, top_dir)
  File "...", line 145, in write_report → cw = max(len(t) for t in all_error_types) + 2
  ValueError: max() arg is an empty sequence
  ```
- **fix**: `if len(sim_names) <= 300:` → `if all_error_types and len(sim_names) <= 300:` (msg[44]/[54])
- **stdout before crash** (msg[43]): `Sims found: 15 / With errors: 0 / Clean: 15 / Error types: 0 / Time: 0.2s / Error count distribution: 0 error type(s): 15 sim(s)`

### Bug 2: `find` 不 follow symlink → RAN_ALL 扫到 0 sim
- **location**: line 28 `subprocess.run(['find', top_dir, '-maxdepth', '5', '-name', 'Internal_Monitor.rpt', '-type', 'f'], ...)`
- **trigger**: `RAN_ALL/` 下是 symlink (`random.1118 -> ../random.1118` 等 3 个)，`find` 无 `-L` 不穿透 → 0 rpt。
- **fix**: `find -L ...` (msg[70]/[76])。修后 RAN_ALL 扫到 2712 sim / 1929 有错 / 5 错误类型 / 77.4s。

### Bug 3: path 解析忽略 run-id → 3 日期合并
- **location**: `vsim_report_new` (Perl) `sumsimstatus` + `check_incomplete_sims` 路径解析只取 `path_parts[-4]`(density)+`path_parts[-3]`(group)，忽略 `path_parts[-5]`(run-id `random.1118/1125/1126`)。
- **path layout**: `RAN_ALL/random.1118/24Gb/Legacy/random0.x16_9200/A_Summary.rpt` → [-6]=log_name [-5]=run-id(被忽略) [-4]=density [-3]=group [-2]=sim_dir [-1]=A_Summary.rpt
- **fix**: 提取 `run_id=path_parts[-5]`，拼入 group 名 (`random.1118 Legacy 24Gb`) (msg[96]/[110])
- **vsim_report_new 同 Bug 2**: 3 处 `find` 无 `-L` (line 55/574/662) (msg[80]/[82]/[94])

### Feature: 终端 error matrix 打印
- 原 error matrix 只写报告文件不打印终端。加 `main()` 终端矩阵段 (msg[112]-[156])。
- 规则: 有错误类型 **且** sim≤300 → 打印矩阵；>300 跳过防刷屏；无错误跳过。

## 关键输出格式 (msg[162], 用户回退后)
**终端 stdout**:
```
============================================================
Monitor Error Analysis
  Scanning: <top_directory>
============================================================
  Sims found:   <N>
  With errors:  <N>
  Clean:        <N>
  Error types:  <N>
  Time:         <T>s
  Error Type                                            #Sims
  -------------------------------------------------- --------
  <error_type>                                          <count>
  Error count distribution:
    <N> error type(s): <M> sim(s)
  Report: <rpt_path>
```
**报告文件 xx_monitor_report.txt**: 6 sections (Header / Sims summary / Error Type table / Error count distribution / Error Matrix (when error types & ≤300 sims) / Sim detail list)。

## 错误类型 (DDR5 monitor tags, msg[75] RAN_ALL)
- `PUMP_MON: PUMP Error` (1608 sims)
- `WL_MON: ACT/ECS Error` (748)
- `WL_MON: REF/RFM All/SRE Error` (651)
- `WL_MON: RHR Error` (594)
- `CS_MON: CS Error` (87)
- rpt 行格式: `@timestamp [TAG] message` (PUMP_MON / WL_MON / CS_MON 标签)

## rpt 文件格式
- **空/clean rpt**: 单行 `============================[Internal Monitor Report Done]=====================================` (无 @timestamp 错误行)
- **有错 rpt**: 含 `@timestamp [PUMP_MON] ...` / `@timestamp [WL_MON: ACT/ECS Error] ...` 等行

## Case 构建计划 (next round r1570)
- **task_id**: EDA-Eval-DesignFlow-MonErrorAuditFix-001 (digital/verification, L1 produce-task)
- **核心 bug**: Bug 1 (空错误类型 max() 崩溃) — 最干净可测；附 Bug 2 (find -L symlink) 作第二断言组。
- **attachment A**: buggy `analyze_monitor_errors.py` (须从 trace read_files tool_results 重建，/proj/drcpa 对 e0031982 Permission denied，同 r1541 vsim.pl 先例) + 合成 `Internal_Monitor.rpt` 目录树 (clean rpt + 有错 rpt + symlink 子目录)。
- **hidden B**: 不同规模/取值的 rpt 目录树 (clean-only 触发 Bug 1 / mixed 触发矩阵 / symlink 触发 Bug 2)。
- **check() ≥8 断言**: ①空错误目录不崩 (exit 0) ②sim 计数正确 ③error type 提取正确 ④clean/wit-error 分类 ⑤报告文件生成 ⑥报告 6-section 结构 ⑦find -L 穿透 symlink (symlink 目录 sim 被计入) ⑧Error count distribution 正确 ⑨矩阵 ≤300 阈值 ⑩退化提交 FAIL (空壳/只 print 期望/删 max 修复)。
- **negatives**: naive_empty / naive_print_expected / cheat_core_deleted (删 max guard)。
- **DEBT 原因**: 本轮主交付=fullscan 用户令 #1-3 (已完成)；case 构建需 ~30min (脚本重建+合成 rpt 树+check.py+negatives+self-verify)，本轮剩 ~20min 不足以过质检闸门。质量优先于数量 (§3)。
