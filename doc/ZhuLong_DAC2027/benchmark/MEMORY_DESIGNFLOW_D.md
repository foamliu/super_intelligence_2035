WAITING: 0
SHARD: D (netlist_wave)
DOMAINS: analog_context, schematic_netlist, waveform
DEBT: 0（#349 已合成 FFLatchExtract-001；⚠️ L1/L2 比例债仍存，下轮继续优先 L2 produce）

- **PHASE**: shard D 运行中。已交付 180 条 case（D.jsonl 180 行：analog_context:43/schematic_netlist:99/waveform:38）；台账 case-mark 178 + 1011 parked = 1190 已动过。**本轮 #349 = 交付 EDA-Eval-DesignFlow-FFLatchExtract-001**（schematic_netlist, ew6gi/rongjiez/mc53, B-grade synthesized **L1**, 16 条件 a-p；结构化网表→FF/Latch 候选提取器 ff_latch_list.json+report.md）。**选料**: fresh_D319_avail(mc≥15) 排除 ledger 后 143 fresh；.75 ssh 并发 peek 12 候选(rzitp NO_FILE/ypwty skill 写作 weak/4qpyk DDR config shift debug/ku6wp PDN sim Q&A/qe1va+acdfh 「启动业务场景」boilerplate weak/ntduw 0 turns/zw6mx 工作目录配置 weak/65lrn chitchat/h1v18 smash 快捷键 weak/0qyc2 SpiceAgent 跑 sim 不可移植/**ew6gi ★ FF/Latch cell list 提取 skill 调试** → claim→schematic_netlist)。深读 ew6gi.json(54 msgs)：assistant 诊断 5 bug(对 None 迭代崩溃/list(string) 拆字符致环路检测失效/dbOpenCV viewType 默认 layout 非 schematic)。A-faithful 不可行(U#0 调试请求非 produce + live schematic 不可附加)→B 级合成：facet=结构化网表→FF/Latch 提取器(gen_ff_latch_extract.py --netlist/--outdir)。检测三类：self_loop(输出网回自身输入)/cross_coupled(两门互耦)/master_slave FF(两锁存对级联+时钟互补 c[l]?k 正则兼容 clk/ck)。A=netlist_A.txt(SYNC_CORE_A 8 inst:SRN1/SRN2 SR 锁存+MF1/MF2 master(clk)+SF1/SF2 slave(clkb) FF+CINV1/CAND1, n_latch2/n_ff1/n_comb2)；hidden B=netlist_B.txt(SEQ_BLK_B 12 inst:2 cross-coupled NAND2 锁存+master-slave FF+BS1 self-loop+3 comb, n_latch5/n_ff1/n_comb3)；hidden B2=netlist_B2.txt(LATCH_ONLY_B2 5 inst:1 cross-coupled+1 self-loop+2 comb 无时钟网, n_latch3/n_ff0/n_comb2)。反硬编码五轴：design/inst/net 名全不相交+n_ff 1/1/0(B2 无 FF)+源码禁 10 A 字面量+A-run design==SYNC_CORE_A。check 16 条件 a-p(zip+py_compile/B-run exit0+2文件/9 顶层键/design==SEQ_BLK_B/n_inst==12/n_latch==5/n_ff==1/n_comb==3/latch 5 字段/method∈{self_loop,cross_coupled}/cross_coupled partner≠inst loop_nets≥2/self_loop loop_nets≥1/ff master_slave+master/slave/clock_nets 各 2/BX1 在 comb 不在 latch/report Summary+每 latch/ff 节/反硬编码无 A 字面量+A-run design==SYNC_CORE_A+跨输入 B2 n_latch3/n_ff0/design==LATCH_ONLY_B2+3x sha256)。自验：ref PASS 16/16 + 5 negatives 全 FAIL(empty_shell→b/hardcode_a→d/print_expected→p/ref_core_deleted→f/naive_stub→j, **5 distinct first_fail**) + §4.9 三假全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。⚠️ L1/L2 比例债未还(本 case 亦 L1，fresh 池 mc≥40 peek 12 候选仅 ew6gi 可用，印证 #317/#332/#345-348 连续 6 轮 clean L2 produce 稀缺)，下轮继续优先 L2/L3(可降 mc 阈值到 ≥10 或扩 peek mc 15-40 区段)。台账 mark ew6gi→case；case-mark 177→178；schematic_netlist 98→99；D.jsonl 179→180。深读笔记 designflow/trace_deepreads/ew6gi_fflatch_extract.md。**#348**：htwv2→LvsRuleAudit-001（已归档于流水）。**#347**：194wf→AnalogGroupRoleInfer-001（已归档）。
- (归档批次 2032) 历史 #327 ShortCfgTrace-001 选料/合成流水已搬 MEMORY_D_archive.md
- ⚠️ **关键发现（cline 存储变更）**：cline session 存储现为**目录式** `/home/<user>/.cline/data/sessions/<sid>/<sid>.messages.json`（非根目录 `<sid>.messages.json`）。messages.json 格式 = `{"version":1, ..., "messages":[{"role":"user","content":[{"type":"text","text":"<user_input mode=\"act\">..."}]}]}`（content 是 list，非 str）。旧 peek 脚本（peek_211/216/218/D313/D316）用根目录路径，现在会全部 NO_FILE。**已写修正版 designflow/peek_dirbased.py**（目录路径 + 解析 data["messages"] + content list）供下轮复用。下轮 peek 必须用此版。
- ⚠️ **选料去重 bug 修复**：fresh_D306_pool.tsv 是 #306 时构建的快照，之后台账增长（#314-316 claim 了 cq860/4ne3u/9p8g2 等），这些 session 仍在旧 pool 里。`comm -23 pool_sids peeked_sids` 只排已 peek，**漏排已入台账的**→会重选已做 case（本轮误把 cq860 当 fresh，claim 时 REFUSED 才发现已是 #314）。**正确口径**：fresh_avail = pool_sids − peeked_sids − ledger_sids（已存 designflow/fresh_D317_avail.tsv，176 行）。下轮直接用此文件。

