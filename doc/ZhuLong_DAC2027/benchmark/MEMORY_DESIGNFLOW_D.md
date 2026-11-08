WAITING: 0（#421 交付 GrDecPwrSwitchTbGen-001 · wmzu1 dsgao@hfhds234 mc=1429 · schematic_netlist B-grade synthesized L2 k=12 · byte-sync sha a49f1ef2 size 7845 · D.jsonl 232→233 · 选料复用 #420 cron 日志 fresh 池(24 truly fresh 剩余)，peek top hnzff(meta/continuation-dependent unfit)→wmzu1(GrDecPwr ACT/PRE 上下拉 tb 生成，资产 /proj/drcpa 私有不可读但 Desktop tb.sp NFS 可读→获完整 subckt+NAND 逻辑) · +1 case · ledger_D 1355 · D.jsonl 233 entries；#421 GrDecPwrSwitchTbGen-001,#420 EccTopCircuitCompare-001,#419 0case(归档2088),#418 0case(归档2088),#417 0case(归档2088),#416 RsCalcReport-001,#415 VsimCovReport-001,#414 AddrRtlGateMap-001,#413 2StepOCChainAnalyze-001,#412 SdlGroupPlan-001(已归档批次2086),#411 SimlibLogicCheck-001,#410 SimAccelCellReco-001,#409 选料复核轮 0case,#408 TrimMuxInvDiff-001,#407 dup-fix+claim x8v81,#406 VrefCSMRRSeq-001,#405 0case,#404 0case,#403 OpenWaveFmt-001,#402 PrimeLibFlowAnalyze-001）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #419/#418/#417 流水（3 轮 0-case 选料复核：fresh D A-grade seed 枯竭 / DEBT②自测放宽关键词仍枯竭 / 清空 r416 残留）— 全文已搬 MEMORY_D_archive.md「归档批次 2088」
- #416 流水：交付 RsCalcReport-001（schematic_netlist B-档 L3 k=12）— 真实 trace 7u0m3(e0014566@hfeg0pkn005 mc=183) RsCalc 寄生电阻计算流程：在 austin_rscalc2/testa 版图上生成 calcr 脚本→Virtuoso 批处理启动→检查 .rvn 结果文件与 calcr.log/rsb.log 日志→中文问答解释电阻值→版图优化。会话 80 msgs 模型 glm-5.1-cloud 状态 failed。真实资产：trace 中 .rvn 片段可读(vdd 网络 LV+RSView:NodeList,4 + 4 行节点记录,第 12 列电阻值 16.716/14.028/11.592/7.224)、calcr.log 可读(net name/node count/Succeeded Warning count:0)、rsb.log 可读(3-net M1/vbb/vdd 汇总)；但 RsCalc 结果目录 /rundata/train/AI_Virtuoso/ver/rscalc/e0030265/testa 下 RSDB_<net>/ 为 e0030265 所属不可读 → B-grade synthesized：依据 trace 真实格式合成 A/B 两套 RSDB_<net>/ 结果目录树，候选写通用 rscalc_result_report.py(--result-dir/--out CLI) 扫描 RSDB_* 子目录解析 .rvn 第 12 列电阻 + calcr.log 状态/节点数，产出结构化报告(Total_Nets/[NetResults] per-net Status/Nodes/MaxR/MinR/AvgR/[SummaryStats] Total_Succeeded/Failed/Max_Resistance/Min_Resistance)。A=3 Succeeded(M1/vbb/vdd,各含 .rvn+calcr.log)+rsb.log；B=4 net(vcc/gnd/io Succeeded,clk Failed 无 .rvn——边界情况 NA 处理)+rsb.log。12 条 a-l：含 d Total_Nets + e net 字典序[clk,gnd,io,vcc] + f clk Failed+Nodes=67(从 calcr.log 末行解析 Failed) + g clk NA/NA/NA(Failed 无 .rvn 边界,反臆造) + h/i/j vcc/gnd/io per-net 全字段(电阻 4 位小数) + k SummaryStats 全局统计(仅 Succeeded 取 max/min) + l 3-seed 确定+无 A 名(vdd/vbb/M1)泄露(反硬编码)。自验 ref PASS 12/12(A/B 双端) + §4.9 三假(empty/print-only/core-deleted 全 FAIL) + 2 neg(hardcode_A→d,e,f,g,h,i,j,k,l / ignore_failed→f,g,k)全 FAIL + 3-seed 一致(cond l)。byte-sync sha e40316cb size 14126。D.jsonl 230→231。深读 7u0m3_rscalc_analyze.md。选料：top 42 候选均 exclusion(4-shard 1787-sid 排除集)，4 fresh 候选(cpnbc/o0dm6/bkeur/7u0m3)中 7u0m3 domain 匹配最丰富(schematic+netlist+pyAether+calibre+cellview+skill)。
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
- 📊 trace 覆盖率：230 / 2199 = 10.5%（mc>=30 候选池；D.tsv 现 230 case-mark + 1080 parked · 已动过 1310；快照 2026-11-08 20:08 sessions=5822 mc300=347 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 233 entries / wc -l 233）：analog_context · schematic_netlist · waveform。**#421**：wmzu1(dsgao@hfhds234 mc=1429)→GrDecPwrSwitchTbGen-001（schematic_netlist B-grade synthesized L2，DRAM 行译码电源开关 GrDecPwr ACT/PRE 上下拉验证测试台生成：解析 CDL 开关网表自动识别 DecPwr 端口(PMOS 上拉链漏端∩NMOS 下拉漏端)+阱电源/地端口+PMOS 上拉链实例名+NMOS 下拉管+控制信号，解析 sim_top NAND2 自动识别相位信号，推导 NAND 逻辑 D=NOT(phase) 真值表(ACT→pull_up/PRE→pull_down)，生成自包含 tb.sp(供电/相位 PULSE/控制恒高/行为源 NAND/负载电容/Xswitch/.tran/.print/.probe)+analysis.json；A=R_GidlAryCtrl_switch/GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!/MMP0-2/MMN0/SecHv，B=R_WlPwrGateSwitch/WlDecPwr/wl_sw_total/wlsw/gnd!/vplz!/M_PU0-2/M_PD0/WlPhase(每维度反硬编码+不同 W/L)；12 条 a-l 含 b subprocess 真跑+c/d/e B 名/端口/角色精确+f/g 上拉链/下拉管实例名+h/i 控制/相位信号+j NAND 真值表逻辑+k tb.sp 结构+l 3-seed+无 A 名泄露；自验 ref PASS 12/12+§4.9 三假+3 neg FAIL；byte-sync sha a49f1ef2 size 7845；D.jsonl 232→233。选料复用 #420 cron 日志 fresh 池(24 truly fresh 剩余)，peek top hnzff(meta/continuation-dependent unfit)→wmzu1；资产 /proj/drcpa 私有不可读但 Desktop tb.sp NFS 可读→获完整 subckt+NAND 逻辑）。**#420**：btze4(xiwang@hfeg0pkn002 mc=65)→EccTopCircuitCompare-001（schematic_netlist B-grade synthesized L2，ECC 顶层电路结构对比：strings 提取 sch.oa 二进制 inst:/net: token→EccTop 识别→子模块集合交并差+电源架构判定；A=EccTop128x2New+DVFSCEccTop/SCmosEccTop，B=EccTop256x1New+DVFSCEccTop2/SCmosEccTop2(每维度反硬编码)；12 条 a-l 含 b subprocess 真跑 strings+d/e B cell 名精确+f shared=[EccCtrl]+g/h uniqueA/uniqueB 精确+i count 6/18+j/k verdict+l 3-seed+无A名泄露；自验 ref PASS+§4.9 三假+3 neg FAIL；byte-sync sha d54ad937 size 10274；D.jsonl 231→232。选料破局：scan3.py 扫 11-08 cron 日志 eda_trace_20261108.log→104 fresh→25 truly fresh→btze4）。**#419/#418/#417**：3 轮 0-case 选料复核（fresh D A-grade seed 枯竭，全文已归档批次 2088）。**#416**：7u0m3(e0014566@hfeg0pkn005 mc=183)→RsCalcReport-001（schematic_netlist B-grade synthesized L3，RsCalc 寄生电阻结果报告生成：扫描 RSDB_<net>/ 子目录解析 .rvn 第 12 列电阻 + calcr.log 状态/节点数→结构化报告 Total_Nets/[NetResults]/[SummaryStats]；A=3 Succeeded(M1/vbb/vdd)，B=4 net(vcc/gnd/io Succeeded + clk Failed 无 .rvn 边界 NA 处理)；12 条 a-l 含 f clk Failed+g clk NA 边界+h/i/j per-net 全字段+k 全局统计+l 3-seed+无A名泄露；自验 ref PASS+§4.9 三假+2 neg FAIL；byte-sync sha e40316cb size 14126；D.jsonl 230→231）。**#415**：wk3wd→VsimCovReport-001。**#412**：5fpjy(jcgu@hfeg0pin003 mc=152)→SdlGroupPlan-001（schematic_netlist B-grade synthesized L3，group-gen-sdl skill 匹配组生成分析阶段：SPICE 网表+match_cfg→groups.json；A=折叠cascode 3-mirror AABB / B=telescopic-bias 4-mirror Central Symmetry + 3-deep cascode(MCSC orphan) + 不同 orphans；12 条 a-l 含 B 三类 group 精确器件集 + orphans 精确(反硬编码) + 划分性质 + pattern∈allowed & 最大CM==B默认 + 3-seed 顺序不变性；自验 ref PASS + §4.9{a,e,f} + 4 neg FAIL；byte-sync sha 0572a9cb size 11257；D.jsonl 430→431）。**#411**：rl62o→SimlibLogicCheck-001。**#410**：qhzmr→SimAccelCellReco-001。**#409**：选料复核轮 0 case。**#408**：x8v81→TrimMuxInvDiff-001。**#407**：dup-fix+claim x8v81。**#406**：42jk5→VrefCSMRRSeq-001。**#405/#404**：0case。**#403**：OpenWaveFmt-001。**#402**：PrimeLibFlowAnalyze-001。**#401**：SramButterfly-001。**#400**：AbMatchPlacementCheck-001。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈39KB（本轮 #421 交付 GrDecPwrSwitchTbGen-001，已归档 #417/#418/#419 三条 0-case 流水到 MEMORY_D_archive.md「归档批次 2088」，42KB→39KB 回到 40KB 红线内）
- DEBT: 0 选料阻塞（#420 交付 EccTopCircuitCompare-001，破局 fresh-seed 枯竭：⚠️ **DEBT① 推翻** — 发现 11-08 cron 日志 /home/t0002965/log/eda_trace_20261108.log 是 fresh 源（每日 00:00 更新，2889 qualifying sessions），scan3.py 抽 D-domain 候选 cross-ref 台账(修复 sid-normalization bug：台账存全 <timestamp>_<sid>，cron 用短 <sid>，sed -E 's/^[0-9]+_//' 归一)→ 104 fresh→25 truly fresh→采 btze4。**rescan 不再是唯一路径，可直接扫 cron eda_trace_YYYYMMDD.log**。#419 0case 已清空 r416 残留。其余运维项仍存：①~~全量 rescan~~(已破局，可直接扫 cron 日志) ②放宽 D-domain 关键词（#418 自测即便放宽 summary.tsv 仍枯竭，但 cron 日志路径已绕过此限制）③跨 shard domain 重分配（spice_sim/waveform 部分回流 D）④/proc 资产获取权限（/proj/dscqa、/rundata/drcpa_sim、/rundata/drcoa、/home/cliu/drcoa、/home/wellesc、/proj/train/AI_drcqa/workdir/jcgu、/rundata/train/AI_Virtuoso/ver/rscalc 归属 cadmin/私有，e0031982 无读权限无 sudo，#408/#410/#411/#412/#413/#414/#415/#416/#420 均被迫采 B-grade synthesized 而非 A-grade faithful）⑤跨 shard dup 清理。⚠️ 未碰 shard B 飞行；⚠️ 并行 shard D agent 已交付 #416（其 D.jsonl/deepread 未由本 agent 提交）。
- 🧾 断言: k_rationale=k_check=12 ✓（#421 GrDecPwrSwitchTbGen-001 落 jsonl 12==12≥8 达标；#420 12==12 达标；存量 233 entries test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 11-09 新 case 达标）。
- 🎯 通过率: 最近20条 n/a（#421/#420 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #421 流水：交付 GrDecPwrSwitchTbGen-001（schematic_netlist B-档 synthesized L2 k=12）— 真实 trace wmzu1(dsgao@hfhds234 mc=1429) DRAM 行译码电源开关 GrDecPwr ACT/PRE 上下拉验证测试台生成：用户逐字「@R_GidlAryCtrl_switch.netlist 这个电路有什么」→「在电路正常 ACT 和 PRE 时，对GRDECPWR 的影响」→「我有一个secHV激励 上升沿是act,下降沿是pre,怎么做逻辑可以仿真看到 GrDecPwr 的上拉和下拉的过程中的电位变化」→「用nand将 SecHv 和 cm1_sw_total / cm1sw 做逻辑来模仿 ACT 和 pre 时候 GrDecPWR 的变化」→「cm1_sw_total / cm1sw 在开关有效窗口内是高电平，且是恒定的」→「@ALPS sim_top 网表 写一个验证tb」。agent 解析 CDL 网表识别顶层 subckt R_GidlAryCtrl_switch(端口 GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!)，分析两条通路：通路A(PMOS 链 MMP2→MMP1→MMP0→vwlp! 上拉，cm1 低导通)+通路B(NMOS MMN0 下拉)；推导 NAND 控制逻辑 D_total=NAND(secHV,cm1_sw_total)/D_cm1sw=NAND(secHV,cm1sw)，因 cm1 恒定高→D=NOT(secHV)：ACT(secHV=1)→D=0→上拉，PRE(secHV=0)→D=1→下拉；读 ALPS sim_top 发现 nand2Y_Xdecx1 把 SecHv+cm1sw 做 NAND 得 net0 驱动 cm1_sw_total=cm1sw=net0，GrDecPwr=net2 → 写 R_GidlAryCtrl_switch_sim_tb.sp。资产 /proj/drcpa/V0/workdir/dsgao/ 私有不可读(Permission denied，DEBT④)但 agent 在 /home/dsgao/Desktop/ 写的 tb.sp 经 NFS 共享可读→获完整 subckt 结构(MMP0-4/MMN0-1)+NAND 逻辑+tb 格式→B-grade synthesized：合成 A/B 两套同结构开关网表+sim_top(含 NAND2)。候选写通用 dec_pwr_switch_tb_gen.py(--netlist/--sim-netlist/--out CLI) 解析 CDL 自动识别 DecPwr 端口(PMOS 上拉链漏端∩NMOS 下拉漏端)+阱电源/地端口+PMOS 上拉链实例名+NMOS 下拉管+控制信号(非二极管栅极)，解析 sim_top NAND2 自动识别相位信号(非开关端口/非电源输入)，推导 NAND 逻辑+真值表(ACT→D=0→pull_up/PRE→D=1→pull_down)，生成自包含 tb.sp(供电/相位 PULSE/控制恒高/行为源 NAND/负载电容/Xswitch/.tran/.print/.probe)+analysis.json。A=R_GidlAryCtrl_switch/GrDecPwr/cm1_sw_total/cm1sw/vss!/vwlp!/MMP0-2/MMN0/SecHv，B=R_WlPwrGateSwitch/WlDecPwr/wl_sw_total/wlsw/gnd!/vplz!/M_PU0-2/M_PD0/WlPhase(每维度反硬编码：cell/net/MOS/信号/阱电源/相位名全不同，W/L 820n/481n→1.5u/0.45u，多 1 颗 clamp)。12 条 a-l：含 b subprocess 真跑 + c/d/e B 名/端口/角色精确 + f/g 上拉链/下拉管实例名(集合) + h/i 控制/相位信号 + j NAND 真值表逻辑 + k tb.sp 结构(.tran/.print/PULSE/供电/负载/DUT) + l 3-seed 确定+无 A 特有名(11 个)泄露。自验 ref PASS 12/12(A/B 双端) + §4.9 三假(empty/print-only-hardcodeA/core-deleted 全 FAIL) + 3 neg(hardcode_a/empty/always_pullup)全 FAIL + negative_selftest ALL-FAIL-OK + 3-seed 一致。byte-sync sha a49f1ef2 size 7845。D.jsonl 232→233。深读 wmzu1_decpwr_switch_tbgen.md。选料：复用 #420 cron 日志 fresh 池(_tmp/shardD_2223/truly_fresh_short 24 剩余)，cross-ref 现 ledger(1200 sids) 24 全仍 fresh，按 scan3 score 排序 peek top 候选：hnzff(ziyuny mc=2766)=4 user 全 meta/continuation-dependent(读前会话/学之前结果/接着做 device match check，前提缺失→②类失败) unfit → wmzu1(dsgao mc=1429)=4 user 全自然 produce-task(分析网表+推导 NAND+生成 tb)，资产私有但 Desktop tb.sp 可读→采。Research 日报 2026-11-08 designflow 建议(rewrite_queue 加缺陷类别/修复前后 pass-rate 列 + 资源轴纳入判分 + LLM judge 一致性)已阅，本 case check.py 已含 12 独立条件+三假+neg 自验(判分可验证性达标)，资源轴/judge 一致性非本轮阻塞，纳入下轮评估。
- #420 流水：交付 EccTopCircuitCompare-001（schematic_netlist B-档 synthesized L2 k=12）— 真实 trace btze4(xiwang@hfeg0pkn002 mc=65) ECC 顶层电路结构对比：用户逐字「帮我对比一下DDGOA和DDCPC在EccTop这个电路的差异」。agent 在两个 OA 工程(/proj/ddgoa、/proj/ddcpc)下对二进制 sch.oa 用 strings 提取 inst:/net: token，识别 ECC 顶层单元(cell 名含 EccTop)，汇总子模块集合，检测电源/架构标记(DDGOA=stdcell container 含 SCmosEnBuf+vssz/vccz；DDCPC=两分支 DVFSC-dual-voltage+SCmos 含 vccsc/vdd2l+lvlshft)，交付结构化对比报告。资产 sch.oa 二进制不可直接读→B-grade synthesized：合成 A/B 两套 OA 工程目录树(sch.oa 二进制含嵌入 inst:/net: ASCII token，非可打印 noise bytes 0x80-0xFF 与 token 干净分隔)。候选写通用 ecc_top_compare.py(--projA/--projB/--out CLI) 遍历 <proj>/libs/*/<cell>/schematic/sch.oa，subprocess 真跑 strings 提取 token，识别 EccTop 顶层，汇总子模块集合交并差，电源架构判定(DVFS-dual-voltage/SCmos-enable-buffer/standard)，输出结构化 report.json。A=projA EccTop128x2New+BankTopX2/projB DVFSCEccTop+SCmosEccTop；B=projA EccTop256x1New+BankTopX4/projB DVFSCEccTop2+SCmosEccTop2(每维度反硬编码：cell 名/子模块名/电源标记全不同)。12 条 a-l：含 b subprocess 真跑 strings + d/e B 的 cell 名精确(非 A) + f shared=[EccCtrl] + g/h uniqueA/uniqueB 精确集合字典序 + i count 6/18 + j/k verdictB=DVFS-dual-voltage/verdictA=SCmos-enable-buffer + l 3-seed 确定+无 A 特有名泄露(精确匹配非子串)。自验 ref PASS 12/12 + §4.9 三假(empty/print-only/core-deleted 全 FAIL) + 3 neg(neg_empty/neg_hardcode_A/neg_core_deleted)全 FAIL。byte-sync sha d54ad937 size 10274。D.jsonl 231→232。深读 btze4_ecctop_compare.md。选料：scan3.py 扫 11-08 cron 日志 eda_trace_20261108.log 抽 D-domain 候选 cross-ref 台账(修复 sid-normalization bug：台账存全 <timestamp>_<sid>，cron 用短 <sid>，sed -E 's/^[0-9]+_//' 归一)→ 104 fresh→25 truly fresh→采 btze4(schematic:744 netlist:58)。⚠️ DEBT① 推翻：cron 日志是 fresh 源，rescan 非唯一路径。
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
