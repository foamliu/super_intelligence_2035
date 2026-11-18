# xlzwr 深读笔记 — r885 cross-shard collision 发现

**session**: 1793692877234_xlzwr.messages.json
**user/host**: ronghu @ hfeg0plg93(10.129.8.225) / hfeg0pkn005(10.129.2.14)
**mc**: 27 (hspice:142;aether:81;netlist:58;schematic:27;.cdl:20;mixed-signal:19;lvs:14;floorplan:13)
**D-purity**: netlist/schematic/analog dominant, hspice-heavy (characterization context)
**ledger旧判**: parked 2026-11-13 03:56, "char hspice removal_hbm error debug '请分析原因', non-falsifiable explain"
**pool_reaudit_D**: 可造(需原型) log-grounded root-cause debug Q&A tool, cited-evidence-chain prototype-pending (r704/r712)

## 选料动机 (r885)

D-pure fresh 池耗尽 (r878, 11-16 快照) + truly-parked 候选清单剩最后一项 xlzwr (r880 audit: rser7/0uitr/9wc1h/xlzwr/iqj11 五条, 前 4 已 r880/r881/r883/r884 cased)。cited-evidence-chain 原型经 r881(FinesimSyntaxDiagQA)/r883(ParasiticsAnnotDiag)/r884(EsdEmTechViaKeyErrorDiag) 三条已 proven。xlzwr 是清单最后一项, 套原型立即可造。

## trace 深读 (25 msgs, agent=lead)

3 个用户轮 (mode="act"):
- **U0** (msg 0): 提供 ffrqN_Rfreshtokenx2 cell 定义 (pins Ck/CkN/D/Q/RN, add_flop IQ IQN Ck&!CkN D -clear !RN, back-bias supplies vbp/vcc/vbn/vss) + 2 条 hspice failure errors (Task 27 removal_hbm__RN__lh__CkN__hl__ACQ_1, Task 30 removal_hbm__RN__lh__Ck__lh__ACQ_1, both rc=1 "hspice exited with code 1: >error ***** hspice job aborted", SC-24/SMSC-95/CDPL-12) + "请分析原因" + 附件 deck.cir/ffrqN_Rfreshtokenx2.cdl.spf
- **U21** (msg 21): "两个文件已经上传" (re-attach deck.cir + cdl.spf, agent 之前找不到)
- **U23** (msg 23): ".lis文件已经上传，请分析" (attach deck.lis — decisive evidence)

assistant 3 轮递进归因:
1. (msg 20) 读不到附件, 基于报错+cell def 做技术归因: 猜竞态/悬空节点收敛塌陷
2. (msg 22) 读到 deck.cir+cdl.spf, 定位: removal 判据 glitch_check 要求 MAX v(Q)<0.24V (glitch_threshold_q=0.3 × Vcc=0.8), 但 vd_stim=0.8(D=1) 使 Q 释放后升到 0.8 必然 FAIL
3. (msg 24) 读到 deck.lis, 定论: transient 实际跑完收敛 (284100 points, 9.65s, 259504 iter), pivtol/singular supplies 是噪声; 真因是 PASSFAIL 优化器在所有 removal 取值上都 FAIL (Both end of window has same sign × 20+ 轮, bisection 从 ±1ps 扩到 ±1.2e-6), removal=failed/sis_passlist=failed/sis_faillist_check=failed → job aborted; 修复=removal 弧用 D=0(=复位值) + Ck/CkN 收敛成单一差分时钟

## 金标准事实 (从真实 deck.cir/deck.lis/cdl.spf 提取)

**deck.cir** (592 lines):
- L1: `.title removal_hbm__RN__lh__Ck__lh__ACQ_1`
- L67: `.param glitch_threshold_q = 0.3`
- L185: `vd_stim d_harness 0 dc 0.8` (D=1, 核心矛盾点)
- L544: `.meas tran glitch_check_hbm__ck__lh__q__lh_check MAX v(q) FROM = '1e-11 - m_constraint * removal'`
- L545: `.meas tran glitch_check_hbm__ck__lh__q__lh_value PARAM = '(0.24 - glitch_check_hbm__Ck__lh__Q__lh_check)>0'` (Q 峰值必须 < 0.24V)
- L560: `.tran 1e-11 1.136351e-07 sweep OPTIMIZE = opt1 RESULT = sis_passlist,sis_faillist_check`

