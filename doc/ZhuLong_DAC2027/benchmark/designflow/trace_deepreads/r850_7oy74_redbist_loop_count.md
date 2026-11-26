# r850 深读笔记 — 7oy74 (thomas1w@hfeg0pjn099/10.129.40.108)

## trace 元数据
- session: `1794450614593_7oy74`，用户 thomas1w，host hfeg0pjn099(10.129.40.108)，mc39
- domain: digital（DDR5 verification 仿真 debug，xrun/irun + SV randcase pattern）
- agent: lead，43 msgs，1 user turn（单轮 debug-Q&A）
- subdir-path ALIVE 291971B（flat-path NOFILE 假阴性，path-bug revival 又一例；r849 已确认 ALIVE）
- 旧判(2026-11-14) r503: "sim-path+pattern-path debug (truncated) debug pattern" → parked
- 11-15 reaudit: debug-Q&A 合法 → 待深读；r850 兑现

## 用户真实意图（U#0 原话）
```
/proj/ddgoa/V0/simdir/verilog/thomaswu/verilog.lpddr5.ddgoa.1029/log/log.regression_dft_20261111_201335/tm_redbist_check_failcol.x16/    这个是仿真路径
pattern 的路径为 /rundata/ddgoa/.../tm_redbist.run 和 /rundata/ddgoa/.../cmds_testmode/TM_RedBist.sv
我这里明明是循环8次，为为什么log中只有7次
`ifdef TEST_COL
    repeat(8) begin
        rdf = new(4); assert(rdf.randomize());
        randcase
            1: begin $sformat(pattern_name,"col_single_bit_force_test3"); sorted_col_force_and_collect(rdf, rdf.num_err, 1, "col_test3", ...); ... end
            1: begin $sformat(pattern_name,"col_single_bit_force_test2"); ... end
```
核心意图：**repeat(8) 循环了 8 次，为什么 log 里只看到 7 次**（debug-Q&A，单轮）。

## assistant 真实诊断（msg[42] 结论 + 数据支撑）
1. **repeat(8) 真的跑了 8 次**：irun.log 里 `sorted_col_force_and_collect` 每轮打印一条 `==== Sorted fail addresses (forced=32, new=N, total=T, task=col_testX) ====`，共 **8 条**：
   | 轮 | task | new | total | irun.log 行号 |
   |---|---|---|---|---|
   | 1 | col_test2 | 5 | 5 | 35179 |
   | 2 | col_test3 | 5 | 10 | 35324 |
   | 3 | col_test2 | 5 | 15 | 35474 |
   | 4 | col_test3 | 5 | 20 | 35629 |
   | 5 | col_test2 | 5 | 25 | 35789 |
   | 6 | col_test3 | 5 | 30 | 35954 |
   | 7 | col_test2 | 2 | 32 | 36127 |
   | 8 | col_test2 | 0 | 32 | 36304 |
2. **A_Summary.rpt 只显示 7 次的原因**：后处理报告按 **pattern_name 变化** 记一条，只有当 pattern_name 与上一条不同时才单独记行。第 7、8 轮**连续撞到同一分支 col_test2**（randcase 两个 `1:` 是 50/50，连续同名很正常），报告把这两轮**合并成一行** → 7 条（col_test2/col_test3 交替 6 条 + 末尾一条 col_test2 实为 7,8 两轮合并）。
3. **附带发现**：(a) 第 8 轮 `new=0`：fail_addrs 缓冲上限 32，第 7 轮已填满到 32，第 8 轮 force 出的地址重复或被 `buffer full(32), skip` 拦掉，无新增；若按"新增地址数"数轮次则只见 7 次有新增(5+5+5+5+5+5+2)。(b) 循环结束后 sorted_col_release 抛 UVM_ERROR "unable to locate hdl path" 空字符串(arr="",bk="",ydec="")。

## A 档不可行核验（r850 实测）
- `/rundata/ddgoa` 与 `/proj/ddgoa` 对 e0031982 在 10.129.40.108 上 Permission denied（cadmin 组，同 r844/r845/r848/r849 模式）
- 真实 irun.log 2.6MB、A_Summary.rpt 不可达
- 但 trace 中 assistant 的 run_approved_command 完整返回了 8 条 "Sorted fail addresses" 头 + 行号 + new/total/task + pattern_name 序列，gold 完整可见
- → B 档 synthesized reframe：忠实于 trace 报告结构的小型自包含 fixture 复刻 repeat(8)/randcase/A_Summary dedup 场景

## 拟造任务形态
B 档 synthesized debug-Q&A，digital 域。交付 = `analyze_loop_count.py <sim_dir>` 解析 irun.log + A_Summary.rpt + pattern.sv，输出结构化 JSON 诊断（actual_loop_count / report_recorded_line_count / root_cause_class=report_adjacent_same_name_dedup / merged_iteration_indices / merged_pattern_name / buffer_full_iteration / buffer_cap / refuse-to-hallucinate）。

## fixture 设计
- A（可见，trace 真实值）：repeat(8)，task 序列 [col_single_bit_force_test2/3 交替 + 末尾两轮 col_single_bit_force_test2]，merge [7,8]，cap 32，new [5,5,5,5,5,5,2,0]，A_Summary 7 行
- B（隐藏判分，结构不同）：repeat(10)，task 序列 [row_force_a/b 交替 + 末尾两轮 row_force_a]，merge [9,10]，cap 45，new [5,5,5,5,5,5,5,5,5,0]，A_Summary 9 行（反硬编，B 专属 token 不泄漏 A）
