#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r784 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r740_spotcheck19.tsv (batch18, 10 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r783 档3 batch9-17 done (reframe_note 32->107).
本轮 r784 档3 batch18 (r740 spotcheck19, 10 cases 待 apply). reframe_note 107->117.

reframe_note text = spotcheck19 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck19 10 keep_reframe):
  - foundry-PDK-unportable produce-action->produce-tool (portability-driver): 4 cases
    SlicerSizeOpt (jiangbaol@hfeg0pkn003, license-blocked) / SlicerSizingOpt (jiangbaol@hfeg0pkn002, foundry PDK+LSF) /
    CpIcpChar (wnyu@hfeg0pgn021, foundry PDK 双电压域厚氧管) / FineSimTbAuditFix (lanxinz@hfeg0pkn001, trace 无 runnable artifact + PDK)
  - analysis/Q&A->produce-tool 分析器 (Q&A-driver): 3 cases
    MR7PsdScopeAnalyze (tongfanl@hfhds201 DDR6 vecgen) / SiOutWarnDiag (zxtu@hfeg0pkn002, trace incomplete) /
    WtmWriteArrayScope (tongfanl@hfhds201 DDR6 vecgen)
  - produce-action skill/tb 生成->produce-tool (sub-skill 提取): 2 cases
    SpBisecDeckGen (adaml@hfeg0pkn002, 写 skill -> deck 生成器) /
    TspcTimingBisecTbGen (adaml@hfeg0pkn002, 生成 testbench -> tb 生成器, A 档不可行 U#133 给根因)
  - produce-action 调参->produce-tool 解析+规划子流 (portability-driver): 1 case
    OTATunePlan (zhukaic@hfeg0plg58, foundry PDK 不可便携, 抽取解析+规划子流不真跑 hspice)

tongfanl DDR6 vecgen 集群占 spotcheck19 2/10 (MR7PsdScopeAnalyze + WtmWriteArrayScope, both analysis/Q&A).
jiangbaol 同 user 同意图不同 host 不同 reframe 目标占 2/10 (SlicerSizeOpt + SlicerSizingOpt).
adaml skill/tb 生成占 2/10 (SpBisecDeckGen + TspcTimingBisecTbGen, both sub-skill 提取).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-MR7PsdScopeAnalyze-001":
        "DDR6 vecgen MR7 PSD0/PSD1 scope 分析器->produce-tool (analysis/Q&A->produce-tool 分析器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 tongfanl@hfhds201 原话「帮我看下，对于MR7，会区分PSD0或者PSD1吗？是不是只用设置PSD0即可，PSD1会和PSD0的保持一致」(analysis/Q&A 问答案, trace 金标准 1791958972412_xk1n1 mc506: MR7 不区分 PSD0/PSD1 只设一次, 证据 ddr6_specdef.sv:36 MODEMA_BITS=8 bit[7]=0 + ddr6_package.sv:487-491 MR7_zq_* in TYPE_modereg_direct + :585 注释 Direct address shared + ddr6_interface.sv:129 单份 modereg_direct), agent 在 trace 读 sv 诊断 PSD scope(文本答案)未产出结构化分析脚本; A 不可行原因=真实 vecgen 代码生产文件 SUT 沙盒不可达 -> 用真实 DDR6 vecgen sv 场景便携化为合成 fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「帮我看下...会区分吗」= 问答案), case 收敛为 produce-tool(写 analyze_mr7_psd_scope.py 真跑产 outB.json)给 check() 牙(§4.1 hidden-B cross-input guard B struct_name==TYPE_modereg_page0 ≠ A direct + shared==false ≠ A + §4.9 防硬编/防 print-expected); 重构为产 PSD scope 分析脚本+outB.json; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SiOutWarnDiag-001":
        "FineSim si.out warning 分类诊断器->produce-tool (analysis/Q&A + trace-incomplete->produce-tool 诊断器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 zxtu@hfeg0pkn002 原话「分析这个报告的warnning：finesim.golden004_all_perbank_daily_4b4g_.../si.out」(analysis/Q&A 分析给答案, trace 实为 agent 在文件系统定位 si.out 未果的 file-search saga, 从未读到文件 trace incomplete), 便携子技能=si.out 单文件 warning/error/fatal 按 8 类分类 + 每条结构化 + summary; A 不可行原因=trace 不完整(agent 从未读到 si.out, file-search saga) -> case 收敛为 produce-tool(写 si_out_warn_diag.py 诊断器真跑产 diagnostic_report.json), B 档 synthesized 合规(§3 允许 A 档不可行时 B 档), reframe 由 trace 不完整驱动非配额驱动; 用真实 si.out 格式场景便携化为合成 fixture(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「分析...warnning」= 分析给答案), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B summary.total==20 + by_severity{warning:17,error:2,fatal:1} + outcome==aborted ≠ A + §4.9 防硬编); 重构为产 si_out_warn_diag.py+diagnostic_report.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SlicerSizeOpt-001":
        "strongarm DQ-slicer 约束 sizing 优化器->produce-tool (portability+license-blocked produce-action->produce-tool 优化器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 jiangbaol@hfeg0pkn003 原话「调节 strongarm DQ-slicer 的 pmos/nmos/itail/in width+finger 8 参数, 使 Cur_slicer_latch_avg @ TT_1V_45 <= 380uA, 同时最小化 slicer2nd_dly_r0/slicer2nd_dly_r1」(produce-action 调参优化, trace 末尾卡 FineSim license 无用户接受产物 trace incomplete/license-blocked), 合成金标准=便携 model-free strongarm + hspice sweep 选优; A 不可行原因=trace 不完整 + FineSim license 阻塞 + foundry PDK 不可便携 .75 -> case 收敛为 produce-tool(写 slicer_size_opt.py 优化器真跑 HSPICE sweep 产 opt_result.json), B 档 synthesized 合规, reframe 由 trace incomplete+license-blocked 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); trace 用户=produce-action(「调节...使...」= 调参优化), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B hspice_ran==True + best_cur_avg<=current_limit + §4.9 防 A knob 名泄漏); 重构为产 slicer_size_opt.py+opt_result.json; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(license 阻塞无法交付)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SlicerSizingOpt-001":
        "StrongARM slicer 约束 sizing 优化器->produce-tool (portability produce-action->produce-tool 优化器 reframe + 二次 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 jiangbaol@hfeg0pkn002 原话「根据 .sp 调 pmoswidth/nmoswidth/itailwidth 使 Cur_slicer_latch_avg ≤380uA，使 slicer2nd_dly_r0/r1 最小」(produce-action 调参优化, trace agent 写 sa_submit/sa_wait/sa_collect 脚本 bsub finesim 跑参数扫描 → FineSim FSPRO license daemon down 阻塞, 仅交付基线 350uA<380✓/dly=46/45ps+脚本, 未测最优 sizing), trace 走 foundry PDK+LSF+FineSim 不可便携 .75; A 不可行原因=foundry PDK+LSF+license 不可便携 .75 -> case 收敛为 produce-tool(写优化器真跑 HSPICE sweep), B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; 二次 reframe(原 level-1 StrongARM 再生失败 cur=-3.99nA+dly failed → 5 级电流饥饿型反相器链); asset_fidelity=synth_deck ✓; layer=L2 ✓(已标, check 真跑 HSPICE); trace 用户=produce-action(「调...使...」= 调参优化), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B baseline cur 偏差<5% + best_run.cur<=budget + §4.9 budget 取自 spec_B 反硬编); 重构为产优化器+sweep_results.csv; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(license down 无法交付)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-OTATunePlan-001":
        "五管 OTA 自动调参解析+规划子流->produce-tool (portability produce-action->produce-tool 解析+规划子流 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 zhukaic@hfeg0plg58 原话读 ota.md skill 后「开始执行」自动调参五管 OTA(gain>38dB/PM>60°/GBW>200MHz, 可调 XMMN0/1/XMMP0/1 的 w/l, finger max=7.8u/min=200n, 3 次 w/l 迭代 + 1 次偏置电流 2~4uA 杠杆, trace agent 4 轮迭代 × 并行 2 仿真 = 8 次 hspice 全部成功, 基线 34.72dB/56.96°/273.3MHz → 终版 i4a gain=38.10✓/PM=65.00✓/GBW=178.4✗ 尾电流镜钳位), A 不可行原因=foundry PDK 不可便携 .75 -> case 抽取「解析基线 .lis + 建模型 + 设计首轮并行试验 + 出优化网表与报告」子流, 不要求 SUT 真跑 hspice(PDK 不在沙盒), 用隐藏 B .lis 防硬编码, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck(待 @A apply 档2); trace 用户=produce-action(「开始执行」自动调参 = 调参优化), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B gain_db/pm_deg/gbw_hz 与 check 独立解析 B 一致 |Δ|<=0.5dB/1°/5% + §4.9 trial_plan ≥2 trial 含 xmmn_l/xmmp_l/i_bias 在 [200n,7.8u]/[2u,4u]); 重构为产 parse_lis.py+trial_plan.json+proposed_netlist.sp+analysis_report.txt; check.py 10 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(PDK 不可便携无法真跑)无法有牙 => 收敛为 produce-tool 子流提取是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误标应改 L1(check 仅 subprocess 跑候选 python 解析 .lis, 不启动 HSPICE), metadata bug 待 @A apply 档1 补。",
    "EDA-Eval-DesignFlow-WtmWriteArrayScope-001":
        "DDR6 vecgen WTM write-to-array scope 分析器->produce-tool (analysis/Q&A->produce-tool 分析器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 tongfanl@hfhds201 原话「帮我分析下这个环境，并回答：当进入WTM 模式时，发送write命令，会不会把数据发到array里去？」(analysis/Q&A 问答案, trace 金标准 1792033394584_xd7ut mc1379127: WTM 模式下 write 命令会把数据写入 array, 因 write_mem_arr 的门控 if 只跳过 Write_Leveling_Training 未含 Write_Training_Mode, 证据 ddr6_test.sv:1548 write_mem_arr 调用 + :1537 门控 if(!nt&!cmd_ignore&...&!(`mr_da.MR5_func_mode==Write_Leveling_Training)) + ddr6_package.sv:387 WTM 枚举), agent 在 trace 读 sv 诊断(文本答案: 会写入 array)未产出结构化分析脚本; A 不可行原因=真实 vecgen 代码生产文件 SUT 沙盒不可达 -> 用真实 DDR6 vecgen sv 场景便携化为合成 fixture 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analysis/Q&A(「帮我分析下...并回答...会不会」= 问答案), case 收敛为 produce-tool(写 analyze_wtm_write_array.py 真跑产 outB.json)给 check() 牙(§4.1 hidden-B cross-input guard B write_mem_arr_call.line>0 + gating_if.line>0 非 distractor 误命中 + wtm_in_skip_modes==True + write_goes_to_array_in_wtm ≠ A + §4.9 防硬编); 重构为产 WTM write array scope 分析脚本+outB.json; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 analysis/Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: mc=1379127 极高(mega/noisy session), 观察。",
    "EDA-Eval-DesignFlow-CpIcpChar-001":
        "PLL 电荷泵 Icp 表征 + 偏置管工作区分类器->produce-tool (portability produce-action->produce-tool 表征器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 wnyu@hfeg0pgn021 原话「搭建并调通PLL的CP模块...整理一个表格」(produce-action 表征 + 产表格, trace agent 用 HSPICE .op/.tran 迭代 sizing/bias, 逐管判定工作区, U83 用户接受 Icp 每档位电流表, 覆盖 0.85V 与 1.8V 双电压域厚氧管 PVT 遍历), trace 走 foundry PDK(cxmtG6_1C2A p25ud18_ckt/ptn_lv)+多电压域厚氧管不可便携 .75; A 不可行原因=foundry PDK 不可便携 .75 -> 提取「CP Icp 表征 + 偏置管工作区分类(sat/lin/cut)+accept 判定」子技能, DUT level-1 Shichman-Hodges MOS, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓; layer=L2 ✓(已标, check 真跑 HSPICE); trace 用户=produce-action(「搭建并调通...整理一个表格」= 表征 + 产表格), case 收敛为 produce-tool(写 cp_char.py 表征器真跑 HSPICE 产 char_table.csv+report)给 check() 牙(§4.1 hidden-B cross-input guard B 各档位 Iup/Idown 偏差<10% + 偏置管 mpsrc 分类为 triode(lin) 检出非饱和陷阱 + B 管子名非 A + accept==False + §4.9 name-agnostic + spec_B 反硬编 + 交叉重跑 A→A accept==True); 重构为产 cp_char.py+char_table.csv+report; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(PDK 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-FineSimTbAuditFix-001":
        "FineSim testbench 静态审计 + 三类错误修复器->produce-tool (portability+trace-no-artifact produce-action->produce-tool 审计修复器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 lanxinz@hfeg0pkn001 原话对 cline 提 FineSim testbench 审阅请求: 审阅 run + sim_TT25c0.94v.sp, 若有语法错误则重新生成修改版 testbench(produce-action 审阅+修复, 原 trace DRAM RowPreDec hspice 多轮分析性输出无 runnable artifact 违反 design_flow submit.zip 契约), 提取「FineSim testbench 静态审计 + .param/.probe/冗余 Vsrc 三类错误修复 + 仿真器真跑验证」子技能, DUT level-1 Shichman-Hodges 反相器/NAND2 链(.75 无 foundry PDK), FineSim -spice 真跑; A 不可行原因=trace 无 runnable artifact + foundry PDK 不可便携 -> case 收敛为 produce-tool(写 tb_audit_fix.py 审计修复器真跑 FineSim 验证), B 档 synthesized 合规, reframe 由 trace 无 artifact + portability 驱动非配额驱动; asset_fidelity=synth_deck ✓; layer=L2 ✓(已标, check 真跑 FineSim); trace 用户=produce-action(「审阅...若有语法错误则重新生成修改版」= 审阅+修复), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B original log 含 FineSim 真跑签名 + 'unresolved condition' abort + 修改版不含 '.probe v()' 空选择子 + 修改版 B Successfully Completed ≠ A + §4.9 反 6 假提交); 重构为产 tb_audit_fix.py+修改版 testbench; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(无 artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SpBisecDeckGen-001":
        "HSPICE 内建 bisection deck 生成器->produce-tool (sub-skill 提取 produce-action 写 skill->produce-tool deck 生成器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 adaml@hfeg0pkn002 原话 U#3「调用这个 skill 的时候, 发现 skill 没有充分考虑 EDA 仿真器自身的能力...仿真器自带 bisection 优化, 调用后没有用这个方案, 反而用 sh 脚本做分析。针对这个情况, 更新 skill, 要求写激励和做分析的时候, 首先检查仿真器是否有内建的功能」(produce-action 写/更新 skill, trace agent 读真实 .sp 范例+HSPICE manual 产 SKILL.md 13-section + references), 本 case 抽取「内建 bisection deck 生成器」子技能; A 不可行原因=produce-action 写 skill 文档非 design_flow submit.zip 契约的交付物 -> case 抽取子技能(写 skill → 写 deck 生成工具), B 档 synthesized 合规, reframe 由 子技能提取 驱动非配额驱动; asset_fidelity=synth_deck(待 @A apply 档2); layer=L1 ✓(已标, check 仅 subprocess 跑候选 python 生成 deck 文本, 不启动 HSPICE); trace 用户=produce-action(「生成 skill」「更新 skill」= 写/更新 skill 文档), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B1/B2 cross-input guard B1 deck 含 .param Opt1 + sweep optimize + .measure goal + .MODEL optmod opt method=bisection + B1 搜索参数 ClkSkew 非 A DelayTime + B1 不含外部 sh 循环 ≠ A + §4.9 反硬编 A); 重构为产 bisec_deck_gen.py+out_deck.sp; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(写 skill 文档非 runnable artifact)无法有牙 => 收敛为 produce-tool 子技能提取是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TspcTimingBisecTbGen-001":
        "TSPC_RVT setup/hold bisection testbench 生成器->produce-tool (sub-skill 提取 + A 档不可行 produce-action->produce-tool tb 生成器 reframe, §4 有牙必要, r740 spotcheck batch18): 用户 adaml@hfeg0pkn002 原话 U#1/U#10「生成 spice 仿真激励, 通过 hspice 仿真 check 这个电路的 setup/hold time, 以及 tCLK2Q。并且优化电路内部的晶体管的尺寸」+ U#28「提取方法用 bisection 的仿真方法来做」+ U#133「我强调一遍, hspice 自带 bisection 的仿真优化方案」(produce-action 生成 testbench, trace agent 产 6 个 testbench + measure_chk.sp + parse_mt0.py, 先写外部 bash/LSF bisection 循环被 U#133 纠正后改写为原生 hspice bisection .MODEL OPT METHOD=BISECTION), 本 case 取 setup/hold bisection testbench 生成结构; A 不可行原因=U#133 给根因(§A-② 排除 A 档) -> case 抽取子技能(写 testbench → 写 tb 生成器), B 档 synthesized 合规, reframe 由 子技能提取 + A 档不可行 驱动非配额驱动; asset_fidelity=synth_deck ✓; layer=L1 ✓(已标, check 仅 subprocess 跑候选 python 生成 tb 文本, 不启动 HSPICE); trace 用户=produce-action(「生成 spice 仿真激励...check setup/hold...用 bisection」= 生成 testbench), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B1/B2 cross-input guard B1 env 块 .temp/.lib/.param pvcc 与 spec_b1 一致 + bisection .param Opt1 name+三值与 spec_b1 一致(tsu/150p/-50p/350p 非 A 200p/0/400p) + .meas q_chk FIND GOAL + .tran SWEEP OPTIMIZE + .MODEL optmod OPT METHOD=BISECTION ≠ A + §4.9 反硬编 A + 确定性 B1 两次 byte-identical); 重构为产 tspc_timing_bisec_tb_gen.py+out_tb.sp; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(写 testbench 文档非 runnable artifact)无法有牙 => 收敛为 produce-tool 子技能提取是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-MR7PsdScopeAnalyze-001": "analysis/Q&A->produce-tool 分析器",
    "EDA-Eval-DesignFlow-SiOutWarnDiag-001": "analysis/Q&A + trace-incomplete->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-SlicerSizeOpt-001": "portability+license-blocked produce-action->produce-tool 优化器",
    "EDA-Eval-DesignFlow-SlicerSizingOpt-001": "portability produce-action->produce-tool 优化器 (二次 reframe)",
    "EDA-Eval-DesignFlow-OTATunePlan-001": "portability produce-action->produce-tool 解析+规划子流",
    "EDA-Eval-DesignFlow-WtmWriteArrayScope-001": "analysis/Q&A->produce-tool 分析器",
    "EDA-Eval-DesignFlow-CpIcpChar-001": "portability produce-action->produce-tool 表征器",
    "EDA-Eval-DesignFlow-FineSimTbAuditFix-001": "portability+trace-no-artifact produce-action->produce-tool 审计修复器",
    "EDA-Eval-DesignFlow-SpBisecDeckGen-001": "sub-skill 提取 produce-action 写 skill->produce-tool deck 生成器",
    "EDA-Eval-DesignFlow-TspcTimingBisecTbGen-001": "sub-skill 提取 + A 档不可行 produce-action->produce-tool tb 生成器",
}


def apply_one(case_id, note):
    path = os.path.join(CASES_DIR, case_id + ".json")
    if not os.path.exists(path):
        return ("MISSING", path)
    with open(path, "r", encoding="utf-8") as f:
        raw = f.read()
    d = json.loads(raw)
    m = d.get("metadata", {})
    if "reframe_note" in m:
        return ("ALREADY", case_id)
    m["reframe_note"] = note
    d["metadata"] = m
    out = json.dumps(d, ensure_ascii=False, indent=2)
    json.loads(out)  # verify parseable
    with open(path, "w", encoding="utf-8") as f:
        f.write(out)
    return ("OK", case_id)


def main():
    print(f"=== r784 batch18 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 107 + {counts['OK']} = {107 + counts['OK']}")


if __name__ == "__main__":
    main()
