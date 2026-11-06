WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

- **PHASE**: shard D 运行中。已交付 153 条 case（D.jsonl 153 行）；台账 case-mark 152 + 890 parked = 1042 已动过。**本轮 #315 = FmInstFreq-001 已交付**（次选 4ne3u claim+深读→合成，waveform, track=synthesized B-grade, L1 stub-harness 真跑候选, 16 条件 a-p）。4ne3u trace 不完整(agent search_codebase 超时中断,无 user-accepted 产物)→不做 A-faithful,改 B-grade synthesized(prompt 仍用 U#1 逐字)。下轮续 peek fresh_D306 rank 206+。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：152 / 1511 = 10.1%（mc>=30 候选池；D.tsv 现 152 case-mark + 890 parked · 已动过 1042；快照 2026-11-06 08:40 sessions=3896）。已覆盖 domain（D.jsonl 153 行）：analog_context:33 · schematic_netlist:83 · waveform:37。⚠️ **#315 选料**：次选 4ne3u(e0023936@10.129.32.75 mc44)已 claim+深读+合成交付。fresh_D306_pool.tsv(262 fresh) rank 206+ 仍剩 ~57 未 peek，下轮续。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈16KB（归档批次 2027 后；低于 32KB 红线）
- DEBT: 0（#314 DlygResInsert-001 已交付，DEBT 清零；fresh_D306 pool rank 206+ 仍剩 ~57 未 peek 下轮续）
- 🧾 断言: k_rationale=k_check=16 ✓（本轮 #314 DlygResInsert-001 16 条断言 ①-⑯ 对应 check a-p 全；#313 NetlistSigRename-001 16 条；#312 NetlistHierFlowchart-001 16 条；#311 CdlXistorAudit-001 16 条；#310 NetlistCellReplace-001 16 条；#309 NetlistGate2Verilog-001 16 条；#308 CellRewriteSimlib-001 16 条；#307 OpCornerSummary-001 15 条；#306 FarthestCellPick-001 14 条；#305 SpStimLoopAudit-001 16 条；#304 SimReportPvtSummary-001 15 条；#303 WaveMaxFind-001 15 条；#302 SpTestbenchParamFix-001 14 条；#301 NetlistMMultAudit-001 16 条；#299 SineZeroCrossFreqPeak-001 16 条；#298 InvPulseStimTb-001 14 条；#297 SpiceldViewChg-001 14 条；#296 FinesimIgnoreGen-001 14 条；#295 CosimStimFolderGen-001 14 条；#294 CellExpandGen-001 14 条；#293 SchFixFloating-001 14 条）。shard D 存量 152 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。今日 108/152 达标。rewrite_queue.tsv 全部 done（无待修）。

