WAITING: 0
SHARD: A (digital_front)
DOMAINS: digital, eda_other, pnr_signoff, verification

- **PHASE**: shard A 新 case 合成阶段（断言债已清零）。负责 domain: digital, eda_other, pnr_signoff, verification
- 每轮做 1 条 case：trace_ledger.py --shard A next → claim → 深读 → 合成 → 自验 → 追加 EDA-Eval-DesignFlow_A.jsonl
- 📊 trace 覆盖率：9/1001 = 0.9%（covered=9 · case 9 · parked 1）
- 🎯 通过率: 0/0（A 档尚未实跑；先清断言债）· B 档目标 20–30%
- 🧾 断言: k_rationale=k_check 达标（今日 6/6 达标：Digital-010 k=19 / Digital-021 k=17 / Digital-022 k=17 / Digital-023 k=17 / CosimSetup-001 k=16 / WaveSig-001 k=17）· 队列清零 ✓
- 📦 体积：TASK≈17KB / MEMORY≈待测

### 2026-11-02 shard A 轮 5：WaveSig-001 新 case 合成 ✓（A 档 trace-faithful）
- 选料：trace_ledger.py --shard A next 给的候选全是物理/模拟域（calibre/hspice/skill），按 shard A 工具在 keywords 列重排，挑出纯 shard A 候选。t0002441@hfhds201 的 synopsys 会话是 AskEDA Q&A bot（agent=lead，非设计流），弃。最终选 `1793087996513_u78sz`（hengbow/hfeg0pgn045, mc=407, synopsys:1013=finesim+WaveView+verdi）—— DDR5 fullchip array coretiming 波形关键信号提取，domain=verification（覆盖 1→2）。claim → mark case。
- 深读：scp 整条 messages.json (511 msgs) + 真实产物 `/home/hengbow/zl_job/turboWave/fsdb/`（sig_demo.sig 1069B 格式参考 / _clean.sig 3367B raw 混合大小写 / coretiming_signals.sig **2747B 真实金标准** / 6 个分类中间 .sig / sxcmd.log 18661B WaveView ACE 验证日志）。用户真实意图：ddr5 fullchip finesim 波形查 array coretiming 违例 → 给 waveview 可 load 的关键信号 list → 格式同 sig_demo → **字母全小写**（raw 大写 netlist load 不到）。A 档任务说明=用户原话轮 3/5/6/8/9 逐字，根因反馈轮 7 作 hint 不进 prompt。
- 合成：A 附件=sig_demo.sig(格式参考·真) + hierarchy_manifest_A.txt(raw netlist 全路径, 混合大小写, 顶层/控制器/地址/电源干扰 + array coretiming 真信号) + user_request.md(用户原话)。隐藏 B(不进 SUT 沙箱)=hierarchy_manifest_B.txt(结构性不同: 前缀 xiatop_a1.xi_ary8g_a_t.xi_ary1g_g0.xi_m512meg_b02 / msaq 实例 7777 / WL sec t12·t13·t14 共 6 条 vs A 13 / BL bit<5> vs <11> / cslmsaqs01<31> vs cslmsaqs00<63>) + hidden_manifest.json。B 内嵌进 check.py 字符串(_MANIFEST_B)，assets/hidden/ 留底审计。
- L1 grader：check.py 17 独立标签 (a)-(q)。静态 .sig 解析(格式/全小写/SA≥3/列选 cslmsaqs/BL≥2/WL≥10 跨 sec×mq/dummy WL≥3/A 前缀一致) + **subprocess 在隐藏 B 上重跑候选 gen_coretiming_sig.py**(exit0/非空) + cross-input guard(B 前缀≠A / B 小写格式 / B WL 计数=6 且 sec=t12·13·14 / 无 A 专属 token lwdrq_msaq_5455·bgab01·m512meg_0·s54m0 泄漏) + 随机化(3 seed 打乱 manifest → 信号集合一致)。raw 大写 netlist(S54M0WLEU/Bla<11>/CK_t)→lowercase 陷阱 + 跨输入双前缀击败硬编码 A 的 fake。
- 参考解 `reference/gen_coretiming_sig.py`(类别 regex 过滤, 通用 A/B) + `coretiming_signals.sig`(生成器 A 输出 37 信号) + `coretiming_signals_B_check.sig`(B 输出 20 信号) + `reference_submit.zip`。真跑：A 输出 SA5+BL12+WL13+Dummy7；B 输出 SA5+BL6+WL6+Dummy3，全 B 前缀，无 A token 泄漏。
- 自验：ref reference_submit.zip check() PASS（17 全过）；**真实 trace 金标准 coretiming_signals.sig 也 PASS**（用户实际接受产物通过判分）；negative_selftest.py NEG_RC=0 全 5 FAIL（fake_empty→e / fake_print_expected→m / fake_core_deleted→d / naive_no_wl_filter→k / naive_hardcode_a_wl→m），3 §4.9 假 + 2 naive。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 字段 == disk check.py roundtrip OK；9 行/9 unique id 保留。trace_ledger.py --shard A mark → case（covered=9/1001=0.9%）。domain 覆盖：digital:4 · eda_other:1 · pnr_signoff:2 · verification:2。下轮：WAITING: 0。

