# deepread 0g9n6 — thomas1w 仿真卡死 (sim hang, zero-delay gate oscillation)

## trace
- session: 1794557869660_0g9n6
- user: thomas1w  host: hfeg0plg98  domain: verification  mc: n/a (parked_reaudit revival)
- 27 msgs, deepseek-v4-flash
- U#0 原话: `/rundata/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.1030/llog_1113/scan_allspeed.x16/  仿真卡死，加了一些zero loop的检测，也没检查出来，帮我看下`

## agent 分析过程
1. list_allowed_files scan_allspeed.x16/ → irun.log, A_Compare.rpt, Pattern_tasks.v, A_Pattern_Sim.v 等
2. read_files irun.log (43745 行) → 尾部 line 43730 `ncsim> run`, 43731 `dutconfig.dvfscsupt==2`, 43732 `ncsim: *W,TRZDGOC: Possible zero-delay gate oscillation detected`
3. read A_Compare.rpt → pattern_start @ 1ps, BG_Act-Wr-RdAp @ 1914132770 ps
4. grep irun.log → COUNTS: TRZDGOC=1, oscillat=1, gateloop=1 (全 log 仅 1 处, 在 line 43732 run 区)
5. 定位 TB root /proj/ddgoa/V0/sim/verilog/sos_manage/lpddr5_tb (compare_tasks.sv / pincompare.sv)
6. 结论: 不是 TB "卡时间步进" 零环 ($time 不动), 而是真实门级组合逻辑零延迟振荡 (combinational loop / zero-delay gate oscillation), 发生在 sim time 1914941946 ps (~1.9149 ms), 在第 1 个随机跑到的 BG_Act-Wr-RdAp pattern 里. 真正抓到的是 ncsim 内建检测器 (-gateloopwarn → TRZDGOC), 不是用户在 TB 加的 zero-loop 检测.

## 关键事实 (checkable)
- failing_tool: ncsim (irun)
- warning_code: TRZDGOC (zero-delay gate oscillation)
- gateloop_flag: -gateloopwarn (enabled)
- sim_hang_time_ps: 1914941946
- irun_log_lines: 43745
- trzdgoc_count: 1 (line 43732)
- run_command_line: 43730 (`ncsim> run`)
- pattern_name: BG_Act-Wr-RdAp
- root_cause_class: combinational zero-delay gate oscillation (NOT tb time-step stuck loop)
- user_watchdog_caught: False (ncsim built-in -gateloopwarn caught it, not user's added zero-loop detection)
- TB family: lpddr5_tb / compare_tasks.sv / pincompare.sv

## 判定: parked_thematic_dup
- 与 r645 `CmpTaskZeroDelayOscDiagnose-001` (ia08o, xy1zhang@hfeg0pgn145) **同一根因类**:
  两者都是 ncsim TRZDGOC zero-delay gate oscillation, 同一 lpddr5_tb/compare_tasks.sv TB 家族,
  同一 -gateloopwarn 检测路径. r645 已落地 (A.jsonl 349→350, k=15).
- 虽 trace 不同 (不同 session/user), 但任务设计 (debug-Q&A: 解析 irun.log 找 TRZDGOC 振荡根因)
  与 r645 高度同质, B 变体也难做出 ≥8 维与 r645 全异的差异 (都是 TRZDGOC + compare_tasks + 同样的
  zero-delay-osc 根因结构). 造出来会与 r645 在判分结构上大面积重叠.
- 按 11-15 任务初衷「真实性=唯一来源」+ 避免题库同质化: park, 不造. 下轮选不同根因类的候选.

## 下轮建议
优先 debug-Q&A 但**不同失败模式**: 编译错误 (xmvlog/xmelab E,xxx 而非 TRZDGOC 振荡), 或
runtime assert/timeout/死锁 (非 zero-delay-osc). 候选: o5njo (irun.log sim-error, e0039602),
pz29g (A_Compare.rpt error, e0039602), whu5z (smoke.log FAIL, lorikx), d56nb (sim-failure, ruisongs).
