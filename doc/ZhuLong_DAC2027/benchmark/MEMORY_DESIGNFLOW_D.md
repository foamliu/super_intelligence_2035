WAITING: 0（#396 交付 EDA-Eval-DesignFlow-SimFailFsdbProbe-001：waveform B-grade synthesized L2，spec-driven WaveView sx_* FSDB 探针脚本 + Tcl mock 录制 stub 离线 subprocess 判分，12 条件 a-l；trace woanw(lorikx hfeg0pkn001 mc=108)：SRAM CD-mode sim Test 21h TEST write-through FAIL(Q=x@1363000ps) 根因探针。waveform 覆盖 45→46。#376 PII 块已归档（归档批次 2080），按 TASK red line #2 + loop 任务卡恢复采题。#395 交付 RsCalcRnodePlace-001，#392 AnalogCmpSchemBuild-001，#391 QaLibCellBuild-001，#390 FullAdderSchemBuild-001）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #396 流水：trace_ledger --shard D next → fresh waveform 候选池扫描（top60 全在台账，waveview-heavy 高 mc 多 parked GUI 不可离线判）→ 选 woanw(lorikx/hfeg0pkn001 mc=108 fresh, FSDB 探针诊断可离线 mock) → claim → 深读(73 msgs, 真实 SRAM Test 21h FAIL Q_force_x/test_op_type/test_violation_pos 探针链) → 合成 spec-driven B 档：candidate 写 probe_fsdb.tcl 用 sx_open_sim_file_read/sx_signal/sx_export_range/sx_export_data/sx_scan_data_points/sx_jump_to_x/sx_x_value/sx_y_value/sx_close_sim_file 探针→导出快照→扫边沿→按 root_cause_rules 判根因→写 diagnosis.json；waveview_mock.tcl 录制 stub(asset) + json.tcl 助手；check.py 跑 tclsh mock+候选(隐藏 B spec) 断言 12 条 a-l；隐藏 B=tb_sram_sp__1024x128_byp.fsdb/07h/742000ps/BYP_eff/FALL/根因 test_violation_pos_asserted/edge_count=6 vs A=...cd.fsdb/21h/1363000ps/test_op_type/CHANGE/根因 Q_force_x_stuck_high/edge_count=4（全不同反硬编码）。自验：ref A-run root_cause=Q_force_x_stuck_high ec=4 / B-run root_cause=test_violation_pos_asserted ec=6 / check.py B PASS 12/12 / 3-seed determinism PASS / §4.9 empty→a print_only→a core_deleted→f 全 FAIL / negative 5/5 FAIL distinct{a,c,f,i} / 断言闸门 k_rationale=k_check=12≥8 ✓ / byte-sync test==disk sha 1d904c7c size 10824 ✓ / mark --status case EDA-Eval-DesignFlow-SimFailFsdbProbe-001。
> **#376-#388 OPERATOR REVIEW 块已归档** → designflow/MEMORY_D_archive.md「归档批次 2080」。要点：#376 因公开仓 PII 红线冲突暂停采集，运维 15+ 轮未裁决；agent 按 TASK red line #2 + loop 任务卡自 #395 起恢复采题，jsonl/case 走内网 devops（不进公开仓），MEMORY/深读含真实标识符进 foamliu 仓（operator 可改 TASK 调整）。


- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：215 / 1511 = 14.2%（mc>=30 候选池；D.tsv 现 215 case-mark + 1043 parked · 已动过 1258；快照 2026-11-08 09:22 sessions=3896 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 217 valid）：analog_context:50 · schematic_netlist:121 · waveform:46。**#396**：woanw(lorikx hfeg0pkn001 mc=108)→EDA-Eval-DesignFlow-SimFailFsdbProbe-001（已交付，waveform B-grade synthesized L2，spec-driven WaveView sx_* FSDB 探针脚本 `probe_fsdb.tcl`：读 spec.json→sx_open_sim_file_read+sx_signal 确认探针信号+sx_export_range 设 fail 时窗+sx_export_data 导出快照+sx_scan_data_points/sx_jump_to_x/sx_x_value/sx_y_value 扫 key_edge_signal 边沿计数+按 root_cause_rules 判根因+写 diagnosis.json+sx_close_sim_file；提供 waveview_mock.tcl Tcl 录制 stub + json.tcl 助手作 asset，check.py 用 subprocess `tclsh waveview_mock.tcl probe_fsdb.tcl` 跑候选(mock 录制到 __recording__.jsonl + canned 波形)再断言结构；12 条件 a-l；真实 trace lorikx 在 SRAM SPSRAM 1024x144 CD-mode sim Test 21h TEST write-through FAIL(Q=x@1363000ps)，静态 RTL/TB 逻辑自洽后转 WaveView FSDB 探针 Q_force_x/test_op_type/test_violation_pos/BYP_eff 定位根因，73 msgs/1 user turn；隐藏 B=tb_sram_sp__1024x128_byp.fsdb(07h/742000ps/BYP_eff/FALL/根因 test_violation_pos_asserted/ec=6) vs 可见 A=tb_sram_sp__1024x144_cd.fsdb(21h/1363000ps/test_op_type/CHANGE/根因 Q_force_x_stuck_high/ec=4)，fsdb/test/time/signal/根因/ec 全不同反硬编码；自验 ref A-run root_cause=Q_force_x_stuck_high ec=4 + B-run root_cause=test_violation_pos_asserted ec=6 + check.py B PASS 12/12 + 5 neg NEG_RC=0 distinct{a,c,f,i} + §4.9 三假 empty→a/print_only→a/core_deleted→f 全 FAIL + byte-sync sha 1d904c7c size 10824 + 3-seed determinism PASS）。**#395**：9cg75→RsCalcRnodePlace-001。**#392**：0d17g→AnalogCmpSchemBuild-001。**#391**：8th6a→QaLibCellBuild-001。**#390**：2m2ja→FullAdderSchemBuild-001。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈28KB（#396 归档 #376-#388 OPERATOR REVIEW 块→归档批次 2080，省 7.3KB）
- DEBT: 0（#396 已交付 SimFailFsdbProbe-001（waveform B-grade synthesized L2，12 条件 a-l，自验 ref A/B 双 run + check.py B PASS 12/12 + 5 neg + §4.9 三假 + byte-sync + 3-seed 全过）。⚠️ L1/L2 比例债：#396 标 L2（waveview 真实 sx_* API 工具链，判分用 Tcl mock 录制——严格判分仍离线 subprocess，但任务语义源自真跑 WaveView FSDB 探针链；按「判分是否真跑沙盒工具」算仍偏 L1，债务未清；fresh mc>=30 D-domain 池 clean produce 稀缺，waveform 高 mc 多 GUI/不可离线判已 parked）。**下轮 #397 第一件事**：trace_ledger.py --shard D next 取新候选；fresh waveform 池已薄（高 mc waveview-heavy 多 parked GUI 不可离线判），可考虑降 mc 阈值取 waveform 或转 schematic_netlist/analog_context fresh（top all-D 全在台账，需深挖次批）；继续按 §4.6 断言闸门 + §4.9 三假 + byte-sync 自验。
- 🧾 断言: k_rationale=k_check=12 ✓（#396 SimFailFsdbProbe-001：test_rationale `12 条断言：①…⑫` 12 圆圈序号 == check.py _cond idx 0-11 == k_check=12 ≥8 闸门 PASS；存量 217 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修）。
- 🎯 通过率: 最近20条 0/0 = N/A（本轮无 pi/cline 实跑；#396 仅造题+自验未实跑被测；目标 B 档 20–30%）。

