#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
r830 (2026-11-18) metadata-debt backfill 档3 (reframe_note) batch5.
Source: r825 bounded queue 提议 (reframe_note backfill 160 missing P1).
        r826 batch1 +12 (235->247, miss 160->148).
        r827 batch2 +12 (247->259, miss 148->136).
        r828 batch3 +12 (259->271, miss 136->124).
        r829 batch4 +12 (271->283, miss 124->112).
        本轮 batch5 = alphabetical 续 12 missing after GmidLut (r829 batch4 末位).
        reframe_note 283->295, miss 112->100.

Spec: r773-r800 档3 batch9-34 完成 reframe_note 32->235 (driver 三分 portability/Q&A-analysis/harness
      互斥可枚举归类). r826-r830 await-scan 期接续 backfill reframe_note 160 missing.
      本轮 batch5 12 case = 9 keep_reframe_for_teeth (portability) + 3 keep_faithful.

apply: cases/B/<case>.json metadata 新增 reframe_note (末位 key, 保留键序), indent=2 ensure_ascii=False。
       仅补 reframe_note, 不动 test_rationale/check.py/negative/asset_fidelity (asset_fidelity r824 已 100% 收口)。

Driver 分类 (12 case: 9 keep_reframe portability + 3 keep_faithful):
  - portability-driver (foundry PDK / real 网表/CSV/.lis/.sp 激励不可沙盒复刻 → synth_deck / synth_data):
      9 case: HierMeasIncGen (real DDR Dbus driver hspice 网表不可复刻→synth_deck) /
              HierarchyTrace (real 112MB LP5X fullchip 网表不可复刻→synth_deck) /
              IddblkCsvDiff (real finesim iddblk.csv 不可复刻→synth_data, characterization 域) /
              InvOptSpec (foundry PDK+real FineSim 不可复刻→synth_deck) /
              InvTripDelay (real .sp 激励+foundry 不可复刻→synth_deck) /
              LibCellListGen (real netlist 不可复刻→synth_deck) /
              LpfAnomalyDetect (real LPF netlist+m2701 PDK 不可复刻→synth_deck, Q&A-analysis 二级 subsumed) /
              LvLvioSweep (real DPmux8 netlist 不可复刻→synth_deck) /
              McLisSnmExtractor (real 5000-MC HSPICE .lis 不可复刻→synth_data)
  - keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful):
      3 case: GvimCjkConfigGen (A-faithful, env-config how-to→produce vimrc+report 同形) /
              HcellMissingFind (A-faithful, 找 missing block 同形) /
              IddIpfSignalEm (A-faithful, 修复 idd_to_ipf_flow.py 同形)

metadata bug 待 @A 档1/档2 sweep (reframe_note scope 限定不修, 仅在 note 文本标注):
  - 多 case layer 缺标或标 L2 待复核(check 仅 subprocess 跑候选 python 解析文本, 0 EDA 二进制, 应 L1)
  - level/k_check/shard 字段缺标
  - 与 r773-r800/r826-r829 档3 同口径: reframe_note backfill 不动其他字段
