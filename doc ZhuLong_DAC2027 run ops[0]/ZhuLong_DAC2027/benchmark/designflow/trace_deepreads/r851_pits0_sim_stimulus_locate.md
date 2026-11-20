# r851 深读 — 1791854347080_pits0 — 仿真激励定位 (analysis-Q&A)

## 元数据
- session: `1791854347080_pits0`
- user: `johnl` @ `hfeg0pkn003`(10.129.2.12) [scan 也命中 hfeg0pfn120(10.129.33.246)]
- mc=52, agent=lead, subdir-path ALIVE 314527B / 36 msgs (6 user turns, 2 真实 user input)
- 域: verification (DDR5 xrun 仿真 testbench 激励定位) — 台账旧标 digital, 据真实意图改 verification
- 旧判 r503(2026-11-14): "看下仿真激励在哪里 analysis Q&A" → parked (旧§5 Q&A-gate 误杀)
- 11-15 reaudit: analysis-Q&A / retrieval / explain 合法 → 复活

## 用户真实意图 (原话)
- U#0: `/rundata/drcoa/V0/simdir/verilog/liupei/verilog.ddr5.drcoa.sim_1010/debug_ism_pte1/tm_processmonitor_ismnewadd_pte_num=25.x8   看下这个仿真到激励在哪里`
- U#18: `我不看环境组建 我只看和我的电路端口相关的`
- = 单轮 analysis-Q&A: (1) 定位这个 xrun 仿真的激励在哪 (哪个源文件 / 哪个驱动 task / 哪些行) (2) 只呈现打到电路端口上的激励, 跳过 testbench 环境搭建

