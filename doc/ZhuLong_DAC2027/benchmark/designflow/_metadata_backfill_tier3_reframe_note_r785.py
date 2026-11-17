#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r785 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r741_spotcheck20.tsv (batch19, 8 keep_reframe of 12 cases).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r784 档3 batch9-18 done (reframe_note 32->117).
本轮 r785 档3 batch19 (r741 spotcheck20, 8 cases 待 apply). reframe_note 117->125.

reframe_note text = spotcheck20 per_case_reasoning + cases/B trace_source(user@host) + test_rationale k_check.
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck20 8 keep_reframe):
  - foundry-PDK-unportable produce-action->produce-tool (portability-driver): 4 cases
    VihTripTune (jasminej@hfeahpc505, DfeTop6M6V2 foundry PDK) /
    PVTvarSpecJudge (tongni@hfeg0pkn002, bsub finesim + foundry PDK) /
    StdLibCharTmpl (t0002801@hfeg0plg99, Empyrean Qualib TCL 非便携) /
    TxRonSize (alenxu@hfeg0pkn003, foundry BSIM ptn_lv/ntn_lv)
  - analysis/Q&A->produce-tool 分析器/诊断器 (Q&A-driver): 2 cases
    TrngTranNoise (justind@hfeg0plg53, how-to/Q&A「怎么仿真」) /
    SizingSensDiag (curryxu@hfeg0plg99, analysis「帮我看一下」)
  - produce-action upload/import->produce-tool (sub-skill 提取): 2 cases
    OtaMa0SpecCheck (zhukaic@hfeg0plg58, upload-action -> .ma0 parser+checker) /
    LvDpathCdlImport (jiashengz@hfeg0plg92, Aether import 行为级不可行 -> CDL+topology checker)

