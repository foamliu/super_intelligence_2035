#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r780 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r735_spotcheck14.tsv (batch14 part1, 2 keep_reframe cases)
      + designflow/intent_audit_B_r736_spotcheck15.tsv (batch14 part2, 11 keep_reframe cases).
Spec: r771 bounded queue 档1→档3→档2. r772 档1 done. r773-r779 档3 batch9-13 done (reframe_note 32→80).
本轮 r780 档3 batch14 (r735 spotcheck14 + r736 spotcheck15, 13 cases). reframe_note 80→93.

reframe_note text = spotcheck14/15 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False, round-trip identical 验过.

Driver 分类 (per per_case_reasoning):
  spotcheck14 (2 cases):
    - portability + Q&A 咨询→produce-tool 修复器: 1 case (FineSimDcConvFix, t0002441 问 DC 不收敛原因+方案→写 fixer.py)
    - portability + produce-action 仿真迭代→produce-tool 测量 deck 生成: 1 case (TrtfMeasDeckGen, irene1li 跑仿真迭代+读 FSDB→写 gen_trtf_meas.py 生成测量 deck)
  spotcheck15 (11 cases, tongfanl DDR6 DSCQA vecgen cluster 10 + e0030760 1):
    - portability + explain/understand→produce-tool 解析器: 1 case (SpDeckStructExtract, e0030760)
    - portability + review→produce-tool 审查器: 4 cases (WtmStructReview/PoststressTbAudit/WtmFileReview/WtmPatternDirReview, tongfanl WTM/pattern review)
    - portability + Q&A 找值→produce-tool 定位器: 1 case (TzqlatLocate, tongfanl 查 tZQLAT)
    - portability + debug-Q&A→produce-tool 诊断器: 3 cases (DatatPrintOrderDiag/LoadModeOpTruncDiag/StimOp2MisMatchDiag, tongfanl debug-Q&A)
    - portability + explain→produce-tool 提取器: 1 case (MrrTaskSignatureExtract, tongfanl explain task MRR 书写逻辑)
    - portability + analyze→produce-tool 分析器: 1 case (ZqPatternTimingAnalyze, tongfanl analyze pattern timing)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-FineSimDcConvFix-001":
        "FineSim DC 不收敛诊断+修复器->produce-tool (portability+Q&A 咨询->produce-tool 修复器 reframe, §4 有牙必要, r735 spotcheck batch14): 用户 t0002441@hfhds201 问「Finesim仿真报DC不收敛的错误,可能的原因及解决方案有哪些?」(纯 Q&A 咨询), agent 在 trace 查 FineSim 官方文档整理 DC 收敛选项全集未产出结构化修复脚本; A 不可行原因=真实 FineSim 环境+生产仿真日志 SUT 沙盒不可达 -> 用自包含合成 FineSim DC 不收敛日志+网表资产保留真实任务结构(asset_fidelity=synth_deck 已标); trace 用户=Q&A 咨询(问原因+方案), case 收敛为 produce-tool(写 fixer.py 修复器+diagnosis.json, 检测日志 non-converg 标记->替换弱 dcalg=1/gmin=0/itl1=5 选项为鲁棒 dcalg=4 伪瞬态->重跑验证收敛)给 check() 牙(§4.2 subprocess 跑候选 python + judge 独立重跑 FineSim -spice 验 'Successfully Completed' + §4.1 hidden-B cross-input guard + name-agnostic + sanity 反 always-pass); 重构为产 fixer.py+diagnosis.json; check.py 14 断言验 弱选项词边界匹配+鲁棒选项注入+judge FineSim 重跑收敛+hidden-B cross-input guard 使纯 Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TrtfMeasDeckGen-001":
        "P2S TX trtf 测量 deck 生成->produce-tool (portability+produce-action 仿真迭代->produce-tool 测量 deck 生成 reframe, §4 有牙必要, r735 spotcheck batch14): 用户 irene1li@hfeg0pkn004 有 finesim 仿真激励 deck(test_dout.sp, P2S TX 主体+predrv+zqcode+FFE/AC boost, 7 corner .alter), 要求仿真迭代出一版符合 trtf(10%-90%) 要求的主体电路, 关心所有管子的 trtf duty; agent 在 trace 用 fscript 读 FSDB 波形+_measure_allmain.py 计算 44 节点 tr/tf/duty; A 不可行原因=真实 FineSim 仿真迭代+FSDB 波形读取环境 SUT 沙盒不可达 -> 用自包含合成 test_dout.sp deck 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=produce-action(跑仿真迭代+读 FSDB 验 trtf), case 收敛为 produce-tool(写 gen_trtf_meas.py 生成测量 deck+parse_trtf.py 解析+report.md, 不真跑 FineSim 迭代+不读 FSDB)给 check() 牙(§4.2 subprocess 跑候选 python 生成 .sp 文本+解析样本 .lis); 重构为产 gen_trtf_meas.py+_meas.sp+parse_trtf.py+report.md; check.py 12 断言验 tr/tf 0.1/0.9 阈值(10%-90% 非 50%-50%)+保留 B .tran/.alter/.inc+parse_trtf.py 正则提取+report.md 列所有 B 节点使原 produce-action 无法有牙(无法真跑 FineSim 迭代+读 FSDB) => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-SpDeckStructExtract-001":
        "6T SRAM HSPICE deck 结构解析->produce-tool (portability+explain/understand->produce-tool 解析器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 e0030760@hfeg0pkn004 原话「/proj/.../6T_SRAM_HC_CH336.sp 帮忙理解下这个文件内容」(纯 explain/understand 请求), agent 在 trace 用 read_files 读 deck(103 行)+被 .include netlist(6T 7 端口+9 实例+12 Solido MC 旋钮), 给结构解释(文本答案)未产出结构化解析脚本; A 不可行原因=真实 HSPICE deck+netlist 生产文件 SUT 沙盒不可达 -> 用自包含合成 6T_SRAM_HC_CH336.sp deck+BitCell_FS_CH336.netlist 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=explain/understand(「理解下这个文件内容」), case 收敛为 produce-tool(写 parse_sp_deck.py 解析器+out.json, 解析 .include netlist+14 NODESET+7 measure+12 MC 旋钮+9 XI 实例)给 check() 牙(§4.2 subprocess 跑候选 python 解析 B + §4.1 hidden-B cross-input guard B 8T 9 端口+16 NODESET+8 measure 击穿硬编 A + name-agnostic + B subckt/measure/nodeset 集合精确匹配); 重构为产 parse_sp_deck.py+out.json; check.py 15 断言验 hidden-B cross-input guard+B subckt/measure/nodeset 集合精确匹配+name-agnostic 使纯 explain 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-WtmStructReview-001":
        "DDR6 WTM 训练模式 stimulus Verilog 静态结构审查->produce-tool (portability+review->produce-tool 审查器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「WTM001_normal_check.v WTM002_normal_check.v 检查下有没有问题，不要改动」(纯 review 请求), agent 在 trace 用 read_files 读两文件给 8 条结构审查发现(文本答案)未产出结构化审查脚本; A 不可行原因=真实 WTM001/WTM002 .v 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM001/WTM002 .v excerpt 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=review(「检查下有没有问题」= 找问题给答案), case 收敛为 produce-tool(写 review_wtm.py 审查器+out.json, 检查 2-iter/6-iter loop+MRSetting 位置+op_mark 宽度+nnop/error_write 字面量)给 check() 牙(§4.2 subprocess 跑候选 python 静态分析文本 + §4.1 hidden-B cross-input guard B1 3-iter loop+MRSetting in loop+narrow op_mark / B2 4-iter loop+MRSetting after end+8hff full op_mark+nnop_unused+$urandom->error_write+Write[6][7] 打破交替 vs A 不同 issue 组合 + name-agnostic); 重构为产 review_wtm.py+out.json; check.py 15 断言验 hidden-B cross-input guard+name-agnostic+issue 集合精确匹配使纯 review 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-PoststressTbAudit-001":
        "DDR6 Poststress 文件夹与 TB 环境对应关系审计->produce-tool (portability+review/audit->produce-tool 审计器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「帮我检查下...是否对应，能否实现相应的目的」(纯 review/audit 请求), agent 在 trace 解析符号链接+cfg_Aging+d6vecgen 消费链, 发现 cfg_Aging line21 激活 Poststress001_Perbank_Datapath 但实际文件 Dualbank 且 bank=2b 不一致(文本答案)未产出结构化审计脚本; A 不可行原因=真实 Poststress/ 文件夹+verilog.ddr6.dscqa.vecgen_local cfg 生产文件 SUT 沙盒不可达 -> 用自包含合成 Poststress/ 文件夹+vecgen_local cfg 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=review/audit(「检查下是否对应」), case 收敛为 produce-tool(写 audit_poststress_correspondence.py 审计器+out.json, 解析符号链接+cfg 激活+Perbank vs Dualbank 不一致)给 check() 牙(§4.2 subprocess 跑候选 python 静态审计文本 + §4.1 hidden-B cross-input guard B poststress_B+tb_B 8 .v 文件+include_refs+cfg_entries active_count==2+mismatches); 重构为产 audit_poststress_correspondence.py+out.json; check.py 14 断言验 hidden-B cross-input guard+cfg_entries active_count+mismatches 使纯 review 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TzqlatLocate-001":
        "DDR6 tZQLAT 参数硬编码值定位->produce-tool (portability+Q&A 找值->produce-tool 定位器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「帮我看下环境里 ZQLAT命令到下一个Valid Command的时间tZQLAT是多少」(纯 Q&A 找值), agent 在 trace 用 search_codebase/read_files/grep 跨 4 文件(ddr6_package.sv:3090 声明+timing_load.sv:1237 max_val(30000,4*tCK)+1423 最终赋值+ddr6_specdef.sv:2059)定位给 30ns 答案(文本答案)未产出结构化定位脚本; A 不可行原因=真实 vecgen_local 4 .sv 生产文件 SUT 沙盒不可达 -> 用自包含合成 vecgen_local 4 .sv 文件资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=Q&A 找值(「tZQLAT是多少」), case 收敛为 produce-tool(写 locate_tzqlat.py 定位器+out.json, 跨文件定位 declaration/min_assignment/final_assignment/opcode/max_val_function/timing_table_reads/hardcoded/computed_value)给 check() 牙(§4.2 subprocess 跑候选 python 静态定位文本 + §4.1 hidden-B cross-input guard B_vecgen 合成+declaration.file=='ddr6_package.sv' 且 comment 含 'ZQCAL latch' + 顶层键集精确匹配); 重构为产 locate_tzqlat.py+out.json; check.py 17 断言验 hidden-B cross-input guard+declaration.file+顶层键集精确匹配使纯 Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-DatatPrintOrderDiag-001":
        "DDR6 WTM DATAT 打印序 vs 波形序反序诊断->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「为什么xrun.log中的DATAT0（3189行）和波形中的数值对不上」(debug-Q&A 找根因), agent 在 trace 用 read_files/grep 读 WTM001_normal_check.v+ddr6_tasks.sv, 发现 gen_wtm_write_data 打印循环 for(j=23;j>=0;j--) 递减先打印 UI23 而 loaddq_fifo 装载 for(i=0;i<bl;i++) 递增 UI0 先上引脚->DATAT 打印序与波形时间序镜像反序, Python 逐位复算两组 DATAT0 与日志 3189/3315 行完全一致(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 WTM004 path+xun.log+stimulus.vec 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM004 path+xun.log+stimulus.vec 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A 找根因(「为什么对不上」), case 收敛为 produce-tool(写 diag.py 诊断器+out.json, 解析 print_loop.direction/fifo_load.direction/datat_vs_waveform)给 check() 牙(§4.2 subprocess 跑候选 python 静态诊断文本 + §4.1 hidden-B cross-input guard B_wtm print_loop.direction=='ascending'+first_ui==0 vs A 递减+fifo_load.direction=='ascending'+datat_vs_waveform); 重构为产 diag.py+out.json; check.py 14 断言验 hidden-B cross-input guard+print_loop.direction+fifo_load.direction+datat_vs_waveform 使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-LoadModeOpTruncDiag-001":
        "DDR6 Load_Mode OP 位宽截断诊断->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「Load_Mode(.ma(8'hDE), .op({4'b0000,1'b1,1'b1,$urandom_range(1),pattern_select}),...); 帮我看下pattern中的这句话，没有把DE寄存器的OP3为正确设为1，这是为啥？」(debug-Q&A 找根因), agent 在 trace 诊断: $urandom_range(1) 返回 32-bit int, 拼接 {4'b0000,1'b1,1'b1,$urandom_range(1),pattern_select}=39bits>MODEOP_BITS(8) 截断预期 1'b1 位(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 pattern.v+specdef 生产文件 SUT 沙盒不可达 -> 用自包含合成 pattern.v+specdef 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A 找根因(「为啥」), case 收敛为 produce-tool(写 diag_loadmode_op_trunc.py 诊断器+out_B, 解析 loadmode_call/ma/op_raw/elements/total_width/modeop_bits/truncated/conclusion)给 check() 牙(§4.2 subprocess 跑候选 python 静态诊断文本 + §4.1 hidden-B cross-input guard B_pattern.v+8 顶层键+modeop_bits==8 从 B_specdef 解析+cast_urandom width==1+total_width==8+truncated); 重构为产 diag_loadmode_op_trunc.py+out_B; check.py 14 断言验 hidden-B cross-input guard+modeop_bits 从 B_specdef 解析+total_width+truncated 使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-MrrTaskSignatureExtract-001":
        "DDR6 task MRR 签名/结构提取->produce-tool (portability+explain->produce-tool 提取器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「/proj/dscqa/.../verilog.ddr6.dscqa.vecgen_local 分析一下上述路径，告诉我task MRR的书写逻辑」(explain/Q&A), agent 在 trace 定位 MRR task 定义(~line 2823), 提取 15 参数签名+begin:MRR_task 块 19 局部变量+3 TODO+子 task 调用链(文本答案)未产出结构化提取脚本; A 不可行原因=真实 ddr6_test.sv MRR task 生产文件 SUT 沙盒不可达 -> 用自包含合成 ddr6_test.sv MRR task 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=explain(「告诉我书写逻辑」), case 收敛为 produce-tool(写 extract_mrr_task_meta.py 提取器+out_B, 提取 task_name/param_count/begin_block_name/local_vars/todo_comments/called_tasks/has_endtask)给 check() 牙(§4.2 subprocess 跑候选 python 静态提取文本 + §4.1 hidden-B cross-input guard B_test.sv 合成 WR task+task_name=='WR' 挡硬编 MRR+param_count==8 挡硬编 15+begin_block_name+local_vars+todo_comments+called_tasks+has_endtask); 重构为产 extract_mrr_task_meta.py+out_B; check.py 16 断言验 hidden-B cross-input guard+task_name 挡硬编+param_count 挡硬编+子 task 调用链使纯 explain 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-ZqPatternTimingAnalyze-001":
        "DDR6 ZQ001 pattern timing 关系分析->produce-tool (portability+analyze->produce-tool 分析器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话粘贴完整 ZQ001_normal_check pattern task+「帮我看下在该环境下，跑pattern：...」(analyze/Q&A), agent 在 trace 拆解 11 步(CLK_SYNC_OFF+250ns DeselectT/ZQCal Latch clear/Active->Write/ZQ Reset MR7 OP[2]+750ns/MRSetting OP[0]/OP[1] ZQ Initiation/MRR(MR7) 读 ZQUF/Active->Read DQ error(ZQUF=1)/Active->Read DQ pass(ZQUF=0)/ZQ Stop MR7 OP[3]+1us/cleanup)给 timing 解释(文本答案)未产出结构化分析脚本; A 不可行原因=真实 ZQ001_normal_check.v pattern 生产文件 SUT 沙盒不可达 -> 用自包含合成 ZQ001_normal_check.v pattern 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=analyze(「看下 timing relationship」), case 收敛为 produce-tool(写 analyze_zq_pattern_timing.py 分析器+out_B, 解析 command_sequence/deselectt_waits_ns/zq_mr7_ops/mrsetting_count/mrr_count)给 check() 牙(§4.2 subprocess 跑候选 python 静态分析文本 + §4.1 hidden-B cross-input guard B_test.sv 合成 REF_double_refresh_check pattern+task_name=='REF_double_refresh_check' 挡硬编 ZQ+13 顶层键); 重构为产 analyze_zq_pattern_timing.py+out_B; check.py 16 断言验 hidden-B cross-input guard+task_name 挡硬编+command_sequence+zq_mr7_ops 使纯 analyze 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-WtmFileReview-001":
        "DDR6 WTM 三文件静态审查->produce-tool (portability+review->produce-tool 审查器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「ll ... WTM001_normal_check.v WTM002_normal_check.v WTM004_block_check.v 帮我检查下这三个文件写的有没有问题」(纯 review 请求), agent 在 trace 读三文件给详细报告(WTM001 data width 288 bits+LFSR taps[23,19,10,4]+5-bit padding+op_mark 8'b0000_1111 / WTM002 dead seed+redundant xor+duplicate task+6-iter+8'hff / WTM004 pattern_name mismatch+premature endtask+duplicate+cross-file gen_wtm_write_data)(文本答案)未产出结构化审查脚本; A 不可行原因=真实 WTM001/002/004 .v 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM001/002/004 .v excerpt 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=review(「检查下有没有问题」), case 收敛为 produce-tool(写 wtm_review.py 审查器+out.json, 检查 width/taps/padding/loop/op_mark/dead-code/redundant/duplicate/pattern_name-matches-stem)给 check() 牙(§4.2 subprocess 跑候选 python 静态审查文本 + §4.1 hidden-B cross-input guard B width 32*6=192/taps[22,18,9,3]/padding4/loop3/op_mark 8'b0000_0010/no-dead-code/no-redundant/no-duplicate/pattern_name-matches-stem vs A 不同); 重构为产 wtm_review.py+out.json; check.py 18 断言验 hidden-B cross-input guard+width/taps/padding/loop/op_mark 全维度 vs A 不同使纯 review 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-WtmPatternDirReview-001":
        "DDR6 WTM 目录 pattern 审查->produce-tool (portability+review->produce-tool 目录审查器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「/home/tongfanl/DDR6/DSCQA/analogsim/WTM/ 帮我看下这里面的pattern有没有问题」(纯 review 请求), agent 在 trace 检查 5 符号链接 Verilog pattern 文件(WTM001-005), 找 7 确认问题(pattern_name copy-paste mismatch/跨文件调用留死代码/error_write bit9 死注入/rowf unused/TODO/条件编译注释/缺 PDE-PDX init/stub/.swp 残留)(文本答案)未产出结构化审查脚本; A 不可行原因=真实 WTM/ 目录 5 .v 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM/ 目录 5 .v 文件资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=review(「看下有没有问题」), case 收敛为 produce-tool(写 review_wtm_dir.py 目录审查器+out.json, 检查 block balance/symlink validity/seed self-consistency/pattern_name mismatch/死代码/死注入/缺 init/stub/.swp)给 check() 牙(§4.2 subprocess 跑候选 python 静态目录审查文本 + §4.1 hidden-B cross-input guard 5 合成 BWTM 文件 BWTM020 pattern_name mismatch+缺 PDE/PDX+rowf unused/BWTM040 死代码+跨文件调用+死注入 bit7/Write[7]/BWTM030 stub/BWTM010/050 clean/.BWTM020 .swp); 重构为产 review_wtm_dir.py+out.json; check.py 15 断言验 hidden-B cross-input guard+5 BWTM 文件 issue 集合精确匹配使纯 review 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-StimOp2MisMatchDiag-001":
        "DDR6 WTM002 OP2-mismatch 诊断->produce-tool (portability+debug-Q&A->produce-tool 诊断器 reframe, §4 有牙必要, r736 spotcheck batch14): 用户 tongfanl@hfhds201 原话「Load_Mode(.ma(8'hDE), .op({4'b0000,1'b0,1'b1,$urandom_range(1),pattern_select}),.op_mark(8'hff),.rstall(0),.enops(0)); 中的OP2位设置为1了，但是WTM002抽出来的激励中，OP2并没有为1。这是为啥?」(debug-Q&A 找根因), agent 在 trace(170 msgs)诊断: WTM002_normal_check.v 3-iter+2 MR222 per iter->6 MR222 all OP[2]=1, op_int merge op_mark=8'hff rstall=0->op_int=op OP[2]=1 正确, 两根因(1) timing_desync sim_addr.op 延迟非阻塞 PSD_OP 采样 stale (2) sampling_source_bug PSD1_OP SC1-only 采样 sc0.sim_addr.op 错 sc(文本答案)未产出结构化诊断脚本; A 不可行原因=真实 WTM002_normal_check.v+ddr6_test.sv+ddr6_genvector.sv 生产文件 SUT 沙盒不可达 -> 用自包含合成 WTM002_normal_check.v+ddr6_test.sv+ddr6_genvector.sv 资产保留真实任务结构(asset_fidelity 缺标, 待 @A apply 档2); trace 用户=debug-Q&A 找根因(「为啥」), case 收敛为 produce-tool(写 diag.py 诊断器+out.json, 解析 loop iter/mr222_sites_per_iter/total_mr222_executions/op_int_merge/timing_desync/sampling_source_bug)给 check() 牙(§4.2 subprocess 跑候选 python 静态诊断文本 + §4.1 hidden-B cross-input guard B loop 5-iter j=4..0+目标位 OP[3]+delay var tdelay+SC0-only 采样 sc1 bug vs A 3-iter OP[2] SC1-only sc0+mr222_sites_per_iter==2+total_mr222_executions==10+op_int_merge.result_when_opmark_ff_rstall0=='op_int = op'); 重构为产 diag.py+out.json; check.py 17 断言验 hidden-B cross-input guard+loop iter+mr222 计数+op_int_merge+timing_desync+sampling_source_bug 使纯 debug-Q&A 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-FineSimDcConvFix-001": "portability+Q&A 咨询->produce-tool 修复器",
    "EDA-Eval-DesignFlow-TrtfMeasDeckGen-001": "portability+produce-action 仿真迭代->produce-tool 测量 deck 生成",
    "EDA-Eval-DesignFlow-SpDeckStructExtract-001": "portability+explain/understand->produce-tool 解析器",
    "EDA-Eval-DesignFlow-WtmStructReview-001": "portability+review->produce-tool 审查器",
    "EDA-Eval-DesignFlow-PoststressTbAudit-001": "portability+review/audit->produce-tool 审计器",
    "EDA-Eval-DesignFlow-TzqlatLocate-001": "portability+Q&A 找值->produce-tool 定位器",
    "EDA-Eval-DesignFlow-DatatPrintOrderDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-LoadModeOpTruncDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
    "EDA-Eval-DesignFlow-MrrTaskSignatureExtract-001": "portability+explain->produce-tool 提取器",
    "EDA-Eval-DesignFlow-ZqPatternTimingAnalyze-001": "portability+analyze->produce-tool 分析器",
    "EDA-Eval-DesignFlow-WtmFileReview-001": "portability+review->produce-tool 审查器",
    "EDA-Eval-DesignFlow-WtmPatternDirReview-001": "portability+review->produce-tool 目录审查器",
    "EDA-Eval-DesignFlow-StimOp2MisMatchDiag-001": "portability+debug-Q&A->produce-tool 诊断器",
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
    print(f"=== r780 batch14 reframe_note apply: {len(REFRAME_NOTES)} cases ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 80 + {counts['OK']} = {80 + counts['OK']}")


if __name__ == "__main__":
    main()
