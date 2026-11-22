# trace_deepread: 1791790142681_jnhb2 — joeyl FineSim DQS jitter duty-alternating PWL

- **session**: `1791790142681_jnhb2.messages.json` (joeyl @ hfeg0pkn004, mc=6, 7 msgs / 104KB)
- **scan**: `ssh_eda_search_20261121_151844` (no new scan since Nov 21 15:21, r1025 same as r1024)
- **keywords**: hspice:7;cmos:3;spectre:2;pdk:2;netlist:2;verilog:1
- **domain**: spice_sim (B shard)
- **case**: `EDA-Eval-DesignFlow-JitterDutyBlockPwlGen-001` (L1, pure Python, k=12)

## 真实意图（U0 原话）

> `/proj/drgqa/V0/simdir/finesim/workdir/joeyl/simulation/sim/SPF-sim/jitter/4_4555.sp`
> 请看这个bench，我想测得让它输入duty在5%拉偏情况下的jitter，但如果我直接把输入信号拉偏5%，实际上也测不出额外增加的jitter，因为只有输入一会儿是5050，一会儿是4555，才能对比得到大的jitter，但这好像很难在bench里写出来，你有什么办法么？

## trace 流（7 msgs，Q&A 探索，assistant 未交付最终方案）

- **msg0 U0**: 指向 FineSim bench `4_4555.sp`（DQS_block_check, jitter），问如何让输入占空比一会儿 50/50 一会儿 45/55 以测出额外 jitter。
- **msg1 A1**: thinking 理解问题（直接拉 45/55 电路会适应测不出 added jitter；需周期到周期占空比变化）。计划：读 bench → 理解激励（PWL/vpulse/PAT）→ 提方案（PWL per-cycle edges / B source / 脚本生成 PWL）。调 `get_agent_policy_status` + `read_files(4_4555.sp)` + `list_allowed_files`。
- **msg2-4**: tool_results — bench 读到（FineSim, .lib model.sp tt, .param DR=8E9/UI=1/DR/HDR=DR/2/period=1/HDR, VREF=0.75*pvddq, SWING=0.03875, tr=tf=SWING*2/slew, slew=4.75G）。关键：**输入源用 PAT**：
  - `V_DQS_N DQS_N 0 PAT (VIH VIL 12n tr tf 'period*0.45' b0101 RB=1 R=-1)`
  - `V_DQS_P DQS_P 0 PAT (VIH VIL 12n tr tf 'period*0.55' b1010 RB=1 R=-1)`
  - 注释掉的 PULSE 版本：`*V_DQS_N DQS_N 0 PULSE('VIH' 'VIL' 12n tr tf 'PWP' 'period')` 其中 `PWP='0.45*period-tr'`, `PWN='0.55*period-tr'`
- **msg5 A2**: thinking — bench 中间 stimulus 部分被截断，要读 lines 86-215 + 相关 bench（3_RJ.sp, 4phase8000.inc）。调 `read_files` 三文件。
- **msg6**: tool_result（lines 86-215，含 XI_IO_DqsRcvTop subckt 调用 + Input Setting 段）。**会话到此结束**，assistant 未给出最终方案。

## 关键观察

1. **真实意图清晰且 produce-able**：用户要一个输入时钟，占空比按段切换（50/50 段 + 45/55 段），整段重复，以注入周期到周期占空比变化测 jitter。
2. **PAT 源限制**：FineSim `PAT` 源占空比写死在 `period*0.45`，无法中途切换 → 需用 PWL 显式列拐点。
3. **bench 参数**：DR=8E9 (8Gbps), HDR=4G, period=250ps, VREF=0.75*pvddq=0.825, SWING=0.03875, VIH=VREF+SWING=0.86375? 实际 VIH/VIL 由 VREF±SWING。tr=tf=SWING*2/slew=0.0775/4.75G=1.63e-11? （trace 给出 .param 但未给最终数值，不重要——case 参数化）。
4. **trace 是 Q&A 探索型**（assistant 只读到 bench，未交付脚本）——但任务初衷明确说 analysis-Q&A/debug-Q&A 都是合法真实意图，且用户意图可 produce-化为参数化 PWL 生成器。

## reframe（合成方向）

**case = EDA-Eval-DesignFlow-JitterDutyBlockPwlGen-001**（L1, 纯 Python, 便携, 结构可判分）

