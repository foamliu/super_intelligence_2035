# post-1113 daily-log mining evidence (r507, 2026-11-14)

## 背景
- 1113 池 mc10.fresh(B)=65 (r506 peek 全质量饱和: filter-mislabeled / P-004 repeat)。
- 无新全量扫描 (latest = ssh_eda_search_20261113_131349, 41409 行, 已用)。
- 解锁路径 = post-1113 daily-log 挖掘 (B r481-r486 同法, 历史有效)。

## 挖掘
- 扫描 daily log: eda_trace_20261113.log (3087 行) + eda_trace_20261114.log (3034 行, 3030 qualifying)。
- 过滤: spice kw (hspice/finesim/spectre/ngspice/spice/custom_sim/siliconsmart/simulator) cnt>=8 且 mc>=10。
- 结果: 473 spice mc>=10 unique slugs (cand_post1113_r507.tsv)。
- 去重 vs 1113 scan summary.tsv slugs (4418): **458 in-scan → 15 truly-NEW** (全 srcday=20261114, 即 11-13 13:13 scan 之后写入)。
- 去重 vs 4-shard ledger (3601) + main/B jsonl (1086): **15 全 fresh** (cand_post1113_NEW.tsv)。

## 15 fresh 逐条 peek (first user_input, .75 dir-format ssh)
| slug | user | host | mc | spice ratio | first_user_input 摘要 | 判定 |
|---|---|---|--:|--:|---|---|
| 1794549248472_sjaal | e0024852 | hfeg0pkn005 | 971 | 0.264 | "看一下...仿真CH336_FS的后仿网表" | Q&A inspection, 非 produce |
| 1794559963037_mjde5 | e0044131 | hfeg0pkn003 | 641 | 0.335 | paste SRAM 2048x40 M16 B2 搭建工作总结 | context-paste, 首条非任务 |
| 1794557484096_ngrdc | joeyl | hfeg0pkn004 | 369 | 0.956 | bias 电路 5corner 电流 variation 缩小, 改 WCKIbBias_Res 电阻/opamp/电流镜尺寸 | **真 produce-task 但 P-004** (joeyl WCK cluster=CmlDividerSweepTbGen-001 progenitor) + 交互式 tuning + /rundata perm |
| 1794555552139_myisk | joeyl | hfeg0pkn004 | 356 | 0.956 | (ngrdc sibling, netlist194+hspice194 同构) | P-004 joeyl WCK |
| 1794548454276_0xbsc | jiangbaol | hfeg0pkn004 | 1569 | 0.409 | "duplicated subckt definition DqIb_2stg_DfeM6V2...该报错应该如何修改" | Q&A debug + jiangbaol P-004 |
| 1794550148719_diznh | jiangbaol | hfeg0pkn004 | 838 | 0.392 | (0xbsc sibling) | P-004 jiangbaol |
| 1794547075294_ad825 | joeyl | hfeg0pkn004 | 367 | 0.507 | (ssh timeout, joeyl WCK cluster) | P-004 joeyl |
| 1794551152849_i2ubt | joeyl | hfeg0pkn004 | 630 | 0.467 | (joeyl WCK cluster) | P-004 joeyl |
| 1794559210459_ct4gh | alexli | hfeg0pkn004 | 1649 | 0.078 | "Jobs are still PEND...cluster queue congested...keep polling" | 交互式 job-polling, 非 produce |
| 1794549576348_3c37v | jerrygu | hfeg0pkn003 | 542 | 0.144 | "请读取decqa项目中SCmosCtrl模块的电路。分析这个模块的功能。" | Q&A 分析, C-domain (schematic/calibre/virtuoso dominant) |
| 1794551024957_jc45u | e0044979 | hfeg0pkn003 | 459 | 0.181 | "Conly resistor instance issue...:pos terminal...Figure out the issue fix" | Q&A diagnosis PEX netlist, C-domain |
| 1794557926672_b3z68 | e0039816 | hfeg0pkn001 | 405 | 0.124 | "回答问题用中文描述" | context-setting (语言设置), schematic/pyAether dominant |
| 1794557266556_79wy5 | e0039816 | hfeg0pkn001 | 107 | 0.216 | "回答问题用中文描述" | context-setting, 同 b3z68 |
| 1794547133373_7uaan | e0046913 | hfeg0pkn003 | 83 | 0.333 | "make common...PrimeTime...lsb_init Failed...分析原因" | Q&A diagnosis, A-domain (STA/PrimeTime/LSF) |
| 1794551102851_uvwbt | yangyli | hfeg0pkn003 | 45 | 0.231 | "1" | empty input, 非任务 |

## 汇总 (15 fresh 分类)
- Q&A / inspection / diagnosis: 6 (sjaal, 0xbsc, 3c37v, jc45u, 7uaan, ct4gh)
- context-setting / paste / empty: 4 (mjde5, b3z68, 79wy5, uvwbt)
- P-004 cluster (joeyl WCK bias / jiangbaol): 5 (ngrdc, myisk, ad825, i2ubt, diznh) — ngrdc 唯一真 produce-task, 但 P-004 + 交互式 + /rundata perm

## 结论
- **0 clean B-domain produce-task** 于 15 fresh post-1113 候选。
- 累计 r506(1113 池 65 fresh) + r507(post-1113 15 fresh) = **80 fresh 候选全质量饱和**。
- fresh≠0 (mc10.fresh(B)=65) ⇒ **非池枯竭**, 实证为「质量饱和」(fresh 全 filter-mislabeled/Q&A/context/P-004 repeat/跨域), 与 r504-r506 同构。
- 15 候选全部 claim+park (parked 974→989), 防止未来 daily-log 挖掘重复 peek。
- 解锁需: 新全量扫描 (>11-14) 产生新 B produce-session, 或放宽 §5 L1/新 archetype (需用户授权)。

## 工件
- .75 workdir: cand_post1113_r507.tsv (473 spice mc>=10), cand_post1113_NEW.tsv (15 truly-new fresh), mine_post1113.py, dedup_scan.py, peek9e.py/peek6f.py
- ledger_B: 15 新 parked (slug 见上表)
