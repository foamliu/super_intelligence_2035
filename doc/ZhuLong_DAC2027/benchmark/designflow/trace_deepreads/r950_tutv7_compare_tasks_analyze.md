# r950 deepread — tutv7 LPDDR6 compare_tasks.sv 三问 analysis-Q&A

## trace
- session: 1795225169331_tutv7 (user e03101, host hfeg0plg15, mc62)
- 40 msgs / 396KB, ALIVE on hfeg0plg15 (subdir sessions/1795225169331_tutv7/)
- domain: verification (LPDDR6 PTE testbench, SystemVerilog)
- 三问 analysis-Q&A (逐字):
  - U#0: 帮我分析一下.../compare_tasks.sv 这个文件的功能
  - U#6: 怎么启用这个compare的功能
  - U#28: 现在的环境启用了吗，启用了的话输出在哪里

## gold (assistant msg#5 / #27 / #39)
- Q1 (msg#5): compare_tasks.sv 是 LPDDR6 TB 比较/校验核心. 7 大组成部分:
  1. 配置 task (compare_set_default/compare_set_ignorebit/compare_set_ignoreval/compare_set_tolerance/compare_enable/compare_disable/model_compare_enable/model_compare_disable)
  2. compare_set_default 默认值: compareflag=1'b0, ignorebit=-1, ignoreval="none", tolerance=timing.tCK/2-timing.tQW_min
  3. gencompare_expdata 函数 (L261-300): 处理 z/x/ODT, ignorex/ignorez/ignore0/ignore1/only01/only01z/only0z/only1z/osc
  4. pattern 统计 (L302-343): always @(pattern_name), pattern_sum.total/passed/failed, pattern_end 打印 Total/Failed/Passed
  5. generate 块 (L345-581): DQ/RDQS_t/RDQS_c, ODT 计算, 忽略标志, buf #(comp_delta) 门控, err_cnt
  6. dm 通道被注释掉不比较
  7. 编译期宏: LOOPBACKSIM/TWORANKSIM/DISODTCOMP/NOCHIP/SCSHARE/SEFF

- Q2 (msg#27): compareflag 是总开关 (TYPE_Compare 结构体). 启用步骤:
  1. compare_set_default() 复位
  2. compare_enable("all") + model_compare_enable(.settype("all")) 在 A_Pattern_Sim.v L6/L15
  3. compare_disable("all") + model_compare_disable("all") 收尾
  settype: rdqs_t/rdqs_c/dq/alert/dutmonitor/all (dm 注释)
  前置条件: 期望数据装载 (dq_exp/rdqs_t_exp FIFO) / PDRIVER.DQ 连接 / dq_compare_flag / ODT/RTT / comp_delta (TS_1600=120ps) / fd_compare/fd_summary $fopen / pattern_name 统计

- Q3 (msg#39): 已启用. verilogrun 无 NOCHIP 宏 (只有 X16/MODELDEBUG/USESDF/DEFF/DUALPATTERN/GLOBAL_SEED) → compare_enable 执行.
  A_Summary.rpt: PE_Pattern_Test DQ_Err:0... Total Pattern:1 Failed:0 Passed:1
  输出: log/noregression.x24/ → A_Compare.rpt, A_Summary.rpt, B_Compare.rpt, B_Summary.rpt, m_Compare.rpt
  A_Compare.rpt 格式: at <时间戳> ps, DUT_DQ :<值>, Model_DQ :<值>

## fixture
- compare_tasks.sv: B档 reconstructed (行1-71逐字自trace read_results msg#2, 行72+按gold msg#5/#27结构重构). 真实文件 Permission denied (e0031982 非 e03101).
- A_Pattern_Sim.v: 逐字自 trace msg#22 (前~90行)
- A_Summary.rpt: 逐字自 trace msg#33 (完整13行)
- A_Compare.rpt: 逐字自 trace msg#35 (前60行)
- verilogrun: 逐字自 trace msg#35 (irun 命令 + +define 宏)

## case
- case_id: EDA-Eval-DesignFlow-Lpddr6CompareTasksAnalyzeQA-001
- domain: verification
- k=17 assertions (a-q), §4.2 subprocess + anti-leak + refuse-to-hallucinate
- ref PASS 17/17, 5 negatives全FAIL (empty/print_expected/core_deleted/b_leak/hallucinate)
- A.jsonl 439→440
