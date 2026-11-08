# r399 选料筛选轮（shard D）· 0 case · DEBT:1（pool exhaustion）

> 日期 2026-11-08；r398 已交付 AutoCellRmAvPf-001。本轮选料筛选，peek 21 条 fresh 候选全判 non-seed / wrong-shard / dup，parked 入台账。**0 case 交付**：mc>=30 fresh 池对 shard D 已枯竭，mc 15-29 fresh 候选多为 Q&A/setup/debug/wrong-shard。

## 选料方法
- 扫描源：11-05 scan（`ssh_eda_search_20261105_192825/summary.tsv`，**已 3 天陈旧**，11-06~11-08 新 session 未捕获）
- shard D tools 过滤 `waveview|cosmos|skill|netlist|spiros|spectrum|analog|schematic`，mc>=30 unique 1168 条
- 排除 ledger_D 1291 anchor（本地 excl_D.txt）→ top 42（mc 592~1627）**全部在台账**
- 次批 mc 15-29（208 unique）多为 fresh，按 waveform-affinity + 非饱和用户(e0014566/xinqiaoz/miccao/ellawu/kenwang/yqlu/lvyy/jason17w/sinanz/ziyuny/tongfanl/haoyut) 打分
- .75 scp messages.json → python 解析首 2-3 user 轮判 seed

## 21 条候选 peek 结论

| session | user | mc | 判定 | 原因 |
|---|---|---|---|---|
| 1792395564570_r3gb7 | lorikx | 300 | **wrong-shard** | U#0「做个 lint 项目文件 + 综合流程，目标 rtl_synth 的 .v」→ RTL synthesis flow（digital_impl），非 shard D |
| 1782728857158_05p8p | e03179 | 303 | **non-seed** | U#0「确认连接 virtuoso 服务器」→ U#1「Virtuoso 未连接 排查」→ 连接/环境排障，无设计交付物 |
| 1789887279405_ve67l | mike | 308 | **non-seed** | U#0「执行 README.md 第一步」→ 意图模糊（cosim 执行），无可判定的 EDA 交付 |
| 1790230469843_kzlkh | lizwen | 303 | **wrong-shard** | U#0「DRC Testpattern Generator」调 drc_pattern_gen.py 生成 .oa → physical_verify/DRC（shard C） |
| 1787122756811_pj0ax | e0014566 | 394 | **dup** | U#0 rscalc RTEXT+checkPoints「先看 rscalc.config, 拷贝 layout, 打 RTEXT, 改 checkPoints」== RsCalcChk-001（ovo6z，逐字同） |
| 1783580842066_09kkp | e0014566 | 399 | **non-seed** | U#0「read prompt_powerfill.md and do the job」→ meta read-prompt-file（真实任务在附件 prompt，不透明） |
| 1785932055598_55ms0 | e0014566 | 311 | **non-seed** | U#1「PowerFill 为啥是 dummy fill 不降电阻？排查配置」→ debug，用户已指根因（配置问题） |
| 1788147634807_soqbk | e0014566 | 382 | **non-seed** | U#0「read prompt_flow.md」+ 5 个 rscalc 电阻分布报告 → meta + dup RsDistReport-001 |
| 1783596713423_53n4v | e0014566 | 320 | **non-seed** | U#0「hello」→ U#1「read prompt_powerfill.md」→ meta |
| 1793610069180_jq7tt | e0024852 | 29 | **non-seed** | U#0「run ...case3_6t8_run_tailor.sh error: dspf unrecognized arguments」→ fix-this-script debug（44 msgs） |
| 1792202007838_ms1ia | bowenguo | 27 | **non-seed** | U#0「如何连接 workspace」→ setup 问题（23 msgs） |
| 1793864108921_6g756 | e0039669 | 26 | **non-seed** | U#0「分析这个电路模块的工作原理和使用场景」→ Q&A（13 msgs，无交付物） |
| 1791954772268_0p3qp | t0002614 | 27 | **non-seed** | U#0「Do you know Finger Crossed Bit-line Counter Coupling Structure?」→ DRAM 概念知识 Q&A |
| 1790163316310_0wjop | e0027537 | 27 | **non-seed** | U#0「use chinese / How do I input Chinese」→ UI/setup（47 msgs） |
| 1793847299644_hu27g | thomasz | 28 | **non-seed** | U#0「看下 input.log 为啥退出了」→ sim log debug（41 msgs） |
| 1792467113057_ny0wi | e0022089 | 28 | **non-seed** | U#0「DDCPB test mode 有没有系统性教程材料」→ 教程 Q&A（43 msgs） |
| 1791964201857_q7jyk | eunicef | 27 | **non-seed** | U#0 EDA warning summary → U#1「将以上回复转为中文」→ translation（27 msgs） |
| 1793079626059_uhxqp | e0039102 | 27 | **non-seed** | U#0「如何将 Agent 部署到烛龙」→ U#1「你就是烛龙」→ harness meta（105 msgs） |
| 1793861357108_vagnh | tabtao | 29 | **wrong-shard** | U#0「调用 Makefile make dc_syn，dc.log 22294 行 Error 如何解决」→ synthesis flow debug（digital_impl） |
| 1793692406403_lcg3v | ronghu | 27 | **non-seed** | U#0 siliconSmart char config（power_meas_supplies/back_bias/netlist）+ hspice 失败 debug；borderline spice_sim（shard B），用户已指失败（31 msgs，有 deck.cir 附件） |

