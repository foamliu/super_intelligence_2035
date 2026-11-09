WAITING: 0（#439 交付 TempParamReforge-001 · jrjm6 ghyang@hfeg0pkn003 mc=62 · schematic_netlist B-grade synthesized L2 k=16 · byte-sync sha eb69a0ed size 10677 · D.jsonl 251→252 · ledger_D 1375→1376 case=249。选料：fresh D-domain 池 _fresh_D427_pool.json(610 行,mc>=30)本地 python 过滤(双边剥 .messages.json/.archive.json/.json 后缀,扣 4-shard 台账 1854 sids,排除 e0031982 自身,D 关键词 netlist/schematic/analog/waveview/hspice/spice/fsdb/vcd/cosmos/spectrum/spiros d_score>=5)得 183 fresh；按 d_score 排序 peek 15 候选 → 3m5t4=NO_FILE、jq6lq/bp54q=mwxi crontab sync devops(非D)、hasla=Finesim deck Q&A「给我脚本语句怎么写」(非produce)、8nqgg=nturns=0、xyqtl=nlchk 命令 Q&A 评脚本(非produce)、54h58=DRC/LVS 场景模板 generic、bih9j/w1dp0=单 turn debug、lgbx4=pvt.log .data/.enddata 但 U#2 用户给根因、8o8qn=.avc 对比+module 解析(分析向)、cw8k2=virtuoso cdl 抽取(emy2netlist,2 turn)、abico=schematic port function(2 turn)、jrjm6=ghyang「/proj/ddgoa/.../Yiotwist_corner sim*.sp 批量改造」13 turn 干净多步 produce ✓ claim。深读 jrjm6(137msgs/723KB)：U#10 复制 -40.sp 去后缀；U#22 参考 case5 复制 p1a3→p2a4 改激励；U#42 tt 文件 ss→tt；U#52/U#64 按 case5/Vcsl 模板替换 meas 段；U#78 温度参数化(.temp -40c→.temp {ptemp},删旧 .alter,加 25/45/98/130 四组温度 alter)；U#98 重写 run-all bsub；U#112 统一文件头；U#124 整合 mt0 读数据列表格；agent Python 脚本逐项完成用户多轮接受。A-faithful 金标准依赖 /proj/ddgoa 私有源树沙盒不可复刻 → B-grade synthesized：把 U#78「温度参数化 + alter 重构」抽成自包含单文件 .sp 改造任务。候选 temp_param_reforge.py <input.sp> <output.sp>：检测 .temp <X>c→改 .temp {ptemp}+保证早期 .param ptemp=<X>(已有则规范化,无则在首个 .param 后插)+从首个 .alter 到 EOF 全删+追加 4 组新温度 .alter(25/45/98/130 各 .alter+.param ptemp=T+注释)+保留 .end。A=sim_p1a3_pl3_ff.sp(corner ff,temp -40,Pattern1a3,5 组 pvcsl .alter 0.88→0.78,meas Write1/2/3/4+tCCD_w,.tran 1n 200n)；隐藏 B=sim_p2a4_pl3_ss.sp(corner ss,temp -55,Pattern2a4,3 组 pvcsl .alter 0.90/0.85/0.80/0.75,meas Read1/Read0+tCCD_r,.tran 1n 220n,dut_yio2)——corner/温度/激励/meas/alter组数/.tran 全不同反硬编码。判分 L2 subprocess 真跑候选于隐藏 B + 16 条 a-p 结构化字段断言(a zip 含 .py b py_compile c B 退出0非空 d .temp {ptemp} e 无 .temp -55c f .param ptemp=-55 g ptemp 早于 .temp h 保留 .param pvcsl=0.90 i 首个.alter后无pvcsl j 恰 4 .alter k 4 alter 依次 25/45/98/130 l meas 保留 tCCD_r1/r0/tA_r1 m .tran 1n 220n n 反硬编码 A-only token 不泄入 o 跨输入 A→out_A ptemp=-40 & .temp {ptemp} p 3-seed md5 一致)。自验 ref PASS 16/16 + §4.9 三假(empty→c/print_expected→l,0/meas缺+cross-input / core_deleted→j,0 alter)全 FAIL distinct + 2 neg(naive_no_parametrize→d / naive_hardcode_a→f)全 FAIL distinct + negative_selftest NEG_RC=0。byte-sync sha eb69a0ed size 10677。D.jsonl 251→252。🧾 断言: k_rationale=k_check=16 ✓ 今日 11-09 新 case 17/17 达标）
（#438 交付 VparamDeadAudit-001 · evxj6 xuluo@hfeg0pkn001 mc=333 · schematic_netlist B-grade synthesized L2 k=14 · byte-sync sha 84370330 size 14666 · D.jsonl 250→251 · ledger_D 1373→1374 case=248。选料：fresh D-domain mc>=30 池（cand_full.tsv top400 → dedup 273 → 扣台账 1317 sids → 77 fresh）；peek 6 候选 → llns7=NO_FILE、ebxsl=nturns=0(archive?)、ld0p8=LVS meta-skill 写作(非D)、6c7d2=cu3nb 同项目重复(sinanz FullAdder/decoder Aether 电路搭建,L3 太重)、cu3p/cu3nb=L3 多工具电路搭建 tutorial、evxj6=xuluo「分析/proj/dbcoa/.../cyclic_xyz 代码，python 参数 vs verilog 参数对比」干净分析/produce ✓ claim。深读 evxj6(293msgs/1.83MB)：U#0 用户原话「分析这个目录下的代码，这是python下对应的参数，告诉我两者参数有何不同」提需求未指根因；agent 多轮核查 rhr_parameter.pkg（tRFC=280000 死参数零引用、tRC=63 仅 loop_time 扣余量）vs rhr_driver.sv（#11.52 延时链硬编码实际时序、under2 门级链 L4484-4495）；U#29「修改 gen_paralist_sv_aligned.py 使 xyz 逻辑和 sv 一样」agent 生成 4408 行对齐生成器，U#30 用户求总结（隐式接受）。A-faithful 金标准依赖 /proj/dbcoa 私有大源树，沙盒不可复刻真值 → B-grade synthesized：把核心发现「Verilog parameter 声明但死引用 + 硬编码延时 shadow」抽成自包含单文件审计任务。候选 vparam_audit.py <vfile> <out.json>：解析 parameter/localparam 声明(名字/值/行)+refs 计数(剔除声明行,\b 词边界,剔除行注释)+classification(used/dead)+#<num> 硬编码延时(剔除//注释)+value shadow(延时字面量值==param 值)+JSON{params/hardcoded_delays/value_shadows/summary}。A=rhr_top_a.v(10 params,2 dead:T_RFC_A/NOISE_A,8 used,4 delays #5.0×2/#860/#1000,1 shadow #860==OSC_T_A)；隐藏 B=rhr_top_b.v(9 params,2 dead:tRFC_B/tRC_B,7 used,5 delays #11.52×3/#60/#440,1 shadow #60==ACT_PERIOD_B)——名字/值/计数/结构全不同反硬编码。判分 L2 subprocess 真跑候选于隐藏 B + 14 条 a-n 结构化字段断言(py_compile+exit0+四顶层键+n_params9+n_dead2+n_used7+n_delays5+n_shadows1+tRFC_B dead refs0+tREFI_B used refs>=1+#11.52 ref_dly ctx+#60→ACT_PERIOD_B shadow+反硬编码 A-only 名不泄入+4-run md5 一致)。自验 ref PASS 14/14 + §4.9 三假(empty→c/print_only→c/core_deleted→h)全 FAIL + 3 neg(naive_hardcode→i/always_empty→d/core_deleted→h)全 FAIL distinct + negative_selftest NEG_RC=0。byte-sync sha 84370330 size 14666。D.jsonl 250→251。🧾 断言: k_rationale=k_check=14 ✓ 今日 11-09 新 case 16/16 达标）
（#437 交付 VconnConsistCheck-001 · xt9ag e0045144@hfeg0pkn002 mc=301 · schematic_netlist B-grade synthesized L2 k=16 · byte-sync sha 85c8f4dc size 10344 · D.jsonl 249→250 · ledger_D 1372→1373 case=247。选料：fresh D-domain mc>=30 池（cand_all_D.tsv 1693 行）top 80 全在台账；扩到 rank 80-260 本地 python 过滤（excl 双边剥 .messages.json/.messages.archive.json/.json）得 25 fresh，多 e0014566 layout/calibre-pnr(非D)；peek 6 候选 → wp528=Calibre rule-deck 解释 Q&A(非produce)、cv0pc=DRC log 分析(/rundata 私有)、2gkvu=powerfill layout(C域)、aw9d7(8055)=NO_FILE、11fst=parked(SRAM Solido Q&A)、xt9ag=「产生 check 两份 verilog 模块间连线是否一致的脚本」干净 produce ✓ claim。深读 xt9ag(443msgs/1.3MB)：U#0 用户原话需求未指根因；agent 写 Perl check_verilog_conn.pl/cvc.pl 解析 Verilog 例化+按 module type 分组+逐 instance 逐端口比对(.port(sig) 命名连接)+输出 diff CSV(SigDiff/PortMissF1/PortMissF2)；U#256 用户给真实两份 pa_cpu_merged_top.v 比对(7 处 1'b0 vs 1'b1 SigDiff)，U#332 修改后再比对接受(剩 1 处) → A-faithful 可行；本轮做 B-grade synthesized（主题迁移到 Python vconn_check.py，结构化 JSON 报告判分，避免 Perl 编码坑）。候选 vconn_check.py <file1.v> <file2.v> <out.json>：去注释+module/endmodule 切分+例化语句正则(跳过 assign/always/wire/reg/input/output 等关键字)+.port(sig) 命名连接解析(balanced paren)+按 module type 分组+公共类型按 instance 名配对逐端口比对(PortMissF1/F2/SigDiff)+单边类型 InstCountDiff+JSON{summary/common_modules/module_types_f1_only|f2_only/diffs/per_module}。A=MemCtrl/sram_row×2+sense_amp+wl_drv+prech(5 inst vs 4, 3 diff: sram_row.addr SigDiff/sense_amp.en PortMissF1/prech InstCountDiff)；隐藏 B=SubSysTop/data_buf×2+addr_dec+clk_gate+rst_sync(5 inst vs 4, 4 diff: data_buf.u_buf1.din SigDiff dbuf1→din/clk_gate.u_gck.en SigDiff gate_en→1'b0/addr_dec.u_dec.en PortMissF1 dec_en/rst_sync InstCountDiff)——模块名/信号名/差异分布全不同反硬编码。判分 L2 subprocess 真跑候选于隐藏 B + 16 条 a-p 结构化字段断言(含两特定 SigDiff+一 PortMissF1+一 InstCountDiff+反硬编码 A-only 不泄入+相同文件优雅 n_diffs==0+3-seed md5)。自验 ref PASS 16/16 + §4.9 三假(empty→c/print_only→c/core_deleted→j)全 FAIL distinct + 3 neg(naive_hardcode→h/always_empty→e/core_deleted→j)全 FAIL distinct + negative_selftest NEG_RC=0。byte-sync sha 85c8f4dc size 10344。D.jsonl 249→250。🧾 断言: k_rationale=k_check=16 ✓ 今日 11-09 新 case 15/15 达标）
（#436 交付 HierNetTrace-001 · dnp2f junweix@hfeg0pkn002 mc=50 · schematic_netlist B-grade synthesized L2 k=16 · byte-sync sha 8f2836ca size 15181 · D.jsonl 248→249 · ledger_D 1371→1372 case=246。选料：cand_1109.tsv 余 fresh 11p4q/l2j22/rk0ur 全 cross-shard(B/A)；改从 _fresh_D427_pool.json 取 dnp2f(junweix hfeg0pkn002 mc=50, aether:146/schematic:38/waveview:18/pyaether:9, D域) 未在任何 ledger → claim。peek dnp2f(46msgs/135KB)：仅 2 真实 user turn——U#0「怎么可以跨层级点亮信号线」/U#15「aether怎么可以跨层级点亮信号线」（提需求未指根因→A档任务说明可用原文）；agent 检索 aether-tool-qa 知识库+手册 Trace Net 跨层级选项，msg#42 欲清理临时脚本再给答案，msg#45 code_sidecar_sigterm→**最终答案未交付、用户未接受任何结果**→不可 A-faithful，做 B-grade synthesized。主题迁移：「跨层级信号线点亮」→层级化 SPICE 网表按 glob 模式跨层级追踪 net。候选 hier_net_trace.py <netlist.sp> <pattern> <out.json>：解析 .SUBCKT/.ENDS+X 实例调用(行尾=子电路类型,前面 token 按位置映射端口),fnmatch 匹配 net,记录每条 X 调用里匹配 net 的出现{net,parent_subckt,inst,child_subckt,pin,hier_path=parent/inst}+stats。A=sram_col.sp(SramCol/BitCellArray×8BitCell/PrechargeBlk/SenseAmpCol/ColMux+叶子,10 subckts/27 xinstances,模式 bl*,9 matched_nets/25 occ)；隐藏 B=rf_read.sp(RfReadPath/WordDrv×4/RbCell×16/RwAmp/RwlPrech+叶子,9 subckts/30 xinstances,模式 wl*,22 matched_nets(wl/wl0-3/wlb/wlb0-15)/30 occ)——结构/规模/连线名/模式全不同反硬编码。判分 L2 subprocess 真跑候选于隐藏 B + 结构化字段断言。16条a-p：a含.py b py_compile c B退出0合法JSON d四键 e n_subckt_defs==9 f n_total_xinstances==30 g n_matched_nets==22 h n_matched_occurrences==30 i matched_nets精确22升序 j 每net匹配wl* k 特定occ{wl0,RfReadPath/Xw0,WordDrv,pin=wl} l 特定occ{wlb,WordDrv/Xd1,DrvN,pin=in}跨层级 m hier_path==parent/inst n 反硬编码A的bl/bl0-7不入B o 空模式优雅空列表退出0 p 3-seed md5一致。自验 ref PASS 16/16 + §4.9三假(empty→c/print_only→c/core_deleted→k)全FAIL distinct + 3 neg(naive_hardcode→e/always_empty→e/core_deleted→k)全FAIL distinct + negative_selftest NEG_RC=0。byte-sync sha 8f2836ca size 15181。D.jsonl 248→249。🧾 断言: k_rationale=k_check=16 ✓ 今日 11-09 新 case 14/14 达标）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #439 流水：交付 TempParamReforge-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha eb69a0ed size 10677, D.jsonl 251→252）— jrjm6 ghyang@hfeg0pkn003 mc=62，SPICE .sp 温度参数化 + alter 重构；候选 temp_param_reforge.py <input.sp> <output.sp> 检测 .temp <X>c→.temp {ptemp}+保证早期 .param ptemp=<X>+删首个 .alter 到 EOF 全部旧 sweep+追加 4 组新温度 .alter(25/45/98/130)+保留头/.inc/.lib/.measure/.tran/.end；A=sim_p1a3_pl3_ff.sp(corner ff,-40,Pattern1a3,5 pvcsl alters 0.88→0.78,meas Write1/2/3/4,.tran 1n 200n)，隐藏 B=sim_p2a4_pl3_ss.sp(corner ss,-55,Pattern2a4,3 pvcsl alters 0.90/0.85/0.80/0.75,meas Read1/Read0+tCCD_r,.tran 1n 220n,dut_yio2) 反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+16 条 a-p(温度参数化/早期 ptemp/旧 alter 清除/4 新 alter 顺序/meas+.tran+头保留/反硬编码 A-only 不泄入/跨输入 A→ptemp=-40/3-seed md5)；自验 ref PASS 16/16 + §4.9 三假(empty→c/print_expected→l,0/core_deleted→j)全 FAIL distinct + 2 neg(naive_no_parametrize→d/naive_hardcode_a→f)全 FAIL distinct + negative_selftest NEG_RC=0；与已有 SpiceMeasInserter(meas 插入)/CapInsertStgOut(电容插入)/NetlistStructDiff(网表 diff) 操作维度(温度参数化+温度 alter 重构)不同，非重复
- #438 流水：交付 VparamDeadAudit-001（schematic_netlist B-grade synthesized L2 k=14, byte-sync sha 84370330 size 14666, D.jsonl 250→251）— evxj6 xuluo@hfeg0pkn001 mc=333，Verilog parameter 死引用 + 硬编码延时 shadow 审计；trace U#0「分析/proj/dbcoa/.../cyclic_xyz 代码，python 参数 vs verilog 参数对比」（提需求未指根因），agent 多轮核查发现 rhr_parameter.pkg tRFC=280000 死参数零引用、rhr_driver.sv #11.52 延时链硬编码实际时序，U#29 改 gen_paralist_sv_aligned.py 对齐 SV xyz 逻辑生成 4408 行，U#30 求总结隐式接受；A-faithful 金标准依赖 /proj/dbcoa 私有大源树沙盒不可复刻 → B-grade synthesized 把核心发现抽成单文件审计任务；候选 vparam_audit.py <vfile> <out.json> 解析 parameter/localparam 声明(名字/值/行)+refs 计数(剔除声明行+行注释)+classification(used/dead)+#<num> 硬编码延时(剔除//注释)+value shadow(延时字面量==param 值)+JSON{params/hardcoded_delays/value_shadows/summary}；A=rhr_top_a.v(10 params,2 dead T_RFC_A/NOISE_A,8 used,4 delays #5.0×2/#860/#1000,1 shadow #860==OSC_T_A)，隐藏 B=rhr_top_b.v(9 params,2 dead tRFC_B/tRC_B,7 used,5 delays #11.52×3/#60/#440,1 shadow #60==ACT_PERIOD_B) 反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+14 条 a-n 结构化字段断言(py_compile+exit0+四顶层键+n_params9+n_dead2+n_used7+n_delays5+n_shadows1+tRFC_B dead refs0+tREFI_B used refs>=1+#11.52 ref_dly ctx+#60→ACT_PERIOD_B shadow+反硬编码 A-only 名不泄入+4-run md5 一致)；自验 ref PASS 14/14 + §4.9 三假(empty→c/print_only→c/core_deleted→h)全 FAIL + 3 neg(naive_hardcode→i/always_empty→d/core_deleted→h)全 FAIL distinct + negative_selftest NEG_RC=0；与已有 VconnConsistCheck(模块例化端口连线比对)/HierNetTrace(SPICE net 追踪)/NetlistStructDiff(HSPICE 网表 diff) 操作维度(parameter 声明引用审计+延时 shadow 检测)不同，非重复
- #437 流水：交付 VconnConsistCheck-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha 85c8f4dc size 10344, D.jsonl 249→250）— xt9ag e0045144@hfeg0pkn002 mc=301，Verilog 模块间连线一致性 checker；候选 vconn_check.py <file1.v> <file2.v> <out.json> 解析 Verilog 例化(.port(sig) 命名连接)+按 module type 分组+公共类型按 instance 名配对逐端口比对(PortMissF1/F2/SigDiff)+单边类型 InstCountDiff+JSON 报告；A=MemCtrl/sram_row×2+sense_amp+wl_drv+prech(5vs4 inst,3 diff)，隐藏 B=SubSysTop/data_buf×2+addr_dec+clk_gate+rst_sync(5vs4 inst,4 diff: data_buf.din SigDiff/clk_gate.en SigDiff gate_en→1'b0/addr_dec.en PortMissF1 dec_en/rst_sync InstCountDiff) 反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+16 条 a-p 结构化字段断言(两特定 SigDiff+一 PortMissF1+一 InstCountDiff+反硬编码 A-only 不泄入+相同文件优雅+3-seed md5)；自验 ref PASS 16/16 + §4.9 三假(empty→c/print_only→c/core_deleted→j)全 FAIL distinct + 3 neg(naive_hardcode→h/always_empty→e/core_deleted→j)全 FAIL distinct + negative_selftest NEG_RC=0；与已有 HierNetTrace(层级 SPICE net 追踪)/NetlistStructDiff(HSPICE 网表 diff) 文件格式(Verilog)+操作维度(模块例化端口连线一致性比对)均不同，非重复
- #436 流水：交付 HierNetTrace-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha 8f2836ca size 15181, D.jsonl 248→249）— dnp2f junweix@hfeg0pkn002 mc=50，跨层级信号线点亮主题迁移到层级化 SPICE net 追踪（U#0/U#15 用户原话「aether 怎么可以跨层级点亮信号线」提需求未指根因；trace 46 msgs，agent 检索 aether-tool-qa+手册 Trace Net 跨层级选项，msg#45 code_sidecar_sigterm 最终答案未交付→无用户接受结果→不能 A-faithful；B-grade synthesized）；候选 hier_net_trace.py <netlist.sp> <pattern> <out.json> 解析 .SUBCKT/.ENDS+X 实例调用（行尾=子电路类型，前面 token 按位置映射端口）+fnmatch glob 匹配 net+记录每条 X 调用里匹配 net 的出现{net,parent_subckt,inst,child_subckt,pin,hier_path=parent/inst}+stats；A=sram_col.sp(SramCol/BitCellArray×8BitCell/PrechargeBlk/SenseAmpCol/ColMux+叶子,10 subckts/27 xinstances,模式 bl*,9 matched_nets/25 occ)，隐藏 B=rf_read.sp(RfReadPath/WordDrv×4/RbCell×16/RwAmp/RwlPrech+叶子,9 subckts/30 xinstances,模式 wl*,22 matched_nets(wl/wl0-3/wlb/wlb0-15)/30 occ)——结构/规模/连线名/模式全不同反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+结构化字段断言；16条a-p 含 B四统计精确+matched_nets精确22升序+每net匹配wl*+两特定occ(wl0/RfReadPath-Xw0-WordDrv-pin=wl 与 wlb/WordDrv-Xd1-DrvN-pin=in 跨层级)+hier_path结构完整+反硬编码A的bl不入B+空模式优雅+3-seed md5；自验 ref PASS 16/16 + §4.9三假(empty→c/print_only→c/core_deleted→k)全FAIL distinct + 3 neg(naive_hardcode→e/always_empty→e/core_deleted→k)全FAIL distinct + negative_selftest NEG_RC=0；与已有 NetlistStructDiff(两网表 diff)/CapInsertStgOut(插入 measure)/SpiceMeasInserter 不同维度非重复
- #427 流水：（已归档批次 2092）
- #423 流水：（已归档批次 2092）
- #422 流水：（已归档批次 2091）
- #419/#418/#417 流水（3 轮 0-case 选料复核：fresh D A-grade seed 枯竭 / DEBT②自测放宽关键词仍枯竭 / 清空 r416 残留）— 全文已搬 MEMORY_D_archive.md「归档批次 2088」
- #416 流水：交付 RsCalcReport-001（schematic_netlist B-档 L3 k=12）— 全文见 MEMORY_D_archive.md「归档批次 2089」
- #415 流水：交付 VsimCovReport-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha e78d3ea5 size 12105, D.jsonl 229→230）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #414 流水：交付 AddrRtlGateMap-001（schematic_netlist B-grade synthesized L3 k=12, byte-sync sha d4121e46 size 15549, D.jsonl 228→229）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #413 流水：交付 2StepOCChainAnalyze-001（schematic_netlist B-档 L3 k=12, byte-sync sha 7a21129b size 11902, D.jsonl 431→432）— 全文已搬 MEMORY_D_archive.md「归档批次 2098b」
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
- 📊 trace 覆盖率：249 / 1511 = 16.5%（mc>=30 候选池；D.tsv 现 249 case-mark + ... parked · 已动过 1329；快照 2026-11-09 07:29 sessions=5822 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 252 entries / wc -l 252）：analog_context:51 · schematic_netlist:129 · waveform:41。**#439**：jrjm6(ghyang@hfeg0pkn003 mc=62)→TempParamReforge-001（schematic_netlist B-grade synthesized L2 k=16，SPICE .sp 温度参数化+alter 重构：候选 temp_param_reforge.py <input.sp> <output.sp> .temp <X>c→.temp {ptemp}+早期 .param ptemp=<X>+删旧 .alter sweep+追加 4 组温度 .alter 25/45/98/130+保留头/.inc/.measure/.tran/.end；A=sim_p1a3_pl3_ff.sp(ff,-40,Pattern1a3,5 pvcsl alters,meas Write1/2/3/4)，B=sim_p2a4_pl3_ss.sp(ss,-55,Pattern2a4,3 pvcsl alters,meas Read1/Read0+tCCD_r,.tran 1n 220n) 反硬编码；判分 L2 subprocess 真跑 B+16 条 a-p 结构化字段断言;byte-sync sha eb69a0ed size 10677;D.jsonl 251→252）。**#438**：evxj6→VparamDeadAudit-001（Verilog parameter 死引用+硬编码延时 shadow 审计;byte-sync sha 84370330 size 14666;D.jsonl 250→251）。**#437**：xt9ag(e0045144@hfeg0pkn002 mc=301)→VconnConsistCheck-001（schematic_netlist B-grade synthesized L2 k=16，Verilog 模块间连线一致性 checker：候选 vconn_check.py <file1.v> <file2.v> <out.json> 解析 Verilog 例化+按 module type 分组+逐 instance 逐端口比对+InstCountDiff+JSON 报告；A=MemCtrl/sram_row×2+sense_amp+wl_drv+prech(5vs4,3 diff)，B=SubSysTop/data_buf×2+addr_dec+clk_gate+rst_sync(5vs4,4 diff) 反硬编码；判分 L2 subprocess 真跑 B+16 条 a-p 结构化字段断言;byte-sync sha 85c8f4dc size 10344;D.jsonl 249→250）。**#436**：dnp2f(junweix@hfeg0pkn002 mc=50)→HierNetTrace-001（schematic_netlist B-grade synthesized L2 k=16，跨层级 SPICE net 追踪：候选 hier_net_trace.py <netlist.sp> <pattern> <out.json> 解析 .SUBCKT/X 调用+fnmatch 匹配+positional pin 映射+hier_path；A=sram_col.sp(10 subckts/27 xinst,bl*,9 nets/25 occ)，B=rf_read.sp(9 subckts/30 xinst,wl*,22 nets/30 occ) 反硬编码；判分 L2 subprocess 真跑 B+结构化字段断言;byte-sync sha 8f2836ca size 15181;D.jsonl 248→249）。**#435**：g13dw→AgingStepDirSplit-001（FineSim matrix sim-runner Perl aging step1/step2 仿真目录分离;byte-sync sha f9a7fabd size 9389;D.jsonl 247→248,归档2098）。**#434**：ejp6w→NetlistStructDiff-001（HSPICE 网表结构化对比;byte-sync sha f1b297ce size 4398;D.jsonl 246→247,归档2097）。**#433**：suauw→CapInsertStgOut-001（归档2096）。**#431**：us0hd→RegrCaseFilter-001（归档2096）。**#430**：h8pcp→DqReadPathWaveDebug-001（归档2094）。**#429**：pchuf→ClampLeakPwrAnalyze-001（归档2093）。**#428**：e3sf0→InstFuncDiagFix-001（归档2093）。**#427**：xppi3→FsdbMeasRun-001（归档2092）。**#426**：od1ab→BitcellMcSpGen-001（归档2091）。**#425**：szdav→SaSlicerSizingPlan-001（归档2091）。**#424**：scut3→InstArcDiagFix-001（归档2091）。**#423**：ftu9v→XProbeHierGen-001（归档2092）。**#422**：fxfox→SimSpGen-001（归档2091）。**#421**：wmzu1→GrDecPwrSwitchTbGen-001（归档2090）。**#420**：btze4→EccTopCircuitCompare-001（归档2090）。**#416**：7u0m3→RsCalcReport-001。**#415**：wk3wd→VsimCovReport-001（归档2093）。**#412**：5fpjy→SdlGroupPlan-001（归档2086）。
- 📦 体积：TASK_D≈27KB / MEMORY_D≈38KB（本轮 #439 交付 TempParamReforge-001；略超 32KB 软限，下轮可归档 #434/#432b 流水降体积）
- DEBT: 0 选料阻塞（fresh 池 #437 已用 xt9ag；_fresh_D427_pool.json 25 fresh rank 80-260 多 layout/calibre-pnr(非D)：wp528=Calibre rule-deck Q&A(非produce) / cv0pc=DRC log /rundata 私有 / 2gkvu=powerfill layout(C域) / aw9d7=NO_FILE / 11fst=parked(SRAM Solido Q&A) 已 peek 处理；下轮可往 rank 260+ 扩或降 mc>=15）。⚠️ DEBT① 已破局。⚠️ DEBT⑤ 跨 shard 重复已建立 4-ledger 排除集机制。其余运维项：④/proj 资产权限(#435 真实 matrixrun 内部私有→B-grade synthesized,DEBT④ 触发已处理)。⚠️ 未碰其他 shard 飞行。⚠️ 与已有 HierNetTrace(层级 SPICE net 追踪)/NetlistStructDiff(HSPICE 网表 diff)/SPFNetlistCompare 文件格式(Verilog)+操作维度(模块例化端口连线一致性比对)均不同，非重复。
- 🧾 断言: k_rationale=k_check=16 ✓（#439 TempParamReforge-001 落 jsonl 16==16≥8 达标；#438 VparamDeadAudit-001 14==14；#437 VconnConsistCheck-001 16==16；#436 HierNetTrace-001 16==16；#435 AgingStepDirSplit-001 15==15；#434 NetlistStructDiff-001 15==15；#433 CapInsertStgOut-001 16==16；#432b SpiceMeasInserter-001 15==15；#432a TotemXtrShortAudit-001 16==16；存量 252 entries test_rationale 全以 `k 条断言：①…` 开头已核验达标；rewrite_queue.tsv 15/15 done 无待修；今日 11-09 新 case 17/17 达标（#422-#439））。
- 🎯 通过率: 最近20条 n/a（#439/#438/#437/#436/#435/#434/#432/#431/#430/#429/#428/#427/#425/#424/#423/#422/#421 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #435 流水：交付 AgingStepDirSplit-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f9a7fabd size 9389, D.jsonl 247→248）— 全文已搬 MEMORY_D_archive.md「归档批次 2098」
- #434 流水：交付 NetlistStructDiff-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha f1b297ce size 9398, D.jsonl 246→247）— ejp6w yuchens@hfeg0pkn004 mc=549，HSPICE 网表结构化对比；全文已搬 MEMORY_D_archive.md「归档批次 2097」
- #433 流水：交付 CapInsertStgOut-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha c33ab85c size 15001, D.jsonl 245→246）— suauw jiangbaol@hfeg0pkn001 mc=290，StrongArm slicer .sp 比较器 out_stg1 两端参数化电容插入；全文已搬 MEMORY_D_archive.md「归档批次 2096」
- #432b 流水：交付 SpiceMeasInserter-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha d3f2c2a5 size 15938, D.jsonl 244→245）— 全文见 git 历史（本轮压缩为首行指针）
- #432 流水：交付 TotemXtrShortAudit-001（schematic_netlist B k=16, byte-sync sha 4613541c, D.jsonl 243→244）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- #431 流水：交付 RegrCaseFilter-001（schematic_netlist B-grade synthesized L2 k=15, byte-sync sha dd282fc6 size 3691, D.jsonl 242→243）— us0hd e0039102@hfeg0pkn002 mc=166，LPDDR5/DDR5 回归 Perl caselist 按 bus 挑选 case 写新文件不覆盖原文件；全文已搬 MEMORY_D_archive.md「归档批次 2096」
- #430 流水：交付 DqReadPathWaveDebug-001（waveform B-grade synthesized L2 k=15, byte-sync sha 0154aae6 size 8257, D.jsonl 241→242）— h8pcp jinhaoli@hfeg0pkn004 mc=156，DDR5 DQ 读路径波形比对 debug；全文见 git 历史(本轮压缩为首行指针)
- #429 流水：交付 ClampLeakPwrAnalyze-001（analog_context B-grade synthesized L2 k=17, byte-sync sha 659bb607 size 11370, D.jsonl 240→241）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #428 流水：交付 InstFuncDiagFix-001（analog_context B-grade synthesized L2 k=14, byte-sync sha 158f2385 size 10514, D.jsonl 239→240）— 全文已搬 MEMORY_D_archive.md「归档批次 2093」
- #426 流水：（已归档批次 2091）
- #425 流水：（已归档批次 2091）
- #424 流水：（已归档批次 2091）
- #423 流水：（已归档批次 2092）
- #420 流水：交付 EccTopCircuitCompare-001（schematic_netlist B k=12, D.jsonl 231→232）— 全文已搬 MEMORY_D_archive.md「归档批次 2095」
- 流水 #413b (数据质量修复轮 0 新 case · 并行 agent 已交付 2StepOCChainAnalyze-001 · 本 agent 检测重复并修复 D.jsonl 7 malformed task_id) — 全文已搬 MEMORY_D_archive.md「归档批次 2087」
- 流水 #411 (SimlibLogicCheck-001, schematic_netlist B L1) — 全文已搬 MEMORY_D_archive.md「归档批次 2095」
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
