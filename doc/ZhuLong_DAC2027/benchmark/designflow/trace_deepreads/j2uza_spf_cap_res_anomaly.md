# j2uza — SPF net cap+res 解析 + bus 分组 + 偏差/异常检测

- **session**: `1793757030814_j2uza.messages.json` · user `zongjiuh` · host `10.129.32.100` · mc=20 · domain `analog_context`
- **size**: 2,688,859 bytes / **747 msgs** / 8 user turns → 触发 TASK §3「单条 trace >2MB 或 >600 msgs 允许本轮只深读」例外，**DEBT:1，下一轮第一件事是交付 case**。
- **ledger**: trace_ledger_D.tsv 已 `claim` j2uza（2026-11-11）。
- **produce 性质**: 干净 single-produce（多轮演进，但同一交付主线：SPF → bus 分组 → 偏差 → 异常报告）。**非** Q&A/debug/code-review。

## 1. 任务（用户 8 轮原文摘要）

| # | msg | 用户意图 |
|---|---|---|
| 1 | #0 | SPF 文件 `m512Meg_U.spf.TYP_98_RCC` 记录 net RC 值，格式 `*|NET YioSelTop 0.000809724PF`。提取 `Yio0Msaq00<15:0>` ~ `Yio15Msaq00<15:0>` 共 256 根 net 的电容，按偏差判断有无异常。 |
| 2 | #141 | 多 section：`Yio0Msaq00`=section0、`Yio0Msaq28`=section28、`Yio0Msaq55`=section55，同一 bit 不同 section 本质同一根线 → **按 bit 把 `Yio0Msaq00~55` 电容累加后比较**。SPF 不含 `Yio8~15Msaq`，忽略。 |
| 3 | #283 | 比较 bit 电容时**按各个 Yio 分别比较**，不要所有 yio 混在一起。 |
| 4 | #316 | **加电阻**：`*|NET <name> <cap>PF` 下面有 `R13_1 YioTopN YioTopN:5 0.001`、`R13_2 * * <r1>`、`R13_3 * * <r2>`… `R13` 是该 NET 的电阻编号（不同 NET 编号不同），**真实 NET 电阻 = 各 `R13_*` 加总**。电阻加总后跟电容同样处理比较。另外**单独再比较一份 `Yio*Msaq00` vs `Yio*Msaq28` 的电阻和电容**，单独输出文件。 |
| 5 | #461 | 同法统计 **ABUS**：信号 `AbusEv(0~15)W_BG(0~3)Mid(Up/Dn)<7:0>`、`AbusEvUp(0~15)W<7:0>`、`AbusEvDn(0~15)W<7:0>`。**不要统计 E，不要按 bit 加总**。spf 路径 `…/ABUS/SpineTop.spf.TYP_98_RCC`。 |
| 6 | #565 | 报告里把**异常值 summary** 出来。 |
| 7 | #603 | `AbusEvUp<N>W<B>` 与 `AbusEvDn<N>W<B>` 一起对比；`AbusEvUp<N>W_BG<M><B>` 与 `AbusEvDn<N>W_BG<M><B>` 一起对比。即**是否带 BG 分开对比**。 |
| 8 | #673 | 修正：BG 组要匹配的信号是 `AbusEv(0~15)W_BG(0~3)Mid(Up/Dn)<7:0>`，**不是** `AbusEvDn<N>W_BG<M><B>`。 |

## 2. SPF 文件格式（DSPF 1.3，实测确认）

```
*
*|DSPF 1.3
*|DESIGN m512Meg_U
*|DATE "Mon Nov  2 17:16:59 ..."
...
*|NET Yio0Msaq00<0> 0.010269PF        ← net 总电容（PF），单行
*|NET Yio5Msaq38<15> 0.0071...PF
...
*|NET YioCECMsaq55<0> 0.00736731PF
C771166_1 YioCECMsaq55<0>:8 ...        ← 电容细分（不用于 net 总值）
...
R13_1 YioTopN YioTopN:5 0.001          ← 电阻段：R<编号>_<i> <net> <pin> <ohms>
R13_2 * * <r1>                          ← 第 2 段（node 名 * 表示内部）
R13_3 * * <r2>                          ← 第 3 段
...                                     ← NET 真实总电阻 = sum(R<编号>_* 的 <ohms>)
```