## 关键发现
1. **mc>=30 fresh 池对 shard D 真实枯竭**：top 42（mc 592~1627）全在台账；mc 300~600 次批的 fresh 候选绝大多数是 (a) wrong-shard（synthesis/DRC/digital_impl）(b) Q&A/知识/教程 (c) setup/UI/连接排障 (d) debug（用户已指根因/错误）(e) meta「read prompt_X.md」(f) dup（e0014566 rscalc = RsCalcChk/RsCalcLabelAdd/RsDistReport 系列）。
2. **e0014566 fresh 残余全是 rscalc/autovia/powerfill 重题**：pj0ax==RsCalcChk-001（逐字同），09kkp/55ms0/soqbk/53n4v 均为 powerfill/rscalc meta+debug+dup。该用户 65 条 ledger 条目，rscalc 三件套（RTEXT/RNODE/checkPoints）+ autovia/powerfill（生成/清除/同步）已全覆盖。
3. **mc 15-29 fresh 候选质量低**：208 条中高 schematic 计数者（jq7tt schematic 611 / ms1ia schematic 385 / 6g756 schematic 71）首轮均为 Q&A/setup/debug，非「提出需求」型 seed。低 mc 不代表低工作量，但首 user 轮意图模糊/非任务。
4. **scan 陈旧**：11-05 scan 已 3 天，e0042337/e0044131/e0039669/e0024852/bowenguo/ronghu/thomasz 等 11-06 后活跃新用户的部分 session 未在 scan，或 scan 内 session 已被 host 清理（r2314 shard C 亦观察到）。
5. **shard D 真跑 L2 seed 稀缺根因**：analog_context 真实可复现的只有 e0014566 rscalc/autovia/powerfill（已饱和）；schematic_netlist 真实建图多依赖 live Virtuoso/OA 沙盒不可离线复现（已转 mock-stub L2，#392/#390/#389 等）；waveform 真跑 waveview/Verdi 多 GUI 不可离线判（已转 mock #396）。fresh 真跑 L2 produce 几乎耗尽。

## 下轮（r400）第一件事：补 DEBT:1 + 找 seed
1. **触发 .75 rescan**（最高优先）：11-05 scan 陈旧，需新 scan 捕获 11-06~11-08 新 session（新用户 e0042337/e0044131/e0039669/e0024852/bowenguo/ronghu/thomasz/clwang/tabtao 等活跃）。rescan 后重跑 `trace_ledger.py --shard D refresh`。
2. **rescan 后若仍无 seed**：
   - (a) 拓展 mc>=15 + 排除饱和用户后的 fresh 池，对高 schematic/waveview 计数者逐条 peek（本轮仅 peek top-scored，未穷尽 208 条）；
   - (b) 评估 ledger parked 中「schematic-view」候选能否转 B-synthesized layout/schematic 题；
   - (c) 对 lcg3v 类 characterization debug 重新评估：用户首轮若未明指根因（仅给 config），可作 B 档「spec-driven 配置校验 + mock hspice 诊断」题（borderline analog_context / spice_sim，需 operator 裁决 domain 归属）。
3. **🚫 禁止连续两轮 0 case**：r400 必须交付 1 case，否则改主动 rescan + 降阈 + 拓展新用户 host，并把 pool exhaustion 升级 MEMORY 顶层告警。
4. 本轮已 parked 20 条（ledger_D parked 1043→1063），降低下轮重复 peek 成本。

## 台账
- parked +20（r3gb7/05p8p/ve67l/kzlkh/pj0ax/09kkp/55ms0/soqbk/53n4v/jq7tt/ms1ia/6g756/0p3qp/0wjop/hu27g/ny0wi/q7jyk/uhxqp/vagnh/lcg3v）
- ledger_D：case 217 · parked 1063 · 已动过 1280
- 未 peek 的 mc 15-29 fresh 候选（dwhjz/8tdfq/e0042337 netlist、xlzwr/ronghu、0ewj2/jiangbaol 等）留 r400 rescan 后再评
