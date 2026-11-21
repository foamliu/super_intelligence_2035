# Deepread: yin5a (mingyu1l @ hfeg0pkn005, mc185) — r1093

- session: `/home/mingyu1l/.cline/data/sessions/1795154523593_yin5a/1795154523593_yin5a.messages.json` (911KB, 63 msgs)
- domain: analog_context (后仿 post-layout sim 诊断), D-pure (schematic:1151 / netlist:943 / pex:340, C-关键词 lvs:92/calibre:2 远低)
- 真实意图: 用户 mingyu1l 在 FineSim 上对延迟链 `trimnand2_RdColPlsGenNewB_dly` 做后仿，发现「数据有问题不是报错」——后仿 tr(277ps) 比前仿 Baseline(448ps) 还快 38%，物理不可能。要求 agent 找原因 + 解决方案。用户随后逐版改 testbench.sp，agent 每版验证。

## agent 取证链 (msg #1-#62)
1. msg#1-14: 读 verify_summary.csv / code_sweep.data / testbench.sp → 发现 testbench 第20行 `.inc` schematic 网表、第22行 `.inc` SPF(而 `finesim_spf` 选项被注释)、第24行 `Xdut` 被注释；FF角比TT慢(反常)。
2. msg#8-14: 对比 Baseline(448ps) vs 最新 261120_1318(277ps)。读 sim log 电路统计: `# MOSFET:90 / # Resistor:23 (Max=243.43) / # Capacitor:192 (全同 1.86723e-15)` → 23R=21 switch_close+2 parasiticRC2，192C 全同值=parasiticRC2 的 (Cg+Cc+Cov)/2 → **DSPF 几千寄生 R/C 一个没进电路**。根因: schematic 网表把 DUT 平铺顶层(`**TopDesStart..TopDesEnd`，无 `.SUBCKT` 包装)，`.inc` 进来的 SPF 只定义了一个没人例化的 subckt → 死代码。
3. msg#16-22: 读 spf_RCC 确认是**纯寄生文件**(只有 R/C + `*|I` 器件引脚注释，无器件行) → 必须用 `.option finesim_spf=` 标注，不能 `.inc`。回溯 261119_2033 第一次后仿: log 第56行 `WARNING! unknown option finesim_spef` → **选项拼错**(finesim_spef 应为 finesim_spf)，FineSim 静默忽略。读 netlist.postsim: 流程脚本生成，删了 parasiticRC2 + STI 电容，库单元改名 _org，正是配合 finesim_spf 标注的正确底座。
4. msg#24: agent 试图 editor 改 testbench.sp 被策略引擎拦截(仿真目录不在 writableRoot) → 给出根因+可粘贴补丁(prose 交付)。
5. msg#27-50: 用户逐版改 testbench，agent 验证:
   - 1409: `.inc`SPF + Xdut(9端口) → `port size mismatch(9 vs 12)` 挂
   - 1414: schematic 网表 + `.inc`SPF + Xdut 打开 → **两份 DUT 并联**，数据作废
   - 1418: 仅 DSPF + switch_cell.inc + Xdut(12端口) → 162 MOS/3304R/4350C，tr=286ps ✅(DSPF 独立流程)
   - 1421: schematic 网表 + `finesim_spf` 标注 → 100% matched 但 tr=423ps ⚠️(parasiticRC2 重复计算)
   - 1433: netlist.postsim + `finesim_spf` → 21R(Max=0.001)/324C/SPF Res 2740/SPF Cap 4026，tr=286ps ✅ 与 1418 互验 0.01% 偏差
6. msg#51-62: 用户质疑「前仿1400ps现在变小这么多」→ agent 举证 Baseline 是 11-13 旧 schematic(器件 nf=1/2)，11-19/20 改大(nf=2/3)，延迟下降是设计改了非后仿问题；并指出 SPF 反标是「叠加」非「替换」——parasiticRC2 与 SPF 共存会重复计算。

