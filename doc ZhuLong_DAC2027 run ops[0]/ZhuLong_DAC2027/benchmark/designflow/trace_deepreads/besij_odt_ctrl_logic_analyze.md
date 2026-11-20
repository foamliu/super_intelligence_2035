# besij — DqOutTopM6 ODT 控制逻辑分析 (deepread)

- session: 1792563327292_besij.messages.json
- user/host: clarawu / hfeg0pkn003 (10.129.2.12), mc=66
- trace 位置: host 端子目录 `1792563327292_besij/` 下（非根 .messages.json），44 msgs / 274KB
- domain: spice_sim (DDR4 DQ output pad ODT control logic analysis)
- 旧判: parked "consultation/分析, 非交付" → r618 reaudit 复活（analysis Q&A 全部恢复可造）

## 用户原话（3 轮）
1. `<user_input mode="act">学习一下 @/proj/m2701/V0_DDR4/workdir/clarawu/simulation/DqOutTopM6/hspiceD/schematic/netlist/netlist，告诉我这里面 ODT 相关的控制逻辑</user_input>` — 核心任务：读网表分析 ODT 控制逻辑
2. `某一挡（如 <0>）从 OdtEn/MdOdt/WlvEn 到各端接腿的完整信号链画出简化逻辑图` — 追问 <0> 挡信号链
3. `@/proj/m2701/V0_DDR4/workdir/clarawu/simulation/MRodtDec/hspiceD/schematic/netlist/netlist 分析一下这个电路的功能` — 转向分析 MRodtDec 译码器（独立子任务，不在本 case 范围）

## agent 工具链（policy: python-runner + shell-runner, readableRoots=/）
- get_agent_policy_status → enforcing, profileIds=[python-runner, shell-runner]
- list_allowed_files 探 /home/clarawu、/proj/.../DqOutTopM6/hspiceD/schematic/netlist
- read_files 分段读 netlist（1-400, 280-900, 2029-2276, 1631-1850, 2062-2245, 2135-2200, 1013-1033, 888-900）共 2276 行
- search_codebase 查 subckt.*DqOutTop / .global / ODT.*Ctrl → 全部 30s 超时（大 scope）
- editor 写 analyze_netlist.py（枚举全部 .subckt）+ analyze_odt.py（按 .subckt/.ends 栈算每个子电路归属行区 + 定位顶层实例区）
- run_approved_command(python-runner) 跑两脚本

## netlist 结构事实（agent 提取）
- 2276 行，dejoa_io 库，顶层 cell DqOutTopM6
- 全部 .subckt 定义（节选）: switch_close/switch_open, inv/invLx*/inven, nor2/nor2Lx*/nor3/nor3x2, nand2/nand2Lx*, invx1/invx2/invx4/invx8/invx32, aoi21/aoi21x2/aoi21x2_dq, oai31x2_dq, DqFinalODTZq3/4/5/Pdmain CtrlSub1/2/3_New (12 个 ODT 控制子电路), DQTX_scmos, DqOutWlvDelay, ...
- ODT 端接腿子电路（DqFinalODTZq4CtrlSub2_New 例, line 324）:
  - 管脚 `AllOdtNmosEnN AllOdtPmosEnN Out Rst RstN ZqN inh_vcc inh_vss`
  - XMMN14 Out AllOdtNmosEnN vss vss ntn（低有效 N 管下拉端接）
  - XMMN1 Out Rst vss vss ntn（复位钳位腿）
  - XMMN6/XMMN5 net014 RstN / Out ZqN net014（RstN 与 ZqN 串联 ZQ 校准下拉通路）
  - XMMP13/XMMP12 net5 ZqN vcc / Out AllOdtPmosEnN net5（ZqN 使能 PMOS，AllOdtPmosEnN 低有效经 ZQ P 管上拉对 VCC 端接）
  - 各 Zq3/4/5 子电路结构一致，仅管子尺寸（端接阻值）不同；Pdmain 控制主下拉驱动