"""
import json, os

CASES_DIR = "/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/cases/B"

REFRAME_NOTES = {
    # ===== 9 keep_reframe_for_teeth (portability-driver) =====
    "EDA-Eval-DesignFlow-HierMeasIncGen-001":
        "DDR Dbus driver hspice 网表 PGSIG-gate PMOS 层级路径提取 + .measure isub inc.sp 生成->produce (portability-driver reframe, real DDR Dbus driver hspice 网表不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 reedchen@hfeg0pkn003 (sess 1794480714010_clz8j, mc=75) 两步需求 (U1) 从 DDR Dbus driver hspice 网表抓 128 个 Gate 端接 PPubN 信号的 PMOS 完整层级路径 XI0.XI<dq>.XI<drv>.XMMP<n>；(U2) 依 list 生成 .measure tran I_vintcore_stat_loss avg isub(<小写路径>.src) from '10n' to '30n' 的 inc.sp; trace agent 写 extract_final.py (递归解析 .SUBCKT + DqDbusDrv/Drv 子层级 + PGSIG-gate 匹配); A 不可行原因=real DDR Dbus driver hspice 网表不可沙盒复刻 -> 收敛为 extract_final.py (读 hidden B synth 网表, asset_fidelity=synth_deck); reframe 由 portability-driver (real DDR 网表不可复刻); 意图核心 (PGSIG-gate PMOS 层级路径提取 + .measure isub inc.sp 生成) 完整保留; check.py 10 断言验 zip 含 .py + py_compile + hidden B subprocess 真跑 exit0 产 inc.sp + 行数==15(独立 DFS 复算 B netlist PGSIG_B-gate PMOS 数 3×5) + 每行 .measure/isub(.src) 结构 + from/to 窗口==5n/25n(读自 B config) + isub 路径集合==独立层级遍历 GT + measure 名唯一前缀 I_vcore_loss_ + cross-input guard(A 产 16 行非硬编 B 的 15) + gate-sig 从 B config 读(PGSIG_B, 硬编 PGSIG_A 则 B 命中 0) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析网表产 inc.sp 文本, 0 EDA 二进制, 若仅文本解析应 L1), level 缺标应 L1, k_check 字段缺标应 10, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-HierarchyTrace-001":
        "LP5X DDR fullchip 网表 hierarchy 路径存在性检查器->produce (portability-driver reframe, real 112MB LP5X WOWTOP fullchip 网表不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 xinweif@hfeg0pkn005 (sess 1792204349915_1g0xs.messages.archive.json, mc=28) 用 FineSim 仿真 LP5X DDR fullchip 网表(112MB WOWTOP), 分析两路仿真(激励同网表异)致 rdqst fail vs pass 差异, U#70 原话「帮我写一个python脚本，检查这个hierarchy：xi_c_top.xi_array16gtop.xi_array8g_e.xi_array1gbk3.xi_m1g_top.xi_m512meg_u.xi_msaq_28 在这个网表是否存在」; trace agent 迭代 ~15 版 check_hierarchy.py Hierarchy Tracer 扫描 .SUBCKT/X 实例逐层验证; A 不可行原因=real 112MB LP5X fullchip 网表不可沙盒复刻 -> 收敛为 check_hierarchy.py(读 hidden B synth 网表, asset_fidelity=synth_deck); reframe 由 portability-driver(real 112MB 网表不可复刻); 意图核心(hierarchy 路径逐层存在性检查)完整保留; check.py 14 断言验 zip 含 1 个 .py + py_compile + B 合法路径 exit0 stdout 含 CHAIN: + B CHAIN==期望 8 名链 + B 断路径(末层伪实例)exit1 含 BREAK + A 合法路径 exit0 + A CHAIN==期望 9 名链 + A CHAIN≠B CHAIN(泛化非硬编) + B 伪顶层 exit1 + B CHAIN 恰 8 名 + 3 次运行 sha256 一致(幂等) + B CHAIN[0]==WOWTOPB(标准单元 inv/nor2/nand3/buf 被跳过) => 收敛为 produce-action 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析网表文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-IddblkCsvDiff-001":
        "finesim MatrixRun IDD characterization iddblk.csv 两份做差+插值+高亮->produce (portability-driver reframe, real finesim iddblk.csv 不可沙盒复刻->synth_data, §4 有牙必要, r830 reframe_note backfill batch5): 用户 jianwang@hfhds201 (sess 1791955659176_a63u6, mc=40, =.75 local, characterization 域) U#1「把这两个格式的csv文件做差，并将差异比较大的项高亮出来」+U#2「按cellname匹配后计算插值。计算的数据通过表格中的ext_vdd+ext_vddq+ext_vpp*1.64得到」+U#3「绝对差值大于10的高亮」; trace agent 写 csv_diff.py(cellname 匹配 common cells + calc=ext_vdd!+ext_vddq!+ext_vpp!*1.64 + diff=calc_f2-calc_f1 + |diff|>10 过滤降序); A 不可行原因=real finesim MatrixRun iddblk.csv 不可沙盒复刻 -> 收敛为 csv_diff.py(读 hidden B synth CSV, asset_fidelity=synth_data); reframe 由 portability-driver(real finesim CSV 不可复刻); 意图核心(cellname 匹配+插值 calc+diff+|diff|>10 高亮降序)完整保留; check.py 12 断言验 zip 含 .py + py_compile + 无参非零退出 + hidden B 两 CSV 跑通 exit0 产 output CSV + 表头含 cellName/calc_f1/calc_f2/diff + cellName 匹配正确(仅 common B 20) + calc 值正确(抽查 3 cell) + diff 值正确(抽查 3 cell) + |diff|>10 过滤正确(B 18 highlighted) + 降序排列 + cross-input guard(A 重跑≠B) + 每行 |diff|>10 => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 处理 CSV, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-InvOptSpec-001":
        "自定义反相器 invCSx1 W/L/M 联调优化 FineSim tran(delay<20ps/idd<100uA)->produce (portability-driver reframe, foundry PDK+real FineSim 不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 haifengf@hfeg0pkn002 (sess 1791960706202_66ut5, mc=301) 对自定义反相器 invCSx1 做 W/L/M 联调优化, U[91] 核心 spec「W/L/M 一起调，优化延迟<20ps，功耗<100uA，用 FineSim 来跑」, U[173] LMIN=39nm/VDD=1.1V/CLOAD=10fF/duty~50%, U[229] 输入 5GHz 方波 20-80% 边沿 20ps, U[241] FineSim 路径+ntn/ptn 模型; trace agent 构建 invcs_config/netlist_gen/finesim_runner/optimizer/selfcheck 端到端 harness; A 不可行原因=foundry PDK+real FineSim 不可沙盒复刻 -> 收敛为 inv_opt_spec_ref.py(level-1 Shichman-Hodges 反相器 DUT, .75 无 foundry 依赖, asset_fidelity=synth_deck); reframe 由 portability-driver(foundry PDK 不可复刻); 意图核心(W/L/M 网格优化 delay/idd 双约束)完整保留; check.py 16 断言验 zip 含 harness+report_A.json + py_compile + callable run() + 候选在 config_A 真跑 HSPICE hspice_ran=True + 全摆幅边沿=edge_20_80/0.6(/0.6 陷阱) + n_grid=8 + n_feasible=6 + best idx=1 + best delay≈15.04ps + best idd≈10.9uA + best duty≈49.97% + best Wp=2.0um Mp=1 + 每网格点 delay_ps 解析成功(.mt0 raw SI 陷阱) + B cross-input n_feasible=5 best idx=6 Mp=2(≠A, 硬编 A 败) + B best delay≈15.61ps idd≈15.06uA(防硬编) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 HSPICE 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 HSPICE 真跑), level 缺标应 L2, k_check 字段标 16 正确, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-InvTripDelay-001":
        "写电路 testbench spice 仿真激励生成 skill->produce (portability-driver reframe, real .sp 激励+foundry 不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 adaml@hfeg0pkn001 (sess 1792131744105_g48nq, mc=192) 在 /proj/drvsa/V0/workdir/adaml/drgqa_simulation/ 做 DR4/DDR5 I/O 与采样链路 HSPICE 后仿, 参考 DR9500_woCH_woFFE.sp/Curry_tes_DL_CDL/Lbx_DL_CPAMP_TB 等真实 .sp 激励, 要求 agent 生成『写电路 testbench spice 仿真激励』的 skill(保存到 ~/.cline/skills/spice_tb_stimulus/), 覆盖 option/corner/电源/温度/参数/netlist/SPF/analysis/probe/measure; trace agent 迭代产 tb.sp 仿真激励; A 不可行原因=real .sp 激励+foundry 不可沙盒复刻 -> 收敛为 tb.sp(synth_deck 反相器 inv DUT testbench, asset_fidelity=synth_deck); reframe 由 portability-driver(real .sp 激励不可复刻); 意图核心(写电路 testbench spice 仿真激励含 .tran/.measure/.dc)完整保留; check.py 14 断言验 zip 含 tb.sp + 非空文本 + 实例化 inv 子电路(引用非重定义) + .tran 瞬态分析 + .measure 延迟(trig+targ) + .dc 扫描+.measure dc when v()=v()(内建翻转点) + hidden B1 hspice 跑通无 fatal + B1 候选 tpd 与 GT 相对偏差≤15% + B1 vtrip 绝对偏差≤0.15V + B2 tpd 相对偏差≤15%(跨输入) + B2 vtrip 绝对偏差≤0.15V + zip 不含 .sh 外部分析脚本(测量必须 hspice 内建) + 候选 .lis(B1) 含 tpd=/vtrip= measure 结果行(非硬编 echo) + tb.sp 未硬编 A 答案(无 2.13/295.9/296 字面量) => 收敛为 produce-action 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 真跑 HSPICE 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 正确(check 验 hspice 在 B1/B2 真跑), level 缺标应 L2, k_check 字段缺标应 14, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-LibCellListGen-001":
        "netlist Library/Cell header 解析输出 lib_cell.list->produce (portability-driver reframe, real netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 ynbai@hfhds201 (sess 1791602435253_66tx9, mc=162) 提供 cell list 文件与 netlist, 要求生成脚本输出 lib_cell.list(格式 `Library Cell`); netlist 以 `* Library : <lib>`/`* Cell : <cell>`/`* View : schematic` header 块标识 subcell 归属, cell list 每行 `* Cell : <name>` 列出目标; trace agent 读 cell list+netlist+netlist.log, 设计 cell→library 映射(first-wins 多 library cell); A 不可行原因=real netlist 不可沙盒复刻 -> 收敛为 lib_cell_list_gen.py(读 hidden B synth cell_list+netlist, asset_fidelity=synth_deck); reframe 由 portability-driver(real netlist 不可复刻); 意图核心(cell→library 映射输出 lib_cell.list)完整保留; check.py 12 断言验 zip 含 .py + py_compile + --help exit0 提及 cell/netlist 参数 + hidden B 跑通 exit0 + 输出非空每行 `<lib> <cell>` 格式 + B 条目集合==期望 5 个 + 无重复行 + 保持 cell_list_B 顺序(跳过 missing) + 不含 A 的 library(跨输入排除) + 多 library cell(PhyRdDqs)用首个(first-wins) + cross-input guard(A 列表==期望 4 行 A≠B) + A 输出恰 4 行(去重重复+跳过 NOTFOUND+first-wins) => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 netlist 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-LpfAnomalyDetect-001":
        "PLL LPF SPICE 网表结构分析+4 类异常检测器->produce (portability-driver reframe, real LPF netlist+m2701 PDK 不可沙盒复刻->synth_deck, Q&A-analysis 二级 subsumed 进 detector JSON, §4 有牙必要, r830 reframe_note backfill batch5): 用户 wnyu@hfeahpc502 (sess 1794474582550_btfno, mc=134) PLL LPF SPICE 网表结构分析: 找 m2701 PDK 电阻 res(intDEV 库)+读 LPF netlist 分析电路拓扑+识别 XR1 短接电阻/switch_open-close 死子电路/XPM0-XPM2 四端短接 MOS/R0 近零电阻 4 类结构异常+VCTRL→Rz→VCTRLH 零点抵消 Q&A+MOS cap 跨 Rz 必要性 Q&A; trace agent 写 lpf_anomaly_detector.py; A 不可行原因=real LPF netlist+m2701 PDK 不可沙盒复刻 -> 收敛为 lpf_anomaly_detector.py(读 hidden B synth LPF 网表, asset_fidelity=synth_deck); reframe 由 portability-driver(real LPF netlist+m2701 PDK 不可复刻); Q&A-analysis(VCTRL→Rz/MOS cap 解释)二级 subsumed 进 detector JSON 结构化 findings(主 driver=portability 因 asset 须合成, Q&A 由 detector 结构化输出兜底); 意图核心(4 类结构异常检测)完整保留; check.py 13 断言验 zip 含 .py + py_compile + hidden B subprocess 真跑 exit0 + 输出 JSON 含 4 异常子键 + shorted_two_port 检出==GT + all_terminals_tied 检出==GT + defined_not_instantiated 检出==GT + near_zero_resistor 检出==GT + 无误报(检出⊆GT 并集且数量相等) + instance_count==独立复算 + subckt_def_count==独立复算 + A≠B 非硬编(XR1 在 A 检出 B 无) + 空网表优雅处理(合法 JSON total=0) + 确定性 3 次字节一致 => 收敛为 produce-JSON 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析网表文本, 0 EDA 二进制, 若仅文本解析应 L1), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-LvLvioSweep-001":
        "DPmux8 lv-vs-lvio 评估: 4 .measure + 三维扫描建变体网表(Width×Length×类型)->produce (portability-driver reframe, real DPmux8 netlist 不可沙盒复刻->synth_deck, §4 有牙必要, r830 reframe_note backfill batch5): 用户 yifansun@hfeg0pkn001 (sess 1793886971551_nekpi, mc=743) DPmux8 block lv-vs-lvio 评估, 给 input.sp+netlist 路径, 要求 (a) 添加 4 项 .measure(信号延迟/动态读电流/动态写电流/静态电流); (b) 三维度扫描建 60 个变体网表(Width 5 档×Length 6 档×类型_lvio↔_lv 2 档); 约束: 参数引用 w='WP1' 不改、真实 width=width/nf 夹[150nm,2um]、仅 46nm 长度替换; trace agent 写 gen_variants.py; A 不可行原因=real DPmux8 netlist 不可沙盒复刻 -> 收敛为 gen_variants.py(读 hidden B synth netlist+config, asset_fidelity=synth_deck); reframe 由 portability-driver(real DPmux8 网表不可复刻); 意图核心(三维扫描建变体网表+4 .measure+width 钳位+46nm 长度替换+参数引用保持)完整保留; check.py 14 断言验 zip 含 gen_variants.py + py_compile + hidden B exit0 产 out_dir + 变体网表数=32(4×4×2) + lv 变体类型互换 ntn_lvio→ntn_lv 无 _lvio 残留 + 非钳位 width 缩放正确 + 参数引用 w='WP1' 不变 + width 上下限钳位(2um/150n) + 46nm 长度替换目标值非 46nm 保持 + deck 数=32 含 B 4 条 .measure 窗口匹配 B + deck 含 .tran(B 1p 1500n)+.end + 跨输入信号护栏 B deck 用 v(neta<3>) 非 A net36<7> + run_all.sh 含 32 条 bsub fqueue2h finesim + variant_summary.txt 报告 32 变体 + cross-input guard 跑 A→60 变体 deck 用 net36<7> => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 生成变体网表文本+deck, 0 EDA 二进制 run), level 缺标应 L1, k_check 字段标 14 正确, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-McLisSnmExtractor-001":
        "6T SRAM bitcell 5000-MC HSPICE .lis 蝶形分析 RSNM/HSNM 提取+bootstrap bug fix->produce (portability-driver reframe, real 5000-MC HSPICE .lis 不可沙盒复刻->synth_data, §4 有牙必要, r830 reframe_note backfill batch5): 用户 e0030760@hfeg0pkn004 (sess 1794459639804_2692p, mc=105) 6T SRAM bitcell 5000-MC HSPICE .lis 蝶形分析: 提取每样本 RSNM/HSNM+GUI butterfly 图+最大内接正方形标注; 发现 bootstrap 死锁 bug(vin voltage 列头仅在 cur is not None 时识别→0 样本), fix 为无条件 arm pending; dual-marker 随机访问索引(只提交 DC marker 排除 transient marker); SNM=Seevinck 最大轴对齐内接正方形边长(binary-search+sliding-window min); trace agent 写 extractor; A 不可行原因=real 5000-MC HSPICE .lis 不可沙盒复刻 -> 收敛为 snm_extractor.py(读 hidden B synth .lis, asset_fidelity=synth_data); reframe 由 portability-driver(real HSPICE .lis 不可复刻); 意图核心(RSNM/HSNM 提取+bootstrap 死锁 fix+dual-marker 索引+Seevinck max-square)完整保留; check.py 13 断言验 zip 含 .py + py_compile + hidden B subprocess 真跑 exit0+JSON 解析 + JSON 含必需键(n_samples/rsnm/hsnm/index_size/index) + n_samples==8(双 marker transient 不计) + bootstrap 死锁 fix(n>0 且首 'vin voltage' 列头前无表) + RSNM 列 len==n 值 [0.05,0.5]V + HSNM 列 len==n 值 [0.05,0.5]V mean(HSNM)>mean(RSNM) + 独立 O(n²) 暴力 max-square 复算 B 样本1 一致 + dual-marker 索引 index_size==n offset 指向 marker+q_rnm + --sample K 详情 4 完整节点表+rsnm_square 几何 + A≠B 反硬编(A n_samples==6 mean≠B) + 确定性 3 次逐字节一致 + 退化空 .lis exit0 n_samples==0 无 traceback => 收敛为 produce-harness 是让 check() 能区分真假交付的唯一途径, §4.1 hidden-B + §4.2 subprocess 结构性必要, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(check 仅 subprocess 跑候选 python 解析 .lis 文本+算 SNM, 0 EDA 二进制, 若仅文本解析应 L1), level 缺标应 L1, k_check 字段缺标应 13, shard 缺标应 B。",

    # ===== 3 keep_faithful (无 reframe, trace 意图同形便携, asset A-faithful) =====
    "EDA-Eval-DesignFlow-GvimCjkConfigGen-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r830 reframe_note backfill batch5): 用户 adaml@hfeg0pkn002 (sess 1791513539900_7bxtm, mc=21) U#0 问 gvim 中文乱码怎么办, 意图形态=how-to-Q&A+produce-action(agent 探系统环境后生成 vimrc+诊断报告, 非 pure Q&A 文本回复), 可便携性=高(locale 探测/vimrc 配置/字体检测纯文本无 EDA 二进制依赖, asset_fidelity=A-faithful); trace agent 探系统环境(locale=en_US.UTF-8/Vim 8.0/Noto CJK+DejaVu 等宽字体/无 .vimrc), 生成 ~/.vimrc(encoding 检测+guifont 等宽+guifontwide 无衬线 CJK)+诊断报告, 三轮追问迭代(乱码->间距->衬线不一致); case 交付 gvim_cjk_config_gen.py+gvim_cjk_config.vimrc+gvim_cjk_config_report.json 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, env-config how-to 是 2026-11-15 令恢复的合法任务形态, trace agent 产 vimrc+report 与 case 交付 gen script+vimrc+report 同形映射); check.py 21 断言验 zip 含 .py+py_compile+B subprocess exit0 产 vimrc+report 双文件+report 合法 JSON dict+14 顶层键齐全+cross-input(user/host/locale/vim_version/installed_cjk_fonts/installed_mono_fonts)+root_cause_analysis 含 B primary_display_issue+vimrc set encoding=utf-8+fileencodings 含 utf-8+CJK 编码(cp936/gbk/gb18030)+guifont 族名∈B installed_mono_fonts(不得 A DejaVu/Liberation)+guifontwide 族名∈B installed_cjk_fonts(不得 A Noto)+tabstop==B(A=4 B=2)+background==B(A=dark B=light)+colorscheme==B(A=desert B=morning)+A-leak 守卫 11 个 A 专属 token 不得出现+确定性 3 次 rerun sha256 一致 => §4 牙由 hidden-B cross-input(11 A-leak token guard)+§4.2 subprocess 保证, layer=L1, k_check=21==k_rationale=21 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 缺标应 L1(check 仅 subprocess 跑候选 python 探环境产 vimrc+report, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 21, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-HcellMissingFind-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r830 reframe_note backfill batch5): 用户 zjqiao@hfhds201 (sess 1793347412273_nq8l2, mc=98) 提供 hcell 映射文件(每行两列, 第一列 block 名)与 SPICE netlist(AETHER-SE 导出 148MB drvqa_top/WOWTOP_1C2A), 要求把 hcell 第一列逐行在 netlist 中检索找缺失/改过名 block, 意图形态=produce-action(找 missing block 工具), 可便携性=高(纯 Python 解析 netlist .SUBCKT/* Cell header/X 实例引用三类命中位置, 无 EDA 二进制依赖, asset_fidelity=A-faithful); trace agent 写 check_hcell_in_netlist.py 扫 netlist 三类命中位置报告 not-found blocks, deep_search 查 rename; case 交付 check_hcell_in_netlist.py 同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, trace 意图「找 missing block」与 case 交付同名解析器同形映射); check.py 12 断言验 zip 含 .py+py_compile+--help exit0 提及 hcell/netlist 参数+hidden B(hcell_B+netlist_B) exit0+输出非空每行单 token+missing 集合==期望 5 个+无重复行+保持 hcell_B 顺序+* Cell header 检测(AG_PhonyVibCom 仅 * Cell header 命中 .SUBCKT 改名 _v2 不在输出)+X 实例引用检测(T_DDR5IsmTop 仅 X 引用不在输出)+rename 陷阱(AG_PhonyActSpare 改名 exact 匹配失败→missing 须在输出, substring 匹配会假阳性漏报)+cross-input guard(A missing==期望 5 行 A≠B 含 rename 陷阱 AG_VdivActTopSpare 不含重复 FOUND AG_VdivActTop) => §4 牙由 hidden-B cross-input+§4.2 subprocess 保证, layer=L1, k_check=12==k_rationale=12 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L1 正确(check 仅 subprocess 跑候选 python 解析 netlist 文本, 0 EDA 二进制), level 缺标应 L1, k_check 字段缺标应 12, shard 缺标应 B。",

    "EDA-Eval-DesignFlow-IddIpfSignalEm-001":
        "keep_faithful 无 reframe (trace 意图同形便携, §4 无需重构, r830 reframe_note backfill batch5): 用户 yongk1li@10.129.8.125 (sess 1789710184698_xbtsx, mc=77) 在 /home/yongk1li/bin/totem_sc_signal_em/ 维护 DDR5 Signal EM launcher, 配套脚本 idd_to_ipf_flow.py 把 Finesim IDD 仿真 CSV 转 Totem-SC IPF 功耗文件, trace 里用户先问 'totem_sc_signal_em 目录是干嘛的'/'idd_to_ipf_flow.py 看看这个脚本是干嘛的'(explain-Q&A 子意图), 核心交付=修复 idd_to_ipf_flow.py(按层级提取 cell 实例×电压算功耗/GDS 纠正大小写/阈值过滤), 意图形态=produce-action(修复脚本, Q&A-understand 是修复前置非独立交付), 可便携性=高(IDD CSV/IPF 文本纯 Python 处理无 EDA 二进制依赖, asset_fidelity=A-faithful); trace agent 解读脚本+修复 legacy 配置+大小写纠正+阈值过滤; case 交付 idd_to_ipf_flow.py+output.ipf+WHITE_BOX_CELLS+idd_inst_dump.txt 4 文件同形(零偏移, A-faithful); reframe_note=None->补(faithful 无 reframe, debug-Q&A-understand+fix 是 2026-11-15 令恢复的合法任务形态, trace 意图「修复 idd_to_ipf_flow.py」与 case 交付 fixed script+4 文件同形映射, Q&A-understand 子意图 subsumed 进修复交付); check.py 10 断言验 zip 含 4 交付件+交付脚本无 legacy 配置(TARGET_LEVEL/TARGET_CELLS/TARGET_FATHER_CELLS 缺席+if not OUTPUT_SPECS fallback 缺席)+hidden B subprocess exit0+output.ipf 头 2 行 header+条目数==200(2 cells×100, 大小写 bug 版得 0 条 FAIL)+功耗值正确(BCenterCA_X=0.00343440 vdd1 1.908V×idd×1e-6 tol 1e-7, 硬编 A stub FAIL)+阈值过滤(viso root idd=800<=1000 跳过, pin==vdd1! 无 viso!)+WHITE_BOX_CELLS 格式含 2 纠正 cell+大小写纠正(BCenterCA_X 非 bcenterca_x)+idd_inst_dump.txt header+2 行实例 idd/power 正确 => §4 牙由 hidden-B cross-input+§4.2 subprocess 保证, layer=L1(应, check 仅 subprocess 跑候选 python 处理 CSV→IPF, 0 EDA 二进制), k_check=10==k_rationale=10 ✓, 无 reframe, 保留。**metadata bug 待 @A**: layer 标 L2 待复核(应 L1, check 仅 subprocess 跑候选 python 处理 CSV→IPF 文本, 0 EDA/Totem-SC 二进制), level 缺标应 L1, k_check 字段缺标应 10, shard 缺标应 B。",
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
