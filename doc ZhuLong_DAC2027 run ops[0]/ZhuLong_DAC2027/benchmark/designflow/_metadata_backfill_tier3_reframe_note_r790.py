#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r790 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r746_spotcheck25.tsv (batch24, 8/8 keep_reframe cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r789 档3 batch9-23 done (reframe_note 32->163).
本轮 r790 档3 batch24 (r746 spotcheck25, 8 cases 待 apply). reframe_note 163->171.

reframe_note text = spotcheck25 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck25 8 keep_reframe):
  - portability-driven (private .tr0/.sw/.rundata netlist 不可便携 -> 便携 deck/抽 parse/注入子技能): 4 cases
    C2cRfbCmStab (joeyl@hfeg0plg49, 私有 .tr0 不可便携 -> 便携 hspice deck 产 .tr0 + 抽 parse 子技能) /
    CellLeakageIvPlot (mingyu1l@hfeg0pkn002, 真实 .sw 私有产物不可便携 -> 便携 hspice deck 产 .sw + 抽 parse 子技能) /
    DelvtoInjector (joeyl@hfeg0pkn004, 私有 /rundata netlist 不可便携 -> 便携副本 + 抽 delvto 注入子技能) /
    BatchHspiceSubmit (chapinc@hfeg0pkn002, 同 trace 真跑 hspice 不可便携子集 -> 抽 CLI dry-run 可便携子技能, L2 兄弟 BatchBsubHspice 的 L1 sibling)
  - Q&A/analysis/diag->produce-tool (Q&A-driver, 无 runnable artifact -> 产脚本+JSON 给 check 牙): 2 cases
    DdrVecgenDQSELH (tongfanl@hfhds201, diag-Q&A 对比脚本+诊断根因 -> 产诊断脚本+结构化 root_cause) /
    DelayCornerIdent (declanzh@10.129.2.11, analysis 找极值 -> 产 parser+结构化 report)
  - sub-skill extraction (produce-action 多步流程抽子技能 -> produce-tool generator): 2 cases
    CdlBulkSanitize (e0029495@hfeg0pkn002, 三方交叉验证 trace 抽 bulk 显式化子技能) /
    CxsaDcSweepDeckGen (t0002614@10.129.2.13, produce-action 写具体 deck -> produce-tool 参数化 generator)

