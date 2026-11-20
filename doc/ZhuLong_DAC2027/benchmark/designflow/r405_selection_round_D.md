# r405 selection round (shard D) — 0 case · DEBT:1 hfhds201 cron-blind-spot scan confirms exhaustion

## 背景
#399-#404 六轮一致结论「shard D mc≥15 fresh 真实枯竭」。#404 用 11-08 新鲜 ssh 扫描复核（12 台 reachable host，295 recent，top14 peek，0 fresh D seed）。本轮 (#405) 用 **shard B 在 #r404 13:47 发现 bqszj 的同一 productive 路径** —— **hfhds201 本机 cron-blind-spot 扫描**（扫 `/home/*/.cline/data/sessions/` 全部本地 session，diff all-shard ledger 1805 sids）—— 复核 D-domain 枯竭。该路径 #404 未做（#404 扫了 12 台但不含 hfhds201 本机 walk）。

## 路径 — hfhds201 本机 cron-blind-spot 扫描（shard B productive 路径复刻）
eda_flow open_session(hfhds201) → `scan_D405.py` os.walk `/home/*/.cline/data/sessions/`（.75 本机，无需 ssh）→ 270 sessions → 筛 mtime≤45d → D-domain 关键词 (STRONG_D: fsdb/waveview/verdi/wv_/sx_/sw0/_wdf/subckt/.cdl/.spi/schEdit/abMatch/guardring/analogContext；SIM_KW: measure/hspice/finesim/primesim/spectre/tran/dc/ac/sp；WRONG: verilog/sdc/sta/primetime/innovus/calibre/lvs/drc/svrf/pnr/floorplan) → 命中条件 STRONG>0 OR (SIM>0 AND WRONG==0) → 88 D-domain 候选 → 本地 diff all-shard excl(1805 sids) + seed 分析（peek 首 3-5 user 轮）。

### 88 候选分类（按 strong hits desc）
1. **FineSim DC-non-convergence dup cluster（~20 sessions）**：全同「Finesim仿真报DC不收敛的错误, 可能的原因及解决方案有哪些?」→ shard B `uky6c` 已落 case。dup，🚫。
2. **Sine/cosine WaveView Tcl dup cluster（e0023936，~5 sessions: yrvv2/km0sb/g8ory/p5x6n/bqszj）**：全同「使用tcl代码，帮我画一个正弦/余弦波并计算过零点、估算频率与峰值」→ **同用户 e0023936**，shard B `bqszj`(CosineWaveAnalyze-001, 11-08 13:47 落) 已采纳 cosine。yrvv2(65 msgs, sine→cosine)/km0sb(1 msg)/g8ory(50 msgs, sine) 全同用户同任务模式 → 跨 shard dup。🚫（r404 已标「跨 shard 重复清理」为待办，不新增 dup）。
3. **「hi」/「who are you」non-seed（~8: z3212/nwl1p/gbjzx/z34dy/nt0pl/pl82z/x4y2u/oau5r/e179o）**：首用户轮无任务，strong 命中来自 assistant 长文。🚫 non-seed。
4. **License/env 排障 non-seed（~3: 18m80「Could not checkout Verdi license」/ rkdu8+0t51l「记住这个 mmsim.ini 路径先不分析」）**：环境/许可证 troubleshooting，无交付物。🚫。
5. **「explain this script」Q&A non-seed（n5hh7, tongfanl, 34 msgs）**：「帮我看下 dumpFSDB.pl 文件的作用」→「fsmchk 在干啥？」→「getcsv.pl 做了啥」→「vec2verilog.pl 做了啥」→「runsim.pl 做了啥」—— 纯脚本解读 Q&A，无交付物生产。🚫 non-seed。
6. **本机自测 session（y6sbk, user=e0031982=agent 自己）**：「帮我在 WaveView 中打开波形文件 input.fsdb」重复 2 次 —— agent 自测，🚫 自引用。
7. **role-prompt meta（uozyg, e0023936, 39 msgs）**：「你是一位精通 Synopsys Custom WaveView ACE Tcl 文档的 Tcl 脚本工程师……」—— role-setup meta-prompt，且同用户 e0023936（dup bqszj）。🚫。
8. **「Context summary」compacted non-seed（q9bnb/iuhvu/08aia）**：首用户轮是 compacted summary，非原始任务。🚫。
9. **已 IN-LEDGER（6: qb1ua[FM Tcl]/hsizo[netlist→finesim ignore]/kwiij[sim result grep]/68gc9[primesim compare]/3l3yx[primesim CRC]/p5x6n[cosine]）**：全 all-shard ledger 已收录。🚫。
10. **script-analysis non-seed（5cigt, sim=29）**：「分析下这个脚本」—— 脚本解读，无交付物。🚫。

