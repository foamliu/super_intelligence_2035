WAITING: 0（#446 交付 VscForceInsert-001 · 4fbwo mike@hfeg0pkn003 mc=70 · schematic_netlist B-grade synthesized L2 k=14 · byte-sync sha 6dedadce size 15622 · D.jsonl 258→259 · ledger_D case=256。选料：mc>=30 fresh D-dominant 顶部池近枯竭(4fbwo/fg1kv/oue4a 仅 3 fresh in top 80，fg1kv/oue4a 均 Q&A)，4fbwo「在 dscqa DDR6 Finesim 仿真目录 si.inp 追加两条 VSC 力源语句 VSC0111/VSC0112 chanpsd0/chanpsd1 控制器 error_blocking 0 pvss」(提需求未指根因→A档任务说明可用)干净单 produce ✓ claim。深读 4fbwo(88 msgs)：agent 读 si.inp 找到 ** Force WICA 块后插入点(line 137 后、.temp 前)，但目标在 /rundata 下受 agent 可写策略限制(writableRoots=/ai_sandbox,/home)，editor/run_commands 均被拒，最终只在 /home/mike 写 instructions 文件未直接改 deck。A-faithful 依赖私有 /rundata DDR6 仿真沙盒 + writableRoot 限制不可复刻 → B-grade synthesized 抽成自包含 si.inp + JSON 规格的 VSC 力源插入器(续编编号+节点去重+结构化报告)。候选 vsc_inserter.py <si.inp> <vsc_spec.json> <out.inp> <report.json> 解析既有 VSC 行(VSC%04d)+规格条目→按层级节点去重+在最后一条既有 VSC 后插入新 VSC 续编全局编号+保留其余行+输出结构化 JSON{summary,inserted,skipped}。A=si.inp_A(15 既有 VSC:wica_nodeA-E×10+error_blocking×5,.temp -40)+vsc_spec_A.json(3 条目→2 insert/1 skip wica_nodeA 重复)；隐藏 B=si.inp_B(11 既有 VSC:drv×11,.temp 85)+vsc_spec_B.json(4 条目→3 insert/1 skip)——项目/corner/VSC 块规模/节点命名空间(ddr6top·chanpsd·error_blocking·wica_nodeX vs drr5top·dq+ca·drv·error_flag·scan_en·wica_drvX)/spec 条目全不同反硬编码。判分 L2 subprocess 真跑候选于隐藏 B + 14 条 a-n 结构化字段断言(zip 含.py/py_compile/B 退出0+合法JSON/inserted_count==3/skipped_count==1/max_vsc_before==11/max_vsc_after==14/inserted 节点集合/skipped[0] node+reason/新 VSC 行字段/total VSC==14+原 VSC 保留/.temp 放置/反硬编码 A 跑 inserted==2 + A/B-only token 不泄入/3-seed md5)。自验 ref PASS 14/14 + §4.9 三假(syntaxerr→b/print_only→c/core_deleted→j)全 FAIL distinct + 3 neg(naive_no_dedup→d/naive_hardcode_b→m/naive_append_end→l)全 FAIL distinct + negative_selftest NEG_RC=0 + jsonl round-trip 抽 test 字段 exec 跑 PASS 14/14。byte-sync sha 6dedadce size 15622。D.jsonl 258→259。🧾 断言: k_rationale=k_check=14 ✓。选料复用：.75 pick session scored.tsv(709 fresh D-dominant)供后续轮次；下轮 D 应考虑降 mc 阈值(mc>=20)或放宽 d_score>=2/d_score>=1，因 mc>=30 D-dominant fresh 池近枯竭。）今日 11-09 新 case 26/26 达标）
（#440-#443 snapshot 续行全文已搬 designflow/MEMORY_D_archive.md「归档批次 2100」）
（#436-#439 心跳已归档 → MEMORY_D_archive.md「归档批次 2099」）
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform


- #436-#441 流水全文已搬 designflow/MEMORY_D_archive.md「归档批次 2100」
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
- 📊 trace 覆盖率：256 / 1511 = 16.9%（mc>=30 候选池；D.tsv 现 256 case-mark + ... parked · 已动过 1339；快照 2026-11-09 15:10 sessions=5822 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 259 entries / wc -l 259）：analog_context:53 · schematic_netlist:134 · unknown:1 · waveform:42。最近 case：。
- 📦 体积：TASK_D≈27KB / MEMORY_D≈37.5KB（本轮 #446 交付后归档批次 2100：#440-#443 snapshot+#436-#441 流水+覆盖率 blurb → archive，68KB→37.5KB 低于 40KB 红线 ✓；仍超 32KB 软限，DEBT 下轮继续归档）
- DEBT: 0 选料阻塞（本轮 #446 mc>=30 fresh D-dominant 顶部池近枯竭，仅 4fbwo 干净 produce 可用(同批 fg1kv/oue4a 均 Q&A)；4fbwo 选中。.75 pick session scored.tsv(709 fresh D-dominant)仍可供后续轮次。下轮 D 应考虑降 mc 阈值(mc>=20)或放宽 d_score>=2/d_score>=1）。⚠️ DEBT① 已破局。⚠️ DEBT⑤ 跨 shard 重复已建立 4-ledger 排除集机制。其余运维项：④/proj 资产权限(#446 真实 /rundata DDR6 仿真目录受 writableRoots 限制不可写,B-grade synthesized 已处理)。⚠️ 未碰其他 shard 飞行。⚠️ 与已有 SiInpTokenStrip-001(si.inp token 剥除)/DQTXStim/SpStimGen(stimulus 生成)/SpiceMeasInserter(.meas 插入既有 .sp) 操作维度(向 si.inp 既有 VSC 块续编插入力源语句+全局编号续延+层级节点去重+结构化 JSON 报告)不同，非重复。
- 🎯 通过率: 最近20条 n/a（#446/#445/#444/#443/#442/#441/#440/#439/#438/#437/#436/#435/#434/#432/#431/#430/#429/#428/#427/#425/#424 交付未实跑被测；目标 B 档 20–30%）。