- 顶层使能生成（line 2044~2276，3 挡 <0>/<1>/<2>）:
  - 输入: OdtEn→OdtEnN(XI14), OdtNTEn→OdtNTEnN(XI94), WlvEn→DqOutWlvDelay→WlvEnInt→WlvEnN(XI62), MdOdt<0..2>→两级反相(XI53/XI67)→MdOdtBuf<0..2>, MdOdtNT<0..2>→两级反相(XI13/XI66)→MdOdtNTBuf<0..2>, DataEn<0..2>, 复位 NTODTNnRst→XI96/XI98→NTODToRstN/NTODTNnRstBuf
  - 中间结点: net099<n>=nand2x2(OdtEn,MdOdtBuf<n>), net0100<n>=nand2x2(OdtNTEn,MdOdtNTBuf<n>), net0105<n>=nor2x2(OdtNTEnN,MdOdtNTBuf<n>), net0119<n>=nor2x2(OdtEnN,MdOdtBuf<n>), net0153<n>=nor3x2(OdtNTEn,OdtEn,DataEn<n>)
  - PMOS 使能: net0103<n>=aoi21x2_dq(net0100,net099,WlvEnInt)=~(WlvEnInt+net0100·net099), AllOdtPmosEnN<n>=invx8(net0103) → 低有效，上拉端接开启当 WlvEnInt=0 且 (OdtNTEn·MdOdtNTBuf 或 OdtEn·MdOdtBuf) 为真
  - NMOS 使能: net0122<n>=oai31x2_dq(net0105,net0119,net0153,WlvEnN)=~(WlvEnN·(net0105|net0119|net0153)), AllOdtNmosEnN<n>=invx8(net0122) → 低有效，下拉端接开启当 WlvEnN=0（写电平校准）或三路条件同时为关

## 合成决策
- case_id: EDA-Eval-DesignFlow-OdtCtrlLogicAnalyze-001 (spice_sim L1, analysis Q&A → 生成式结构化 ODT 控制逻辑分析报告, A 档 trace-faithful + hidden B cross-input guard)
- A=doc/netlist (trace-faithful 重建 DqOutTopM6 ODT 区: 真实子电路名 DqFinalODTZq3/4/5/Pdmain CtrlSub1/2/3_New + 真实控制信号 OdtEn/OdtNTEn/MdOdt/MdOdtNT/WlvEn/DataEn + 真实使能 AllOdtNmosEnN/AllOdtPmosEnN + 真实门 aoi21x2_dq/oai31x2_dq/nor2x2/nor3x2/nand2x2/invx2/invx4/invx8 + 真实 ZQ 节点 ZqPd3/4/5/PdMain + 真实复位 NTODTNnRst + 真实 ZqN=tmfszqpd_intN<3..5> + 真实使能布尔式注释) + scenario.txt + task_spec.json
- hidden B=合成 DqDrvTopM8 ODT deck (不同顶层/4 个 DqOdtZq2/Pd CtrlSub1/2_New/2 挡 <0><1>/门集 invx4/invx16/nand3x2/nor2x2/aoi22x2/oai21x2/控制 OdtEn/OdtMode/WlEn/DataEn/OdtRstN/使能 OdtNmosEnN/OdtPmosEnN/ZQ 节点 ZqPd2+PdMain/rzqcal_intN), 单源手写 netlist
- 任务: 写 odt_ctrl_analyze.py(workdir,out_dir) 纯结构化 regex 解析 doc/netlist → odt_ctrl_analysis.json 17 顶层键
- check.py[21 断言]: zip含脚本+py_compile+SUT在B上subprocess exit0+合法JSON dict+17键+14字段cross-input(顶层/行数/子电路数/ODT子电路数/类别/门集/挡位/控制输入/使能名/ZQ节点/nmos/pmos计数 均vs独立解析B预期)+pmos/nmos逻辑含B专属token+A-leak守卫(18 A token禁现B输出)+确定性3 rerun sha256
- 自验: ref 21/21 PASS + 4 negs(空壳→无输出/print-only→无输出/hardcode-A→cross-input top_cell mismatch/deleted-core→subckt_count=0)全 FAIL; A/B 双跑确认 ref 通用解(A=DqOutTopM6/12 ODT/3挡, B=DqDrvTopM8/4 ODT/2挡); k_rationale==k_check==21
- 台账 mark besij→case · jsonl_B 378→379
