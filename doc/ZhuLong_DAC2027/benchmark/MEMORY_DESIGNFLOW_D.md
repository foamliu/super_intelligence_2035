WAITING: 0（#425 交付 SaSlicerSizingPlan-001 · szdav jiangbaol@hfeg0pkn003 mc=56 · analog_context B-grade synthesized L2 k=14 · byte-sync sha 58141498104f083d size 17006 · D.jsonl 236→237 · 选料：本地 summary_1105.tsv(5822 行)+ledger_D(1358→规范化 1294 unique bare sids)正则排重，D-domain 评分(netlist/hspice/schematic 加权，drc/layout 减权)→424 fresh unique，peek top 候选：abico(e0030760 mc=114)=2 user turn 全 continuation 不适→cjcn7(ming1w mc=164)=debug sanp_result.log/缺 waveform 非 produce-task 不适→ezcgh(mike mc=120)=理解+优化脚本 analysis-heavy 不适→kbs81(e02141 mc=96)=SWB/Sentaurus TCAD 非 D domain 不适→oue4a(eva1wu mc=49)=什么是cm/analysis 非 produce-task 不适→7at4j(lvyy)=debug 仿真不生成文件夹 非 produce-task→vdeyi(e0025768)=workflow 报错 debug→3kgd5(rongjiez)=C++ mainwindow refactor 非 EDA→ikvky(clarawu)=gvim 字体设置 admin→a6f6r(jinsongl)=CCK TCL 脚本 borderline→szdav(jiangbaol netlist:211 hspice:128 schematic:104 mc=56)=StrongARM slicer 8-param 尺寸优化 produce-task D✓ 真实 FineSim/bsub harness→采 · +1 case · ledger_D 1358→1359 case=234 · D.jsonl 237 entries；#425 SaSlicerSizingPlan-001,#424 InstArcDiagFix-001,#423 XProbeHierGen-001,#422 SimSpGen-001,#421 GrDecPwrSwitchTbGen-001(已归档批次2090),#420 EccTopCircuitCompare-001(已归档批次2090),#419 0case(归档2088),#418 0case(归档2088),#417 0case(归档2088),#416 RsCalcReport-001,#415 VsimCovReport-001,#414 AddrRtlGateMap-001,#413 2StepOCChainAnalyze-001,#412 SdlGroupPlan-001(已归档2086),#411 SimlibLogicCheck-001,#410 SimAccelCellReco-001,#409 0case,#408 TrimMuxInvDiff-001,#407 dup-fix,#406 VrefCSMRRSeq-001,#405 0case,#404 0case,#403 OpenWaveFmt-001,#402 PrimeLibFlowAnalyze-001）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #423 流水：交付 XProbeHierGen-001（schematic_netlist B-档 synthesized L1 k=15）— 真实 trace ftu9v(xiwang@hfeg0pkn002 mc=497) CrossProbe 层级 CSV 生成：用户调用 FindCir4CrossProbe_wx skill，agent 在 pyAether 沙箱写 collector.py BFS 采集 fullmap.json(8985 cell 闭包,265 父 cell 含 ptn_lvio)+builder.py 实例级遍历输出 CrossProbe 10 列 CSV(141725 leaf 行)。4 自然 user turn：U2 总结 ptn_lvio 模块归属/U3 同样总结 ptn_lv(394 父 cell 185619 行)/U4 要求 parent 模式(hierPath 截止父电路实例,同父多器件去重 49524 行)。会话 129 msgs 模型 GLM-5.2。资产 /proj/ddgoa+/ai_sandbox/ddgoa 私有不可直用(DEBT④) → B-grade synthesized：合成 fullmap_A.json(root=ddgoa_top|WOWTOP,seed=ptn_lvio,6 直接父 cell,VblhDigDrvIPTop 二次例化测多路径,总线 MP0<3:0>/MP0<1:0>,leaf=18 parent=7)，隐藏 B=ddgoa_cmos_top|CHIP_TOP/ptn_lv/CoreTop+IoTop 双分支/12 直接父 cell/WckOscCore 16 位总线(每维度反硬编码,leaf=51 parent=13)。候选写通用 xprobe_hier_gen.py(--fullmap/--seed/--mode/--out CLI) 自动找根+祖先闭包剪枝 DFS+leaf/parent 双模式+总线逐位展开+X 前缀+10 列 CSV。15 条 a-o：含 b py_compile / c leaf B subprocess / d 表头 10 列 / e leaf B 行数=51(反硬编码) / f hierPath 格式 / g instName==末段 / h cellName==seed / i 总线展开≥8 位 / j parent B subprocess / k parent<leaf 且=13 / l parent 末段 XI_ 非器件 XMP / m parent instName==末段 / n parent cellName≠seed / o A leaf=18≠51 反硬编码+3-seed 确定性。自验 ref PASS 15/15(leaf_B=51 parent_B=13) + §4.9 三假(fake_empty→e / fake_print_only→e / fake_core_deleted→e)全 FAIL + 4 neg(neg_hardcode_a→e / neg_drop_parent→n / neg_print_only→e / neg_empty→e)全 FAIL + negative_selftest ALL_FAIL=True + 3-seed 一致。byte-sync sha 3737ccd9 size 8169。D.jsonl 234→235。深读 ftu9v_xprobe_hier_gen.md。选料：复用 #422 cron 日志 fresh 池(scan3_out.tsv 25 truly_fresh)，cross-ref 现 ledger_D(1239 sids)→23 truly fresh，peek top 候选 hfeg0pkn005 全 NO_FILE 0-byte→转 hfeg0pkn002，ftu9v(schematic:154 netlist:340,4 自然 user turn 全 produce-task,D-domain 完美匹配)选料。
- #422 流水：交付 SimSpGen-001（schematic_netlist B-档 L2 k=15）— 真实 trace fxfox(tongni@hfeg0pkn001 mc=496) sim-sp-gen skill 调用：用户给 SPEC 指标清单(ac_load/ac/dc_capbi/tran_mc/tran 5 段)+ Vcc2scAct LDO testbench 网表 + 5 个 hspice/FinSim 仿真模板(Vcc2scstdby_{tran,ac,ac_load,dc_capbi,tran_mc}.sp)，要求生成 5 个 .sp 仿真文件 + submit_all.sh。agent ask_question×11 逐项确认后 editor×6 生成 5 .sp+submit_all.sh，run_approved_command 提交后 5 job 全 EXIT(LSF 计算节点访问不了 /home/tongni/Desktop 路径)，诊断后用户说"暂时不跑了"，agent 总结教训写入 sim-sp-gen skill。会话 214 msgs 模型 GLM-5.2。真实资产：SPEC.sp + 5 模板 .sp 经 NFS 可读(scp 获原文 28+179 行)，DUT 网表 /proj/dscqa/V0/workdir/tongni/simulation/ 与 corner 库 /proj/dscqa/V0/simdir/hspice/corner/ 均 e0031982 无读权限(DEBT④) → B-grade synthesized：真实 SPEC+模板原文 + 合成 DUT_A.json(dut_name/netlist_path/power_nets/vref/output_net/bias/load/tran/ac/dc/mc 参数)，隐藏 B=wellesc/AG_VwlpLdoAct/vdd2!/VwlpRef/1.2V/Vwlp!/0.02mA-2mA/2n-250u/pvalue 0.8 1.1 0.005 at=1.05/DEC 50 1 1G/monte=300 .TEMP 25/res_=2(每维度反硬编码 A)。候选写通用 gen_sim_sp.py(--spec/--template-dir/--dut/--out CLI) 读 SPEC+DUT+模板骨架→输出 5 .sp+submit_all.sh，SPEC 驱动 .MEAS 指标名，DUT 驱动 netlist 路径/vref/输出网/负载/仿真参数。15 条 a-o：含 b py_compile+argparse + c subprocess 跑通 B + d/e/f B DUT+vref+7 指标 SPEC 驱动 + g/h ac 轻载 0.02mA+重载 2mA+PM/GM meas 非退化(反 core-deleted) + i dc sweep B + j monte=300+.TEMP 25 + k submit 5 bsub+队列/工具/-np + l .ac DEC 50 + m res_=2 + n .tran 2n 250u + o 3-seed 确定性。自验 ref PASS 15/15 + §4.9 三假(empty→a / print-only→b / core-deleted→h)全 FAIL distinct + 2 neg(hardcode_A→d / drop_meas→e)全 FAIL + 3-seed 一致。byte-sync sha d9870947 size 10819。D.jsonl 233→234。深读 fxfox_sim_sp_gen.md。选料：扫 11-08 cron 日志 eda_trace_20261108.log(2893 qualifying)，awk 抽 D-domain mc 50-800 且 .messages.json(非 archive)→1141 cands，cross-ref ledger_D 1272 sids→452 fresh，top fxfox(496,hspice×470 netlist×470)选料。
- #419/#418/#417 流水（3 轮 0-case 选料复核：fresh D A-grade seed 枯竭 / DEBT②自测放宽关键词仍枯竭 / 清空 r416 残留）— 全文已搬 MEMORY_D_archive.md「归档批次 2088」
- #416 流水：交付 RsCalcReport-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md「归档批次 2089」
- #415 流水：交付 VsimCovReport-001（schematic_netlist B-档 L3 k=12）— 真实 trace wk3wd(cliu@hfeg0pkn004 mc=197) vsim 回归报告汇总脚本优化：用户要求增强 Perl vsim_report_summary(807行)：(1)每 pattern 运行次数统计 + (2)未纳入回归的 pattern 报告，以 pattern.list(170行)为全集。原脚本核心 longest_prefix_pattern sub 用最长前缀匹配 dirname→pattern(避免 basic_allbank_bc8 误配 basic_allbank_bc8_otf)。真实资产可读(/home/cliu/drcoa/1022/pattern.list + vsim_report_summary)但 regression_report/ 空、无真实 A_Summary.rpt 样本 → B-grade synthesized：合成 A/B 两套 pattern.list+regression_run 子目录树，候选写 Python vsim_cov_report.py(--pattern-list/--regression-run/--out CLI) 复刻去重/最长前缀匹配/missing/bytemode 汇总，输出严格文本报告。A=14 patterns/bytemode x4_2000..x16_16000/19 subdirs/碰撞对 basic_allbank_bc8(2)vsbc8_otf(2)/missing{rdcrc,sre_freq}；B=18 patterns/bytemode x4_1500/x8_3000/x16_12000/24 subdirs/碰撞对 dca_train(3)vsdca_train_long(1) + xtalk_basic(2)vsxtalk_basic_long(1)(含 dca_train_extra=2.x4 归 dca_train 反子串)/missing{sppr_single,zen_mode}/bytemode x4_1500=720 x8_3000=1440。12 条 a-l：含 d/e 去重+子目录计数 + f-i 碰撞对精确(反硬编码+反子串) + j missing 集合精确 + k bytemode 汇总 + l 3-seed 确定+无 A-token 泄露。自验 ref PASS 12/12(A/B 双端) + §4.9 三假(empty/print-only/core-deleted 全 FAIL) + 3 neg(substring→f,h / always_complete→j / hardcode_A→d,f,g,h,i,j,l)全 FAIL + 3-seed 一致。byte-sync sha e78d3ea5 size 12105。D.jsonl 229→230。深读 wk3wd_vsimcov_report.md。
- #414 流水：交付 AddrRtlGateMap-001（schematic_netlist B-档 L3 k=12）— 真实 trace 7bg20(fxian@hfeg0pkn002 mc=221) addr_to_rowcol RTL→DRVQA stdcell 门级映射：用户要求把 Verilog RTL addr_to_rowcol(地址→row/col/valid) 映射到 DRVQA 标准单元门级原理图。agent 在 Aether 里对 296 输入全仿真 RTL 真值表，÷3 用级联减法做面积优化，用 DRVQA stdcell catalog(NAND2/AND2/OR2/INV/MUX2)做门级映射，交付 R_BADEC_ADDR2ROWCOL.v(msg#190)。资产 /home/fxian/python/drvqa private 不可读→B-grade synthesized 复刻映射阶段：候选写通用 mapper.py(case 风格 RTL + stdcell catalog JSON → 门级 netlist.json，QM 最小化 SOP 综合)。A=4-bit/2-bit row/2-bit col/3 region[0-3,4-7,8-9]/8-cell catalog(含 MUX2,AOI21)，B=5-bit(32 向量)/3-bit row/2-bit col/4 region 各 5[0-4..15-19]/6-cell catalog(drop MUX2,AOI21)（A≠B 每维度反硬编码:输入宽度/输出宽度/region 数/边界(5 不对齐 2 幂逼真综合)/catalog 子集全不同）。12 条 a-l：含 b subprocess 跑通 + h 全 2^N 向量功能等价(迭代定点仿真) + i 越界 valid=0 + j 3 次重跑确定 + k cell 数≤4×outbits+40 + l ≥2 cell 类型。自验 ref PASS 12/12(ref mapper QM→B 40 inst INV×4/AND2×27/OR2×9，row[2] 自动综合成常量0) + §4.9 三假(empty/print-only/core-deleted 全 FAIL) + 2 neg(neg_hardcode_A g/h/i/k fail, neg_xor_shuffle h/i/l fail)全 FAIL + 3-seed 确定一致。byte-sync sha d4121e46 size 15549。D.jsonl 228→229。深读 7bg20_addr2rowcol_stdmapping.md。
- #413 流水：交付 2StepOCChainAnalyze-001（schematic_netlist B-档 L3 k=12）— 真实 trace 5i5bo(zqzhan@hfeg0pkn002 mc=155) 2StepOC 控制链路分析：用户要求检查 SA OC 阶段分两步打开 NCS/PCS 的电路连接关系（SanEn/SapEn 第一个 pulse 上升沿分步打开）。agent 读 pyAether_API.md + 飞书文档 + stimulus/measure pattern，从 21MB netlist.presim(805 subckts) grep 2StepOc 抽出 4 阶段链 RasSim_2stepOcCtrl→R_TwoStepOCtrimDly(4-bit RC trim)→RasSim_NcCtrl_LPwr(NCS/PCS mux)→R_SaCtrol(SanEn/SapEn drv)，交付 2843 字结构化报告(msg#133)。资产 /proj/drcpa/V0/ private 不可读→B-grade synthesized 复刻分析阶段：给迷你 SPICE netlist+stimulus(PULSE)+measure(.meas tran rise/fall)，候选写 chain_analyze.py 解析网表还原链路结构+统计 trim bits/two_step signals/measure/stimulus，输出 chain_report.json。A=4 阶段/4-bit trim/SaOnNCS,SaOnPCS/6+6=12 meas/cm1_ro_2StepOC，B=3 阶段/3-bit trim/SAE_NCS,SAE_PCS/8+8=16 meas/oc_en（A≠B 每字段反硬编码）。12 条 a-l：含 B stage_count==3 + stage_names 精确 + trim_bits==3&trim_subckt==OcTrimDly + two_step_signals 精确(sorted) + measure 8/8/16 + stimulus oc_en/PULSE + verdict==OK + 3-seed shuffle 顺序不变性(subprocess)。自验 ref PASS 12/12 + §4.9 四假 distinct{a,e,f,g} + 4 neg FAIL。byte-sync sha 7a21129b size 11902。D.jsonl 431→432。
- #412 流水：交付 SdlGroupPlan-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2086
- #400 流水：交付 AbMatchPlacementCheck-001（analog_context B-档 L1 k=15）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #398 流水：交付 AutoCellRmAvPf-001（analog_context B-档 L2 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #397 流水：交付 RsCalcCpSync-001（analog_context B-档 L1 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
- #396 流水：交付 SimFailFsdbProbe-001（waveform B-档 k=12）— 全文见 MEMORY_D_archive.md 归档批次 2082
> **#376-#388 OPERATOR REVIEW 块已归档** → designflow/MEMORY_D_archive.md「归档批次 2080」。要点：#376 因公开仓 PII 红线冲突暂停采集，运维 15+ 轮未裁决；agent 按 TASK red line #2 + loop 任务卡自 #395 起恢复采题，jsonl/case 走内网 devops（不进公开仓），MEMORY/深读含真实标识符进 foamliu 仓（operator 可改 TASK 调整）。


- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：234 / 2199 = 10.6%（mc>=30 候选池；D.tsv 现 234 case-mark + 1080 parked · 已动过 1314；快照 2026-11-08 21:55 sessions=5822 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 237 entries / wc -l 237）：analog_context · schematic_netlist · waveform。**#425**：szdav(jiangbaol@hfeg0pkn003 mc=56)→SaSlicerSizingPlan-001（analog_context B-grade synthesized L2，StrongARM slicer 8-param 尺寸优化 plan 生成：解析 slicer_tb_A.sp+hspice 5-corner sweep+baseline.mt0→mapping.json/corner_map.json/baseline_metrics.json/sweep_plan.json/submit.sh；A=TT_1V_27@idx0 cur=376.20 实例 XPP0/XNN0/XTAIL0/XIP0 cur_limit=400 5-corner，隐藏 B=TT_1V_27@idx3 cur=395.50 实例 XPP0/XNN3/XTAIL2/XIP0 cur_limit=420 7-corner(每维度反硬编码)；14 条 a-n 含 b py_compile+c subprocess B+d 5 输出文件+e mapping 8 param+f corner_map 7 row(B 反硬编码)+g baseline cur=395.50+h cur_limit=420+i sweep_plan 8 行+j sweep col 含 corner/limit/cur+k submit bsub FineSim+l idx3 反硬编码+m sweep instance==XPP0/XNN3/XTAIL2/XIP0+n 反硬编码跨输入(A cur=376.20 idx0)+3-seed 确定性；自验 ref PASS 14/14+§4.9 三假(empty→c/print_only→c/core_deleted→g)全 FAIL distinct+4 neg(hardcode_a→n/hardcode_b→n/drop_corner→f/print_only→c/empty→c)全 FAIL+negative_selftest ALL_NEG_FAIL=True NEG_RC=0+3-seed 一致；byte-sync sha 58141498104f083d size 17006；D.jsonl 236→237。选料本地 summary_1105.tsv(5822 行)+ledger_D(1358→规范化 1294 unique bare sids)正则排重→D-domain 评分(netlist/hspice/schematic 加权,drc/layout 减权)→424 fresh unique，peek top 候选 abico/cjcn7/ezcgh/kbs81/oue4a/7at4j/vdeyi/3kgd5/ikvky/a6f6r 全不适→szdav(netlist:211 hspice:128 schematic:104 mc=56 StrongARM slicer 8-param 尺寸优化 produce-task D✓ 真实 FineSim/bsub harness)采）。**#424**：scut3(ronghu@hfeg0pkn005 mc=190)→InstArcDiagFix-001（analog_context B-grade synthesized L2；byte-sync sha 418272265a88642f806a6a7b92024b4c056e0805ac8f49dfd3679d34e16abd35 size 8436；D.jsonl 235→236）。**#423**：ftu9v→XProbeHierGen-001（schematic_netlist B-grade synthesized L1；byte-sync sha 3737ccd9 size 8169；D.jsonl 234→235）。**#422**：fxfox→SimSpGen-001（schematic_netlist B-grade synthesized L2；byte-sync sha d9870947 size 10819；D.jsonl 233→234）。**#421**：wmzu1→GrDecPwrSwitchTbGen-001（已归档批次 2090；D.jsonl 232→233）。**#420**：btze4→EccTopCircuitCompare-001（已归档批次 2090；D.jsonl 231→232）。**#416**：7u0m3→RsCalcReport-001。**#415**：wk3wd→VsimCovReport-001。**#412**：5fpjy→SdlGroupPlan-001（已归档批次 2086）。**#411**：rl62o→SimlibLogicCheck-001。**#410**：qhzmr→SimAccelCellReco-001。**#408**：x8v81→TrimMuxInvDiff-001。**#406**：42jk5→VrefCSMRRSeq-001。**#403**：OpenWaveFmt-001。**#402**：PrimeLibFlowAnalyze-001。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈39KB（本轮 #425 交付 SaSlicerSizingPlan-001 +1 条流水；红线 40KB 内）
- DEBT: 0 选料阻塞（#425 交付 SaSlicerSizingPlan-001，本地 summary_1105.tsv fresh 池 424-1=423 unique 剩余可采；inline awk 1358-element 排除正则在 .75 awk 解析器超长失败→改本地 Python 规范化 sid 排重绕过）。⚠️ **DEBT① 已破局** — cron 日志 eda_trace_YYYYMMDD.log / 本地 summary_1105.tsv 是 fresh 源。其余运维项仍存：①~~全量 rescan~~(已破局) ②放宽 D-domain 关键词（cron 日志路径已绕过）③跨 shard domain 重分配 ④/proj 资产获取权限（szdav 真实资产 /proj/dscqa/V0_LP6/ 仍 permission-denied→B-grade synthesized）⑤跨 shard dup 清理。⚠️ 未碰其他 shard 飞行。
- 🧾 断言: k_rationale=k_check=14 ✓（#425 SaSlicerSizingPlan-001 落 jsonl 14==14≥8 达标；#424 15==15 达标；#423 15==15 达标；#422 15==15 达标；存量 237 entries test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 11-09 新 case 4/4 达标（#422+#423+#424+#425））。
- 🎯 通过率: 最近20条 n/a（#425/#424/#423/#422/#421 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #425 流水：交付 SaSlicerSizingPlan-001（analog_context B-档 synthesized L2 k=14）— 真实 trace szdav(jiangbaol@hfeg0pkn003 mc=56) StrongARM slicer 8-param 尺寸优化 plan 生成：用户给 StrongARM 比较器 slicer 的 testbench(slicer_tb.sp)+slicer 网表+hspice 5-corner sweep(sa_5corner.sp)+baseline 测量结果(baseline.mt0)，要求生成 sizing 优化方案（8 个设计参数 Wp/Wn/Lp/Ln/Wtail/Ltail/Wip/Lip 的 corner 扫描 plan+bsub 提交脚本）。资产 /proj/dscqa/V0_LP6/ private permission-denied → B-grade synthesized：A=slicer_tb_A.sp+slicer_netlist_A(8 实例 XPP0/XNN0/XTAIL0/XIP0)+sa_5corner_A.sp(5 corner:TT_1V_27/FF_0.9V_-40/SS_1.1V_125/TT_1V_-40/TT_1V_85)+baseline_A.mt0(idx0 cur=376.20 cur_limit=400)+prompt.txt+task_brief.md；隐藏 B=TT_1V_27@idx3 cur=395.50 实例 XPP0/XNN3/XTAIL2/XIP0 cur_limit=420 7-corner(每维度反硬编码：idx/corner 数/cur/cur_limit/实例下标全不同)。候选写通用 sa_sizing_plan.py(--tb/--netlist/--corner-sp/--baseline/--out CLI) 解析 testbench+网表+corner sweep+baseline→mapping.json(8 param)+corner_map.json(N row)+baseline_metrics.json(cur/cur_limit/idx)+sweep_plan.json(8 行 N param 扫描)+submit.sh(bsub FineSim)。14 条 a-n：含 b py_compile+c subprocess 跑通 B+d 5 输出文件全生成+e mapping 8 param+f corner_map 7 row(B 反硬编码)+g baseline cur==395.50+h cur_limit==420+i sweep_plan 8 行+j sweep col 含 corner/limit/cur+k submit bsub FineSim+l idx==3 反硬编码+m sweep instance==XPP0/XNN3/XTAIL2/XIP0+n 反硬编码跨输入(A cur==376.20 idx==0 实例 XPP0/XNN0/XTAIL0/XIP0)+3-seed 确定性。自验 ref PASS 14/14+§4.9 三假(empty→c/print_only→c/core_deleted→g)全 FAIL distinct+4 neg(neg_hardcode_a→n/neg_hardcode_b→n/neg_drop_corner→f/neg_print_only→c/neg_empty→c)全 FAIL+negative_selftest ALL_NEG_FAIL=True NEG_RC=0+3-seed 一致。byte-sync sha 58141498104f083d size 17006。D.jsonl 236→237。深读 szdav_sa_slicer_sizing.md。选料：本地 summary_1105.tsv(5822 行)+ledger_D(1358→规范化 1294 unique bare sids，strip .messages.archive.json/.messages.json/.json 后缀)正则排重→424 fresh unique D 候选（inline awk 1358-element 排除正则在 .75 awk 解析器超长 syntax error→改本地 Python 规范化排重绕过），D-domain 评分(netlist/hspice/schematic 加权，drc/layout 减权)→peek top 候选 abico(e0030760 mc=114)=2 user turn 全 continuation 不适→cjcn7(ming1w mc=164)=debug 非 produce-task→ezcgh(mike mc=120)=analysis-heavy→kbs81(e02141 mc=96)=SWB/Sentaurus TCAD 非 D→oue4a(eva1wu mc=49)=什么是cm 非 produce-task→7at4j(lvyy)=debug 仿真非生成→vdeyi(e0025768)=workflow 报错 debug→3kgd5(rongjiez)=C++ mainwindow 非 EDA→ikvky(clarawu)=gvim 字体 admin→a6f6r(jinsongl)=CCK TCL borderline→szdav(jiangbaol netlist:211 hspice:128 schematic:104 mc=56 StrongARM slicer 8-param 尺寸优化 produce-task D✓ 真实 FineSim/bsub harness)采 · ledger_D 1358→1359 case=234。
- #424 流水：交付 InstArcDiagFix-001（analog_context B-档 synthesized L2 k=15）— 真实 trace scut3(ronghu@hfeg0pkn005 mc=190) SiliconSmart 表征 inst 文件测量失败诊断+修正：用户对 DRAM 单元 DbusRcvnew_DbusMg 做功耗感知表征，HSPICE deck.mt0 显示 arc delay__latr__lh__dbusl__hl__acq_1 的 tout__dbusl__hl_trig/targ 全 failed（DbusL 从未 1→0 跳变，arc 在 acquire 模式下逻辑上不可造），deck.lis job concluded 无语法错误。用户先「分析原因以及如何修改」再「inst 文件应该改成什么样」。agent 追踪网表拓扑定位根因（DbusL=IQN|(RCPfrc&RCP)，acquire 模式输出由捕获值驱动），产出修正 inst。会话 7 msgs。资产 uploads 4 文件(inst+cdl.spf+deck.cir+deck.lis+deck.mt0)全部 NFS 可读 → B-grade synthesized：A=真实 inst(加显式 latR lh→DbusL state_partitions one 失败 arc 行)+真实网表+真实 deck_A.mt0(trimmed 45 行)+真实 deck_A.lis；隐藏 B=合成单元 WlRdBufNew_WlMg(cell/pin/signal/instance 名全不同:WlQ/WlD/latW/latWN/latWS/RdEn/RdFrc;上拉 MMP22/MMP30 下拉 MMN24/MMN26 三态 XI_invenPF_3;supplies vpb/vcc/vccx;forbidden_state 用 RdEn;deck_B.mt0 title delay__latw__lh__wlq__hl__acq_1 tout__wlq__hl failed)每维度反硬编码。候选写通用 inst_arc_diag_fix.py(--inst/--netlist/--mt0/--out CLI) 解析 inst+网表+mt0→diagnosis.json(cell/output/function/latch/switching_set/forbidden_state/failed_arcs/root_cause/pullup_insts/pulldown_insts)+inst_fixed.txt(抑制不可造 arc 的 state_partitions)。15 条 a-o：含 b py_compile+c subprocess B+d cell==WlRdBufNew_WlMg+e output==WlQ+f function==IQN|(RdFrc&RdEn)+g failed_arc latw/wlq/lh/hl+h root_cause==arc_uncreatable_in_state+i pullup=={MMP22,MMP30}+j pulldown=={MMN24,MMN26}+k 失败 arc state_partitions 抑制+l 必要段落保留+m forbidden_state 保留+n 反硬编码跨输入(A cell==DbusRcvnew_DbusMg pullup=={MMP10,MMP12} failed_arc.from==latr)+o 3-seed 确定性。自验 ref PASS 15/15(A/B 双端)+§4.9 三假(empty→c/print_only→c/core_deleted→i)全 FAIL distinct+2 neg(hardcode_a→d/hardcode_b→n 跨输入)全 FAIL+negative_selftest ALL_NEG_FAIL=True NEG_RC=0+3-seed 一致。byte-sync sha 418272265a88642f806a6a7b92024b4c056e0805ac8f49dfd3679d34e16abd35 size 8436。D.jsonl 235→236。深读 scut3_instarcdiagfix.md。选料：复用 #423 cron 日志 fresh 池(scan3_out.tsv 25 truly_fresh)，cross-ref 现 ledger_D(1274 sids)→22 truly fresh，peek 7 候选(hnzff/brrc3/qty8f/knbkz/q5znu/38tea/i4kkz)全不适(continuation-dependent/分析非 produce/非 D domain/与 #423 重复/borderline)→scut3(D-domain SiliconSmart inst 表征失败诊断+修正 2 自然 user turn 全 produce-task 真实附件可读)选料。
- #423 流水：交付 XProbeHierGen-001（schematic_netlist B-grade synthesized L1 k=15, byte-sync sha 3737ccd9 size 8169, D.jsonl 234→235）— 全文已搬 MEMORY_D_archive.md「归档批次 2090」
- #420 流水：交付 EccTopCircuitCompare-001（schematic_netlist B-grade synthesized L2 k=12, byte-sync sha d54ad937 size 10274, D.jsonl 231→232）— 全文已搬 MEMORY_D_archive.md「归档批次 2090」
- 流水 #413b (数据质量修复轮 0 新 case · 并行 agent 已交付 2StepOCChainAnalyze-001 · 本 agent 检测重复并修复 D.jsonl 7 malformed task_id) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- 流水 #411 (交付 EDA-Eval-DesignFlow-SimlibLogicCheck-001, schematic_netlist B-grade synthesized L1, 15 条件 a-o, byte-sync sha 5e7590e6 size 10068, cliu rl62o hfeg0pkn004 mc=216) — 全文见 git 历史(被 #413b 替换压缩)
- (归档批次 2085) 流水 #410 (SimAccelCellReco-001, analog_context B k=16, qhzmr e03179@hfeg0pkn002 mc=29, byte-sync sha 38eccf62 size 9956) 全文已搬 MEMORY_D_archive.md
- 流水 #409 (选料复核轮 0 case · hfeg0pkn005 fresh A-grade D seed 枯竭 · DEBT 真外部阻塞) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- (归档批次 2085) 流水 #408 (TrimMuxInvDiff-001, schematic_netlist B k=16, dsgao x8v81@hfeg0pkn001 mc=0, byte-sync sha 41d51c79 size 11178) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #407 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #405 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2083) 流水 #404 (选料复核轮 0 case · DEBT:1 三路径全枯竭需运维; 孤儿 5 全 A/B/C / parked+deepread 仅 t0aom=shard B / 11-08 fresh ssh 12 host 0 fresh D seed) 全文已搬 MEMORY_D_archive.md
- (归档批次 2083) 流水 #403 (交付 EDA-Eval-DesignFlow-OpenWaveFmt-001, waveform A-grade faithful L1, 16 条件 a-p, byte-sync sha c1ef37d5, rongjiez 7fcir hfeg0plg98 mc=16; 孤儿采纳破局) 全文已搬 MEMORY_D_archive.md
- (归档批次 2084) 流水 #402 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #401 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- (归档批次 2084) 流水 #399 (已搬 MEMORY_D_archive.md「归档批次 2084」)
- 流水 #395 (已归档批次 2082 — RsCalcRnodePlace-001 analog_context B k=12)
- (归档批次 2080) 流水 #393 (质量审计 QaLibCellBuild-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- 流水 #394 (已归档批次 2082 — FullAdderSchemBuild-001 质量审计 全过)
- (归档批次 2081) 流水 #392 (AnalogCmpSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha b8aef498 size 10377, xxchen 0d17g mc=393) 全文已搬 MEMORY_D_archive.md
- (归档批次 2078) 流水 #390 (FullAdderSchemBuild-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha f7f035da size 10973, sinanz 1793862562240_2m2ja mc=197) 全文已搬 MEMORY_D_archive.md
- (归档批次 2077) 流水 #389 (VerilogDriveFsmBlock-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha e4743f03, mike fl4rh) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #387 (AutoCellDrcFlowGen-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 70390949, miccao rhti4) 全文已搬 MEMORY_D_archive.md
- (归档批次 2074) 流水 #386 (RsDistReport-001, analog_context B-grade synthesized L1, 14 条件 a-n, byte-sync sha 248ee63c, e0014566 r9m9l) 全文已搬 MEMORY_D_archive.md
- (归档批次 2073) 流水 #385 (NetlistSigTrace-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 17d00745, e0030085 vb3m8) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #384 (ModelQaTbGen-001, schematic_netlist B-grade synthesized L2, 12 条件 a-l, byte-sync sha 972189af) 全文已搬 MEMORY_D_archive.md
- (归档批次 2072) 流水 #383 (FsdbMeasRunGen-001, waveform B-grade synthesized L1, 16 条件 a-p, byte-sync sha dcd48dde) 全文已搬 MEMORY_D_archive.md
- (归档批次 2076) 流水 #388 (质量审计 ModelQaTbGen-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2075) 流水 #379/#380/#381/#382 (质量抽查轮, option d, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2071) 流水 #378 (质量抽查 #374 CtleTranPower-001, analog_context, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- (归档批次 2069) 流水 #374 (CtleTranPower-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2070) 流水 #375 (PortTextPinPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2067) 流水 #372 (DevListSummary-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2065) 流水 #370 (CstViewPrecheck-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2066) 流水 #371 (SelFigReport-001, analog_context, B-grade synthesized L1, 16 条件 a-p) 全文已搬 MEMORY_D_archive.md
- (归档批次 2063) 流水 #368 (WaveCmpWrap-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2064) 流水 #369 (LvsRptAnalyze-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2062) 流水 #367 (WvDispCfg-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2061) 流水 #366 (WrCornerCmp-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #365 (CosWaveWdf-001, waveform, A-grade faithful L2 真跑 WaveView ACE, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2060) 流水 #364 (DelayChainCmp-001, schematic_netlist, B-grade synthesized L1, 14 条件 a-n) 已搬 MEMORY_D_archive.md
- (归档批次 2058) 流水 #363 (NetlistSubstPlan-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2057) 流水 #362 (IOBufTune-001, analog_context, B-grade L2 真跑 HSPICE, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2056) 流水 #360 (AutocellPlaceGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2054) 流水 #358 (SaTransistorExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2052) 流水 #357 (TestModeExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（tx5s5/e04201/mc46；Verilog 网表 test-mode 标识符扫描+分类计数+模块定义抽取；跨 shard 共享第六例）
- (归档批次 2051) 流水 #356 (SpiceClosureExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（aw9d7/dsgao/mc273；SPICE 子电路依赖闭包抽取器；同 shard 同 trace 不同意图复用第五例）
- (归档批次 2050) 流水 #355 (SchHierCopyPlan-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（8orer/lvyy/mc165；schematic hierarchy copy 闭包+拓扑序+循环检测；跨 shard 共享第四例，mc>=15 fresh-vs-all D-domain 池枯竭）
- (归档批次 2049) 流水 #354 (CdlNetlistGen-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md（genvz/adaml/mc183；emy2netlist CDL 抽取单轮 produce；选料发现 mc>=30 D-domain fresh 池枯竭）
- 流水 #353 (LvsMrcBrknetDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 见上方 PHASE 行（沿用 #353 peek 已 claim 的 wdnwl；A-faithful 不可行因 /rundata cuij 私有不可读）
- 流水 #352 (LvlShftCatalog-001, analog_context, B-grade L1, 16 条件 a-p) 已归档摘要见上方 PHASE 行末（fresh 池 peek 16 候选仅 1 clean D-domain produce；park 13 weak）
- (归档批次 2048) 流水 #351 (XfightingDiag-001, waveform, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #350 (PexFailDiag-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2048) 流水 #349 (FFLatchExtract-001, schematic_netlist, B-grade L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2047) 流水 #345/#346/#347/#348 已搬 MEMORY_D_archive.md（4 条大流水，#349 PHASE+流水已含摘要）
- (归档批次 2046) 流水 #344/#343/#342/#341 已搬 MEMORY_D_archive.md
- (归档批次 2045) 流水 2026-11-07 06:2x #340 NetlistBisectLocalize-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2043) 流水 2026-11-07 #335/#336/#337 已搬 MEMORY_D_archive.md（#335 FineSimDataParse-001 / #336 LdoCircuitReport-001 / #337 选料轮 DEBT:1）
- (归档批次 2044) 流水 2026-11-07 #338 MbistCellFind-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2039) 流水 2026-11-07 03:2x-04:0x #334 选料/peek 轮 已搬 MEMORY_D_archive.md
- (归档批次 2036) 流水 #333 (WvSigListGen-001, waveform, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #332 (MillerOpampTopoAudit-001, schematic_netlist, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2035) 流水 #331 (DlyChainTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #330 (CpumpDeckGen-001, analog_context, B-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #329 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2034) 流水 #328 (LdoTbGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #327 (ShortCfgTrace-001) 已搬 MEMORY_D_archive.md
- (归档批次 2032) 流水 #326 (SpfTriggerMonitor-001) 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #318 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #319 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #320 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #321 已搬 MEMORY_D_archive.md
- (归档批次 2030) 流水 #322 已搬 MEMORY_D_archive.md
- (归档批次 2033) 流水 #323 (OtaSimReport-001) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #317 (选料/peek 轮, DEBT:1) 已搬 MEMORY_D_archive.md
- (归档批次 2037) 流水 #316 (ToggleCounterBindGen-001, schematic_netlist, A-grade, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2029) 流水 #315 (FmInstFreq-001) 已搬 MEMORY_D_archive.md
- (归档批次 2028) 流水 #314 (DlygResInsert-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #313 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #312-prep 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #311 已搬 MEMORY_D_archive.md
- (归档批次 90) 流水 #309 (NetlistGate2Verilog-001) 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 13:5x | shard D #310 | 交付 NetlistCellReplace-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 89) 流水 #308 (CellRewriteSimlib-001) 已搬 MEMORY_D_archive.md
- (归档批次 85) 流水 #303 (WaveMaxFind-001, waveform, 15 条件 a-o) 已搬 MEMORY_D_archive.md
- (归档批次 88) 流水 #302 已搬 MEMORY_D_archive.md
- (归档批次 91) 流水 2026-11-06 08:0x | shard D #301 | 交付 NetlistMMultAudit-001（16 条件 a-p）已搬 MEMORY_D_archive.md
- (归档批次 83) 流水 #300 (选料/peek 轮) 已搬 MEMORY_D_archive.md
- (归档批次 84) 流水 #299 (SineZeroCrossFreqPeak-001) 已搬 MEMORY_D_archive.md
- (归档批次 75) 流水 #291 (LatDffRsHierExtract-001) 已搬 MEMORY_D_archive.md
- (归档批次 76) 流水 #292 (WvFsdbReaderV2Gen-001) 已搬 MEMORY_D_archive.md
- (归档批次 77) 流水 #293 (SchFixFloating-001) 已搬 MEMORY_D_archive.md
- (归档批次 78) 流水 #294 (CellExpandGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 74) 流水 #290 (PorCapSweepGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 72) 流水 #289 (WvAcReportGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 73) 流水 #288 (ChPulseRespGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 70) 流水 #287 (CtleTranGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 69) 流水 #286 (Wr2dqEdgeMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 68) 流水 #285 (Wr4thCkMeas-001) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #285 已搬 MEMORY_D_archive.md
- (归档批次 67) 流水 #284 (SiInpTokenStrip-001) 已搬 MEMORY_D_archive.md
- (归档批次 66) 流水 #283 (PsdDqMap-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #282 (MeasTrtfSkewGen-001) 已搬 MEMORY_D_archive.md
- (归档批次 65) 流水 #280 (VrefcsMrrSeq-001) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #279 (碰撞让步轮 MosParamStat-001, 无交付) 已搬 MEMORY_D_archive.md
- (归档批次 64) 流水 #278 (CircWfReport-001, analog_context, 16 条件 a-p) 已搬 MEMORY_D_archive.md
- (归档批次 2027) 流水 #277 已搬 MEMORY_D_archive.md
- (归档批次 63) 流水 #276 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #275 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #273 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档批次 63) 流水 #272 已搬 MEMORY_D_archive.md（含选料/peek/深读/合成/自验/教训全文）
- (归档) 流水 #268 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #267 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #266 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #265 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #264 已搬 MEMORY_D_archive.md（归档批次 59）
- (归档) 流水 #263 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #262 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #261 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #260 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #259 (MosSizeDoeGen-001) 已搬 MEMORY_D_archive.md（归档批次 56）
- (归档) 流水 #258 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #257 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #256 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #255 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #254 已搬 MEMORY_D_archive.md（归档批次 57）
- (归档) 流水 #253 (SweepCfgParse-001) 已搬 MEMORY_D_archive.md（归档批次 58）
- (归档) 流水 #252 (aq0vc/SpStimGen-001) + #251 (xkg53/FinesimAutoRun-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #250 (eypbp/PwlConvert-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #249 (s96je/HierSpiceMosCount-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #248 (7fcir/OpenWaveFmt-001) 已搬 MEMORY_D_archive.md（归档批次 55）
- (归档) 流水 #240-#247（含 #247 3jb3i/Tcs0PatAnalyze-001 全文）已搬 MEMORY_D_archive.md（归档批次 53/54/55）
- (归档) 流水 #240-#246 已搬 MEMORY_D_archive.md（归档批次 53）
- (归档) 流水 #241 已搬 MEMORY_D_archive.md（归档批次 52）
- (归档) 流水 239 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 238 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 237 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 235 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 234 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 233 已搬 MEMORY_D_archive.md（归档批次 51）
- (归档) 流水 #232 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #231 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #230 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #229 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #228 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #227 已搬 MEMORY_D_archive.md（归档批次 50）
- (归档) 流水 #225 已搬 MEMORY_D_archive.md（归档批次 50）