**deck.lis** (2325 lines):
- L24: `**warning** pivtol too large ** reset to half minimum value of (gmindc,gmin)` (噪声)
- L26: `**warning** the following singular supplies have a terminal that is not connected` (噪声)
- L115-189+: `**warning** Both end of window has same sign.` × 20+ 轮, `extend bisection window to (X,-X)` 从 ±1.145e-12 扩到 ±0.00015833
- 末尾: `removal = failed / sis_passlist = failed / sis_faillist_check = failed / Failed Transient Data Sweep Occurs 24 times / ***** job aborted`
- transient summary: `transient 9.65s 284100 points 259504 iter rev=9290` (跑完收敛)

**cdl.spf** (72 lines):
- L28: `.GLOBAL vbn vbp vcc vss`
- L62: `.SUBCKT ffrqN_Rfreshtokenx2 Ck CkN D Q RN`
- L66: `MMP0 net5 RN vcc vbp ptn W=1.08u L=64n` (PMOS, RN 高时 net5 拉到 vcc → 复位低有效, Q=0 复位态)

## 🚨 cross-shard collision 发现 (r885 关键发现)

`trace_ledger.py --shard D mark --session 1793692877234_xlzwr --status case --case-id EDA-Eval-DesignFlow-RemovalUnsolvableDiag-001 --force` 触发警告:
```
WARN --force: session 已在他 shard B 台账 (status=case, case_id=EDA-Eval-DesignFlow-CharRemovalAbort-001, 2026-11-05 20:05)
```

**B shard 已于 2026-11-05 20:05 用同一 trace xlzwr 造了 `EDA-Eval-DesignFlow-CharRemovalAbort-001`** (domain=characterization, B.jsonl)。查 B case 的 real_task_summary:
> ronghu 用 Synopsys SiliconSmart V-2023.12-SP5 对标准单元 ffrqN_Rfreshtokenx2（异步复位 DFF, Ck&!CkN, RN 低有效复位, back-bias）做 timing characterization。两条 removal 弧（Task 27/30）同时 hspice job aborted... 本 case 抽取其「读 deck.cir+deck.lis+netlist → 结构化根因诊断」这一可复用子流，要求交付通用诊断器并在隐藏同类 deck 上交叉校验。

**与我拟建的 EDA-Eval-DesignFlow-RemovalUnsolvableDiag-001 完全同 trace + 同任务抽象 + 同诊断器交付形态 = 完整重复**。

## 裁定

🚫 **不造** (TASK 纪律: 🚫 改别人 shard 的 jsonl + cross-shard 互斥)。D ledger xlzwr 已 `mark --status parked --force` 还原, note 记 cross-shard dup of B CharRemovalAbort-001。

## 暴露的 cross-shard 去重漏洞

- xlzwr 在 B ledger 是 `status=case` (2026-11-05), 在 D ledger 是 `status=parked` (2026-11-13)。**4-shard 联合台账的互斥只靠 `--force` 警告, 不强制阻断** — 若 D 不 peek B jsonl 直接 mark, 就会产出重复 case 进 D.jsonl。
- pool_reaudit_D.tsv 把 xlzwr 标 "可造(需原型)" 时 (r699/r726 期) 未交叉验 B ledger 是否已 cased — **pool_reaudit 是 D 单方重审, 未对 4-shard 已-cased 集合做差集**。
- 建议 (discuss r888 议题): pool_reaudit_D.tsv 应补一列 `cross_shard_cased` (对 4-shard ledger status=case 集合做 in-check), 避免后续 revival 又踩同坑。

## truly-parked 清单终态 (r880 audit 5 条全部 consumed)

| sid | 命运 | 轮次 |
|---|---|---|
| iqj11 | D cased WvSignalDisplayGuideQA-001 | r880 |
| 9wc1h | D cased FinesimSyntaxDiagQA-001 | r881 |
| rser7 | D cased ParasiticsAnnotDiag-001 | r883 |
| 0uitr | D cased EsdEmTechViaKeyErrorDiag-001 | r884 |
| xlzwr | 🚫 cross-shard dup B CharRemovalAbort-001, D 不造 | r885 (本轮) |

**truly-parked 清单清零**。D 域 forward-work 路径:
1. 等 .75 新扫描快照 (r878 后无新快照, 最新 11-16) → fresh pool 补充
2. 转向 pool_reaudit_D.tsv "可造(需源)" 候选 (ad3nu cross-shard dup B / f4smw netlist-compare / trfp9 WaveView probe-reuse howto / 481m5 不feasible / 3anqw skill-launch) — 需 ssh fetch + deepread + cross-shard 验
3. **trfp9 (xiaoyu1d@hfeahpc501, waveform, WaveView probe-signal-reuse how-to)** 是下轮优先: prototype-proven (r711/r880 manual-grounded howto), self-contained (WaveView Tcl API 经 pyAether 可取, 无需 remote netlist fetch), 非 cross-shard dup (ledger 仅 D-parked)
