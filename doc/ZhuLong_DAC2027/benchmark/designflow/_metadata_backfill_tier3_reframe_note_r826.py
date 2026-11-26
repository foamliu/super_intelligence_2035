#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r826 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch1.
Source: r825 bounded queue 提议 (asset_fidelity 100% 收口后下一道 bounded queue =
        reframe_note backfill 160 missing P1). 本轮 batch1 = alphabetical 首 12 missing.
Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). 本轮 r826 起 await-scan 期接续 backfill reframe_note 160 missing, batch1 12 case.
      reframe_note 235->247, miss 160->148.

reframe_note text 来源:
  - keep_reframe_for_teeth case: spotcheck per_case_reasoning + cases/B trace_source(user@host/session/mc)
    + test_rationale k_check + asset_fidelity; driver 分类(portability/Q&A-analysis/harness).
  - keep_faithful case: r825 §观点(3) disclosure 完整性 — keep_faithful case 亦补 reframe_note
    记录「无 reframe + trace 意图同形便携判据」, §5 asset_provenance disclosure 成对字段完整。
    文本以 "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r7XX spotcheck batchN)" 开头。

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 4 keep_reframe portability + 8 keep_faithful):
  - portability-driver (foundry PDK / 完整流含 OA / FineSim+foundry 不可沙盒复刻 → level-1 proxy / 子流抽取):
      4 case: AOI21ArcChar / AlterDeckSplit / ButterflyCurve / CTLEAC
  - Q&A-analysis-driver: 0 case
  - harness-driver: 0 case
  - keep_faithful (无 reframe, trace 意图同形便携): 8 case:
      BatchBsubHspice / BisecMt0SmCalc / BistOscRccReorder / BlSpfCapClassify /
      BmatrixRerunGen / BndGaussPwlGen / CTLESpec / CTLETranDeck

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer/level 缺标或误判 (应 L1/L2), k_check 字段缺标, shard 缺标, asset_fidelity 个别应微调
  - 与 r773-r800 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 4 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-AOI21ArcChar-001":
        "AOI21 input-arc timing 表征 harness->produce (portability reframe, B档 sub-task + asset_fidelity, §4 有牙必要, r727 spotcheck batch7): 用户 e0029308@hfeg0pkn001 (sess 1792380576403_uumms, mc=343) 做 AIOI21 标准单元 input-arc timing 表征(Maestro/ADE AMS, FineSim GLIBCXX 冲突→xrun 跑通), 真实意图=把这一套沉淀成可复用 AOI21 input-arc 表征 Python harness; A 不可行原因=完整流用 Maestro/ADE+FineSim/xrun+foundry PDK 不可沙盒复刻 → 抽取「7 arc×2 corner×2 load=28 combo + degenerate arc 标识 + per-arc worst」子流 + HSPICE level-1 SPICE cell 库 proxy(asset_fidelity=synth_deck); reframe 由 portability-driver 非 Q&A/配额驱动; check.py 13 断言验 harness 在 hidden B 上 subprocess 真跑 HSPICE + 28 combo + degenerate arc + per-arc worst => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer/level 应 L2(check 真跑 HSPICE 二进制)。",

    "EDA-Eval-DesignFlow-AlterDeckSplit-001":
        "AF eFuse 阵列多 .alter PVT 角扫描 deck 拆分器->produce (portability reframe, B档 sub-task + asset_fidelity, §4 有牙必要, r727 spotcheck batch7): 用户 yueliu@hfeahpc501 (sess 1793093197648_x2w2z, mc=303) 用 FineSim 跑 AF_Blown_Array_Block eFuse 阵列多 .alter PVT 角扫描 deck, 真实意图=多 .alter PVT 角扫描 deck 拆分忠实; A 不可行原因=完整流用 FineSim V-2023.12+foundry 模型不可沙盒复刻 → 抽取「多 .alter deck 拆 N=3 自洽单角 deck + .alter 块消除 + .lib 角名 + .ic 收敛辅助 + split[i]==alter[i] HSPICE 等价验证」子流, .75 HSPICE V-2023.12-SP1-1 真跑 level-1(asset_fidelity=synth_deck); reframe 由 portability-driver; check.py 10 断言验 deck 拆分器在 hidden B 上拆 N=3 + .alter 消除 + .lib 角名 + split[i]==alter[i] HSPICE 等价 => 收敛为 produce-deck-splitter 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。",

    "EDA-Eval-DesignFlow-ButterflyCurve-001":
        "6T SRAM 直流 SNM 蝴蝶曲线表征 harness->produce (portability reframe, foundry PDK→level-1 proxy, §4 有牙必要, r724 spotcheck batch5): 用户 e0030760@hfeg0pkn002 (sess 1793155079677_gnmu0, mc=293) 做 6T SRAM 单元直流 SNM 表征(手写 vtc_a.sp/vtc_b.sp 交叉耦合反相器对 + plot_butterfly.py 解析 HSPICE .lis SI 后缀算最大内接正方形 SNM≈0.306V), 真实意图=SNM 表征忠实; A 不可行原因=foundry PDK 不可沙盒复刻 → 便携化为 level-1 Shichman-Hodges MOS + HSPICE .dc/.PRINT harness(butterfly_gen.py 自包含 level-1 .dc 扫两条 VTC + .lis SI 解析 + 蝴蝶曲线交叉 + 最大内接正方形 SNM, .75 HSPICE V-2023.12-SP1-1 真跑, asset_fidelity=synth_deck, P-005 §9 line 27 机制); reframe 由 portability-driver(foundry PDK 不可复刻); check.py 18 断言真跑 HSPICE hidden B + result_B.json 必需键齐全(curve_a/b_points/snm/symmetry_residual/vdd/n_points/hspice_ran) + hspice_ran==true + cross-input guard => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。",

    "EDA-Eval-DesignFlow-CTLEAC-001":
        "CTLE 接收端 AC 仿真+spec 自检 harness->produce (portability reframe, B档 sub-task extraction, §4 有牙必要, r727 spotcheck batch7): 用户 alenxu@hfeg0pkn003 (sess 1790142100320_n91pk, mc=755) DFE_alenxu 接收端 CTLE 设计完整流(spec→网表→FineSim AC/眼图→.meas→PVT→OA 原理图, 1017 msgs/465 tool_use), 真实意图=CTLE 设计完整流忠实; A 不可行原因=完整流含 OA 原理图 pyAether GUI 不可沙盒复现 → 抽取「AC 仿真 + .meas/.op 解析 + spec-check harness」子流(asset_fidelity=synth_deck); reframe 由 portability-driver(完整流含 OA 不可复现), 非 Q&A→produce; check.py 12 断言验 harness 在 hidden B 上 subprocess 真跑 FineSim + 4 spec_checks + .op idd 解析(防 .meas idd 返回~0 stub) => 收敛为 produce-harness 子流抽取是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。",

    # ===== 8 keep_faithful (无 reframe, trace 意图同形便携) =====
    "EDA-Eval-DesignFlow-BatchBsubHspice-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r746 spotcheck batch25): 用户 chapinc@hfeg0pkn002 (sess 1793270732926_ebmf3, mc=97) U0 逐字「你能帮我写一个python脚本自动往队列提交仿真吗，需要什么信息跟我提」, 意图形态=produce-action(写脚本自动 bsub 提交 hspice), 可便携性=中(LSF bsub + hspice 真跑, .75 上 hspice 可跑便携 stub deck); trace agent 经 5 轮 ask_question 锁 spec → editor 写 batch_submit_hspice.py → --dry-run/--help 验证, case 交付 batch_submit_hspice.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe, trace 意图与 case 交付同形); check.py 11 断言验 py_compile/--help/--list 4 .sp/--dry-run 4 bsub/bsub 结构/stem 推导/默认 SPEC-faithful/--exclude/覆盖生效/L2 真跑 hspice B inv_tb.sp job concluded/跨输入 A vs B 反硬编码 => §4 牙由 hidden-B cross-input + §4.2 subprocess 真跑 hspice 保证, 无 reframe, 保留。**metadata bug 待 @A**: level 缺标应 L2, k_check 字段缺标应 11(header 已 11)。",

    "EDA-Eval-DesignFlow-BisecMt0SmCalc-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r753 spotcheck batch32): 用户 xuelianf@hfeg0pkn002 (sess 1794206448451_z4swx, mc=214) U0 逐字「请写一个程序，取出同时带有关键词D1和关键词bisec_mt0文件内第4行第1列的数据记为vtarget_D1，按照公式(0.93*1000-vtarget_D1*1000)*0.156-36.43计算SM1...输出格式 directory,SM1,SM0...」, 意图形态=produce-action(写计算程序), 可便携性=高(纯文本后处理, 无 EDA 二进制依赖); trace agent 写 calc 脚本, case 交付 calc_sm.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 14 断言验候选 calc_sm.py + §4.1 hidden B cross-input(B1/B2 cwd 不同反硬编码)+§4.4 zip 含脚本+py_compile+CSV 表头==directory,vtarget_D1,vtarget_D0,SM1,SM0+行数==5+directory 列+vtarget 独立重算+SM1/SM0 独立重算+3 位小数 => §4 牙由 hidden-B cross-input 保证, layer=L1(check 仅 subprocess 跑候选 python 解析 .bisec_mt0 文本+验 CSV, 无 EDA 二进制), 无 reframe, 保留。**metadata bug 待 @A**: level 缺标应 L1, asset_fidelity 应标 real-from-trace(用真实 PrimeSim bisec_mt0 目录树结构合成), shard 缺标应 B。",

    "EDA-Eval-DesignFlow-BistOscRccReorder-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r724 spotcheck batch5): 用户 johnl@hfeg0pfn119 (sess 1792483903326_cllpy, mc=354) DRAM BIST 振荡器 T_BistOsc 表征批量仿真全 corner 跑失败, 3 个具体请求(① RCC 路径修正 T_BistOscNew.spf.RCC→T_BistCtrlNew.spf_RCC ② gen_var_osc() 11 行→256 行全扫描顺序 [0..4]+[251..255]+[5..250] ③ 输出修正后 gen_osc_case.py + fixed_T_BistOsc.sp + diagnosis.json), 意图形态=produce-action(修脚本+修 deck+诊断), 可便携性=中(FineSim 真跑, L2); prompt A-faithful verbatim 逐字还原 3 请求, case 交付 fixer+gen_osc_case_fixed+fixed_T_BistOsc.sp+diagnosis.json 同形(零偏移); reframe_note=None→补(faithful 无 reframe, 含真实踩坑 RCC 文件名混淆 BistOsc/BistCtrl); check.py 16 断言验 zip 含 5 文件 + diagnosis 指出缺失 RCC 与正确 RCC + NETLIST_PATH==T_BistCtrlNew.spf_RCC + gen_var_osc() 产 256 行 + var_osc 顺序正确 => §4 牙由 hidden-B cross-input + L2 真跑 FineSim 保证, 无 reframe, 保留。",

    "EDA-Eval-DesignFlow-BlSpfCapClassify-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r754 spotcheck batch33): 用户 mhyu@hfeg0plg49 (sess 1794294098670_kpqjv, mc=0, legacy 低于 mc>=10 阈值审计判意图非判 mc 保留) 在 /proj/x0s0f/V0/ver/pex/mhyu 下对六种 BL routing 的 SPF 结果做「按 BL 索引范围提取并分类寄生电容(对地/耦合/总计)」, 意图形态=produce-action(verb 提取+分类=action), 可便携性=高(纯 SPF 文本后处理, 无 EDA 二进制); trace agent 跑 spf_bl_extract_fixed.py, case 交付 spf_bl_extract_fixed.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 12 断言验候选 spf_bl_extract_fixed.py + §4.1 hidden B1 cross-input(--range 0-23 非 A 的 0-15)+§4.4 zip+py_compile+CLI exit0+CSV 表头严格 bl_index,net,cap_type,coupled_net,cap_value_pf+48 行 ground+BL0 ground 容差±1e-3+coupling 容差+total=ground+sum(coupling)+无负电容+反硬编码 => §4 牙由 hidden-B cross-input 保证, layer 应 L1(check subprocess 跑候选 python 解析 SPF 文本+验 CSV, 0 EDA 二进制), 无 reframe, 保留。**metadata bug 待 @A**: layer/level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-BmatrixRerunGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r741 spotcheck batch20): 用户 yuankong@hfhds201 (sess 1792395143753_ai203, mc=14) U12 逐字「帮我写个脚本，我可以在某个路径下...执行bmatrix -f...将其转换成另一种格式,生成文件sim.save_rerun,格式转换示例...」, 意图形态=produce-tool(显式要求写脚本+生成文件), 可便携性=高(纯文本格式转换, 无 EDA 二进制); trace 末轮 assistant ask_question 未答未产出最终脚本, case 基于 U12 自含转换示例合成便携 L1 Python(去 Fail+primesim. 前缀+job 最后 '.' 换空格+前拼 BASE 路径), A-faithful 意图 + B-synth 实现(trace 未产出); reframe_note=None→补(faithful 意图零偏移, 实现因 trace 未产出而合成); check.py 12 断言验 .py 脚本+sim.save_rerun + §4.1 hidden B cross-input(B 输出行数恰 5 仅 Fail 行 + Pass/空行/Other 排除 + 格式转换规则校验, B 值与 A 反)+§4.9 反硬编 + 无参数/输入缺失非零退出 => §4 牙由 hidden-B cross-input 保证, level=L1(check 仅 subprocess 跑候选 python 解析文本格式转换, 不启动 EDA 工具), 无 reframe, 保留。**metadata bug 待 @A**: k_check/k_rationale 字段缺标应 12, layer 缺标应 L1。",

    "EDA-Eval-DesignFlow-BndGaussPwlGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r738 spotcheck batch17): 用户 joeyl@hfeg0plg49 (sess 1790572773219_t5osd, mc=56) 逐字「我想在电路仿真中加一个电源噪声，它是高斯分布...生成一个可以直接被testbench inc的PWL文件，你可以帮我写这么一个生成脚本吗」, 意图形态=produce-action(写生成器产 PWL), 可便携性=高(纯算法脚本, 无 foundry 依赖); trace agent 写 generate_noise_pwl.py(白噪声→FFT→余弦滚降带通掩码→IFFT→缩放 sigma→时域包络→+DC mean→SPICE PWL), case 忠实复刻同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 15 断言验 generate_noise_pwl.py+.pwl + §4.1 hidden B cross-input guard + §4.9 防硬编/防 print-expected + 可复现(同 B 两次 sha256 同)+种子敏感+高斯分布 mean/std+带通能量占比>0.55+tstart 受控+DC mean 控制+3x 幂等 => §4 牙由 hidden-B cross-input 保证, level=L1(check 仅 subprocess 跑候选 python 产 PWL, 不启动 HSPICE), k_check=15==k_rationale=15 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标(level 已 L1 应补 layer:L1 一致)。",

    "EDA-Eval-DesignFlow-CTLESpec-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r723 spotcheck batch4): 用户 cwei@hfeg0plg93 (sess 1790487462826_wb03t, mc=691) SpiceAgent CTLE 接收端 AC spec 合规(spec.md→dut/tb→FineSim AC→解析 .meas), 意图形态=produce-tool(ctle_spec_check.py harness=用户真实交付 AC spec 合规自检), 可便携性=中(FineSim 真跑, L2); trace agent 产 spec-check harness, case 交付 ctle_spec_check.py 同形(零偏移); reframe_note=None→补(faithful 无 reframe); check.py 12 断言验 FineSim 真跑 hidden B + dc_g/hf_g/peaking 金标准 tol + failed-measure 处理 => §4 牙由 hidden-B cross-input + L2 真跑 FineSim 保证, 无 reframe, 保留。",

    "EDA-Eval-DesignFlow-CTLETranDeck-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r741 spotcheck batch20): 用户 kaixuanx@hfeg0pkn002 (sess 1792720528359_2tuxj, mc=183) U0 逐字「我设计了一个CTLE电路...我已经仿真了CLTE的AC性能ctle_act_ind.sp，现在我想仿真相关的瞬态性能ctle_act_ind_tran.sp，我需要你帮我总结一下需要仿真的各项性能指标，并帮我重新写一个仿真脚本」, 意图形态=produce-action(总结指标+重写仿真脚本), 可便携性=高(check 阶段验 .sp 文本内容不启动 HSPICE, L1); trace agent 发现 PRBS() 不被 HSPICE 识别改用 LFSR() 源, 产 ctle_act_ind_tran_v2.sp(.TRAN 1024 bit@7.2Gbps + 5 类 .MEAS: 眼图/延迟/过冲/共模/功耗), case 忠实复刻 produce-tool(交付 gen_ctle_tran_deck.py 生成 tran deck)同形(零偏移, A-faithful); reframe_note=None→补(faithful 无 reframe); check.py 15 断言验 gen_ctle_tran_deck.py+out.sp + §4.1 hidden B cross-input guard(B out.sp .TRAN + LFSR/PRBS 源非 PULSE + 差分输入 + 5 类 .MEAS + 眼图/延迟/过冲/共模/功耗, B 值与 A 反)+§4.9 反硬编 => §4 牙由 hidden-B cross-input 保证, level 应 L1(check.py 仅 subprocess 跑候选 python 产 out.sp 文本, 验 .sp 内容不启动 HSPICE), k_check=15==k_rationale=15 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1, level 缺标应 L1。",
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
