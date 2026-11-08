# R416 选料 + 交付轮（shard D · 2026-11-08 21:30–22:00）· 1 case 交付

## 目标
trace_ledger --shard D next → 候选池 mc≥30 D-domain（analog_context|schematic_netlist|waveform）→ cross-ref 4-shard 排除集 → 选 fresh 候选 → claim → 深读 → 合成 → 自验 → 落 D.jsonl。

## 选料路径 A（peek-based，0 seed）
`/home/t0002965/log/ssh_eda_search_20261105_192825/summary.tsv`（11-05 快照，已 3 天陈旧）。
- mc≥30 D-domain 命中：1607 行 / 1118 unique sids
- top 79 unique sids 中 fresh（不在 ledger_D）：1（puv3q，calibre-dominant physical_verify 非 D）
- Peek 7 fresh 候选（ap4dl/iih6g/oblxr/r7e7z/06htj/ipbrb/puv3q）**全部 parked 非 seed**：meta/Q&A/verification/env-debug/trivial-L1/wrong-shard。

## 选料路径 B（4-shard 排除集 + 深扫，命中 7u0m3）
peek 路径 A 枯竭后，改用 4-shard TSV 实读排除集（A+B+C+D 共 1787 sids，`designflow/_tmp/excl_all_sids_416.txt`）本地 grep `cands_D_mc30.tsv`（1693 行）：
- top 42 候选**全部 exclusion**（已在某 shard 台账）
- 深扫 rank 260+ 找到 **4 fresh** 候选：cpnbc / o0dm6 / bkeur / **7u0m3**
- 选 7u0m3（e0014566@hfeg0pkn005 mc=183）—— domain 匹配最丰富（schematic+netlist+pyAether+calibre+cellview+skill）
- claim：`trace_ledger.py --shard D claim --session 1785488442211_7u0m3 --user e0014566 --host hfeg0pkn005 --match 183 --domain schematic_netlist`

## 深读 7u0m3
RsCalc（寄生电阻计算）流程 on `austin_rscalc2/testa` 版图：80 msgs，模型 glm-5.1-cloud，状态 failed。工作流：生成 calcr 脚本→Virtuoso 批处理启动→检查 .rvn 结果文件与 calcr.log/rsb.log 日志→中文问答解释电阻值→版图优化。
真实资产可读性：trace 中 .rvn 片段可读（vdd 网络 `LV+RSView:NodeList,4` + 4 行节点记录，第 12 列电阻值 16.716/14.028/11.592/7.224）、calcr.log 可读（net name/node count/Succeeded Warning count:0）、rsb.log 可读（3-net M1/vbb/vdd 汇总）；但 RsCalc 结果目录 `/rundata/train/AI_Virtuoso/ver/rscalc/e0030265/testa` 下 `RSDB_<net>/` 为 e0030265 所属不可读 → **B-grade synthesized**。详见 `designflow/trace_deepreads/7u0m3_rscalc_analyze.md`。

## 交付 EDA-Eval-DesignFlow-RsCalcReport-001
- domain: schematic_netlist (shard D) · grade: B synthesized · level: L3
- 任务：写通用 `rscalc_result_report.py` 扫描 RSDB_<net>/ 子目录，解析 .rvn 第 12 列电阻 + calcr.log 状态/节点数 → 结构化报告（Total_Nets / [NetResults] per-net Status/Nodes/MaxR/MinR/AvgR / [SummaryStats] Total_Succeeded/Failed/Max_Resistance/Min_Resistance）
- 输入 A：3 Succeeded（M1/vbb/vdd，各含 .rvn + calcr.log）+ rsb.log
- 隐藏 B：4 net（vcc 214节点/5行.rvn, gnd 98/3行, io 178/6行 均 Succeeded；**clk 67节点 Failed 无 .rvn —— NA 边界**）+ rsb.log
- 12 条独立条件 a-l：d Total_Nets / e net 字典序[clk,gnd,io,vcc] / f clk Failed+Nodes / g clk NA 边界 / h/i/j vcc/gnd/io per-net 全字段 / k SummaryStats 全局统计 / l 3-seed 确定+无 A 名(vdd/vbb/M1)泄露
- 自验：ref PASS 12/12（A/B 双端）+ §4.9 三假（empty/print-only/core-deleted 全 FAIL）+ 2 neg（hardcode_A→d,e,f,g,h,i,j,k,l / ignore_failed→f,g,k 全 FAIL）+ 3-seed 一致
- byte-sync sha e40316cb size 14126
- D.jsonl 230 → 231
- 公开仓 PII 清理：calcr.log/rsb.log 中 e0030265/e0014566/austin_rscalc2/hfednd200//rundata 路径全部替换为占位符（*.log gitignored，git add -f 强制入库）

## 结论
- 1 case 交付（路径 B 命中 7u0m3）；路径 A peek 7 候选 0 seed（全 parked）。
- ledger_D：7u0m3 marked case（covered 227→228）；parked +7（路径 A）。
- D.jsonl 231。
- WAITING: 0 · DEBT: 0。