spotcheck25 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None→应 L2) 2/8: C2cRfbCmStab/CdlBulkSanitize (check 真跑 hspice 验 sanitized CDL/产 .tr0)
  - layer 缺标/误分类(→应 L1) 4/8: BatchHspiceSubmit(已 r772 normalize L1 ✓)/CxsaDcSweepDeckGen(L2→L1)/DdrVecgenDQSELH(→L1)/DelayCornerIdent(L2→L1)/DelvtoInjector(L2→L1)
    (check 仅 subprocess 跑 sys.executable[SUT 脚本] 产 deck/解析 .mt0/诊断, 不启动 hspice/xmsim)
  - layer=L2 ✓ 正确 1/8: CellLeakageIvPlot (check subprocess 调 hspice 产 .sw)
  - **B 域累计 layer 漏网 31 例**(r789 累计 25 + 本批 6: C2cRfbCmStab/CdlBulkSanitize 缺标应 L2 + CxsaDcSweepDeckGen/DdrVecgenDQSELH/DelayCornerIdent/DelvtoInjector 误分类应 L1), r772 档1 level→layer normalize 漏网之鱼
  - asset_fidelity 缺标 6/8(仅 C2cRfbCmStab=synth_deck ✓ + CellLeakageIvPlot=synth_deck ✓ 已标), 待 @A apply 档2
  - level/tier 缺标或误分类, 待 @A apply 档1 补 sweep
  - k_check 对账 8/8 header==circled 一致, k_check ≥8 ✓ (最低 CdlBulkSanitize/DelayCornerIdent=12)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-BatchHspiceSubmit-001":
        "HSPICE LSF bsub 批量提交脚本 CLI dry-run/--list 子技能->produce-tool (portability produce-action run->produce-tool CLI dry-run reframe, §4 有牙必要, r746 spotcheck batch24): 用户 chapinc@hfeg0pkn002 (sess 1793270732926_ebmf3 mc97, 与 BatchBsubHspice 同 trace 双抽取), trace 用 LSF bsub 批量提交 HSPICE 仿真; A 不可行原因=produce-action 真跑 bsub+hspice 依赖 LSF 集群+foundry PDK 不可便携 .75 -> case 抽取「CLI --dry-run/--list 子技能(batch_submit_hspice.py 仅产 dry-run stdout 结构)」子技能, B 档 synthesized 合规(还原 chapinc 场景列 LSF/HSPICE spec, 比 BatchBsubHspice prompt 详尽), reframe 由 portability-driver 非配额驱动(对应 BatchBsubHspice 的 L2 兄弟); asset_fidelity 缺标应 A=trace-verbatim+B=synth(待 @A apply 档2); trace 用户=produce-action(批量提交跑仿真), case 收敛为 produce-tool(写 batch_submit_hspice.py 产 --dry-run/--list stdout 结构/跨输入 A vs B 反硬编/确定性, check 注释明言 NO real bsub/hspice invocation -- L1 offline) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 batch_submit_hspice.py CLI dry-run; check.py 15 断言验 zip 含脚本+py_compile+--dry-run stdout 结构+--list 输出+反硬编 => 收敛为 produce-tool CLI dry-run 子技能是让 check() 能区分真假交付的唯一途径(同时保 L1 可便携, 对 L2 真跑兄弟 BatchBsubHspice 形成层级对照), §4 结构性必要, 保留。注: layer=L1 ✓ 已 r772 normalize 正确(check 仅 subprocess 跑 sys.executable[script] 取 stdout, 不调 hspice 二进制); level 缺标应 L1, k_check 字段缺标(header 15 已对账), metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-C2cRfbCmStab-001":
        "DDR4 C2C common-mode RFB vs NON-RFB 稳定性对照探针器->produce-tool (portability analysis private .tr0->portable hspice deck+parse reframe, §4 有牙必要, r746 spotcheck batch24): 用户 joeyl@hfeg0plg49 (sess 1793176752981_ikfrw mc34), U0 逐字「跑 C2C common-mode 稳定性仿真, /rundata/m2701/.../C2C/ 下 Tran_RFB 和 Tran(NON-RFB) 各含 45 corner FineSim tran 结果(.tr0), 对照统计 v(xi_wck_c2c_19.out) 在 2n~5n 窗口 avg 电平, 判断 RFB 是否稳定共模」; A 不可行原因=analysis 统计私有 .tr0 Synopsys 二进制 + /rundata/m2701 DDR4 私有目录权限不可便携 .75 -> case 抽取「便携 hspice deck 产 .tr0 + 抽 parse 子技能(zl_c2c_probe.py)」子技能, B 档 synthesized 合规(还原 C2C 场景含真实 /rundata 路径+探针点+45 corner), reframe 由 portability-driver 非配额驱动; asset_fidelity ✓ 已标(synth_deck); trace 用户=analysis(统计对照已有 .tr0), case 收敛为 produce-tool(写 zl_c2c_probe.py 产 report.json/两 variant avg/45 corner mean±std/RFB vs NON-RFB 对照/L2 真跑 hspice 产便携 .tr0 供解析/跨输入 A vs B 反硬编/确定性, subprocess.run([\"hspice\", indep_sp, \"-o\", ...])) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 zl_c2c_probe.py+hspice deck; check.py 14 断言验 py_compile+report.json+两 variant avg+45 corner mean±std+RFB 对照+反硬编 => 收敛为 produce-tool portable deck+parse 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L2(check 真跑 hspice subprocess 产 .tr0), level 缺标应 L2, k_check=14 ✓ 已标, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-CdlBulkSanitize-001":
        "标准单元库 CDL 网表 bulk 显式化清洗器->produce-tool (sub-skill extraction 三方交叉验证->bulk 显式化 reframe, §4 有牙必要, r746 spotcheck batch24): 用户 e0029495@hfeg0pkn002 (sess 1793670518248_ap4dl mc188), U0 逐字「HSPICE 跑标准单元库 CDL 网表做功能验证, 反相器输出电平不对: 输入低时输出本应拉到 VDD, 实际只停 0.47V, 上拉失效, 怀疑 CDL 网表 MOS 写法跟 HSPICE 默认行为不匹配, 请帮我写 sanitize_cdl.py 对 CDL 清洗/补全, 处理后用 HSPICE 跑就能得到正确轨到轨输出」; trace 3 端口 M 行省略 bulk->HSPICE 默认衬底接地->PMOS 衬底错->上拉失效 0.4727V, agent 写 sanitize_cdl 按模型名首字母推断衬底显式化, 修复后 19 cell rc=0; reframe 动因=sub-skill 提取(从三方交叉验证 trace 抽 bulk 显式化子技能, check 真跑 hspice 加牙), B 档 synthesized 合规(还原 0.47V 症状+请写 sanitize_cdl.py, 不告根因/解法, §4 允许); asset_fidelity 缺标应 A=trace-verbatim(real CDL)+B=synth(待 @A apply 档2); trace 用户=produce-tool(写清洗脚本), case 保留同形并加 check 真跑 hspice 验 sanitized CDL 轨到轨输出(给 check 牙), reframe 由 sub-skill-driver 非配额驱动; 重构为产 sanitize_cdl.py+L2 真跑 hspice 验证; check.py 12 断言验 py_compile+3 端口 M 行检测+模型名首字母推断衬底+PMOS→VDD+NMOS→地+L2 真跑 hspice sanitized CDL 轨到轨+反硬编(subprocess.run([hspice_bin, tb, \"-o\", run_dir])) => 子技能提取是让 check() 能区分真假交付(清洗是否真使 HSPICE 输出正确)的唯一途径, §4 结构性必要, 保留。注: layer 缺标(None)应补 L2(check 真跑 hspice subprocess 验 sanitized CDL), level 缺标应 L2, k_check=12 ✓ 已标, metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-CellLeakageIvPlot-001":
        "cell_leakage .sw 文件 HSPICE 私有产物解析+IV 2x2 出图器->produce-tool (portability produce-tool parse private .sw->portable hspice deck+parse reframe, §4 有牙必要, r746 spotcheck batch24): 用户 mingyu1l@hfeg0pkn002 (sess 1793969040205_8yrag mc=0, 低命中但 real_task_summary 完整可溯源, 满足红线 1「有 trace_source」), U0 逐字「请帮我把这个路径下面的 cell_leakage .sw 文件制作成图片. Professional semiconductor device characterization chart, 2x2 grid, 4 器件 NTK WL mid/top/bot/BL Select, X=Vg, Y=|Id| log」; trace agent 逆向 .sw 格式(0030 头/30 变量/13-char 定宽/1e30 哨兵)用 plot_cell_leakage_iv.py 解析+交叉验证 .meas 出 PNG; A 不可行原因=produce-tool 解析真实 .sw 私有 HSPICE 产物不可便携 .75 -> case 抽取「便携 hspice deck 产 .sw + 抽 parse 子技能(parse_sw_iv.py)」子技能, A 档 verbatim 合规(U0 原话逐字含英文 chart spec), reframe 由 portability-driver 非配额驱动; asset_fidelity ✓ 已标(synth_deck); trace 用户=produce-tool(解析 .sw→出图), case 收敛为 produce-tool(写 parse_sw_iv.py/L2 真跑 hspice 在隐藏 B deck 产 B.sw0/.sw0 存在可解析/候选解析器 exit 0 产非空 iv_data.json/4 器件/5 corner/X=Vg/Y=|Id| log/PNG 2x2/跨输入 A vs B 反硬编/确定性, subprocess 调 hspice 产 .sw) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 parse_sw_iv.py+hspice deck; check.py 14 断言验 py_compile+真跑 hspice 产 .sw+解析器 exit 0+4 器件+5 corner+X=Vg/Y=|Id| log+PNG 2x2+反硬编 => 收敛为 produce-tool portable deck+parse 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 ✓ 已正确(check 真跑 hspice subprocess 产 .sw), level 缺标应 L2, k_check 字段缺标(header 14 已对账), mc=0 备注(低命中但 trace 真实可溯源, 不违反红线), metadata bug 待 @A apply 档1 补 sweep。",
    "EDA-Eval-DesignFlow-CxsaDcSweepDeckGen-001":
        "CXSA1x4_1C2A 灵敏放大器 DC sweep deck 参数化生成器->produce-tool (sub-skill extraction produce-action 写具体 deck->produce-tool 参数化 generator reframe, §4 有牙必要, r746 spotcheck batch24): 用户 t0002614@10.129.2.13 (sess 1794379471399_jp83r mc105), U0 逐字「CXSA1x4_1C2A 灵敏放大器静态特性仿真, 根据网表 netlist 和参考测试网表写一份直流仿真测试 deck. TT/125℃/直流/vad2!=1.4V/Iso 关/Sel=1.77V/OC 与 PreEq 栅压同绑 Vdleq 扫描 1.17→1.77V 看 BL 电压」; trace agent 读网表定位 Iso/Sel/OC/PreEq/SA-core, 写 sim_dc.sp + check_lib.py; reframe 动因=sub-skill 提取(produce-action 写具体 deck -> produce-tool 参数化 generator, manifest 驱动 hidden-B), B 档 synthesized 合规(还原 SA 场景+请写参数化 Python 生成器 dc_sweep_deckgen.py 读 manifest 产 deck, 比原 trace 的「写具体 deck」升级为参数化 generator); asset_fidelity 缺标应 A=trace-verbatim(netlist)+B=synth(待 @A apply 档2); trace 用户=produce-action(写 DC sweep deck), case 收敛为 produce-tool(写 dc_sweep_deckgen.py 读 manifest 产 deck/.lib TT/.inc netlist/.dc sweep pvdleq 1.17 1.77 0.01/.probe v(Bla<0>)/.measure/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[gen_py, manifest, -o, out] 产 deck, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 dc_sweep_deckgen.py 参数化 generator; check.py 13 断言验 py_compile+读 manifest+产 deck+.lib TT+.inc netlist+.dc sweep+.probe+.measure+反硬编 => 子技能提取(参数化 generator)是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 跑 generator python 产 .sp 文本不启动 hspice), level 缺标应 L1, k_check 字段缺标(header 13 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-DdrVecgenDQSELH-001":
        "DDR vecgen Aging 仿真 DQSELH define 缺失根因诊断器->produce-tool (Q&A diag-Q&A->produce-tool diagnose+JSON reframe, §4 有牙必要, r746 spotcheck batch24): 用户 tongfanl@hfhds201 (sess 1794131955891_zm0zw mc92), U0 逐字「帮我对比下 ./runsti/gen_stimulus_Aging 和 run_compress 两个激励生成脚本, 告诉我为啥跑 Aging 仿真会报错, 并给出修复. 报错: xmsim *E,ERRSEV Compress_task.v:268 '1p6 mode, dqselect=0, dq0 can not input'」; trace agent 定位根因: gen_stimulus_Aging 第7行 -d 'WRNOPAD NOENDMRR AGING' 缺 DQSELH define; A 不可行原因=纯 diag-Q&A(对比+诊断+给修复)无 runnable artifact 无 check 牙 -> case 抽取「静态解析脚本+结构化 root_cause 产诊断脚本+JSON」子技能, A 档 verbatim 合规(tongfanl 原话逐字含真实报错+/proj 路径), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(scripts)+B=synth(待 @A apply 档2); trace 用户=diag-Q&A(对比+诊断+给修复), case 收敛为 produce-tool(写诊断脚本产 root_cause 定位+缺 DQSELH define+修复建议+跨输入 A vs B 反硬编+确定性, subprocess.run 跑 sys.executable[model, \"--defines\", ...] 验 root_cause 定位, 不调 hspice/xmsim 二进制) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产诊断脚本+结构化 root_cause JSON; check.py 14 断言验 zip 含脚本+py_compile+root_cause 定位+缺 DQSELH define+修复建议+反硬编 => 收敛为 produce-tool 诊断器是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 跑 SUT python 诊断脚本不启动 hspice/xmsim), level=L2 误分类应改 L1(同因), k_check 字段缺标(header 14 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-DelayCornerIdent-001":
        "HSPICE MC 仿真 .mt0 多工艺角 delay 极值定位+分组报告器->produce-tool (Q&A/analysis analysis 找极值->produce-tool parser+report reframe, §4 有牙必要, r746 spotcheck batch24): 用户 declanzh@10.129.2.11 (sess 1794450128835_b497y mc462, 高命中), U0 逐字「在 HSpice MC 仿真目录下, measurement.mt0 含多工艺角(alter#)×多偏置(index)组合下的 delay_fall_ns 和 delay_rise_ns, 找出全局 max 和 min, 按 alter# 分组报告每角 min/max 范围, 标注产生极值的条件(index/pvwlp/pvfsbln/temper/alter#)」; 228 行=19 alter#×12 index; A 不可行原因=纯 analysis(解析 .mt0 报极值)无 runnable artifact 无 check 牙 -> case 抽取「parser+结构化 report(delay_corner_checker.py)」子技能, B 档 synthesized 合规(还原 .mt0 格式+列顺序+请做极值分析), reframe 由 Q&A/analysis-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(.mt0)+B=synth(待 @A apply 档2); trace 用户=analysis(解析 .mt0 报极值), case 收敛为 produce-tool(写 delay_corner_checker.py 产 全局 max+min delay_fall+delay_rise/按 alter# 分组/标注极值条件 index/pvwlp/pvfsbln/temper/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[script, \"spec_B.json\"] 解析 .mt0, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 delay_corner_checker.py+结构化 report; check.py 12 断言验 py_compile+读 .mt0 跳过注释行+全局 max+min delay_fall+delay_rise+按 alter# 分组+标注极值条件+反硬编 => 收敛为 produce-tool parser+report 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 跑 SUT python 解析 .mt0 不启动 hspice), level 缺标应 L1, k_check 字段缺标(header 12 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-DelvtoInjector-001":
        "ULVT delvto netlist 注入器(netlist 加 vth 偏移+幂等替换+verify diff)->produce-tool (portability produce-action run->portable copy+inject sub-skill reframe, §4 有牙必要, r746 spotcheck batch24): 用户 joeyl@hfeg0pkn004 (sess 1794452932656_i7nlb mc165), U0 逐字「请帮忙用这个: /home/joeyl/ulvt_delvto/reduce_vth.py 给 /rundata/m2701/.../Bias/hspiceD/.../netlist 加 vth=-0.2v, 再替换为 -0.1, 并对 CML_C2C netlist 同样处理」; trace agent 读 AI_USAGE.md/reduce_vth.py/config.cfg, 因 /rundata 只读先拷 netlist 到可写区, 改 config.cfg 指向副本, 跑 reduce_vth.py(pulvt_ckt/nulvt_ckt X 实例追加 _delvto 幂等), verify_netlist.py 逐行 diff; A 不可行原因=produce-action 跑 reduce_vth.py 依赖 /rundata/m2701 项目目录权限受限不可便携 .75 -> case 抽取「便携副本 + 抽 delvto 注入子技能(delvto_injector.py)」子技能, B 档 synthesized 合规(还原 ULVT delvto 场景+/rundata 只读需先拷+请写 delvto_injector.py), reframe 由 portability-driver 非配额驱动; asset_fidelity 缺标应 A=trace-verbatim(netlist)+B=synth(待 @A apply 档2); trace 用户=produce-action(跑 reduce_vth.py 注入 delvto), case 收敛为 produce-tool(写 delvto_injector.py 读 config.cfg/pulvt_ckt+nulvt_ckt X 实例追加 _delvto/幂等替换/续行+注释+精确 token/verify_netlist diff/跨输入 A vs B 反硬编/确定性, subprocess 仅跑 sys.executable[\"delvto_injector.py\",\"config.cfg\"] 三处, 不调 hspice) 给 check() 牙(§4.1 hidden-B cross-input guard + §4.9 反硬编); 重构为产 delvto_injector.py 子技能; check.py 13 断言验 py_compile+读 config.cfg+pulvt_ckt+nulvt_ckt X 实例追加 _delvto+幂等替换+verify_netlist diff+反硬编 => 收敛为 produce-tool portable copy+inject sub-skill 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L2 误分类应改 L1(check 跑 SUT python 注入脚本不启动 hspice), level 缺标应 L1, k_check 字段缺标(header 13 已对账), asset_fidelity 缺标, metadata bug 待 @A apply 档1/档2 补 sweep。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-BatchHspiceSubmit-001": "portability produce-action run->produce-tool CLI dry-run",
    "EDA-Eval-DesignFlow-C2cRfbCmStab-001": "portability analysis private .tr0->portable hspice deck+parse",
    "EDA-Eval-DesignFlow-CdlBulkSanitize-001": "sub-skill extraction 三方交叉验证->bulk 显式化",
    "EDA-Eval-DesignFlow-CellLeakageIvPlot-001": "portability produce-tool parse private .sw->portable hspice deck+parse",
    "EDA-Eval-DesignFlow-CxsaDcSweepDeckGen-001": "sub-skill extraction produce-action 写具体 deck->produce-tool 参数化 generator",
    "EDA-Eval-DesignFlow-DdrVecgenDQSELH-001": "Q&A diag-Q&A->produce-tool diagnose+JSON",
    "EDA-Eval-DesignFlow-DelayCornerIdent-001": "Q&A/analysis analysis 找极值->produce-tool parser+report",
    "EDA-Eval-DesignFlow-DelvtoInjector-001": "portability produce-action run->portable copy+inject sub-skill",
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
    print(f"=== r790 batch24 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 163 + {counts['OK']} = {163 + counts['OK']}")


if __name__ == "__main__":
    main()
