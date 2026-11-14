# Deepread: 12h9v — dsgao@hfhds201 — FineSim OOM 诊断

**session**: `1794641146841_12h9v.messages.json` (565KB, 46 msgs, 25 user / 21 assistant)
**user**: dsgao (hfdes group), mc=60
**keywords**: drc:868;netlist:596;aether:234;mixed-signal:229;schematic:49;floorplan:22;hspice:21;virtuoso:18
**tools**: 132 netlist, 28 schematic, 18 virtuoso, 12 spectre, 11 hspice, 7 pyAether, 6 cellview, 1 calibre
**spice_ratio**: 21/(868+596+...) ≈ 0.010 — 低, 但首个 user msg 是真实 FineSim OOM 仿真日志

## 真实任务（首条 user 原话）
用户粘贴了一段 FineSim/PrimeSim 仿真日志，包含：
- `Resource Usage for Matrix Building(self/total): 175.4/21487.4 sec (cpu), 177.0/19909.0 sec (elapsed), 14331.9/211079.8 MB`
- `WARNING! primesim_monitor cannot popen when getting processor number: Cannot allocate memory`
- 2 次 `Out of Physical Memory happened on <timestamp> (Total Physical RAM: 791207264 KB; Free: <N> KB)` 警告
- 2 次 `Disk swapping disappeared on <timestamp>` 恢复
- `Starting DC Initialization ...`
- 最后问「仿真这样怎么解决」

## assistant 行为
1. 调 `skills aether-tool-qa` 查 OOM/disk swapping/Matrix Building 知识库
2. `search_codebase` 检索 aether_tool_qa.md 交流群问答
3. `read_files` 读 reference 文档
4. 多次 `run_commands`/`run_approved_command` 被拒（raw shell disabled）
5. assistant 基于知识库给出一般性建议（终止其他内存作业 / 换更大内存机器 / 减小规模）

## 合成决策
- **archetype**: spice_sim 错误诊断（新 archetype — 不是 subckt 缺失，而是 OOM/内存/磁盘交换资源诊断）
- **A 档 trace-faithful**: 保留真实 OOM 日志格式（WARNING + 时间戳 + RAM 值 + Disk swapping disappeared 模式）
- **泛化**: 写 `analyze.py` 解析 FineSim OOM 日志 → `diag_report.json`（结构化：simulator/run_dir/matrix_building/popen_failures/oom_events/disk_swapping_periods/simulation_phases/summary）
- **hidden B**: 3 OOM events (vs A=2), 2 popen (vs A=1), 1 unresolved swap (vs A=0), severity critical (vs A=high), 全异 timestamps/memory/run_dir
- **cross-input guard**: A vs B 必须在 oom_count/popen_count/has_unresolved_swap/severity/mem_self_mb/run_dir 全不同
- **判分**: 12 断言 a-l，含 cross-input guard (l)

## 覆盖
- ledger_B: 12h9v mark case (467/1510)
- domain: spice_sim (新 archetype: OOM 资源诊断)