- (归档批次 63) 历史 #268 CellPrefixExtract-001 选料流水已搬 MEMORY_D_archive.md
- 每轮做 1 条 case：trace_ledger.py --shard D next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_D.jsonl → 日报
- ⚠️ **台账/排除集修复**：trace_ledger.py `next` 生成的 awk 排除集有 digit 转写 bug（如 `1790142103120_n91pk` 实际应为 `1790142100320_n91pk`），且 excl 条目带 `.messages.json` 后缀而 summary.tsv session_file 也带后缀、awk `sub` 剥后缀后两边不匹配 → 已交付 session(n91pk/wg5u2/wb03t/4a852) 漏排重返候选池。**本轮改用 4-shard TSV 实读 262-anchor 排除集 + awk BEGIN 对 excl 也 `sub(/\.messages\.json$/,"")` 双边剥后缀**（designflow/_tmp/excl_all.txt，运行后清理），得真 fresh 候选。建议运维修 trace_ledger.py：(1) anchor 从 TSV 直读勿二次转写；(2) 排除匹配双边剥 `.messages.json`。
- 📊 trace 覆盖率：178 / 1511 = 11.8%（mc>=30 候选池；D.tsv 现 178 case-mark + 1011 parked · 已动过 1190；快照 2026-11-07 04:52 sessions=3896 mc300=347 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 180 行）：analog_context:43 · schematic_netlist:99 · waveform:38。**#349**：ew6gi→EDA-Eval-DesignFlow-FFLatchExtract-001（已交付）。**#348**：htwv2→EDA-Eval-DesignFlow-LvsRuleAudit-001（已交付）。**#347**：194wf→EDA-Eval-DesignFlow-AnalogGroupRoleInfer-001（已交付）。**#346**：选料/深读轮 DEBT:1（已归档流水）。**#345**：lp4xw→FineSimDeckReport-001（已归档）。**#344**：l5r0u→IOBufParamTune-001（已归档）。**#343/#342**：选料轮（已归档）。**#341**：ca92c→AnalogGroupCfgMergeDummy-001（已归档）。
- 📦 体积：TASK_D≈25KB / MEMORY_D≈待测（#347 PHASE+流水更新；下轮视体积归档 #345 及更早流水到 MEMORY_D_archive.md）
- DEBT: 0（#349 已合成 FFLatchExtract-001；⚠️ L1/L2 比例债仍存，下轮继续优先 L2 produce）。**下轮 #350 第一件事**：trace_ledger.py --shard D next 取新候选 → 优先 L2/L3 produce（fresh 池 clean L2 稀缺，可降 mc 阈值到 ≥10 或扩 peek 到 mc 15-40 区段；连续 6 轮 #317/#332/#345-349 顶/中 mc 池 L2 produce 稀缺，可考虑跨 shard 共享 L2 trace 或扩 scan 源）。
- 🧾 断言: k_rationale=k_check=16 ✓（#349 FFLatchExtract-001，16 条件 a-p 全对账；#348/#347 亦 16 条件 a-p）。存量 180 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。rewrite_queue.tsv 全部 done（无待修）。今日 132/180 达标（#349 新增 1 条达标）。

