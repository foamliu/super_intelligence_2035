# Deepread — 1793609997920_hsw4o (xxchen @ hfeg0pbn011, mc=43)

- **trace_source**: user=xxchen, host=hfeg0pbn011 (10.129.2.11), session_file=1793609997920_hsw4o, match_count=43, keywords=netlist:39;analog:25;cmos:6;synopsys:1
- **domain**: schematic_netlist (SPF/DSPF resistance netlist parsing + graph traversal)
- **session size**: 1,228,028 bytes, 232 messages, 3 real user turns
- **freshness**: fresh-sid (not in 4-ledger). xxchen has prior D cases (not fresh-USER), pivot fresh-sid per #532/#533 strategy.
- **task family**: SpfTrueShortScan — 新建，非 dup（见下方维度正交）

## 用户原话（逐字，3 轮）

### U[0] (len=618)
```
问题反馈：
我看到了其中有很多的假错，如：
traceNet_291953474_DQSWrLvl1new_traceNet.rep
R29_492039     vdd2dq!:313777                   vdd2dq!:3335780                  480.979
路径中存在一个大电阻（>10 欧姆）的存在。这其实不是我想查的net.
结合 spf_specialCheck_sd_short.py 和 traceSPFresNode.py 脚本目的
设计一个新的检查脚本，查出SRC/DRN/GATE 到 power 真正short的 节点。
过滤掉path中存在大电阻的情况，只找到如下case：
traceNetRes_large.rep
R29_223932     XI_ChanMid.XI_DQPSD1.XI_DqPad_1.XI_IO_DqIoTop.XI_IO_P2sTop.XI_IO_P2sTopCore.XI_IO_TsacDcaLocal.XI_IO_DcaCoreVdd_1.XI_IO_TsacDcaLocal_buf1_0.XMMP0 :SRC vdd2dq!:3833826                  0.001
路径一直到 vdd2dq! 都是 0.001 （<10欧姆） 的情况。
考虑到SPF文件特别大 > 50G 有什么比较好的算法实现？
```

### U[1] (len=120)
```
修改需求如下
1）脚本不在进行：GATE的trace，只需要：SRC 和 ：DRN 即可
2）测试大节点时，只选择 power为 vdd2dq! 进行测试即可。
3）脚本过滤path改成，只保留路径中每个res的value 都是0.001欧
```

### U[2] (len=46)
```
给脚本spf_specialCheck_sd_true_short.py 写一个使用说明文档
```

## 任务机制（gold = 用户最终接受 agent 产物）

**目标**：`spf_specialCheck_sd_true_short.py` —— 在 StarRC DSPF/SPF 寄生网表中，找出 MOS 管 SRC/DRN pin **真正短路到 power net** 的节点。

