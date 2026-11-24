# r1139 — wvvpb WvvpbSlowCellLocate-001 cases/B JSON 交付轮（dangling wrap）

**日期**: 2026-11-24  **shard**: B  **轮次**: r1139  **类型**: 1-case 交付轮（JSON wrap，非新 trace）

## 选料与发现

- `trace_ledger.py --shard B next` 取候选；fresh B-spice 池经 r1130-r1138 连续产出后偏薄。
- 从 1124 新 scan（ssh_eda_search_20261124_023802）按 hspice/finesim/spectre 关键词 + mc≥8 过滤，扣台账 1602 已 ledgered slug，得真 fresh 候选。
- 顶层候选多为 virtuoso/drc/verilog 主导（C/A 域）；hspice-dominant 的（3bis4/vo4gm/vdeyi/q3y71/tc4yu 等）全部已 ledgered（cased/parked）。
- peek wvvpb(thomasz@hfhds206/mc95) 发现是真实 B 域 spice_sim 任务，但 `claim` 被 REFUSED：**该 session 早在 2026-11-22 已标 status=case（case_id=EDA-Eval-DesignFlow-WvvpbSlowCellLocate-001）**。

## dangling 发现

- `cases/B/EDA-Eval-DesignFlow-WvvpbSlowCellLocate-001.json` **不存在**，但 `assets/WvvpbSlowCellLocate-001/`（fast.list/slow.list/task_brief.md/prompt.txt + hidden/）与 `reference/WvvpbSlowCellLocate-001/`（check.py/reference_solution.py/reference_submit.zip/negative/×4）均已完整建于 11-22。
- 即：case 在旧 jsonl 工作流下已建并计入台账，但 2026-11-23 运维令改 cases/<shard>/<id>.json 后，该 case 的 JSON 从未补写 → **dangling（assets/reference 有，cases/B JSON 无）= 未交付**。
- 全库类似 dangling 共数十个（pre-jsonl-deletion 遗留）。

## 真实任务（trace 溯源）

- user: thomasz · host: hfhds206(10.129.32.80) · session: `1795153863375_wvvpb.messages.json` · mc: 95 · domain: spice_sim
- thomasz 用 FineSim (PrimeSim V-2023.12-SP2) 跑 DDR4（ddgoa）同一电路两次瞬态仿真，仅把温度从 30°C 改成 45°C，仿真明显变慢（只跑完约 20%）。
- 用 WaveView 从两次 FSDB 波形里抓每个信号的 VC_count（value-change / time-point 计数，近似正比该 cell 耗时），导出 fast.list（常温基准，100% 完成，top-1000 信号）与 slow.list（高温慢跑，~20%，top-1000 信号）。
- 用户原话：「有个仿真只改了温度，就变慢特别多，我抓了一下 time point 数量，想定位到具体是在哪些 cell 话了大量时间。」
- assistant 真实交付：`analyze_list_vc.py`（解析 .list + 统计 min/median/mean/max/CV/max-median 比 + top-1000 占比 + 按 net/block 聚合 + flatness）+ `grep_siout.py`（解析 si.out 日志 PROG 进度/温度/步长）。
- assistant 诊断结论：慢的不是某个 cell，而是**全局时间步坍缩**——slow 的 VC 分布几乎均匀（top-1000 仅占 1.72%，389 个信号在 max 的 80% 以内），温度↑→漏电指数↑→偏置/电荷泵支路变硬→求解器全局限流到极小步长→每个节点每步都打点。

## 本题交付物（程序化抽出的 L1 工具）

- `analyze_slow_cells.py`：纯 Python stdlib，接口 `python analyze_slow_cells.py [fast.list] [slow.list] [report.json]`
- 解析两份 .list（跳过 3 行 OS/Qt preamble + 表头，逐行 tab 拆 idcode/name/VC(pct%)，idcode 须纯数字），以 hierarchy_name 为 key 建 dict。
- 对每个信号算 `vc_diff = slow_vc - fast_vc`；only_in_slow 按 fast_vc=0；only_in_fast 单列。
- 按 vc_diff 降序、hierarchy 字典序升序取前 20 → `top_slow_cells`。
- 输出 report.json 8 字段：fast_signal_count / slow_signal_count / common_count / only_in_slow / only_in_fast / top_slow_cells / max_diff / max_diff_hierarchy。

## 判分设计（19 条断言 a-s，k=19 ≥ 8）

- 隐藏 B：fast_B.list(20 信号) / slow_B.list(21 信号)，与 A（xi_c_top/xi_channel 域）在规模/取值/结构上不同（xi_dram_top/xi_bank0 域）。
- 反硬编码 A'：B 的 VC×2 + 层级名 `_r2` 后缀 → max_diff 300000（非 150000），hierarchy 含 _r2。
- 跨输入护栏：A-only 信号（xi_c_top/xi_channel/vbncore…）不得出现在 B report；B-must 信号（xi_dram_top/xi_bank0/vdd_core…）必须出现。
- §4.9 三假（empty/print_only/core_deleted）跑 B 全 FAIL；B-hardcode stub 跑 A' 必 FAIL。
- 确定性：候选对 B 连跑 3 次 report.json sha256 一致。

## 自验结果

- reference_submit.zip 跑 check.py：**19/19 PASS（True）**。
- 4 个 negative（empty/print_only/core_deleted/hardcode_B）跑 check：**全 FAIL（AssertionError）**。
- test 字段与 check.py 字节级一致（sha256 636c61f28186）。
- cases/B JSON 已落库（21036 bytes）。

## 台账与覆盖

- 台账 wvvpb 早于 11-22 标 case，本轮仅补 cases/B JSON，**covered 不变 = 595/4529 = 13.1%**。
- 本轮为"交付补全"非"新 trace 造题"；dangling case 仍需后续逐个补 JSON（数十个）。
- 🎯 最近20条 20/20=100%（不变，本轮未 pi 实跑）。

## 坑

- ssh piped stdin（`cat f.py | ssh host 'cat > x && python3 x'`）不可加 `</dev/null`（会断 stdin pipe 使远端收到空文件）；仅交互式 ssh 才需 `</dev/null` 防 hang。
- cline 新版 messages.json 是 dict（顶层 keys: version/updated_at/agent/sessionId/messages），非裸 list。
- `.cline/data/sessions/<sid>/` 是目录，内含 `<sid>.json` + `<sid>.messages.json`。
