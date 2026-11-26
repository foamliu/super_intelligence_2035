#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r791 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r747_spotcheck26.tsv (batch25, 9/11 keep_reframe cases 待 apply; TrimMarginSpec + InstCurrentMeasGen 已标 ✓, HcellMissingFind keep_faithful 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r790 档3 batch9-24 done (reframe_note 32->171).
本轮 r791 档3 batch25 (r747 spotcheck26, 9 cases 待 apply). reframe_note 171->180.

reframe_note text = spotcheck26 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck26 11 keep_reframe):
  - Q&A-driver (explain/Q&A/debug/audit Q&A -> produce-tool 给 check 牙): 5 cases
    SpiceDeckPairDiff (e0024852, explain-Q&A deck diff -> produce-tool diff CLI) /
    XaLogCompare (e0024852, explain-Q&A XA log diff -> produce-tool compare CLI) /
    ModelLibVerDiff (e0024852, explain-Q&A PDK model.lib 版本 diff -> produce-tool diff CLI) /
    MeaNetPathDiag (shanliny, debug-Q&A .meas 提不出值 -> produce-tool 诊断脚本+root_cause) /
    WtmCrcInjectionAudit (tongfanl, audit-Q&A 检查 .v 行能否实现 CRC 错注入 -> produce-tool 审计脚本+JSON)
  - portability-driver (foundry/HSPICE/Virtuoso SKILL 不可便携 -> 抽便携子技能): 3 cases
    DOERankBuild (thqu, 全 DOE skill 含 HSPICE 真跑+foundry -> post-sim ranking 子技能) /
    SpTempParamAlter (ghyang, foundry/HSPICE 不可便携 -> deck 重写器子技能) /
    SpiceInAutoIl (sierraw, Virtuoso SKILL .il 不可便携 -> Python param gen 子技能)
  - harness-driver (produce-action file -> generator script for hidden-B teeth): 1 case
    G5TbGen (wzj, 交付 .sp testbench -> 交付 generator script 支撑 §4.1 hidden-B cross-input)