### 2026-11-02 shard A 轮 2：Digital-021 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-021`（digital, PrimeTime 时序报告负 slack 路径提取, L1 离线 Python）标 `incomplete`：jsonl test 字段是旧 1568B 弱判分（4 packed 条件），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-021/check.py` 从 4 packed 条件 → 17 独立标签 (a)-(q)：
  (a)zip2files / (b)py_compile / (c)print-token-TOTAL/NEG/WORST_SLACK/WORST_ENDPOINT / (d)A-exit0 / (e)A-TOTAL=12 / (f)A-NEG=5 / (g)A-WORST_SLACK=-1.957 / (h)A-WORST_ENDPOINT=test_so[25] / (i)A-rerun-rpt-7fields / (j)A-rerun-rpt-test_so[25] / (k)A-rerun-rpt-(-1.957) / (l)A-rerun-rpt-exactly-5-Path-headers(no-MET) / (m)B-exit0 跨输入守护 / (n)B-TOTAL=9 / (o)B-NEG=4 / (p)B-WORST_SLACK=-2.483 / (q)B-WORST_ENDPOINT=wb_dat[5]
- 隐藏 B 附件 `assets/.../hidden/pt_reg2out_B.tarpt`：9 paths / 4 VIOLATED / worst -2.483 @ wb_dat[5] / func_ss_m125c_cbest_T + shift_tt_25c_cworst_T 视角，与 A(12/5/-1.957/test_so[25]) 结构性不同；B 不进 SUT 沙箱，check() 内嵌字符串。
- 参考解 `reference/extract_neg_slack.py` + `neg_slack.rpt` + `reference_submit.zip`；A 实跑 stdout `TOTAL=12 NEG=5 WORST_SLACK=-1.957 WORST_ENDPOINT=test_so[25]`，B 实跑 `TOTAL=9 NEG=4 WORST_SLACK=-2.483 WORST_ENDPOINT=wb_dat[5]`。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→b / fake_print_expected→i / fake_core_deleted→l / naive_wrong_neg→f / naive_hardcode_a→n），NEG_RC=0 全 FAIL，5 个不同标签。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 1568→14221B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-021 → done；剩 Digital-022/023 待整改（下轮第一件事）。

### 2026-11-02 shard A 轮 3：Digital-010 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-010`（digital, 4 通道 16-bit 带饱和乘累加器 MAC RTL + VCS 功能仿真, L2 真跑 VCS）标 `incomplete`：jsonl test 字段是旧 1123B 弱判分（k_check=0，substring-only），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-010/check.py` 从 0 实质条件 → 19 独立标签 (a)-(s)：
  (a)zip5files / (b)module-mac4 / (c)endmodule / (d)acc0-3 / (e)pos-sat-7fffffff / (f)neg-sat-80000000 / (g)wide-intermediate-longint / (h)submit-log-PASS / (i)submit-log-no-FAIL / (j)vcd-structure(>200B+$timescale/$enddefinitions/$var) / (k)VCS-A-compile-run / (l)A-PASS / (m)A-no-FAIL / (n)VCS-B-compile-run / (o)B-PASS / (p)B-no-FAIL / (q)checkpointB1-asym(7fffffff 80000000 0000002b 00000032) / (r)checkpointB6-neg-sat(80000000 x4) / (s)checkpointB7-post-reset-small(000f4240 x4)
