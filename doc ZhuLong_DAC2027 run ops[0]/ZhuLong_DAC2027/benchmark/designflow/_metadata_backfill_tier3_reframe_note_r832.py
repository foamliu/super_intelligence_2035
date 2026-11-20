#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r832 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch7.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        r830 batch5 +12 (283->295, miss 112->100).
        r831 batch6 +12 (295->307, miss 100->88).
        本轮 batch7 = alphabetical 续 12 missing after Mt0Reorg (r831 batch6 末位),
        起算 Mt0TskewCalc, M->N->O->P 段.
        reframe_note 307->319, miss 88->76.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r832 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch7 12 case = 6 keep_reframe_for_teeth (portability) + 6 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 6 keep_reframe portability + 6 keep_faithful):
  - portability-driver (foundry PDK / real .mt0.csv/.sp netlist/HSPICE deck 不可沙盒复刻 -> synth_deck / synth_data):
      6 case: Mt0TskewCalc (real FineSim .mt0.csv 不可复刻->synth_data, spice_sim) /
              NetlistLintHsp (real ~100MB 网表+foundry 不可复刻->synth_deck, spice_sim) /
              NetlistStaticCheck (real CXMT 混合信号网表不可复刻->synth_deck, spice_sim) /
              NetlistTranDeck (real tran-sim-gen skill 依赖 foundry HSPICE 不可复刻->synth_deck, 子技能提取) /
              NocalOffsetDeck (real HSPICE 校准 testbench 不可复刻->synth_deck, characterization) /
              OtaAutoTune (real foundry PDK+HSPICE 5T OTA deck 不可复刻->synth_deck, characterization)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      6 case: MultiPvtSpGenBuild (A-faithful, PVT 表+黄金模板便携, SP 卡生成器同形) /
              NetlistDiffBankLogic (A-faithful, FineSim 网表文本 scp 便携, diff 工具同形) /
              NetlistModSummary (A-faithful, 463K 行 Finesim 网表文本便携, 模块摘要器同形) /
              OtaAcReport (A-faithful, wv_export .tbl ASCII 便携 post-WaveView, 报告生成器同形) /
              PexStimulusBuild (A-faithful, 参考刺激+PEX 网表文本便携, 后仿 stimulus builder 同形) /
              PlatInvsThick (A-faithful, condition 文件+inv deck 模板便携, 厚栅 deck 生成器同形)