## agent 真实做法 (定位链)
1. list_allowed_files 看 sim dir → xrun.history / A_Pattern_Sim.v / A_Summary.rpt / probe.tcl / partition.txt / config
2. read xrun.history → s3/s4 行 `+define+ISM25 +num=25 +define+PROJECTNAME=DDR5TOP ... top.sv -input probe.tcl`
3. read A_Pattern_Sim.v → 第 17 行 `DFT_ISM025_Ras();` 无条件调用 + 第 19 行 `ifdef ISM25` 重复
4. read Pattern_tasks.v → `include "patterns/cmds_testmode/cmds_processmonitor/TM_Processmonitor_ismnewadd_pte.v"`
5. 写 find_ism025.py (run_approved_command python-runner) grep → DFT_ISM025_Ras 定义在模式文件第 1047 行
6. read 模式文件 1047-1121 → 拿到 DFT_ISM025_Ras 完整 task body
7. 最终答复 (中文 markdown): 激励源文件路径 + 行 1047-1121 + 端口相关命令 (ACT/PRE on bg=7/ba=3/row=16'h7AE0 两次 + testmode 装载经 CA + IsmSel=011001 + readsig 21 次移位) + 明确"没有 DQ 写/读数据(不像 ISM50/51)" + 区分环境(top.sv/PowerUp/initialize/Config_Timing) vs 端口激励

## DFT_ISM025_Ras task body (真实, 行 1047-1121)
- `Enable_TM();`
- `load_dft("cm0_ts_LoadCmEn",.cid(0)); Deselectn(.n(20));`
- `Load_TestMode(.ma('o000),.op('b0_0010),...)` cm0_ts_LoadCmEn
- `Load_TestMode(.ma('o016),.op(6'b010000),...)` cm1_fc_MR70PracAboSupt (PRAC)
- `Load_Mode(.ma(MR70),.op(8'b0000_0010),...)` PRAC/ABO 使能
- `Load_TestMode(.ma('o351),.op('b00_1000),...)` PerBankTrimBGH<1> 选 bank23
- `Load_TestMode(.ma('o011),.op('b0_0001),...)` cm0_ts_TdqEn
- `load_dft("cm0_ts_IsmClkSel",.cid(0))`
- `Load_TestMode(.ma('o151),.op('b00_0100),...)` cm0_ts_IsmEn 使能 Process Monitor
- `Load_TestMode(.ma('o500),.op('b01_1001),.op_mark('b11_1111),...)` cm0_ts_IsmSel<5:0>=01_1001
- `Load_TestMode(.ma('o501),.op('b00_0010),.op_mark('b00_0011),...)` cm0_ts_IsmSel<6>=1
- **端口存储命令**: `Active(.ba(3),.bg(7),.row(row_addr3=16'h7AE0),.enops(0)); Precharge(.ba(3),.bg(7),.enops(0)); Deselectn(20);` ×2
- `Load_TestMode(.ma('o143),.op('b01_0000),...)` cm0_ts_IsmOutEn 输出数字码
- `repeat(21){ Deselectn(5); load_dft("cm0_ts_ReadSigClk"); Deselectn(5); unload_dft("cm0_ts_ReadSigClk"); }` readsig clk 移位读出
- `Load_TestMode(.ma('o143),.op('b00_0000),...)` 关 IsmOutEn
- `Load_TestMode(.ma('o520),.op('b00_0100),...)` cm0_ts_IsmRst=1 复位 → =0
- `endtask` 行 1121

## 关键真实数据 (从 trace 完整可见)
- A_Pattern_Sim.v: 67 行, 第 17 行 `DFT_ISM025_Ras();` 无条件, 第 19 行 `ifdef ISM25` 重复; rowf='h7AE0
- Pattern_tasks.v: 1 行 include 模式文件
- A_Summary.rpt: Global_Seed 615542576, Passed Pattern 1, Failed 0
- A_Compare.rpt: `cm0_ts_IsmmSel[6:0] : 011001, pmbit : 01110_00000000000, start_stop : 669 ps`
- xrun.history: s3/s4 = 12Oct 17:48 跑, +define+ISM25 +num=25 +define+PROJECTNAME=DDR5TOP +define+PROJ_NAME="DRCOAF" +define+X8 +define+POST +define+USESDFX, top.sv, incdir .../liupei/.../sim_1010/netlist/V0_20260921_Layout_DDR5TOP_2026Sep30.095710
- probe.tcl: 7 行, probe TOP + TOP.A_pattern_gen.timing
- partition.txt: -primtop BCenterCA/BnkGTopX4_gut/array1G_Bot/array1G_Top/D_BankLogicx2/...
- tbconfig: tbarchetecture=ddr5, tbprojecttopname=DDR5TOP, dbversion=V0
- 模式文件含多个 task: DFT_ISM017_Ras(行1) / DFT_ISM026_Ras(行88) / DFT_ISM027_Ras(行197) / DFT_ISM029 / DFT_ISM050 / DFT_ISM025_Ras(行1047) / DFT_ISM051(行1124) / DFT_ISM051_Cas(行1215)

## A档可行性核验
- /rundata/drcoa 对 e0031982 在 10.129.2.12 实测 Permission denied (cadmin 组, 同 r844/r845/r848/r849/r850 模式)
- → A档不可行, B档 synthesized reframe
- B档忠实依据: trace 中 read_files 对所有关键文件(xrun.history / A_Pattern_Sim.v / Pattern_tasks.v / A_Summary.rpt / A_Compare.rpt / probe.tcl / partition.txt / tbconfig / si.env / 模式文件多段含完整 DFT_ISM025_Ras body) tool_result 内容完整可见(agent-policy readableRoots=["/"] 未剥离), 可忠实提炼成自包含小型 fixture

## 拟造任务形态
- case_id: EDA-Eval-DesignFlow-SimStimulusLocateQA-001
- domain: verification
- 档: B档 synthesized
- 范式: S5 analysis-Q&A + specificity oracle (静态中文 markdown 报告, 同 DqselDefineMismatchQA-001)
- 交付: submit.zip 内 stimulus_locate_report.md
- fixture A(可见): 自包含 sim_dir_A/ 复刻真实结构(xrun.history/A_Pattern_Sim.v/Pattern_tasks.v/A_Summary.rpt/A_Compare.rpt/probe.tcl/partition.txt/config + patterns/.../TM_Processmonitor_ismnewadd_pte.v 含多 task + DFT_ISM025_Ras 完整 body)
- hidden-B(判分, 结构同标识符全改): sim_dir_B/ 不同 task(DFT_ISM038_Ras) + 不同 bg/ba/row + 不同 MR(MR62) + 不同 IsmSel 值 + 不同 Global_Seed, judge-only 不进 SUT 沙箱
- check.py: 解析 A 推导 ground-truth(源文件/驱动 task/定义行/端口命令 ACT+PRE bg7/ba3/row 0x7AE0/testmode 装载/IsmSel=011001/环境区分), 解析 B 推导 B-only 标识符; 断言报告含 A 真实事实 + 不泄漏 B + refuse-to-hallucinate(ISM025 无 DQ 写读) + 区分环境 vs 端口(对应用户第二条意图) + 反退化
- 预计 k≈13

## 同批未选
- 本轮单条 case, pits0 优先(DEBT b 标记 subdir ALIVE 可优先深读)