4 keep_faithful (Vcc2scVarJudge/PostSimDeckBatch/BmatrixRerunGen/CTLETranDeck) 零偏移, 不需 reframe_note.
spotcheck20 关键发现 2: 3 例 layer=L2 误标应改 L1 (TrngTranNoise/OtaMa0SpecCheck/LvDpathCdlImport, check 仅 subprocess 跑候选 python 不启动 EDA 工具)
  - reframe_note backfill scope 限定不修 layer, 在 note 文本标注 layer bug 待 @A 档1 补 sweep (与 r783 AgingDirSeparateTransform layer=None 同型第三型).
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-VihTripTune-001":
        "VIH 翻转点 4 宽度调优 harness->produce-tool (portability produce-action->produce-tool 调优器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 jasminej@hfeahpc505 原话「这是我的testbench,帮我修改网表中DfeTop6M6V2网表中MP28/23/10/3的尺寸（在现有尺寸附近微调），使得输出的csv文件中从0到1（>0.8）的翻转点在vih=170上，并且使得=1/2/3的翻转点结果尽可能接近」(produce-action 调参优化, deepread 1792143054616_zr9dt mc212), trace agent 写 launch_edit.run.sh 跑 exp1 但环境反复卡(LD_PRELOAD/libstdc++/后台进程被中止), 用户「中止把」, trace 未达调优终态; DfeTop6M6V2 走 foundry PDK 不可便携 .75; A 不可行原因=foundry PDK 不可便携 .75 -> case 抽取「4 宽度调优使 VIH DC 翻转点命中 target」子技能, DUT level-1 Shichman-Hodges, HSPICE V-2023.12-SP1-1 真跑, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity 缺标应 synth_deck (DfeTop6M6V2 foundry 场景便携化为合成 slice_A.sp, 待 @A apply 档2); layer=L2 ✓(已标 level=L2, check 真跑 HSPICE, hdr 14 conditions); trace 用户=produce-action(「帮我修改...尺寸...使得...」= 调参优化), case 收敛为 produce-tool(写 vih_tune.py 调优 harness 真跑 HSPICE sweep) 给 check() 牙(§4.1 hidden-B cross-input guard B widths.json 4 键 + 命中 target + spread 容差, B 值与 A 反 + §4.9 反硬编); 重构为产 vih_tune.py+HSPICE 真跑; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(foundry PDK 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TrngTranNoise-001":
        "FineSim 双RO TRNG 瞬态噪声 deck 注入器->produce-tool (Q&A/how-to->produce-tool deck 注入器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 justind@hfeg0plg53 原话「finesim前仿怎么仿真真随机数生成电路？」+「这是我的testbench 我怎么修改？」(how-to/Q&A 问方法+改 testbench, trace 1792204147117_hsrib 84 msgs), 原 .tran 1p 1900n 未启用瞬态噪声->TRNG1 恒定; 首改 NOISETMIN=1e-15+NOISEFMAX=100G 卡死 0.0%; 终解 .tran 1p 1900n NOISE=1 NOISEFMIN=1 NOISEFMAX=10G NOISESCALE=1 NOISESEED=1 + 全局 .option; A 不可行原因=真实 testbench 生产文件 SUT 沙盒不可达 -> case 抽取「给 FineSim testbench 注入瞬态噪声选项产 out.sp」子技能, B 档 synthesized 合规, reframe 由 Q&A/how-to→produce-tool 驱动非配额驱动; asset_fidelity 缺标应 synth_deck (真实 FineSim testbench 场景便携化为合成 deck, 待 @A apply 档2); trace 用户=Q&A/how-to(「怎么仿真」「我怎么修改」= 问方法), case 收敛为 produce-tool(写 enable_trng_noise.py 注入器产 out.sp) 给 check() 牙(§4.1 hidden-B cross-input guard B out_B.sp .tran NOISE=1 + NOISEFMAX=10G 非 A 50G + NOISESEED 非 A + 差分源, B 值与 A 反 + §4.9 反硬编); 重构为产 enable_trng_noise.py+out_B.sp; check.py 12 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/how-to 无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: level=L2 误标应改 L1(check 仅 subprocess 跑候选 python 产 out_B.sp 文本, 不启动 FineSim, 与 CTLETranDeck 同为 deck 生成), metadata bug 待 @A apply 档1 补 sweep (与 r783 AgingDirSeparateTransform layer=None 同型第三型)。",
    "EDA-Eval-DesignFlow-PVTvarSpecJudge-001":
        "PVT-corner 变化量 SPEC 合规判定器->produce-tool (portability produce-action->produce-tool 判定器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 tongni@hfeg0pkn002 原话「这个语句丢仿真……variation 是所有 corner 的电压的分布范围要小于 5mV，所以你要读取 measure 的文件，做判断，并给出优化策略」(produce-action 跑仿真+判定+优化), trace agent 走 LSF bsub + foundry PDK 不可便携, 写 check_vcc2sc_stdby_var.py 解析 .mt0 算 variation 判 FAIL(unload 5.13mV/load1mA 15.26mV); A 不可行原因=foundry PDK + LSF bsub 不可便携 .75 -> case 抽取「PVT variation SPEC 合规判定器」子技能, DUT level-1 PMOS 自偏置 Vcc2sc, hspice .alter 跑 PVT corner, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, check 真跑 HSPICE); trace 用户=produce-action(「丢仿真...读取...做判断...给出优化策略」= 跑+判+优化), case 收敛为 produce-tool(写 pvt_var_judge.py 判定器真跑 HSPICE) 给 check() 牙(§4.1 hidden-B cross-input guard B sim_log 'job concluded' + .mt 文件 + hspice_rc=0 + 解析 .alter variation + PASS/FAIL, B 值与 A 反 + §4.9 反硬编); 重构为产 pvt_var_judge.py+HSPICE 真跑; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(foundry PDK 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: 与 Vcc2scVarJudge-001 同 session_file z6mt7 双抽取(不同子技能: A-faithful 解析判定器 vs B-synth 真跑判定器, check.py 异构), host 字段不一致(pkn002 vs pkn001)是 metadata bug 待核。",
    "EDA-Eval-DesignFlow-StdLibCharTmpl-001":
        "标准单元库 corner 参数化表征模板生成器->produce-tool (portability produce-action->produce-tool deck 生成器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 t0002801@hfeg0plg99 原话「检查STD 的tcl...TT corner 1.8V 25度...我要一个模板」(produce-action 生成参数化表征模板, deepread 1792478336435_qe1n4 mc212), trace 212 mc: agent 用 editor 多次部分写入→文件结构错乱→改用 Python 沙箱直接生成全新文件; Empyrean Qualib TCL 非便携到 .75; A 不可行原因=Empyrean Qualib TCL 非便携 .75 -> 提取「corner 参数化 std-cell library char template 生成 + 真跑 + 解析报告」子技能, 介质从 Qualib TCL 改为 HSPICE .sp deck(level-1 Shichman-Hodges), B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, check 真跑 HSPICE); trace 用户=produce-action(「检查STD 的tcl...我要一个模板」= 生成参数化模板), case 收敛为 produce-tool(写 std_char_tmpl_gen.py 生成 HSPICE deck + 真跑 + 报告) 给 check() 牙(§4.1 hidden-B cross-input guard B cell 名/端口/metrics 非 A + corner 参数 + report 行数, B 值与 A 反 + §4.9 反硬编); 重构为产 std_char_tmpl_gen.py+char_template.sp+library_char_report; check.py 15 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(Qualib TCL 非便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-OtaMa0SpecCheck-001":
        "两级 OTA .ma0 HSPICE 测量数据解析 + 指标合规判定器->produce-tool (sub-skill 提取 upload-action->produce-tool parser+checker reframe, §4 有牙必要, r741 spotcheck batch19): 用户 zhukaic@hfeg0plg58 原话「/workspace-upload 上传 ota_2stg_sim.ma0_data.md」(upload-action 上传文件, deepread 8exxf_ota_ma0_speccheck mc36/21 user turns), trace agent 寻找 upload 脚本, 首次 AK 权限失败(code=84107017), 第二次成功(doc_id=550004378822537267); 真实 .ma0 数据: PrimeSim HSPICE V-2023.12-SP1-1, temp=85°C/vcc!=1.025V, gain=55.78dB/PM=80.72°/GBW=973kHz/f_3db=1.82kHz; A 不可行原因=upload 本身不可评测(无 check 牙) -> case 抽取上传数据的「.ma0 解析+合规判定」子技能, B 档 synthesized 合规, reframe 由 sub-skill extraction 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (真实 .ma0 数据作可见 A, 待 @A apply 档2); trace 用户=upload-action(「/workspace-upload 上传...」= 上传文件非分析), case 收敛为 produce-tool(写 ma0_parser.py+checker) 给 check() 牙(§4.1 hidden-B cross-input guard B .ma0 3-corner post-layout -40/27/125°C + alter#3 故意 FAIL gain<45 & GBW<400k + 逐值校验, B 值与 A 反 + §4.9 反硬编 + malformed .ma0 拒绝); 重构为产 ma0_parser.py+compliance_report.md; check.py 12 断言验 hidden-B cross-input guard+防硬编使纯 upload-action(不可评测)无法有牙 => 收敛为 produce-tool 子技能提取是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: level=L2 误标应改 L1(check 仅 subprocess 跑候选 python 解析 .ma0 文本, 不启动 HSPICE, 与 OTATunePlan/b19 误分类同型「subprocess 跑候选 parser」非「真跑 EDA 工具」), metadata bug 待 @A apply 档1 补 sweep (与 r783 AgingDirSeparateTransform layer=None 同型第三型)。",
    "EDA-Eval-DesignFlow-SizingSensDiag-001":
        "器件尺寸灵敏度/设计问题诊断器->produce-tool (Q&A/analysis->produce-tool 灵敏度诊断器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 curryxu@hfeg0plg99 原话「帮我看一下这个FIFO电路哪里有些问题，有哪些管子的尺寸可以调整的？仿真激励：…sp 仿真网表：…netlist」(analysis/Q&A 问诊断+建议, trace 79 mc), agent 仅读文件给文字建议(其 run_commands 被禁, 未真跑仿真); A 不可行原因=真实 FIFO 电路生产文件 SUT 沙盒不可达 -> case 抽取「器件尺寸灵敏度/设计问题诊断器」子技能, DUT level-1 Shichman-Hodges 单级 CMOS 反相器+负载, hspice 跑 baseline + per-device W ±20% 扰动 + 中心差分灵敏度排名, B 档 synthesized 合规, reframe 由 Q&A/analysis→produce-tool 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, 候选真跑 HSPICE 产 .lis, check 验 .lis 'job concluded'); trace 用户=Q&A/analysis(「帮我看一下...哪里有些问题，有哪些管子的尺寸可以调整」= 问诊断+建议), case 收敛为 produce-tool(写 sizing_sens_diag.py 诊断器真跑 HSPICE 产灵敏度排名) 给 check() 牙(§4.1 hidden-B cross-input guard B top_candidate + sensitivity 排名 + ranking.csv rows + A 交叉重跑 top 一致, B 值与 A 反 + §4.9 反硬编); 重构为产 sizing_sens_diag.py+HSPICE 真跑; check.py 14 断言验 hidden-B cross-input guard+防硬编使纯 Q&A/analysis(无 runnable artifact)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-TxRonSize-001":
        "DDR5 TX PODL 输出驱动器 Ron 表征 + sizing-to-target 器->produce-tool (portability produce-action->produce-tool Ron 表征+sizing 器 reframe, §4 有牙必要, r741 spotcheck batch19): 用户 alenxu@hfeg0pkn003 原话 U115「如果需要使上拉下拉导通电阻为 120 欧，n管与p管尺寸为多少」(produce-action sizing to target Ron, trace 186 mc), 用 HSPICE 对 PMOS 上拉(ptn_lv)/NMOS 下拉(ntn_lv)做线性区 DC 扫描(VDS→10mV, Ron=VDS/|Id|), 按 Ron∝1/W_total 缩放 W/M finger multiplier 命中目标 Ron=120Ω; trace 用 foundry BSIM(ptn_lv/ntn_lv l=39n, 不可移植); A 不可行原因=foundry BSIM 不可便携 .75 -> 提取「线性区 Ron DC 表征 + 按 Ron∝1/(W·M) sizing-to-target」子技能, 便携化为 level-1 Shichman-Hodges + HSPICE .dc/.measure harness, B 档 synthesized 合规, reframe 由 portability 驱动非配额驱动; asset_fidelity=synth_deck ✓(已标); layer=L2 ✓(已标, check 真跑 HSPICE); trace 用户=produce-action(「使上拉下拉导通电阻为 120 欧，n管与p管尺寸为多少」= sizing to target), case 收敛为 produce-tool(写 tx_ron_size.py Ron 表征+sizing 命中器真跑 HSPICE) 给 check() 牙(§4.1 hidden-B cross-input guard B params.json + report.method==hspice + Ron 提取 + sizing 命中 120Ω + W/M 缩放, B 值与 A 反 + §4.9 反硬编); 重构为产 tx_ron_size.py+HSPICE 真跑; check.py 16 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(foundry BSIM 不可便携)无法有牙 => 收敛为 produce-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。",
    "EDA-Eval-DesignFlow-LvDpathCdlImport-001":
        "LV_DPATH CDL shell + 静态拓扑校验器->produce-tool (sub-skill 提取 + tool-limit produce-action Aether import->produce-tool CDL+topology checker reframe, §4 有牙必要, r741 spotcheck batch19): 用户 jiashengz@hfeg0plg92 原话「根据网表生成电路 Aether」+ 完整 LV_DPATH SPICE 网表(负沿 D 触发器 DOUT=D&RN, 行为级单元 INV/NOR2/CLKINV/NCHIZ/FBS + 测试激励)(produce-action 生成 Aether 原理图, trace 136 mc), assistant 检索 Aether 手册(2.6.4 File→Import CDL/Verilog Netlist) + pyAether API(aeGenerateSchematicFromVerilog) → 确认行为级源/开关无法转原理图器件 → 生成 LV_DPATH.cdl(pin-only shell) + LV_DPATH.v(结构化 Verilog) + import_lv_dpath.py + check_cdl.py(静态拓扑校验 6 subckt/9 inst/11 net 全 PASS); A 不可行原因=Aether import 对行为级单元不可行(tool-limit) -> case 收敛为 produce-tool(写 CDL+check_cdl.py 静态拓扑校验器), B 档 synthesized 合规, reframe 由 sub-skill extraction + tool-limit 驱动非配额驱动; asset_fidelity 缺标应 real-from-trace (真实 LV_DPATH 网表逐字保留, 待 @A apply 档2); trace 用户=produce-action(「根据网表生成电路 Aether」= 生成 Aether 原理图), case 收敛为 produce-tool 给 check() 牙(§4.1 hidden-B cross-input guard B CDL 结构不同 DFF + check_cdl.py 真跑 PASS + 判别力 FAIL, B 值与 A 反 + §4.9 反硬编); 重构为产 LV_DPATH.cdl+check_cdl.py; check.py 9 断言验 hidden-B cross-input guard+防硬编使纯 produce-action(Aether import 不可行)无法有牙 => 收敛为 produce-tool 子技能提取是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留(k=9 最低但 ≥8 过闸)。注: level=L2 误标应改 L1(check 仅 subprocess 跑 check_cdl.py 静态拓扑校验, 不启动任何 EDA 工具), metadata bug 待 @A apply 档1 补 sweep (与 r783 AgingDirSeparateTransform layer=None 同型第三型)。",
}

