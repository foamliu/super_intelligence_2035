#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r836 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch11.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247)   r827 batch2 +12 (247->259)
        r828 batch3 +12 (259->271)   r829 batch4 +12 (271->283)
        r830 batch5 +12 (283->295)   r831 batch6 +12 (295->307)
        r832 batch7 +12 (307->319)   r833 batch8 +12 (319->331)
        r834 batch9 +12 (331->343)   r835 batch10 +12 (343->355, miss 52->40)
        本轮 batch11 = alphabetical 续 12 missing after SnmAnalyzerExplain-001-v2
        (r835 batch10 末位), 起算 SnmButterflyCalc, S->T 段.
        reframe_note 355->367, miss 40->28.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r836 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch11 12 case = 9 keep_reframe portability + 1 keep_reframe Q&A-analysis + 2 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe portability + 1 keep_reframe Q&A-analysis + 2 keep_faithful):
  - portability-driver (real sim deck/netlist/.lis/d.dir tree/sim env 不可沙盒复刻 -> synth_*):
      9 case: SnmButterflyCalc (real HSPICE .lis DC sweep 蝶形曲线数据不可复刻->synth_doc, spice_sim, L1) /
              Sp2tVerilogaSwitch (real Spectre sim env+PSF 二进制波形不可复刻->synth_doc, spice_sim, L2) /
              SpGen (real LDO netlist+HSPICE tran run 不可复刻->synth_deck, spice_sim, L2) /
              SpiceCfgDirMerge (real shdc+apps spice config dir tree 不可 scp 便携->synth_tree, spice_sim, L1) /
              SpiceFlowAuto (real AnasimPro sim dir+网表不可复刻->synth_deck, spice_sim, L2; **track=faithful 但 asset=synth_deck mismatch 待 @A**) /
              SpiceMeasInjector (real /proj slicer FineSim deck 不可复刻->synth_deck, spice_sim, L2) /
              SpiceParamSweepGen (real 模板 .sp+/proj 不可复刻->synth_deck, spice_sim, L2) /
              SpiceSim (real DDR4 P2S netlist+HSPICE run 不可复刻->synth_deck, spice_sim, L2) /
              SpiceTbGen (real hspiceD 网表不可复刻->synth_deck, spice_sim, L2)
  - Q&A-analysis-driver (原 trace 为 diagnosis/Q&A, reframe 为 produce-report 加 §4 牙):
      1 case: SpfMeasDiag (原「说明为什么 measure 不出来」纯诊断, reframe->produce diagnostic_report.json, real SPF/sim log 不可便携->synth_data, spice_sim, L2)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      2 case: SpRcAlterGen (用户显式要「改激励+两个文件 merge 用 .alter 跑」produce-action, real .sp 激励文本 scp 便携, asset=A-faithful, track=faithful, spice_sim, L1) /
              SpfAutosimSetup (用户显式要「迁移到 autosim 复跑」produce-action setup 脚本, real spf_extractor_config.json 文本便携, asset=A-faithful, track=faithful, characterization, L2)