## 可 checkable 的取证事实 (reframe 为 pex_effective_audit.py)
- SPF 引入方式: `.inc .spf`(死代码) vs `.option finesim_spf=`(正确) vs 拼错 `finesim_spef`(typo_ignored)
- Xdut 例化状态: instantiated(双DUT风险) / commented / absent
- netlist parasiticRC2 实例数 + 挂靠节点
- sim.log 电路统计: MOSFET/Resistor/Capacitor 计数 + Resistor Max(243.43=parasiticRC2指纹) + Capacitor Min==Max(全同=schematic寄生指纹)
- SPF 标注统计: `# SPF Res` / `# SPF Cap` (>0 = 寄生真进电路 = pex_effective)
- `WARNING! unknown option` 选项名
- 后仿 tr vs 前仿 tr: faster(物理可疑)/slower(自洽)

## 合成决策
- 真实交付 = prose 诊断 + testbench 补丁(被 policy 拦) → 纯 Q&A 交付 prose，check() 直接判 prose 没牙(文本子串匹配)。
- 守 r1083/r1088 reframe 范式: 把 agent 手工做的「后仿寄生有效性取证」自动化成 `pex_effective_audit.py`(对任意 FineSim 后仿 run 可运行的审计工具)。
- asset A = trace 1318 原案(testbench_A.sp: .inc SPF+finesim_spf注释+Xdut注释; netlist_A.sp: 2 parasiticRC2 flat-top DUT; sim_A.log: 90MOS/23R/192C 纯schematic; baseline_A.mt0: 448ps 前仿)
- hidden B(check-only) = 不同故障组合: finesim_spef typo(生效)+Xdut instantiated+schematic 网表; 3 parasiticRC2; 120MOS/25R/198C 全同; SPF Res/Cap=0; unknown_option=finesim_spef; 后仿310ps<前仿520ps(faster)
- hidden A'(anti-hardcode, 同名异内容) = CLEAN: netlist.postsim + .option finesim_spf + Xdut 注释; 0 parasiticRC2; 162MOS/21R(Max=0.001)/324C 非全同; SPF Res 2740/SPF Cap 4026; pex_effective=True; 后仿286ps>前仿210ps(slower) → B vs A' 每维不同, 击穿 B-hardcode stub
- check.py k=17(a-q): B-side 13(a-m) + A' 交叉 4(n-q), 独立 oracle 实时从 B/A' 文件算金值
- §4.9 三假: empty->b(空stdout) / print_only->n(A'交叉: 打B的JSON在A'上失配) / core_deleted->c(B spf_mode 不符) + hardcode_b->n(A'交叉), 3 distinct fail letter (b,c,n) ≥3
- 自验: reference_submit.zip 跑 check.py PASS(17/17) + negative_selftest 4 fake 全 FAIL 3 distinct(b,c,n)
- D.jsonl 568→569, byte-sync sha=a8a5aeef589037427988a6edce1a7586ff699c230bea7fa7a5a6bdc8ad7dfafc/size=11843

## 选料背景 (r1093)
- 高 mc D-pure 池已采空(r1091 结论再确认: 1i0em/0wqbh/1nsgi/4chsl/fl4rh/2mwdb 等全 case/parked)。
- 本轮 .75 summary.tsv(20261121_151844) D-pure filter(ds≥cs, mc5-250) 948 候选, 4-shard 台账(4213 slug)交叉去重 → fresh 8 条 peeked: yin5a(mc185)/gw1z7(mc106)/exhq3(mc140)/gqp76(mc52)/ivkz8(mc53)/z4w3g(mc107)/pofwk(mc127)/25kpf(mc19)。
- ivkz8/pofwk/gw1z7 实 peek 后判 B-domain(spice_sim/characterization: aging rerun / PVT sim env / Verilog+pt_shell STA) → 跨域交 B, 不自造。
- 2mwdb(parked 空 note) peek = fsmchk log 诊断 Q&A(257 msgs, 同 check-weak) → 不 reconsideration。
- yin5a = 唯一 D-domain(analog_context) fresh + reframe 可 checkable → 选定。