**关键解析点**：
- `*|NET <name> <cap>PF` 行 → net 名 + 总电容（PF）。用 `re.compile(r'^\*\|NET\s+(\S+)\s+([0-9.eE+-]+)PF')`。
- 电阻段：紧跟某 `*|NET` 行之后、直到下一个 `*|NET` 之前，形如 `R<k>_<i> <a> <b> <val>`。**同一 `<k>` 的所有 `_<i>` 段求和** = 该 NET 的总电阻（不同 NET 的 `<k>` 编号不同；用户明确「真实 NET 电阻为各个 `R<k>_*` 的加总」）。
- net 名含 bus 位：`Yio<N>Msaq<sect><<bit>>`，`<N>`=0~7（8~15 缺）、`<sect>`∈{00,28,55,…}、`<bit>`=<15:0>。

## 3. 金标准机制（assistant 产脚本，B-grade synthesized 抽象核心）

助手产多个迭代脚本：`analyze_caps.py` → `analyze_spf_caps.py` → `analyze_yio_caps.py`（Yio 电容+电阻，含 section 累加、按-Yio 分组比较、`Yio*Msaq00` vs `Yio*Msaq28` 单独输出）→ `analyze_abus.py` / `abus_summary.py`（ABUS，带 BG 分组、3-sigma+IQR 异常 summary）。最终交付落到 `/rundata/ddgoa/V0/simdir/finesim/workdir/zongjiuh/simulation/20261103_SPF_RC/{YIO,ABUS}/`。

**核心算法**（去重到可沙盒复刻的最小机制）：
1. **parse SPF**：逐行扫，命中 `*|NET <name> <cap>PF` 记录 net 总电容；命中 `R<k>_<i> <a> <b> <val>` 按 `<k>` 累加进「当前 net」的电阻段总和（`<k>` 是 per-net 电阻编号；遇到下一个 `*|NET` 切换 current net）。
2. **bus 分组**：按 net 名 regex 分组。
   - Yio：`Yio(?P<n>\d+)Msaq(?P<sect>\d+)<(?P<bit>\d+)>` → 按 `(n, bit)` 把各 sect 电容/电阻累加（同 bit 不同 sect = 同一根线）；再**按 n（每个 Yio）分别**统计。
   - ABUS：`AbusEv(Up|Dn)<N>W<B>` 一组（不带 BG）；`AbusEv<N>W_BG<M>Mid(Up|Dn)<B>` 一组（带 BG）；不按 bit 加总。
3. **偏差/异常检测**：每个分组算 `Mean / Std / CV%(=std/mean*100)`；两种 outlier 计数：
   - **3-sigma**：`|v - mean| > 3*std` 的成员数（3s 列）。
   - **IQR**：`v < Q1-1.5*IQR` 或 `v > Q3+1.5*IQR` 的成员数（IQR 列）。
4. **report**：每组一行 `Key / Mean / Std / CV% / 3s / IQR`；异常值 summary 单独列出（哪根 net、值、命中 3s 还是 IQR）。电容、电阻各一份；`Yio*Msaq00` vs `Yio*Msaq28` 单独一份。

**实测报告片段**（msg#584 ABUS 电容，确认列与算法）：
```
*** ABUS Capacitance Anomaly Summary ***
AbusEvUp<N>W<B>
       Key      Mean           Std        CV%    3s  IQR
       N=0   1.697841e-02   4.914917e-04  2.8948  0   0
       N=3   2.106375e-02   7.417682e-04  3.5212  0   3   ← IQR 命中 3 个
       N=11  2.668459e-02   7.265723e-04  2.7228  0   2
Parsed: C=640, R=640
```

## 4. B-grade synthesized case 设计（下一轮交付）

- **case_id 建议**：`EDA-Eval-DesignFlow-SpfCapResAnomaly-001`（analog_context, B-grade synthesized, L2）。
- **可见 A**：合成小 SPF（DSPF 1.3 头 + 8~12 个 `*|NET Yio<N>Msaq<sect><bit> <cap>PF` 行 + 每行下 2~4 个 `R<k>_<i>` 电阻段；2~3 个 sect，N=0~3，bit<7:0> 子集）+ example_output/report_A.json。
- **隐藏 B**（check.py 只跑 B）：不同 net 名前缀（如 `Dat<N>Sect<sect><bit>`）、不同 cap/res 值、不同 sect 集、**植入 1~2 个明显异常值**（让 3-sigma 或 IQR 命中 ≠0）；A/B net 名 + sect 名 + 编号空间完全不相交反硬编码。
- **SUT 交付**：`spf_cap_res_anomaly.py <spf> --out <report.json> [--bus yio|abus]`，纯 stdlib（禁 numpy/scipy/pandas/subprocess/calibre/pyaether/eval/exec/socket），输出 JSON 报告（不产 PDF/txt，便于 check.py 比对）。
- **check.py ≥8 条件 a-n（独立 oracle 重导 + 子进程真跑 SUT）**：
  - a zip 含脚本 + py_compile + 无禁止运行时 + 无 B 专属字面量硬编码
  - b JSON 顶层键齐全（bus_groups / per_group_stats / anomaly_summary / parsed_nets）
  - c parsed_nets 数 == oracle（B 中 `*|NET` 行数）
  - d 每个 net 的 cap == oracle（容差 1e-15 PF）
  - e 每个 net 的 total_res == oracle（sum of R<k>_* 段，容差 1e-15）← **核心：电阻段求和**
  - f bus 分组 == oracle（按 (n,bit) 累加 sect 后的组成员集合）
  - g 每组 Mean == oracle（容差 1e-12）
  - h 每组 Std == oracle（容差 1e-12）
  - i 每组 CV% == oracle（容差 1e-6）
  - j 每组 3-sigma outlier 数 == oracle（植入异常值必须被检出）
  - k 每组 IQR outlier 数 == oracle
  - l anomaly_summary 列出的异常 net 集合 == oracle（值 + 命中类型）
  - m 反硬编码 A（A 输入也跑通，且 A/B 输出互不泄漏、A/B 名不相交）
  - n 3-seed sha256 稳定（排序后确定性输出）
