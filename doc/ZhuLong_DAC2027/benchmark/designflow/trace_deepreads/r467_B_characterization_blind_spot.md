# r467 B 线深读笔记 — characterization 域扫描词汇盲点（structural blind spot）

**日期**：2026-11-13 02:0x · **shard**：B · **轮次**：r467 · **类型**：域结构性分析（非单 trace 深读）

## 缘起

r466 立「characterization 在 1109 池 0 fresh-dominant, SiliconSmart/custom_sim kw 极少, 是另一结构性短板」但未量化。本轮做种群级量化，回答：characterization fresh=0 是「mined-out」还是「scan 词汇盲点」？

## 方法（.75 run_commands 只读）

### §1 1109 扫描 characterization 关键词命中

```
grep -icE 'siliconsmart|custom_sim|characteriz|liberty|timing_model|ccs|ecsm|nldm|timing_arc' \
  /home/t0002965/log/ssh_eda_search_20261109_224902/summary.tsv
→ 0
```

**1109 扫描 38082 行中 0 行含 characterization 工具关键词**（SiliconSmart / custom_sim / liberty / timing_model / CCS / ECSM / NLDM / timing_arc）。对照 spice 仿真器关键词：`spectre` 命中 2369 行、`hspice` 命中 8583 行 ⇒ 扫描能抓 spice 仿真器，**唯独抓不到 characterization 工具**。

### §2 daily trace log 交叉验证（11/10–11/13）

```
for d in 20261110 20261111 20261112 20261113; do
  grep -icE 'siliconsmart|custom_sim|silicon?smart' /home/t0002965/log/eda_trace_$d.log
done
→ 20261110: 0 / 20261111: 0 / 20261112: 0 / 20261113: 0
```

**daily log 4 天 0 SiliconSmart/custom_sim 提及**——盲点不只在 1109 扫描快照，在持续生成的 daily log 里同样 0。这不是快照过时，是**日志/扫描的 keyword 词汇表系统性不含 characterization 工具词**。

### §3 spice-filtered 池 mc≥10 top keywords（B 候选池源）

```
awk '$5+0>=10 && $6 ~ /hspice|finesim|spectre|ngspice|spice|simulator/' summary.tsv
| tr ';' '\n' | cut -d: -f1 | sort | uniq -c | sort -rn | head
→ 3756 hspice · 3316 netlist · 2321 schematic · 1775 synopsys · 1745 aether
   1705 analog · 1388 verilog · 1206 pyAether · 1180 drc · 1174 cmos
   985 lvs · 834 cadence · 833 waveview · 721 virtuoso · 680 spectre
```

**spice 过滤池被 netlist/schematic/verilog/drc/lvs 等非 spice token 大量稀释**——印证 r464「17/17 fresh 全跨域」：spice 关键词是一张宽网，捞进的 session 多数是 netlist/schematic-dominant（跨域），非 spice-dominant。spectre 仅 680（vs hspice 3756）⇒ Cadence spectre sim 在 cline trace 里远少于 Synopsys hspice。

### §4 现有 53 条 characterization case 的 trace 来源

B.jsonl 53 条 characterization case（OpampChar-001 / Sram6tDcChar-001 / NmosAgeChar-001 / GmidLut-001 / ButterflyCurve-001 / CpIcpChar-001 / StdLibCharTmpl-001 / CapCharProps-001 …）**全部经 spice 关键词命中**（hspice/spectre），trace 本身是 spice 仿真任务恰好做 characterization（如 GM/ID 查表、蝴蝶曲线、SRAM DC 特性）。**无一例经 SiliconSmart/custom_sim 关键词发现**——因为扫描里这类关键词命中 0。

## 结论

**characterization fresh=0 不是「mined-out」（被挖光），是「scan vocabulary blind spot」（扫描词汇表盲点）+ 「characterization 多走 batch flow 非 interactive cline」**：

1. **扫描词汇盲点**：scan/keyword 提取词表不含 SiliconSmart / custom_sim / liberty / timing_model / CCS / ECSM / NLDM / timing_arc ⇒ 即使 cline trace 里有 characterization 工具调用也抓不到。修法：扩 scan keyword 词表（非本轮可做，需 @A 改扫描脚本）。
2. **交互式覆盖盲点**：characterization（尤其 SiliconSmart lib characterization）通常走 batch/flow 脚本（run_siliconsmart.tcl + corners 批跑），**不走 interactive cline 会话** ⇒ 698 台 cline trace 天然不含这类工作。这是 cline-trace-based benchmark 的**结构性覆盖盲区**——只能抓交互式 EDA，抓不到批流式 characterization。
3. **53 char case 是 spice 副产品**：现存 characterization case 全是 spice 仿真任务里碰巧做 char（GM/ID、蝴蝶曲线、DC 特性），非 SiliconSmart/lib-char 工作流。characterization 域在 benchmark 里的「真实」占比被高估——53 条里 0 条是 lib-characterization 工作流。

## 对 P-004 / 论文的影响

- **P-004 fresh-pool track**：B 域 characterization fresh=0 的根因从「mined-out」修正为「scan 词汇盲点 + 交互式覆盖盲区」。这与 spice 域的「high-mc mined-out」（真挖光）是**不同根因**：spice 是数量枯竭（6/6 high-mc ledgered），characterization 是**从未被扫描发现**。修法不同：spice 靠新扫描，characterization 靠扩 scan 词表 + 可能根本无 interactive 源（需另寻数据源）。
- **论文 Q5（benchmark 演进 / 域分布）**：13 个域里 characterization（B 子域）的 case 来源有结构性偏差——53 条全来自 spice 副产品，0 条来自 lib-char 工作流。若论文声称覆盖 characterization，需在 Threats 注明「characterization case 经 spice 仿真间接获取，非 SiliconSmart/lib-char 直接工作流」。

## 本轮可做 case？

- mc≥10 fresh=15（r466 复算闭合真值）全非 B-dominant（r464 种群级）⇒ spice 域无可做。
- characterization 域 fresh=0 且根因是扫描盲点（非 mined-out）⇒ characterization 域无可做。
- **本轮 0 case（非池枯竭：mc10.fresh=15>0；根因 = fresh 全跨域 + characterization 扫描盲点）**

## 证据文件

- .75 run_commands 输出（grep/awk on summary.tsv + daily logs）见本轮 eda_flow session `shardB_20261113-r467_shardB-r467-charcheck_0`
- 本地 B.jsonl domain 分布：222 spice_sim / 53 characterization / 0 非 B 域（无 metadata.domain 误标）