- TRUE L2 grader：check() 在 .75 上用 VCS R-2020.12 重跑候选 mac4.v 对 (1) 原始可见 tb A（从 workdir 附件读，非提交件，防篡改）+ (2) 内嵌隐藏 tb B（结构性不同：非对称 per-lane / en=0 hold / 中途 reset / 负饱和 / 复位后小正值）。仅打印假日志或硬编码 A 向量者无法过 B 重跑。golden sat32 用 sized 64-bit 字面量（VCS R-2020.12 安全）。
- 隐藏 B 内嵌 check.py 字符串 `_TB_MAC4_B`（不进 SUT 沙箱）；经验值 B1=7fffffff 80000000 0000002b 00000032 / B6=80000000 x4 / B7=000f4240 x4。
- 参考解 `reference/mac4.v`（longint 中间量 + sized-literal sat32）+ `reference_submit.zip`；A 实跑 5 checkpoint 全 PASS(7fffffff/00000000/c0008000/80010000/80000000)，B 实跑 7 checkpoint 全 PASS。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→d / fake_print_expected→l(fresh-VCS-A-run 检测 acc=0≠golden, 击败 log-fake 攻击) / fake_core_deleted→e / naive_no_wide→g / naive_never_saturate→e），NEG_RC=0 全 FAIL，5 个不同标签。fake_print_expected 结构合法(过 b-j)仅在全新 VCS 重跑(l)失败——真正测试 L2 log-faking 防御。
- 闸门：k_rationale=19=k_check=19≥8 ✓；jsonl test 1123→13297B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- .75 sandbox 会话 `shardA_20261102-...Digital-010-rebuild_0`：declare_done + close_session(keep=false) 已清理。
- 队列 `rewrite_queue.tsv` Digital-010 → done；与 Digital-021 共计今日 2/4 达标，剩 Digital-022/023 待整改。