### 汇总
| 类别 | 数量 | 处置 |
|---|---|---|
| FineSim DC dup cluster (shard B uky6c) | ~20 | 🚫 dup |
| Sine/cosine WaveView Tcl dup (e0023936, shard B bqszj) | ~5 | 🚫 跨 shard dup |
| hi/who-are-you non-seed | ~8 | 🚫 non-seed |
| license/env 排障 | ~3 | 🚫 non-seed |
| explain-script Q&A (n5hh7) | 1 | 🚫 non-seed |
| agent 自测 (y6sbk) | 1 | 🚫 自引用 |
| role-prompt meta (e0023936) | 1 | 🚫 dup+meta |
| compacted-summary non-seed | ~3 | 🚫 non-seed |
| 已 IN-LEDGER | 6 | 🚫 dup |
| script-analysis non-seed | 1 | 🚫 non-seed |
| **fresh D-domain synthesizable seed** | **0** | — |

## 结论
shard D mc≥15 fresh + hfhds201 cron-blind-spot **两路径全枯竭**，本轮 #399 起第 **7** 轮一致结论。**shard B 在 hfhds201 盲区找到 bqszj 的同一 productive 路径，对 D-domain 只产出 dup（uky6c/bqszj）+ non-seed**。agent 已无法在会话内自行破局，维持 #404 升级请求（按优先级）：
1. **触发 .75 全量 rescan**：summary.tsv 2026-10-28 已 11 天陈旧；scan infra 非会话内可做。
2. **shard 孤儿再分配裁决**：5 真孤儿中 ThkOxIdvgVthCheck-001(HSPICE Vth 提取) deepread 明文 shard B；若运维判定归 D（analog device char 边界），D 可采纳（需补 reference_submit.zip）。
3. **降阈扩池**：接受 mc≥10 D-domain 候选（#399 已试 mc15-29 全 non-seed；mc<10 信号更弱，需运维认可）。
4. **跨 shard 重复清理**：cpv3d(ConnFileNetChk-001) 同在 A+D jsonl；本轮又见 e0023936 sine/cosine WaveView Tcl 全归 shard B，D 不再新增同用户同任务 dup。

## 交付
- 🚫 0 case 落 jsonl（无新 D-domain seed 可合成，🚫 不越 shard / 🚫 不造低质 / 🚫 不判分歧义 / 🚫 不新增跨 shard dup）
- ✅ 选料复核记录（本文件）
- ✅ MEMORY_D 更新（WAITING:1 DEBT:1 + 心跳 + 流水 #405）
- ✅ ledger_D 无新增（无 claim/mark）
- 无新 PII / 无改 jsonl / 无动 EDA-Flow-Bench 仓
- eda_flow session 已 close_session(keep=false) 释放

## research 日报核对（2026-11-08）
11-08 research 日报 designflow 建议 = 「benchmark maintenance debt + 资源预算即测量规格」（论文 2611.08417 Terminal-Bench 2.0→2.1 审计）。与本轮 shard D pool-exhaustion 阻塞**无相关可执行条目**（rewrite_queue.tsv 15/15 done 无维护债；本轮是选料枯竭非判分/资源问题）。按 TASK 常驻令「无相关条目则忽略，不影响既有排期」—— 忽略，不影响 WAITING:1 排期。
