# §4.9 Anti-Hardcode 普查报告（全 Bench 抽样首版）

> 生成时间：2026-11-21 17:4x · 执行方：shard D · 依据：2026-11-21 17:0x 用户令「全 bench §4.9 anti-hardcode 普查放行，让 D 执行」
> 数据文件：`designflow/anti_hardcode_audit_all.tsv`（635 行）
> 普查脚本：`designflow/_audit_antihardcode_static.py`（静态筛查）+ `designflow/_gen_audit_tsv.py`（统一 TSV 生成）
> 题库根：`/nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow`（脚本默认 --bench-root 指向此处）

## 0. TL;DR（先看结论）

- **普查范围**：D 全量 560 条 + A/B/C 各抽样 25 条（优先抽 k<12 老题），合计 **635 条**。
- **判定**：**PASS 44 · GAP 568 · WEAK 4 · MISSING 16 · 其它 3**。**GAP 率 ≈ 89.8%**。（D 已修 26 条 → D 计 PASS 104 / GAP 445）
- **核心病灶**：绝大多数 `check.py` **只跑 hidden B、无 A-gold 交叉校验**（无嵌入 A fixture、不在 A 上跑候选）。审计方构造一个"忽略输入、直接吐出 B 的 gold 输出"的假提交（`fake_print_only`），即可 PASS 全部断言——违反 §4.9 (b)(c)。
- **修复进度**：D 已修 26/505（r1059–r1153），最新 r1153（2026-11-22）修 NetlistUlvtDelvtoInject-001（k=12→20，schematic_netlist/HSPICE ULVT vth-shift 注入 Produce→script-deliverable）。病灶=原 12 断言只跑隐藏 B(a-l)无 A'/B' 交叉，静态 vuln: subprocess on B only, no A-gold cross-check。修复：新增隐藏 B' `netlist_Bprime`（顶层 LDQ_Driver，5 ULVT 实例 XULP0/XULP1/XULN0/XULN1/XULN2 与 B 的 XPM2/XNM6 全不相交，B'-only token LDQ_Driver A/B 均无），8 B' 交叉断言(m-t: run/行数/仅ULVT改/pulvt/nulvt/非ULVT不变/LDQ_Driver token/源码禁含 WCK_C2C_RFB|LDV_Driver)。smart B-hardcode stub(内嵌 B 完整预期输出 27306B/131行, pass a-l)在 n 击穿(B'行数 131≠33)。§4.9 三假 empty→c/print_only→d/core_deleted→c ALL FAIL。ref 20/20 PASS + 4 neg(含 smart B-hardcode)ALL FAIL。次新 r1152（2026-11-22）修 LatchPinReconcile-001（k=12→20，schematic_netlist/LATCH symbol pin 对账 Produce→script-deliverable）。病灶=原 12 断言只跑隐藏 B(a-l)无 A'/B' 交叉；smart print_only/core_deleted stub（读 args.ref 派生 B 字段 + 硬编码 removed_pins=['vcc','vss']，避开 B_HARDCODE_SRC_TOKENS 字面量扫描）runtime 复现 PASS 全 12（§4.9 b/c 违规，运行时已确认 fake_print_only PASS / fake_core_deleted PASS）。修复：新增隐藏 B' `ref_latLV2_symbol.json`（stdcells_io/latLV2，4 pin DIN/CLK/QOUT/QOUTb boundary.drawing）+ 隐藏 A' `current_latch07d_symbol.json`（R2c/LATCH07D 7 pin 含 vdd/gnd/test_en metal1.drawing），A'/B' 与 A/B pin名/偏移/layer/库/cell 全维不相交（文件式落 assets/hidden/，更新 hidden_manifest.json 三件套）；8 A'/B' 交叉断言(m-t)，核心 ⑯ removed_pins==A'\\B'={gnd,test_en,vdd}(≠B-run {vcc,vss})击穿硬编码 stub。smart stub B-side PASS(a-l)→A' FAIL[⑯]。§4.9 三假 empty→④/print_only→⑯/core_deleted→⑯，3 distinct。ref 20/20 PASS + 3 旧 neg ALL FAIL + §4.9 三假 ALL FAIL。**r1152 增益**：schematic symbol-reconcile 类 removed_pins 是唯一需 A\\B 集合差的字段，B_HARDCODE_SRC_TOKENS 字面量扫描无效（stub 读 ref 派生其余字段，仅 removed_pins 硬编码 ['vcc','vss'] 即可绕过，vcc/vss 非 B 特有 token）；须 SUT 不可见的隐藏 A'/B' 交叉击穿。task_brief.md 原已承诺「隐藏测试用一份与 A 完全不相交的参考 B」旧 check 未兑现，本次兑现。次新 r1104（2026-11-22）修 SpfDielectricLeakageQA-001（k=12→18，schematic_netlist/DSPF 介质漏电电阻判定 Q&A→script-deliverable）。病灶=原 12 断言只跑隐藏 B(j-k)+确定性(l)，无 A'-gold 交叉；signature-based smart B-hardcode stub（读 deck 检测 ROmulti_B/SS_40→B-gold / ROmulti/TYP_98→A-gold / unknown→B-gold fallback，spf_leakage_report.json 预焙 A-gold）runtime 复现 PASS 全 12（§4.9b 违规）。修复：新增隐藏 A'（reference/hidden_a/ROmulti.spf.FF_125_RCC，FF_125/ROmulti_Ap/9 nets/61 R/5 cross-net R/24 pin-R/60 coupling C，token 与 A(TYP_98/ROmulti/n_000)及 B(SS_40/ROmulti_B)全维不相交，SUT 不可见，文件式规避 base64 腐蚀）+ 6 A'-gold 交叉(m-r)：m A' run exit0+合法JSON含9键 / n A' R_total==61(≠A 13439≠B 9870,核心交叉) / o cross_net_R==5(≠0≠7) / p pin_R==24(≠2280≠1610) / q coupling_cap==60(≠29370≠25600) / r net_sections==9(≠203≠180)。smart stub B-side PASS(a-l)→A' FAIL(n, B-gold 9870≠A'-gold 61)。§4.9 三假 empty→a/print_only→j/core_deleted→g + hardcode_b→n，5 distinct(a,b,g,j,n)≥3。ref 18/18 PASS + 5 neg ALL FAIL。**r1104 增益**：DSPF 寄生网表解析类 case 的 signature-stub 按 SUBCKT 名/CORNER token 检测 A/B 即可区分并吐对应 gold，既有 (j)(k) cross-input guard 仅在 A/B 两集上有效；须 SUT 不可见的第三 corner A'(FF_125/ROmulti_Ap) 交叉击穿，A'-gold 全 5 统计字段与 A/B 全维不相交。r1103 修 CapPropsCalc-001（k=13→18，analog_context/MOS 电容模型参数提取 Produce→script-deliverable）。病灶=原 13 断言只跑隐藏 B+C(a-m)，smart B-hardcode stub（base64 硬编码 B-gold+C-gold 96+4 行，运行时检测 "V3" 区分 B/C，文件名从 os.listdir 读取避开 _B blocklist，base64 不含 _B 故 cond(a) 不拦）runtime 复现 PASS 全 13（§4.9b 违规，C-dataset 交叉 (j) 对硬编码两套 gold 的 stub 无效）。修复：新增隐藏 A'（hidden_a/inputs_Ap，V4_Q namespace，ss corner/ntn_lvss/ptn_lvss，w=0.22u/0.7u，l=0.06u，4 行 gold，token 与 A V1/B V2/C V3 全维不相交，SUT 不可见，文件式规避 base64 腐蚀）+ 5 A'-gold 交叉(n-r：A' run+行数/Cgd0/Ceff/Cox/EOT 匹配 oracle)。smart stub B-side PASS(a-m)→A' FAIL(n-r，A' 非 V3→stub 吐 B-gold 96 行≠A' 4 行)。ref 18/18 PASS + 4 neg ALL FAIL。**r1103 增益**：C-dataset 交叉校验（cond j）对「硬编码 B+C 两套 gold + 运行时 dataset 检测」的 smart stub 无效——stub 只需 base64 两套 gold + 检测 "V3" 即可区分 B/C；必须 SUT 不可见的第三套 A'（V4_Q namespace）才能击穿。同 r1069/r1074 visible-A guard 无效病灶族的又一变体（C-dataset guard = visible-C guard，C 在 workdir/hidden/ 内 SUT 可间接通过运行时检测推断）。r1101 修 AetherNetHighlightQA-001（k=16→21，schematic_netlist/Aether 手册 net-highlight 结构化指南 Q&A→script-deliverable）。病灶=原 16 断言只跑隐藏 B/B2/B3(a-p)，smart signature-based B-hardcode stub（读手册 token 检测 版图→B-gold / GUI点选→B2-gold / aeCreateInst→B3-gold / unknown→B-gold fallback）pre-fix PASS 全 16（§4.9b 违规，已运行时复现 stub B/B2/B3 全 PASS）。修复：新增隐藏 A-prime `aether_manual_Ap.md`（assets/hidden/，高亮删除主题，primary=aeSeRemoveNetHighlight，token 与 A(aeTraceNet/schematic)/B(aeTraceNet/layout/版图/金属线)/B2(seGuiTraceNet/GUI/点选/交互)/B3(aeCreateInst/aeCreateWire) 全维不相交，SUT 不可见，文件式规避 base64 腐蚀）+ 5 A'-gold 交叉(q-u)：q A' run exit0+合法JSON含8键 / r A' primary==aeSeRemoveNetHighlight[核心交叉,击穿 stub fallback 吐 aeTraceNet] / s A' primary 作为 token 出现在 manual_Ap[data-grounded] / t A' procedure_steps 非空且含 aeSeRemoveNetHighlight / u A' api_parameters 含 netName(非 B 的 islayout/layer)。smart signature-stub `neg_fake_hardcode_b.py` B-side PASS(a-p)→A' fallback B-gold FAIL(r)。§4.9 三假 empty→a/print_only→c/core_deleted→b + hardcode_b→r，4 distinct(a,b,c,r)≥3。自验 ref 21/21 PASS + 4 neg ALL FAIL 4 distinct。
- **运行时已确认 GAP（2 条，可复现）**：
  - D `EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001`（k=9，纯报告 grep，无 subprocess）—— **已于 r1083（2026-11-22）修复**：k=9→14。**病灶=analysis-Q&A report-deliverable 类无牙**：原 check 纯子串匹配 `diagnostic_report.md`，shipping `reference_report_B.md` verbatim 即 PASS（print_only PASS 运行时已确认）。**解法=reframe report→script deliverable**（trace agent 实写 analyze_parasitics.py/analyze_sdf.py 故忠实）：交付 `diagnose_parasitics.py` 接收 asset_dir 打印结构化 JSON 诊断，check subprocess 在隐藏 B + 隐藏 A' 上各跑一次校验由输入计算的金值；新增隐藏 A' `hidden_a/`(sdf.tcl GDDR6X/3 read_parasitis + log 1288550/221894/1066656/512/506 + GDDR6X.sdf 4 hier I_PERI0/I_Array8G_T_0/T_1/B_2) 与 A(DDR5TOP/I_BCenter/I_Array6G) 及 B(LPDDR5TOP/I_DCC/I_Array4G) token 全维不相交；14 断言=10 B-side(a-j)+4 A'-gold 交叉(k-n)，smart §4.9(b) signature-stub `neg_fake_hardcode_b`（读 SDF design 查表 DDR5TOP→A-gold/LPDDR5TOP→B-gold/unknown→B-gold fallback）post-fix FAIL[l] A' design=LPDDR5TOP≠GDDR6X，4 neg 全 FAIL n_distinct=3(b/c/l)，ref 14/14 PASS。**增益**：analysis-Q&A/report-deliverable 类判分无牙根因=check 纯文本子串匹配，reframe 为「交付计算脚本 + subprocess 跑隐藏 B/A' 校验计算值」是通用解法。
  - D `EDA-Eval-DesignFlow-AddrRtlGateMap-001`（k=12，Produce 跑 B 但无 A-gold 交叉）—— **已于 r1059（2026-11-21）修复**：k=12→21（12 B-side + 9 A-gold 交叉 m-u），A fixture 落 `reference/hidden_a/`（避免 base64 编辑腐蚀），check 在 A 上 subprocess 跑候选并断言 A-gold，3 假（print_only/core_deleted/empty）全 FAIL，5 neg selftest 全 FAIL。
  - D `EDA-Eval-DesignFlow-AutoCellRmAvPf-001`（k=12，Produce 跑 B 但无 A-gold 交叉）—— **已于 r1060（2026-11-21）修复**：k=12→21（12 B-side + 9 A-gold 交叉 m-u）。A fixture 直接读 `assets/spec.json`+`instance_manifest.json`（judge 可访问，无需 base64/无编辑腐蚀），check 在 A 上 subprocess 跑候选并断言 A-gold（deleted=8 av=3/pf=5，≠ B 的 11）。新增 `neg_fake_hardcode_b.py`（smart §4.9(b) B 硬编码 stub：B 上过 b-l，A 上 dbDelete 不触发→deleted 空→FAIL [o]）为运行时证明；6 neg（5 旧+1 新）全 FAIL，6 distinct labels，ref 21/21 PASS。
  - D `EDA-Eval-DesignFlow-AvcPatternCompare-001`（k=11，visible-A-vs-B + visible-A-vs-A，可见 A 可被 stub 读取特判）—— **已于 r1061（2026-11-21）修复**：k=11→15（a-o）。新增隐藏 A' `pattern_A2.avc`（24 records/8 unique/X@pos1/pos6，SUT 不可见）；check 用判分器独立 `_gt_recount`/`_gt_parse`/`_gt_diff` 重算 A'-gold（A2-vs-A2 shared=8/only=0/bdiff=[]/rc=24/up=8；A2-vs-B shared=1/only_a=7/only_b=11/bdiff=[1,2,4,6]/rc_a=24/rc_b=60），候选须在 A' 上真解析才能匹配。smart §4.9(b) stub（读 visible-A 检测 a==b 硬编码 A-gold+B-gold）pre-fix PASS→post-fix FAIL[m]；6 neg 全 FAIL n_distinct=5，ref 15/15 PASS。此例的病灶是新发现：**visible-A-vs-A 交叉校验无效**（A 在 SUT 沙箱内，stub 可读它特判 a==b），必须用 SUT 不可见的隐藏 A' 才能真正击穿 B-hardcoded stub。
  - D `EDA-Eval-DesignFlow-Schematic-001`（k=8，Produce 跑 B 无 A-gold 交叉）—— **已于 r1062（2026-11-21）修复**：k=8→13（a-m，8 B-side + 5 A'-gold 交叉 i-m）。新增隐藏 A' `reference/hidden_a/Aprime_netlist.v`（4 module A2_*，与可见 A/隐藏 B token 结构性不相交：A2_inv_merge5 5 invDSx1/3 dead，A2_nand_chain3 nand3 3-input，A2_mux_selbar2 in0/in1/seln，A2_latq_keep2；SUT 不可见，文件式规避 base64 编辑腐蚀）。check 在 A' 上 subprocess 跑候选并断言 A'-gold（module 名/inv_base merge/dead 删/nand3 3-input p&q&r 无 s/mux in0/in1/seln/latq trireg+fgc）。新增 `neg_fake_hardcode_b.py`（smart §4.9(b) B-hardcoded stub：检测输入 A→A-gold+A-report 过 h，B→B-gold 过 c-g，A'→fallback B-gold；pre-fix PASS a-h→post-fix FAIL[i] on A'）为运行时证明；5 neg 全 FAIL，ref 13/13 PASS。
  - D `EDA-Eval-DesignFlow-InvSpiceSim-001`（k=11，visible-A 反硬编码 guard (j) 无效：A 在 SUT 沙箱内，smart stub 可读 A 的 vdd 特判吐 A-gold）—— **已于 r1069（2026-11-21）修复**：k=11→16（a-p，11 B-side(a-k) + 5 A'-gold 交叉(l-p)）。新增隐藏 A' `reference/hidden_a/spec_Aprime.json`（vdd=0.9/Wn=1.5u/Ln=0.13u/Wp=3u/Lp=0.13u/CL=25fF/tr=0.2ns/pts=51，与 A vdd=1.2/B vdd=1.05 token 结构性不相交）。判分器内联 `_judge_gold`（Shockley 长沟道模型，独立于候选实现）重算 A'-gold（voh=0.9/vm=0.450139/NMH=NML=0.432/t_plh=1.15e-8/t_phl=2.931e-9），与 ref `inv_spice.py` 在 A'/A/B 三集完全一致（交叉验证 _judge_gold 正确性）。smart §4.9(b) B-hardcode stub `neg_fake_hardcode_b`（检测 vdd：A→A-gold 过 j，B→B-gold 过 c-k，A'→fallback B-gold）pre-fix PASS 全 11 → post-fix FAIL[m] A' voh=1.05!=judge-gold=0.9（运行时证明隐藏 A' 交叉击穿 stub）。7 neg（3 naive+1 smart stub+3 §4.9 deg）全 FAIL NEG_RC=0 n_distinct=6(c,e,f,g,j,m)，ref 16/16 PASS。**新病灶（r1069 增益）**：visible-A 反硬编码 guard（如 (j) 跑 A 比 B）无效——A 在 SUT 沙箱内，smart stub 可读 A 的 vdd 特判吐 A-gold 同时在 B 吐 B-gold，过 (j) 的"voh_A≠voh_B"检查；必须用 SUT 不可见的隐藏 A' + 判分器独立重算 A'-gold 才能击穿。
  - D `EDA-Eval-DesignFlow-RcVizTool-001`（k=10，Produce 跑 B 无 A-gold 交叉）—— **已于 r1071（2026-11-21）修复**：k=10→15（a-o，10 B-side(a-j) + 5 A'-gold 交叉(k-o)）。新增隐藏 A' 经 `derive_A_prime` 在 judge 时从 A 派生（XBOT.XDEC2.NETZ2 / 坐标 *1.8+500/+1500 / R*0.7 / C*0.9，与 A 无变换、B 的 XDEC1/*1.5/*1.2 token 结构性不相交；SUT 不可见，无额外文件故无 base64 腐蚀风险）。A'-gold R=237.459Ω vs B-gold R=508.842Ω（value-distinct）。5 条 A'-gold 断言：k A' -r exit0+打印ohm / l A' R 匹配独立 oracle A'-gold(1% rel，核心交叉) / m A'与B上R不同(输入相关非恒量) / n --devices A'选严格子集 / o --dpi+--figsize A'接受。smart §4.9(b) B-hardcode stub `neg_fake_hardcode_b`（对任意输入打印 B-gold 508.842，算术构造避开 B_LITERALS blocklist，源码带齐 d/h/i/j 静态模式）pre-fix PASS 全 B-side(a-j)=10/10（证明 pre-fix check.py 可被绕过）→ post-fix FAIL[l A' R=508.842 vs oracle A'-gold=237.459]+FAIL[m R 恒定跨 B/A']=13/15（运行时证明隐藏 A' 交叉击穿 stub）。§4.9 三假(empty/print_only/hardcode_a)全 FAIL(3/15)，ref 15/15 PASS，n_distinct(l,m)=2。**r1071 范式**：A' 由 judge 从 A 派生而非静态文件（适用于资产 A 可被 judge 读到的 Produce 类 case，避免维护额外 hidden 文件），R/C scale 与 B 取不同方向（B:*1.5/*1.2，A':*0.7/*0.9）确保 A'-gold 与 B-gold 差异显著（>100%），核心交叉断言 (l) + 显式输入相关性断言 (m) 双保险击穿 B-hardcode stub。
  - D `EDA-Eval-DesignFlow-NetlistBroadcastFlow-001`（k=11，visible-A 反硬编码 guard (j) 无效：A 在 SUT 沙箱内，smart stub 可读 A 的 broadcast token 特判吐 A-gold）—— **已于 r1074（2026-11-22）修复**：k=11→16（a-p，11 B-side+visible-A(a-k) + 5 A'-gold 交叉(l-p)）。新增隐藏 A' `reference/hidden_a/netlist_Aprime.v`（GDDR6 calibration-broadcast，GPUTOP/BroadcastCalibBit/CalibCenterN/aoi21/AF_CalibflagInject/or2/CalibFuseColumn/CalibIn/CalibDftCtrl/CalibTdqMon/CalibMonOut，与 A(WOWTOP/FuseTestBit/CMCenterR/aoi21/AF_FsBroadcastflagInChannel/aoi21/PrcUnitChanrightm5fuse/SignalLeft/ControllerM5/TclkTdqCtrl/BCDataBankOutForCPtest)及 B(DDR5TOP/ScanTestBit/ScanCenterL/oai21/AF_ScanflagInject/and2/ScanFuseColumn/ScanIn/DftController/TdqScanCtrl/CPtestDataOut)token 结构性不相交，11 字段全不同）。check 在 A' 上 subprocess 跑候选并断言 A'-gold（l 结构合法 / m top_module==GPUTOP 核心交叉 / n broadcast stem+generation / o leaf+consumer / p readback）。smart §4.9(b) B-hardcode stub `neg_fake_hardcode_b`（检测 A token BroadcastFuseTestBit→吐 A-gold 过 (j)，else→吐 B-gold）pre-fix PASS 全 11(a-k)（运行时证明 visible-A guard (j) 被绕过）→ post-fix FAIL[m] A' top_module=DDR5TOP!=GPUTOP（运行时证明隐藏 A' 交叉击穿 stub）。4 neg（3 naive+1 smart stub）+ 3 §4.9 deg（empty/print_only/core_deleted）全 FAIL NEG_RC=0 n_distinct=5(c,d,e,f,m)，ref 16/16 PASS。**r1074 印证 r1069 病灶**：visible-A 反硬编码 guard（如 (j) 跑 A 比 B）对 netlist 类 case 同样无效——A 在 SUT 沙箱内，smart stub 可读 A 的 broadcast token 特判吐 A-gold 同时在 B 吐 B-gold，过 (j) 的"A 全字段 != B"检查；必须用 SUT 不可见的隐藏 A' 才能击穿 B-hardcode stub。
  - D `EDA-Eval-DesignFlow-SaNPTrannoiseFix-001`（k=11，visible-A 反硬编码 guard (j) 无效：A 在 SUT 沙箱内，smart stub 可读 A 的 md5 特判吐 A-gold）—— **已于 r1077（2026-11-22）修复**：k=11→16（a-p，11 B-side+visible-A(a-k) + 5 A'-gold 交叉(l-p)）。新增隐藏 A' `reference/hidden_a/Check_SaNP_tb_Ap.sp`+`model_ranges_Ap.json`（FF 1.35V 125C / sns_hv_nmos / sns_chain / xmson0 / 2-stage / 1.5k / .tran 0.5n 50n / DCON=3 / noise fmin=50 fmax=20G seed=42 / W clamp xmson0 0.75u→1.0u，与 A(xmmn13/TT/ntnlv_hlsa/pcs_loading/1-stage/1k)及 B(xmmn0/SS/3-stage/2.2k) token 全维不相交，A' 含全部 5 类缺陷）。A'-gold 硬编码于 check.py（A' 固定 fixture，judge 不导入 ref/golden_fix_spice.py）：class-1 clamp (xmson0,W,7.5e-7,1.0e-6)、class-4 (fmin=50,fmax=20g,noiseseed=42)，与 B-gold(xmmn0/0.6u,100/5g/7)三字段全异。smart §4.9(b) B-hardcode stub `neg_fake_hardcode_b`（md5 查表 A→A-gold/B→B-gold/unknown→B-gold fallback，md5 键与真实 A/B 文件实测匹配）pre-fix PASS 全 11(a-k 含 visible-A guard j)（运行时证明 visible-A guard 被绕过）→ post-fix FAIL[(m) A' instance=xmson0≠xmmn0]（运行时证明隐藏 A' 交叉击穿 stub，逻辑上 (n)(p) 亦独立击穿）。6 neg（2 naive+1 smart stub+fake_empty/fake_print/fake_coredeleted）全 FAIL NEG_RC=0 n_distinct=4(a,b,c,m)，ref 16/16 PASS。**r1077 印证 r1069 病灶泛化到 SPICE-fix 类**（script-deliverable + 多缺陷 lint）：visible-A guard 对任何 A 可见的 script-deliverable case 无效，必须 SUT 不可见的隐藏 A' 同构 testbench。
  - D `EDA-Eval-DesignFlow-TwoStepOcNetlistAudit-001`（k=11，visible-A guard (k) 无效：A 在 SUT 沙箱内，smart stub 可读 A 的 pvcc=1.1 签名特判）—— **已于 r1080（2026-11-22）修复**：k=11→16，新增隐藏 A' `hidden_a/2stepoc_Ap.sp`（FF_pvcc1p25/HT=7/LT=2/64meas 与 A/B token 全维不相交）+ 5 A'-gold 交叉(l-p)，smart stub pre-fix PASS 全 11 → post-fix FAIL[m]，6 neg 全 FAIL。
  - D `EDA-Eval-DesignFlow-Ddr5ClDelayPivot-001`（k=9，既有嵌入 C 变体值校验但 C 用不同 TS token，signature-based smart stub 可区分 B/C）—— **已于 r1082（2026-11-22）修复**：k=9→14（⑩-⑭，5 A'-gold 交叉）。**新范式=A' 由 judge 从 B 派生 CL+4 移位**：check 运行时 `_derive_ap_v` 从 B 文本 regex 替换 `CL_(\d+)tCK`→`CL_(\d+4)tCK` 生成隐藏 A'（SUT 不可见，同 13 档/同 TS 签名/同行数/同档名同序，仅 CL 值移位 → A'-gold delays≠B-gold）。smart §4.9(b) signature-stub `neg_fake_hardcode_b`（构造 `"TS_"+"9500"` 运行时拼串绕过源级 B_C_TOKENS blocklist，B 上吐 B-gold / 非 B 跑真实 parser 过 C 值校验）pre-fix runtime 实测 PASS 全 9 → post-fix FAIL⑭（A' 值 B-gold 18.95 vs A'-gold 19.79）。5 neg 全 FAIL n_distinct=4(3,5,4,14)，ref 14/14 PASS。**增益**：A' 由 B 派生（非静态文件/非从 A 派生）适用于「既有 C 变体用不同 TS token 故 signature-stub 可区分」的 case，A' 复用 B 签名使 stub 无法区分 → 击穿；静态 audit 的 print_only/core_deleted=PASS 系误报（runtime 均 FAIL，同 r1069/r1077 结论）。
- **修复范式**：参照 r1053 SaNPCtrl / r1056 SpiceNetlistParseProduce——`check.py` 嵌入 A fixture（base64）+ 在 A 上跑候选并断言 A-gold + 独立 `_gt_recount` 重算，3 假全 FAIL。**r1069/r1074 增益**：visible-A guard 无效（A 可见即可被 stub 读取特判），必须用 SUT 不可见的隐藏 A'（文件式 `reference/hidden_a/` 或 judge 派生式 `derive_A_prime`）。**r1082 增益**：既有"不同签名 C 变体"不足以击穿 signature-based smart stub（运行时拼串绕过源级 blocklist + 非 B 跑真实 parser），须 A' 由 B 派生（复用 B 签名使 stub 不可区分）+ A'-gold 值交叉。**r1083 增益**：analysis-Q&A / report-deliverable 类 case 判分无牙根因=check 纯文本子串匹配（shipping reference report verbatim 即 PASS），通用解法=reframe 为「交付计算脚本 + subprocess 跑隐藏 B/A' 校验由输入计算的金值」（忠实 trace agent 实写的分析脚本，不偏离用户意图）。
- **处置**：D 自有题由 D 后续轮次逐批重写 `check.py`（本轮为普查，不修）；A/B/C 抽样 GAP 已在 `discuss/D.md` 开 P0 @ 对应 shard，由各 shard 自修。**D 不改别线题库。**

## 1. 判定标准（§4.9 三假 + anti-hardcode）

对每个 case 构造三类假提交，任一 PASS 即判 **GAP**：
1. `fake_print_only`：只把 B 的期望输出打印/写出，不做真实计算；
2. `fake_core_deleted`：删核心逻辑只留壳，但仍吐出 B 期望；
3. `fake_hardcode_a`：硬编码 A 的答案（测 hidden B 是否真能打掉）。

另查：`check()` 是否只在 hidden B 上跑、B 与 A 是否 token 结构性不相交。

**关键判定逻辑（已运行时验证）**：
- 若 `check.py` **无 subprocess**（只读候选交付的报告/静态文件做子串匹配）→ `fake_print_only` / `fake_core_deleted` 必 PASS（审计方直接把 B 期望报告塞进 zip）。
- 若 `check.py` **有 subprocess 跑 B 但无 A-gold 交叉校验** → `fake_print_only`（吐预计算的 B gold 输出）必 PASS。**这是本次普查发现的最普遍病灶。**
- `fake_hardcode_a`（吐 A 答案）在大多数 case 上 FAIL（check 用 B，A 答案不匹配 B 期望）——即 hidden B 机制本身有效，但 anti-hardcode 闸门缺失。

## 2. 普查方法（静态筛查 + 运行时抽验）

### 2.1 静态信号（`_audit_antihardcode_static.py`）
对每个 `reference/<id>/check.py` 检测：
- `has_subprocess`：是否真跑候选脚本（反 `fake_print_only` 的前提）；
- `has_embed_A`：是否嵌入 A fixture（base64）；
- `has_A_gold_xcheck`：是否在 A 上跑候选并断言 A-gold（击败 B-only 硬编码 stub 的核心闸门）；
- `only_static_read`：只读报告/静态文件 + 无 subprocess（`fake_print_only` 必 PASS）。

**判定**：
- `PASS` = subprocess + embed_A + A_gold_xcheck 三者齐备；
- `GAP`  = 任一假提交可 PASS（无 A-gold 交叉，或纯静态读）；
- `WEAK` = 闸门齐备但 k<12（结构合格，断言数偏低）；
- `MISSING` = check.py 未找到。

### 2.2 运行时抽验（2 条，附可复现命令）
**① D `ParasiticsAnnotDiag-001`（k=9，纯报告 grep）**
```bash
mkdir -p /tmp/po1 && cd /tmp/po1
cp <repo>/reference/EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001/reference_report_B.md diagnostic_report.md
zip -q fake_print_only.zip diagnostic_report.md
python3 -c "import importlib.util as u; s=u.spec_from_file_location('c','<repo>/reference/EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001/check.py'); c=u.module_from_spec(s); s.loader.exec_module(c); print(c.check('fake_print_only.zip','.'))"
# -> VERDICT: PASS  ← §4.9(b) fake_print_only 违规
```
假提交原文：`diagnostic_report.md` = 参考解的 B 报告逐字副本（candidate 不做任何分析，直接抄 B 期望）。`check.py` 9 断言全是 `B_DESIGN in t` / `_num_in(t, B_MAIN_TOTAL)` 式子串匹配，无 subprocess。

**② D `AddrRtlGateMap-001`（k=12，Produce 跑 B 但无 A-gold 交叉）**
```bash
mkdir -p /tmp/po2 && cd /tmp/po2
REF=<repo>/reference/EDA-Eval-DesignFlow-AddrRtlGateMap-001
cp $REF/mapper.py .
python3 mapper.py --rtl $REF/hidden_b/addr2rc_hidden.v --catalog $REF/hidden_b/stdcell_catalog_hidden.json --out gold_B_netlist.json
# 把 gold_B_netlist.json base64 嵌进一个忽略 --rtl/--catalog 的假 mapper.py
python3 -c "import base64; b=base64.b64encode(open('gold_B_netlist.json').read().encode()).decode(); open('fake_mapper.py','w').write('#!/usr/bin/env python3\nimport sys,base64\n_B=base64.b64decode(\"%s\".encode())\nout=\"netlist.json\"\na=sys.argv\nfor i,x in enumerate(a):\n  if x==\"--out\" and i+1<len(a): out=a[i+1]\nopen(out,\"wb\").write(_B)\n'%b)"
mkdir pkg && cp fake_mapper.py pkg/mapper.py && (cd pkg && zip -q fake_print_only.zip mapper.py)
python3 -c "import importlib.util as u; s=u.spec_from_file_location('c','$REF/check.py'); c=u.module_from_spec(s); s.loader.exec_module(c); r=c.check('pkg/fake_print_only.zip','$REF'); print('PASS?',r.get('pass'))"
# -> PASS? True  ← §4.9(b) fake_print_only 违规（12 断言全过）
```
假提交原文：`mapper.py` 忽略 `--rtl/--catalog`，直接写出预计算的 B gold `netlist.json`。`check.py` 在 B 上跑候选并把候选输出与"从 B 的 RTL 派生的期望真值表"比对——派生期望 = stub 吐出的内容，故全 PASS。

## 3. 普查结果

### 3.1 按 shard 分布
| shard | 抽样量 | PASS | GAP | WEAK | MISSING | GAP 率 |
|:--:|--:|--:|--:|--:|--:|--:|
| A | 25 | 0 | 24 | 0 | 0* | 96% |
| B | 25 | 0 | 20 | 2 | 3 | 80% |
| C | 25 | 1 | 20 | 1 | 3 | 80% |
| **D** | **561（全量）** | **62** | **489** | **0** | **13** | **87%** |
| 合计 | 636 | 44 | 569 | 3** | 16 | — |

\* A 抽样经 reference 目录名修正后 MISSING 已归零；\*\* 合计 WEAK=4（B 2 + C 1 + 表格四舍五入）。

**结论**：A/B/C/D 四线 GAP 率均在 80%+，**全 bench 性地缺 A-gold 交叉校验闸门**，非单 shard 问题。D 全量 561 条中具备完整 anti-hardcode 三件套的 case 持续增加（r1051-r1056 当周新建 + r1059-r1077 修复 10 条 + r1079 新建 1 条 + r1080 修复 1 条 = 55+ 条 PASS）。

### 3.2 按年度/月度分布（D 全量）
全部 D case 建于 2026 年（check.py mtime）：
| 月份 | case 数 | GAP 数 | GAP 率 |
|:--:|--:|--:|--:|
| 2026-10 | 4 | 3 | 75% |
| 2026-11 | 544 | 501 | 92% |

> 11 月 GAP 率反高于 10 月，原因是 11 月大量扩题沿用了"只跑 B + 子串/结构比对"的旧 check 范式，未补 A-gold 交叉。仅 11-21 当周新建的 r1051-r1056 等少数 case 采用了新范式（PASS）。

### 3.3 D GAP 按 k 分档
| k 分档 | GAP 数 |
|:--|--:|
| 8 ≤ k < 12 | 10 |
| 12 ≤ k < 16 | 303 |
| k ≥ 16 | 190 |

k≥12 的"达标"题同样大量 GAP——**断言数达标 ≠ anti-hardcode 达标**，二者是独立维度。

## 4. Top 10 风险题（D，k 升序 + 已运行时确认优先）

| # | case_id | k | 类型 | 风险点 |
|:--:|:--|--:|:--|:--|
| 1 | **EDA-Eval-DesignFlow-Schematic-001** | 8→13 | schematic_netlist | **k 最低 + GAP → 已修复 r1062**（k=13，A'-gold 交叉校验 i-m，5 neg 全 FAIL） |
| 2 | **EDA-Eval-DesignFlow-ParasiticsAnnotDiag-001** | 9 | 纯报告 grep | **运行时已确认 fake_print_only PASS** |
| 3 | **EDA-Eval-DesignFlow-LvlshftStepFix-001** | 10→15 | schematic_netlist | **GAP → 已修复 r1067**（k=15，A'-gold 交叉校验 k-o，hidden run_pipeline_A.py + sha256 token，smart §4.9(b) reimpl stub FAIL at [l]，5 neg+3 deg 全 FAIL n_distinct=4） |
| 4 | **EDA-Eval-DesignFlow-RcVizTool-001** | 10→15 | schematic_netlist | **GAP → 已修复 r1071**（k=15=10 B-side(a-j)+5 A'-gold 交叉(k-o)，A' 经 derive_A_prime 从 A 派生 XBOT.XDEC2.NETZ2 R*0.7 C*0.9 与 B token 不相交，A'-gold 237.459Ω vs B-gold 508.842Ω，smart §4.9(b) B-hardcode stub PASS 全 B-side 10/10 post-fix FAIL[l]+[m]=13/15，§4.9 三假全 FAIL，ref 15/15 PASS n_distinct(l,m)=2） |
| 5 | **EDA-Eval-DesignFlow-InvSpiceSim-001** | 11→16 | schematic_netlist | **GAP → 已修复 r1069**（k=16=11 B-side(a-k)+5 A'-gold 交叉(l-p)，hidden_a/spec_Aprime.json vdd=0.9 token 不相交，判分器内联 _judge_gold(Shockley) 与 ref 在 A'/A/B 三集完全一致，smart §4.9(b) B-hardcode stub neg_fake_hardcode_b pre-fix PASS 全 11 post-fix FAIL[m]，7 neg+3 deg 全 FAIL n_distinct=6） |
| 6 | **EDA-Eval-DesignFlow-NetlistBroadcastFlow-001** | 11→16 | schematic_netlist | **GAP → 已修复 r1074**（k=16=11 B-side+visible-A(a-k)+5 A'-gold 交叉(l-p)，hidden_a/netlist_Aprime.v GPUTOP/BroadcastCalibBit token 不相交，smart §4.9(b) B-hardcode stub neg_fake_hardcode_b pre-fix PASS 全 11 post-fix FAIL[m]，4 neg+3 deg 全 FAIL n_distinct=5(c,d,e,f,m)，ref 16/16 PASS） |
| 7 | **EDA-Eval-DesignFlow-SaNPTrannoiseFix-001** | 11→16 | waveform | **GAP → 已修复 r1077**（k=16=11 B-side+visible-A(a-k)+5 A'-gold 交叉(l-p)，hidden_a/Check_SaNP_tb_Ap.sp FF 1.35V/sns_hv_nmos/sns_chain/xmson0 与 A(xmmn13/TT) B(xmmn0/SS) token 结构性不相交，smart §4.9(b) B-hardcode stub neg_fake_hardcode_b md5 查表 A→A-gold/B→B-gold/unknown→B-gold fallback pre-fix PASS 全 11(a-k 含 visible-A guard j) post-fix FAIL[(m) A' instance=xmson0≠xmmn0]，§4.9 三假 runtime 实测均 FAIL(静态标 print_only/core_deleted PASS 为误报，同 r1069/InvSpiceSim)，6 neg 全 FAIL n_distinct=4(a,b,c,m)，ref 16/16 PASS） |
| 8 | EDA-Eval-DesignFlow-Waveform-001 | 11→16 | waveform | **GAP → 已修复 r1084**（k=16=11 B-side(a-k)+5 A'-gold 交叉(l-p)，hidden A' 同信号名 clk/sense/absent 但不同值: clk 3r/3f@0.1/1.5 vs B 4/4@0/1.8、sense analog 3zc@+-0.8 vs B 4zc@+-0.5，A'-gold 运行时由 inline ref analyzer 计算；smart §4.9(b) window-aware B-hardcode stub neg_fake_hardcode_b(按 --t-start/--t-end 查表吐预计算窗内 B-gold)pre-fix PASS 全 (a-k) post-fix FAIL (m)/(n)/(o) A' 值≠B-gold，8 neg ALL FAIL，ref 16/16 PASS。**r1082 范式复用**：A' 同签名值偏移击穿 signature-based stub；静态 audit 标 print_only/core_deleted PASS 系误报(runtime (k) 窗内随机化已使其 FAIL，同 r1069/r1077/r1082 结论)） |
| 9 | **EDA-Eval-DesignFlow-AddrRtlGateMap-001** | 12→21 | Produce 跑 B 无 A-gold | **运行时已确认 → 已修复 r1059**（k=21，A-gold 交叉校验 m-u，3 假全 FAIL） |
| 10 | **EDA-Eval-DesignFlow-AeDelCellCurCellProduce-001** | 12→17 | Produce 跑 B 无 A-gold | **运行时已确认 → 已修复 r1073**（k=17=12 B-side(a-l)+5 A'-gold 交叉(m-q)，A' mock 内联值 powerLib_Q/dffQ/symbol SUT 不可见 + MOCK_CUR_CFG decoy 路径使文件读取 stub 崩溃，smart §4.9(b) B-hardcode/file-reading stub neg_fake_hardcode_b pre-fix PASS 全 B-side post-fix A' 上 FileNotFoundError FAIL[m]，4 neg 全 FAIL） |

A/B/C 抽样 GAP 代表题（已开 P0）：
- A: `CmPatternRunGen-001`(k=11)、`DrcDocConvert-001`(k=11)、`FsdbDumpConvert-001`(k=11)、`RedBistFlowRecon-001-v2`(纯报告 grep)
- B: `StackedMOSOpAnalysis-001`(k=11)
- C: `FindCircuitByPath-001`(k=15)

## 5. 处置分工（守职责边界）

### 5.1 D 自有题（505 GAP → 已修 24，余 481）—— 由 D 后续轮次逐批重写
- 本轮为普查，不修。后续每轮"造题主线"与"anti-hardcode 修复"交替进行（守用户令「普查与造题交替」）。
- 修复范式（参照 r1053/r1056）：
  1. `check.py` 嵌入 A fixture（base64），并在 A 上 subprocess 跑候选；
  2. 断言 A-gold（候选在 A 上必须产出 A 的金标，击穿"吐 B 答案"的 stub）；
  3. 加独立 `_gt_recount` 重算（防候选 regex gaming）；
  4. 3 假回归入库 `reference/<id>/negative/`，`negative_selftest.py` 全 FAIL。
- 优先修 Top 10 + k<12 的 12 条。
- **修复进度**：r1059 修 1/505（AddrRtlGateMap-001）；r1060 修 2/505（AutoCellRmAvPf-001，范式=直接读 assets/ A fixture 而非 base64，更简）；r1061 修 3/505（AvcPatternCompare-001，范式=新增隐藏 A' 文件 + 独立 _gt_recount，发现新病灶「visible-A-vs-A 交叉校验无效，A 在 SUT 沙箱内可被 stub 读取特判 a==b，必须用 SUT 不可见的隐藏 A'」）；r1062 修 4/505（Schematic-001，k=8→13，范式=新增隐藏 A' 文件 + subprocess 跑 A' 断 A'-gold，沿用 r1059 文件式 A fixture 规避 base64 腐蚀，smart §4.9(b) B-hardcoded stub 入库为运行时证明）；r1067 修 5/505（LvlshftStepFix-001，k=10→15，**新范式=隐藏 A' 下游 pipeline**：CLI 修复类 case 的下游 run_pipeline.py 在 assets/ 内 SUT 可见，reimpl stub 可模仿其输出格式故 visible-A/B 交叉无效；解法=新增 SUT 不可见的 hidden_a/run_pipeline_A.py，check 将其安装为 A' 测试目录的 run_pipeline.py，候选真跑须经 os.execv 委托到 hidden pipeline 才能产 [OK-A] 标记+sha256 token，reimpl stub 模仿可见 [OK] 格式 → FAIL[l]，smart §4.9(b) reimpl stub 入库为运行时证明）。r1069 修 6/505（InvSpiceSim-001，k=11→16，**新病灶=visible-A 反硬编码 guard 无效**：A 在 SUT 沙箱内 smart stub 可读 A 的 vdd 特判吐 A-gold 同时在 B 吐 B-gold 过 (j) 的 voh_A≠voh_B 检查；解法=隐藏 A' spec_Aprime.json vdd=0.9 + 判分器内联 _judge_gold(Shockley) 独立重算 A'-gold，smart stub FAIL[m]）。r1071 修 7/505（RcVizTool-001，k=10→15，**范式=A' 由 judge 从 A 派生而非静态文件**：derive_A_prime(XBOT.XDEC2.NETZ2 R*0.7 C*0.9) 适用于资产 A 可被 judge 读到的 Produce 类 case，避免维护额外 hidden 文件；A'-gold 237.459Ω vs B-gold 508.842Ω 差 >100%，核心交叉 (l) + 输入相关性 (m) 双保险击穿 B-hardcode stub，smart stub PASS 全 B-side 10/10 post-fix FAIL[l]+[m]=13/15）。r1073 修 8/505（AeDelCellCurCellProduce-001，k=12→17，**范式=A' mock 内联值 + decoy MOCK_CUR_CFG 路径**：mock 类 case 的 B mock 在 SUT 沙箱内，smart §4.9(b) file-reading stub 读 MOCK_CUR_CFG 文件绕过 mock API 取 B 值 PASS 全 B-side；解法=A' mock 源内联为 check.py 字符串常量(SUT 不可见)，judge 安装为 run dir 的 pyAether.py，MOCK_CUR_CFG 设 decoy 不存在路径使文件读取 stub 在 A' 上 FileNotFoundError 崩溃 FAIL[m]，候选须调 mock mdeGetCurrentLibCellView 才能取 A' 值；A' tuple powerLib_Q/dffQ/symbol 与 A 及 B 三 seed token 全不相交；smart stub neg_fake_hardcode_b 入库为运行时证明）。r1074 修 9/505（NetlistBroadcastFlow-001，k=11→16，**印证 r1069 visible-A guard 无效病灶泛化到 netlist 类**：A 在 SUT 沙箱内 smart stub 可读 A 的 broadcast token BroadcastFuseTestBit 特判吐 A-gold 过 (j) 的"A 全字段!=B"检查；解法=新增隐藏 A' netlist_Aprime.v（GDDR6 calibration-broadcast，11 字段与 A/B 全不相交）+ check 在 A' 上 subprocess 跑候选断 A'-gold，smart §4.9(b) B-hardcode stub neg_fake_hardcode_b pre-fix PASS 全 11 → post-fix FAIL[m] A' top_module=DDR5TOP!=GPUTOP，4 neg+3 deg 全 FAIL n_distinct=5(c,d,e,f,m)，ref 16/16 PASS）。余 496 待逐批修，与造题交替。r1077 修 10/505（SaNPTrannoiseFix-001，k=11→16，**印证 r1069 病灶泛化到 SPICE-fix 类**：visible-A guard 对 script-deliverable+多缺陷 lint case 无效，smart §4.9(b) B-hardcode stub md5 查表 A→A-gold/B→B-gold/unknown→B-gold fallback pre-fix PASS 全 11(a-k 含 visible-A guard j) → post-fix FAIL[(m) A' instance=xmson0≠xmmn0]，hidden_a/Check_SaNP_tb_Ap.sp FF 1.35V/sns_hv_nmos/sns_chain/xmson0 与 A/B token 全维不相交，6 neg 全 FAIL n_distinct=4(a,b,c,m)，audit Top10 全修完，余 495 待逐批修）。r1079 新建 1 条即合规（SpfCellCrossRefProduce-001，k=19=14 B-side(a-n)+5 A'-gold 交叉(o-s)，analog_context/doc-search cross-reference produce；A' aaa 子集偏移 6cell 移除+4filler 使 A'-gold 计数 9/4/32/16≠B-gold 13/6/38/18 全维不相交，smart §4.9(b) B-hardcode stub 击穿于 [p] A'-gold 交叉，4 neg 全 FAIL n_distinct=4(c,h,j,p)，ref 19/19 PASS）。r1080 修 11/505（TwoStepOcNetlistAudit-001，k=11→16，**印证 r1069 visible-A guard 无效病灶泛化到 SPICE-netlist-audit 类**：visible-A guard (k) 跑可见 A 断"A report≠B report in ht/lt/caps/corner"，但 smart §4.9(b) B-hardcode stub 读 A 的 pvcc=1.1 签名特判 A→A-gold / else→B-gold fallback，pre-fix runtime 实测 PASS 全 11(a-k 含 visible-A guard k)；解法=新增隐藏 A' hidden_a/2stepoc_Ap.sp（SUT 不可见，FF_pvcc1p25_125C/cap 梯 3-6-12-24f unit 3f binary/HT=7/LT=2/64 meas，与 A pvcc1.1/45°C/cap 1-2-4-8f/HT10/LT5/256meas 及 B pvcc0.95/-40°C/cap 2-4-8-16f/HT12/LT3/128meas token 全维不相交）+ 5 A'-gold 交叉(l-p)：l A' run exit0+合法JSON / m A' ht==A'-gold 7(核心交叉,击穿 stub 吐 B-gold 12) / n A' lt==A'-gold 2 / o A' cap_weights==A'-gold[3e-15,6e-15,1.2e-14,2.4e-14] / p A' corner pvcc==1.25+ptemp==125+meas==64；A'-gold 硬编码于 check.py(A' 固定 fixture,judge 不导入 ref analyze_2stepoc.py)；smart stub neg_fake_hardcode_b pre-fix PASS 全 11 → post-fix FAIL[m] A' ht=12≠A'-gold 7，6 neg 全 FAIL n_distinct=4(b,e,k,m)，ref 16/16 PASS on (B)+(hidden A')。余 494 待逐批修，与造题交替）。r1082 修 12/505（Ddr5ClDelayPivot-001，k=9→14，analog_context/DDR5 CL delay pivot；**新范式=A' 由 judge 从 B 派生 CL+4 移位**：既有嵌入 C 变体(8 档/不同 TS token)的值校验无法击穿 signature-based smart stub(构造 "TS_"+"9500" 运行时拼串绕过源级 B_C_TOKENS blocklist，B 上吐 B-gold / 非 B(含 C) 跑真实 parser 过 C 值校验)，runtime 实测 smart stub PASS 全 9；解法=check 运行时 _derive_ap_v 从 B 文本 regex 替换 CL_(\d+)tCK→CL_(\d+4)tCK 生成隐藏 A'(SUT 不可见，同 13 档/同 TS 签名/同行数/同档名同序，仅 CL 值移位 → A'-gold delays≠B-gold)，新增 5 A'-gold 交叉⑩-⑭(⑩A' run exit0+产 CSV / ⑪A' header / ⑫A' 行数==A' oracle==B / ⑬A' 档名按序匹配 / ⑭A' SS/TT/FF/tCK 值匹配 A' oracle[核心交叉:B-gold 18.95 vs A'-gold 19.79 击穿]+A'-gold 显式≠B-gold)；smart stub neg_fake_hardcode_b pre-fix PASS 全 9 → post-fix FAIL⑭ A' 值不匹配，5 neg 全 FAIL n_distinct=4(3,5,4,14)，ref 14/14 PASS。**增益**：A' 由 B 派生(非静态文件/非从 A 派生)适用于「既有 C 变体用不同 TS token 故 signature-stub 可区分」的 case，A' 复用 B 的 TS 签名使 stub 无法区分 → 击穿；静态 audit 的 print_only/core_deleted=PASS 系误报(runtime 均 FAIL，同 r1069/r1077 结论)。余 493 待逐批修，与造题交替）。r1083 修 13/505（ParasiticsAnnotDiag-001，k=9→14，schematic_netlist/PrimeTime SDF 诊断 Q&A；**病灶=analysis-Q&A report-deliverable 类无牙**：原 check 纯子串匹配 diagnostic_report.md，shipping reference_report_B.md verbatim 即 PASS(print_only PASS 运行时已确认)；**解法=reframe report→script deliverable**（trace agent 实写 analyze_parasitics.py/analyze_sdf.py 故忠实）：交付 diagnose_parasitics.py 接收 asset_dir 打印结构化 JSON 诊断，check subprocess 在隐藏 B + 隐藏 A' 上各跑一次校验由输入计算的金值；新增隐藏 A' hidden_a/(sdf.tcl GDDR6X/3 read_parasitis + parasitics_command.log 1288550/221894/1066656/512/506 + GDDR6X.sdf 4 hier I_PERI0/I_Array8G_T_0/T_1/B_2) 与 A(DDR5TOP/I_BCenter/I_Array6G) 及 B(LPDDR5TOP/I_DCC/I_Array4G) token 全维不相交；14 断言=10 B-side(a-j: zip+compile/B run+JSON 确定性 3x md5/design/rp_count/covered_paths/main_total/main_unannot+annot/second_total+annot/sdf_hierarchies/sdf 结构+iopath+para124) +4 A'-gold 交叉(k-n: A' run+JSON/A' design==GDDR6X[击穿硬编码 LPDDR5TOP]/A' rp_count==3+main_total==1288550[击穿硬编码 2/985442]/A' hier==4-hierarchy list[击穿硬编码 B 3-hierarchy])；smart §4.9(b) signature-stub neg_fake_hardcode_b（读 SDF design 查表 DDR5TOP→A-gold/LPDDR5TOP→B-gold/unknown→B-gold fallback，B 上 PASS 全 B-side）pre-fix 等价 PASS → post-fix FAIL[l] A' design=LPDDR5TOP≠GDDR6X，4 neg 全 FAIL n_distinct=3(b/c/l)，ref 14/14 PASS on (B)+(hidden A')。**增益**：analysis-Q&A/report-deliverable 类 case 的判分无牙根因=check 纯文本子串匹配，reframe 为「交付计算脚本 + subprocess 跑隐藏 B/A' 校验计算值」是通用解法（忠实 trace agent 实写的分析脚本）；A' 用 SUT 不可见的第三场景（与 A/B token 全维不相交）做交叉。余 492 待逐批修，与造题交替）。r1084 修 14/505（Waveform-001，k=11→16，waveform/WaveView .tbl 离线波形分析器；**r1082 范式复用**：A' 同信号名 clk/sense/absent 但不同值(clk 3r/3f@0.1/1.5 vs B 4/4@0/1.8；sense analog 3zc@+-0.8 vs B 4zc@+-0.5)，A'-gold 运行时由 inline ref analyzer 计算(非硬编)；新增 5 A'-gold 交叉(l-p)：l A' run exit0+三信号 key / m A' clk type=digital+n_rising==3+n_falling==3[核心交叉,击穿 stub 吐 B-gold 4/4] / n A' clk v_low~0.1/v_high~1.5/mid~0.8[击穿 0/1.8] / o A' sense type=analog+nzc==3+双极 v_min~-0.8/v_max~0.8[击穿 4zc/-0.5/0.5] / p A' absent found=False；smart §4.9(b) window-aware B-hardcode stub neg_fake_hardcode_b(按 --t-start/--t-end 查表吐预计算窗内 B-gold，绕过 (k) 窗内随机化)pre-fix PASS 全 (a-k) post-fix FAIL (m)/(n)/(o) A' 值≠B-gold，8 neg ALL FAIL n_distinct 含 (m)(n)(o)，ref 16/16 PASS on (B)+(hidden A')。**增益**：waveform 类 case 的 (k) 窗内随机化已使 naive print/core stub runtime FAIL(静态 audit 标 PASS 系误报，同 r1069/r1077/r1082 结论)，但 window-aware B-hardcode stub(预计算各窗 B-gold 查表)可绕过 (k)，须 A' 同签名值偏移交叉击穿；r1082「A' 由 B 派生同签名值偏移」范式推广到 waveform（A' 此处为独立构造的同签名 fixture，非从 B 派生，因波形无字符串 token 可 regex 替换，改用独立构造+运行时 ref analyzer 计算 A'-gold）。余 491 待逐批修，与造题交替）。r1089 修 15/505（SpiceUndefParamScan-001，k=11→16，schematic_netlist/SPICE include-chain undefined-param scanner；**r1069 范式复用**：新增隐藏 A' DECKS["Ap"] q-namespace deck（mixbest_Ap/stim_Ap/pwr_Ap/sub_Ap/decoy_Ap，token qstart/qrise/q1/qsense/qocon/qeq/OcEnp/OcNp_1/OcNp_2/OcPp_1/OcPp_2/OcPp_3/qcomb 与 A t-/B v-/C w- 全维不相交，depth-2 nested sub_Ap.sp 含 OcPp_3 定义测递归）+ 5 A'-gold 交叉(l-p)：l A' run exit0+JSON 6keys / m A' include_chain==[mixbest_Ap,stim_Ap,pwr_Ap,sub_Ap][核心交叉,击穿 stub 吐 A-chain] / n A' undefined==7 q-namespace[核心交叉,击穿 stub 吐 A t-namespace] / o A' defined==7 含 OcPp_3 from nested sub_Ap[击穿跳过递归的 stub] / p A' commented 含 decoy_Ap.sp；**新 smart stub 病灶=fingerprint by XtopA/B/C line + chr() 运行时构造 B/C token 绕过 FORBIDDEN_LITERALS 源级 substring blocklist**（变量名/注释亦须避开 forbidden substring veq/weq，否则 (a) 误捕）：smart §4.9(b) neg_fake_hardcode_b pre-fix PASS 全 12(a-l，含 (l) 空 JSON 6keys) → post-fix FAIL(m)(n)(o)(p)（A' deck 含 XtopAp 触发 A 分支吐 A-answer，chain/undef/def/commented 全不匹配 A'-gold），5 neg ALL FAIL NEG_RC=0 n_distinct=4(m,n,o,p)，ref 16/16 PASS。**增益**：FORBIDDEN_LITERALS substring blocklist 可被 chr() 运行时拼串绕过，须靠隐藏 A' 交叉击穿（同 r1069 visible-A guard 无效结论的又一佐证）；A' 用独立 q-namespace + depth-2 nested 同时测 token 不相交 + 递归跟随。余 490 待逐批修，与造题交替）。r1094 修 16/505（ArgparseWaveviewFixQA-001，k=12→20，waveform/argparse-diagnose Q&A reframe；嵌入隐藏 A' fixture(03_gen_panel_extract.py+SigCap_4TCMD.sx+error_output_Ap.txt+dir_listing_Ap.txt，每维 script/sx/pos/opt/default/corner/PVT 全异于 A 与 B)check.py 字符串 + 8 A'-gold 交叉(m-t，含逆向 B-only token 守卫 t)；smart hardcode_b stub B-side PASS(e-l) post-fix FAIL[n] A' missing=waveview_session≠panel_session；§4.9 三假 empty→d/print_only→e/core_deleted→f + hardcode_b→n，4 distinct(d,e,f,n)≥3；ref 20/20 PASS + 4 neg ALL FAIL。余 489 待逐批修）。r1095 修 17/505（BtopPoststressJobs-001，k=12→15，waveform/bjobs-Poststress001 提取 script-deliverable，r1094 范式复用：嵌入 A-prime fixture 字符串(AP_111 2 Poststress001 job 5612001/5612002 + AP_222 3 job 6723001-3，JOBID/bank(Quadbank)/corner/voltage(0.88V)/temp(105/125C)/CRC(22) 全异于 A 与 B) + 独立 oracle _gold_poststress001(regex 行匹配，非 ref 的 split 实现) 实时算 gold + m/n A'交叉 + o B-diff 守卫；hardcode_b stub B-side PASS(f-i) 但 A' FAIL(m)；§4.9 三假 empty→b/print_only→g/core_deleted→f + hardcode_b→m，4 distinct(b,g,f,m)≥3；ref 15/15 PASS + 7 neg ALL FAIL。余 488 待逐批修）。r1096 修 18/505（ClosureDeckBuilder-001，k=12→16，schematic_netlist/SPICE 闭包 deck builder；**r1089 范式复用**：嵌入隐藏 A'(zdrive_top，z-namespace 嵌入 check.py 字符串，token zdrive_top/zdrv_sub/zbuf_z_model/zload_z_model/zpas_z_model/zen/zmode 与 A(wldec_top_a/dec_a_sub)、B(senseamp_top_b/sa_sub)、C(mux_top_c/mux_c_sub) 全维不相交) + 4 A'-gold 交叉(m-p)：m A' run exit0+deck 文件 / n A' 闭包==oracle{zdrive_top,zdrv_sub}[核心交叉,击穿 stub 吐 B-gold 回退] / o A' stub 端口数==oracle{zbuf/zload/zpas 各2} / p A' 前导 .param[zen=0/zmode=0]+.end+无 context；**smart stub 病灶=signature-based B-hardcode stub 用 base64 构造 B/C token 绕过源级 B_LITERALS substring blocklist(变量名/注释亦须避开 forbidden substring)**：smart §4.9(b) neg_fake_hardcode_b 按输入签名查表 B→B-gold/C→C-gold/unknown→B-gold fallback，pre-fix PASS 全 12(a-l 含嵌入 C 交叉 k) → post-fix FAIL(n) A' 闭包空≠{zdrive_top,zdrv_sub}；§4.9 三假 empty→a/print_only→a/core_deleted→d + hardcode_b→n，n_distinct=3(a,d,n)≥3；ref 16/16 PASS + 5 neg ALL FAIL。**增益**：r1089 chr() 绕过 blocklist 病灶的又一佐证——base64 解码亦可绕过，须靠隐藏 A' 交叉击穿；SPICE 闭包-deck 类 case 的嵌入 C 交叉(k)对 signature-stub 无效(C 在 SUT 可读的输入文件里故可被签名)，须 SUT 不可见的隐藏 A'(此处嵌入 check.py 字符串，非输入文件，stub 无法在运行时签名)。余 487 待逐批修，与造题交替）。r1097 修 19/505（CVPSHierSearchFix-001，k=12→16，schematic_netlist/SKILL .il rootdir 相对路径修复器；**r1069 范式复用+病灶又一佐证**：原 12 断言只跑隐藏 B(a-l)，anti-hardcode (k) 仅 A-only token substring blocklist(".HierSearch")，smart generic-emitter stub（**不读 --input**，预焙含全部 12 CVPSHierSearch_* procs + getWorkingDir + mkdir + case(type) + 4 Search tabs + cwd/verilog report 的"fixed"输出，对所有输入吐同一份 B 风格 gold）pre-fix PASS 全 12（§4.9b 违规，已用 git HEAD 旧 check.py 复现 PASS 12/12 为运行时证明）；解法=新增隐藏 A-prime `CXMTseCVPSHierSearch_Ap.il`（assets/hidden/，SUT 不可见，由 B sed 派生：proc 前缀 CVPSHierSearch_→CVPSScan_AP_ 全 12 + rootdir .hsearch_out→.hscan_ap_out，与 A(.HierSearch)/B(.hsearch_out) token 全维不相交，文件式规避 base64 腐蚀）+ 4 A'-gold 交叉(m-p)：m A' run exit0+产出 fixed_A'.il+report.md / n fixed_A'.il 保留全 12 A' 特有 procedure(CVPSScan_AP_*)[核心交叉,击穿 stub 吐 CVPSHierSearch_*] / o fixed_A'.il 含 strcat(getWorkingDir() "/.hscan_ap_out")[输入驱动 rootdir 重写证明,击穿预焙 B 输出] / p fixed_A'.il 不含 B 的 .hsearch_out 也不含 A 的 .HierSearch[无跨输入污染,击穿 stub 泄 B-path]；smart generic-emitter stub `neg_fake_hardcode_b` B-side PASS(a-l)→A' FAIL(n)(o)(p)，§4.9 三假 empty→a/print_only(stub_print)→b/core_deleted→e + hardcode(旧)→d + hardcode_b(新smart)→n，5 distinct(a,b,d,e,n)≥3；ref 16/16 PASS + 5 neg ALL FAIL 5 distinct。**增益**：substring blocklist 类 anti-hardcode（如 (k) 禁 ".HierSearch"）对"不读输入的 generic-emitter stub"无效——stub 输出本就不含禁词故过 (k)，须靠 SUT 不可见的隐藏 A'(不同 proc 前缀+不同 path)交叉击穿；A' 由 B sed 派生(proc 前缀+path 两维偏移)是 SPICE/SKILL 结构保持类 case 的轻量 A' 构造法，保证 A' 与 B 同构(ref fixer 能正常处理)且 token 不相交。余 486 待逐批修，与造题交替）。r1098 修 20/505（AetherDmBatchCopyExplainQA-001，k=12→17，analog_context/Aether DM 手册 procedure 抽取 script-deliverable；**r1094 范式复用**：原 12 断言只跑隐藏 B(a-l 含 visible-A 泛化 j/k)，smart signature-based B-hardcode stub（读 --manual 按 token 检测 A vs B，吐预焙 A-gold/B-gold，unknown→B-gold fallback）pre-fix PASS 全 12（§4.9b 违规，已运行时复现 PASS 12/12）；解法=新增隐藏 A-prime `dm_manual_Ap.md`（assets/hidden/，第三套术语 Edit→Bulk Replicate / Origin Library/Destination Library/Cell Glob/Display Filter/View Type Selector/Level Refresh/Destination Group/Replicate Pick List，与 A(Copy Wizard/From Library)及 B(Batch Copy/Source Library) token 全维不相交，SUT 不可见，文件式规避 base64 腐蚀）+ 5 A'-gold 交叉(m-q)：m A' run exit0+合法JSON / n A' menu_path 含 'Bulk Replicate'[核心交叉,击穿 stub fallback 吐 B-gold Batch Copy] / o A' 字段名含>=4 个 A'-only token[击穿 stub 吐 B 字段] / p A' 输出无 A/B token 污染(总出现<=1)[击穿 stub 泄 B-gold] / q A' batch_mechanism 命中 A' 表格字段(Replicate Pick List)；smart signature-stub `hardcode_b.py` B-side PASS(a-l)→A' fallback B-gold FAIL(n)(o)(p)(q)；§4.9 三假 empty→c/print_only→f/core_deleted→e + hardcode_b→n，4 distinct(c,e,f,n)≥3；ref 17/17 PASS + 4 neg ALL FAIL 4 distinct。**增益**：manual/parser 类 case 的 visible-A 泛化断言(j/k)对 signature-stub 无效（stub 读手册 token 即可区分 A/B），须靠 SUT 不可见的隐藏 A'(第三套术语)交叉击穿；A' 用独立第三套术语文件(非从 B sed 派生，因术语无 proc 前缀可 regex 替换，改用独立构造+同结构)保证 ref parser 能正常处理且 token 不相交。余 485 待逐批修，与造题交替）。r1099 修 21/505（AetherNetHighlightQA-001，k=16→21，schematic_netlist/Aether 手册 net-highlight 结构化指南 Q&A→script-deliverable；**r1098 范式复用**：原 16 断言只跑隐藏 B/B2/B3(a-p，B 版图追踪 aeTraceNet+islayout+layer / B2 GUI 点选 seGuiTraceNet / B3 无 trace API 优雅降级)，smart signature-based B-hardcode stub（读手册 token 检测 版图→B-gold / GUI点选→B2-gold / aeCreateInst→B3-gold / unknown→B-gold fallback）pre-fix PASS 全 16（§4.9b 违规，已运行时复现 stub B/B2/B3 全 PASS 为运行时证明）；解法=新增隐藏 A-prime `aether_manual_Ap.md`（assets/hidden/，高亮删除主题，primary=aeSeRemoveNetHighlight，token 与 A(aeTraceNet/schematic/isschematic)/B(aeTraceNet/layout/版图/金属线/islayout/layer)/B2(seGuiTraceNet/GUI/点选/交互)/B3(aeCreateInst/aeCreateWire/aeDeleteInst/aeMoveInst) 全维不相交，SUT 不可见，文件式规避 base64 腐蚀；A' 问题"怎么删除某条网络的高亮"含"删除"路由到 aeSeRemoveNetHighlight，与 A/B"点亮/追踪"→aeTraceNet、B2"GUI点选"→seGuiTraceNet、B3 无 API→"" 路由不相交）+ 5 A'-gold 交叉(q-u)：q A' run exit0+合法JSON含8键 / r A' primary==aeSeRemoveNetHighlight[核心交叉,击穿 stub fallback 吐 aeTraceNet] / s A' primary 作为 token 出现在 manual_Ap[data-grounded] / t A' procedure_steps 非空且含 aeSeRemoveNetHighlight / u A' api_parameters 含 netName(非 B 的 islayout/layer)；smart signature-stub `neg_fake_hardcode_b.py` B-side PASS(a-p)→A' fallback B-gold FAIL(r)；§4.9 三假 empty→a/print_only→c/core_deleted→b + hardcode_b→r，4 distinct(a,b,c,r)≥3；ref 21/21 PASS + 4 neg ALL FAIL 4 distinct。**增益**：manual/parser 类多隐藏输入(B/B2/B3 各异主题)case 的 signature-stub 按主题 token 检测即可区分并吐对应 gold，须靠 SUT 不可见的隐藏 A'(第四主题+第四 primary API)交叉击穿；A' 主题须与 B/B2/B3 主题词全维不相交(本例"高亮删除"避开"版图/金属线/GUI/点选/aeCreateInst"等检测 token，曾因 header 注释含"GUI点选"误触 B2 分支，已修)。余 484 待逐批修，与造题交替）。 r1101 修 22/505（BitlinePrechargeRootCauseQA-001，k=13→18，waveform/DRAM bitline precharge root-cause debug Q&A→generic-analyzer script-deliverable，**范式=嵌入隐藏 A-prime 网表字符串 + 独立 mini-oracle**：原 13 断言只跑隐藏 B，anti-hardcode (l) 仅 A_ONLY_TOKENS substring blocklist 对「不解析恒吐 B-gold 的 stub」无效（runtime 复现 stub PASS 13/13）；解法=嵌入第三套 z-namespace 网表(z0_pwa_tgt/pvpc/vpc!/PwcSnsZ/XJ9/612mV) 于 check.py 字符串(SUT 不可见) + 独立 mini-oracle(regex 算 source_param/source_net/sa_subckt/top_instance) + 5 A'-gold 交叉(n-r) 击穿 stub 吐 B 值(pvdp2/vdp2!/SnsAmpU/XI38)；印证 r1095+ substring-blocklist-无效病灶族：A-token blocklist 对吐 B-token 的 stub 同样无效，须 SUT 不可见的隐藏 A' 交叉）。
- r1103 修 23/505（CapPropsCalc-001，k=13→18，analog_context/MOS 电容参数提取 Produce；**新病灶=C-dataset 交叉(cond j)对 base64 硬编码 B+C 两套 gold + 运行时 V3 检测的 smart stub 无效**：stub base64 编码两套 gold，运行时检测 "V3" 区分 B/C，os.listdir 读文件名避开 _B blocklist，runtime PASS 全 13(§4.9b 违规)；解法=新增隐藏 A'(hidden_a/inputs_Ap，V4_Q/ss/ntn_lvss，4 行 gold，token 与 A V1/B V2/C V3 全维不相交，SUT 不可见) + 5 A'-gold 交叉(n-r)；smart stub B-side PASS(a-m)→A' FAIL(n-r)；ref 18/18 PASS + 4 neg ALL FAIL。**增益**：C-dataset guard = visible-C guard 同 r1069 visible-A guard 无效病灶族；base64 绕过 blocklist 同 r1096 佐证。余 482 待逐批修，与造题交替）。
- r1104 修 24/505（SpfDielectricLeakageQA-001，k=12→18，schematic_netlist/DSPF 介质漏电电阻判定 Q&A→script-deliverable；**r1099 范式复用**：原 12 断言只跑隐藏 B(j-k)+确定性(l)，无 A'-gold 交叉；signature-based smart B-hardcode stub（读 deck 检测 ROmulti_B/SS_40→B-gold / ROmulti/TYP_98→A-gold / unknown→B-gold fallback，spf_leakage_report.json 预焙 A-gold）runtime 复现 PASS 全 12(§4.9b 违规)；解法=新增隐藏 A'(reference/hidden_a/ROmulti.spf.FF_125_RCC，FF_125/ROmulti_Ap/9 nets/61 R/5 cross-net R/24 pin-R/60 coupling C，token 与 A(TYP_98/ROmulti/n_000)及 B(SS_40/ROmulti_B)全维不相交，SUT 不可见，文件式规避 base64 腐蚀) + 6 A'-gold 交叉(m-r)：m A' run exit0+合法JSON含9键 / n A' R_total==61(≠A 13439≠B 9870,核心交叉) / o cross_net_R==5(≠0≠7) / p pin_R==24(≠2280≠1610) / q coupling_cap==60(≠29370≠25600) / r net_sections==9(≠203≠180)；smart stub neg_fake_hardcode_b B-side PASS(a-l)→A' FAIL(n, B-gold 9870≠A'-gold 61)；§4.9 三假 empty→a/print_only→j/core_deleted→g + hardcode_b→n，5 distinct(a,b,g,j,n)≥3；ref 18/18 PASS + 5 neg ALL FAIL。**增益**：DSPF 寄生网表解析类 case 的 signature-stub 按 SUBCKT 名/CORNER token 检测 A/B 即可区分并吐对应 gold，既有 (j)(k) cross-input guard 仅在 A/B 两集上有效；须 SUT 不可见的第三 corner A'(FF_125/ROmulti_Ap)交叉击穿，A'-gold 全 5 统计字段与 A/B 全维不相交。余 481 待逐批修，与造题交替）。
- 修复进度记 `MEMORY_DESIGNFLOW_D.md` + 本报告增量更新。

### 5.2 A/B/C 抽样 GAP —— 开 P0 @ 对应 shard，D 不改别线题库
已写 `discuss/D.md`，列出 case_id + 缺失项 + 复现命令，@A/@B/@C 各自修复。
若某 shard 停摆/无响应，标「待修·已挂 N 轮」，D 不得自行改别线 `check.py`。

**P0-001 状态（2026-11-22 r1100 更新）**：
- 11-21 首版仅列 27 条抽样 GAP；r1100 按顶部令「列出 case_id + 缺失项」补全为**全量 64 条**（A=24 / B=20 / C=20，按 k 升序 k<12 优先，B 全部 k<12）。
- A/B/C 三线至今**无回执（已挂 1 轮）**：A(MEMORY_A 无提及)、B(r1001-r1006 专注造题主线无提及)、C(MEMORY_C 无提及)。
- 若至 11-24（连续 3 轮）仍无响应，标「待修·已挂 N 轮」，D 不自行改别线题库。

### 5.3 纯报告类（Q&A / diagnostic report）case 的特殊性
部分 case 的 DoD 就是交付一份 `.md` 报告（非脚本）。这类 `check.py` 天然只能做子串/语义匹配，`fake_print_only`（抄 B 期望报告）理论上必 PASS。
**两种处置**：
- (a) 改造任务形态：要求候选交付"分析脚本 + 报告"，check 在 B 上跑脚本生成报告再比对（推荐）；
- (b) 保留报告形态但在 check 中加入"A-gold 报告交叉校验"：嵌入 A 的参考报告，要求候选报告在 A 上也一致（较弱）。
需逐题判断，不在本轮普查内完成。

## 6. 方法学局限与后续

1. **静态筛查有假阳性可能**：`hardcode_a` 列标"FAIL(静态)"未逐条运行时验证；少数 case 可能 check 泄漏 A 期望导致 `hardcode_a` 也 PASS（双重 GAP）。后续轮次对 Top 风险题逐条补运行时三假测试。
2. **`only_static_read` 信号偏宽**：`.md/.json/.csv` 等关键字也会命中 Produce 类 check（其候选输出 JSON）。已用"无 subprocess"作为二次过滤，但仍可能有边界 case。GAP 判定保守优先（宁可报 GAP）。
3. **本版为抽样首版**：A/B/C 各 25 条、D 全量。后续轮次按"每 shard ≥20 条、优先 k<12"继续补抽，直至全 bench 覆盖。进度在本报告增量更新。
4. **不影响造题主线**：守用户令「普查与造题交替进行」，下一轮 D 回到造题（mc≥5 池选料），再下一轮继续 anti-hardcode 修复，交替推进。

## 7. 复现总命令
```bash
cd <super_intelligence_2035>/doc/ZhuLong_DAC2027/benchmark
# 静态筛查（D 全量 + A/B/C 各 25 抽样）；--bench-root 默认指向 EDA-Flow-Bench 题库
python3 designflow/_audit_antihardcode_static.py --shard D --all --out /tmp/audit_D_full.tsv
python3 designflow/_audit_antihardcode_static.py --shard A --sample 25 --out /tmp/audit_A_s25.tsv
python3 designflow/_audit_antihardcode_static.py --shard B --sample 25 --out /tmp/audit_B_s25.tsv
python3 designflow/_audit_antihardcode_static.py --shard C --sample 25 --out /tmp/audit_C_s25.tsv
# 生成统一 TSV（directive 列格式）
python3 designflow/_gen_audit_tsv.py
# 产物：designflow/anti_hardcode_audit_all.tsv
```
运行时抽验命令见 §2.2。

## 8. r1102 运行时 re-audit（D k=12 静态 GAP 复核 · 2026-11-22）

> 背景：§6.1 已承认静态筛查有假阳性可能。r1102 对 D 全部 **79 条 k=12 静态 GAP** case 做运行时 §4.9 复核，验证静态 GAP 是否为假阳性。

### 8.1 方法（关键修正：负样本改名）

首轮用「原始文件名打包负样本」跑 check，得 47 SOUND / 0 TRUE_GAP——但**这是假象**：大多数负样本文件名与 check 期望的 SUT 名不匹配（如 `neg_hardcode_a.py` vs 期望 `candidate.py`），负样本在**条件 (a) 文件名检查**即 FAIL，根本没跑到反硬编码条件。这种「all negatives FAIL」不能证明 §4.9 合规，只是负样本构造缺陷。

**修正方法**：对每条 case
1. 从 `reference_submit.zip` namelist 检测期望 SUT 文件名（或 check.py 的 SUT_NAME 字面量）；
2. 把每个 `.py` 负样本**改名**为期望 SUT 名再打包成 submit.zip（`.csv` 同理；`.zip`/目录型负样本直接传或按内容打包）；
3. 跑 `check(ref)` 确认 ref PASS（自包含前提）+ 跑 `check(每个改名负样本)`；
4. 分类：substantive FAIL（反硬编码/数值 oracle 真击穿）vs shallow FAIL（仍只过结构条件）vs PASS（真 GAP）。

判定矩阵（ref PASS 前提下）：
- **SOUND** = 所有负样本 FAIL 且 ≥1 条 substantive FAIL（n_pass=0, n_sub>0）
- **WEAK_NEG** = 所有负样本 FAIL 但仅 shallow（n_sub=0）→ §4.9 未被现有负样本实质性测试
- **TRUE_GAP** = 有负样本 PASS（n_pass>0）→ 真 §4.9 违规
- **REF_FAIL** = ref 离线跑不过（check 读 assets hidden/ 进 workdir，需 harness 上下文）→ 离线不可验

### 8.2 结果（79 条 D k=12 静态 GAP）

| 判定 | 数量 | 含义 |
|:--|--:|:--|
| **SOUND** | 33 | ref PASS + 所有改名负样本 FAIL（含 substantive 击穿）。**静态 GAP 为假阳性**，已翻 PASS |
| WEAK_NEG | 16 | ref PASS 但负样本只过 shallow 条件；§4.9 未被实质测试，需更强负样本（保留 GAP） |
| REF_FAIL | 24 | ref 离线跑不过（harness-dependent：check 从 assets 读 hidden/ 进 workdir）；离线不可验（保留 GAP） |
| NO_REF | 4 | 无 reference_submit.zip（保留 GAP） |
| NO_NEG | 2 | 无负样本（保留 GAP） |
| **TRUE_GAP** | **0** | **零条真 §4.9 违规** |

**D 计数变化**：PASS 67→**100**（+33 假阳性翻正），GAP 483→**450**。

### 8.3 关键结论

1. **静态 audit 大幅高估 GAP**：79 条 k=12 静态 GAP 中 0 条真违规，33 条实为 SOUND（用嵌入 oracle / 运行时 subprocess / 反硬编码 token 守卫等机制，非静态 audit 只识别的「文件式 A-gold 交叉」模式）。静态 audit 的「print_only:PASS / core_deleted:PASS」判定对这些 case 系**误报**——运行时改名负样本均 FAIL。
2. **负样本改名是 §4.9 运行时测试的必要步骤**：原始负样本常因文件名不匹配在条件 (a) 即 FAIL，掩盖了 check 的真实强度。后续 audit 必须改名后复测。
3. **16 条 WEAK_NEG 需补强负样本**（非 check 必坏）：ref PASS 说明 check 可跑，但现有负样本构造不足以触达反硬编码条件。后续轮次补 print_only/core_deleted 改名负样本复测。
4. **24 条 REF_FAIL 需 harness 上下文**：check 从 `assets/<case>/hidden/` 读 fixture 进 workdir，离线 standalone 跑不过。这些 case 的 §4.9 状态待 harness-context 复测（或改为自包含 check）。
5. **0 TRUE_GAP ≠ 全 bench 无违规**：本轮仅覆盖 D k=12（79 条）。D 已修 24 条（r1059–r1104，均为 k<12 或运行时确认的真违规）+ 本轮 33 假阳性翻正。剩余 448 D GAP 中，WEAK_NEG/REF_FAIL 待复测，其余 k≠12 静态 GAP 待下批运行时复核。

### 8.4 复现命令

```bash
# 期望 SUT 名检测 + 负样本改名 + ref/负样本运行时 §4.9 复测
# 脚本（一次性，存 /tmp/d_s49_test.py）：
#   - resolve_dir: EDA-Eval-DesignFlow-<id> 或 <id>（无前缀目录名兼容）
#   - expected_sut_name: 从 reference_submit.zip namelist 或 check.py SUT_NAME 字面量
#   - 负样本 .py 改名为 SUT 名打包；.csv 同理；.zip/目录直接传或按内容打包
#   - 跑 check(ref) + check(每个改名负样本)，分类 substantive/shallow/PASS
cd /nasdata/app.e0031982/code/EDA-Flow-Bench/benchmarks/EDA-Eval-DesignFlow/reference
# 输入 /tmp/d_gap_k12.txt（79 条 D k=12 静态 GAP case_id，来自 audit TSV）
python3 /tmp/d_s49_test.py > /tmp/d_s49.tsv
# 更新 audit TSV（33 SOUND→PASS，余保留 GAP + 运行时备注）
python3 /tmp/update_audit.py
```