**"真正短路"定义（关键，U[1] 第 3 条 + lessons #103）**：从 pin 节点到 `*|NET` head 节点（power net 名本身，如 `vdd2dq!`）存在一条路径，路径上**每一个电阻的 value 都恰好 == 0.001Ω**（per-element 规则，**不是** min-total-resistance）。
- ✅ true short: `0.001 + 0.001 + ... + 0.001`（全 0.001，path total = hops × 0.001）
- 🚫 false positive (旧 sd_short 漏报): pin → 0.001Ω → sub-node → **480.979Ω** → vdd2dq! head（路径含大电阻）
- 🚫 mixed path (lessons #103 关键修复): `0.001 + 5.0 + 0.001`（total = 6.002 < 10，但含 5.0Ω 非全 0.001）→ **必须拒绝**（用户要 per-element 全 0.001，不是 total < 10）

**SPF/DSPF 格式**：
```
*
*|DSPF 1.3
*|DESIGN <name>
*|DIVIDER .
*|DELIMITER :
*|SUBCKT <design> <ports>
*|NET <netname> <cap>
*|P (<portnode> <direction> ...)
*|I (<instpin> <inst> <pinname> <type> ...)
R<rname> <nodeA> <nodeB> <value>
*|ENDNET
.ends
```

**Power net 判定**：`*|NET` 名以 `!` 结尾（如 `vdd2dq!`、`vss!`）。U[1] 第 2 条：测试大节点时只选 `vdd2dq!`。

**Pin 判定**：`*|I (<instpin> <inst> <pinname> <type> ...)`，pinname ∈ {SRC, DRN, GATE}。U[1] 第 1 条：只查 SRC/DRN，不查 GATE。

**算法（agent 实测，56.5GB SPF 可流式处理）**：
1. 流式扫描 SPF，按 `*|NET` 段切分。
2. **parse-time pruning**：电阻行 `R<name> <A> <B> <value>` 若 `value != 0.001`（容差 1e-9）→ 立即丢弃，不入图（大电阻/假错根因永远不进图）。
3. 仅保留 `value == 0.001` 的边，构建 per-net 邻接表。
4. 从 net head 节点（`*|NET` 名本身）BFS flood，所有可达 pin 节点 = true shorts。
5. 报告行（TSV）：`net pin_kind attach_res pin_node power_node path_total hops` 流式写出。
6. 性能：56.5GB / 402M lines / vdd2dq! 7.1M edges kept / 250K dropped / 767s 一遍扫完。

**gold 标准样本**：
- TRUE short（须报）: `XI_ChanMid.XI_DQPSD1...XMMP0:SRC` → vdd2dq!, path total 0.035Ω, 35 hops, attach R29_223932, 全 0.001。
- FALSE positive（须拒）: `XI_...DQSWrLvl1new` path 含 R29_492039=480.979Ω。

## 工具链（agent 5 步）

1. `env_check.py` —— 只读检查 workspace 文件大小/内存/磁盘。
2. `spf_specialCheck_sd_true_short.py` —— 主脚本（流式扫描 + per-net graph + BFS flood + --selftest 13 checks）。
3. `run_bg.py` / `poll_true_short.py` / `kill_true_short.py` —— 后台跑 + 轮询日志 + 终止（52.7GB Channel.spf_RCC）。
4. `verify_true_short.py` —— 与旧 `sd_short.report` 交叉验证（subset rule + filtered FP count）。
5. `spf_specialCheck_sd_true_short_usage.md` —— 使用说明文档（U[2] 产物）。

**迭代关键（lessons.md）**：
- #1: GC thrash — 默认 cyclic GC 在 gen-2 扫数百兆对象 → 禁用 `gc.disable()`（pure-Python refcount 无环）。
- #2: 安全帽 — `--max-net-res` 默认 200M 边，vss! 地网 ~100M 边 / ~50GB RAM。
- #3（核心）: **per-element vs aggregate path semantics** — 初版用 Dijkstra min-total-R < 10Ω（错），用户要 **every res == 0.001Ω**（per-element）。`0.001 + 5 + 0.001` total=6.002<10 仍须拒。修法：parse-time 丢弃所有 ≠0.001 的边，图里只剩 0.001 边 → BFS flood 即 least-hop = least-R path。

## 维度正交（非 dup）

vs **SpfResPathTrace-001** (#506): 单目标节点 → min-total-R path 到 head net（优化问题）。本 case: 多实例 SRC/DRN 扫描 → per-element 全-0.001 boolean 分类（filter 问题）。机制不同（min-R vs all-equal-0.001）。
vs **SpfRccShieldDiff-001** (#516): 两文件 cap diff + per-net 屏蔽判定。本 case: 单文件 R-path short 分类。
vs **SpfCapResAnomaly-001** (#509): SPF cap/res 异常检测。本 case: true-short 分类 + per-element 过滤。
vs **PexNodeCapExtract-001** (#492): node cap 提取。本 case: resistance path，非 cap。
vs **RailMapMissingAudit-001** (#529): rail 枚举审计（4 输入）。本 case: SPF R-path 短路检测（单输入 + graph flood）。
vs **dlyg-0.001-insert case** (schematic_netlist): 在 .spf_RC 文件 .ends 前插入 `R_mid ... 0.001` 行（文件修改）。本 case: 解析 SPF 找 true short（只读分析）。

→ 非 dup ✓

## B-grade synthesized 合成设计（自包含）

**保留**：SPF/DSPF 格式解析 + power-net 判定（`!` 后缀）+ SRC/DRN pin 提取（`*|I` 行）+ per-element 0.001Ω 过滤 + parse-time pruning + BFS flood + TSV 报告。
**放弃**：56.5GB 流式性能优化（gc.disable / max-net-res cap / run_bg / poll / kill，纯工程性难≥8断言）；旧 sd_short 交叉验证（依赖外部旧 report，不可自包含）；使用说明文档（U[2]，纯文档性）；Channel.spf_RCC 真实大文件（不可打包）。

**A/B/C 不相交设计**：
- A: power net `vddA!`, pins `A_*`, true shorts 3 + FPs 2 + mixed 1 + GATE 2 + non-power 1
- B (hidden): power net `vddB!`, pins `B_*`, true shorts 4 + FPs 3 + mixed 2 + GATE 3 + non-power 2（counts 全异）
- C (嵌入 check.py): power net `vddC!`, pins `C_*`, true shorts 2 + FPs 1 + mixed 1 + GATE 1（反硬编码，最小）
- A/B/C prefix（vddA/B/C!）+ pin 前缀（A_/B_/C_）+ counts 全不相交。

**关键 fixture 设计（测 per-element 规则）**：
- true short: pin → R1(0.001) → n1 → R2(0.001) → ... → vddX! head（全 0.001，须报）
- FP large-R: pin → R(0.001) → sub → R(480.979) → vddX! head（含大电阻，须拒）
- **mixed path**: pin → R(0.001) → mid → R(5.0) → mid2 → R(0.001) → vddX! head（total 6.002<10 但非全 0.001，须拒 — per-element 规则核心）
- GATE pin: `*|I (...GATE...)` 即使全 0.001 到 head 也不报（pins=SRC,DRN only）
- non-power net: `*|NET sigA 0.5PF`（无 `!`）即使全 0.001 也不报
- pin-pin resistor: `R X:SRC Y:DRN 0.001`（两端都是 pin，非 power net 边，须正确处理）

**SUT**: `spf_true_short_scan.py` 纯 stdlib（argparse/os/re/sys/collections.deque），禁 subprocess/socket/urllib/ctypes/eval/exec/numpy/pandas + 禁 B/C 字面量。
**check.py**: 14 条件 a-n 独立 oracle（独立 re-parse + re-flood，不 import SUT）。
**negative**: empty / print_expected / hardcode_a / core_deleted ≥4 个，全 FAIL。