spotcheck26 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None->应 L1) 8/9: SpiceDeckPairDiff/XaLogCompare/ModelLibVerDiff/MeaNetPathDiag/SpTempParamAlter(已 L1)/SpiceInAutoIl(已 L1)/G5TbGen/WtmCrcInjectionAudit(已 L1)
    (check 仅 subprocess 跑 sys.executable[SUT 脚本] 解析文本/产 deck, 不启动 hspice/finesim/Virtuoso)
  - layer=L1 ✓ 已正确 1/9: DOERankBuild (check 跑候选 post-sim 解析排序, 不启动 hspice)
  - **B 域累计 layer 漏网 39 例**(r790 累计 31 + 本批 8: 8 例 layer 缺标应 L1, 0 例 layer 误分类),
    r772 档1 level->layer normalize 漏网之鱼 (cases/B has_layer 143->303 仍缺 92 的实证)
  - asset_fidelity 缺标 7/9(仅 SpTempParamAlter=synth_deck ✓ + SpiceInAutoIl=synth_deck ✓ 已标), 待 @A apply 档2
  - level 缺标或 layer None, 待 @A apply 档1 补 sweep
  - k_check 对账 9/9 header==circled 一致, k_check >=8 ✓ (最低 MeaNetPathDiag=12)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-SpiceDeckPairDiff-001":
        "FineSim deck 配对结构化 diff 报告器->produce-tool (Q&A explain-Q&A->produce-tool diff CLI reframe, §4 有牙必要, r747 spotcheck batch25): 用户 e0024852@hfeg0pkn004 (sess 1791981291929_4oo3i mc134), U0 逐字「I want to know the difference of _finesim.sp and _finesim_pre.sp tell me in chinease」; trace 实为 sim_log_compare.py 解释 + _finesim.sp vs _finesim_pre.sp 差异讲解; A 不可行原因=纯 explain-Q&A(对比两份 FineSim deck 讲差异)无 runnable artifact 无 check 牙 -> case 抽取「结构化 diff CLI(spice_deck_diff.py 产 JSON)」子技能, A 档 verbatim 合规(U0 原话逐字), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp)+B=synth(待 @A apply 档2); trace 用户=explain-Q&A(讲差异), case 收敛为 produce-tool(写 spice_deck_diff.py 产 .option 解析/.measure 签名/.alter 计数/added/removed/changed/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[tool, ref, cmp, out] 解析文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 spice_deck_diff.py 结构化 diff CLI; check.py 15 断言验 py_compile+CLI 三参+.option 解析+.measure 签名+.alter 计数+added/removed/changed+反硬编 => 收敛为 produce-tool diff CLI 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 sys.executable 解析文本, 不调 hspice), level 缺标应 L1, k_check 字段缺标(header 15 已对账), metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-XaLogCompare-001":
        "FineSim XA log 配对结构化 diff 报告器->produce-tool (Q&A explain-Q&A->produce-tool compare CLI reframe, §4 有牙必要, r747 spotcheck batch25): 用户 e0024852@hfeg0pkn004 (sess 1792118523831_f10db mc68, 与 SpiceDeckPairDiff 同用户不同 session), U0 逐字「you compare the result of /rundata/lacaa/.../CCK_include_rshort1M_1009/xa.log and this log tell me in chinese」; trace 实为多轮 XA log/dspf 对比讲解; A 不可行原因=纯 explain-Q&A(对比两份 FineSim XA log 讲差异)无 runnable artifact 无 check 牙 -> case 抽取「结构化 log diff CLI(xa_log_compare.py 产 JSON)」子技能, A 档 verbatim 合规(U0 原话逐字含真实 /rundata 路径), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.log)+B=synth(待 @A apply 档2); trace 用户=explain-Q&A(讲差异), case 收敛为 produce-tool(写 xa_log_compare.py 产 版本解析/measure 结果/统计/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[tool, ref, cmp, out] 解析文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 xa_log_compare.py 结构化 log diff CLI; check.py 15 断言验 py_compile+CLI 三参+版本解析+measure 结果+统计+反硬编 => 收敛为 produce-tool compare CLI 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 sys.executable 解析文本, 不调 hspice), level 缺标应 L1, k_check 字段缺标(header 15 已对账), metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-ModelLibVerDiff-001":
        "PDK HSPICE model.lib 版本结构化 diff 报告器->produce-tool (Q&A explain-Q&A->produce-tool diff CLI reframe, §4 有牙必要, r747 spotcheck batch25): 用户 e0024852@hfeg0plg79 (sess 1792653194974_s2f9d mc294, 与 SpiceDeckPairDiff/XaLogCompare 同用户三连), U0 逐字「ev06（新）与 Rev05（旧）的区别在那里 就是具体的区别 参数变了 还是什么更改了」; trace 实为 SRAM-tailor DSPF flow 调试 saga, 便携子技能=foundry model-library 版本结构化 diff; A 不可行原因=纯 explain-Q&A(对比两份 PDK HSPICE model.lib 版本讲差异)无 runnable artifact 无 check 牙 -> case 抽取「结构化 model diff CLI(model_lib_diff.py 产 JSON)」子技能, A 档 verbatim 合规(U0 原话逐字), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.lib)+B=synth(待 @A apply 档2); trace 用户=explain-Q&A(讲差异), case 收敛为 produce-tool(写 model_lib_diff.py 产 header version+date 解析/.model 解析/参数 HSPICE 后缀解码/added/removed/changed/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[tool, old, new, out] 解析文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 model_lib_diff.py 结构化 model diff CLI; check.py 16 断言验 py_compile+CLI 三参+header version+date 解析+.model 解析+参数 HSPICE 后缀解码+added/removed/changed+反硬编 => 收敛为 produce-tool diff CLI 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 sys.executable 解析文本, 不调 hspice), level 缺标应 L1, k_check 字段缺标(header 16 已对账), metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-DOERankBuild-001":
        "锥形驱动器 DOE 优化 post-sim ranking 构建器->produce-tool (portability produce-action 全 DOE skill->post-sim ranking 子技能 reframe, §4 有牙必要, r747 spotcheck batch25): 用户 thqu@hfeahpc503 (sess 1793151811279_nrep6 mc215), U2 逐字「把这个锥形驱动器的优化流程做成一个 skill」+ U3「以基础网表为基础生成不同 DOE 的网表, 并进行 Check…告诉我激励是什么…交互式问答」; trace 实为 NAND+三级反相器链 168 design point HSPICE .measure 扫描取 f1/f2/f3/fL, 抽象成通用 DOE-optimizer skill(交互式问答→生成 DOE 网表→HSPICE→排序 CSV); A 不可行原因=produce-action 全 DOE skill 含 HSPICE 真跑+foundry model 不可便携 .75 -> case 抽取「post-sim ranking 子技能(doe_rank.py 跑候选 post-sim 解析排序)」子技能, A 档 verbatim 合规(thqu 原话逐字含 DOE skill 交互式问答需求), reframe 由 portability-driver 非配额驱动(非配额, A 档全流程不可行); asset_fidelity 缺标应 A=trace-verbatim(.lis/.var/.lib)+B=synth(待 @A apply 档2); trace 用户=produce-action(完整 DOE skill), case 收敛为 produce-tool(写 doe_rank.py 读 .lis/.var/.lib/PDP dly×area 排序/延迟排序/top-N/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[script, lis, var, lib, out_csv] 跑候选 post-sim 解析排序, 不启动 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 doe_rank.py post-sim ranking 子技能; check.py 16 断言验 py_compile+读 .lis/.var/.lib+PDP dly×area 排序+延迟排序+top-N+反硬编 => 收敛为 produce-tool post-sim ranking 子技能是让 check() 能区分真假交付的唯一途径(同时保 L1 可便携, 对原 trace 全 DOE skill 形成层级对照), §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 跑候选 post-sim 解析, 不启动 hspice), level 缺标应 L1, k_check 字段缺标(header 16 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-MeaNetPathDiag-001":
        ".meas 节点路径器件实例名 vs net 名错配诊断器->produce-tool (Q&A debug-Q&A->produce-tool diagnose+fixed.sp reframe, §4 有牙必要, r747 spotcheck batch25): 用户 shanliny@hfeg0pkn001 (sess 1793234226913_xtse5 mc43), U0 逐字「为什么我sp文件中的mea语句没法提取相应的数值?」+ io_d0_template.sp + DSPF 附件; trace 56 msgs/3.5MB, 纯症状轮(只给现象+反问, 未给根因/修复), assistant 解析 DSPF 发现 .mea v(xtop.xxsa[1].mpmyrc:s) 用双 x 器件实例路径而非 net 名(单 x)→名字不匹配→提不出数值, 修复=6 条 .mea 节点路径双 x→单 x; A 不可行原因=纯 debug-Q&A(问 .measure 提不出值的根因)无 runnable artifact 无 check 牙 -> case 抽取「诊断脚本+结构化 root_cause+产 fixed.sp(mea_netpath_diag.py)」子技能, A 档 verbatim 合规(U0 原话逐字), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp+.dspf)+B=synth(待 @A apply 档2); trace 用户=debug-Q&A(问根因), case 收敛为 produce-tool(写 mea_netpath_diag.py 产 fixed.sp+diagnosis.md/.measure v() 内不再含双 x 实例前缀/节点路径用单 x net 前缀/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[script] 解析文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 mea_netpath_diag.py 诊断器+fixed.sp; check.py 12 断言验 zip 含脚本+py_compile+无参数/参数错非零退出+产 io_d0_template_fixed.sp+diagnosis.md+保留 B 全部 8 条 .measure 名+.measure v() 不再含双 x 实例前缀+单 x net 前缀条数>=7+真跑候选+反硬编 => 收敛为 produce-tool 诊断器是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 sys.executable 解析文本, 不调 hspice; hspice 仅出现在 .lib 路径字符串 fixture 中), level 缺标应 L1, k_check 字段缺标(header 12 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SpTempParamAlter-001":
        "温度参数化 deck 重写器(.temp 硬编码→.temp {ptemp}+追加 ptemp=25/45/98/130 4 组 .alter)->produce-tool (portability produce-action foundry/HSPICE->deck rewriter 子技能 reframe, §4 有牙必要, r747 spotcheck batch25): 用户 ghyang@hfeg0plg93 (sess 1793240429367_jrjm6 mc62), U39 要求把温度参数化(保留 .param ptemp=-40, 把 .temp -40c 换成 .temp {ptemp}, 删原 pvcsl/pload .alter, 改成 ptemp=25/45/98/130 4 组 .alter); trace agent 写 refactor_temp_alter.py; A 不可行原因=produce-action foundry model+HSPICE V-2023.12 不可便携 .75, 真实 .sp 在 /proj/ddgoa e0031982 无权限读 -> case 抽取「deck 重写器子技能(温度参数化, 文档化结构 B-synthesized)」子技能, B 档 synthesized 合规(还原 Yiotwist corner 多角扫描场景+请写 deck 温度参数化重写器), reframe 由 portability-driver 非配额驱动; asset_fidelity ✓ 已标(synth_deck); trace 用户=produce-action(deck 重写温度参数化), case 收敛为 produce-tool(写 deck 重写器 读 deck/.temp→.temp {ptemp}/删原 .alter/追加 ptemp=25/45/98/130 4 组 .alter/保留 .subckt/.meas/.tran/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable 跑候选改写 .sp 文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 deck 重写器子技能; check.py 14 断言验 py_compile+读 deck+.temp→.temp {ptemp}+删原 .alter+追加 ptemp=25/45/98/130 4 组 .alter+保留 .subckt/.meas/.tran+反硬编 => 收敛为 produce-tool deck 重写器子技能是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑 sys.executable 改写 .sp 文本, 不调 hspice), level 缺标应 L1, k_check 字段缺标(header 14 已对账), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-SpiceInAutoIl-001":
        "Virtuoso IC6.1.7 spiceIn 自动化参数文件生成器(Python 复刻 .il SKILL)->produce-tool (portability produce-action .il SKILL->Python param gen 子技能 reframe, §4 有牙必要, r747 spotcheck batch25): 用户 sierraw@hfeg0plg76 (sess 1793272819713_jo5q8 mc116), U0 逐字「能写个.il文件实现这个功能吗」(Virtuoso IC6.1.7 ISR23 自动化 CDL→schematic 反标); trace agent 查 IC6.1.7 文档+源码确认 GUI 机制后写 381 行 spiceIn_auto.il(DPL+IPC handler+主过程 spiceInAuto 写参数文件并跑翻译器); A 不可行原因=produce-action .il SKILL 依赖 Virtuoso runtime 不可便携 .75, 真实 CDL 在 /proj/lacaa 无权限读 -> case 抽取「Python param gen 子技能(读 config.json 产 spiceInParams DPL 参数文件+构造 spiceIn 命令)」子技能, A 档 verbatim 合规(sierraw 原话逐字含 .il 需求), reframe 由 portability-driver 非配额驱动(A 档 .il 不可行); asset_fidelity ✓ 已标(synth_deck); trace 用户=produce-action(写 .il SKILL 自动化), case 收敛为 produce-tool(写 spicein_param_gen.py 读 config.json/产 spiceInParams DPL 参数文件/构造 spiceIn 命令/覆盖所有 cell 选项/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable 跑候选产文本参数文件, 不调 Virtuoso) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 spicein_param_gen.py Python param gen 子技能; check.py 14 断言验 py_compile+读 config.json+产 spiceInParams DPL 参数文件+构造 spiceIn 命令+覆盖所有 cell 选项+反硬编 => 收敛为 produce-tool Python param gen 子技能是让 check() 能区分真假交付的唯一途径(同时保 L1 可便携, 对原 trace .il SKILL 形成层级对照), §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑 sys.executable 产文本参数文件, 不调 Virtuoso), level 缺标应 L1, k_check 字段缺标(header 14 已对账), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-G5TbGen-001":
        "G5 平台工艺参数 spice testbench 生成器->produce-tool (harness produce-action file->generator script for hidden-B teeth reframe, §4 有牙必要, r747 spotcheck batch25): 用户 wzj@hfeg0pkn002 (sess 1793341820971_f5ser mc96), U0 逐字「帮我建立一个spice的testbench, 其中包含了G5平台的process parameter」; trace 金标准 gen_tb.py 生成 G5_testbench.sp(74 行, 13 项 .param + .inc foundry model + 3 corner alter + DUT 实例); reframe 动因=harness-driver(produce-action「建立 testbench」=交付 .sp 文件 → 交付 generator script, 支撑 §4.1 hidden-B cross-input guard, file→script for teeth); A 档 verbatim 合规(U0 原话逐字), reframe 由 harness-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.sp)+B=synth_deck(待 @A apply 档2); trace 用户=produce-action(建立 TB), case 收敛为 produce-tool(写 TB 生成器 产 deck/.param 工艺参数/.inc model/.lib 3 corner alter/DUT 实例/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable 跑候选产 .sp 文本, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 TB 生成器 script(原 trace 已是 generator, case 形态继承并强化 hidden-B cross-input); check.py 13 断言验 py_compile+产 deck+.param 工艺参数+.inc model+.lib 3 corner alter+DUT 实例+反硬编 => 收敛为 produce-tool generator script 是让 check() 能区分真假交付的唯一途径(同时支撑 hidden-B 反硬编), §4 结构性必要, 保留。注: layer 缺标(None)应补 L1(check 仅 subprocess 跑 sys.executable 产 .sp 文本, 不调 hspice), level 缺标应 L1, k_check=13 ✓ 已标, asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-WtmCrcInjectionAudit-001":
        "WTM CRC 错注入审计器(检查 .v 行能否实现 CRC 错注入目的)->produce-tool (Q&A audit-Q&A->produce-tool audit+JSON reframe, §4 有牙必要, r747 spotcheck batch25): 用户 tongfanl@hfhds201 (sess 1793363756811_iy9oc mc154), U0 逐字「帮我看下/home/tongfanl/DDR6/DSCQA/analogsim/WTM/WTM004_block_check.v文件, 95:97 行能实现在 WTM 期间造 CRC 错的目的吗? 158 行到 161 行能实现在退出 WTM 后造 CRC 错的目的吗?」; trace 实为静态审计 .v 行能否实现 CRC 错注入目的(无 root cause/fix); A 不可行原因=纯 audit-Q&A(检查能否实现目的)无 runnable artifact 无 check 牙 -> case 抽取「审计脚本+结构化 audit report(产 JSON)」子技能, A 档 verbatim 合规(tongfanl 原话逐字含真实 /home 路径+行号 95:97/158:161), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.v)+B=synth(待 @A apply 档2); trace 用户=audit-Q&A(检查能否实现), case 收敛为 produce-tool(写审计脚本 读 .v/定位 95:97 行/定位 158:161 行/WTM 期间 CRC 错注入判定/退出 WTM 后 CRC 错注入判定/结构化 audit JSON/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[sp, wtm_v, \"-o\", out] 解析 .v 文本, 不调仿真器) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产审计脚本+结构化 audit JSON; check.py 15 断言验 py_compile+读 .v+定位 95:97 行+定位 158:161 行+WTM 期间 CRC 错注入判定+退出 WTM 后 CRC 错注入判定+结构化 audit JSON+反硬编 => 收敛为 produce-tool 审计器是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑 sys.executable 解析 .v 文本, 不调仿真器), level 缺标应 L1, k_check 字段缺标(header 15 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-SpiceDeckPairDiff-001": "Q&A explain-Q&A->produce-tool diff CLI",
    "EDA-Eval-DesignFlow-XaLogCompare-001": "Q&A explain-Q&A->produce-tool compare CLI",
    "EDA-Eval-DesignFlow-ModelLibVerDiff-001": "Q&A explain-Q&A->produce-tool diff CLI",
    "EDA-Eval-DesignFlow-DOERankBuild-001": "portability produce-action 全 DOE skill->post-sim ranking 子技能",
    "EDA-Eval-DesignFlow-MeaNetPathDiag-001": "Q&A debug-Q&A->produce-tool diagnose+fixed.sp",
    "EDA-Eval-DesignFlow-SpTempParamAlter-001": "portability produce-action foundry/HSPICE->deck rewriter 子技能",
    "EDA-Eval-DesignFlow-SpiceInAutoIl-001": "portability produce-action .il SKILL->Python param gen 子技能",
    "EDA-Eval-DesignFlow-G5TbGen-001": "harness produce-action file->generator script for hidden-B teeth",
    "EDA-Eval-DesignFlow-WtmCrcInjectionAudit-001": "Q&A audit-Q&A->produce-tool audit+JSON",
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
    print(f"=== r791 batch25 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 171 + {counts['OK']} = {171 + counts['OK']}")


if __name__ == "__main__":
    main()
