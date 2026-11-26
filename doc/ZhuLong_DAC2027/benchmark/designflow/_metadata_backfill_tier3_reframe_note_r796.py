#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r796 (2026-11-18) metadata-debt backfill 档3 (reframe_note) apply.
Source: designflow/intent_audit_B_r752_spotcheck31.tsv (batch30, 6/12 keep_reframe cases 待 apply;
        6 keep_faithful = MultiPvtSpGenBuild + MosDcGuiTool + Mt0AggMinMax + Mt0FolderAggStat +
        SvUsedModelExtract + QueueCorePolicyPatch 无 reframe_note OK).
Spec: r771 bounded queue 档1->档3->档2. r772 档1 done. r773-r795 档3 batch9-29 done (reframe_note 32->216).
本轮 r796 档3 batch30 (r752 spotcheck31, 6 cases 待 apply). reframe_note 216->222.

reframe_note text = spotcheck31 per_case_reasoning + cases/B trace_source(user@host/session/mc) + test_rationale k_check (header).
apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False.

Driver 分类 (per per_case_reasoning, spotcheck31 12 case: 6 keep_reframe + 6 keep_faithful):
  - Q&A-driver (how-to/explain/debug/analysis/diagnosis Q&A -> produce-tool 给 check 牙): 6 cases (100% Q&A-driver, 0 portability/0 harness/0 sub-skill)
    DspfPerfMultiProcDiag (e0044979, Q&A-diagnosis -> produce-diagnoser-tool) /
    SharedLibDeployFix (e0024852, Q&A debug-how-to -> produce-fix-tool, check ⑧ 真跑 gxrc_t FineSim binary borderline L1->L2) /
    FinesimOptionExtend (yanxvwei, Q&A how-to/explain -> produce-extender-tool) /
    SimResultDirRestruct (xuelianf, Q&A why/diag -> produce-fix) /
    PostSimUncommentFix (reedchen, Q&A debug -> produce-fix) /
    LibCoordMapper (e0046686, Q&A analysis/relation-mapping -> produce-mapper-tool)