`jitter_duty_block_pwl_gen.py --spec <spec.json> --out <pwl.inc>`:
- 读 JSON spec: node / vih / vil / tr / tf / period / td / blocks[{duty, n_cycles}] / n_repeats
- 输出 SPICE PWL .inc: `V_<node> <node> 0 PWL( + <t> <v> ... + )`
- 锚点 (0, vil)，每周期 4 拐点: (t,vil),(t+tr,vih),(t+duty*period,vih),(t+duty*period+tf,vil), t=td+k*period
- blocks 按 [N1@duty1, N2@duty2] 顺序拼成超级块，重复 n_repeats 次

**A** (可见, spec_A.json): node=DQS_P, vih=0.825, vil=0.4125, period=250ps, td=12ns, tr=tf=4.105ps, blocks=[{0.50,4},{0.45,4}], repeats=3 → 24 周期
**hidden B** (spec_B.json): node=WCK_P, vih=0.660, vil=0.330, period=200ps, td=10ns, tr=tf=3.2ps, blocks=[{0.50,5},{0.55,3}], repeats=4 → 32 周期（五重 anti-hardcode: 节点/电压/周期/延迟/分段数全异）

## check.py 12 条 (a-l, k_check=k_rationale=12)

①(a)zip+py_compile+size>200 ②(b)B exit0+非空.inc ③(c)PWL头/尾+节点==spec_B ④(d)时间严格递增+首点0+电压仅{vil,vih} ⑤(e)上升沿==下降沿==总周期数 ⑥(f)相邻上升沿间隔==period+首沿==td ⑦(g)block-1周期 high==D1*period ⑧(h)block-2周期 high==D2*period ⑨(i)tr+tf逐周期 ⑩(j)max==vih+min==vil ⑪(k)anti-hardcode DQS_P缺席+B节点在场 ⑫(l)3-seed sha256一致

**核心齿**: ⑧(h) block-2 占空比交替(反 naive 全 0.50) + ⑥(f) period + ⑦(g) block-1 + ⑪(k) anti-hardcode + ⑤(e) 周期计数

## 3 negs (§4.9 三假)

- neg_empty(空→a size199<=200)
- neg_print_only(硬编码 A DQS_P→c 节点不符 + h/k)
- neg_core_removed(读 spec B 正确但所有周期 duty 0.50 丢交替→h block-2 high=1.0e-10≠1.1e-10)

§4.9 三假全 FAIL ✓（自验实测：a / c / h 三齿分别击中）

## 自验

- ref jitter_duty_block_pwl_gen_ref.py → check.py **PASS 12/12 ✓**
- negative_selftest 3/3 **FAIL-as-expected ✓**
- 3-seed 确定性 ✓（ref 纯函数, %.12e 格式化）
- **tolerance 教训**: 初版 _close 用 `tol*max(1.0,abs(a),abs(b))` 对 ps 级值(1e-10)给绝对阈值 1e-9 → 5% 占空比差(1e-11)被吞, neg_core_removed 误 PASS；改为纯相对 `rel*max(abs(a),abs(b))+abs_floor` 修复

## distinct（vs 现存 B case）

- vs StimPWL-001(thqu 7输入V源HSPICE真跑) / PwlStimTransform-001(hairuizh 重命名PWL网) / WvCurPwlStimGen-001(yinyus 电流PWL平移) / BndGaussPwlGen-001(joeyl 高斯噪声PWL) — 本 case=**占空比分段交替时钟PWL生成器**(两duty比+块结构+边沿计算), 无重复 ✓
- vs DivSelDuty-001(wnyu 分频器占空比验证非生成) / DutyOffsetAlertMaxProduce-001(1xu8a .mt0后处理非激励) / DutyMeasMt0Report(bolint .measure非生成) — 本 case=生成激励非测量/后处理 ✓
- vs JitterTieRerun-001/Tr0JitterRemeas-001(joeyl jitter重跑重测) — 本 case=生成注入jitter的输入激励, 上游非下游 ✓
- vs PulseStimTbGen-001(单脉冲TB) / DcaStimSweepGen-001(.data sweep) / CmlDividerSweepTbGen-001(12TB swing/vref sweep) — 本 case=单时钟占空比块交替, 非sweep非多TB ✓
