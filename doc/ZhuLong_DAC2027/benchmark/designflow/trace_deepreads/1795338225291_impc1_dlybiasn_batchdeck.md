# 深读笔记: 1795338225291_impc1 (aryaoy@hfeg0pkn005, mc=92, schematic+waveform)

## 会话概况
- 65 msgs, 426KB, user aryaoy, host hfeg0pkn005, cwd /proj/drvqa/V0/workdir/aryaoy/
- agent = cline (block-sim skill + virtuoso-cli skill)

## 真实意图（用户原话 + 行为）
1. 用户先问 block-sim 技能怎么用（FineSim block 级仿真，virtuoso-cli 桥接）
2. 用户给出 9 个目标 cell（drvqa_cmos_core 库）：
   - R_dlybiasn{500,750,1000,1250,1500,2000}ps_custom
   - R_dlybiasn{250,500,1000}ps_custom_small
   - 工艺角 TT/SS，测 Delay Time (In→OUT)
3. 用户选择「复用项目现有 delay 测量 bench」

## agent 工具链
- list_allowed_files: 探 /proj/drvqa/V0/workdir/aryaoy/, model/, setup/sim/, sim_setup(Normalsim/finesim_option), Aryaoy_DlyCell/, simulation/ 软链 → /rundata/drvqa/V0/simdir/finesim/workdir/aryaoy/simulation/
- read_files: cds.lib, reference_test.sp (aryaoy_R_OcOffDlyNcs210_vdly_schematic_ALPS/test.sp), skill 脚本(extract_netlist.py/run_simulation.py), virtuoso-cli api(_base.py/__init__.py/cli.py)
- SandBox_MCP_Server__run_code: 确认 pyAether 沙箱 cwd=/proj/drvqa/V0/workdir/aryaoy/, 试 EdaSession() 连 bridge → RuntimeError: Cannot connect

## 关键产物 / 发现
- 9 个 cell 全部确认存在于 drvqa_cmos_core，有 schematic/symbol/layout/verilog 视图
- 模型: current → V2B_HK_Model_D5_v0d1_Rev02_t01; 基准 test.sp 用 Rev01_t01 + incFile_V1_HKMG
- Golden delay 范式 (从 test.sp 提炼):
  - vcc=0.98 / vdd1=2.1 / vbn=-0.07 / vbp=1.08 / vss=0.0
  - i_dlybias=6.63u (delay bias 电流, OTA 式偏置)
  - In 在 10.2n 触发, .tran 1n 2000n
  - 测 In→OUT 0.5V 阈值延迟 (rise/fall tr/tf 10ps)
- sim_setup 差异: DRVQA 用自研 createCornerFile/createControlFile + Normalsim/*.csv, 非 skill 默认 vrwck_lookup.pl
- DlyCell_result/ 里只有 WaveView .sx 会话文件(非可复用 sim setup), 真正仿真控制是 aryaoy_R_OcOffDlyNcs210_vdly_schematic_ALPS/test.sp

## 阻塞
- EdaSession 连不上 Virtuoso bridge (~/.virtuoso-cli/ports/ 无实例)
- block-sim 抽网表是硬依赖 (extract_netlist.py 需 cxmt_SchmaticTool_Dsim_SpiceOut 在 Virtuoso 里跑)
- agent 如实汇报阻塞, 提议先把 9 cell 的 sim.sp/stimulus/pvt 模板预生成好, 等 bridge 一就绪就跑

## case 合成: EDA-Eval-DesignFlow-DlyBiasnBatchDeckGen-001
- 域: schematic_netlist (shard D), L1 (离线 Python deck 生成)
- 内核: batch_deck_gen.py 读 paradigm_spec.json + cell_manifest.json, 为每个 cell × corner 生成 FineSim deck
- deck 结构: .option / .param(supplies+i_dlybias) / .lib 模型引用 / 各电源 vsrc / idlybias 电流源 / In 脉冲激励 / cell 例化 / .meas 延迟(rise+fall+avg) / .tran
- A(给SUT): Rev01 模型, 阈值0.5, tran 1n/2000n, trigger 10.2n, i_dlybias 6.63u, 电源{vcc,vdd1,vbn,vbp,vss}, 3 cell, corners[TT,SS]
- B1(hidden): Rev02 模型, 阈值0.45, tran 2n/4000n, trigger 20.4n, i_dlybias 8.2u, 电源多 vbn2, 4 cell(多 vbn2 pin), corners[TT,SS,FF] → 12 deck
- B2(hidden): Rev03 模型, 阈值0.4, tran 0.5n/3000n, trigger 15.0n, i_dlybias 5.5u, 2 small-variant cell, corners[TT,SS,FF_cold] → 6 deck
- A/B1/B2 结构性不相交(模型版本/阈值/tran网格/触发时刻/i_dlybias/电源集合/cell名/corner集 全不同)
- k_check=14: ①zip含脚本 ②B1 exit0+有deck ③B1 deck数=12 ④B1模型路径=Rev02 ⑤B1阈值=0.45(反硬编码A=0.5) ⑥B1 tran stop=4000n(反A=2000n) ⑦B1 trigger=20.4n(反A=10.2n) ⑧B1 i_dlybias=8.2u(反A=6.63u) ⑨B1 接 vbn2(B1有A无,测电源泛化) ⑩B2 corner≠B1+deck数=6 ⑪B1≠B2内容 ⑫反硬编码A(A阈值=0.5≠B1=0.45) ⑬确定性md5 ⑭随机化3种子同名集
- 自验: reference 14/14 PASS + 3 负样本(print_only/empty_stub/hardcode_a)全 FAIL + negative_selftest 0 bug
- 按 11-23 运维令只写 cases/D/<id>.json 不碰 jsonl
- 台账 1795338225291_impc1 → case