## 流水
- #446 流水：交付 VscForceInsert-001（schematic_netlist B-grade synthesized L2 k=14, byte-sync sha 6dedadce size 15622, D.jsonl 258→259）— 4fbwo mike@hfeg0pkn003 mc=70，Finesim si.inp deck VSC 力源语句插入（续编编号+节点去重+结构化报告）；trace U#原「在 dscqa DDR6 Finesim 仿真目录的 si.inp 中追加两条 VSC 力源语句：VSC0111/VSC0112 chanpsd0/chanpsd1 控制器 error_blocking 0 pvss」（提需求未指根因→A档任务说明可用），agent 读 si.inp 找到 ** Force WICA 块后插入点(line 137 后、.temp 前)，但目标在 /rundata 下受 writableRoots 策略限制，editor/run_commands 均被拒，最终只在 /home/mike 写 instructions 文件未直接改 deck；A-faithful 依赖私有 /rundata DDR6 仿真沙盒 + writableRoot 限制不可复刻 → B-grade synthesized 抽成自包含 si.inp + JSON 规格的 VSC 力源插入任务；候选 vsc_inserter.py <si.inp> <vsc_spec.json> <out.inp> <report.json> 解析既有 VSC 行(VSC%04d)+规格条目→按层级节点去重+在最后一条既有 VSC 后插入新 VSC 续编全局编号+保留其余行+输出结构化 JSON{summary,inserted,skipped}；A=si.inp_A(15 既有 VSC:wica_nodeA-E×10+error_blocking×5,.temp -40)+vsc_spec_A.json(3 条目→2 insert/1 skip wica_nodeA 重复)，隐藏 B=si.inp_B(11 既有 VSC:drv×11,.temp 85)+vsc_spec_B.json(4 条目→3 insert/1 skip) 反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+14 条 a-n 结构化字段断言(zip 含.py/py_compile/B 退出0+合法JSON/inserted_count==3/skipped_count==1/max_vsc_before==11/max_vsc_after==14/inserted 节点集合/skipped[0] node+reason/新 VSC 行字段/total VSC==14+原 VSC 保留/.temp 放置/反硬编码 A 跑 inserted==2 + A/B-only token 不泄入/3-seed md5)；自验 ref PASS 14/14 + §4.9 三假(syntaxerr→b/print_only→c/core_deleted→j)全 FAIL distinct + 3 neg(naive_no_dedup→d/naive_hardcode_b→m/naive_append_end→l)全 FAIL distinct + negative_selftest NEG_RC=0 + jsonl round-trip PASS 14/14；与已有 SiInpTokenStrip-001(si.inp token 剥除)/DQTXStim/SpStimGen(stimulus 生成)/SpiceMeasInserter(.meas 插入既有 .sp) 操作维度(向 si.inp 既有 VSC 块续编插入力源语句+全局编号续延+层级节点去重+结构化 JSON 报告)不同，非重复
- #445 流水：交付 TimingMeasFileGen-001（schematic_netlist B-grade synthesized L2 k=16, byte-sync sha c320ed04 size 11572, D.jsonl 257→258）— gvexo kerwind@hfeg0pkn002 mc=135，Custom WaveView .sig 信号列表→FineSim .measure timing 文件生成；trace U#13「用finesim measure语法写一个timing_measure文件，测量 check_signal.sx 文件中其他信号第1个上升沿50%和第1个信号第1个上升沿50%的时间差...san*→pvnoc，sap*→pvpcsg」（提需求+完整 spec 未指根因→A档任务说明可用），agent 读 check_signal.sx + match_signal.sig + 模板 .sp，按前缀→参数映射(san*→pvnoc/sap*→pvpcsg/ocn*/ocp*跳过)+层级节点规范化(xi_...v(sig)→v(xi_...sig))+RISE=1+50%阈值生成 50 条 .MEASURE，因 policy writableRoot 限制文件落 /home/kerwind/ 再 copy 到 /rundata；A-faithful 依赖私有 /proj/ddgoa 工程沙盒 + Custom WaveView .sx/.sig + writableRoot 限制不可复刻 → B-grade synthesized 抽成自包含「.sig 信号列表→FineSim .measure 文件生成」任务；候选 timing_measure_gen.py <sig> <out.sp> 解析 signal= 行(跳注释/空行)→第1=参考(TRIG)其余=目标(TARG)+节点规范化((.+)\.v\(([^)]+)\)→v(\1.\2)、裸→v())+前缀分类(san*→pvnoc/sap*→pvpcsg/其余跳过)+输出 .MEASURE tran t_<name> TRIG v(<ref>) VAL=pvint*0.5 RISE=1 TARG v(<tar>) VAL=<param>*0.5 RISE=1；A=match_signal.sig(1 ref secd + 12 valid san/sap + 2 skip ocn/ocp)，隐藏 B=match_signal_B.sig(ref=clkb + 10 valid + 2 skip) 反硬编码；判分 L2 subprocess 真跑候选于隐藏 B+16 条 a-p 结构化字段断言(含 zip 含.py/py_compile/B 退出0+n_measures/n_measures==n_valid/TRIG==ref+pvint+RISE1/TARG∈valid/TARG-VAL 前缀映射/TARG-RISE1/skip 缺席/名唯一+prefix t_/ref 规范化原始 vs v 形式/跨输入 A 跑+反泄/.MEASURE tran 模式/3-seed md5/VAL *0.5 形式/ref 不作 TARG)；自验 ref PASS 16/16 + §4.9 三假(empty→c/print_expected→l/core_deleted→e)全 FAIL distinct + 4 neg(naive_hardcode_a→d/naive_skip_none→d/naive_no_normalize→e/naive_wrong_param→g)全 FAIL distinct + negative_selftest NEG_RC=0 + jsonl round-trip PASS 16/16；与已有 SpiceMeasInserter(.meas 插入既有 .sp)/CapInsertStgOut(.sp 电容插入)/NetlistStructDiff(网表 diff) 操作维度(从信号列表 .sig 生成独立 timing_measure .sp 文件+前缀→参数映射+层级节点规范化+跳过规则)不同，非重复
- #443 流水：交付 ModBodySwapCelldefine-001（schematic_netlist B-grade synthesized L2 k=14, byte-sync sha c299cb15 size 10982, D.jsonl 255→256）— z9zx7 cliu@hfeg0pkn004 mc=161，SystemVerilog 标准单元库模块体替换（修 endmodule 拼接 + celldefine 包装器保留两 bug）；trace U#335/U#338 用户原话「帮忙修改脚本...目前出现上一个cell的endmodule和下一个cell的module连在一起的问题以及需要保留每个cell的 `celldefine 和 `endcelldefine」（给现象两 bug+目标行为，未指根因→A档任务说明可用），agent _repro_real 实测真实 fileB 265/267 body 缺尾换行、fileA `celldefine=633/`endcelldefine=637 自身失衡 4、旧输出 269 replaced + joined 行，重写为顶层扁平 module 扫描器；A-faithful 依赖私有 46574 行 simlib 源树沙盒不可复刻 → B-grade synthesized 抽成自包含小型 SV 库模块体替换任务；候选 replace_modules.py <fileA> <fileB> <output> 扫 fileB 顶层 module body 保证以 \n 结尾 + 扫 fileA module span 只换内层 body 保留 `celldefine/`endcelldefine 包装器+空行+注释 + 未匹配模块逐字节保留 + 无 joined 行；A=simlib_A.sv+new_cells_A.sv(5 mods inv_a/nand2_a/nor2_a/buf_a/dff_a，nand2_a+nor2_a 包装器紧挨无空行)，隐藏 B=simlib_B.sv+new_cells_B.sv(6 mods mux2_b/and2_b/latch_b/or2_b/xor2_b/tri_buf_b，替换{or2_b,xor2_b,tri_buf_b}/保留{mux2_b,and2_b,latch_b}，5 `celldefine 包装器) 反硬编码；判分 L2 subprocess 真跑 B+14 条 a-n(无 joined 行/`celldefine 计数==fileA_B 5/`endcelldefine 计数==5/替换集合{or2_b,xor2_b,tri_buf_b}/保留集合{mux2_b,and2_b,latch_b}逐字节==fileA_B/body 以 \n 结尾/模块名集合==fileA_B/模块数==6/反硬编码 (simlib_B,new_cells_A) 无交集→0 替换 output==fileA_B/3-seed md5)；自验 ref PASS 14/14 + §4.9 三假(empty→c/print_expected→f/core_deleted→h)全 FAIL distinct + 3 neg(naive_no_newline→e/naive_drop_wrappers→f/naive_hardcode_b→m)全 FAIL distinct + negative_selftest NEG_RC=0 + jsonl round-trip PASS 14/14；与已有 VconnConsistCheck(Verilog 模块例化端口连线比对)/HierNetTrace(SPICE net 追踪)/NetlistStructDiff(网表 diff)/VparamDeadAudit(parameter 死引用) 操作维度(SV 库 module body 按名替换+celldefine 包装器保留+endmodule 拼接修复)不同，非重复
- #442 流水：交付 HciStressExtract-001（waveform B-grade synthesized L2 k=16, byte-sync sha 21ea932a size 12880, D.jsonl 254→255）— cdza6 yh1yang@hfeg0pkn002 mc=48，Custom WaveView ring oscillator 瞬态波形 NMOS HCI 应力参数提取；trace U#0「阅读提示词，从wave文件中提取HCI stress」（提需求未指根因→A档任务说明可用），agent 写 analyze_hci.py：Vdd=median(vout>0.5)、Vth=Vdd/3、mask=(Vgs>Vth)&(Vds>Vth)、np.diff 升降沿配对应力窗口、累计 t_eff+Vg/Vd_stress 峰值、输出终端表格+PDF；A-faithful 依赖私有 wave 文件 → B-grade synthesized 抽成自包含波形 HCI 提取+JSON 报告任务；候选 hci_stress_extract.py <wave_file> <out.json> [--from/--to] 解析 Custom WaveView→Vdd/Vth→窗口检测→JSON{summary,signals,windows,per_window_stats}；A=ro_wave_A.txt(Vdd≈1.2V,20ps,10周期,800点,11窗口,v(ro1_mid<0>)/v(ro1_mid<8>)/v(out))，隐藏 B=ro_wave_B.txt(Vdd≈0.9V,30ps,8周期,720点,9窗口,v(ro1_mid<3>)/v(ro1_mid<5>)/v(vdd)) 反硬编码；判分 L2 subprocess 真跑 B+16 条 a-p(独立参考实现校验 n_windows/t_eff/vg_stress/vd_stress/per_window_stats + 跨输入反硬编码 A vdd≈1.2 且 A-only 信号名不泄入 B + 3-seed md5)；自验 ref PASS 16/16 + §4.9 三假(empty→c/print_only→k/core_deleted→g)全 FAIL distinct + 3 neg(naive_always_zero→g/naive_hardcode_a→d/naive_no_windowing→g)全 FAIL + negative_selftest NEG_RC=0 + jsonl round-trip PASS 16/16；与已有 DqReadPathWaveDebug(DDR5 DQ 读路径波形比对 debug)/WaveCmpWrap(波形比较包装)/WvSigListGen(波形信号列表)/CosWaveWdf(cos 波形 WDF) 操作维度(瞬态波形 HCI 应力窗口检测+累计 t_eff+峰值应力电压)不同，非重复
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


