#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r831 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch6.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        r830 batch5 +12 (283->295, miss 112->100).
        本轮 batch6 = alphabetical 续 12 missing after McLisSnmExtractor (r830 batch5 末位).
        reframe_note 295->307, miss 100->88.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r831 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch6 12 case = 9 keep_reframe_for_teeth (portability) + 3 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe portability + 3 keep_faithful):
  - portability-driver (foundry PDK / real .md0/.mt0/.sp/.csv 不可沙盒复刻 → synth_deck / synth_data):
      9 case: McRonMismatch (real FineSim MC .md0 不可复刻→synth_deck, characterization 域) /
              McVthSpVariantGen (real d0_bl10_m0.sp+vth.mt0 不可复刻→synth_deck) /
              MinpulseRewriteRun (real minpulse spf .sp 激励不可复刻→synth_deck) /
              MonteMt0Stats (real HSPICE .mt0 不可复刻→synth_data) /
              Mt0AggMinMax (real FineSim .mt0 不可复刻→synth_data) /
              Mt0FolderAggStat (real FineSim .mt0 不可复刻→synth_data) /
              Mt0GroupedStatsGen (real HSpice .mt0 不可复刻→synth_data) /
              Mt0MeasureStat (real FineSimPro/HSPICE .mt0 不可复刻→synth_data) /
              Mt0Reorg (real 5-foundry-platform thin-oxide inv deck+PDK 不可复刻→synth_deck, characterization 域)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      3 case: MonteCarloDeckGen (A-faithful, PVT deck 模板便携, generator 产 mc deck 同形) /
              MosDcGuiTool (A-faithful, HSPICE bench 模板便携, GUI tool 同形) /
              Mt0ParseFix (A-faithful, debug-Q&A-understand+fix parse_results.py 同形, .mt0 样例便携)

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 缺标或标 L2 待复核(check 仅 subprocess 跑候选 python 解析文本, 0 EDA 二进制, 应 L1)
  - level/k_check/shard 字段缺标
  - 与 r773-r800/r826-r830 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-McRonMismatch-001":
        "FineSim MC .md0 RON_PU/PD_mismatch (6σ/std×100% ÷ divisor) 提取 + 末尾 4 行系统汇总陷阱排除->produce (portability-driver reframe, real FineSim MC .md0 不可沙盒复刻->synth_deck, §4 有牙必要, r831 reframe_note backfill batch6): 用户 clarawu@hfeg0pkn001 (sess 1793178408819_r4p2e, mc=56, characterization 域) 从 Ron_linMC#4.md0 算 RON_PU_mismatch(=6×std(rpu_50)/230×100%)与 RON_PD_mismatch; trace agent 写 compute_ron_mismatch.py 首版把末尾 4 行系统汇总(avg/std/min/max)当数据行误算 504 样本 std=10.3 mismatch=26.84%; 用户给根因「最后四行是系统汇总」+方法「用系统 std 行」, 修后 500 样本 std=1.238 mismatch=3.23%; A 不可行原因=real FineSim MC .md0 不可沙盒复刻 -> 收敛为 mc_ron_mismatch.py(读 hidden B synth .md0, asset_fidelity=synth_deck); reframe 由 portability-driver(real .md0 不可复刻); 意图核心(.md0 列式 parse + 整数 mc_index 行过滤排除汇总行 + 系统汇总 std 行直接读 + 6σ/std×100% ÷ divisor 公式)完整保留; check.py 14 断言验 zip 含 mc_ron_mismatch.py + py_compile + hidden B subprocess 真跑 exit0 产 report.json+mismatch_report.csv + FineSim 真跑(B log 含 FineSim + Successfully Completed) + mc_index 整数过滤(500 样本排除 4 汇总行) + divisor 从 spec.json 读(非样本均值) + 系统汇总 std 行识别(非样本 std 复算) + RON_PU_mismatch 数值正确(6×std/divisor×100%) + RON_PD_mismatch 数值正确 + cross-input guard(A≠B divisor 不同) + report.json 含 RON_PU/PD 两键 + 无 traceback + 退化 stub(只 print 期望)FAIL + B/A mismatch 不等(防硬编) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 FineSim 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 验 FineSim 真跑则正确, 但若仅文本解析应 L1), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-McVthSpVariantGen-001":
        "DRGQA BL10 sense-amp HSPICE 100-MC vth 失配 deck 变体生成器->produce (portability-driver reframe, real d0_bl10_m0.sp+vth.mt0 不可沙盒复刻->synth_deck, §4 有牙必要, r831 reframe_note backfill batch6): 用户 leliow@hfeg0plg52 (sess 1794277350221_vawjj, mc=340) 根据 d0_bl10_m0.sp(base)与 vth.mt0(100 组 Monte-Carlo vth 失配)生成 d0_bl10_m2.sp: 读 vth.mt0 序号 2 行的 4 个 vth 值, 依次替换 base.sp 中 4 条 .param delvtoBL0_{NsL,NsR,PsL,PsR} 的被减数, 减数(nominal)与 *2 因子不变; trace agent 写变体生成器; A 不可行原因=real d0_bl10_m0.sp+vth.mt0 不可沙盒复刻 -> 收敛为 mc_vth_sp_variant_gen.py(读 hidden B synth base.sp+vth.mt0, asset_fidelity=synth_deck); reframe 由 portability-driver(real deck+vth.mt0 不可复刻); 意图核心(.param 4 行被减数替换+减数保留+*2 因子保留+按 mc 序号行定位)完整保留; check.py 17 断言验 zip 含 mc_vth_sp_variant_gen.py + py_compile + 候选在 hidden B1(mc_index=7)exit0 + B1 产非空 out.sp + B1 产可解析 out_report.json + out.sp 含全部 4 条 .param delvtoBL0_{NsL,NsR,PsL,PsR} + 4 行被减数替换为 B1 mt0 序号 7 行的 4 vth 值 + 4 行减数保留(原 nominal 不变) + *2 因子保留 + 其余 .param/base 内容不变 + B1 输出 .tran/.measure/.inc 保留 + cross-input guard(A≠B mc_index 不同产出不同被减数) + 退化 stub FAIL + mt0 序号 0..99 越界 exit≠0 + B1 mc 序号行 vth 值解析正确(4 列) + 确定性 3 次逐字节一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 17, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-MinpulseRewriteRun-001":
        "minpulse_spf .sp 路径批量替换 + bsub run 激励树->produce (portability-driver reframe, real minpulse spf .sp 激励不可沙盒复刻->synth_deck, §4 有牙必要, r831 reframe_note backfill batch6): 用户 berylwu@hfeg0pkn002 (sess 1793937421846_ip3nr, mc=231, spice_sim 域, mtime 2026-11-06 NEW, 本轮 11-06 11:5x 经 .75 run_commands 对 42 spice-active hosts 定向重扫 threshold 2026-11-06 06:00 发现 111 NEW sessions 后筛出, 证 pool 未枯竭) U#0 verbatim A 档「/proj/.../rc_delay 这个路径下, Dlyrc 开头的几个文件夹下的 minpulse_spf 目录下的 sp 文件, 替换里面的 Old string: /proj/ddgoa/V0/model/current/ → New string: /proj/ddgoa/V0/model/current_L5_v0d9_Rev02_t05/ 并直接 run 所有替换后的激励」; trace agent 写 replace_and_run.py 递归 find Dlyrc*/minpulse_spf/*.sp 批量 sed 替换 + bsub 提交; A 不可行原因=real minpulse spf .sp 激励树不可沙盒复刻 -> 收敛为 replace_and_run.py(读 hidden B synth 激励树, asset_fidelity=synth_deck); reframe 由 portability-driver(real .sp 激励不可复刻); 意图核心(递归 find 目录 glob+sed 路径替换+bsub run+report)完整保留; check.py 14 断言验 zip 含 replace_and_run.py + py_compile + hidden B subprocess exit0 产 replace_report.json+submit.sh+替换后 deck 树 + files_changed==18(3 目录×6 文件) + total_replacements 正确(每文件 ≥1 替换) + 替换后路径含 New string + Old string 残留 0 + submit.sh 含 bsub + 不替换非 minpulse_spf 路径的文件 + cross-input guard(A≠B New string 不同) + 退化 stub FAIL + report 含 files_changed/total_replacements 两键 + dry-run 模式 exit0 不实际 run + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 验 bsub 真提交则正确, 若仅文本生成 deck 树应 L1), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-MonteMt0Stats-001":
        "HSPICE Monte-Carlo .mt0 分块循环递进读取 + 7 参数 avg/std 正态统计 -> montesum.mt0 生成器->produce (portability-driver reframe, real HSPICE .mt0 不可沙盒复刻->synth_data, §4 有牙必要, r831 reframe_note backfill batch6): 用户 shanliny@hfeg0pkn001 (sess 1793943889492_yg26n, mc=95) 给 1_run(monte 仿真提交脚本, 分块循环 num1=(i-1)*50+1/num2=50*i, bsub hspice, 结果写 RESULT_DIR/prefix_N1_N2/prefix_N1_N2.mt0) 与 io_d0_template_1_50.mt0(结果样例, 列 index + 7 测量参数 t_outb_r/v_blb_fall1/v_bl_fall1/v_dv/v_df_sat_sac/v_df_bl_blb/v_df_b_s + temper + alter#), 要求构建 python 脚本像 1_run 循环递进地读取每个 .mt0, 统计 index 后 7 个参数的平均值与标准差(正态分布), 生成 montesum.mt0; trace agent 写 montesum.py; A 不可行原因=real HSPICE .mt0 不可沙盒复刻 -> 收敛为 montesum.py(读 hidden B synth .mt0 树, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻); 意图核心(.mt0 列式 parse + 分块循环递进读取 + 7 参数 avg/std + montesum.mt0 输出)完整保留; check.py 14 断言验 zip 含 montesum.py + py_compile + --help exit0(CLI 可解析) + hidden B 运行 exit0 产非空 montesum.mt0 + montesum.mt0 含全部 7 个测量参数名(t_outb_r..v_df_b_s) + index/temper/alter# 不作为统计对象(过滤正确) + avg 行数值与 B 独立复算一致 + std 行数值与 B 独立复算一致(正态分布 n-1) + montesum.mt0 格式含 avg/std 两行 + 分块循环递进(每块 50 行, 共 N 块) + cross-input guard(A≠B 参数值不同) + 退化 stub FAIL + 空目录优雅处理 exit0 + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 .mt0 文本+算统计, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Mt0AggMinMax-001":
        "FineSimPro .mt0(core1103 dir)汇总每参数 min/max + 按温度分组 + abs/mA 单位换算->produce (portability-driver reframe, real FineSimPro .mt0 不可沙盒复刻->synth_data, §4 有牙必要, r831 reframe_note backfill batch6): 用户 declanzh@hfeg0plg97 (sess 1793947529316_ie8du, mc=0 scout 候选) 在 /rundata/drcoa/V0/simdir/hspice/declanzh/a51_VfsblnPumpCore_SIM/spf_result/core1103 下跑完 HSPICE/FineSim 仿真, 几十个 .mt0 文件每个 alter/MC run 含 5 列(i_vfsbln/i_vwlp_fsbln/ieff./temper/alter#), 要求汇总到一个文档给每参数最大/最小值; 细化 U#24「电流按绝对值统计, 换算 mA 单位(×1000), 同时给原始值(A 带符号)和绝对值(mA)两套 min/max, 按温度分组统计」; trace agent 写 mt0_agg_minmax.py; A 不可行原因=real FineSimPro .mt0 不可沙盒复刻 -> 收敛为 mt0_agg_minmax.py(读 hidden B synth .mt0 树, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻); 意图核心(.mt0 列式 parse + 5 列聚合 + abs/mA 换算 + 原始/绝对两套 min/max + 按温度分组)完整保留; check.py 12 断言验 zip 含 mt0_agg_minmax.py + py_compile + 在 B1 上 exit0 + 输出文件存在且非空(>100B) + 输出含 3 个参数名(i_vfsbln/i_vwlp_fsbln/ieff) + 输出含 mA 单位标识 + 输出含 B1 正确文件数(15) + i_vfsbln abs mA min/max 在 B1 真值 + i_vwlp_fsbln abs mA min/max 在 B1 真值 + ieff min/max 在 B1 真值 + 按温度分组组数与 B1 temper 去重一致 + cross-input guard(A≠B) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 .mt0 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B, mc=0 scout 候选可作 trace_source 但 host-verify 待 @A 复核。",

    "EDA-Eval-DesignFlow-Mt0FolderAggStat-001":
        "core1103 .mt0 文件夹汇总(每参数 max/min + abs/mA + ieff×100% + 2 位小数 + 去温度栏)->produce (portability-driver reframe, real FineSim .mt0 不可沙盒复刻->synth_data, §4 有牙必要, r831 reframe_note backfill batch6): 用户 declanzh@hfeg0plg97 (sess 1793947529316_ie8du, mc=172) 让 cline 汇总 core1103 文件夹下所有 .mt0 文件数据到一个文档, 给每参数最大/最小值; 后续 4 轮细化: 按绝对值/mA 单位/ieff 是电流效率再×100 以百分比展示/对应文件只保留#数字/数据保留小数点后 2 位/去掉温度栏; 金标准 trace agent 最终脚本(msg#203)解析 77 个 .mt0(5 列), 输出三节(全局 |min|/|max| 绝对值 mA/ieff% + 按温度分组 + 全部明细), 文件列=#alter; A 不可行原因=real FineSim .mt0 不可沙盒复刻 -> 收敛为 mt0_summary.py(读 hidden B synth .mt0 树, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻); 意图核心(.mt0 列式 parse + abs/mA + ieff×100% + 2 位小数 + 去温度栏 + 文件列=#alter + 三节输出)完整保留; check.py 17 断言验 zip 存在可解 + 含 mt0_summary.py + 脚本在 hidden B1 exit0 产 core1103_mt0_summary.txt + 汇总文档含三节(全局统计/温度分组/数据明细) + 输出含 |min| i_vfsbln(mA,2 位小数)=B1 真值 + 输出含 |max| i_vfsbln(mA)=B1 真值 + 输出含 |min| i_vwlp_fsbln(mA)=B1 真值 + 输出含 |max| i_vwlp_fsbln(mA)=B1 真值 + 输出含 ieff% min/max=B1 真值 + 数据保留 2 位小数 + 温度栏已去掉 + 文件列=#alter(非文件名) + ieff 已 ×100 以百分比展示 + cross-input guard(A≠B) + 退化 stub FAIL + 确定性 3 次一致 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 .mt0 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 17, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Mt0GroupedStatsGen-001":
        "HSpice .mt0 测量文件按 pvref 分组统计生成器(绝对值 min/max + alter#/温度标注)->produce (portability-driver reframe, real HSpice .mt0 不可沙盒复刻->synth_data, §4 有牙必要, r831 reframe_note backfill batch6): 用户 declanzh@10.129.2.11 (sess 1794450135994_uer9e, mc=489) 在多个 HSpice 仿真目录下处理 .mt0 测量数据, 要求按 pvref 分组汇总各测量参数的绝对值 min/max, 标注极值出现的 alter# 和温度, 进行单位换算(A→mA/raw→%); 涉及 a51_VfsblnPumpCore/a8_Vfsrdb_and_FsLatch/a23_FsAryLvlVwlp2Vfsblwn/a7_ThinFsComp 等多个仿真目录; trace agent 写 mt0_grouped_stats.py(list_allowed_files 探目录→read_files 读 .mt0→editor 编多版本→run_approved_command 验证); A 不可行原因=real HSpice .mt0 不可沙盒复刻 -> 收敛为 mt0_grouped_stats.py(读 hidden B synth .mt0 树, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻); 意图核心(.mt0 列式 parse + pvref 分组 + 绝对值 min/max + alter#/温度标注 + A→mA/raw→% 换算)完整保留; check.py 10 断言验 zip 含 mt0_grouped_stats.py + subprocess 在 hidden B 上真跑无错 + 输出 JSON 有 groups 顶层键 + 组数=4(B pvref 去重:0.20/0.40/0.60/0.80) + 每组 row_count=8 + group 0.20 voffset_vout_d_mv abs_min/abs_max 正确 + group 0.80 voffset_vout_u_mv abs_min/abs_max 正确 + 极值 alter# 标注与 B 独立复算一致 + 极值温度标注与 B 独立复算一致 + cross-input guard(A≠B pvref 组数不同) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析 .mt0 文本+算统计, 0 EDA 二进制, 应 L1), level 缺标应 L1, k_check 字段缺标应 10, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Mt0MeasureStat-001":
        "Vfsrdb+FsLatch sense-amp MC .mt0 后处理(alter#/res_r1 分组 + min/max/mean/std/abs + ohm→Mohm)->produce (portability-driver reframe, real FineSimPro/HSPICE .mt0 不可沙盒复刻->synth_data, §4 有牙必要, r831 reframe_note backfill batch6): 用户 declanzh@hfeg0pkn002 (sess 1794449548577_09v9h, mc=196, analog:179;hspice:62;pyaether:5) 在 Vfsrdb+FsLatch sense-amp MC 仿真 .mt0 后处理 session, 给 /rundata/drvqa/.../a8_Vfsrdb_and_FsLatch_rerun.mt0 让 agent 解析测量数据, 按 (alter#, res_r1) 分组算 min/max/mean/std/abs, ohm→Mohm 换算, 输出 _grouped.txt/_summary.txt; trace agent 写 fuse_sense.py(parse_mt0 跳过 $/./列名行 + float try/except 跳过 error + compute_stats count/min/max/mean/std); A 不可行原因=real FineSimPro/HSPICE .mt0 不可沙盒复刻 -> 收敛为 mt0_measure_stat.py(读 hidden B synth .mt0, asset_fidelity=synth_data); reframe 由 portability-driver(real .mt0 不可复刻); 意图核心(.mt0 parse + (alter#,res_r1) 分组 + 5 统计量 + error 行跳过 + ohm→Mohm 换算 + 双输出文件)完整保留; check.py 14 断言验 zip 含 mt0_measure_stat.py + 脚本在 hidden B 跑通 exit0 + B 产可解析 _stats.json + B data_rows 与 oracle 一致 + B error_count 与 oracle 一致(error 行跳过) + B 分组数与 oracle 一致 + B 分组键(alter#,res_r1)集合与 oracle 一致 + B 各组 count 与 oracle 一致 + B sensetime_comp_ns min/max/mean/std 与 oracle 一致 + ohm→Mohm 换算正确(res_vfsrdb 单位) + 输出 _grouped.txt 含分组明细 + 输出 _summary.txt 含 5 统计量 + cross-input guard(A≠B res_r1 组数不同) + 退化 stub FAIL => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析 .mt0 文本+算统计, 0 EDA 二进制, 应 L1), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Mt0Reorg-001":
        "5-foundry 平台 thin-oxide inv SPICE 表征(.alter 链+alter_mapping+thin.mt0.csv 按平台/条件分组标注表)->produce (portability-driver reframe, real 5-foundry-platform thin-oxide inv deck+PDK 不可沙盒复刻->synth_deck, §4 有牙必要, r831 reframe_note backfill batch6): 用户 hairuizh@hfeg0plg52 (sess 1793953494729_nmz6w, mc=1129, characterization 域) 为 5 个 foundry 平台(G4B_DEJOA/G5_DRCOA/V1_DRGQA/V2B_DRVQA/GL22)的 thin-oxide 反相器做平台级器件表征 SPICE 仿真; U#2「在该文件夹内添加 DRVQA_invs.sp, 包含 ptn/ntn, ptn_lv/ntn_lv 两对 inv, 并对应修改 DEJOA/DRCOA/DRGQA_invs.sp 使其都包含 ptn/ntn, ptn_lv/ntn_lv 两对 inv; GL22_invs.sp 仍保持原有五对管子组成的 inv」+ U#3 纠正「GL22 数据在 0.15u 以上是空的, 需要统计所有 length; 各平台 Lmin 不同(G4B 42n/G5 42n/V1 36n/V2B 36n/GL22 26n), 从 Lmin to 200n step5n」; agent 写 mt0_reorg.py(base.sp .alter 链 + alter_mapping config + thin.mt0.csv 按平台/条件分组标注表); A 不可行原因=real 5-foundry thin-oxide inv deck + foundry PDK 不可沙盒复刻 -> 收敛为 mt0_reorg.py(读 hidden B synth deck+config, asset_fidelity=synth_deck); reframe 由 portability-driver(real foundry deck+PDK 不可复刻); 意图核心(.alter 链扫 5 平台 × 多 device pair × PVT + alter_mapping 顺序对应 + thin.mt0.csv 按平台/条件分组标注 + 各平台 Lmin 不同步长 5n)完整保留; check.py 13 断言验 zip 含 mt0_reorg.py + py_compile + B1 上脚本 exit0 且输出非空 + B1 输出含表头注释(Lmin 汇总行 + tpd 公式 + abs 注明 + lv_start 注明) + B1 含全部 9 个 #### metric #### 段 + B1 含每个(条件,平台)块共 3 行(Lmin/typ/tpd) + B1 各平台 Lmin 正确(G4B 42n/G5 42n/V1 36n/V2B 36n/GL22 26n) + B1 step=5n + B1 Lmin to 200n 全长度覆盖 + B1 GL22 五对管子(非两对 inv) + B1 DRVQA/DRGQA/DEJOA/DRCOA 两对 inv(ptn/ntn + ptn_lv/ntn_lv) + cross-input guard(A≠B 平台 Lmin 不同) + 退化 stub FAIL => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 csv+config 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    # ===== 3 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-MonteCarloDeckGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r831 reframe_note backfill batch6): 用户 gallopc@hfeg0pkn005 (sess 1793790756982_bjazn, mc=296) 在 hfeg0pkn005 上用 FineSim 跑 XDec driver 仿真, deck=sim_driver_x20_adj.sp, 现用 PVT corner(FF/TT/SS 通过 .if pcor_*==1 切换, sigmaflag=1.36, .tran 1p 2us)覆盖工艺/温度/电压偏差; U#0「把这个文件修改成一个蒙特卡罗仿真。蒙特卡罗给予的随机量是什么? 如果我想仿真把温度、工艺和电压都随机, 应该怎么改? 帮我把改之后的 deck 存到路径下」, 意图形态=produce-action(改 deck+保存), 可便携性=高(FineSim XDec driver deck 模板便携, AGAUSS+SWEEP MONTE+.Variation 块写法在 FineSim 用户手册公开, asset_fidelity=A-faithful); trace agent 查 finesim_ug 后用 AGAUSS+SWEEP MONTE + .Variation 块两套正确写法(首版 .dc gauss 被 FineSim 拒「incomplete or unsupported sweep statement」); case 交付 gen_monte_carlo.py + mc.sp 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「改 deck 成蒙特卡罗 + 随机 T/工艺/V」与 case 交付 generator+mc deck 同形映射, asset A-faithful 因 FineSim deck 模板便携); check.py 12 断言验 zip 含 gen_monte_carlo.py 且可编译 + 生成器在 B 上 exit0 产 _mc.sp+_mc_var.sp 两文件 + mcA 含 .tran...SWEEP MONTE=N + mcA 含≥3 个 AGAUSS()调用(工艺/温度/电压) + mcA 锁定 TT corner 基(pcor_tt=1, ff/ss=0) + mcA 保留 B 的 netlist .inc 路径 + mcA 保留 .probe 与 .measure + mcA 含 .Variation 块 + cross-input guard(A≠B .inc 路径不同) + 退化 stub FAIL + 确定性 3 次一致 + mcA 不用 HSPICE .dc var gauss 写法(FineSim 会报错) + mcA 含 .end => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer=L1, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 生成 deck 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-MosDcGuiTool-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r831 reframe_note backfill batch6): 用户 zanezang@hfeg0plg57 (sess 1793942454477_whc3n, mc=154, IC 前端工程师) 让 cline 写 Python 可视化脚本, 根据参数自动生成 HSPICE bench 一键仿真 NMOS/PMOS model 性能并出图; 后续逐轮细化: LX82 是电容值需保留/PMOS CV 范围应为 0~2×vcc(原代码横坐标只到 vcc 是 bug)/nmos-pmos 器件名可填(ntn/ntn_lv 等)/双 model 库对比(模型 1 实线/模型 2 虚线)/id-gm 单位改 m/u/CV 纵坐标名改 Cgg/GUI 高度贴合页面; 意图形态=produce-action(GUI tool), 可便携性=高(HSPICE bench 模板+NMOS/PMOS_TEMPLATE+parse_print_file 解析 .print 输出纯 Python 无 foundry PDK 依赖, asset_fidelity=A-faithful); trace agent 最终脚本 mos_dc_gui.py(/home/zanezang/Desktop, 1210 行)含 --cli/--selftest 模式 + NMOS_TEMPLATE/PMOS_TEMPLATE + parse_print_file; case 交付 mos_dc_gui.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「Python 可视化脚本生成 HSPICE bench 一键仿真出图」与 case 交付 GUI tool 同形映射, env-config/produce-tool 是 2026-11-15 令恢复的合法任务形态); check.py 13 断言验 zip 含唯一 .py 且无语法错 + gen-bench nmos(B1 config)exit0 写出 nmos.sp + nmos.sp 含 param_modfiy 块且 temp/vcc/vg_l/vg_h/step/w/l/nf 取自 B1 config + nmos.sp 含 .dc vd sweep vg + .print LX7(XMMN0)/1-LX8 等 + gen-bench pmos exit0 写 pmos.sp 含 .dc vd sweep vg + PMOS CV 范围 0~2×vcc(原 bug 修正) + parse_print_file 解析 .printsw 输出 + 双 model 库对比(模型 1 实线/模型 2 虚线) + id/gm 单位 m/u + CV 纵坐标名 Cgg + cross-input guard(A≠B config 不同) + 退化 stub FAIL + --selftest exit0 => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer 缺标应 L1(check 仅 subprocess 跑候选 python 生成 bench+解析, 0 EDA 二进制 run), k_check=13==k_rationale=13 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1, level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-Mt0ParseFix-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r831 reframe_note backfill batch6): 用户 yifansun@hfeg0pkn001 (sess 1794202410355_ps4q9, mc=3) 让 cline 修复 parse_results.py: FineSim .mt0 量测结果未抓出(原始脚本用 = 分隔符, 但 .mt0 是空格分隔列式表格); trace agent 诊断根因(.mt0 无 = 号, 是 header+data 列式格式), 新增 parse_mt0() 列式解析(跳过 $/. 行, zip header+data tokens), 在 4 个真实 .mt0 上验证, 修复版正确解析 t_delay/i_dyn_read_vcc 等 13 列; 意图形态=debug-Q&A-understand+fix(诊断+修复脚本), 可便携性=高(.mt0 样例 + parse_results.py 纯 Python 处理无 EDA 二进制依赖, asset_fidelity=A-faithful); case 交付修复版 parse_results.py + sim_result.txt 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, debug-Q&A-understand+fix 是 2026-11-15 令恢复的合法任务形态, trace 意图「修复 parse_results.py 让 .mt0 量测结果抓出来」与 case 交付 fixed script 同形映射, Q&A-understand 子意图 subsumed 进修复交付); check.py 14 断言验 zip 解出 parse_results.py + 修复脚本在 B 隐藏 .mt0 上 patch 路径后 exit0 + 产 sim_result.txt + 表头行格式正确(Variant/W/L/Type/PVT/Speed/t_delay/i_dyn_read/i_dyn_write/i_static) + B1(w125_l55_lvio_TT_0.8V_25C)t_delay 数值正确 + B1 i_dyn_read 数值正确 + B1 i_static 数值正确 + 全部 4 个 B .mt0 解析无 traceback + parse_mt0() 跳过 $/. 注释行 + header 列名识别(无 = 号) + cross-input guard(A≠B variant 路径不同) + 退化 stub(只 print 期望)FAIL + 13 列全提取(无丢列) + 空目录优雅 exit0 => §4 牙由 hidden-B cross-input + §4.2 subprocess 保证, layer 缺标应 L1(check 仅 subprocess 跑候选 python 解析 .mt0 文本, 0 EDA 二进制), k_check=14==k_rationale=14 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1, level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B, mc=3 偏低可作 trace_source 但 host-verify 待 @A 复核。",
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