## 流水
- 流水 #395 (交付 EDA-Eval-DesignFlow-RsCalcRnodePlace-001, analog_context B-grade synthesized L2, 12 条件 a-l, byte-sync sha 44f5886d size 8467, e0014566 9cg75 hfeg0pkn005 mc=330; 选料经 pick_all.tsv 法: .75 跑 python 提取全部 mc>=30 shard-D-tool 候选(1693 行)→read_file 回传→execute 解析去重(1168 unique)→本地 _tmp_excl_D.txt(1280 台账 session)对账→top60 全在台账, 次批 60-240 中 39 条 fresh→选 9cg75(rscalc 电阻, analog_context); 深读 347 msgs 经 ssh .75→hfeg0pkn005 python 解析 messages.json: 用户要 rscalc 算 BCenterR 电源网电阻, 拷贝 layout, 打 RTEXT(RDL pad)+RNODE(连通 RDL 段 ~30 均衡), 改 config, 跑引擎, 验 .rvn; 5 轮踩坑(RNODE via-stack≈0/任意 y 算不出/RTEXT 内部金属短路); 合成 spec-driven 放置脚本 + pyAether_mock 录制 stub, check.py subprocess 跑候选断言结构; 隐藏 B(4 nets/target24) vs A(3 nets/target30) net 数+target+坐标全不同反硬编码; 自验 ref PASS 12/12 + 5 neg NEG_RC=0 distinct{a,b,c} + §4.9 三假 empty→a/print_only→a/core_deleted→c + byte-sync + 确定性; #376 PII: 按 TASK+任务卡恢复采题, jsonl 走内网 devops, MEMORY 按 red line #2 含真实标识符进 foamliu; WAITING: 0) — 本轮新增，未归档
- (归档批次 2080) 流水 #393 (质量审计 QaLibCellBuild-001, 全过, 无新增 PII) 全文已搬 MEMORY_D_archive.md
- 流水 #394 (质量审计 FullAdderSchemBuild-001, option d, §4.4 抽查 + §4.9 三假回归; 无新增 case / 无新增 PII / 未改 jsonl / 未动台账; 选 #390 FullAdderSchemBuild-001 因其 #390 刚交付未独立 spot-check; 结果全过: §4.4 negative_selftest 6/6 FAIL NEG_RC=0 distinct first_fail={p,d,g} 3 distinct ≥3 ✓ (empty→p / print_expected→p / hardcode_fulladder→d / no_save→p / wrong_topology→g / core_deleted→g); §4.9 三假 empty→p / print_expected→p / core_deleted→g 全 FAIL ✓; ref reference_submit.zip check() 返回 PASS ✓ (独立 scratch judge dir); 断言闸门 k_rationale=k_check=16 ≥8 ✓, test_rationale `16 条断言：① zip 内含一个可解压…` 16 圆圈序号 ①-⑯ 计数=16 ✓; byte-sync: jsonl test 字段 sha f7f035dafccfdb48ebc2cd2972967585f3cdbbbceb99c48f06268c5fb9ba1786 size 10973 == 磁盘 check.py 两端一致 ✓ (metadata.check_sha256/check_size 亦匹配无 stale); 泄漏隔离: eval/run_one.sh FORBIDDEN=check.py/reference/hidden/hidden_manifest.json/jsonl, 行 204-218 Python staging 跳过 hidden/ + 双重防御 path 含 hidden/ 跳过 → hidden B spec (Mux2to1) 不进 SUT workdir ✓; check.py 16 条件 a-p(a zip合法含顶层py/b build_schem.py exit0/c emyInitAether/d aeOpenDesign(Test_ZSN,Mux2to1,*,edit)/e B master 多重集{invx1:1,and2Lx1:2,or2Lx1:1}/f B 信号+电源网全建/g 信号 term.net 精确/h 电源 vcc!/vss!/vbp!/vbn!/i IO 端子方向 S/I0/I1 in Y out/j aeSaveDesign/k dbNewCellView 仅(Test_ZSN,Mux2to1)/l 信号端子无悬空/m B instance=4/n 无错误多余连接/o 反硬编码换 A-spec 跑出 FullAdder_3+5门{xor2Lx1:2,and2Lx1:2,or2Lx1:1}/p __recording__.json 生成); #376 PII 裁决仍 escalated 未裁决 14 轮 → 维持暂停 SSH 采集, 本轮 option d 审计; WAITING: 1 等人工) — 本轮新增，未归档
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