- (归档) 流水 #193–#204 已原文搬 MEMORY_D_archive.md（归档批次 2026-11-03 #205）；更早 #164–#192 亦见 prior commits / ARCHIVE_OPERATOR_DESIGNFLOW.md
- (归档批次 2052) 2026-11-07 #351 XfightingDiag-001 daily 流水全文已搬 MEMORY_D_archive.md（3lvd6/jackliu/waveform mc88，B-grade L1 16 条件 a-p）

### 流水 #391（2026-11-08 shard D）
- 交付：QaLibCellBuild-001（schematic_netlist B-grade synthesized L1，spec-driven pyAether 多 cell 库+techfile 构建 + mock 录制 stub 离线 subprocess 判分，16 条件 a-p）。
- 源 trace：8th6a（kenwang @ hfeg0pkn004，mc=407，Virtuoso IC617 SKILL DRC QA pattern 库/cell 构建，387 msgs/13 user turns）。
- 自验：ref reference_submit.zip check() PASS 16/16（B spec）；§4.9 三假 empty→[a] / print_expected→[p] / core_deleted→[p] 全 FAIL distinct；negative_selftest 5/5 FAIL distinct first_fail {a,d,f,p}；断言闸门 k_rationale=k_check=16(a–p)≥8 ✓，test_rationale 以 `16 条断言：①…` 开头 ✓；jsonl test 字段与磁盘 check.py byte-sync（11522B，sha 918a94153a3d2f38e5de05ca8210306cb909231b31c115d30fbf7ea54bf50fe8 两端一致）✓；B 反硬编码（A=QA_Lib_A Buf3x/NandTie，B=QA_Lib_B Buf2x/AndOr1，库/cell/门集全不同）+ 3-seed 一致性 PASS。
- 选料：trace_ledger.py --shard D next 取候选；.75 awk 长 exclusion regex 超 ARG_MAX（1298 entries）→ 改本地读 trace_ledger_D.tsv 排除 + .75 awk 仅做 mc/domain 过滤；fresh mc>=30 D-domain 候选多为 layout/powerfill/rscalc（shard C）或 PDK QA handoff/debug/resume，clean schematic_netlist/waveform produce 稀缺 → 沿用 #390 mock-stub 离线判分模式。
- 🎯 通过率: 最近20条（B 档 synthesized L1，未跑 pi/cline）n/a（本轮仅造题+自验，未实跑被测）。
- 📊 trace 覆盖率：212 / 1511 = 14.0%（mc>=30；D.tsv 212 case-mark + 1043 parked = 1255 已动过）。
- 🧾 断言: k_rationale=k_check=16 ✓（今日 1/1 达标，存量 30 条断言清单债见 rewrite_queue.tsv）。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈33KB。
- DEBT: 0；⚠️ L1/L2 比例债 35→36 轮；waveform(45) 仍最低覆盖域。