## 流水
- 2026-11-07 11:0x | shard D #349 | **交付 EDA-Eval-DesignFlow-FFLatchExtract-001**（schematic_netlist, ew6gi/rongjiez/10.129.2.11 mc53, B-grade synthesized **L1**, 16 条件 a-p）。open_session default_designflow_shardD_shardD-349-peek_0（peek 用，已 declare_done+close）。**选料**: fresh_D319_avail(mc≥15)排除 ledger 后 143 fresh。.75 ssh 并发 peek 12 候选(peek_D349.py 目录式 messages.json): rzitp(NO_FILE)/ypwty(skill 写作指南+group generate weak)/4qpyk(DDR5/DDR6 finesim config_pincheck shift debug 16 turns)/ku6wp(PDN sim 文件用法 Q&A weak)/qe1va+acdfh(「启动业务场景:仿真与验证」boilerplate 1-3 turns weak)/ntduw(0 user turns)/zw6mx(工作目录配置 weak)/65lrn(hello/who are you chitchat)/h1v18(smash 快捷键/连续copy skill Q&A weak)/0qyc2(SpiceAgent 跑 sim tb_ibis_link.sp 不可移植)/ew6gi(★FF/Latch cell list 提取 skill 调试 produce facet)。**选 ew6gi**→claim→schematic_netlist。**深读** ew6gi.json(247KB/54 msgs/3 user turns)：U#0 逐字「cxmt_getLatchFFCellList.il是virtuoso的一个脚本，实现了获取电路中可能的FF/Latch cell list，cxmt_getLatchFFCellList.py是把这个skill脚本翻译成aether的pyaether脚本，但是现在pyaether脚本跑出来的结果和skill的结果不一样，甚至有时会直接报'NoneType' object is not iterable，输出文件是空的，请你帮我看下问题出在哪里，先不要直接修改我的文件」。assistant MSG#13 诊断 5 bug: ①对 None 迭代崩溃(etMakeTable 默认 None，SKILL foreach nil no-op vs Python for x in None TypeError) ②list(string) 拆字符(SKILL list(x) 单元素表 vs Python list("CK")=['C','K']，致 ae.member 永不匹配→环路检测失效) ③dbOpenCV viewType 默认 layout 非 schematic(应用 dbOpenCVByType 显式传)。**A-faithful 不可行**(U#0 调试请求非 produce + live schematic 不可附加)→**B 档 synthesized**：facet=结构化网表→FF/Latch 候选提取器。**合成** gen_ff_latch_extract.py --netlist/--outdir 解析 `# design:<NAME>`+`INSTANCE <inst> <cell> <pin>:<dir>:<net> ...`(dir∈{in,out,inout}，schematic instTerms 方向可移植表征)，检测三类：self_loop(inst 的 out 网同时是其 in 网)/cross_coupled(两 inst A,B 互耦 A.out→B.in 且 B.out→A.in)/master_slave FF(两 cross-coupled 对，master 时钟网 CK+slave 互补网 CKB+master 输出被 slave 读取级联；c[l]?k 正则兼容 clk/ck/clkb/CKB；构成 FF 的 4 inst 从 latch 移除归 ff)，emit ff_latch_list.json(9 顶层键 design/n_instances/latch_candidates/ff_candidates/feedback_paths/n_latch/n_ff/combinational_cells/n_combinational + 每 latch 5 字段 inst/cell/method/partner/loop_nets + 每 ff 5 字段 name/method/master_insts/slave_insts/clock_nets)+report.md(## Summary+每 latch `## Latch:`+每 ff `## FF:`)。**A=netlist_A.txt**(SYNC_CORE_A 8 inst: SRN1/SRN2 NOR2 SR 锁存(Q/QBAR 互耦) + MF1/MF2 NAND2 master(clk 互耦 MF1Q/MF2Q) + SF1/SF2 NAND3 slave(clkb 互耦 SF1Q/SF2Q + c:in:MF1Q 级联) master-slave FF + CINV1 INV/CAND1 AND2 comb, n_latch=2/n_ff=1/n_comb=2)。**hidden B=netlist_B.txt**(SEQ_BLK_B 12 inst: L3a/b+L4a/b 两 cross-coupled NAND2 锁存 + L5a/b NAND2 master(CK)+L6a/b NAND3 slave(CKB) FF + BS1 NOR2 self-loop(FB) + BX1 BUF/BX2 XOR2/BX3 OR2 comb, n_latch=5/n_ff=1/n_comb=3)。**hidden B2=netlist_B2.txt**(LATCH_ONLY_B2 5 inst: BR1/BR2 NOR2 cross-coupled(Q2/Q2N) + BS2 NAND2 self-loop(FB2) + BC1 INV/BC2 NAND3 comb 无时钟网→无 FF, n_latch=3/n_ff=0/n_comb=2)。**反硬编码五轴**: design SYNC_CORE_A/SEQ_BLK_B/LATCH_ONLY_B2 全不同；inst SRN1/MF1 vs L3a/L5a vs BR1/BS2 全不相交；net QBAR/clkb/MF1Q vs QB_N/CKB vs Q2N/FB2 全不同；n_ff 1/1/0(B2 无 FF，硬编 1 者 B2 p FAIL)；源码禁 10 A 字面量(SYNC_CORE_A/SRN1/SRN2/MF1/MF2/SF1/SF2/QBAR/clkb/MF1Q)；A-run design==SYNC_CORE_A。**check 16 条件 a-p**: a(zip 防泄漏 check/reference/negative/jsonl/hidden/_tmp+py_compile)/b(B-run exit0+ff_latch_list.json+report.md)/c(9 顶层键)/d(design==SEQ_BLK_B)/e(n_inst==12)/f(n_latch==5)/g(n_ff==1)/h(n_comb==3)/i(latch 5 字段)/j(method∈{self_loop,cross_coupled})/k(cross_coupled 存在 partner≠inst 且 loop_nets≥2)/l(self_loop 存在 loop_nets≥1)/m(ff master_slave+master_insts2+slave_insts2+clock_nets2)/n(BX1 在 comb 且不在 latch)/o(report Summary+每 latch/ff 节)/p(反硬编码源码无 A 字面量+A-run design==SYNC_CORE_A+跨输入 B2 n_latch3/n_ff0/design==LATCH_ONLY_B2+3x sha256 一致)。**自验**: ref PASS 16/16 + 5 negatives 全 FAIL(empty_shell→b 无文件 / hardcode_a→d design 硬编 SYNC_CORE_A≠SEQ_BLK_B / print_expected→p 硬编 B 输出致 A-run/B2-run design 错 / ref_core_deleted→f 删 FF 检测致 n_latch=9≠5 / naive_stub→j method="latch" 非法枚举，**5 distinct first_fail b/d/p/f/j**) + §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。台账 mark ew6gi→case(FFLatchExtract-001)；case-mark 177→178；schematic_netlist 98→99；D.jsonl 179→180。**教训**: (1) **FF/Latch 反馈环路检测是 schematic_netlist L1 可验好范式**: self_loop/cross_coupled/master_slave 三类+inst/net 方向→16 条件天然丰富，与 AnalogGroupRoleInfer(@group 注释)/LvsRuleAudit(SVRF 模块) facet 不同无重复；(2) **时钟网正则须兼容 clk/ck 两拼写**: `(?i)c[l]?k` 匹配 clk(c-l-k)与 ck(c-k)及 clkb/CKB，原 `ck` 漏 clk 致 A FF 漏检(n_ff=0)；(3) **确定性须排序 set/dict 迭代**: Python hash 随机化致 set 迭代序跨进程不同→JSON 字段序变→sha256 不一致，`sorted(all_nets)`+`sorted(edge_map.keys())` 修复；(4) **anti-hardcode 字面量勿出现在 ref 源码注释**: 「clkb」作文档示例写进 _is_clk_net 注释→误命中 A_LITERALS 子串检查→改「complementary clock bar」；(5) ⚠️ **L1/L2 比例债仍存**: 本 case 亦 L1，fresh 池 mc≥40 peek 12 候选仅 ew6gi 可用(L1 facet)，印证 #317/#332/#345-348 连续 6 轮 clean L2 produce 稀缺，下轮继续优先 L2/L3。附件 assets/FFLatchExtract-001/{prompt.txt,task_brief.md,netlist_A.txt,hidden/{netlist_B.txt,netlist_B2.txt,hidden_manifest.json}}；reference/FFLatchExtract-001/{gen_ff_latch_extract.py,check.py,reference_submit.zip,negative/5 .py+negative_selftest.py}。
- (归档批次 2047) 流水 #345/#346/#347/#348 已搬 MEMORY_D_archive.md（4 条大流水，#349 PHASE+流水已含摘要）
- (归档批次 2046) 流水 #344/#343/#342/#341 已搬 MEMORY_D_archive.md
- (归档批次 2045) 流水 2026-11-07 06:2x #340 NetlistBisectLocalize-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2043) 流水 2026-11-07 #335/#336/#337 已搬 MEMORY_D_archive.md（#335 FineSimDataParse-001 / #336 LdoCircuitReport-001 / #337 选料轮 DEBT:1）
- (归档批次 2044) 流水 2026-11-07 #338 MbistCellFind-001 全文已搬 MEMORY_D_archive.md
- (归档批次 2039) 流水 2026-11-07 03:2x-04:0x #334 选料/peek 轮 已搬 MEMORY_D_archive.md
- (归档批次 2036) 流水 #333 (WvSigListGen-001, waveform, B-grade synthesized, 16 条件 a-p) 已搬 MEMORY_D_archive.md/Vdd_ac), 越负越好, @100kHz 预计 -5~+10dB 不满足 -20dB」+ corners tt/ff/ss + Cout2nF ESR3ohm）+ dut_ldo_v1.sp（.SUBCKT ldo_v1 vdd vout gnd vref en：5T EA=nMOS diff X1/X2 ntn w5u l2u (gate=vref/vfb, src=tail_n) + pMOS mirror X3/X4 ptn w5u l2u (X3 diode-conn gate==drain=ea_out) + bias X5/X6 ntn_m w6u/w2u l2u + Rbias 290k vdd→vb_tail + PMOS pass Xpass ptn w5u l0.3u **nf200** (drain=vout gate=ea_out src=vdd) + R1 100k vout→vfb + R2 1.1M vfb→gnd (ratio → vfb=0.825 → vref≈0.825) + Cout 2n vout→vout_esr + Resr 3 vout_esr→gnd）。**A-faithful 判定**：U#0 纯 produce + user-accepted 产物存在 + 真实 spec/dut 可提取 → **A-faithful 可行**；但产物在 /home/jessegao（非便携）+ live SPICE 验证（PSRR/gain/PM）→ **B 档 synthesized**：spec-driven LDO deck+report 生成器（gen_ldo_design.py --spec --outdir → dut.sp+tb_ac+tb_loadreg+tb_linereg+tb_psrr+report.md），check 验**结构**不验 sim 结果（无需真跑 SPICE，L1 离线可验）。**本轮因 40min 预算耗尽未能合成** → parked z5ett 留 #335 合成（DEBT:1）。深读笔记 designflow/trace_deepreads/z5ett_ldo_design.md（含真实 spec+dut 拓扑+合成 plan+check 12-16 条件清单）。**7 weak 候选已全部 parked** 防止重选（jsb4j/npkmm/ld0p8/nibwl/ewjnc/wsi93/4vv1y）。台账 case-mark 168 + parked 895 = 1063 已动过；analog_context 33/schematic_netlist 81/waveform 33 不变；D.jsonl 169 行不变。**断言闸门**：本轮无 case 交付，k 断言不适用。**教训**：(1) **fresh_D317_avail 池顶部 mc 137-196 区段 produce 密度极低**（8 中 7 weak，仅 1 A-faithful），印证 #317/#332 结论「中等 mc 池 Q&A/debug/skill 占主导」；(2) **z5ett 是干净 A-faithful LDO produce 范式**：spec-driven deck 生成（5T EA+PMOS pass+divider+Cout/ESR）是 analog_context L1 可验好范式，spec→器件参数映射明确（pass W/nf 由 iload+vdrop 推，divider ratio 由 vout/vref 推），16 条件天然丰富（拓扑/测试台/报告/跨输入/确定性）；(3) **PSRR 负值声明是强反硬编码轴**（U#1 用户澄清「psrr 为负值」），report.md 必须含「越负越好」声明，naive 写正数者 FAIL；(4) **ssh cat 拉 messages.json 须用 ip 不带 user**（.75 e0031982 免密到 697/698，但 scp/jessegao@ 失败 Permission denied；peek 脚本用 `ssh ip cmd` 不带 user 才通）；(5) **选料/peek 轮需把 weak 候选全部 park** 防止下轮重选（本轮 7 条全 parked）。open_session default_designflow_shardD-333_0。**选料**：fresh_D319_avail(mc>=30)池 #329 已确认 clean produce 耗尽；本轮 peek 5 条 parked cross-shard dup 候选(ooyxi=sophiaw NO_FILE / 314mt=sophiaw 0turns / x2w2z=yueliu L2 FineSim fqueue batch / fkprl=e0014566 L2 layout RTEXT/RNODE / u78sz=hengbow ★waveform .sig 生成)→选 u78sz 跨 shard 共享(继 #331 6qt0a、#332 ahjnv 第三例)。u78sz(hengbow/hfeg0pgn045 mc407, ledger parked note「cross-shard dup = A CoreTimingSig-001 (verification)」)已被 shard A 取 verification L2 意图(coretiming 时序违例检查/分析)；本 case 取**同 trace 不同意图**=waveform L1 离线 .sig 信号列表生成器，无 FSDB/waveview/fscript 依赖。在 .75 deepread_u78sz.py + deepread_u78sz_sig.py 提取 511 msgs/25 user turns + assistant tool_use(.sig writes)：U#2「检查 ddr5 fullchip array coretiming+时序违例，找开启地址对应 wl 和 BL」+U#4「给出关键信号的路径 list，waveview 下直接 load」+U#5「把你找的信号也弄成 sig_demo.sig 格式」+U#8/U#13/U#24「wv 只认小写」+U#11「分五个文件我一次只能 load 一个」+U#16/U#17「根据 netlist 找真实层次不猜测」。**A-faithful 不可行**：真实 /home/hengbow fsdb(2GB)+netlist(公共目录)不可附加 + live waveview/fscript 不便携 → **B 档 synthesized**。**合成**：gen_wv_sig.py(--spec <spec.json> --outdir <dir>) 读 spec JSON{design,n_files,groups:[{name,file,signals:[...]}]}，_split_leaf(路径按 . 拆 parent+leaf)+_format_signal(顶层 signal=v(leaf)/层次 signal=parent.v(leaf) **全小写**，总线位 <n> 保留)+gen(每组一 .sig 文件+# group/# design 注释+单文件去重+manifest.json{design,n_files,total_signals,files:[{name,n_signals}]})。A=spec_A.json(DDR5_CORETIMING 5 groups 84 signals: 01_top_pad 23/02_read_pad 29/03_controller 6/04_array_addr 16/05_array_bl_wl 10，真实 trace 信号 ck_t/ca<0..13>/ldqpad<0..7>/cm1_fc_rdlatencyto56/ra10<0..3>/ra10gapin<0..3>/ble_b<0..3>/wlr<0>)；hidden B=spec_B.json(LPDDR4_PHY **4 groups** 46 signals, PHY_top 层次, ck_p/cmd<0..6>/dq<0..7>/phy_rdlat_sel<0..2>/rowa<0..3>/wlx<0..1>，与 A 信号名全不相交)；hidden B2=spec_B2.json(SERDES_ANALOG **3 groups** 19 signals, serdes_top 层次, **全标量无总线位** vddl!/vbg/ibias/pfd.up/cp_out/vco_ctrl/drv.outp/dfe_tap，测无总线处理)。反硬编码五轴：design DDR5/LPDDR4/SERDES 全不同；group 数 5/4/3→输出文件数不同(硬编 5 者 B 上 g FAIL)；信号名全不相交(硬编 A 信号者 B/B2 上 i/n FAIL)；层次前缀 xictop/PHY_top/SerDes_top 全不同；B2 无总线位(不处理标量者 o FAIL)。金标 gen_wv_sig_ref.py。check.py 16 条件 a-p：解 zip(防 check/reference/negative/jsonl 泄漏)→py_compile→B 真跑 subprocess(spec 路径 abspath 化)→全小写(WaveView 硬约束, 字母检查)→v(leaf)/path.v(leaf) 格式(正则, 总线 <n> 允许在 v 内)→无 [ 方括号(必须 <>)→.sig 文件数==spec_B group 数 4→manifest 文件名集==实际+各 n_signals==实际行数→每 .sig 文件含其 group 全部叶子(去重后)→. 层次分隔(无 / 或 ::)→单文件无重复 signal=→# 注释存在且不被计为 signal→反硬编码源码无 A 标记(ck_t/cm1_fc_rdlatencyto56/ra10gapin/ble_b<0>/xictop.xi_array8g_t)+A-run 产 v(ck_t)+v(ca<0>)→跨输入 B2-run 产 serdes_top+group 数 3≠4→B2 所有 signal= 行无 <(全标量)→3 次确定性 sha256。自验：ref PASS 16/16 a-p + 6 negatives(empty_shell→c / hardcode_a→g / no_lowercase→d / no_split→g / print_expected→c / ref_core_deleted→e)全 FAIL + §4.9 三假(empty/print_expected/ref_core_deleted)全 FAIL。**断言闸门** k_rationale=k_check=16 ✓。**教训**：(1) **跨 shard trace 共享第三例验证可行**：u78sz 已被 A 取 verification L2(coretiming 时序违例检查)，本 case 取同 trace waveform L1 离线 .sig 生成——不同意图+domain+L-level+check，parked note「D does not rebuild」可被 mark 覆盖（继 #331/#332 模式，parked 行保留 note + 新 case 行加 case_id）；(2) **WaveView 全小写是强反硬编码约束**：用户反复强调(U#8/13/24)「wv 只认小写」，生成器必须 lowercase 全部路径——naive 保留原 case 者 d 上立即 FAIL；(3) **.sig 格式 = signal = path.v(leaf)** 是 waveform L1 可验好范式：叶子 v() 包裹 + 点分层次 + 总线 <n>，16 条件天然丰富(格式/小写/分文件/去重/manifest/跨输入/确定性)；(4) **B2 全标量无总线位**是额外反硬编码轴：不处理标量(总输出 <n>)者 o 上 FAIL；(5) fix bug: check.py (e) 正则 v\([^()<>]+\) 会拒总线位 <n>，改 v\([^()]+\)（v 内允许 <> 仅拒括号）；(6) fix bug: _run_candidate subprocess cwd=tmp_out 需 spec 路径 abspath 化，否则相对 spec 路径解析失败。台账 mark u78sz→case；waveform 32→33；D.jsonl 168→169。
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
