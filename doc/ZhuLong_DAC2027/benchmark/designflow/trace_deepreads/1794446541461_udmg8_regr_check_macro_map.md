# deepread — 1794446541461_udmg8 (lein, hfeg0pkn001, mc396)

**session**: `1794446541461_udmg8` @ 10.129.2.10, 479 msgs / 2.93 MB, 目录格式。
**user**: lein, **domain**: verification (LPDDR6 验证平台 pump monitor / 回归宏映射)。
**keywords**: verilog:2675; drc:564; netlist:194; cmos:42; rtl:22; analog:20; lib.defs:18; .cdl:16 (A-dominant, mc396, fresh 未入任何 shard 台账)。

## user turns (15 条实质)
- U#0/U#3: `refresh_parc.run` 路径下此用例验证的场景有哪些？
- U#1: 纠正前提——PRAC = Per-Row Activation Count (DDR5/LPDDR6 RowHammer 防护), 重新分析。
- U#2: **核心 produce-task**——结合 lpddr6 验证环境, 分析 `proj_monitors.inc` 中 `CS_CHECK`/`WL_CHECK`/`PRAC_CHECK` 三个宏, 都是 `Regressions` 下哪些用例需要使用。
- U#4/U#5/U#6: 在 `project_pump_monitor.sv` 文件里加上代码注释; 修改 lpddr6 只有 all bank / dual bank 刷新(无 perl bank)。
- U#7/U#10/U#11: `refwlmonitors`/`TYPE_REF`/`refmonitors` 变量定义/实例化/采样实际值位置。
- U#8: **produce-task**——分析 ddr6 验证平台 + ddr5 `project_pump_monitor.sv`, 给 lpddr6 平台写一个 pump_monitor SV 监视文件。
- U#12/U#13/U#14: 分析 ddr5 `project_pump_monitor.sv` 监视了什么/实现方式; bind 哪些信号; `proj_package.sv` `TYPE_REF` 各组成变量含义。

## agent 工作 (241 tool_use: read_files×99, run_approved_command×68, editor×55, list_allowed_files×17)
- 写 search_checks.sh / search_includes.sh / search_tb.sh / search_make.sh / search_prac.sh / search_ref_mon.sh 等 grep 脚本扫描回归树。
- 关键发现: run 脚本 (run_tapeout_normal_tt / run_tapeout_x6_tt) 以 `vsim ... -d "... WL_CHECK "` 形式携带 CHECK 宏——宏作为 `-d "..."` define list 的尾 token。
- 两种调用格式: Perl `system("...vsim -sr <scn> --regnameb=<scn> -d \"... <MACRO> \" ...")` 与 shell `...vsim -sr <scn> -d "... <MACRO> " ...`。
- 实测: WL_CHECK 用于 refresh/rhr 系列, LEVELING_CHECK 用于 leveling, **CS_CHECK/PRAC_CHECK 在 run_tapeout* 中未使用**(grep 空)。
- `--rannum N` 变体: refresh_sr_shmoo (rannum 0-4) 同 scenario 多 seed。
- U#8/U#12/U#14: 深度分析 pump monitor ~2446 行 + 11 条 bind 语句 + TYPE_REF 结构体逐成员解释(分析报告型, 非可执行产物)。

## A-faithful 选定子任务
U#2 的宏→用例映射是确定性、可自包含的 produce-task: 扫描 run_* 脚本, 提取每个 vsim 调用的 scenario(`--regnameb=` 优先, `-sr` 回退) + CHECK 宏(`-d "..."` list 中 `_CHECK` 后缀 token) + `--rannum` 变体, 输出结构化映射 JSON。
- 用户给: .inc 宏名 + Regressions 路径 + 目标(哪些用例用哪个宏); **未给**: 解析算法/格式细节/define-list 提取规则 → A-faithful 合格。
- deliverable = 修改/分析私有 `/rundata/decqa/...` + `/proj/drcoa/...` 文件 → **INFEASIBLE**(沙盒无权限, /rundata 对 e0031982 Permission denied) → **B 档合成**自包含 run 脚本扫描器。

## 合成 case
**EDA-Eval-DesignFlow-RegrCheckMacroMap-001** (verification L1-B, k=13, B 档, archetype=regression-run-check-macro-mapper)
- ref: `regr_check_macro_map_ref.py` 纯 stdlib regex 解析两种格式(Perl `\"` 转义 + shell `"`), 跳过 `#` 注释行, --regnameb 优先, _CHECK 尾 token, --rannum, 输出 {scripts_scanned, total_invocations, invocations, by_macro, no_check, per_macro_counts, unique_scenarios, scenarios_with_rannum_variants}。
- A=run_A/{run_tapeout_A(Perl 6 active+1 commented decoy), run_x6_A(shell 4 active, 含 -sr/--regnameb 不一致 trap)}。
- B=hidden/run_B/{run_normal_B(Perl 11 active+1 commented decoy_b), run_x6_B(shell 3, cbr_alias→cbr_train_real trap), run_corner_B(shell 2)}; 16 invocations, WL=8/CS=2/PRAC=2/LEVELING=1/NO_CHECK=3, 无 A 名重叠(跨输入守卫)。
- check.py 13 条件(a-m), 独立 string-oracle(str.find/split/endswith, NO regex)。
- 自验: ref SELFTEST 13/13 PASS; 5neg(naive_empty/print_only/hardcoded_A/no_comment_strip/wrong_macro)全 FAIL; §4.9 fake-submit(empty_zip/garbage/print_string)全 FAIL; 断言闸门 k_rationale=k_check=13 ✓。
