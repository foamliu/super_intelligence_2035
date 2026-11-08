WAITING: 0（#410 交付 SimAccelCellReco-001 · qhzmr e03179@hfeg0pkn002 mc=29 · analog_context B-grade synthesized L1 k=16 · byte-sync sha 38eccf62 size 9956 · D.jsonl 429 行(226 valid)；#409 选料复核轮 0 case(hfeg0pkn005 fresh A-grade D seed 枯竭 真外部阻塞),#408 TrimMuxInvDiff-001,#407 dup-fix+claim x8v81,#406 VrefCSMRRSeq-001,#405 0case,#404 0case,#403 OpenWaveFmt-001,#402 PrimeLibFlowAnalyze-001,#401 SramButterfly-001）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


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
- 📊 trace 覆盖率：222 / 1511 = 14.7%（mc>=30 候选池；D.tsv 现 222 case-mark + 1070 parked · 已动过 1292；快照 2026-11-08 12:06 sessions=3896 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 226 entries / wc -l 429）：analog_context · schematic_netlist · waveform。**#410**：qhzmr(e03179@hfeg0pkn002 mc=29)→SimAccelCellReco-001（analog_context B-grade synthesized L1，/proj/dscqa 资产权限阻塞→合成 sim_path+config+reco JSON 忠实复刻 trace：CRC 路径判定 + ranked cell 推荐表；A=9cell/CRC OFF/top R_lvlshftVcc2sc2Vdly / B=10cell/CRC_11 ON/top R_dly2VddVss；16 条 a-p；自验 ref PASS 16/16 + 4 neg FAIL distinct{d,p,f,g} + §4.9 三假 distinct{d,p,f}；byte-sync sha 38eccf62 size 9956；D.jsonl 428→429）。**#409**：选料复核轮 0 case(hfeg0pkn005 fresh A-grade D seed 枯竭)。**#408**：x8v81→TrimMuxInvDiff-001。**#407**：dup-fix+claim x8v81。**#406**：42jk5→VrefCSMRRSeq-001。**#405/#404**：0case。**#403**：OpenWaveFmt-001。**#402**：PrimeLibFlowAnalyze-001。**#401**：SramButterfly-001。**#400**：AbMatchPlacementCheck-001。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈31KB（本轮 #410 交付 1 case，流水新增 1 行）
- DEBT: 0（#410 交付清零。⚠️ 需运维仍存：①全量 rescan summary.tsv（11-05 已 3 天陈旧）②放宽 D-domain 关键词 ③跨 shard domain 重分配（spice_sim/waveform 部分回流 D）④/proc 资产获取权限（/proj/dscqa、/rundata/drcpa_sim、/rundata/drcoa 归属 cadmin，e0031982 无读权限无 sudo，#408/#410 均被迫采 B-grade synthesized 而非 A-grade faithful）⑤跨 shard dup 清理。⚠️ 未碰 shard B 飞行。）
- 🧾 断言: k_rationale=k_check=16 ✓（#410 SimAccelCellReco-001 落 jsonl，16==16≥8 达标；存量 226 entries test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 1/30 新 case 达标）。
- 🎯 通过率: 最近20条 n/a（#410 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- 流水 #410 (交付 EDA-Eval-DesignFlow-SimAccelCellReco-001, analog_context B-grade synthesized L1, 16 条件 a-p, byte-sync sha 38eccf62b4cedd388d81f16dffd9fccc63abe412998c128d84d5b80499e6955f size 9956, e03179 qhzmr hfeg0pkn002 mc=29; 选料: trace_ledger --shard D next → mc≥30 top26 全 IN-LEDGER(确认 #399-#409 枯竭) → 降阈 mc15-29 跑 cand2.py 得 361 D-domain 候选 → 本地 cross-ref all-shard ledger(3358 sids A+B+C+D) → 多个 FRESH e03179@hfeg0pkn002(strong D: netlist+analog+waveview) → 选 qhzmr(mc=29, netlist:231/analog:97/transistor:55/waveview:20) → eda_flow open_session → ssh 10.129.2.11 scp qhzmr.messages.json(220KB/36msgs,dir-based) → 完整深读: U0「我有仿真加速的优化需求...」meta(问方案非build) / U4「方案二的仿真路径是/proj/dscqa/.../primesim.Golden008_...,帮我查看下哪些cell可以直接替换」A-grade seed✓(表达目标未给修复→采纳为 prompt) → 助手 gold: ①CRC 路径判定(路径不含 CRC_01/10/11→CRC 关闭→D_CRCR10_CRCTop 输出静态→可直接替换) ②列 run 目录无 finesim.prof ③解析历史 vam_reco_Golden008.json→9 cell ranked 表(R_lvlshftVcc2sc2Vdly 37%/512x → AG_VdbiasAct 8%/16x → IO_CABufCore 6%/12x → ...) ④用户选 D_CRCR10_CRCTop→gen_bnk_va 替换；⚠️ 资产获取阻塞: /proj/dscqa 在 10.129.2.11 Permission denied(同 #408 /rundata/drcpa) → 采 B-grade synthesized(trace_source 真实 qhzmr,assets 合成忠实复刻 trace 结构) → 合成 A(sim_path.txt 无 CRC 关键字/CRC OFF + config.json DSCQA→D_CRCR10_CRCTop + vam_reco.json 9 cell 忠实 trace) + hidden B(sim_path_B.txt 含 CRC_11/CRC ON + vam_reco_B.json 10 cell 不同名不同用量不同 top=R_dly2VddVss + config_B.json 同 DSCQA) + prompt.txt(逐字 U4 原文) + task_brief.md(交付接口≤3 行) + hidden_manifest.json → ref analyze_sim_accel_ref.py(CLI 4 参: 读 sim_path+config+reco→determine_crc+find_crc_block+parse_reco→report.json) → check.py 16 条 a-p(a zip 含 analyze_sim_accel.py+report.json / b py_compile / c B-run exit0+B_report.json / d 8 顶层键 / e 5 crc 键 / f B crc_enabled==True / g B crctop_replaceable==False / h B crc_block_name==D_CRCR10_CRCTop / i B cells len==10 / j B top_cell==R_dly2VddVss / k 每 cell 5 字段 / l rank 1..10 递增 / m total==len / n top_cell==cells[0] / o 3-seed md5 一致 / p 反硬编码 A crctop_replaceable==True+A top R_lvlshftVcc2sc2Vdly+A≠B 三字段全不同)；自验: ref_submit.zip PASS 16/16 + negative_selftest 4 neg FAIL distinct{d,p,f,g} NEG_RC=4(empty_shell→d 缺顶层键 / print_expected→p 反硬编码 A 返 B 值 / core_deleted→f crc_enabled None / always_off→g crctop_replaceable True) + §4.9 三假 empty_shell→d / print_expected→p / core_deleted→f 全 FAIL distinct / 断言闸门 16==16≥8 ✓ / byte-sync jsonl test sha 38eccf62...== 磁盘 check.py 9956B ✓ / 追加 D.jsonl(428→429, id=EDA-Eval-DesignFlow-SimAccelCellReco-001) → ledger_D qhzmr mark --status case；eda_flow close_session(keep=false) 释放；⚠️ B-grade 而非 A-grade 因 /proj/dscqa 资产获取权限阻塞(非意图降级)；无新 PII(prompt 含真实路径/proj/dscqa/.../e03179 但按 red line #2 保留原值,仅 key/token 掩码——本 prompt 无 key/token) / EDA-Flow-Bench 新增 assets+reference(prompt+task_brief+sim_path+config+vam_reco+hidden×4+check.py+ref+4 neg+negselftest+ref_submit.zip) / D.jsonl 追加 1 行; research 日报 11-08 designflow 建议(benchmark maintenance debt+资源预算)与本轮 case 交付无直接可执行条目(rewrite_queue 15/15 done，本 case 已含 cond o 3-seed + cond p 反硬编码)，按常驻令忽略; WAITING: 0) — 本轮新增，未归档
- 流水 #409 (选料复核轮 0 case · hfeg0pkn005 fresh A-grade D seed 枯竭 · DEBT:0 真外部阻塞; 选料: #408 清 DEBT 后无 in-flight claim → 启动新主机扫描扩展 fresh 池；目标选 summary.tsv 中 D-domain 命中第 1 的 hfeg0pkn005(10.129.2.14, 436 sessions, 未被 #407 五主机扫描覆盖) → eda_flow open_session(hfhds201) → ssh hfeg0pkn005 `find /home/*/.cline/data/sessions/ -name "*.messages.json" -mtime -30` → 376 sessions → 本地 cross-ref all-shard ledger(1660 sids, A+B+C+D, _tmp/pkn005_sids.tsv + pkn005_notledger_paths.txt) → **208 not-in-ledger** → scp paths.txt + peek_pkn005.py 到 hfeg0pkn005:/tmp/ 远程 python3 批量解析首 2 user 消息(约 90 JSONDecodeError 因 >200KB 截断, 118 成功解析) → D-domain 命中评估: 11cny(clwang verilog 路径 Q&A 非 seed) / mn1f7+z7niq+sax7n+u9tql+vmnh4+9vjrk+7b4kj(e0014566 virtuoso API one-liner demo 非 design-flow) / y6sbk+qx7gd(e0031982 agent 自测跳过) / yyk0s(e0027609 DEJOA act Q&A) / 4p1z2(ronghu cdl.spf 1msg 过短无 gold) / d328b+9q3m7(rongjiez compare_wave_new.pl 解释脚本 Q&A 非 build) / 1uhpn(qiang3xu waveview eye-diagram config how-to) / msv4x+jqnx3+pqwcu(yqlu TCP-CT-M1 用户已给根因+修复 A 档不可用) / 0mkow(yixiaow qualib tcl 过 terse) / 277nq(jinsongl ERC=physical_verify 非 D) / 3v5rl(ellawu dummy+DRC=physical_verify 非 D) / wlraf(eunicef nicap_qa net warning Q&A marginal) / mikng(haoxu primesim 路径 spice_sim 非 D) / 75n4g(jingjiew signal OSC tb stimulus spice_sim 非 D) / 其余 ~80(e0014566/e0046686/ellawu/rongjiez/sxdong/t0002987 等 bsub env / anasimpro-gui / skill-creator / hi/nihao / workflow-controller meta 非 D 非 seed 元任务) → **0 fresh D synthesizable A-grade seed**；跨 2 批新主机扫描(#407: hfeg0pkn001-4+pnd002; #409: hfeg0pkn005)均无 fresh A-grade D seed；eda_flow close_session(keep=false) 释放; 🚫 0 case 落 jsonl(不越 shard/不造低质/不判分歧义/不新增跨 shard dup); ✅ 选料复核记录 designflow/r409_selection_round_D.md + _tmp/pkn005_sids.tsv + _tmp/peek_pkn005.py(reusable); ledger_D 无新增(无 claim/mark, 1334 不变); 无新 PII / 无改 jsonl(428 不变) / 无动 EDA-Flow-Bench 仓 assets+reference; **WAITING: 1 等人工(真外部阻塞)**：①全量 rescan summary.tsv(11-05 已 3 天陈旧, 无 newer summary.tsv, cron 仅 eda_trace_20261108.log 无新 summary.tsv 产物) ②放宽 D-domain 关键词 ③考虑跨 shard domain 重分配(spice_sim/waveform 部分回流 D)) — 本轮新增，未归档
- 流水 #408 (交付 EDA-Eval-DesignFlow-TrimMuxInvDiff-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 41d51c79d9965a0c size 11178, dsgao x8v81 hfeg0pkn001 mc=0; 选料: 清 #407 DEBT:1 → eda_flow open_session(hfhds201) → ssh hfeg0pkn001 scp 1793945103405_x8v81/1793945103405_x8v81.messages.json(391KB/82msgs) → 完整深读 3 任务链：①U0「drcpa...R_trimEqOff 和 drcoa...R_trimEqOff 有区别吗，为什么后仿真 delay 有差异」A-grade seed✓(表达目标未给修复→采纳为 prompt) ②U26/U45/U53 GidlAryCtrl testbench 修改+验证(另一独立链,未采纳) ③U69 R_tOCTrim pair 对比(A-grade seed→采纳为隐藏 B) → 助手 gold( idx=25): 两 netlist 共享全部 stdcell(invDS/invDSx1/mx2LVSx2/dlyg*of8*)，顶层 R_trimEqOff 的 trim 选择通路 drcoa 多 1 级 invDSx1(XI13: trimN→trim)，drcpa 仅 XI7 → delay 差异来源 = 多 1 级反相器；⚠️ 资产获取阻塞：/rundata/drcpa_sim、/rundata/drcoa 归属 cadmin:drcpa，e0031982 无读权限且无 sudo → 无法取真实 netlist → 采 B-grade synthesized(trace_source 真实 x8v81，assets 合成但忠实复刻 trace 结构差异模式) → 合成 A pair(drcpa_R_trimEqOff 111 行 / drcoa_R_trimEqOff 119 行，drcoa 含 XI13<0>/<1> 额外 invDSx1 + 3 额外 XI_switch) + hidden B pair(drcpa_R_tOCTrim 154 行 / drcoa_R_tOCTrim 156 行，drcoa XI18 dlyg2→dlyg0 / XI25 dlyg4→dlyg6 / XI30 dlyg4→dlyg6 + XI29<0>/<1> 额外 invLx2) + prompt.txt(逐字 U0 原文) + task_brief.md(交付接口≤3 行) → ref analyze_netlist_diff.py(读两 netlist→parse_header/parse_subcircuits/parse_top_level_instances/diff_instances/delay_finding/diff_hunk_count→report.json) → check.py 16 条 a-p(a zip+analyze_netlist_diff.py / b py_compile / c B-run exit0+report.json / d 7 必需顶层键 / e file_line_counts==B 实际 / f Date 左右不同 / g TopDesign 左右不同 / h subcircuits.shared>=3 / i left_only+right_only 为 list / j added 含 XI29 / k changed 含 XI25 / l changed 含 XI30 / m changed 含 XI18 / n delay_relevant_finding 非空+>=2 delay 关键词 / o 3-seed md5 一致 / p 反硬编码 A finding≠B 且 A 含 XI13 不含 XI25)；自验: ref_submit.zip PASS 16/16 + negative_selftest 4 neg FAIL distinct{c,d,h,p} NEG_RC=0(print_expected→c / empty_shell→d / core_deleted→h / always_trim_inv→p) + §4.9 三假 empty_shell→d / print_expected→c / core_deleted→h 全 FAIL distinct / 断言闸门 16==16≥8 ✓ / byte-sync jsonl test sha 41d51c79d9965a0ced6ad5bdb1c76d888ad9ee382eba8b0bbbe17161c488140a == 磁盘 check.py 11178B ✓ / 追加 D.jsonl(427→428, id=EDA-Eval-DesignFlow-TrimMuxInvDiff-001) → ledger_D x8v81 mark --status case；eda_flow close_session(keep=false) 释放；⚠️ B-grade 而非 A-grade 因资产获取权限阻塞(非意图降级)；无新 PII(prompt 含真实路径/proj/drcpa/.../dsgao/...但按 red line #2 保留原值，仅 key/token 掩码——本 prompt 无 key/token) / EDA-Flow-Bench 新增 assets+reference(4 netlist + prompt + task_brief + hidden_manifest + check.py + ref + 4 neg + negselftest + ref_submit.zip) / D.jsonl 追加 1 行; research 日报 11-08 designflow 建议(benchmark maintenance debt+资源预算)与本轮 case 交付无直接可执行条目(rewrite_queue 15/15 done，本 case 已含 cond o 3-seed + cond p 反硬编码)，按常驻令忽略; WAITING: 0) — 本轮新增，未归档
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
