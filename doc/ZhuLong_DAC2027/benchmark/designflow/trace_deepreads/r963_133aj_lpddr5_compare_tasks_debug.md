# r963 deep-read: 1795226325736_133aj — LPDDR5 vector-replay compare-result debug

**Candidate**: 1795226325736_133aj (e0039503@hfeg0pkn003, mc132, verification domain)
**Trace**: 117 msgs, 903KB, scp'd to eda_flow workdir
**Case produced**: EDA-Eval-DesignFlow-Lpddr5CompareDiagnose-001 (debug-Q&A → diagnose produce-task + hidden-B, k=23/23, §4.9 三假 FAIL)

## Session arc

- U#0 (msg 0):「帮我分析这个路径下的 compare_tasks.sv 文件」→ assistant 读完 compare_tasks.sv (556行) + lpddr5_test.sv + lpddr5_package.sv + timing_load.sv 上下文，产出完整结构分析报告。
- U#2 (msg 23):「为什么我的结果文件里面没有比较的结果」→ assistant 排查发现: ① 结果文件在每次运行的子目录里 (vsim 脚本建独立 run dir, A_Compare.rpt/A_Summary.rpt 用相对路径打开); ② A_Compare.rpt 只记 mismatch 不记 pass; ③ **关键**: A_Summary.rpt 只有 "Global_Seed is 1235153712" + "====" 头, 无 per-pattern 行。
- U#3 (msg 38):「8_LP5_read32_tCCD_COVERAGE.x16 这个是正常跑完的」→ assistant 查该 run dir 的 sim.log, 发现 `Simulation complete via $finish(1) at time 1397333870 PS + 0 / ./pevave_tasks.sv:184 $finish` — 仿真被 pevave_tasks.sv L184 $finish 结束, **不是**走主流程 pattern_end (L8866) 正常收尾。
- U#4 (msg 65/68/69):「方案B该怎么改」→ assistant 深挖: getpetablevalue() (L188-199) 把 .avc DQ 列的 L/H (读期望 strobe 数据) 一律映射成 1'bz 丢弃, 且 loadsequencetable 从不赋 dq_exp → compare_tasks.sv DQ 比较通路恒 x → 结构性静默。方案B fix: 拆 getpetablevalue 为 _drive (0/1→驱动, X/L/H→z) + _exp (L/H→0/1, 0/1/X→z), loadsequencetable 里 DQ/DM 同时赋 dq_out + dq_exp。
- msg 91: policy 限制只读 /proj, 不能直接改 pevave_tasks.sv → assistant 产出 apply_plan_b.py 一键补丁脚本 (18 处精确替换) + validate_plan_b.py 校验 (18/18 命中)。

## Root-cause gold (4 layers)

1. **结果文件位置**: vsim 脚本每次运行建独立 run dir (log_dv/<pattern>.x16/), A_Compare.rpt/A_Summary.rpt 用相对路径打开, 顶层目录没有。
2. **A_Compare.rpt 性质**: 错误日志 (compareflag=1 + mismatch 才写), 不是结果报告; 全 pass 时只有 pattern 头。
3. **$finish 抢杀 pattern_end**: pevave_tasks.sv L184 `#100ps; $finish;` 在 loadsequencetable 放完 CSV 后结束仿真 → 主流程 L8859 "Final random number" / L8866 `pattern_name="pattern_end"` / L8879 `simdone=1` 从未执行 → A_Summary.rpt 永远只有 seed 头 (compare_tasks.sv 的 always@(pattern_name) 块只在 pattern_end 到达时写 per-pattern 汇总行)。
4. **比较通路结构性静默**: getpetablevalue() L188-199 的 case 只映射 "0"→0, "1"→1, default→z — .avc DQ 列的 L/H (读期望 strobe 数据) 落入 default→z 被丢弃; loadsequencetable (L144-159) 只赋 dq_out, 从不赋 dq_exp → dq_exp 恒 x → gencompare_expdata 返回 x → dq_err 恒 x → 永不报 mismatch。

## .avc / CSV 编码 (确认)

- .avc: ARBIN/ARBOUT 格式, 引脚字符按位置排列, DQ 列含 0/1/X/L/H。
- avc2csv.sh 原样转 CSV, 不区分读/写。
- CSV DQ 列整行: 全 0/1 = 写突发 (驱动数据); 全 L/H = 读突发 (期望/strobe 数据); 全 X = 空闲。零混合行 (classify_dq_rows.py 确认)。
- READ runs: DQ 全 L/H, DQS 也 L/H (RDQS 读码形), 行长 24/48 行。
- WRITE runs: DQ 全 0/1, DQS=0, 行长 32/64 行。
- 无需解 CA 命令, 仅凭 DQ 列值即可区分读/写/空闲。

## 方案B fix (delivered as apply_plan_b.py)

- 新增 `getpetablevalue_drive(v)`: 0/1→驱动值, X/L/H→z (写驱动/释放)。
- 新增 `getpetablevalue_exp(v)`: L/H→0/1, 0/1/X→z (读期望)。
- loadsequencetable DQ0-15 + DM0/DM1: `dq_out[i] <= #dq_delay getpetablevalue_drive(...)` + `dq_exp[i] <= #dq_delay getpetablevalue_exp(...)`。
- RDQS 保留原样 (DQS 的 L/H 在读码形里是 strobe 本身, 不是期望数据)。
- dq_delay = t_val + 240 (L105), t_val = 该行 PS 周期, 随每个 pattern 的 period= 运行时传入, 不写死。
- 校验: 18/18 替换串精确命中 pevave_tasks.sv, helper 锚点匹配, 文件未被打补丁。
- 注意: 改完机制层通, 但需对齐 (dq_exp 更新时刻 vs DUT 真实 WCK→DQ 输出延时) + 滤波, 否则跳变沿毛刺误报。

## Case 提炼

- 类型: debug-Q&A → diagnose produce-task (通用根因诊断脚本)。
- 输入: sim run dir (A_Summary.rpt + A_Compare.rpt + sim.log + A_Pattern_Sim.v + pevave_tasks.sv + base_check.csv)。
- 输出: JSON 12 字段 (global_seed / summary_has_only_seed_header / pattern_end_reached / sim_ended_via_finish / finish_location / pattern_name / compare_enable_value / dq_exp_assigned_in_vector_flow / getpetablevalue_drops_LH / read_bursts_present / write_bursts_present / total_csv_lines)。
- A = trace run dir (PE_Pattern_Test, $finish@pevave_tasks.sv:184, seed 1235153712, 34 行 CSV, 可见)。
- hidden B = 同根因结构但不同 pattern (LP5_Write16_Burst) / 不同 $finish 行 (191) / 不同 seed (9876543210) / 不同 CSV 行数 (48) / 不同 DQ 序列。
- check.py 23 条断言: zip+编译+运行A/B + A 12字段 + B 跨输入差值 (pattern/finish/seed/lines 均不同于A) + B 结构同根因 + 确定性 + 反退化 + 反硬编码 (A/B pattern_name 和 finish_location 必须不同)。
- ref PASS 23/23, 5neg (empty-shell/print-only/core-deleted/wrong-logic/skip-csv) 全 FAIL, §4.9 三假 FAIL。
