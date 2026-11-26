# trace_deepread: p0nyi — ruisongs xrun 仿真计时对比诊断

- **session**: `1793597102437_p0nyi.messages.json`
- **user/host**: ruisongs @ hfeg0pfn090 (10.129.33.216)
- **mc**: 55 (verilog:1395; lvs:52; netlist:40; .spi:38; analog:15; pex:8; drc:8; synopsys:4)
- **size**: 433832 bytes / 69 msgs / 3 user prompts
- **agent**: deepseek-v4-flash
- **trace_kind**: digital / DDR5 DRVQA xrun 仿真计时对比诊断 (咨询「为什么慢」→ 分析报告 + 建议)
- **archetype**: log-parser / diagnosis-gen（B 档合成：抽可判分计时对比核心做成离线报告器）

## 真实任务流

### User#1 (msg 0)
> `/proj/drvqa/V0/simdir/verilog/ruisongs/array_test/verilog.ddr5.drvqa.1026net/build_file/noregression.x8/xrun.log,分析一下，/proj/drvqa/V0/simdir/verilog/ruisongs/verilog.ddr5.drvqa.1[...]`

给两份 xrun.log，问为什么慢。

### Agent 行为 (msg 1–48)
- 多轮 read_file / write_file(Python analyze*.py) / run_commands 逐行对比两份日志
- 抽取的阶段计时（msg 48 最终表）：

| 阶段 | A (array_test) | B (wenzhuod) |
|---|---|---|
| 启动 | Oct 31 13:18:57 | Oct 28 19:52:44 |
| 编译+elab 结束 | 13:30:09 `total 00:11:12` | 20:03:55 `total 00:11:10` |
| 仿真进程 | 13:30:09 → Nov 1 10:24:06 (~20h54m) | 20:03:55 → 20:34:02 (~30m) |
| 结束 | `$finish(1) at 11 PS` (line 109200) | `$finish(1) at 11 PS` (line 108796) |
| 日志行数 | 109,240 | 108,836 |

- 排除设计/工具差异（同网表 V0_WOWTOP_1C2A_2026Oct26.161302、同 11 PS $finish、同量 dsn~3GB/trn~0.5GB、同量日志行数）
- 结论：瓶颈在环境资源（NFS 85MB/s 窄管道 / 内存争抢 swap 抖动）非设计问题

### User#2 (msg 49)
> 现在导致第一个环境下的所有仿真运行速度特别慢，分析下

### Agent (msg 50–66)
- 采集系统级信息：loadavg 6.6(64 核)、MemTotal ~1006GB、Swap 0 使用、磁盘 99TB/44.9TB free
- 定位运行目录挂载：NFSv3 `10.129.143.208:/HFPROJRUNS_DRVQA` (64KB block, hard timeo=600)
- NFS 实测吞吐 ~52–85 MB/s（接近 1GbE 上限 ~110 MB/s）
- 结论：所有仿真都往同一 NFS 卷写 ~3.5GB Xcelium 快照，多并发互抢窄管道

### User#3 (msg 67)
> 现在怎么解决这个问题

### Agent (msg 68)
- 建议：把 Xcelium 运行目录从 NFS 改到本地 /tmp（632GB 空闲、实测 423 MB/s，快 5–8 倍），用 symlink 引用源码/网表，只回传结果
- 给出 shell 包装脚本骨架

## B 档合成决策

trace 是咨询「为什么慢 + 怎么解决」，agent 给出**分析报告 + 建议**，未生成可复用工具（工程目录只读，analyze*.py 是一次性分析脚本非通用报告器）。

**可判分核心**：两份 xrun.log 的「编译/elab」与「仿真」两阶段计时抽取 + 结构化比较（ratio / slower / same-finish）。这是 trace 里唯一**可纯离线、可结构化判分**的核心——agent 在 msg 48 给出的计时表就是 deliverable 的输出契约。

**合成**：把计时对比核心抽成 `xrun_timing_compare.py`（纯 stdlib），定义清晰的 xrun-timing-log v1 格式（基于真实 xrun 标记：`Start time:` / `xmelab: total` / `xmsim: starting at` / `$finish(n) at time <val> <unit>` / `xmsim: total` / `Job:...is done @<ts>`）。

**A/B 差异**：
- A (visible): 2 份日志，ruisongs+wenzhuod，Oct 日期，$finish 11 PS，跨日 Oct31→Nov1，行数 1240/1180，ratio 41.7x
- B (hidden): 2 份日志，lhtian+ruisongs，Nov 日期，$finish 1500 NS，跨日 Nov28→Nov29，行数 1500/1450，ratio 35.7x
- B 关键差异：**$finish 单位不同 (NS vs PS)** 验单位解析器；**跨日 + 不同用户** 验非写死；**不同 netlist 版本** 验 same_netlist 比较

## 判分设计 (k=15)

check.py 用**独立手动解析器**（split-based，与 reference 的 regex 解析器实现风格不同）从 B 字节重算期望值，避免 reference/check 同 bug 互掩。3 个随机顺序（A=slow/B=fast 与 A=fast/B=slow 互换）验 slower_sim 非写死 "A"。

条件覆盖：zip 合法 / py_compile / 退出码+JSON / 顶层键 / start_ts / compile_sec / sim_sec / wallclock(跨日) / finish 值+单位 / total_lines / user / ratio_sim / slower_sim(3 顺序) / same_finish / same_netlist+compile_delta。

4 negative: naive_empty / print_only(只 stdout 不写 --out) / core_removed(CLI 齐但解析 stub 全 0) / substring_match(用 `in` 匹配，单位写死 PS、用户写死 ruisongs)。全 FAIL。§4.9 (a)(b)(c) 三假提交 FAIL。

## 与既有 case 关系

A.jsonl 已有 SramVcsLogDiagnose / IrunSimDiagnose / SimFailParse（**错误/失败解析**类）、PatStatSpeed（pattern 频率统计）、SimSpeedupMonitor（SV 代码 perf 优化）。本 case 是 **xrun 计时阶段对比**（compile vs sim elapsed、wallclock ratio、$finish 时刻），关注 *性能计时* 非 *错误*，deliverable 与判分条件零重叠。
