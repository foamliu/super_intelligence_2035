WAITING: 0（#408 交付 TrimMuxInvDiff-001 + 清 DEBT:1：①#407 claim 的 x8v81(dsgao@hfeg0pkn001, schematic_netlist) 完整深读 82 msgs→U0 逐字「drcpa...R_trimEqOff 和 drcoa...R_trimEqOff 有区别吗，为什么后仿真 delay 有差异」A-grade seed✓ + U69 R_tOCTrim pair 作隐藏 B；②⚠️ 资产获取阻塞：/rundata/drcpa_sim、/rundata/drcoa 归属 cadmin:drcpa，e0031982 无读权限且无 sudo→无法取真实 netlist→采 B-grade synthesized（trace_source 真实 x8v81，assets 合成但忠实复刻 trace 结构差异模式：A=trim mux XI13 额外反相器 / B=延时抽头 dlyg4→dlyg6 + XI29 额外反相器）；③合成 assets(A: drcpa/drcoa R_trimEqOff 111/119 行 + hidden B: drcpa/drcoa R_tOCTrim 154/156 行) + ref analyze_netlist_diff.py + check.py 16 条 a-p + 4 neg + ref_submit.zip；④自验 ref PASS 16/16 + 4 neg FAIL distinct{c,d,h,p} NEG_RC=0 + §4.9 三假 distinct{d,c,h}；⑤断言闸门 16==16≥8 ✓ + byte-sync sha 41d51c79d9965a0c size 11178 ✓；⑥追加 D.jsonl 427→428 + mark --status case。#407 dup-fix+claim x8v81(partial deep-read),#406 VrefCSMRRSeq-001(孤儿采纳),#405 0case,#404 0case,#403 OpenWaveFmt-001,#402 PrimeLibFlowAnalyze-001,#401 SramButterfly-001）
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
- 📊 trace 覆盖率：221 / 1511 = 14.6%（mc>=30 候选池；D.tsv 现 221 case-mark + 1070 parked · 已动过 1291；快照 2026-11-08 12:06 sessions=3896 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 225 entries / wc -l 428）：analog_context · schematic_netlist · waveform。**#408**：x8v81(dsgao@hfeg0pkn001)→TrimMuxInvDiff-001（B-grade synthesized L1，资产获取权限阻塞→合成 netlist 忠实复刻 trace 结构差异：A=trim mux XI13 额外反相器 / B=延时抽头 dlyg4→dlyg6 + XI29 额外反相器；16 条 a-p；自验 ref PASS 16/16 + 4 neg FAIL distinct{c,d,h,p} + §4.9 三假 distinct{d,c,h}；byte-sync sha 41d51c79d9965a0c；D.jsonl 427→428）。**#407**：dup-fix + post-summary fresh scan + claim x8v81(partial deep-read)。**#406**：42jk5(t0002470)→VrefCSMRRSeq-001（⚠️ #407 修正：大写 line 428 是 #406 误增 dup，已移除；原小写 line 237 保留）。**#405**：0case。**#404**：0case。**#403**：OpenWaveFmt-001。**#402**：PrimeLibFlowAnalyze-001。**#401**：SramButterfly-001。**#400**：AbMatchPlacementCheck-001。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈31KB（本轮 #407 dup-fix + scan，无大块新增）
- DEBT: 0（#408 清零：#407 claim 的 x8v81 已完整深读→合成→自验→追加 D.jsonl 427→428 TrimMuxInvDiff-001。⚠️ 需运维仍存：①全量 rescan summary.tsv ②孤儿再分配(cell_rewrite_simlib/SpfNtsvMissingDiag 实已在 jsonl，#406 orphan 检测 case-sensitivity bug) ③跨 shard dup 清理(kk5tf/lywbf/ezcgh/h2sri=shard B 已 case) ④/proc 资产获取权限（/rundata/drcpa_sim、/rundata/drcoa 归属 cadmin:drcpa，e0031982 无读权限且无 sudo，本轮被迫采 B-grade synthesized 而非 A-grade faithful）⑤剩余 fresh seeds h12nr(mike,sub_schematic)/262wq(allenzh,HSPICE debug) 待采。⚠️ 未碰 shard B 飞行。）
- 🧾 断言: k_rationale=k_check=16 ✓（#408 TrimMuxInvDiff-001 落 jsonl，16==16≥8 达标；存量 225 entries test_rationale 全部以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 1/30 新 case 达标）。
- 🎯 通过率: 最近20条 n/a（#408 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- 流水 #408 (交付 EDA-Eval-DesignFlow-TrimMuxInvDiff-001, schematic_netlist B-grade synthesized L1, 16 条件 a-p, byte-sync sha 41d51c79d9965a0c size 11178, dsgao x8v81 hfeg0pkn001 mc=0; 选料: 清 #407 DEBT:1 → eda_flow open_session(hfhds201) → ssh hfeg0pkn001 scp 1793945103405_x8v81/1793945103405_x8v81.messages.json(391KB/82msgs) → 完整深读 3 任务链：①U0「drcpa...R_trimEqOff 和 drcoa...R_trimEqOff 有区别吗，为什么后仿真 delay 有差异」A-grade seed✓(表达目标未给修复→采纳为 prompt) ②U26/U45/U53 GidlAryCtrl testbench 修改+验证(另一独立链,未采纳) ③U69 R_tOCTrim pair 对比(A-grade seed→采纳为隐藏 B) → 助手 gold( idx=25): 两 netlist 共享全部 stdcell(invDS/invDSx1/mx2LVSx2/dlyg*of8*)，顶层 R_trimEqOff 的 trim 选择通路 drcoa 多 1 级 invDSx1(XI13: trimN→trim)，drcpa 仅 XI7 → delay 差异来源 = 多 1 级反相器；⚠️ 资产获取阻塞：/rundata/drcpa_sim、/rundata/drcoa 归属 cadmin:drcpa，e0031982 无读权限且无 sudo → 无法取真实 netlist → 采 B-grade synthesized(trace_source 真实 x8v81，assets 合成但忠实复刻 trace 结构差异模式) → 合成 A pair(drcpa_R_trimEqOff 111 行 / drcoa_R_trimEqOff 119 行，drcoa 含 XI13<0>/<1> 额外 invDSx1 + 3 额外 XI_switch) + hidden B pair(drcpa_R_tOCTrim 154 行 / drcoa_R_tOCTrim 156 行，drcoa XI18 dlyg2→dlyg0 / XI25 dlyg4→dlyg6 / XI30 dlyg4→dlyg6 + XI29<0>/<1> 额外 invLx2) + prompt.txt(逐字 U0 原文) + task_brief.md(交付接口≤3 行) → ref analyze_netlist_diff.py(读两 netlist→parse_header/parse_subcircuits/parse_top_level_instances/diff_instances/delay_finding/diff_hunk_count→report.json) → check.py 16 条 a-p(a zip+analyze_netlist_diff.py / b py_compile / c B-run exit0+report.json / d 7 必需顶层键 / e file_line_counts==B 实际 / f Date 左右不同 / g TopDesign 左右不同 / h subcircuits.shared>=3 / i left_only+right_only 为 list / j added 含 XI29 / k changed 含 XI25 / l changed 含 XI30 / m changed 含 XI18 / n delay_relevant_finding 非空+>=2 delay 关键词 / o 3-seed md5 一致 / p 反硬编码 A finding≠B 且 A 含 XI13 不含 XI25)；自验: ref_submit.zip PASS 16/16 + negative_selftest 4 neg FAIL distinct{c,d,h,p} NEG_RC=0(print_expected→c / empty_shell→d / core_deleted→h / always_trim_inv→p) + §4.9 三假 empty_shell→d / print_expected→c / core_deleted→h 全 FAIL distinct / 断言闸门 16==16≥8 ✓ / byte-sync jsonl test sha 41d51c79d9965a0ced6ad5bdb1c76d888ad9ee382eba8b0bbbe17161c488140a == 磁盘 check.py 11178B ✓ / 追加 D.jsonl(427→428, id=EDA-Eval-DesignFlow-TrimMuxInvDiff-001) → ledger_D x8v81 mark --status case；eda_flow close_session(keep=false) 释放；⚠️ B-grade 而非 A-grade 因资产获取权限阻塞(非意图降级)；无新 PII(prompt 含真实路径/proj/drcpa/.../dsgao/...但按 red line #2 保留原值，仅 key/token 掩码——本 prompt 无 key/token) / EDA-Flow-Bench 新增 assets+reference(4 netlist + prompt + task_brief + hidden_manifest + check.py + ref + 4 neg + negselftest + ref_submit.zip) / D.jsonl 追加 1 行; research 日报 11-08 designflow 建议(benchmark maintenance debt+资源预算)与本轮 case 交付无直接可执行条目(rewrite_queue 15/15 done，本 case 已含 cond o 3-seed + cond p 反硬编码)，按常驻令忽略; WAITING: 0) — 本轮新增，未归档
- 流水 #407 (dup-fix + post-summary fresh scan + claim x8v81 · DEBT:1 下轮必先交付; 选料: trace_ledger --shard D next → mc≥15 fresh 枯竭(#399-#406 八轮确认) → 本轮改走 post-summary ssh 扫描(summary.tsv 11-05 已 3 天陈旧)：eda_flow open_session(hfhds201) → .75 本地 mtime<4d scan → 26 recent sessions → ssh 5 remote hosts(hfeg0pkn001/2/3/4 + hfeg0pnd002) mtime<3d find → 47 fresh sessions not in summary.tsv → 本地 cross-ref 4 shard ledgers(check_sids.py 提取 5-char sid regex) → 真正不在任何 ledger 的 D-domain seeds 仅 3：x8v81(dsgao,netlist compare+fix,schematic_netlist)/h12nr(mike,sub_schematic script dev)/262wq(allenzh,HSPICE debug)；其余 D-domain 候选 kk5tf/lywbf/ezcgh/h2sri=shard B 已 case(跨 shard dup)；2ka5p(e0030760 SPICE testbench WSNM/Iread/Iwrite/Ileak 检查)=D ledger parked(unfit,2026-11-05)；同期修复 #406 数据质量问题：#406「孤儿采纳」实际是 case-sensitivity bug(大写 VrefCSMRRSeq-001 vs 小写 VrefcsMrrSeq-001 line 237 已存在)→ 移除 D.jsonl line 428(大写重复行,428→427)→ cell_rewrite_simlib/SpfNtsvMissingDiag 也非真孤儿(已在 B/D jsonl)；peek x8v81: 2.06MB/390msgs,U0 逐字「drcpa_digital_R_trimEqOff_schematic.netlist 和 drcoa_digital_R_trimEqOff_schematic.netlist...fngidl 要恒为vwlp」A-grade seed✓(表达目标未给修复) → claim x8v81 → partial deep-read note → DEBT:1 下轮完整深读+合成+自验+追加; eda_flow close_session(keep=false) 释放; 🚫 0 case 落 jsonl(本轮为选料+dup-fix,非 case 交付)；✅ x8v81_netlist_compare_fix.md 深读笔记; ledger_D 新增 x8v81 claimed(无 mark case); research 日报 11-08 designflow 建议(benchmark maintenance debt+资源预算)与本轮 dup-fix+fresh scan 无直接可执行条目(rewrite_queue 15/15 done),按常驻令忽略; 无新 PII / D.jsonl 移除 1 行(428→427) / 无动 EDA-Flow-Bench assets+reference; WAITING: 0) — 本轮新增，未归档 · 交付 EDA-Eval-DesignFlow-VrefCSMRRSeq-001, analog_context A-grade faithful L1, 16 条件 a-p, byte-sync sha f027f63b size 17237, t0002470 42jk5 10.129.2.13 mc=363; 选料: #399-#405 七轮 mc≥15 fresh 枯竭 → 本轮改走真孤儿扫描(assets+reference 双存且不在任何 jsonl)；修前两轮 orphan-detection bug(读错 id 字段 case_id→实际 id；前缀双形匹配 EDA-Eval-DesignFlow-X / X)得 6 真孤儿{VrefCSMRRSeq,SpfNtsvMissingDiag,cell_rewrite_simlib,ThkOxIdvgVthCheck,DrcQaDiffReport,FeintFlowAudit} → 按 ledger 归属筛掉 DrcQaDiffReport(=C)/FeintFlowAudit(=A)/ThkOxIdvgVthCheck(=shard B 明文) → 完整性筛掉 SpfNtsvMissingDiag(缺 negative+negselftest+refsubmit)/cell_rewrite_simlib(无 ledger，需重建 trace_source) → 唯一完整+ledger_D 拥有=VrefCSMRRSeq → 采纳；trace=42jk5(t0002470@10.129.2.13,mc=363,analog_context,ledger_D 已 mark case 2026-11-05)；prompt=逐字用户「你能否从/proj/drcoa/V0/simdir/verilog/ydhe/verilog.ddr5.drcpa.aicov/patterns/analogsim目录下找到VrefCS到MRR的连续序列」(clean 提需求，未指出根因→A 档 faithful seed ✓)；check.py 16 条 a-p(a zip+find_vrefcs_mrr.py / b py_compile / c B-run exit0 / d 顶层键 / e B total==6 / f by_file 逐文件相等 / g 序列字段齐全 / h (file,vrefcs_op) 对集 / i mrr_ma 集 / j 中间件∈{MPC,Deselectn} / k 直连 VrefCS→MRR ma='d18 / l [MPC] ma='d22 / m [MPC,Deselectn] 校准序列 / n 013→0 序列(EOF 截断) / o 跨输入守卫 A-run total==4 + 051 ma='d26 + 052 ma='d12 / p 3-seed 子集确定性)；hidden B=check.py 内嵌 B_CONTENT(8 文件名同 A，op/ma/loop/中间件全不同)；自验: negative_selftest ref PASS 16/16 + 4 neg FAIL distinct{c,o,e,e} NEG_RC=0 / §4.9 三假 empty_shell→c / print_expected→o / core_deleted→e 全 FAIL distinct / 断言闸门 16==16≥8 ✓ / byte-sync jsonl test sha f027f63b30acdd91bb0a78f60e9cf78f3a37092c04613f7087e1be690011c092 == 磁盘 check.py 17237B ✓ / 追加 D.jsonl(427→428, id=EDA-Eval-DesignFlow-VrefCSMRRSeq-001) → ledger_D 42jk5 已 mark case(2026-11-05，case-id 大小写差异 VrefcsMrrSeq vs VrefCSMRRSeq，jsonl 以 assets 目录名 VrefCSMRRSeq 为准)；⚠️ ledger_D 42jk5 有两行(一行全字段 20:06 + 一行空 user/host 19:56)历史 dup，未清理；无新 PII / 无改 EDA-Flow-Bench assets+reference(孤儿已存在) / 仅 D.jsonl 追加 1 行; research 日报 11-08 designflow 建议(benchmark maintenance debt 可见化 + 资源轴纳入判分)与本轮孤儿采纳无直接可执行条目(本 case check.py 已含 cond p 3-seed 确定性 + cond o 跨输入守卫，资源轴待被测实跑时再记)，按常驻令忽略; WAITING: 0) — 本轮新增，未归档
- 流水 #405 (选料复核轮 0 case · DEBT:1 hfhds201 cron-blind-spot 扫描确认枯竭; 选料: 复刻 shard B 13:47 找到 bqszj 的同一 productive 路径 — eda_flow open_session(hfhds201) → scan_D405.py os.walk `/home/*/.cline/data/sessions/`(.75 本机无需 ssh) → 270 sessions → 筛 mtime≤45d → D-domain 关键词(STRONG_D: fsdb/waveview/verdi/wv_/sx_/sw0/_wdf/subckt/.cdl/.spi/schEdit/abMatch/guardring/analogContext; SIM_KW: measure/hspice/finesim/primesim/spectre/tran/dc/ac/sp; WRONG: verilog/sdc/sta/primetime/innovus/calibre/lvs/drc/svrf/pnr/floorplan) → 命中 STRONG>0 OR (SIM>0 AND WRONG==0) → 88 D 候选 → read_file 回本地 → diff all-shard ledger(1805 sids, _excl_D405.json) + seed peek 分析(并发 run_commands python 解析首 3-5 user 轮): ①FineSim DC-non-convergence dup cluster ~20(全同「Finesim仿真报DC不收敛」→ shard B uky6c) ②sine/cosine WaveView Tcl dup cluster(e0023936,~5: yrvv2 65msgs sine→cosine / km0sb 1msg sine / g8ory 50msgs sine / p5x6n cosine / bqszj cosine=shard B CosineWaveAnalyze-001) 全同用户同任务→跨 shard dup ③hi/who-are-you non-seed ~8(z3212/nwl1p/gbjzx/z34dy/nt0pl/pl82z/x4y2u/oau5r/e179o) ④license/env 排障 ~3(18m80 Verdi license / rkdu8+0t51l mmsim.ini 记路径) ⑤explain-script Q&A(n5hh7 tongfanl 34msgs「dumpFSDB.pl 作用」→「fsmchk 在干啥」→…纯解读无交付) ⑥agent 自测(y6sbk user=e0031982「WaveView 打开 input.fsdb」重复) ⑦role-prompt meta(uozyg e0023936 39msgs「你是精通 WaveView ACE Tcl 文档工程师」meta+dup 用户) ⑧compacted-summary non-seed(q9bnb/iuhvu/08aia) ⑨已 IN-LEDGER 6(qb1ua FM Tcl / hsizo netlist→finesim ignore / kwiij sim result grep / 68gc9 primesim compare / 3l3yx primesim CRC / p5x6n cosine) → 0 fresh D synthesizable seed; eda_flow close_session(keep=false) 释放; 🚫 0 case 落 jsonl(不越 shard/不造低质/不判分歧义/不新增跨 shard dup); ✅ 选料复核记录 designflow/r405_selection_round_D.md; ledger_D 无新增(无 claim/mark); research 日报 11-08 designflow 建议(benchmark maintenance debt+资源预算)与本轮 pool-exhaustion 阻塞无相关可执行条目(rewrite_queue 15/15 done)，按常驻令忽略; 无新 PII / 无改 jsonl / 无动 EDA-Flow-Bench 仓; WAITING: 1 等人工(rescan/orphan 再分配)) — 本轮新增，未归档
- (归档批次 2083) 流水 #404 (选料复核轮 0 case · DEBT:1 三路径全枯竭需运维; 孤儿 5 全 A/B/C / parked+deepread 仅 t0aom=shard B / 11-08 fresh ssh 12 host 0 fresh D seed) 全文已搬 MEMORY_D_archive.md
- (归档批次 2083) 流水 #403 (交付 EDA-Eval-DesignFlow-OpenWaveFmt-001, waveform A-grade faithful L1, 16 条件 a-p, byte-sync sha c1ef37d5, rongjiez 7fcir hfeg0plg98 mc=16; 孤儿采纳破局) 全文已搬 MEMORY_D_archive.md
- 流水 #402 (交付 EDA-Eval-DesignFlow-PrimeLibFlowAnalyze-001, schematic_netlist A-grade faithful L1, 16 条件 a-p, byte-sync sha c64bc9b7 size 5401, johnl cr42l hfeg0pkn001 mc=43; 选料: trace_ledger --shard D next → 复用已有深读 designflow/trace_deepreads/cr42l_primelib_flow.md(11-08 10:51, USER#0 逐字「帮我看下这里的k库流程是怎样的」A-档 seed, gold=assistant IDX20 流程分析 5 步: prepare→bsub→primelib→validate→LC) → claim cr42l → eda_flow open_session(fetch) ssh hfeg0pkn001 cat 16 真实 A 文件(README/cells.txt(93)/config/project.json(library=stdcells_ac,corner=SS_0p98_m40c)/primelib/char_all_comb.tcl/scripts×10) → 合成 spec-driven A-档 faithful L1: candidate 写 analyze_flow.py 读任意 PrimeLib 工程目录→JSON; 隐藏 B=iolib_io_project(合成 library=iolib_io/corner=TT_1p1_25c/15 IO cells/vcc=1.1/temp=25/slew_lower=20%, 全不同于 A); check.py 16 条 a-p(含 o 反硬编码 + p 3-seed 确定性); 自验: ref B-run library=iolib_io/cell_count=15/7 steps ✓ / ref A-run library=stdcells_ac ✓ / check.py PASS 16/16 / 4 neg FAIL distinct{b,o,h-n,c} NEG_RC=0 / §4.9 三假全 FAIL / 3-seed md5 一致 / A-only 泄漏闸门 0 ✓ / 断言闸门 16==16≥8 ✓ / byte-sync sha c64bc9b7 size 5401 ✓ / 追加 D.jsonl(221→222) → mark --status case; WAITING: 0) — 本轮新增，未归档
- 流水 #401 (交付 EDA-Eval-DesignFlow-SramButterfly-001, analog_context B-grade L2 faithful, 16 条件 a-p, byte-sync sha 01a90649 size 19800, e0030760 gnmu0 hfeg0pkn002 mc=102; orphan-adoption 破局: #399/#400 后 shard D mc>=15 fresh 真实枯竭 → 扫描 EDA-Flow-Bench assets/+reference/ 完整孤儿(已建好未落 jsonl) → 修两 bug(dir-name 前缀不匹配 / jsonl id 字段 task_id 或 id)后真完整孤儿仅 4 个(DrcUnusedVarClassify/FeintFlowAudit/InnovusProjLogDiag/SramButterfly), 仅 SramButterfly D-domain → 关键反转: daily_B「SramButterfly-001 不可用(沙盒无 HSPICE)」STALE, 实测 .75 有 hspice V-2023.12-SP1-1 + anaconda py3.8.8/numpy1.24.2 → 采纳 gnmu0(e0030760 U[28]「仿真SRAM 蝴蝶曲线试一下」A-档 seed, 深读 1793155079677_gnmu0_sram_butterfly_snm.md, GT SNM 0.306205/0.436626, level-1 Shichman-Hodges, 45°-rotated inscribed-square SNM); .75 HSPICE 标定 ref A SNM=0.3062053==expected / B SNM=0.4366261==expected / hspice_ok=true n=101; check.py 用 env -u PYTHONPATH anaconda py3.8.8 跑(walrus := 默认 python3.7.1 SyntaxError) → packaged ref submit.zip PASS 16/16; negative_selftest 7/7 FAIL NEG_RC=0 first_fail {c,e,f,g,h,i,j,k,m,n} distinct / §4.9 三假 naive_empty→c naive_print_expected→k naive_max_width→j 全 FAIL distinct; 断言闸门 k_rationale(①..⑯)=16=k_check(a-p)=16≥8 ✓ test_rationale `16 条断言：①…`; byte-sync jsonl test sha 01a9064918e79f913167fbc30830c784a3b8eb041a4a72b0c7c08633368ed915 == 磁盘 check.py 19800B ✓ 无重复; 追加 D.jsonl(220→221 task_id 字段) → mark --status case(ledger_D case 218→219, session 1793155079677); eda_flow session close_session(keep=false) 释放; 无新文件写入 EDA-Flow-Bench(仅 D.jsonl 改动, 孤儿 assets/reference/check.py 已在盘); #376 PII: jsonl 走内网 devops, MEMORY 按 red line #2 含真实标识符进 foamliu; WAITING: 0) — 本轮新增，未归档
- 流水 #399 (选料筛选轮 0 case · DEBT:1 pool exhaustion; 经 trace_ledger --shard D next → .75 eda_flow run_commands python 提取 mc>=30 shard-D-tool 候选 1168 unique → 本地 excl_D.txt(1291 台账 anchor)对账 top42 mc592~1627 全在台账; 降阈 mc15-29 得 208 fresh(按 waveform-affinity+非饱和用户打分); scp 21 条 messages.json 到 .75 workdir peek 首 2-3 user 轮: r3gb7=RTL synthesis(wrong-shard) / 05p8p=Virtuoso 连接排障(non-seed) / ve67l=执行 README(non-seed) / kzlkh=DRC testpattern(wrong-shard C) / pj0ax=rscalc RTEXT==RsCalcChk-001(dup) / 09kkp+55ms0+soqbk+53n4v=e0014566 powerfill/rscalc meta+debug+dup / jq7tt=dspf arg debug / ms1ia=connect workspace / 6g756=电路分析 Q&A / 0p3qp=Finger Crossed Q&A / 0wjop=input Chinese / hu27g=log debug / ny0i=教程 Q&A / q7jyk=翻译 / uhxqp=部署 agent meta / vagnh=synthesis dc.log debug(wrong-shard) / lcg3v=siliconSmart char hspice debug(borderline spice_sim) → 全 non-seed/wrong-shard/dup; mark --status parked 20 条(1043→1063); 写 r399_selection_round_D.md; 无新 case / 无改 jsonl / 无 PII; 关键发现: mc>=30 fresh 池对 shard D 真实枯竭, e0014566 fresh 残余全 rscalc/autovia/powerfill 重题, 11-05 scan 已 3 天陈旧; r400 第一件事=触发 .75 rescan + 降阈拓展新用户 host, 必须交付 1 case; ⚠️ 未碰 shard B 在飞 WtmWriteArrayScope-001(xd7ut, spice_sim); WAITING: 1) — 本轮新增，未归档
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