### 2026-11-02 shard A 轮 4：Digital-022 断言闸门整改 ✓
- 队列队首 `EDA-Eval-DesignFlow-Digital-022`（digital, DC 综合 DFT 插入失败根因诊断与修复, L1 离线静态 Tcl/report 检查）标 `incomplete`：jsonl test 字段是旧 1357B 弱判分（5 packed/substring 条件），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-022/check.py` 从 5 packed 条件 → 17 独立标签 (a)-(q)：
  (a)zip-exactly-2-files / (b)set_clock_gating_style-active-line / (c)active-control_signal-scan_enable[RC1 fix] / (d)no-active-control_signal-scan_mode[RC1 no-residue] / (e)active-set_dft_signal-Constant-scan_mode[RC2 fix] / (f)no-active-type-TestMode[RC2 no-residue] / (g)set_dft_configuration-fix_clock_gating-commented[RC3 fix] / (h)no-uncommented-fix_clock_gating[RC3 no-residue] / (i)ScanEnable-preserved-both-views / (j)scan_mode-Constant-both-views / (k)report-scan_enable / (l)report-TEST-130 / (m)report-Constant / (n)report-门控 / (o)report-扫描链/chain / (p)report-TestMode / (q)cross-input-guard: report generic ICG mechanism (ICG|测试引脚|test pin) 且不把 A 专属 731 当唯一解释（对隐藏 B 的 512 同样成立）
- 关键防御：注释剥离(_strip_comments) 只在活跃行检验关键配置，击败"关键词全放注释"的 fake_print_expected。
- 隐藏 B 附件 `assets/.../hidden/case_fail_B.tcl`：module PuTopSecDft / 门控控制信号误设 test_mode2 / scan_enable 端口 test_se / TEST-130=512 / chains baseline=256，与 A(PuTopDftEcc/scan_mode/scan_enable/731/390) 结构性不同；+ dft_drc_summary_B.txt + hidden_manifest.json；B 不进 SUT 沙箱。
- 参考解 `reference/dc_fixed.tcl`(=baseline 三 RC 还原) + `fix_report.md`(3-RC 诊断+ICG 机制+修改对照+指标对比) + `reference_submit.zip`。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty→a / fake_print_expected[keywords-in-comments]→c / fake_core_deleted[RC3 uncommented]→g / naive_break_scanenable→i / naive_no_generic_mechanism→q），NEG_RC=0 全 FAIL，5 个不同标签。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 1357→6209B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-022 → done；与 Digital-010/021 共计今日 3/4 达标，剩 Digital-023 待整改（下轮第一件事）。

### 2026-11-02 shard A 轮 5：Digital-023 断言闸门整改 ✓（队列清零）
- 队列队首 `EDA-Eval-DesignFlow-Digital-023`（digital, VCS 编译/仿真 makefile 参数化改造, L1 离线静态 + GNU make -n 干跑）标 `incomplete`：jsonl test 字段是旧 1500B 弱判分（4 packed/substring 条件），rationale 是散文。
- 本轮重建磁盘 `reference/EDA-Eval-DesignFlow-Digital-023/check.py` 从 4 packed 条件 → 17 独立标签 (a)-(q)：
  (a)zip-exactly-3-files / (b)make-n-valid-syntax / (c)MOD-?= / (d)CONFIG-def / (e)RTL_F-?= / (f)NET_F-?= / (g)PR_NET_F-?= / (h)TB_TOP-?= / (i)UPF_FILE-?= / (j)QUEUE-?= / (k)ONLINE-?= / (l)-include-$(CONFIG)/cfg/$(MOD).cfg-dash-optional / (m)comp/comp_net/comp_pr_net-body-uses-$(RTL_F)/$(NET_F)/$(PR_NET_F)-no-literal-pu.f / (n)run-rule-bsub-guarded-by-$(if)-ONLINE-switch / (o)tpl_mod.cfg-7vars-plain-=-no-?= / (p)README-优先级+接入+var-table>=6 / (q)cross-input-guard
- L1 grader 用 GNU make 4.3 `-n` 干跑（不执行 VCS，只展开 recipe），校验 makefile 语法合法 (b) + 变量替换正确 (q)；注释剥离 (#) 后在活跃行检验变量定义与 rule body。
- 隐藏 B 配置卡 `assets/.../hidden/cfg/dma.cfg`（DMA 模块：DmaTop/normal/dma.f/dma_net.f/dma_pr_net.f/../../upf/dma.upf/FF_85，与 A 的 PU: PuTopDftEcc/gputest/pu.f/../../upf/sim.upf/TT_25 结构性不同）+ hidden_manifest.json；B 不进 SUT 沙箱，check() 内嵌 `_CFG_DMA` 字符串在临时目录写出后 `make -n MOD=dma CONFIG=cfg/dma.cfg ONLINE=0 comp run verdi`，断言输出含 dma.f + DmaTop 且不含 bsub/pu.f/PuTopDftEcc/work_pu —— 击败把 `-top PuTopDftEcc` 硬编码进 verdi rule body 的 fake_print_expected（过 a-p 静态，仅 (q) 失败）。
- 参考解 `reference/makefile_para`（?= 默认保 PU 行为 + -include $(CONFIG) + $(if $(filter 1,$(ONLINE))...) bsub 守护 + WORK=work_$(MOD)_mix_power_case）+ `cfg/tpl_mod.cfg`（7 变量普通 = 占位符模板）+ `cfg/README.md`（变量表 12 行 + 优先级 + 新模块接入 7 步）+ `reference_submit.zip`；默认干跑复现 PU（pu.f/work_pu/bsub -q gputest），DMA 干跑复现 dma.f/DmaTop/无 bsub。
- negative/ + negative_selftest.py：3 §4.9 假 + 2 naive（fake_empty->a / fake_print_expected[hardcoded -top PuTopDftEcc in verdi]->q / fake_core_deleted[comp body -f ../tb/pu.f]->m / naive_no_online_switch[unconditional bsub]->n / naive_qmark_in_cfg[tpl cfg ?=]->o），NEG_RC=0 全 FAIL，5 个不同标签。
- 闸门：k_rationale=17=k_check=17≥8 ✓；jsonl test 1500→9803B 同步（test==disk check.py roundtrip OK）；7 行/7 unique id 保留。
- 队列 `rewrite_queue.tsv` Digital-023 → done；今日 4/4 达标，shard A 断言债清零 ✓。下轮起开新 case：`trace_ledger.py --shard A next → claim → 深读 → 合成`。

### 2026-11-02 shard A 轮 6：EDA-Eval-DesignFlow-CosimSetup-001（断言债清零后首条新 case，L2 真跑 tcsh）✓
- 选料：trace_ledger.py --shard A next → 在 .75 summary.tsv 按 shard A tools 过滤取候选；最高 mc=679 是 johnl/mt7ua（已 parked，Innovus PnR+GenLEF 无 self-contained L2 grader）；按 domain 偏好扩展扫描，选 `1789887279405_ve67l.messages.json`（mike/hfhds211, mc=279, innovus:100+voltus:98+synopsys:2264）—— DDR6 logic-cosim (SystemC phy_model+VCS+Spike) Quick Start 多步构建编排 trace（695 msgs/2.6MB）。claim domain=eda_other。深读：scp 整条 messages.json 到 .75，解析 user 22 轮意图 + assistant 工具链，提取真实 setup_standalone.csh 全文（118 行 csh/tcsh）+ 真实 8 个预编译产物清单 + 真实 Step-1 stdout（`Standalone environment setup complete!`）。
- 合成：A 档 trace-faithful Step-1 子任务。A 附件 = 真实 csh + manifest + 8 个 truncate stub 产物（按真实字节）。隐藏 B 结构性不同：gcc 11.3.0 / spike gcc-9.3.0_Aug14_2026_v2 / systemcDir 2024.06-SP1-1 / 安装根 /proj/dscqa/phyv_n6_arch_sim_1/wanglj / license 占位符 LICENSE_SERVER_PLACEHOLDER / boost 1.81.0 / 全部产物 size 不同（ddrArchmodel 158M vs A 126M）。B 不进 SUT 沙箱，check() 内嵌字符串 + truncate 重建。
- L2 grader：check.py 16 独立标签 (a)-(p)。静态 csh 解析（set/setenv + $var/${var} 展开）+ 8 产物大小校验 + license 占位符 + /proj//tool/ TODO 标记 + **真跑 tcsh source**（subprocess `tcsh -c 'source ...; echo ENV_REAL ...'`，验证 D6_DIR/SYSTEMC_HOME/VCS_HOME/SPIKE_DIR/RISCV_PATH/VERDI_HOME 真被设置 + libboost_program_options.so 软链接真被创建）。cross-input guard (m)(n)(o)(p) 在 B 上重跑候选，击败硬编码 A 的 fake_print_expected 与 naive。
- 自验（.75 hfhds201, tcsh 6.18.01）：verify_env.py 在 A 上 exit 0（12 ENV_OK + 8 ARTIFACT_OK + 3 LICENSE + 9 TODO + 6 ENV_REAL + SYMLINK_OK）；check.py reference_submit.zip workdir_A → CHECK PASS（16 全过）；negative_selftest.py NEG_RC=5 全 FAIL（fake_empty→b / fake_print_expected→m / fake_core_deleted→j / fake_hardcode_sizes→o / fake_literal_license→n，5 标签），REF re-PASS。**真 L2：tcsh source 实际执行，env var 与软链接真实生效。**
- 闸门：k_rationale=16=k_check=16≥8 ✓；jsonl test 11163B == disk check.py roundtrip OK；8 行/8 unique id 保留。trace_ledger.py --shard A mark → case（covered=8/1001=0.8%）。domain 覆盖：digital:4 · eda_other:2 · pnr_signoff:2 · verification:1。下轮：WAITING: 0。