- **§4.9 三假**（空 zip / 错名脚本 zip / 非 zip）→ check() 顶部 early-return 全 REJECTED。
- **negative**：empty_shell / print_only / core_removed（删电阻段求和→e FAIL）/ static_a（硬编码 A 字面量→m FAIL）→ 全 FAIL，且命中条件互异。
- **断言清单**：`k 条断言：①…` 与 check.py 条件 a-n 一一对应，k_rationale == k_check（≥8，目标 14）。

## 5. 维度正交（非重复）

既有 D analog_context SPF/PEX 相关 case：
- `SpfResPathTrace-001`（#506 xxchen）：SPF **电阻网络路径** Dijkstra min-R 路径追踪（路径搜索）。
- `PexNodeCapExtract-001`（#492 renfengc）：**PEX** 文件 node 的 grounded/coupling/total/declared cap 提取（per-node cap，无分组/无异常检测）。
- `SpfTriggerMonitor-001`、`PowerSupplyHierInventory-001`：非 cap/res 解析。

**本 case = SPF `*|NET` cap + `R<k>_<i>` 电阻段求和 + bus 分组(Yio/ABUS) + cross-section 累加 + per-group Mean/Std/CV + 3-sigma & IQR 异常检测 + anomaly summary**。机制（电阻段按编号求和 + 双 outlier 准则 + bus 分组累加）与上述全不同，非重复。亦区别于 waveform 侧 #504 `CouplingPivotStats`（SPF 耦合 CSV 透视，非 net cap/异常检测）。

## 6. 下一轮计划（DEBT:1 偿还）

1. **第一件事**：按本笔记 §4 合成 `SpfCapResAnomaly-001`（assets A + hidden B + reference gold `spf_cap_res_anomaly_ref.py` + check.py 14 条件 + negative ×4 + negative_selftest）。
2. 自验：ref PASS 14/14 + negative 全 FAIL + §4.9 三假全 REJECTED + 3-seed sha256 一致 + 独立 oracle（重写一套 parse+stats，与 ref 互验）。
3. 断言闸门：`k_rationale == k_check == 14 ≥ 8` ✓ → 追加 `EDA-Eval-DesignFlow_D.jsonl` → `trace_ledger.py --shard D mark --session 1793757030814_j2uza --status case --case-id EDA-Eval-DesignFlow-SpfCapResAnomaly-001` → 日报。
4. 心跳：清 DEBT 0，恢复 `WAITING: 0`。

## 7. 沙盒不可复刻部分（B-grade 抽象理由）

- 真实 SPF 文件 `m512Meg_U.spf.TYP_98_RCC` 在 `/proj/ddgoa/` 私有路径，沙盒无访问 + 体量大（grep 全文件曾 SIGKILL 超时，见 msg#59）。→ 合成小 SPF 文本自包含。
- 真实 `/rundata/...` 输出目录 + 698 主机 + finesim 仿真上下文不可复刻。→ SUT 只产 JSON 报告到本地。
- ABUS 的 `AbusEv…Mid(Up/Dn)<7:0>` 复杂命名 + BG 分组规则（用户 #7/#8 两次修正）→ B-grade 保留**两种 bus 命名族 + 带/不带 BG 分组**的核心分组逻辑，但简化命名（A/B 用不相交的简单前缀，如 `Yio<N>S<sect><bit>` vs `Dat<N>S<sect><bit>`），不丢机制。