N段 domain-wave 观察: batch7 keep_faithful 占比 50% (6/12) 显著高于 batch5/batch6 (25%),
  因 N段 Netlist* 群 (4 case) 的 SPICE 网表是文本可 scp 便携 -> asset_fidelity=A-faithful 主流,
  与 M段 .mt0/.sp/.md0 后处理群 (real artifact 不可便携 -> synth) 形成对比.
  portability-driver 二分族延续: N段 keep_reframe 3 case 均 real project 网表/skill 不可便携须合成.

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 缺标或标 L2 待复核(check 仅 subprocess 跑候选 python 解析文本, 0 EDA 二进制, 应 L1)
  - level/k_check/shard 字段缺标
  - 与 r773-r800/r826-r831 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 6 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-Mt0TskewCalc-001":
        "FineSim .mt0.csv 测量文件 PP/WP 两组 Tr/Tf 向 1.5ns 取余后分组算 Tskew->produce (portability-driver reframe, real FineSim .mt0.csv 不可沙盒复刻->synth_data, §4 有牙必要, r832 reframe_note backfill batch7): 用户 reedchen@hfeg0plg49 (sess 1792139236507_7jzqb, mc=2294, spice_sim 域) 给 output_SS_9V-40C.mt0.csv(PP(epp)/WP(ewp) 两组各含 Tr(_r)/Tf(_f) 延迟值), 要求全部值向 1.5ns 取余后每组 Tskew=max(Tf_max,Tr_max)-min(Tf_min,Tr_min); U#45 用户纠正 PP/WP 是两种独立情况各算各的 Tskew; trace agent 写 tskew_calc.py(解析 $DATA1/.TITLE 头 + 按前缀/后缀分类列 + mod 1.5ns + 分组极值); A 不可行原因=real FineSim .mt0.csv 不可沙盒复刻 -> 收敛为 tskew_calc.py(读 hidden B synth .mt0.csv, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0.csv 不可复刻); 意图核心(.mt0.csv 列式 parse + PP/WP 前缀分类 + Tr/Tf 后缀分类 + mod 1.5ns 取余 + 分组极值 Tskew 公式 + PP/WP 独立计算)完整保留; check.py 13 断言验 zip 含唯一 .py + py_compile + 接受 --input/--output CLI + B 上 exit0 产非空 output JSON + output 含 pp_tskew_ps/wp_tskew_ps 两键 + B 上 PP Tskew 正确(容差 2ps) + B 上 WP Tskew 正确 + mod 1.5ns 取余正确(非原始值) + PP/WP 独立计算(不混组) + Tr/Tf 前后缀分类正确 + cross-input guard(A≠B 数据值不同) + 退化 stub(只 print 期望)FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 .csv 文本+算 Tskew, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-NetlistLintHsp-001":
        "~100MB SPICE/HSPICE 层次化网表流式语法格式 lint + HSPICE elaboration 权威首错记录->produce (portability-driver reframe, real ~100MB 网表+foundry HSPICE 不可沙盒复刻->synth_deck, §4 有牙必要, r832 reframe_note backfill batch7): 用户 jason17w@hfeg0pnd002 (sess 1790563683904_l7aol, mc=288, spice_sim 域) 要求对 ~100MB SPICE 网表做语法/格式 lint(无法一次读入内存), cline 写流式 netlist_checker.py 逐行扫描+HSPICE elaboration 验证; 本 case 取其可移植子技能=流式 SPICE 网表语法+格式 lint(name-agnostic)+HSPICE 作 elaboration 权威记录首错行/消息; A 不可行原因=real ~100MB 网表+foundry HSPICE 环境不可沙盒复刻 -> 收敛为 netlist_lint.py(读 hidden B synth 层次化 level-1 MOS 网表, 9 类缺陷: unclosed/pin-mismatch/undef-sub/missing-model/..., asset_fidelity=synth_deck); reframe 由 portability-driver(real 网表+foundry HSPICE 不可复刻); 意图核心(流式逐行扫描不一次性读入内存 + 9 类语法错误分类计数 + max_line_length 格式检查 + HSPICE elaboration 作语法权威记录首错行/消息)完整保留; check.py 27 断言验 hidden B 网表可定位 + zip 合法 + 含 netlist_lint.py + py_compile + 候选在 B 上不崩溃/超时 + 产 lint_report.json + 产 hspice_validation.json + hspice_ran==true + n_lines 统计正确 + 9 类缺陷按类别报告 + unclosed_subckt 检出 + pin_count_mismatch 检出 + undefined_subckt_call 检出 + missing_model 检出 + max_line_length 违规检出 + 流式内存不爆(OOM guard) + HSPICE 首错行记录 + HSPICE 首错消息记录 + cross-input guard(A≠B) + 退化 stub FAIL + 确定性 3 次一致 + lint_report 结构合法 + ... => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 HSPICE elaboration 真跑)结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 HSPICE elaboration 真跑含 EDA 二进制), level 缺标应 L2, k_check 字段缺标应 27, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-NetlistStaticCheck-001":
        "CXMT 混合信号网表 R1-R4 静态规则检查统一工具(电压域枚举/跨域直驱/stdcell 扇出/spare 充足性)->produce (portability-driver reframe, real CXMT 混合信号网表不可沙盒复刻->synth_deck, §4 有牙必要, r832 reframe_note backfill batch7): 用户 tongni@hfeg0pkn004 (sess 1794220525700_nj8q4, mc=150, spice_sim 域) 在 CXMT 混合信号设计网表上做 R1-R4 静态规则检查(顶层设计单元电压域枚举 / 跨电压域直驱风险 / stdcell 扇出>4 告警 / spare 充足性≥40%); trace agent 用 editor 反复写 r1r2_report.py(475 行)+r3_fanout_report.py(178 行)+r4_spare_report.py(212 行) 三独立脚本 + run_netlist_checks.py 统一 CLI runner, 真实网表上跑通出 R1-R4 报告(R1=8 顶层单元含电压域/R2 检出 net027 跨域双向直驱); 用户没把「解析网表+跑四项检查+出合并报告」沉淀成统一可复用工具; A 不可行原因=real CXMT 混合信号网表不可沙盒复刻 -> 收敛为 netlist_static_check.py(读 hidden B synth 网表, asset_fidelity=synth_deck); reframe 由 portability-driver(real 网表不可复刻); 意图核心(SPICE 网表 parse + R1 电压域枚举 + R2 跨域直驱风险 + R3 stdcell 扇出>4 告警 + R4 spare≥40% 充足性 + 合并报告)完整保留; check.py 15 断言验 zip 含 netlist_static_check.py + py_compile + 候选在 hidden B1 上 subprocess exit0 写非空报告 + B1 报告 R1 段含 vcc!(1.025V)/vdd1!(1.8V)/vwlp!(2.5V) 三域枚举 + R2 段检出跨域直驱风险 net + R3 段检出扇出>4 stdcell + R4 段 spare 充足性百分比 + 四项合并为单报告 + cross-input guard(A≠B 网表不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析网表文本+规则检查, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 15, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-NetlistTranDeck-001":
        "tran-sim-gen skill 可移植子技能: 解析 .SUBCKT 端口分类电源/输出/信号输入->生成 tran testbench->HSPICE 真跑测 tpd->produce (portability-driver reframe + 子技能提取, real tran-sim-gen skill 依赖 foundry HSPICE 不可沙盒复刻->synth_deck, §4 有牙必要, r832 reframe_note backfill batch7): 用户 tongni@hfeg0pfn119 (sess 1792378687851_j8vf6, mc=156, spice_sim 域) 已建 tran-sim-gen skill(给定 testbench netlist 识别外部驱动输入信号并生成 tran .sp); trace 本体是 skill 用法解释+MCP 重构(A-档合规需求轮 T0/T63), 本 case 取其可移植子技能=解析 .SUBCKT 端口->分类电源/输出/信号输入->生成 tran testbench->HSPICE 真跑->测 tpd; A 不可行原因=real skill 依赖 foundry HSPICE 环境+真实设计网表不可沙盒复刻 -> 收敛为 tb_gen.py(读 hidden B synth level-1 子电路网表 nand3.sp, asset_fidelity=synth_deck); reframe 由 portability-driver(real skill+foundry HSPICE 不可复刻) + 子技能提取(从 skill 用法解释轮提取可移植 tran-deck 生成子能力); 意图核心(.SUBCKT 端口 parse + 电源/输出/信号输入分类规则 + pwl 电压源驱动信号输入 + 负载电容 + .tran + .measure tpd)完整保留; check.py 18 断言验 hidden B 网表可定位 + zip 合法 + 含 tb_gen.py + py_compile + 候选在 B 上 exit0 + 产 result.json + hspice_ran==true + n_inputs==3(识别 nand3 全部 a/b/c) + 电源分类正确(vdd/gnd) + 输出分类正确(out) + pwl 源加在信号输入 + 负载电容加在输出 + .tran 语句存在 + .measure tpd 存在 + tpd 数值在合理范围 + cross-input guard(A≠B 网表不同 n_inputs 不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 HSPICE 真跑)结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 HSPICE 真跑含 EDA 二进制), level 缺标应 L2, k_check 字段缺标应 18, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-NocalOffsetDeck-001":
        "比较器输入失调校准->不校准对照 testbench 改写(init/cal_clk/cal_en 常置化让校准不启动)->produce (portability-driver reframe, real HSPICE 校准 testbench 不可沙盒复刻->synth_deck, §4 有牙必要, r832 reframe_note backfill batch7): 用户 yanghao@hfeg0pkn002 (sess 1792460814763_xq6n1, mc=58, characterization 域) 对 hspice 提比较器输入失调校准->不校准对照 testbench 改写请求: '参照 cal_only.sp 写一个不校准都测量 offset 的 sp 文件, 作为对照。即 init 一直为1, 开关一直断开, DFF6~0 始终没有时钟触发'; 原核心是把 init/cal_clk/cal_en 三个控制信号常置化(init=vdd / clk=0 / en=0)让校准流程不启动, 保留 .subckt/.measure offset/Vip ramp; A 不可行原因=real HSPICE 校准 testbench(含 cmp_dut 3 级反相器+开关电容校准 apparatus)不可沙盒复刻 -> 收敛为 nocal_deck_gen.py(读 hidden B synth cal_A.sp+spec_A.json, asset_fidelity=synth_deck); reframe 由 portability-driver(real testbench 不可复刻); 意图核心(三个控制信号 vsource 常置化 init=vdd/cal_clk=0/cal_en=0 + 保留 .subckt cmp_dut + 保留 .measure offset/Vip ramp + 校准流程不启动)完整保留; check.py 14 断言验 zip 含 nocal_deck_gen.py + py_compile + 候选在 B 上产 nocal_only.sp + nocal deck init 控制 vsource 常置 vdd + cal_clk vsource 常置 0 + cal_en vsource 常置 0 + DFF 无时钟触发 + .measure offset 保留 + Vip ramp 保留 + .subckt cmp_dut 保留 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(若 check 验 HSPICE 真跑则正确, 若仅生成 deck 文本应 L1), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-OtaAutoTune-001":
        "5T OTA 自动调参: 迭代调 XMMN0/XMMN1/XMMP0/XMMP1 的 W/L, HSPICE .LSTB AC loop-stability 测 gain/PM/GBW->produce (portability-driver reframe, real foundry PDK+HSPICE 5T OTA deck 不可沙盒复刻->synth_deck, §4 有牙必要, r832 reframe_note backfill batch7): 用户 zhukaic@hfeg0plg94 (sess 1792030774508_515eb, mc=149, characterization 域) 用 skill 驱动 HSPICE AC loop-stability(.LSTB vsource=v0, 单位增益反馈)仿真, 对 5T OTA(NMOS 差分对 MMN0/MMN1 + PMOS 镜像负载 MMP1/MMP0 + NMOS 尾管镜像 MMN3/MMN2 + 尾电流源 i4=2uA + vcc=1.025V)迭代调整 XMMN0/XMMN1/XMMP0/XMMP1 四管 W/L, 达成 gain/PM/GBW 三项验收; trace 3 trial 后 gain/GBW 达标 PM 未达标, 结论三项同时达标不可行; A 不可行原因=real foundry PDK+HSPICE 5T OTA deck 不可沙盒复刻 -> 收敛为 ota_tune.py(读 hidden B synth deck, asset_fidelity=synth_deck); reframe 由 portability-driver(real foundry deck+PDK 不可复刻); 意图核心(5T OTA netlist + .LSTB AC loop-stability + 四管 W/L 迭代调参 + gain/PM/GBW 三指标测 + 可行性判定)完整保留; check.py 16 断言验 zip 含 ota_tune.py+report.json+tuned_netlist.sp + py_compile + A report.method==hspice_run 且 feasible 且 best_design 满足 A spec + A baseline 指标 + 迭代 trial 记录 + HSPICE 真跑 + gain/PM/GBW 测量 + cross-input guard(A≠B spec 不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess(含 HSPICE 真跑)结构性必要, 保留。**metadata bug 待 @A**: layer 标 L3 正确(多工具链路 HSPICE 迭代调参+回归), level 缺标应 L3, k_check 字段缺标应 16, shard 缺标应 B。",

    # ===== 6 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-MultiPvtSpGenBuild-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 reedchen@hfeg0pkn002 (sess 1793941691690_z3tqe, mc=69, spice_sim 域, 11-09 fresh) 要求在 ReedChenWork_TB_DbusRcvWritePostSim 工作目录下构建多 PVT 前仿后仿环境, 参考 ReadPostSim/scripts/SKILL.md; 金标准 gen_sp_write.py 读 PVT 表(corner,voltage,temp)+黄金模板, 对每 corner 生成 1 个 SP 卡, 做 corner->库映射(model.sp 主段 TT/SS/FF); 意图形态=produce-action(构建多 PVT 仿真环境), 可便携性=高(PVT 表+黄金模板+SKILL.md 文本可 scp 便携, asset_fidelity=A-faithful); case 交付 gen_sp_write.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「构建多 PVT 前仿后仿环境生成 SP 卡」与 case 交付 generator 同形映射, env-config/produce-action 是 2026-11-15 令恢复的合法任务形态); check.py 12 断言验 zip 含 gen_sp_write.py + py_compile + B post(无 mc)退出 0 生成 5 个 .sp(每 PVT 行一个) + 每 corner .temp 行替换为 '.temp <temp>c' + .lib model.sp 主段设为 corner 名(TT->TT,SF->SF) + 每 .sp 含前仿+后仿段 + cross-input guard(A≠B PVT 表不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 SP 卡文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-NetlistDiffBankLogic-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 jingc@hfeg0pkn001 (sess 1794191339271_hx61r, mc=9, spice_sim 域) 让 cline 对比两份 FineSim SPICE 网表 drgqa_banklogic(496 行)与 drgqx_banklogic(494 行)(D_BankLogic 单元, /rundata/drgqx/.../RAS_edit/), 判断电路改了哪些; cline 写 compare_netlist.py 解析 .SUBCKT 端口/XI 实例/.connect, 输出结构化 diff + HTML 报告(8 端口删/10 端口增/...); 意图形态=debug-Q&A-analysis+produce-tool(对比网表出 diff 报告), 可便携性=高(FineSim SPICE 网表是文本可 scp 便携, asset_fidelity=A-faithful); case 交付 compare_netlist.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, debug-Q&A-analysis 是 2026-11-15 令恢复的合法任务形态, trace 意图「对比两份网表判断改了哪些电路」与 case 交付 diff 工具+报告同形映射); check.py 14 断言验 zip 解出 compare_netlist.py + py_compile + 候选在 B1 对(ClkBuf)真跑 subprocess exit0 非空输出 + B1 头部 LIB_A/CELL_A/LIB_B/CELL_B 正确 + B1 PORTS_REMOVED 列表含 Vb + B1 PORTS_ADDED 列表 + B1 实例 diff + B1 连接 diff + cross-input guard(A≠B netlist 对不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L1, k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析网表文本出 diff, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B, mc=9 偏低可作 trace_source 但 host-verify 待 @A 复核。",

    "EDA-Eval-DesignFlow-NetlistModSummary-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 e0015056@hfeg0pkn002 (sess 1794466529228_2397x, mc=610, spice_sim 域) 要求整理 /proj/decqa/V0/simdir/finesim/decqaF/Netlists/Netlist_Vcap_20260707PM 下电路的所有模块介绍; agent 写 parse_netlist_modules.py 解析 463K 行 Finesim 网表(7799 SUBCKT/12 library), 提取模块定义按 library 分组输出结构化摘要(端口/器件计数/顶层实例分析); 意图形态=analysis+produce-tool(整理网表模块介绍), 可便携性=高(AETHER-SE 生成 Finesim hspiceD 网表是文本可 scp 便携, asset_fidelity=A-faithful); case 交付 parse_netlist_modules.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, analysis/explain 是 2026-11-15 令恢复的合法任务形态, trace 意图「整理电路所有模块介绍」与 case 交付模块摘要器+结构化 JSON 同形映射); check.py 10 断言验 parser 在 hidden B 上 exit0 且输出合法 JSON + total_modules=19(非 Input A 的 21, 杀 hardcoded_A) + library 集合含 analog_lib 且 7 库完全匹配 + analog_lib module_count=3(BiasGen/VoltRef/Amp2Stage) + Amp2Stage 端口=[INP,INM,OUT,VDD,VSS] + cross-input guard(A≠B 网表不同 module 数不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => §4 牙由 hidden-B cross-input(21 vs 19 杀 hardcoded) + §4.2 subprocess 真跑保证, layer=L2, k_check=10==k_rationale=10 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析网表文本, 0 EDA 二进制, 应 L1), level 缺标应 L1, k_check 字段缺标应 10, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-OtaAcReport-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 zhukaic@hfeahpc503 (sess 1792978836622_054zc, mc=271, spice_sim 域) 用 Synopsys Custom WaveView(wv -ace_no_gui ACE Tcl)读取 HSPICE 两级 OTA AC/STB 仿真结果 ota_2stg_sim.ac0, 将数据结果转化为图片, 生成 workspace 仿真报告(loop-gain/phase Bode + PSR + 度量 JSON + markdown/HTML 报告); 意图形态=analysis+produce-tool(仿真结果转报告), 可便携性=高(经 WaveView wv_export 导出的 .tbl 是 ASCII 数据表可 scp 便携, 非 HSPICE 二进制 .ac0, asset_fidelity=A-faithful); case 交付 harness 读 hidden B wv_export .tbl 产 report.json+Bode+报告同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, analysis 是 2026-11-15 令恢复的合法任务形态, trace 意图「读 HSPICE AC/STB 结果生成仿真报告」与 case 交付报告生成器同形映射, asset A-faithful 因 WaveView .tbl ASCII 导出便携非 .ac0 二进制); check.py 16 断言验 zip 存在可解 + 含候选 harness .py + py_compile + harness 在 hidden B 表上 exit0 跑完 + out_dir 产 report.json 可解析 + report.json 含全部 10 个度量键 + dc_loopgain_linear 落 B 金标准 2% 内 + phase_margin 落 B 金标准内 + GBW 落 B 金标准内 + PSR 度量正确 + cross-input guard(A≠B .tbl 数据不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2, k_check=16==k_rationale=16 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析 .tbl ASCII+算度量, 0 EDA 二进制 run, 应 L1; 若验 WaveView wv 真跑则 L2 正确), level 缺标应 L1, k_check 字段缺标应 16, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PexStimulusBuild-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 e0024852@hfeg0pkn003 (sess 1794488730591_9lfys, mc=205, spice_sim 域) 要求以 stimulus_pex_rev06_model_rev04.sp 为蓝本为 CH231_HDT_Bitcell_FS_WiPin.gds 写后仿文件; agent 深读发现参考模板其实例化原理图 cell(hd_CH252_bitcell, hd_*_dbc) 而 PEX 网表(hdt_CH231_bitcell, hdt_*_fs)是死代码, 且 tt_sram_dbc 不定义 hdt_*_fs 会报 undefined subckt; 改例化 PEX 子电路 + 选 fs_sram_fs corner; 意图形态=produce-action(以后仿 stimulus builder 改写参考模板), 可便携性=高(参考刺激文件+PEX 网表是文本可 scp 便携, asset_fidelity=A-faithful); case 交付 pex_stimulus_builder.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「以参考刺激为蓝本为 PEX 子电路写后仿文件」与 case 交付 stimulus builder 同形映射); check.py 10 断言验 zip 含 pex_stimulus_builder.py + subprocess 在 hidden B 真跑无错 exit0 产 out_B.sp + out_B.sp 例化 PEX 子电路(B 的 pex_name)于>=1 测试 cell + out_B.sp 不再例化原理图 cell(sch_name) + .LIB corner==族匹配 corner(tt_sram_sf)而非参考 dbc 角 + 全部测试 cell 例化 PEX + cross-input guard(A≠B pex_name/sch_name 不同) + 退化 stub FAIL + 确定性 3 次一致 + ... => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer=L2, k_check=10==k_rationale=10 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制 run, 应 L1), level 缺标应 L1, k_check 字段缺标应 10, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-PlatInvsThick-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r832 reframe_note backfill batch7): 用户 hairuizh@hfeg0pkn002 (sess 1793879856361_1281g, mc=366, spice_sim 域) 给 plat_invs_thin/ 文件夹路径+7 要求做 plat_invs_thin->plat_invs_thick 复制+改厚栅: 1 沿用 condition 文件 2 反相器电源 pvwlp/pvss 3 GL22 只生成 ptk/ntk+ptk_lv/ntk_lv 两对 4 仅 sel_sweep=0/sel_case=2/sel_cond{0,1,2} 5 cthin->cthick 6 real swidth N=250n P=500n draw=real*shrink, L 扫 125n-1u step25n 7 自跑 mspice+debug; 金标准 4 平台厚栅 .sp(DEJOA shrink0.318/DR...); 意图形态=produce-action(复制+改厚栅生成 4 平台 deck), 可便携性=高(condition 文件+inv deck 模板文本可 scp 便携, asset_fidelity=A-faithful); case 交付 gen_thick_deck.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, produce-action 是合法任务形态, trace 意图「复制 plat_invs_thin 改厚栅生成 4 平台 inv deck」与 case 交付 deck 生成器同形映射, 与 Mt0Reorg(同用户 hairuizh 但 real 5-foundry thin-oxide deck+PDK 不可便携->synth_deck)区别在本 case condition 文件+模板便携故 A-faithful); check.py 12 断言验 zip 含 gen_thick_deck.py + py_compile + 脚本在 hidden B(同一 plat_invs_thin 源+config_B.json)上 exit0 产 4 平台 *_invs.sp+base.sp+run_hspice.sh + 每平台 cg1 电容用 Cthick 而非 Cthin(规则 5) + 每平台含 ntk/ptk 主对+ntk_lv/ptk_lv 的_lv + GL22 只两对(规则 3) + sel_sweep=0/sel_case=2/sel_cond{0,1,2}(规则 4) + real swidth N=250n P=500n(规则 6) + L 扫 125n-1u step25n + cross-input guard(A≠B config 不同) + 退化 stub FAIL + 确定性 3 次一致 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑保证, layer 缺标应 L1, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制; 若验 mspice/HSPICE 真跑则 L2), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",
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