S->T 段 domain-wave 观察: batch11 keep_faithful 占比 17%(2/12) 高于 batch8/batch10 P/S 段 8%, 与 batch7 N段 50% 相比仍偏低,
  因 S->T 段 Spice*/Sp* 群多为 real SPICE deck/netlist/.lis/sim dir 不可沙盒复刻 -> portability-heavy (9/12=75% portability, 与 batch10 S段持平);
  Q&A-analysis 1/12=8% (SpfMeasDiag 诊断) 反映 S->T 段含 diagnosis 真实用户意图;
  S->T 段 spice_sim 域占比 11/12=92% (仅 SpfAutosimSetup 为 characterization), 与 batch10 S段 83% 持平, S->T 段是 spice_sim 域主流段.
  track≠asset_provenance mismatch 累计: batch11 内 1 例(SpiceFlowAuto track=faithful asset=synth_deck), r835 累计 61 -> 62 待 @A 档2 sweep.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 标 L2 待复核(若 check 仅 subprocess 跑候选 python 生成/解析文本 0 EDA 二进制应 L1): Sp2tVerilogaSwitch/SpGen/SpiceMeasInjector/SpiceParamSweepGen/SpiceSim/SpiceTbGen/SpfAutosimSetup
    (SpiceFlowAuto/SpfMeasDiag 若真跑 HSPICE/FineSim 则 L2 合规)
  - k_check/k_rationale 缺标应补: SnmButterflyCalc=15/Sp2tVerilogaSwitch=14/SpGen=15/SpRcAlterGen=15/SpfAutosimSetup=12/SpfMeasDiag=10/SpiceCfgDirMerge=15/SpiceFlowAuto=8/SpiceMeasInjector=10/SpiceParamSweepGen=10/SpiceSim=10/SpiceTbGen=14
  - track 缺标应补(SpGen/SpfMeasDiag/SpiceMeasInjector/SpiceParamSweepGen/SpiceSim/SpiceTbGen track=None 应 synthesized; SpRcAlterGen/SpfAutosimSetup track=None 应 faithful; SpiceFlowAuto track=faithful 但 asset=synth_deck mismatch)
  - shard 缺标应 B (全 12 case shard=None)
  - 与 r773-r800/r826-r835 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-SnmButterflyCalc-001":
        "6T SRAM HSPICE .lis DC 扫描蝶形曲线 HSNM/RSNM 计算(两种 .lis 表格式: 按信号分块+合并表, R 曲线轴互换, 最大轴对齐内接正方形, 纯 Python 标准库)->produce (portability-driver reframe, real HSPICE .lis DC sweep 蝶形曲线数据不可沙盒复刻->synth_doc, §4 有牙必要, r836 reframe_note backfill batch11): 用户 e0030760@hfeg0pkn001 (sess 1794297017130_0uuj2, mc=259, spice_sim 域) 在 6T SRAM Solido Custom Output 流程中据 HSPICE .lis DC 扫描蝶形曲线数据计算 HSNM/RSNM(最大轴对齐内接正方形), 集成到 MC/HSV 仿真流程, 需支持两种 .lis 表格式(按信号分块+合并表), R 曲线做轴互换; A 不可行原因=real HSPICE .lis DC sweep 蝶形曲线仿真输出不可沙盒复刻(数量+体积+项目路径) -> 收敛为 snm_butterfly.py(读 hidden B synth .lis doc, asset_fidelity=synth_doc); reframe 由 portability-driver(real .lis 仿真输出不可复刻); 意图核心(两表格式 parse + 蝶形曲线提取 + R 曲线轴互换 + 最大轴对齐内接正方形 + HSNM/RSNM 计算 + 纯 Python 标准库)完整保留; check.py 15 断言验 zip 含 snm_butterfly.py + py_compile + 候选在 hidden B 上 exit0 + HSNM/RSNM 数值正确 + cross-input guard(A≠B .lis 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 解析 .lis 文本 0 EDA 二进制), level 缺标应 L1, k_rationale/k_check 缺标应 15, track=synthesized 一致 asset=synth_doc ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Sp2tVerilogaSwitch-001":
        "Verilog-A 理想 SP2T 开关模型(t<20ns COM↔OUT1 导通, 端口 COM/OUT1/OUT2/CTRL)+Spectre testbench 仿真验证->produce (portability-driver reframe, real Spectre sim env+PSF 二进制波形不可沙盒复刻->synth_doc, §4 有牙必要, r836 reframe_note backfill batch11): 用户 qiang3xu@hfeg0pkn005 (sess 1794398362877_7prw8, mc=881, spice_sim 域) USER 原话「veriloga 理想 SP2T 开关, 在 20ns 实现切换输入, 并仿真验证代码是否正确」; 真实助手探环境找到 Spectre 23.1.0.305+ahdl include 路径, 创建 sp2t_switch.va(Verilog-A 理想 SP2T 开关, t<20ns COM↔OUT1 导通)+test_sp2t.scs(Spectre testbench), 跑 Spectre 成功(0 errors/0 warnings/2 notices), 卡在 PSF 二进制波形提取; A 不可行原因=real Spectre sim 环境+PSF 二进制波形不可沙盒复刻 -> 收敛为 sp2t_switch.va+testbench 文本(asset_fidelity=synth_doc); reframe 由 portability-driver(real Spectre 环境+PSF 不可复刻); 意图核心(Verilog-A SP2T 开关模型 + t<20ns 切换逻辑 + COM/OUT1/OUT2/CTRL 端口 + testbench 结构 + 仿真可跑通验证)完整保留; check.py 14 断言验 zip 含 Verilog-A 开关模型 sp2t_switch.va + 端口齐全 + t<20ns 切换逻辑 + testbench + cross-input guard(A≠B 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 解析/校验文本 0 EDA 二进制应 L1; 若真跑 Spectre 则 L2), level 缺标, k_rationale/k_check 缺标应 14, track=design_flow 应复核(若资产 synth_doc 应 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpGen-001":
        "LDO 参考电路网表 tran testbench 生成(解析 .SUBCKT 头分类端口 power_rails/poweron/vss_*已接地/load_output, 生成 .sp: 电源 PWL 斜坡+PwrOn 斜坡+iload load/unload 阶跃+三个 .MEASURE 窗口, 真跑 HSPICE 报告 no-load/loaded/unloaded 电压)->produce (portability-driver reframe, real LDO netlist+HSPICE tran run 不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 tongni@hfeg0pkn003 (sess 1792724929127_2vuso, mc=468, spice_sim 域) 复用 sim-sp-gen DomainSkill 给 LDO 参考电路网表搭 tran testbench; 用户多轮迭代抓三条真实 bug: ①vss_AnlgRef 已和 vss 连一起不该外加电压源 ②Vcc 还没上电(电源斜坡必须先于 load step) ③iload 必须是阶跃; A 不可行原因=real LDO netlist+HSPICE tran 仿真运行不可沙盒复刻(项目路径+真跑) -> 收敛为 gen_sp.py(读 hidden B synth deck+netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+HSPICE run 不可复刻); 意图核心(.SUBCKT 头 parse + 端口分类 + 电源 PWL 斜坡先于 load + vss_* 已接地不外加 + iload 阶跃 + 三个 .MEASURE 窗口 + no-load/loaded/unloaded 电压)完整保留; check.py 15 断言验 zip 含 gen_sp.py 入口 + py_compile + 候选在 hidden B 上 exit0 产 .sp + .sp 含 .tran/.measure/PWL + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制应 L1; 若真跑 HSPICE 则 L2), level 缺标, k_rationale/k_check 缺标应 15, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceCfgDirMerge-001":
        "shdc+apps 两个 spice 配置目录树合并(按文件名列表对比差异+合并到 merged 保留层级结构+冲突文件加后缀备份)->produce (portability-driver reframe, real shdc+apps spice config dir tree 不可 scp 便携->synth_tree, §4 有牙必要, r836 reframe_note backfill batch11): 用户 chengk@hfeg0pgn022 (sess 1790576052982_qc0nn, mc=26, spice_sim 域)「读取 shdc 与 apps 两个 spice 配置目录, 按文件名列表对比差异、合并到 merged 并保留层级结构、冲突文件加后缀备份」; A 不可行原因=real shdc+apps 两套 spice 配置目录树不可 scp 便携(项目配置路径) -> 收敛为 spice_cfg_dir_merge.py(扫 hidden B synth_tree 两 fixture 目录, asset_fidelity=synth_tree); reframe 由 portability-driver(real config dir tree 不可 scp); 意图核心(两目录树遍历 + 文件名 diff + 合并到 merged 保留层级 + 冲突文件加后缀备份 + 幂等)完整保留; check.py 15 断言验 zip 含 spice_cfg_dir_merge.py + py_compile + 候选在隐藏 B 上 exit0 产 merged 树 + merged 层级保留 + 冲突文件后缀备份 + cross-input guard(A≠B tree 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 扫目录树 0 EDA 二进制), k_rationale/k_check 缺标应 15, track=synthesized 一致 asset=synth_tree ✓, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceFlowAuto-001":
        "AnasimPro SPICE 仿真全流程自动化 8 步(搭目录结构+分析网表 includes/model_paths/has_alter/has_end+生成 PVT 角点 .alter+构建 runsim.sh bsub 批量提交+提交监控 LSF+收集解析 measure measurement.json+生成跨角点 benchmark 对比报告 benchmark_report.json)->produce (portability-driver reframe, real AnasimPro sim dir+网表不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 sophiaw@hfeg0plg09 (sess 1789371142448_mw3vr, mc=28, spice_sim 域) 对仿真目录完成 8 步 SPICE 仿真管理流程; 用户消息自带 8 条结构化验收标准直接映射 check() 8 条断言; A 不可行原因=real AnasimPro 仿真目录+网表不可沙盒复刻 -> 收敛为 spice_flow_auto.py(读 hidden B synth_deck sim dir, asset_fidelity=synth_deck); reframe 由 portability-driver(real sim dir+网表不可复刻); 意图核心(8 步: 目录结构+网表分析+PVT alter 生成+runsim.sh+LSF 提交监控+measure 解析+benchmark 报告)完整保留; check.py 8 断言验 zip 含 spice_flow_auto.py + py_compile + 候选在 hidden B 上 exit0 + 8 步产物齐全(measurement.json/benchmark_report.json 等) + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成脚本/解析文本 0 EDA 二进制应 L1; 若真跑 LSF/HSPICE 则 L2), level 缺标, k_rationale/k_check 缺标应 8, **track=faithful 但 asset=synth_deck mismatch**(track≠asset_provenance, real sim dir 不可便携故 asset=synth_deck, track 应为 synthesized), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceMeasInjector-001":
        "DDR4 DFE slicer FineSim deck 注入 .measure 语句(测 XI7 整体电源功耗+测 1.53n 后 LDFEdataEr 第一个下降沿达 vvdd-0.36 时刻+测该时刻 outn_stg1/outp_stg1 电压, 复用已有 .meas AVG 窗口 10n-32*UI)->produce (portability-driver reframe, real /proj slicer FineSim deck 不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 jiangbaol@hfeg0pkn004 (sess 1794471761891_g0x1k, mc=838, spice_sim 域) 在 004_onlySlicer_delay_m2701.sp 中添加 .measure 语句: ①测 XI7 整体电源功耗(采样时间与已有功耗一致) ②测 1.53n 后 LDFEdataEr 第一个下降沿达 vvdd-0.36 时刻 ③测该时刻 outn_stg1/outp_stg1 电压; 助理解析已有 .meas AVG 窗口, 找 isub(XI7.XI_DqIbSAHFM6IP.inh_vcc) 路径, 注入 .probe/.meas 块; A 不可行原因=real /proj slicer FineSim deck 不可沙盒复刻(项目 /proj 路径) -> 收敛为 sp_meas_injector.py(读 hidden B synth deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck 不可复刻); 意图核心(读 deck + 找已有 .meas 窗口 + 注入 .measure 电源功耗 + 下降沿时刻 + 节点电压 + .probe 块)完整保留; check.py 10 断言验 zip 含 sp_meas_injector.py + 脚本在 hidden B 上 exit0 产注入后 deck + 注入 .measure 语句结构正确 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 注入文本 0 EDA 二进制应 L1; 若真跑 FineSim 则 L2), level 缺标, k_rationale/k_check 缺标应 10, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceParamSweepGen-001":
        "HSPICE 参数化仿真 deck 扫描生成(以 mixbest_V1_RBL_95_no_probe_I.sp 为模板, 9 变量 Sanadj1-4/Sapadj1-4 二值且相等+R_BL 15 值, 240 个 .sp 文件 16 文件夹×15 R_BL, + runsim_RBL_NxPx bsub+primesim 批量提交脚本)->produce (portability-driver reframe, real 模板 .sp+/proj 不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 vincentz@10.129.2.13 (sess 1794488236128_fhfno, mc=1456, spice_sim 域) 以 mixbest_V1_RBL_95_no_probe_I.sp 为基础模板, 要求生成 9 变量(Sanadj1-4/Sapadj1-4 二值且相等 + R_BL 15 值)的 240 个参数化 .sp 文件(16 文件夹×15 R_BL 值), 并生成 runsim_RBL_NxPx 脚本用 bsub+primesim 批量提交仿真; A 不可行原因=real 模板 .sp+/proj 路径不可沙盒复刻 -> 收敛为 sweep_generator.py(读 hidden B synth 模板 deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real 模板 .sp+/proj 不可复刻); 意图核心(模板 parse + 9 变量枚举 + Sanadj/Sapadj 二值且相等约束 + R_BL 15 值 + 240 文件生成 + 16 文件夹 + runsim bsub+primesim 脚本)完整保留; check.py 10 断言验 zip 含 sweep_generator.py + 在 hidden B 上 subprocess 真跑 exit0 + 生成文件数/结构正确 + cross-input guard(A≠B 模板不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制应 L1; 若真跑 primesim 则 L2), level 缺标, k_rationale/k_check 缺标应 10, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceSim-001":
        "DDR4 P2S predriver TX 链 tr/tf/duty 测量 HSPICE .measure deck 生成(给 netlist+MEAS_tr.sp+MEAS_skew.sp, tr 全测→tf 全测→duty 全测分组, 迭代管子尺寸满足 trtf<20ps/duty 50%±3%/skew<5ps)->produce (portability-driver reframe, real DDR4 P2S netlist+HSPICE run 不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 irene1li@hfeg0pkn004 (sess 1791523486486_ws2bi, mc=248, spice_sim 域) 给 netlist+MEAS_tr.sp+MEAS_skew.sp, 生成 HSPICE .measure deck, 要求 tr 全测→tf 全测→duty 全测分组, 迭代管子尺寸满足 trtf<20ps/duty 50%±3%/skew<5ps; A 不可行原因=real DDR4 P2S netlist+HSPICE 仿真运行不可沙盒复刻 -> 收敛为 gen_meas_deck.py(读 hidden B synth deck+netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist+HSPICE run 不可复刻); 意图核心(netlist parse + .measure deck 生成 + tr/tf/duty 分组 + 约束 trtf<20ps/duty 50%±3%/skew<5ps + 迭代 sizing)完整保留; check.py 10 断言验 zip 含 gen_meas_deck.py + ASCII-only(中文乱码→FAIL) + py_compile + 在 hidden B 上 exit0 产 deck + .measure 语句结构 + cross-input guard(A≠B deck 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制应 L1; 若真跑 HSPICE 则 L2), level 缺标, k_rationale/k_check 缺标应 10, track 缺标应 synthesized, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpiceTbGen-001":
        "SPICE testbench 生成(为 hspiceD 网表 INV/latch_t 生成综合 spice_testbench.sp: subckt 定义+电源+激励+.tran+.measure+.options+.temp+PVT corner)->produce (portability-driver reframe, real hspiceD 网表不可复刻->synth_deck, §4 有牙必要, r836 reframe_note backfill batch11): 用户 wzj@hfeg0pkn002 (sess 1794547157832_xhqs8, mc=499, spice_sim 域)「帮我生成一个 spice 的 testbench」, 为 INV/latch_t 等 hspiceD 网表生成综合 SPICE 测试台; 真实 trace 用 gen_spice_tb.py 生成 spice_testbench.sp; A 不可行原因=real hspiceD 网表不可沙盒复刻(项目路径) -> 收敛为 spice_testbench.sp 生成(读 hidden B synth DUT, A=3 级反相器链, B=NAND2+缓冲 网名/拓扑/器件全异, asset_fidelity=synth_deck); reframe 由 portability-driver(real hspiceD 网表不可复刻); 意图核心(testbench 结构: subckt 定义+电源+激励+.tran+.measure+.options+.temp+PVT corner + 可跑通 HSPICE V-2023.12 验证)完整保留; check.py 14 断言验 zip 含 spice_testbench.sp + .incl + .tran + .measure + .options + .temp + PVT corner + cross-input guard(A≠B DUT 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 生成/校验 deck 文本 0 EDA 二进制应 L1; 若真跑 HSPICE 则 L2), level 缺标, k_rationale/k_check 缺标应 14, track 缺标应 synthesized, shard 缺标应 B。",

    # ===== 1 keep_reframe_for_teeth (Q&A-analysis-driver) =====
    "EDA-Eval-DesignFlow-SpfMeasDiag-001":
        "FineSim PEX 后仿 inverter 电容 .meas 失败根因诊断(扁平 DSPF 1.3 仅 1 个 .SUBCKT PEX_CASE, 6 条 .meas 引用节点/子电路在 SPF 中不存在或层次不匹配, sim_inv_Rev03.log 报 measure failure)->produce-report (Q&A-analysis-driver reframe, 原 trace 纯诊断「说明为什么 measure 不出来」->produce diagnostic_report.json 加 §4 牙, real SPF 36895 行/sim log 不可便携->synth_data, r836 reframe_note backfill batch11): 用户 fan1yang@hfeg0plg104 (sess 1794461147267_g4ixv, mc=41, spice_sim 域) 原话「检查该目录下的 spf, sp 和 inv_03/sim_inv_Rev03.log 文件, 说明为什么 measure 不出来」针对 /rundata/lacaa/.../sim_inv/; 助手经 list_allowed_files/read_files/run_approved_command(写 check_meas.py 解析 SPF 36895 行)诊断: SPF 是扁平 DSPF 1.3 仅 1 个 .SUBCKT PEX_CASE(DIVIDER=./DELIMITER=:), 6 条 .meas 引用节点/子电路在 SPF 中不存在或层次不匹配; 意图形态=Q&A-diagnosis(原是「说明为什么 measure 不出来」纯讲解); A 不可行原因=Q&A 无 check 牙(纯讲解无法区分真假交付) -> 收敛为 diagnose_spf_meas.py+diagnostic_report.json(在 hidden B synth SPF/sim log 上重跑诊断, asset_fidelity=synth_data); reframe 由 Q&A-analysis-driver(原 Q&A→produce diagnostic_report.json 含 root_cause+evidence+failures); 意图核心(根因定位: 扁平 DSPF 格式 + .SUBCKT 单一 + .meas 引用节点/层次不匹配 + evidence: sim log measure failure + 6 条 .meas 逐条归类)完整保留; check.py 10 断言验 SPF 扁平 DSPF 判定(is_flat=True/format=DSPF/subckt_count) + report 合法 JSON + 候选在 hidden B 上重跑 exit0 复现诊断 + root_cause 与 oracle 一致 + cross-input guard(A≠B SPF 不同) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-report 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python 解析 SPF 文本 0 EDA 二进制应 L1; 若真跑 FineSim 则 L2), level 缺标, k_rationale/k_check 缺标应 10, track 缺标应 synthesized, shard 缺标应 B。",

    # ===== 2 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-SpRcAlterGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r836 reframe_note backfill batch11): 用户 victorq@hfeg0plg96 (sess 1793608841437_53e2m, mc=315, spice_sim 域) IGZO 1SC1LWL 结构 tWL 均匀性研究, U#1 原话「帮我改上述激励, SC 的参数和 pC 的参数是联动的, 大的 SC loading 匹配小的 PC loading, 小的 SC loading 匹配大的 PC loading, 保证 tWL 仿真均一性, 两种 RC 条件的 WL_len 都 sweep 1024 1536 256, 保存在原目录下面」, 随后追问「两个文件可以 merge 一起用 .alter 来跑吗?」; 真实助手先生成两个单条件 .sp(bigSC_smallpC.sp/smallSC_bigpC.sp), 再合并成 .alter 多 case deck; 意图形态=produce-action(改激励+.alter merge, A-档①verbatim 用户原话); 可便携性=高(real .sp 激励文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 sp_rc_alter_gen.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「改激励 SC/pC 联动+两文件 .alter merge」与 case 交付 sp_rc_alter_gen.py 产 .alter deck 同形映射, asset A-faithful 因 .sp 激励文本 scp 便携); check.py 15 断言验 zip 含 sp_rc_alter_gen.py + py_compile + 候选在 hidden B 上 exit0 产 .alter deck + .alter 语句结构 + SC/pC 联动约束 + WL_len sweep 1024/1536/256 + cross-input guard(A≠B 激励不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1, k_check=15==k_rationale=15 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本 0 EDA 二进制), level 缺标应 L1, k_check=15==k_rationale=15 ✓, track 缺标应 faithful(资产 A-faithful 一致), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-SpfAutosimSetup-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r836 reframe_note backfill batch11): 用户 e0046686@10.129.2.14 (sess 1794529802472_qcrl8, mc=189, characterization 域) 按 TASK_EXTRA_SPF_M4B4.md 分析执行: terminal 跑 2P PEX M4B4(1024x72)/M4B1(32x72) 多 PVT SPF 抽取(运行目录 pex420/pex1024x72, GloryEX_2026.06_P010, 廖建文 Rev07 PEX deck/lvs runset), 要迁移到 autosim 工具下复跑——分析 autosim 入参(MeasureFile/TemplateFile/TimingTransition/PVT/Param)及 spf_extractor_config.json(fs_dir/dbc_dir/lvs_rule 等)如何配置; 助手产 setup_2p_pex420.py(494 行幂等 patch, 60 OK/0 FAIL): patched spf_extractor_config.json; 意图形态=produce-action(setup 脚本+幂等 patch config, A-档①verbatim 用户原话+验收标准); 可便携性=高(real spf_extractor_config.json 文本 scp 便携, asset_fidelity=A-faithful, track=faithful); case 交付 setup_spf_autosim.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「迁移到 autosim 复跑+配置 spf_extractor_config.json」与 case 交付 setup_spf_autosim.py 幂等 patch config 同形映射, asset A-faithful 因 config.json 文本 scp 便携); check.py 12 断言验 zip 含 setup_spf_autosim.py 可执行 + py_compile + 候选在 hidden B 上 exit0 产 patched config + config 字段齐全(fs_dir/dbc_dir/lvs_rule/MeasureFile/TemplateFile/TimingTransition/PVT/Param) + 幂等(二次运行无 diff) + cross-input guard(A≠B config 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer=L2 待复核(若 check 仅 subprocess 跑候选 python patch JSON 文本 0 EDA 二进制应 L1; 若真跑 autosim/PEX 则 L2), level 缺标, k_check=12==k_rationale=12 ✓, track 缺标应 faithful(资产 A-faithful 一致), shard 缺标应 B。",
}


def main():
    applied = 0
    skipped = []
    for case_id, note in REFRAME_NOTES.items():
        path = os.path.join(CASES_DIR, f"{case_id}.json")
        if not os.path.exists(path):
            skipped.append((case_id, "MISSING FILE"))
            continue
        with open(path, "r", encoding="utf-8") as f:
            d = json.load(f)
        md = d.get("metadata", {})
        if "reframe_note" in md:
            skipped.append((case_id, "ALREADY HAS reframe_note"))
            continue
        # insert reframe_note as last metadata key, preserve existing order
        md["reframe_note"] = note
        d["metadata"] = md
        with open(path, "w", encoding="utf-8") as f:
            json.dump(d, f, ensure_ascii=False, indent=2)
        applied += 1
        print(f"  APPLY {case_id}")
    print(f"\nApplied: {applied} / Skipped: {len(skipped)}")
    for cid, why in skipped:
        print(f"  SKIP {cid}: {why}")


if __name__ == "__main__":
    main()
