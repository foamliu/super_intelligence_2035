WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform

- **PHASE**: shard D 运行中。已交付 155 条 case（D.jsonl 155 行）；台账 case-mark 154 + 890 parked = 1044 已动过。**本轮 #318 交付 MeasStmtExtract-001（B 档 synthesized, L1 真跑候选, 16 条件 a-p）**，修 #317 DEBT。选料：peek_dirbased.py 在 .75 上批量 peek 33 候选(fresh_D317_avail mc 57-79, shard D 域)→中等 mc 池 Q&A/debug/analysis 占主导，clean script-produce 稀缺；选 8b8wk(ghyang mc69, .meas 解释讨论)做 B 档结构化提取任务。下轮 #319：继续用 fresh_D317_avail 剩余 ~143 候选 peek（或放宽 mc 15-30 / 80-150），找 clean A-faithful produce。
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：154 / 1511 = 10.2%（mc>=30 候选池；D.tsv 现 154 case-mark + 890 parked · 已动过 1044；快照 2026-11-06 08:40 sessions=3896）。已覆盖 domain（D.jsonl 155 行）：analog_context:33 · schematic_netlist:84 · waveform:37。⚠️ **#318 选料**：peek_D318.py 在 .75 上并跑 33 候选(fresh_D317_avail mc 57-79, shard D 域)→sig=PRODUCE 0 条（cline 工具名是 editor 非 write_to_file，produce-signal 漏判；按 editor 数+produce 文件重判）：w1dp0=LSB输出粘贴·xppi3=给 measure script+fsdb(意图弱)·xyqtl=nlchk 分析·sao7s=解析 perl 当文档·4fbwo=force 信号迭代 debug·ob8f4/56jqu/e5opy=编辑 run-regression skill·psbg1=skill 搭建 Q&A·mwyd9/3anqw/e0b5q/lvlshft skill 触发·ps5ix=simlib 组合 Q&A·lsc1e=跑 RC flow·57rrw=maxtoken Q&A·vtz09=用户给根因(disqualified A)·lq00u=修 sacap CSV(重依赖)·8b8wk=分析仿真文件+.meas 解释★·qv65m=重构 build/run 环境·rbvi8=查 cell 替换(依赖 live prof)·nsf5a=tcl/Q&A·1kipj=跑 skill·t5ge3=live 布局·mx7xh=修语法错·7uwtz/p28m8=skill 触发/Q&A。**clean script-produce 候选(6azjv perl 重构/lq00u sacap CSV)依赖重/trace 大(2.3-2.6MB)，20min 内不可完成**→选 8b8wk 做 B 档(.meas 结构化提取，纯文件 in/out，真跑候选只需 python3 subprocess)。**下轮**：fresh_D317_avail 剩 ~143 候选未 peek；或放宽 mc 15-30(shard A 先例)/mc 80-150 大 trace 早期 produce 轮。
- 📦 体积：TASK_D≈26KB / MEMORY_D≈16KB（归档批次 2027 后；低于 32KB 红线）
- DEBT: 0（#318 已交付 MeasStmtExtract-001，#317 peek 轮 DEBT 已修）
- 🧾 断言: k_rationale=k_check=16 ✓（本轮 #318 MeasStmtExtract-001 16 条断言 ①-⑯ 对应 check a-p 全；#316 ToggleCounterBindGen-001 16 条；#315 FmInstFreq-001 16 条；#314 DlygResInsert-001 16 条；#313 NetlistSigRename-001 16 条；#312 NetlistHierFlowchart-001 16 条；#311 CdlXistorAudit-001 16 条；#310 NetlistCellReplace-001 16 条；#309 NetlistGate2Verilog-001 16 条；#308 CellRewriteSimlib-001 16 条；#307 OpCornerSummary-001 15 条；#306 FarthestCellPick-001 14 条；#305 SpStimLoopAudit-001 16 条；#304 SimReportPvtSummary-001 15 条；#303 WaveMaxFind-001 15 条；#302 SpTestbenchParamFix-001 14 条；#301 NetlistMMultAudit-001 16 条；#299 SineZeroCrossFreqPeak-001 16 条；#298 InvPulseStimTb-001 14 条；#297 SpiceldViewChg-001 14 条；#296 FinesimIgnoreGen-001 14 条；#295 CosimStimFolderGen-001 14 条；#294 CellExpandGen-001 14 条；#293 SchFixFloating-001 14 条）。shard D 存量 155 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。今日 110/155 达标。rewrite_queue.tsv 全部 done（无待修）。

