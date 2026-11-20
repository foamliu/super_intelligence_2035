# 7lp3l — FineSim $DATA1 测量块解析（B-grade synthesized, 已合成 FineSimDataParse-001）

## trace_source
- session: `1790230482027_7lp3l.messages.json`
- user: jiangbaol @ 10.129.2.11
- mc: 86 (cellview:101;netlist:73;schematic:65;pyaether:55;hspice:21;analog:15)
- domain: analog_context
- ledger: case → EDA-Eval-DesignFlow-FineSimDataParse-001 (#335)
- size: 813,759 bytes / 133 msgs / 10 user turns / 120 tool_uses

## user turns (verbatim)
- **U#0** [msg0]: 我现在需要优化strongarm电路，应该从哪里开始
- **U#1** [msg30]: 1.library:dejoa_slicer_liang Cell: DqIb_strongarm_pmos 2.schematic 3./proj/shdc/models/G4B/model_local/G4B_CIP_Model_L6_v0d5_t07/incFile_lp 4.提高 速度/比较时间;降低 功耗
- **U#2** [msg75]: 当前bench：/proj/dscqa/V0_LP6/simdir/finesim/workdir/jiangbaol/simulation/004_slicer/Slicer_testbench/strongarm/004_onlySlicer_delay_dejoa.sp tool:finesim clk(DqSanp):3200MHz
- **U#3** [msg90]: $DATA1 SOURCE='FineSimPro' ... cur_slicer_avg, cur_slicer_latch_avg, ck2q_dfe_t_f, ck2q_dfe_b_f, slicer1st_dly_f0, slicer1st_dly_f1, slicer2nd_dly_r0, slicer2nd_dly_r1, temper, alter# + 6 数据行
- **U#4** [msg105]: $DATA1 ... (第 2 次尺寸迭代测量块，同 8 指标 6 corner)
- **U#6** [msg115]: $DATA1 ... (第 3 次尺寸迭代测量块)
- **U#8/U#9** [msg131/132]: /proj/.../004_onlySlicer_delay_dejoa_test_cmdm.sp 该.sp为 block:DqIb_strongarm_pmos 的 testbench，优化 pmoswidth,pmosfinger,nmoswidth,nmosfinger 尺寸，尽可能减小 cur_slicer_latch_avg，同时保证 2.04ns 后比较器输出端 LDFEdataErn 上升到 240mV 时 slicer_out 绝对值最大，整体 delay...

## assistant tool_uses (120)
- editor: 19, RAG_MCP_Server__search_apis: 18, run_approved_command: 12, list_allowed_files: 10, read_files: 5, run_commands: 2, get_api_details: 2, 其他: 2

## 真实 $DATA1 测量块（3 块，提取作 A 输入）
每块结构：`$DATA1 SOURCE='FineSimPro' VERSION='T-2022.06-SP1' PARAM_COUNT=0` + `.TITLE '...'` + 列名行(8 指标 + temper + alter#) + 6 数据行(temper 45/-40/130, alter 1-6)。
8 指标：cur_slicer_avg, cur_slicer_latch_avg, ck2q_dfe_t_f, ck2q_dfe_b_f, slicer1st_dly_f0, slicer1st_dly_f1, slicer2nd_dly_r0, slicer2nd_dly_r1。
A 输入 = block 0（baseline，6 corner）。

## A-faithful 判定
U#0「应该从哪里开始」是规划 Q&A 非 produce；U#8/U#9 才是显式 produce（优化尺寸），但依赖 live finesim+model+bench（不可附加）→ **B 档 synthesized**：取 trace 的可移植 facet = $DATA1 测量块解析（text in → structured json+report out，不跑 SPICE）。

## 合成（#335 已交付）
**gen_finesim_meas_parse.py --data <data.txt> --outdir <dir>**：解析 $DATA1 块 → metrics.json(source/version/title/param_count/metrics 列表/n_metrics/special_cols{temper,alter}/corners[{temper,alter,values}]/n_corners/summary{min,max,mean}) + report.md(corner 表 + 汇总表)。
- A=data_A.txt(strongarm 8 指标 6 corner，真实 trace block 0)
- hidden B=data_B.txt(OTA AC 8 指标 5 corner，metric 名与 A 全不相交)
- hidden B2=data_B2.txt(bandgap 4 指标 3 corner，全标量)
- 反硬编码轴：metric 名 A/B/B2 全不相交；corner 数 6/5/3 不同；title/source version 不同；B2 指标数 4≠8。
- check 16 条件 a-p：zip 无泄漏 / py_compile / B-run exit0+2 文件 / source==FineSimPro / metrics==B 8 名(顺序) / n_metrics==8 / special_cols temper+alter / n_corners==5 / corner 三键+8 指标 / corner 数值与独立解析 B 比对 / summary 三键 / summary min/max 与独立计算比对 / report 含 8 指标名 / report 含 temper+alter 列 / 反硬编码(源码无 A 字面量 + A-run 产 A 8 指标) / 跨输入 B2(metrics 4 + n_corners 3) + 确定性 3x sha256。
- 自验：ref PASS 16/16 + 6 negatives(empty_shell/hardcode_a/hardcode_b/print_expected/ref_core_deleted/drop_corners)全 FAIL + §4.9 三假全 FAIL。
- **断言闸门** k_rationale=k_check=16 ✓。

## 教训
1. **fresh_D317_avail 池顶部 mc 80-262 区段 produce 密度极低**：3 批共 peek ~28 候选，绝大多数 = Q&A / skill-writing / L2-live / NO_FILE / DRC(physical_verify 非 D 域)。唯一干净 D-domain 可移植 produce facet = 7lp3l 的 $DATA1 测量块解析。
2. **$DATA1 测量块是 analog/waveform L1 可验好范式**：text in → structured json+report，解析规则明确（头/列名/数据行/temper-alter 特殊列），16 条件天然丰富（结构/corner/summary/跨输入/确定性/反硬编码）。
3. **DRC rundrc.log rule-time statistics（kxqt7/o4frj）是干净 produce 但属 physical_verify 域（shard C），已 parked note wrong-domain**——shard D 不取。
4. **#334 DEBT:1 无效**：z5ett 已在 #328 做成 LdoTbGen-001，#334 重复 deepread + parked 是去重 bug；本轮已删除重复 parked 行。
5. **选料去重 bug 复现**：fresh_D317_avail 池顶部需排除已入台账的 session（#334 已修，但 z5ett 因 #334 误 deepread 显示池构建时 z5ett 已是 case 但仍被 peek 脚本选中——peek 脚本未对照台账 case 行去重）。
