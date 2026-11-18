#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r829 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch4.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        本轮 batch4 = alphabetical 续 12 missing after DspfCapExtractValidate (r828 batch3 末位).
        reframe_note 271->283, miss 124->112.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r829 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch4 12 case = 7 keep_reframe_for_teeth + 5 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 7 keep_reframe + 5 keep_faithful):
  - portability-driver (foundry PDK / /proj 网表不可沙盒复刻 / real artifact 缺失 → level-1 proxy / synth_deck / synth_data):
      6 case: DspfTailorNetFix (real DSPF/tailor project不可复刻→synth_deck) /
              DutySkewAvg (real FineSim .mt0不可复刻→synth_data edges.csv) /
              FineSimModelScopeFix (real Totem-SC project不可复刻→synth_deck dut.sp/models.sp) /
              FineSimNoRefCktFix (real array netlist不可复刻→synth_deck) /
              FineSimWorkflowRunner (foundry不可复刻+real artifact缺失→level-1 synth_deck workflow) /
              GmidLut (foundry+real MPQA批量仿真不可复刻→level-1 NMOS synth_data params)
  - Q&A-analysis-driver (诊断/解释 → 结构化 JSON 报告 for §4 subprocess 有牙):
      1 case: FineSimMetricCornerDiag (哪个文件含指标+为何只TT→diagnose_metrics_corners.py+JSON 报告)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful/A-verbatim):
      5 case: DspfFloatLayerDiag (A-faithful, 用户显式要「修改命令」produce-action 同形) /
              FinesimLaunchAgent (A-faithful, 用户显式要「创建 agent」produce-action 同形) /
              FinesimMatrixrunAgent (A-faithful, 同上 twin case) /
              FloatingNetChecker (A=trace-verbatim, 用户显式要「检查工具」produce-action 同形) /
              FsdbPulseFilter (A-faithful, trace agent 写 final_report.py, case 同形 produce-report)

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer/level 缺标或误判 (应 L1/L2), k_check 字段缺标, shard 缺标
  - 与 r773-r800/r826/r827/r828 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 7 keep_reframe_for_teeth =====
    "EDA-Eval-DesignFlow-DspfTailorNetFix-001":
        "DSPF-based SRAM tailoring detect_map.py net_of_node() 理想供电解析 bug 修复->produce (portability-driver reframe, real DSPF/tailor project 不可沙盒复刻->synth_deck, §4 有牙必要, r829 reframe_note backfill batch4): 用户 e0044979@hfeg0pkn003 (sess 1794462731642_97zkm, mc=539) SRAM idle-cell tailor run 拒绝裁剪 idle cell, plan.log 报 mapping_not_verified, 用户诊断 VDD/VSS 为理想供电无 RC net, node name 应==net name, 要求修复 detect_map.py 的 net_of_node(); 根因=net_of_node() 返回空致 pin_unmapped, 加裸全局名(无':'无'.')自解析分支; A 不可行原因=real /rundata DSPF+tailor project 不可沙盒复刻 -> 收敛为 detect_map.py 修复(读 hidden B DSPF 文本, 自解析理想供电, asset_fidelity=synth_deck); reframe 由 portability-driver(real DSPF/tailor 不可复刻); 意图核心(修复 net_of_node 理想供电自解析 bug)完整保留; check.py 12 断言验 detect_map.py + hidden B exit 0 输出 tab 分隔 node->net + VDDCE/VSSCE/VDDPST 自解析为自身 + 内建地 0 解析为 0 + 有映射 XI3/0 解析为 vddce_rc + 有 *|NET 声明 VDDCE_RC 解析为 declared + 无映射 ':'/'.' 子节点解析为空(守卫) + 3 随机种子 probe 子集一致 + 随机化理想供电名自解析(反硬编码) + 跨输入 guard => 收敛为 produce-action 修复是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 跑候选 python 解析 DSPF 文本, 0 EDA 二进制, 若仅文本解析应 L1), level 缺标, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-DutySkewAvg-001":
        "DDR4 DQS 多相 divider 输出窗口平均 duty/skew 测量(固定边沿序号 bug 修复)->produce (portability-driver reframe, real FineSim .mt0 不可沙盒复刻->synth_data edges.csv, §4 有牙必要, r829 reframe_note backfill batch4): 用户 joeyl@hfeg0pkn004 (sess 1791958847728_7ycbz, mc=53) FineSim 仿真 DDR4 DQS testbench, 测 divider 多相输出 out0..out3 窗口平均 duty/skew, 原测法固定边沿序号(rise=5/fall=6) 因 divider 相位/分频比随 corner 漂移致 duty=1.47~1.53(应~0.5)/skew=2.4e-10(5 UI 应 1 UI); A 不可行原因=real FineSim .mt0/.sw0 不可沙盒复刻 -> 收敛为 duty_skew_avg.py(读 edges.csv 完整周期配对边沿计数, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻->synth edges.csv); 意图核心(完整周期配对边沿计数修复固定序号 bug)完整保留; check.py 16 断言验 zip 含 duty_skew_avg.py+out_A.csv + py_compile + hidden B exit 0 产 out_B.csv + 表头 5 duty_*+3 skew_* 8 列 + A/B duty 值匹配 ref(±2%) + B duty_out0 落 (0.3,0.5) 即边沿计数歧义被完整周期配对正确处理(反朴素固定序号) + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 跑候选 python 处理仿真导出数据), level 缺标应 L2, k_check 字段缺标应 16, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FineSimMetricCornerDiag-001":
        "FineSim .md0 指标定位 + 多工艺角缺失诊断->produce (Q&A-analysis-driver reframe, 哪个文件含指标+为何只TT 的 Q&A->diagnose_metrics_corners.py+JSON 报告 for §4 subprocess 有牙, r829 reframe_note backfill batch4): 用户 e0024852@hfeg0pkn002 (sess 1793589408208_roznq, mc=553) SRAM bitcell 后仿 (hd_CH252, PEX rev06/model rev04), 问 sim_result 目录哪个文件含 Iread/Ileak/SNM 指标及怎么解析, 以及 FF/SS/FS/SF 工艺角结果在哪; 助手诊断 .md0 是 measure dump 含全部指标, 但 stimulus 只加载 tt_sram_dbc 工艺角且无 .alter 块故只跑 TT, FF/SS/FS/SF 不存在; A 不可行(为 §4 有牙)原因=「哪个文件+为何只 TT」自然语言 Q&A 不可被 subprocess 确定性判分 -> 收敛为 diagnose_metrics_corners.py(输出 diagnostic_report.json, asset_fidelity=A-faithful, sim_result 文件便携); reframe 由 Q&A-analysis-driver(Q&A-诊断->produce-JSON 报告); 意图核心(定位指标文件+诊断多工艺角缺失)完整保留; check.py 13 断言验 zip 含 diagnose_metrics_corners.py+diagnostic_report.json + JSON 13 schema 字段齐全 + 重跑 A exit 0 复现 shipped 报告(反手写) + metrics_source_file 以 .md0 结尾(非 .log/.sw0) + metrics_found==[iread,ileak,iwrite,wnm_1,wnm_2] + measure_statements 解析 + corners_expected vs corners_found + 缺失角根因==无 .alter + 跨输入 guard => 收敛为 produce-JSON 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 .md0 文本+诊断, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FineSimModelScopeFix-001":
        "Ansys Totem-SC FineSim 'can't find model' .model ./ 本地作用域语法修复->produce (portability-driver reframe, real Totem-SC project 不可沙盒复刻->synth_deck dut.sp/models.sp, §4 有牙必要, r829 reframe_note backfill batch4): 用户 e0014566@hfeg0plg58 (sess 1784623431472_gvm3g, mc=554) Ansys Totem-SC 电源/EM 可靠性仿真 (DRAM G4B-CIP block, FineSim 底层 SPICE), runme 跑失败 FineSim 报 'can't find model for mosfet mn1/mp1 / diode d1'(共9错), ELMV 段错误; 根因=模型文件 incFile_G4B_CIP/incFile_lp 用 HSPICE 专有本地模型作用域语法 .model ./ntn. type, FineSim 不支持 ./ 前缀; 修复=把 .model ./ 替换为 .model(去 ./ 前缀保留模型名, 共53处)+CHECK_MODEL_CORNER 1->0 + CRLF->LF, FineSim 成功 'Successfully Completed'; A 不可行原因=real Totem-SC project+FineSim 二进制不可沙盒复刻 -> 收敛为 fixer.py(读 models.sp 去 ./ 前缀, asset_fidelity=synth_deck); reframe 由 portability-driver(real Totem-SC 不可复刻); 意图核心(修复 .model ./ HSPICE 本地作用域语法 FineSim 不兼容)完整保留; check.py 16 断言验 zip 含 7 必要件 + diagnosis.root_cause 指出 .model ./ + broken_syntax=='.model ./' + 修复后 0 个 .model ./ + .model 语句数==原始(未丢模型定义) + dut.log 含 'FineSim Successfully Completed' + 跨输入 guard => 收敛为 produce-action 修复是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 FineSim 跑通日志, 候选真跑模型语法修复), level 缺标应 L2, k_check 字段缺标应 16, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FineSimNoRefCktFix-001":
        "FineSim 'no reference ckt' 缺失 .subckt .inc 注入修复->produce (portability-driver reframe, real array netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r829 reframe_note backfill batch4): 用户 rongtaoy@hfeg0pkn001 (sess 1791963948520_hk622, mc=257) DDR5/DRAM memory array sense-margin 仿真, 把 PEX 抽出的 SPF(spf_CC) 与前仿网表做 .subckt 端口对比黑盒替换, FineSim 报 'ERROR! no reference ckt <name> for xi_<inst> ... of <parent>'(10+条), 根因=netlist 里 X 实例引用的 .subckt 定义缺失(spf include 未 .inc 进主网表), 修复=把缺失的寄生 subckt 定义通过 .inc 注入(黑盒替换端口不变); A 不可行原因=real array netlist+PEX SPF 不可沙盒复刻 -> 收敛为 fixer.py(解析 FineSim 日志 'no reference ckt' + 注入缺失 .inc, asset_fidelity=synth_deck); reframe 由 portability-driver(real array netlist 不可复刻); 意图核心(注入缺失 subckt .inc 修复 no reference ckt)完整保留; check.py 14 断言验 zip 含 fixer.py + py_compile + 源码含 'no reference ckt' 日志解析标记(反硬编) + name-agnostic(不含 A/B 缺失 subckt 名字面量) + hidden B exit 0 产 diagnosis.json + missing_subckts 集合==B ground truth + 注入后 dut.sp 含缺失 .inc + FineSim 日志含 Successfully Completed + 跨输入 guard => 收敛为 produce-action 修复是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 FineSim 跑通), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FineSimWorkflowRunner-001":
        "FineSim 端到端仿真工作流 runner(DC/Tran/AC 多类分析+解析+收敛判定+结构化报告)->produce (portability-driver reframe, foundry 不可复刻+real artifact 缺失(用户未接受/未跑通最终工作流)->level-1 Shichman-Hodges synth_deck workflow, §4 有牙必要, r829 reframe_note backfill batch4): 用户 zjqiao@hfhds206 (sess 1791017602459_fwgyy, mc=312) U#0 原话「你能否自己形成一个工作流进行finesim仿真」, 希望 agent 自主形成可复用端到端跑通的 FineSim 仿真工作流(给定网表+分析配置自动驱动 FineSim 跑多类分析/解析 .measure/判收敛/落结构化报告); trace agent 用 run_approved_command 调 finesim 但用户未接受/未跑通最终工作流(无 real artifact); A 不可行原因=foundry PDK 不可沙盒复刻 + real artifact 缺失 -> 收敛为 finesim_workflow.py(Python 入口, level-1 Shichman-Hodges MOS 反相器 DUT, .75 无 foundry PDK 依赖, asset_fidelity=synth_deck); reframe 由 portability-driver(foundry 不可复刻 + B档 synthesized sub-flow); 意图核心(形成可复用 FineSim 仿真工作流)完整保留; check.py 14 断言验 zip 含 finesim_workflow.py + py_compile + hidden B exit 0 产 workflow_report.json+detail.csv+summary.csv + finesim 真跑(report.finesim_ran==true 且 run.log 含 'finesim', 反 fake_no_rerun/fake_core_deleted) + analyses_run==sorted(B)[ac,dc,tran](反漏分析) + .measure 解析 + 收敛判定 + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 FineSim 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 finesim 真跑), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-GmidLut-001":
        "Gm/Id 查找表构建器(.op 网格扫描+MOS 工作点解析+Vds=0 截止区 Cgg=0 陷阱)->produce (portability-driver reframe, foundry+real MPQA/ALPS 批量仿真不可沙盒复刻->level-1 NMOS synth_data params, §4 有牙必要, r829 reframe_note backfill batch4): 用户 t0002801@hfeg0plg99 (sess 1791876404012_d7cbo, mc=190, characterization 域) 做模拟电路自动 sizing, 用 MPQA/ALPS 批量跑 MOSFET I-V, 发现 testbench Vd=0 管子截止致 Cgg=0 全 0, 需重建完整 Gm/Id LUT; A 不可行原因=real MPQA/ALPS 批量仿真+foundry 模型不可沙盒复刻 -> 收敛为 gmid_lut_gen.py(HSPICE .op 在 (Vgs,L) 网格扫点, level-1 NMOS params, 解析 id/gm/gds/vth/cgtot/cgs/cgd 算 gm_id/id_over_w/ft 输出 CSV, asset_fidelity=synth_data); reframe 由 portability-driver(foundry+real MPQA 不可复刻->level-1 synth_data params); 意图核心(重建完整 Gm/Id LUT + Vds=0 截止区 Cgg=0 陷阱烤进 check)完整保留; check.py 16 断言验 zip 含 gmid_lut_gen.py+gmid_lut_A.csv + py_compile + hidden B exit 0 产 lut_B.csv + 12 必需列齐全 + 行数==|vgs|×|l| + 所有 cgg>0(核心陷阱 Vds=0 截止区 Cgg≈0) + cgg 随 L 单调增 + id 随 Vgs 单调增 + 跨输入 guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 HSPICE .op 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 HSPICE .op 真跑), level 缺标应 L2, k_check 字段缺标应 16, shard 缺标应 B。",

    # ===== 5 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful/A-verbatim) =====
    "EDA-Eval-DesignFlow-DspfFloatLayerDiag-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r829 reframe_note backfill batch4): 用户 e0024852@pkn004 (sess 1794225375454_btflh, mc=16) U#0 原话「/rundata/.../pex_hd_CH252_bitcell/hd_CH252_bitcell.dspf 我观察到这个 dspf 文件生成的并不全 我想知道寄生电路来自那一层 以及这一层的位置 帮我修改现有的命令」, 意图形态=diagnose+produce-action(verb「修改命令」显式要 patch command, 非纯 Q&A), 可便携性=高(real gxrc 命令+DSPF LAYER_MAP/tran.map 便携, asset_fidelity=A-faithful); trace agent 读 dspf *LAYER_MAP/tran.map VIA 段/gex 抽取日志/open_short.rpt, 判定无内部 via 缺失, 根因=背面阱 tap 经 BV0->bmetal1 连 VDD/VSS 被当 floating 由 REMOVE_FLOATING=YES 丢掉, 缺失层=BV0+bmetal1, 修改命令 REMOVE_FLOATING YES->NO, case 交付 gxrc_cci_cmd_patched+diagnosis_report.md 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「诊断+修改命令」与 case 交付 patched command+report 同形映射); check.py 17 断言验 zip 含 patched 命令+diagnosis_report.md + REMOVE_FLOATING 改 NO + COUPLE_TO_GROUND MODE 改 YES + 命令行数与 A 一致(忠实 patch 非重写) + FLOATING_HANDLING 保留 + EXT_VIA_CAP/EXT_RES_BODY_CAP 保留 + 泛化到 B 后 REMOVE_FLOATING=NO + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1, k_check=17==k_rationale=17 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确, level 缺标应 L1, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FinesimLaunchAgent-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r829 reframe_note backfill batch4): 用户 zjqiao@hfhds206 (sess 1794474782925_5ityn, mc=404) U#0 原话「这个代码是我进行 finesim 仿真的代码,现在我希望你能创建一个 agent,在用户说明激励文件和网表文件以后,启动该程序,将激励文件填入激励文件的位置,然后选择网表,再点击运行仿真」, 意图形态=produce-action(verb「创建 agent」显式要 codegen CLI agent), 可便携性=高(stimulus_manager.py Tkinter GUI bundle 内嵌命令组装逻辑便携, asset_fidelity=A-faithful); trace agent 深读 _build_matrixrun_cmd/_run_auto_all/_run_matrixrun 流程, 提取 GUI 命令组装逻辑产 extract_bundle.py(567 行 CLI agent), case 交付 sim_launch_agent.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「创建启动 agent」与 case 交付 CLI agent 同形映射); check.py 17 断言验 zip 含 .py agent + py_compile + --dry-run 在 config_B 产出 matrixrun -p 开头命令 + -p/-v/-f/-nr/-nl/-i 取 B 值(反硬编码 A) + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, layer=L1, k_check=17==k_rationale=17 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python --dry-run, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 17, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FinesimMatrixrunAgent-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r829 reframe_note backfill batch4): 用户 zjqiao@hfhds201 (sess 1793243267055_5hjg7, mc=612, =.75 local) U#0 原话「这个代码是我进行finesim仿真的代码,现在我希望你能创建一个agent,在用户说明激励文件和网表文件以后,你看可以启动该程序,将激励文件填入激励文件的位置,然后选择网表,再点击运行仿真,你可以做到吗」+ attached stimulus_manager.py(137KB Tkinter GUI bundle), 意图形态=produce-action(verb「创建 agent」显式要 codegen CLI agent), 可便携性=高(GUI bundle 内嵌 matrixrun 命令构造逻辑便携, asset_fidelity=A-faithful); trace 612 msgs/2MB, assistant 解析 GUI bundle 提取 matrixrun 命令构造逻辑产 extract_bundle CLI agent, case 交付 headless CLI agent 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, twin case of FinesimLaunchAgent, trace 意图「创建 agent」与 case 交付 CLI agent 同形映射); check.py 19 断言验 zip 含 .py + py_compile + hidden B exit 0 + stdout 含 '[DRY-RUN] matrixrun command:' + 命令以 matrixrun 开头 + -f/-nr/-p/-q 取 B 值(反硬编码 A) + 跨输入 guard => §4 牙由 hidden-B cross-input 保证, layer=L1, k_check=19==k_rationale=19 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确, level 缺标应 L1, k_check 字段缺标应 19, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FloatingNetChecker-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r829 reframe_note backfill batch4): 用户 xiwang@hfeg0pkn002 (sess 1794195576366_jp8n9, mc=34) U#0 原话「现在有检查 floating 的工具吗？」+ ask_question 澄清「悬空节点/网(floating net):网表里无驱动的浮空网, net 上端子数只连了1个或看图悬空」, 意图形态=produce-action(verb「检查工具」显式要 build checker tool), 可便携性=高(纯 Python CDL/SPICE 解析器 tokenize_lines/parse_cdl/find_floating, 无 EDA 二进制依赖, asset_fidelity=A=trace-verbatim); trace agent 查工作区已有 collector/check_reach/validate_csv 非floating检测, 查 pyAether aeGetIncompleteNets(layout) 但设计库 OA 格式+pyAether 沙箱 down, 交付 check_floating.py(纯 Python CDL/SPICE 解析器+薄 Aether 封装), case 交付 check_floating.py+run_floating.sh 同形(零偏移, A=trace-verbatim); reframe_note=None->补(faithful 无 reframe, trace agent 因 pyAether 沙箱 down 转纯 Python 解析是 trace 内决策非 case 重构, trace 意图「floating 检查工具」与 case 交付纯 Python 解析器同形映射); check.py 23 断言验 zip 含 check_floating.py+run_floating.sh + py_compile + 8 必填函数齐全 + --selftest exit 0 + SELF-TEST OK + 检出 FLOAT1 + hidden B 检出 B floating nets + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1, k_check=23==k_rationale=23 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确, level 缺标应 L1, k_check 字段缺标应 23, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-FsdbPulseFilter-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r829 reframe_note backfill batch4): 用户 kejunw@hfeg0pkn002 (sess 1794398756746_2g3in, mc=866) U#0 原话逐字「你可以直接分析分析fsdb波形吗」+「请分析如下 path 的所有信号,筛选出脉冲宽度小于300ps,tr 和 tf 大于600ps 的信号 xi_c_top.xi_array16gtop.xi_spinetop.xi_banktopx2b23.xi24」, 意图形态=produce-report(verb「筛选出...信号」显式要 filtered list/report), 可便携性=高(real fscript dump 出的 .tbl 文本波形便携, asset_fidelity=A-faithful); trace agent 用 fscript dump clean_out2.tbl(12 信号, 900-999ns 步长 1ns), 写 final_report.py 计算 25-75% 上升时间/75-25% 下降时间/50% 阈值脉冲宽度并筛选, case 交付 filter_pulse_signals.py+pulse_filter_report.json 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace agent 写 final_report.py 与 case 交付 filter 脚本+JSON 报告同形映射); check.py 13 断言验 zip 含 filter_pulse_signals.py+pulse_filter_report.json + JSON 合法且 5 顶层键齐全 + A 重跑 exit 0 复现 shipped 报告(反手写) + n_signals_total==12 + n_signals_filtered 匹配 + filtered_signals 集合匹配 + 跨输入 guard => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1, k_check=13==k_rationale=13 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 .tbl 文本波形, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",
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