## 流水
- 2026-11-06 19:2x | shard D #318 | **交付 MeasStmtExtract-001（schematic_netlist, B 档 synthesized, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261106-shardD_shardD-pick318。**选料**：fresh_D317_avail.tsv(176 真 fresh) 取 mc 57-79 共 33 候选 → peek_D318.py(目录式路径+解析 data["messages"] content list+editor 工具计数+produce 文件正则)在 .75 上并跑(10 worker) → 33 候选全 peek(5 NO_FILE, 28 有文件)。**triage**：sig=PRODUCE 0 条(cline 工具名是 editor 非 write_to_file/create_file，原 produce-signal 漏判；按 editor 数+produce 文件名重判)。中等 mc(57-79)池**Q&A/debug/analysis/skill-触发占主导**：w1dp0=LSBATB 输出粘贴·xppi3=给 measure script+fsdb(意图弱)·xyqtl=nlchk 命令分析·sao7s=解析 perl 当文档·4fbwo=force 信号迭代 debug·ob8f4/56jqu/e5opy=编辑 run-regression skill 文档·psbg1=skill 搭建 Q&A·mwyd9/3anqw/e0b5q=/lvlshft skill 触发·ps5ix=simlib_base 组合 Q&A(用户确认式问)·lsc1e=跑 glory RC flow·57rrw=maxtoken/超时 Q&A·vtz09=用户已给根因(A 档 disqualified)·lq00u=修 sacap CSV(重依赖 spf+README+现有代码)·8b8wk=分析仿真文件+.meas 解释★·qv65m=重构 build/run 环境(33 轮)·rbvi8=查 cell 替换(依赖 live prof)·nsf5a=tcl/Q&A·1kipj=跑 batch_auto_via.il·t5ge3=live pyaether 布局·mx7xh=修第 57 仿真语法错·7uwtz/p28m8=skill 触发/Q&A。**clean script-produce(6azjv perl 重构 runModelQA / lq00u sacap CSV)依赖重 + trace 2.3-2.6MB，20min 内不可深读+合成+自验**。**决策**：选 8b8wk(ghyang@10.129.2.12 mc69, cmos/netlist/sch)做 B 档——用户真实请求是「分析仿真文件按功能介绍 + 解释 .meas 语句」(纯解释非 produce)，合成「写脚本把 SPICE deck 所有 .meas 指令结构化提取为 JSON」(服务用户 inventory .meas 的真实目标)。**深读**：8b8wk U#0-3 逐字(U#3 真实 .meas 句 `.meas tran tcsl_w1 when v(xi_msaq_fbcc_02.cslcon0<0>) val='0.5*pvcsl' td=tmeas rise=c_csl_w1 print=0`)→写 trace_deepreads/8b8wk_meas_extract.md。**合成**：A=合成 SPICE deck(7 条 .meas: when/param/avg/max/cross 修饰/续行/单引号 val，嵌套实例路径 v(x.sig)取自 U#3 真实句式)；hidden B=9 条(when/param/avg/min/max/rms + tran/dc/ac/空 analysis 三类)；hidden B2=5 条(无引号 val/param/2 行续行/注释)；empty deck=0 条。**反硬编码三轴**：A/B/B2 .meas 名完全不相交 + 字段值不同 + 续行结构不同。金标 extract_meas_ref.py：logical_lines(续行 + 合并)+split_tokens(括号平衡保持 v(x.y<0>) 整体)+parse_meas(analysis 类型检测/name/kind=when|delay|avg|rms|min|max|find|param/target=val/td/rise/fall/cross 去引号/print bool/lineno 首行)。**16 条件 a-p**：a zip 含.py 无禁 import/路径+无 A 名硬编 b py_compile c B-run exit0+合法 JSON list 非空 d B 记录数==9 e 11 键+类型(str/bool/int) f B when-name 集合{tdq0,tdq1,tdq2,vswd} g B analysis 分布 tran6/dc1/空1/ac1 h B val 逐条 i B td 逐条 j B rise+fall 逐条 k B cross 逐条 l B print True 恰{tdq0,trms} m B lineno∈[1,13] n 续行 B2 tmax2 单条 lineno7 printTrue + B2 tw0.val 无引号==0.5 o 反硬编码 A-run 数7+名集合+A∩B 空 p 边界+确定性 B2 tprm.kind=param target=x+y + empty→[] + 3 次重跑 B 字节一致。**自验**：ref PASS 16/16；10 negative 全 FAIL NEG_SELFTEST PASS；§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL；确定性 3 次 PASS；test==disk sha 83cb5171bc8a8062 GATE PASS k=16。台账 mark 8b8wk→case；schematic_netlist 83→84；D.jsonl 154→155。**教训**：(1) **cline 工具名是 editor 不是 write_to_file/create_file**——peek produce-signal 必须按 editor 计数+produce 文件名正则判；(2) **中等 mc(57-79)池 Q&A/debug/analysis 占主导，clean script-produce 稀缺**，下轮放宽 mc 15-30 或 peek mc 80-150 大 trace 早期 produce 轮；(3) **真实 .meas 句式**是 schematic_netlist L1 结构化提取好范式，续行/无引号 val/param/avg-min-max-rms kind 天然丰富 16 条件；(4) **B 档合成要服务用户真实目标**——8b8wk 用户要「理解 deck 里所有 .meas」，合成「提取 .meas 到结构化表」对齐。**下一步**：fresh_D317_avail 剩 ~143 候选未 peek；下轮继续 peek 找 A-faithful produce。
- 2026-11-06 18:4x-19:0x | shard D #317 | **选料/peek 轮（无 case 交付，DEBT:1）**。open_session shardD_20261106_shardD-pick317。**选料**：fresh_D306_pool.tsv(262) 经 `comm pool−peeked−ledger` 得 fresh_D317_avail.tsv(176 真 fresh)。**关键发现**：cline 存储改目录式 `<sid>/<sid>.messages.json` + messages.json 格式 `{"messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list）；旧 peek 脚本用根目录路径现在全 NO_FILE。写 peek_D317_v3.py/peek2.py（目录路径+解析 data["messages"]）在 .75 上跑。**peek 17 候选**（mc 30-80，shard D 域）：hi28t(alanji)=UI how-to 找选项·hojhc(aocao)=仿真提速 debug(U#1 给根因+修复)·ku6wp(kevin3d)=「文件怎么用」Q&A·tjzn5(tongfanl)=研究环境/检查文件 Q&A·5u4s2(e0025730)=业务场景 模拟电路生成 /lvlshft(skill 触发需 live pyaether)·ew6gi(rongjiez)=debug pyaether 报错·krjo2(lizwen)=打pin报错 debug·97g9m(e0039602)=分析 fsdb 信号·0h1pb(chengk)=读代码给流程图 analysis·cq860(thomasz)=★clean produce(写 test.py 插 R_mid/R_out 到 .ends 前)但**已是 #314 DlygResInsert**·4ne3u(e0023936)=★clean produce(Tcl ACE FM 瞬时频率)但**已是 #315 FmInstFreq**·ziv3j/ku6wp 等 nturns=0 经全文件重读仍 Q&A。**结论**：中等 mc(30-80)池 Q&A/debug/analysis 占主导，clean produce 已被 #314-316 取走。**下轮**：用 designflow/peek_dirbased.py 批量 peek fresh_D317_avail.tsv 剩余 ~159 候选（schematic_netlist/waveform/analog 域优先），找 clean A-faithful produce 交付。**教训**：(1) cline 存储目录化——peek 必须用 `<sid>/<sid>.messages.json` 路径 + 解析 `data["messages"]` 的 content list；(2) 选料去重必须 `pool−peeked−ledger` 三集相减，仅 `−peeked` 会重选已做 case；(3) 中等 mc 池 produce 密度低，下轮可放宽到 mc 15-30（shard A 已放宽先例）或 peek 更高 mc(80-150) 大 trace 的早期 produce 轮。脚本已存 designflow/peek_dirbased.py + designflow/fresh_D317_avail.tsv。
- 2026-11-06 18:3x | shard D #316 | **交付 ToggleCounterBindGen-001（schematic_netlist, track=faithful A-grade, L1 真跑候选, 16 条件 a-p）**。open_session shardD_20261106_shardD-pick316。**选料**：fresh_D306_pool.tsv(262 fresh) rank 206-262 共 57 候选未 peek → 写 peek_D316.py（57 targets，max_workers=20 并发 ssh 从 .75 到各机）→ 本机直 ssh 全超时(网络隔离)→改在 .75 上跑 peek_D316.py（.75 免密到 697/698）成功 329 行 peek_out。逐条审 57 候选 A-faithful produce-task：多数为诊断/Q&A/教学/analysis（pcb1x=skill 抓 Pin List 但需 live Virtuoso·k3qx4=高亮 net·9p8g2★=python 脚本生成 toggle_counter.sv·y9y0f=重跑 finesim 需真工具·bgrlw=读网表非 produce·a6f6r=说明 tcl 逻辑非 produce）。**clean A-faithful produce + 离线可验 = 9p8g2**★(clwang@10.129.2.14 mc31, schematic:110 pyaether:25)。**深读 9p8g2**：scp msgs.json(3.4MB) 到 .75 workdir → deepread.py 提取 user turns + assistant tools。**U#0 逐字**(唯一 A-faithful produce)「输入件目录是/home/clwang/test；编写一个python脚本，通过bind的方式，对文件cellname中的cell的输入输出信号添加信号翻转计数，具体的cell定义在cell_define.sv文件中，自己定义一个统计信号翻转的module，把定义的moudle和bind代码放在一个文件,文件名叫toggle_counter.sv」(纯提需求未给根因/修复→A-faithful)。U#91「修改了输入件，请重新执行」为细化非 produce。agent 受 policy-engine writableRoots 限制逐块 editor 写 add_toggle_counter.py + toggle_counter.sv，多次 search_codebase 30s 超时靠 read_file 分段读 cell_define.sv。**user-accepted 产物**(U#104)：`module toggle_counter_<cell>(input A, input Y,...); logic [31:0] cnt_A; always @(A) cnt_A<=cnt_A+32'd1; ... endmodule` + `bind <cell> toggle_counter_<cell> u_<cell> (.A(A),.Y(Y));`；input/output 端口都监测(输出作 counter 的 input)，inout/电源轨排除，32-bit 计数器。**真实输入**：cellname.sv(最终 invx1/nand2Lx1/oai21GFx3 3 cells) + cell_define.sv(真实 8711 行非 ANSI 库)。**合成**：trace 有 user-accepted 产物→A-faithful；真实 /home/clwang/test 不可附加→assets 用真实 cell_define 子集(extract_A.py 抽 7 真实 module 含 3 targets+4 distractors, 277 行)+真实 cellname，hidden B/B2 合成不同 cells。**hidden B**：bufx1/nand3Px1/oai22x/mux2busx(含总线 [3:0] D0/D1/Y + 电源 vdd/gnd)。**hidden B2**：invxZ/and2x/nor2Qx + cellname 含 notexistX(缺失 cell 测优雅跳过)。**反硬编码三轴**：A/B/B2 cell 名完全不相交 + B 含总线端口测范围处理 + B2 含缺失 cell 测鲁棒性。金标 add_toggle_counter_ref.py：argparse(--celldef cell_define.sv / --celllist cellname[→.sv] / --output toggle_counter.sv)；parse_design(非 ANSI：module 名 + body input/output/inout 行 + 端口名/范围/方向)；monitored 仅 input+output；gen_counter_module(input decl + logic[31:0] cnt_ + always@(p) cnt<=cnt+32'd1) + gen_bind(.p(p))；缺失 cell stderr 警告不崩。**16 条件 a-p**：a zip 含.py 无禁 import/路径 b py_compile c B-run exit0+非空 d B 每 cell 有 module toggle_counter_<cell> e B 每 cell 有 bind f B 计入所有 input(cnt+always@) g B 计入所有 output h B inout/电源不计数 i B bind 连每个信号(.p(p)) j B 总线范围保留(mux2busx [3:0]) k 反硬编码 A:源码无 A cell 名+A-run 产 invx1(A,Y)+bind l 跨输入 B2:产 invxZ/and2x/nor2Qx 正确端口 m 缺失 cell 优雅(B2 notexistX 跳过不崩) n 确定性 3 次重跑 sha256 一致 o 计数器递增(cnt<=cnt+) p 单文件含 module+bind。**自验**：ref PASS 16/16；10 negative 全 FAIL(empty_shell/syntax_err/print_expected_B/hardcode_a/no_inout_filter/output_not_counted/no_bind/no_increment/nondeterministic/ref_core_deleted)NEG_RC=0 NEG_SELFTEST PASS；§4.9 三假{empty_shell,print_expected_B,ref_core_deleted}全 FAIL；确定性 3 次 PASS；test==disk sha 1524d87aed36be42 GATE PASS k=16。台账 mark 9p8g2→case；schematic_netlist 83→84；D.jsonl 153→154。**教训**：(1) **本机不能直 ssh 698 机**（网络隔离全超时）→ peek/深读脚本必须经 .75 中转（.75 免密到 697/698）；(2) **9p8g2 是干净 A-faithful + 离线可验好范式**：python 生成器读 cell 库→emit SV，纯文件 in/out，真跑候选只需 python3 subprocess，无需 EDA 工具；(3) **非 ANSI cell 库解析**（module header 列端口名 + body input/output/inout 行带方向/范围）是核心难度，naive 正则易漏范围/方向；(4) **反硬编码靠 A/B/B2 cell 名不相交 + B 总线 + B2 缺失 cell**，硬编 A 输出者 B 上 d/e/j FAIL，不处理缺失 cell 者 m FAIL；(5) **bind-based toggle counter**（input/output 都监测、inout 排除）是 schematic_netlist L1 可验好范式，16 条件天然丰富。**下一步**：fresh_D306 pool rank 206-262 已 peek 完，下轮需 trace_ledger refresh 生成新 fresh 池再 peek。
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