spotcheck31 关键发现 (本轮 reframe_note scope 限定不修 layer/level/asset_fidelity, 仅在 note 文本标注 layer bug 待 @A 档1 补 sweep):
  - layer 缺标(None)应补 L1 2/6: DspfPerfMultiProcDiag / LibCoordMapper (check 仅 subprocess 跑候选 python 解析文本+验 JSON, 无 EDA 二进制)
  - layer 误分类候选 1/6: SharedLibDeployFix (metadata 标 L1, check ⑧ subprocess.run 真跑 gxrc_t FineSim binary deploy smoke test,
    按 r747 rule check 阶段真跑 EDA 二进制 -> L2, 但主交付是 env-deploy 脚本非 simulation, borderline 建议复核)
  - layer=L1 ✓ 已正确 3/6: FinesimOptionExtend / SimResultDirRestruct / PostSimUncommentFix
  - 本批 1 例 pre-existing header != circled-mark count: FinesimOptionExtend (header=12 vs circled=14)
  - **B 域累计 layer 漏网 58->61 例**(r795 累计 58 + 本批 3: 47 缺标 + 11 误分类 + 本批新增 2 缺标 + 1 误分类候选;
    注: 本批 layer 缺标型主导 2/6 应补 L1, 对照 r795 1/5 应补 L2 新形态)
  - asset_fidelity 缺标 6/6 (全批无 asset_fidelity 标注, 待 @A apply 档2)
  - k_check metadata 缺标 3/6 (DspfPerfMultiProcDiag=22/LibCoordMapper=22 应标; FinesimOptionExtend header 12/circled 14; 
    SimResultDirRestruct=12/PostSimUncommentFix=10/SharedLibDeployFix=10 metadata 无 k_check 字段, 待 @A apply 档1 补 sweep)
  - 0 例 layer=L2 已正确 (对照 r795 1/5 IfElsePairFix check 真跑 hspice)
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    "EDA-Eval-DesignFlow-DspfPerfMultiProcDiag-001":
        "DSPF-tool two-stage flow 多进程诊断+stage2 慢因分析器->produce-tool (Q&A-diagnosis->produce-diagnoser-tool reframe, §4 有牙必要, r752 spotcheck batch30): 用户 e0044979@hfeg0plg76 (sess 1793941518837_i4kkz mc20), U0 verbatim 验证 .sh 设 TOOL_DIR 后哪个版本 dspf-tool 被调用(version-pinning Q&A)+U1(主意图)「给 tailor_fold+powerrep 开多进程 + 诊断 stage2 为何 2:08:39」(Q&A-diagnosis); trace 金标准 47 msgs CXMT Redwood lacaa TV1_FS SRAM characterization FineSim dspf-tool two-stage flow, powerrep 有真杠杆(DSPF_POWER_POOL_MAX_MB=9214), tailor_fold 无 env 杠杆(coupling.db verify 单线程), stage2 多相位串行, agent 读 log/源码给文本诊断; A 不可行原因=纯 Q&A-diagnosis(「诊断为何慢」=给文本分析答案)无 runnable artifact 无 check 牙 -> case 抽取「perf 诊断器(perf_diagnoser.py 真跑分析 perf_summary.json 产 JSON 报告)」子技能, A 档 verbatim 合规(e0044979 原话两问逐字+perf_summary.json 附件), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 perf_summary.json 结构合成, 待 @A apply 档2); trace 用户=Q&A-diagnosis(诊断给答案), case 收敛为 produce-tool(写 perf_diagnoser.py 真跑分析产 JSON 报告 7 顶层键) 给 check() 牙(§4.1 hidden-B cross-input tool_family==hspice 非 A 的 dspf + stages 名 cross-input guard + §4.5 确定性 sha256, check 仅 subprocess 跑候选 python 分析 perf_summary.json 文本+验 JSON 结构, 无 EDA 二进制调用); 重构为产 perf 诊断器; check.py 22 断言验候选 perf_diagnoser.py+JSON 报告 => 收敛为 produce-diagnoser-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: **layer 缺标(None)应补 L1**(check 仅 subprocess 跑候选 python 分析文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 22(test_rationale header=22), asset_fidelity 缺标应 real-from-trace, track 缺标应 faithful, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SharedLibDeployFix-001":
        "FineSim gxrc_t 共享库部署修复器->produce-tool (Q&A debug-how-to->produce-fix-tool reframe, §4 有牙必要, r752 spotcheck batch30): 用户 e0024852@hfeg0pkn004 (sess 1793944907619_ddo96 mc218), U0 verbatim「i run gxrc_t ... got error libdizo.so cannot open ... how to fix it」(debug-Q&A how-to-fix); trace 金标准 218 msgs FineSim gxrc_t 共享库部署修复, P010 安装 tarball 截断 7 个非系统库缺失(186/1349), 从 P004 参考安装补齐缺失非系统 .so, 排除 glibc 系统库避段错误, 保留 libstdc++.so.6, 生成 setup_env.sh 导出 LD_LIBRARY_PATH, agent 修 deploy; A 不可行原因=纯 debug-Q&A(「how to fix it」=给修复方法)无 runnable artifact 无 check 牙 -> case 抽取「缺失共享库修复器(fix_missing_libs.sh+setup_env.sh 真跑产部署)」子技能, A 档 verbatim 合规(e0024852 原话逐字含报错原文+路径+how to fix it), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 P010/P004 lib 结构合成, 待 @A apply 档2); trace 用户=debug-Q&A(给修复方法), case 收敛为 produce-tool(写 fix_missing_libs.sh+setup_env.sh) 给 check() 牙(§4.1 hidden-B cross-input B P010/P004 非 A + §4.4 libdizo.so 补齐+无 glibc 系统库 + §4.5 ⑧ source setup_env.sh 后跑 gxrc_t 退出码 0, **check ⑧ subprocess.run([\"bash\",\"-c\",\"source setup && bash {gxrc}\"]) 真跑 gxrc_t FineSim 二进制作 deploy smoke test**, 击破 不补齐/假 setup stub, 是 §4.2 真跑候选); 重构为产 共享库部署修复器; check.py 10 断言验候选 fix_missing_libs.sh+setup_env.sh => 收敛为 produce-fix-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: **layer 误分类候选**(metadata 标 L1, check ⑧ 真跑 gxrc_t FineSim binary deploy smoke test, 按 r747 rule check 阶段真跑 EDA 二进制 -> L2, 但主交付是 env-deploy 脚本非 simulation, borderline 建议复核), level 已标 L1, k_check 缺标应 10(test_rationale header=10), asset_fidelity 缺标应 real-from-trace, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-FinesimOptionExtend-001":
        "FineSim option 解析+扩展器->produce-tool (Q&A how-to/explain->produce-extender-tool reframe, §4 有牙必要, r752 spotcheck batch30): 用户 yanxvwei@hfeg0pkn002 (sess 1793946809755_zao50 mc8), U0 verbatim「finesim_option.sp 这里有很多finesim 的option，解析每个option的含义，扩展这个文件（保留备份）：给出这些option的含义，及其他可以设置的值...列出更多DRAM的finesim 仿真的option」(Q&A-how-to + produce-extend 混合); trace 金标准 8 msgs agent 读原文件+扫描 SRAM/proj 下 .sp/.cir 收集 finesim_* option, editor 写扩展版(每条 .option 后 * 注释块+追加 DRAM 专用 option 集), 备份 .bak; A 不可行原因=Q&A-how-to+produce-extend(「解析含义」=讲解, 「扩展这个文件」=产扩展版)首轮讲解无 runnable artifact 无 check 牙 -> case 抽取「finesim option 扩展器(extend_finesim_option.py 真跑产 extended+backup)」子技能, A 档 verbatim 合规(yanxvwei 原话逐字含「解析每个option的含义，扩展这个文件（保留备份）」+列出更多 DRAM option), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 finesim_option.sp 结构合成, 待 @A apply 档2); trace 用户=Q&A-how-to(讲解)+produce-extend(扩展), case 收敛为 produce-tool(写 extender 真跑产 extended+backup) 给 check() 牙(§4.1 hidden-B cross-input B1/B2/B3 option 名集不同 + §4.4 backup 逐字节一致+extended 保留原始 .option+≥10 新 .option+≥6 DRAM 必备 option + §4.5 3 B 变体结论一致, check 仅 subprocess 跑候选 python 编辑 .sp 文本+验内容, 无 EDA 二进制); 重构为产 finesim option 扩展器; check.py 12 断言验候选 extend_finesim_option.py => 收敛为 produce-extender-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 编辑 .sp 文本+验内容, 无 EDA 二进制), level 已标 L1, k_check 缺标应 12(test_rationale header=12, **pre-existing header=12 vs circled=14 计数不符** 待 @A 修), asset_fidelity 缺标应 real-from-trace, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-SimResultDirRestruct-001":
        "仿真输出目录结构重构器->produce-tool (Q&A why/diag->produce-fix reframe, §4 有牙必要, r752 spotcheck batch30): 用户 xuelianf@hfeg0pkn002 (sess 1794187811534_0218t mc13), U0 verbatim「运行后输出的文件夹为什么不一致...请按照文件2生成输出文件夹的方式修改文件1的程序（不修改group范围）」(Q&A-why + produce-fix 混合); trace 金标准 13 msgs run_group123.py 输出目录生成方式改成像 run.py(os.chdir+相对路径+嵌套 result_D0_<bin>/ 子目录), 不改 group 范围, patch 脚本重构+备份, 保留 group1+group2, 新增运行前 rmtree 清理+bsub -n 16 -R span[hosts=1], agent 改脚本; A 不可行原因=Q&A-why+produce-fix(「为什么不一致」=诊断, 「请...修改」=修)首轮诊断无 runnable artifact 无 check 牙 -> case 抽取「输出目录重构器(run_group123.py patch 真跑产改后脚本)」子技能, A 档 verbatim 合规(xuelianf 原话逐字含「为什么不一致」+「请按照文件2...修改文件1（不修改group范围）」约束), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 run.py/run_group123.py 结构合成, 待 @A apply 档2); trace 用户=Q&A-why(诊断)+produce-fix(修), case 收敛为 produce-tool(写 run_group123.py patch) 给 check() 牙(§4.1 hidden-B cross-input B 非 A + §4.3 os.chdir+GROUPS 不变+shutil.rmtree+bsub -n span+相对路径嵌套 result_D0_<bin>/ + §4.4 C post 全新块名泛化, check 仅 subprocess 跑候选 python 验脚本结构, bsub 为脚本内文本非真跑, 无 EDA 二进制); 重构为产 输出目录重构器; check.py 12 断言验候选 run_group123.py => 收敛为 produce-fix 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 验脚本结构, bsub 为脚本内文本非真跑, 无 EDA 二进制), level 已标 L1, k_check 缺标应 12(test_rationale header=12), asset_fidelity 缺标应 real-from-trace, metadata bug 待 @A apply 档1/档2 补 sweep。",
    "EDA-Eval-DesignFlow-PostSimUncommentFix-001":
        "后仿网表注释取消 bug 修复器->produce-tool (Q&A debug->produce-fix reframe, §4 有牙必要, r752 spotcheck batch30): 用户 reedchen@hfeg0pkn002 (sess 1794187865687_6dvs5 mc47), U0 verbatim「后仿的网表没有正确取消注释出来，请你帮我定位和修复bug」(debug-Q&A + fix); trace 金标准 47 msgs gen_sp_write.py 的 _netlist_cat() 用写死旧块名 DOutFIFOx1_Dmi_PN1p76_DbusMg 分类后仿 .inc spf/XI_ 行, 模板块名改 latsqmuxPF_DPmux_Dbus_length46_rev0 后两类行 --sim post 下保持注释, 金标准=改成按模式匹配(.inc 路径含 .spf 或 subckt -> post; 含 netlist -> pre; XI_ 开头 -> inst), 不依赖写死块名, agent 修 bug; A 不可行原因=debug-Q&A+fix(「帮我定位和修复bug」=给诊断+修复)无独立 runnable artifact 无 check 牙 -> case 抽取「后仿注释修复器(修复后 gen_sp_write.py 真跑产 .sp)」子技能, A 档 verbatim 合规(reedchen 原话逐字含「帮我定位和修复bug」+命令+路径), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 gen_sp_write.py 模板结构合成, 待 @A apply 档2); trace 用户=debug-Q&A+fix(给诊断+修复), case 收敛为 produce-tool(写修复后 gen_sp_write.py) 给 check() 牙(§4.1 hidden-B cross-input B post 非 A + §4.4 post .inc spf/subckt/XI_ 取消注释+pre .inc netlist 保持注释 + §4.5 C post 全新块名 rdqMuxPF 泛化(硬编码 A 块名修复必失败), check 仅 subprocess 跑候选 python gen_sp_write.py 产 .sp 文本+验注释状态, 无 EDA 二进制); 重构为产 后仿注释修复器; check.py 10 断言验候选 gen_sp_write.py => 收敛为 produce-fix 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: layer=L1 ✓ 已正确(check 仅 subprocess 跑候选 python 产 .sp 文本+验注释状态, 无 EDA 二进制), level 已标 L1, k_check 缺标应 10(test_rationale header=10), asset_fidelity 缺标应 real-from-trace, metadata bug 待 @A apply 档1/档2 补 sweep。同 user 同 host 同 tool gen_sp_write.py(本 case 修 bug vs MultiPvtSpGenBuild 构建), same-tool verb-heterogeneous user-cluster。",
    "EDA-Eval-DesignFlow-LibCoordMapper-001":
        "lib_timing_tools (i,c,q) 三维坐标-timing table 关系梳理映射器->produce-tool (Q&A-analysis/relation-mapping->produce-mapper-tool reframe, §4 有牙必要, r752 spotcheck batch30): 用户 e0046686@hfeg0pkn001 (sess 1794187969151_dhy10 mc8), U0 verbatim「lib_timing_tools抽timing需要按照（i_slew，c_slew，q_load）的三维坐标形式传递，再去匹配template table，然后抽值...需要先做下i，c，q与table的关系梳理」(Q&A-analysis 关系梳理); trace 金标准 8 msgs 反标 rev_cali 后端, 扫 4 参考库, CONSTRAINT 表用 (i,c) 2D 且 template_lib(v1=c,v2=i) 与 k_lib(v1=i,v2=c) 变量顺序相反, CELL_DELAY/TRAN 用 q_load 1D, CLK_TRAN 用 c_slew 1D, agent 梳理关系给文本分析; A 不可行原因=纯 Q&A-analysis(「先梳理这个关系」=给关系分析答案)无 runnable artifact 无 check 牙 -> case 抽取「lib 坐标映射器(lib_coord_mapper.py 真跑解析 .lib 产 coord_mapping.json 6 顶层键)」子技能, A 档 verbatim 合规(e0046686 原话逐字含「(i_slew，c_slew，q_load)的三维坐标」+索引传递优先/值传递精确匹配+参考 lib 路径), reframe 由 Q&A-driver 非配额驱动; asset_fidelity 缺标应 real-from-trace(用真实 liberty 片段结构合成, 待 @A apply 档2); trace 用户=Q&A-analysis(关系梳理给答案), case 收敛为 produce-tool(写 lib_coord_mapper.py 真跑解析 .lib 产 coord_mapping.json) 给 check() 牙(§4.1 hidden-B cross-input B var_order [i_slew,c_slew] 非 A 的 [c_slew,i_slew] guard + §4.4 templates/arcs/grids/summary/style_detected, check 仅 subprocess 跑候选 python 解析 .lib 文本+验 JSON 输出, 无 EDA 二进制); 重构为产 lib 坐标映射器; check.py 22 断言验候选 lib_coord_mapper.py+coord_mapping.json => 收敛为 produce-mapper-tool 是让 check() 能区分真假交付的唯一途径, §4 结构性必要, 保留。注: **layer 缺标(None)应补 L1**(check 仅 subprocess 跑候选 python 解析 .lib 文本+验 JSON, 无 EDA 二进制), level 缺标应 L1, k_check 缺标应 22(test_rationale header=22), asset_fidelity 缺标应 real-from-trace, track 缺标应 faithful, metadata bug 待 @A apply 档1/档2 补 sweep。",
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