## 流水
- 2026-11-06 17:3x | shard D #315 | **交付 FmInstFreq-001（waveform, track=synthesized B-grade, L1 stub-harness 真跑候选, 16 条件 a-p）**。open_session shardD_20261106_shardD-pick315。**选料**：复用 #314 次选 4ne3u(e0023936@10.129.32.75 mc44, waveview:273)→claim。**深读 4ne3u**：28 msgs/2 user_input。**U#1 逐字**(唯一 A-faithful produce)「编写一个 Tcl ACE 脚本，计算 FM 信号瞬时频率…6 条编号要求：proc f_vs_t(sig,v_thr)→创建 frequency analog 波形→RISE 扫描设阈→遍历上升沿 f=1/(t2-t1)→追加(t2,freq)→主序开 ./wave.dat 取 wave 调 f_vs_t」(纯提需求→A-faithful task)。agent 工具链：run_code tcl hello(热身)→search_codebase/RAG search_apis 全超时→list_allowed_files/read_files waveview-fsdb-reader 技能脚本→search_codebase 6 查询全 30s 超时→**trace msg 27 中断，无最终产物，用户未接受**。⇒ **无 user-accepted 金标→不做 A-faithful，改 B-grade synthesized**(prompt 仍用 U#1 逐字，track=synthesized 诚实标记)。**WaveView ACE API 调研**(pyAether search_apis/get_api_details 实测)：sx_open_sim_file_read/sx_current_sim_file/sx_find_wave_in_file/sx_create_signal(ANALOG 0)/sx_add_wave/sx_set_threshold/sx_create_scan RISE/sx_scan_data_points/sx_scan_first+sx_scan_next 遍历/sx_scan_jump/sx_jump_to_x/sx_x_value/sx_y_value/sx_append_data/sx_new_wv(批处理返回 NULL!)/sx_display_wave。**关键坑**：sx_new_wv 批处理返 NULL→显示须 `if {$wv ne "NULL"} {catch {sx_display_wave}}` 守护。**合成策略**：trace 无产物+真实 FSDB 不可合成→**离线 Tcl 桩模拟器**真跑候选。wv_stubs.tcl 模拟全部 sx_* 用 config.tcl EDGE_TIMES 喂假上升沿时间(sx_x_value 返 EDGE_TIMES[idx], sx_scan_first/next 遍历)，每 API 调用+sx_append_data (x,y) 写 RECORD；harness.tcl source config→stubs→candidate→dump RECORD；check.py 跑 A/B/B2 解析 RECORD 断言候选用对 API 且 y==1/(t2-t1)。**反硬编码三轴**：B/B2 EDGE_TIMES 与 A 不相交(硬编 A 输出者 B count/值不符→m/n FAIL)+候选须真调 scan 遍历读 sx_x_value(g 拦截跳过 scan 的硬编)+源码无 A 专有字面量(o)。**A**={1e-9,3e-9,6e-9,1e-8,1.5e-8,2.1e-8}6→5 频点 THR0.5；**B**={2e-9,5e-9,9e-9,1.4e-8,2e-8,2.7e-8,3.5e-8}7→6 频点 THR0.3；**B2**={5e-10,1.5e-9,3e-9,5e-9,8e-9}5→4 频点 THR0.7。金标 fm_freq_ref.tcl：f_vs_t→create_signal frequency ANALOG 0→set_threshold→create_scan RISE→scan_first 循环 scan_next，x_value 得 t1/t2，dt>0 freq=1.0/dt，append_data $freq_sig $t2 $freq；main open wave.dat→find_wave wave→f_vs_t 0.5→new_wv 守护 display_wave→close。**16 条件 a-p**：a zip 含.tcl 无禁 import/路径 b tclsh source 无错(桩 unknown 兜底) c proc f_vs_t 恰2参 d 创建 frequency analog e set_threshold f RISE 扫描 g 扫描遍历(scan_first+scan_next) h A append 数=N-1 且 y≈1/(t2-t1) i append x==t2 j 主序开 wave.dat k 主序取 wave l new_wv+display_wave m 跨输入 B append 匹配且与 A 不同(反硬编) n 跨输入 B2 append 匹配 o 源码无 A 字面量 p 确定性3次哈希一致。**自验**：ref PASS 16/16；6 negative 全 FAIL(empty_shell/print_expected/ref_core_deleted+naive_first_only/naive_wrong_formula/naive_fall_scan)NEG_RC=0；§4.9 三假全 FAIL；确定性 3 次 PASS；test==disk sha e0b65b76412e688addbea8b3ba632cc7efcb3e76c4b4fb62b9f196ed44630a84 GATE PASS k=16。台账 mark 4ne3u→case；waveform 36→37；D.jsonl 152→153。**教训**：(1) **trace 不完整(无 user-accepted 产物)→不做 A-faithful**：金标缺失只能 B-grade synthesized，prompt 仍可用 U#1 逐字，track=synthesized 诚实区分；(2) **WaveView 批处理 sx_new_wv 返 NULL**→显示须 catch 守护，金标应守护；(3) **离线 Tcl 桩模拟器是 waveform L1 真跑候选好范式**：sx_* 全桩+EDGE_TIMES 喂假数据+RECORD 录调用→tclsh subprocess 真跑，避开合成 FSDB 死结；反硬编码靠 B/B2 不相交 EDGE_TIMES；(4) **search_codebase 超时是 4ne3u trace 中断真因**：agent 卡 API 搜索非能力不足，A-faithful 难度可能被工具可用性稀释，判据需区分"①交付形态错 vs ③能力不足"。**下一步**：下轮续 peek fresh_D306 rank 206+（~57 fresh 未 peek）。
- (归档批次 2028) 流水 #314 (DlygResInsert-001) 已搬 MEMORY_D_archive.md
- 2026-11-06 17:1x | shard D #314 | **交付 DlygResInsert-001（schematic_netlist, A-faithful, B-grade synthesized, L1, 16 条件 a-p）**。open_session shardD_20261106-shardD-pick314。**选料**：复用 fresh_D306_pool.tsv(262 fresh)→peek rank 186-205 共 20 候选(peek.sh 经 .75 ssh 串行 reader.py 20 候选)。**reader.py 关键修复**：cline messages.json 顶层是 dict{messages:[...]}，user 文本包在 `<user_input mode="act">...</user_input>` 标签内（content list type:text）；首版 reader 把 `<` 开头文本滤掉致 UTURNS=0→改正则 `<user_input[^>]*>(.*?)</user_input>` 提取。逐条审 20 候选：krjo2/mxaca=「启用 skill 打pin报错」诊断·tjzn5=研究环境+查文件问题+skill 怎么用(Q&A)·hn72n=怎么看模型 Q&A·h0gyt=教工作流总结文档(多轮教学非单 produce)·9lbfz=解析脚本+优化建议(analysis)·2igp1=Qt C++ 改 mainwindow(非 shard D)·hojhc=仿真慢找根因(诊断)·a8164=脚本要哪些参数 Q&A·7xqp9=skill-creator 元工作(非 netlist)·97g9m=分析 fsdb 信号(analysis)·8o8qn=找路径+对比文件+解析模块(Q&A/analysis)·znyhe=「启动业务场景」skill 触发·wdnwl=LVS 没过为什么(诊断)·oh3te=autocell 生成 gds(layout 非 shard D)·c39j4=抽激励报错看原因(诊断)·po6m1=ae-auto-placement(layout 非 shard D)·n1b1u=查看 ERC 怎么执行 Q&A。**clean A-faithful produce-task = cq860**★(thomasz@10.129.2.11 mc44, netlist:66 .cdl:30) + **次选 4ne3u**(e0023936 mc44, U#10 WaveView Tcl FM 瞬时频率, waveform, 备用下轮)。**深读 cq860**：50 msgs/4 user_input turns。**U#9 逐字**(唯一 A-faithful produce)「现在需要你把代码写入test.py...捕捉dlyg开头的文件...软链接先copy本地删软链接...加 R_mid mid mid_sw 0.001 / R_out out out_sw 0.001 两行到 .ends  dlyg2s2a 行之前...大小写不敏感...ends 可能是 .end...三种后缀 .spf_RC/.cdl.spf/.cdl...打印处理了多少个文件以及运行时间」(纯提需求未给根因/修复→A-faithful)。U#27「中文注释换英文」/U#48「取脚本名」为细化非 produce 忽略。agent 受 policy-engine writableRoots 限制逐块 editor 写 /home/thomasz/.cline/scripts/data/test.py：replace_symlink_with_real_file(读 target→写本地→os.unlink) + process_file(正则 `^\s*\.ends?\b` IGNORECASE 取**最后一个**匹配作为顶层结束行→在其前插入 2 行) + main(遍历 sorted(listdir) 过滤 dlyg 前缀→处理→打印 "Processed N file(s) in X.XXXs")。**合成**：真实 /proj/ddgoa 网表目录不可附加→B-grade synthesized。**核心难度**：(1)**last .ends/.end 匹配**(顶层 vs 子电路 .ENDS)naive 取首个会错插子电路结束前；(2)大小写不敏感 .ENDS/.End/.end；(3)三后缀过滤 .spf_RC/.cdl.spf/.cdl(endswith 任一)；(4)软链接转实体(read target→write local→unlink)；(5)**数据驱动反硬编码** prompt 贴 A 的 dlyg/R_mid/R_out，task_brief 要求读 config.json{prefix,insert_lines,suffixes}，B/B2 不同 prefix/lines/suffixes 测泛化。金标 dlyg_insert_res_ref.py(CLI `<config.json> <directory>`)：load_config→遍历 sorted(listdir)→过滤 prefix+suffix+isfile/islink→replace_symlink_with_real_file→process_file(last .ends? IGNORECASE, insert before)→print "Processed N file(s) in X.XXXs"。A=config_A.json(dlyg/[R_mid,R_out]/[.spf_RC,.cdl.spf,.cdl])+netlists_A(7 文件含 symlink+子电路 .ENDS+顶层 .ENDS/.End/.end/bare+混合大小写+README/dlyg2b.txt/test.py 非匹配)+prompt.txt(U#9 逐字)+task_brief.md。hidden B=config_B.json(invgx/[C_load,R_drv]/[.spf_RC,.cdl,.spi])+netlists_B(7 文件+2 symlink+invgx2z.txt 错后缀+README/helper.py 非匹配)。hidden B2=config_B2.json(ampz/[L_match]/[.cdl.spf,.spf_RC])+netlists_B2(5 文件+1 symlink)。**反硬编码三轴**：prefix 不相交(dlyg/invgx/ampz)+insert_lines 不相交(R_mid,R_drv / C_load,L_match)+suffixes 组合不同(.spf_RC,.cdl.spf,.cdl / +.spi / .cdl.spf,.spf_RC)。**16 条件 a-p**：a zip 含 .py 无禁 import+无 /proj /rundata /home 路径 b py_compile c B run exit0+非空 d stdout 含 Processed N file(s) in X.XXXs e B 所有 invgx+匹配后缀文件被插 2 行+非匹配未动 f B 软链接转实体(非 link+原 target 首行保留) g 插入块在最后 .ends 前(插入后 .ends 紧随块, blocks[0]+ni_count==last) h 每文件仅 1 块+中间子电路 .ENDS 前不插 i 大小写不敏感 .ENDS/.End/.end 全识别 j .ends 后 cell 名保留 k 反硬编码 A 重跑产 R_mid/R_out+源码无 B 字面量(invgx/C_load/1e-12/out_gnd/R_drv) l 跨输入 B2 产 L_match+源码无 B2 字面量(ampz/L_match/1e-9) m CLI sys.argv/argparse+缺参非零退出+无硬编码 config 路径 n 确定性 3 次重跑 sha256 一致 o 后缀过滤 invgx2z.txt 不被处理 p .end(非 .ends)变体识别。**修一个 check bug**：(g) 首版用 `blocks[0]==last` 比较但插入后 .ends 行下移 ni_count 行→改 `blocks[0]+ni_count==last`。**自验**：ref PASS 16/16；13 negative 全 FAIL(empty/syntax_err/no_output/print_expected_B/hardcode_a/first_ends_only/no_symlink_handle/no_suffix_filter/case_sensitive/wrong_position/ref_core_deleted/no_cli/nondeterministic)NEG_RC=0 NEG_SELFTEST PASS；§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL；test==disk sha c01ae2ceedc2 GATE PASS k=16。台账 mark cq860→case；schematic_netlist 82→83；D.jsonl 151→152。**教训**：(1) **网表批量插电阻(last .ends 前)是 schematic_netlist L1 可验好范式**：last 匹配(顶层 vs 子电路 .ENDS)+大小写不敏感+三后缀过滤+软链接转实体，16 条件天然丰富；(2) **A-faithful prompt=U#9 逐字**贴 dlyg/R_mid/R_out 诱使硬编码，task_brief 数据驱动 config.json，B/B2 不同 prefix/lines/suffixes 测泛化(硬编码 A 者 B 上 0 处理或错插)；(3) **check (g) 插入位置比较须算入插入行数位移**(blocks[0]+ni_count==last，非 blocks[0]==last)；(4) **cline messages.json 顶层是 dict{messages:[...]}，user 文本包在 `<user_input mode="act">` 标签内**——reader 须正则提标签内容，勿按 role:user+content.text 直取(会被 `<` 前缀滤掉)；(5) **first_ends_only negative** 是核心难度拦截器(取首个 .ends 错插子电路前)；(6) **symlink 须 fresh_copy 时重建 symlink**(os.readlink+os.symlink)否则 shutil.copy2 跟随链接变实体文件，(f) 软链接检测失效。**下一步**：下轮续 peek rank 206+（~57 fresh 未 peek）；次选 4ne3u(WaveView Tcl FM 瞬时频率, waveform)可作下轮候选。**选料**：复用 fresh_D306_pool.tsv(262 fresh)→peek rank 186-205 共 20 候选(peek.sh 经 .75 ssh 串行 reader.py 20 候选)。**reader.py 关键修复**：cline messages.json 顶层是 dict{messages:[...]}，user 文本包在 `<user_input mode="act">...</user_input>` 标签内（content list type:text）；首版 reader 把 `<` 开头文本滤掉致 UTURNS=0→改正则 `<user_input[^>]*>(.*?)</user_input>` 提取。逐条审 20 候选：krjo2/mxaca=「启用 skill 打pin报错」诊断·tjzn5=研究环境+查文件问题+skill 怎么用(Q&A)·hn72n=怎么看模型 Q&A·h0gyt=教工作流总结文档(多轮教学非单 produce)·9lbfz=解析脚本+优化建议(analysis)·2igp1=Qt C++ 改 mainwindow(非 shard D)·hojhc=仿真慢找根因(诊断)·a8164=脚本要哪些参数 Q&A·7xqp9=skill-creator 元工作(非 netlist)·97g9m=分析 fsdb 信号(analysis)·8o8qn=找路径+对比文件+解析模块(Q&A/analysis)·znyhe=「启动业务场景」skill 触发·wdnwl=LVS 没过为什么(诊断)·oh3te=autocell 生成 gds(layout 非 shard D)·c39j4=抽激励报错看原因(诊断)·po6m1=ae-auto-placement(layout 非 shard D)·n1b1u=查看 ERC 怎么执行 Q&A。**clean A-faithful produce-task = cq860**★(thomasz@10.129.2.11 mc44, netlist:66 .cdl:30) + **次选 4ne3u**(e0023936 mc44, U#10 WaveView Tcl FM 瞬时频率, waveform, 备用下轮)。**深读 cq860**：50 msgs/4 user_input turns。**U#9 逐字**(唯一 A-faithful produce)「现在需要你把代码写入test.py...捕捉dlyg开头的文件...软链接先copy本地删软链接...加 R_mid mid mid_sw 0.001 / R_out out out_sw 0.001 两行到 .ends  dlyg2s2a 行之前...大小写不敏感...ends 可能是 .end...三种后缀 .spf_RC/.cdl.spf/.cdl...打印处理了多少个文件以及运行时间」(纯提需求未给根因/修复→A-faithful)。U#27「中文注释换英文」/U#48「取脚本名」为细化非 produce 忽略。agent 受 policy-engine writableRoots 限制逐块 editor 写 /home/thomasz/.cline/scripts/data/test.py：replace_symlink_with_real_file(读 target→写本地→os.unlink) + process_file(正则 `^\s*\.ends?\b` IGNORECASE 取**最后一个**匹配作为顶层结束行→在其前插入 2 行) + main(遍历 sorted(listdir) 过滤 dlyg 前缀→处理→打印 "Processed N file(s) in X.XXXs")。**合成**：真实 /proj/ddgoa 网表目录不可附加→B-grade synthesized。**核心难度**：(1)**last .ends/.end 匹配**(顶层 vs 子电路 .ENDS)naive 取首个会错插子电路结束前；(2)大小写不敏感 .ENDS/.End/.end；(3)三后缀过滤 .spf_RC/.cdl.spf/.cdl(endswith 任一)；(4)软链接转实体(read target→write local→unlink)；(5)**数据驱动反硬编码** prompt 贴 A 的 dlyg/R_mid/R_out，task_brief 要求读 config.json{prefix,insert_lines,suffixes}，B/B2 不同 prefix/lines/suffixes 测泛化。金标 dlyg_insert_res_ref.py(CLI `<config.json> <directory>`)：load_config→遍历 sorted(listdir)→过滤 prefix+suffix+isfile/islink→replace_symlink_with_real_file→process_file(last .ends? IGNORECASE, insert before)→print "Processed N file(s) in X.XXXs"。A=config_A.json(dlyg/[R_mid,R_out]/[.spf_RC,.cdl.spf,.cdl])+netlists_A(7 文件含 symlink+子电路 .ENDS+顶层 .ENDS/.End/.end/bare+混合大小写+README/dlyg2b.txt/test.py 非匹配)+prompt.txt(U#9 逐字)+task_brief.md。hidden B=config_B.json(invgx/[C_load,R_drv]/[.spf_RC,.cdl,.spi])+netlists_B(7 文件+2 symlink+invgx2z.txt 错后缀+README/helper.py 非匹配)。hidden B2=config_B2.json(ampz/[L_match]/[.cdl.spf,.spf_RC])+netlists_B2(5 文件+1 symlink)。**反硬编码三轴**：prefix 不相交(dlyg/invgx/ampz)+insert_lines 不相交(R_mid,R_drv / C_load,L_match)+suffixes 组合不同(.spf_RC,.cdl.spf,.cdl / +.spi / .cdl.spf,.spf_RC)。**16 条件 a-p**：a zip 含 .py 无禁 import+无 /proj /rundata /home 路径 b py_compile c B run exit0+非空 d stdout 含 Processed N file(s) in X.XXXs e B 所有 invgx+匹配后缀文件被插 2 行+非匹配未动 f B 软链接转实体(非 link+原 target 首行保留) g 插入块在最后 .ends 前(插入后 .ends 紧随块, blocks[0]+ni_count==last) h 每文件仅 1 块+中间子电路 .ENDS 前不插 i 大小写不敏感 .ENDS/.End/.end 全识别 j .ends 后 cell 名保留 k 反硬编码 A 重跑产 R_mid/R_out+源码无 B 字面量(invgx/C_load/1e-12/out_gnd/R_drv) l 跨输入 B2 产 L_match+源码无 B2 字面量(ampz/L_match/1e-9) m CLI sys.argv/argparse+缺参非零退出+无硬编码 config 路径 n 确定性 3 次重跑 sha256 一致 o 后缀过滤 invgx2z.txt 不被处理 p .end(非 .ends)变体识别。**修一个 check bug**：(g) 首版用 `blocks[0]==last` 比较但插入后 .ends 行下移 ni_count 行→改 `blocks[0]+ni_count==last`。**自验**：ref PASS 16/16；13 negative 全 FAIL(empty/syntax_err/no_output/print_expected_B/hardcode_a/first_ends_only/no_symlink_handle/no_suffix_filter/case_sensitive/wrong_position/ref_core_deleted/no_cli/nondeterministic)NEG_RC=0 NEG_SELFTEST PASS；§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL；test==disk sha c01ae2ceedc2 GATE PASS k=16。台账 mark cq860→case；schematic_netlist 82→83；D.jsonl 151→152。**教训**：(1) **网表批量插电阻(last .ends 前)是 schematic_netlist L1 可验好范式**：last 匹配(顶层 vs 子电路 .ENDS)+大小写不敏感+三后缀过滤+软链接转实体，16 条件天然丰富；(2) **A-faithful prompt=U#9 逐字**贴 dlyg/R_mid/R_out 诱使硬编码，task_brief 数据驱动 config.json，B/B2 不同 prefix/lines/suffixes 测泛化(硬编码 A 者 B 上 0 处理或错插)；(3) **check (g) 插入位置比较须算入插入行数位移**(blocks[0]+ni_count==last，非 blocks[0]==last)；(4) **cline messages.json 顶层是 dict{messages:[...]}，user 文本包在 `<user_input mode="act">` 标签内**——reader 须正则提标签内容，勿按 role:user+content.text 直取(会被 `<` 前缀滤掉)；(5) **first_ends_only negative** 是核心难度拦截器(取首个 .ends 错插子电路前)；(6) **symlink 须 fresh_copy 时重建 symlink**(os.readlink+os.symlink)否则 shutil.copy2 跟随链接变实体文件，(f) 软链接检测失效。**下一步**：下轮续 peek rank 206+（~57 fresh 未 peek）；次选 4ne3u(WaveView Tcl FM 瞬时频率, waveform)可作下轮候选。
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