DRIVER = {
    "EDA-Eval-DesignFlow-VihTripTune-001": "portability produce-action->produce-tool 调优器",
    "EDA-Eval-DesignFlow-TrngTranNoise-001": "Q&A/how-to->produce-tool deck 注入器",
    "EDA-Eval-DesignFlow-PVTvarSpecJudge-001": "portability produce-action->produce-tool 判定器",
    "EDA-Eval-DesignFlow-StdLibCharTmpl-001": "portability produce-action->produce-tool deck 生成器",
    "EDA-Eval-DesignFlow-OtaMa0SpecCheck-001": "sub-skill 提取 upload-action->produce-tool parser+checker",
    "EDA-Eval-DesignFlow-SizingSensDiag-001": "Q&A/analysis->produce-tool 灵敏度诊断器",
    "EDA-Eval-DesignFlow-TxRonSize-001": "portability produce-action->produce-tool Ron 表征+sizing 器",
    "EDA-Eval-DesignFlow-LvDpathCdlImport-001": "sub-skill 提取 + tool-limit produce-action Aether import->produce-tool CDL+topology checker",
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
    print(f"=== r785 batch19 reframe_note apply: {len(REFRAME_NOTES)} cases (target) ===")
    counts = {"OK": 0, "ALREADY": 0, "MISSING": 0}
    for cid, note in REFRAME_NOTES.items():
        status, info = apply_one(cid, note)
        counts[status] = counts.get(status, 0) + 1
        print(f"  [{status}] {info} (driver={DRIVER.get(cid,'?')})")
    print(f"\nSummary: OK={counts['OK']} ALREADY={counts['ALREADY']} MISSING={counts['MISSING']}")
    print(f"Expected reframe_note count after apply: 117 + {counts['OK']} = {117 + counts['OK']}")


if __name__ == "__main__":
    main()
