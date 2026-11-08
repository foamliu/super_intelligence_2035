WAITING: 0（#415 交付 VsimCovReport-001 · wk3wd cliu@hfeg0pkn004 mc=197 · schematic_netlist B-grade synthesized L3 k=12 · byte-sync sha e78d3ea5 size 12105 · D.jsonl 230 entries；#414 AddrRtlGateMap-001,#413 2StepOCChainAnalyze-001,#412 SdlGroupPlan-001(已归档批次2086),#411 SimlibLogicCheck-001,#410 SimAccelCellReco-001,#409 选料复核轮 0case,#408 TrimMuxInvDiff-001,#407 dup-fix+claim x8v81,#406 VrefCSMRRSeq-001,#405 0case,#404 0case,#403 OpenWaveFmt-001,#402 PrimeLibFlowAnalyze-001）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


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
- 📊 trace 覆盖率：226 / 1511 = 15.0%（mc>=30 候选池；D.tsv 现 226 case-mark + 1069 parked · 已动过 1295；快照 2026-11-08 15:12 sessions=3896 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 230 entries / wc -l 230）：analog_context · schematic_netlist · waveform。**#415**：wk3wd(cliu@hfeg0pkn004 mc=197)→VsimCovReport-001（schematic_netlist B-grade synthesized L3，vsim 回归 pattern 覆盖率统计脚本：pattern.list+regression_run 子目录树→per-pattern total/missing/bytemode 汇总；A=14 patterns/19 subdirs/碰撞对 bc8vsbc8_otf/missing{rdcrc,sre_freq}，B=18 patterns/24 subdirs/碰撞对 dca_trainvsdca_train_long+xtalk_basicvsxtalk_basic_long/missing{sppr_single,zen_mode}；12 条 a-l 含 f-i 碰撞对精确(反硬编码+反子串)+j missing 集合+k bytemode 汇总+l 3-seed+无A-token泄露；自验 ref PASS+§4.9 三假+3 neg FAIL；byte-sync sha e78d3ea5 size 12105；D.jsonl 229→230）。**#414**：7bg20→AddrRtlGateMap-001。**#412**：5fpjy(jcgu@hfeg0pin003 mc=152)→SdlGroupPlan-001（schematic_netlist B-grade synthesized L3，group-gen-sdl skill 匹配组生成分析阶段：SPICE 网表+match_cfg→groups.json；A=折叠cascode 3-mirror AABB / B=telescopic-bias 4-mirror Central Symmetry + 3-deep cascode(MCSC orphan) + 不同 orphans；12 条 a-l 含 B 三类 group 精确器件集 + orphans 精确(反硬编码) + 划分性质 + pattern∈allowed & 最大CM==B默认 + 3-seed 顺序不变性；自验 ref PASS + §4.9{a,e,f} + 4 neg FAIL；byte-sync sha 0572a9cb size 11257；D.jsonl 430→431）。**#411**：rl62o→SimlibLogicCheck-001。**#410**：qhzmr→SimAccelCellReco-001。**#409**：选料复核轮 0 case。**#408**：x8v81→TrimMuxInvDiff-001。**#407**：dup-fix+claim x8v81。**#406**：42jk5→VrefCSMRRSeq-001。**#405/#404**：0case。**#403**：OpenWaveFmt-001。**#402**：PrimeLibFlowAnalyze-001。**#401**：SramButterfly-001。**#400**：AbMatchPlacementCheck-001。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈30KB（本轮 #415 交付 1 case，流水新增 1 行；归档批次 2086: #412 流水全文搬 MEMORY_D_archive.md）
- DEBT: 0（#415 交付清零。⚠️ 需运维仍存：①全量 rescan summary.tsv（11-05 已 3 天陈旧）②放宽 D-domain 关键词 ③跨 shard domain 重分配（spice_sim/waveform 部分回流 D）④/proc 资产获取权限（/proj/dscqa、/rundata/drcpa_sim、/rundata/drcoa、/home/cliu/drcoa、/home/wellesc、/proj/train/AI_drcqa/workdir/jcgu 归属 cadmin/私有，e0031982 无读权限无 sudo，#408/#410/#411/#412/#413/#414/#415 均被迫采 B-grade synthesized 而非 A-grade faithful）⑤跨 shard dup 清理。⚠️ 未碰 shard B 飞行。）
- 🧾 断言: k_rationale=k_check=12 ✓（#415 VsimCovReport-001 落 jsonl，12==12≥8 达标；存量 229 entries test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 11-08 新 case 达标）。
- 🎯 通过率: 最近20条 n/a（#413 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- 流水 #413b (数据质量修复轮 0 新 case · 并行 shard D agent 已交付 2StepOCChainAnalyze-001 · 本 agent 检测重复并修复); 选料: trace_ledger --shard D next → 5i5bo(zqzhan@hfeg0pkn002 mc=155) 已被另一并行 agent claim(18:50) → 本 agent scp 5i5bo.messages.json(842KB/134msgs dir-based) → 深读: U#64「检查2StepOc功能，看看有没有什么优化的空间…SA的OC阶段分两步打开NCS和PCS，SanEn/SapEn第一个pulse上升沿分步打开」A-grade seed → 助手 gold: 读pyAether_API.md(1507行)+input.sp(TT/45C/pvcc1.1/t0=60ns/512cycles)+stimulus_2stepOC.sp(81行,5组信号,one-hot Dly/Dly2)+measure_2StepOC.sp(2052行,N=0..255,sapenbusec35→sanenbusec35,256窗口)+netlist grep(RasSim_2stepOcCtrl/R_TwoStepOCtrimDly(4-bit二进制定权电容)/RasSim_NcCtrl_LPwr/R_SaCtrol)→输出2843字链路分析(msg#133); ⚠️资产不可读(/proj/drcpa/V0/private, e0031982无权限) → 本 agent 合成 TwoStepOCAnalyze-001(A=TT/45C/t0=60ns/512cyc/256win/4-bit, B=LT/-40C/t0=50ns/384cyc/192win/5-bit, 15条件a-o, ref PASS+neg FAIL+§4.9{c,e,m}) → **发现 D.jsonl 已有 2StepOCChainAnalyze-001(2StepOCChainAnalyze, case_id 正确但 task_id malformed)** → 删除自身重复 case TwoStepOCAnalyze-001(assets+reference) → 修复 D.jsonl 7 个 malformed task_id: line92-95 task_id=""→case_id(OpenWaveFmt/HierSpiceMosCount/PwlConvert/FinesimAutoRun), line226 SimlibLogicCheck→EDA-Eval-DesignFlow-SimlibLogicCheck-001, line227 SdlGroupPlan→EDA-Eval-DesignFlow-SdlGroupPlan-001, line228 2StepOCChainAnalyze→EDA-Eval-DesignFlow-2StepOCChainAnalyze-001; 验证 2StepOCChainAnalyze-001: ref_submit.zip PASS + byte-sync sha 7a21129b match + 228 entries 全 task_id==case_id; 深读笔记 designflow/trace_deepreads/5i5bo_2stepoc_analyze.md; ledger 5i5bo 已 mark case(19:09 by parallel agent); eda_flow close_session; 无新 PII; **WAITING: 0**) — 本轮新增，未归档
- 流水 #411 (交付 EDA-Eval-DesignFlow-SimlibLogicCheck-001, schematic_netlist B-grade synthesized L1, 15 条件 a-o, byte-sync sha 5e7590e6 size 10068, cliu rl62o hfeg0pkn004 mc=216) — 全文见 git 历史(被 #413b 替换压缩)
- (归档批次 2085) 流水 #410 (SimAccelCellReco-001, analog_context B k=16, qhzmr e03179@hfeg0pkn002 mc=29, byte-sync sha 38eccf62 size 9956) 全文已搬 MEMORY_D_archive.md
- 流水 #409 (选料复核轮 0 case · hfeg0pkn005 fresh A-grade D seed 枯竭 · DEBT:0 真外部阻塞; 选料: #408 清 DEBT 后无 in-flight claim → 启动新主机扫描扩展 fresh 池；目标选 summary.tsv 中 D-domain 命中第 1 的 hfeg0pkn005(10.129.2.14, 436 sessions, 未被 #407 五主机扫描覆盖) → eda_flow open_session(hfhds201) → ssh hfeg0pkn005 `find /home/*/.cline/data/sessions/ -name "*.messages.json" -mtime -30` → 376 sessions → 本地 cross-ref all-shard ledger(1660 sids, A+B+C+D, _tmp/pkn005_sids.tsv + pkn005_notledger_paths.txt) → **208 not-in-ledger** → scp paths.txt + peek_pkn005.py 到 hfeg0pkn005:/tmp/ 远程 python3 批量解析首 2 user 消息(约 90 JSONDecodeError 因 >200KB 截断, 118 成功解析) → D-domain 命中评估: 11cny(clwang verilog 路径 Q&A 非 seed) / mn1f7+z7niq+sax7n+u9tql+vmnh4+9vjrk+7b4kj(e0014566 virtuoso API one-liner demo 非 design-flow) / y6sbk+qx7gd(e0031982 agent 自测跳过) / yyk0s(e0027609 DEJOA act Q&A) / 4p1z2(ronghu cdl.spf 1msg 过短无 gold) / d328b+9q3m7(rongjiez compare_wave_new.pl 解释脚本 Q&A 非 build) / 1uhpn(qiang3xu waveview eye-diagram config how-to) / msv4x+jqnx3+pqwcu(yqlu TCP-CT-M1 用户已给根因+修复 A 档不可用) / 0mkow(yixiaow qualib tcl 过 terse) / 277nq(jinsongl ERC=physical_verify 非 D) / 3v5rl(ellawu dummy+DRC=physical_verify 非 D) / wlraf(eunicef nicap_qa net warning Q&A marginal) / mikng(haoxu primesim 路径 spice_sim 非 D) / 75n4g(jingjiew signal OSC tb stimulus spice_sim 非 D) / 其余 ~80(e0014566/e0046686/ellawu/rongjiez/sxdong/t0002987 等 bsub env / anasimpro-gui / skill-creator / hi/nihao / workflow-controller meta 非 D 非 seed 元任务) → **0 fresh D synthesizable A-grade seed**；跨 2 批新主机扫描(#407: hfeg0pkn001-4+pnd002; #409: hfeg0pkn005)均无 fresh A-grade D seed；eda_flow close_session(keep=false) 释放; 🚫 0 case 落 jsonl(不越 shard/不造低质/不判分歧义/不新增跨 shard dup); ✅ 选料复核记录 designflow/r409_selection_round_D.md + _tmp/pkn005_sids.tsv + _tmp/peek_pkn005.py(reusable); ledger_D 无新增(无 claim/mark, 1334 不变); 无新 PII / 无改 jsonl(428 不变) / 无动 EDA-Flow-Bench 仓 assets+reference; **WAITING: 1 等人工(真外部阻塞)**：①全量 rescan summary.tsv(11-05 已 3 天陈旧, 无 newer summary.tsv, cron 仅 eda_trace_20261108.log 无新 summary.tsv 产物) ②放宽 D-domain 关键词 ③考虑跨 shard domain 重分配(spice_sim/waveform 部分回流 D)) — 本轮新增，未归档
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
