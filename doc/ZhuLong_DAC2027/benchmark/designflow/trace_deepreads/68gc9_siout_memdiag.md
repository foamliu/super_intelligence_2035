# deepread: 1792031875998_68gc9 — FineSim/PrimeSim si.out 仿真日志内存/时间诊断 (kli)

- **trace**: `1792031875998_68gc9.messages.json` (kli @ hfhds206, mc=424, 213 msgs, 1.90MB)
  - live file: `/home/kli/.cline/data/sessions/1792031875998_68gc9/1792031875998_68gc9.messages.json`
  - tool tally: read_files×71, list_allowed_files×16, run_approved_command×6, run_commands×5, editor×4, greppattern×1
  - agent: lead (cline SpiceAgent-style)
- **domain**: spice_sim / schematic_netlist (log diagnostics). scan kw: schematic:955 netlist:51 hspice.
- **user intent (verbatim, 8 substantive turns)**:
  1. `对比/proj/drvqa/.../MatrixRun_Netlist_Vcap_20261013PM_Fullchip/.../si.out /proj/drvqa/.../MatrixRun_Netlist_Vcap_20261014PM_Fullchip/.../si.out_bk 判断仿真时间变长的原因是什么，为什么memory也变大了`
  2. `能通过读取netlist到方式找到多的signal在哪一部分吗，或者找到多出来的.ic节点在哪里`
  3. `对比 .../MatrixRun_Netlist_Vcap_20261016PM_Fullchip_YupengJ/.../si.out 和 .../MatrixRun_Netlist_Vcap_20261016PM_Fullchip/.../si.out 查找前者为什么memory巨大导致仿真推出`
  4. `两个仿真的网表完全相同，查找具体的memory爆炸原因`
  5. `继续` ×2
  6. `.../si.out Total memory usage: peak= 38698.2 MB ... Peak memory usage for simulation: Peak Virtual Memory = 1383493.4 MB ... 两个memory usage有什么区别，为什么Peak memory usage for simulation会这么大`
  7. `对比 .../si.out 和 si.out_bk，我更新了nodeset，两个输出在memory上有improve吗`
- **real agent tool chain**:
  - phase1 (13PM vs 14PM): list_allowed_files 两个 MatrixRun 目录 → read_files si.out（按行段 :1450-2000 抓 subckt_pt/power block；:2000-EOF 抓 summary）→ run_commands grep 'memory|elapsed|peak|cpu' → 写 analyze_netlist2.py（python-runner）对比 netlist.presim 元件/IC/probe 计数。
  - phase2 (Designer043 OOM): read_files si.out + control 文件 → 抓 `.nodeset`/`.probe v(*)`/`finesim_ignore` 展开 → 定位 OOM 根因（broad ignore 8 条 vs per-tile 93 条 → wildcard 匹配爆炸）。
- **真实金标准（agent 接受的分析结论）**:
  - **13PM (ref, 完成)**: Elapsed 19174s (5.33h), CPU 68586s, Total mem peak 32892 MB (avg 28105), Peak Virtual 36758 MB, Peak Resident 35731.5 MB; subckt_pt id=0 parts=2,656,173 nets=2,543,437; Largest partition 1,869,209 devices / 797,310 nodes; .NODESET 548,887; probed signals 6,717,860; Power Block vssdll m=39599 r=206086 c=4963.
  - **14PM (prob, 完成但更重)**: Elapsed 27280s (7.58h, +42%), CPU 82611s (+20%), Total mem peak 62485 MB (+90%), Peak Virtual 62492, Peak Resident 50616; subckt_pt id=0 parts=5,431,734 nets=4,898,071; Largest partition 13,982,380 devices / 5,983,737 nodes; .NODESET 715,425; probed signals 14,955,764 (+2.23x); Power Block vssdll m=39982 r=208637 c=5017. 根因：netlist 版本不同（config_Vcap_trans vs schematic view）→ 元件翻倍。
  - **Golden007 (完成, 10.95h)**: Total CPU 143393.8s, mem peak 58404 MB, Peak Virtual 68920, Peak Resident 67768.2; .nodeset ~2,195,548; .probe v(*) 18,114,956; finesim_ignore ~93 条 per-tile.
  - **Designer043 (OOM 崩溃)**: .nodeset 12,976,128×2=25,952,256; .probe v(*) 27,942,233; finesim_ignore 8 条 broad; 启动 32min 后 "Free swap ratio '0.0%'" + "Out of Physical Memory" 崩溃；2TB 物理+100GB swap 全耗尽。
  - **10800_SS (38698 vs Peak Virtual 1383493.4 MB)**: 解释 Total memory usage (FineSim 内部记账) vs Peak memory usage for simulation (OS 级 RSS/VMS，含 fork 子进程) 区别。
- **si.out 关键格式行（真实）**:
  - `subckt_pt id=0, num_part=2656173, num_net=2543437`
  - `  Power Block from (vssdll!,vss!) devices(m=39599 r=206086 c=4963)`
  - `  Largest partition has 1869209 devices and 797310 nodes.`
  - `  # signals with .NODESET: 548887`
  - `  # probed signals  : 6717860`
  - `Resource Usage for Transient Analysis(self/total): 65080.2/68562.5 sec (cpu), 16305.0/19148.0 sec (elapsed), 93.5/28382.0 MB`
  - `Total CPU time: 68586.2 seconds (19.05 hours), 4 threads`
  - `Total memory usage: peak= 32892.1 MB, avg= 28105.0 MB`
  - `Peak memory usage for simulation: Peak Virtual Memory = 36758.0 MB, Peak Resident Memory = 35731.5 MB`
  - `Total elapsed time: 19174.0 seconds (5.33 hours)`
  - OOM: `WARNING! Free swap ratio '0.0%'  Swap已耗尽` / `WARNING! Out of Physical Memory  物理内存耗尽`
- **合成本任务（B档, case `EDA-Eval-DesignFlow-SiOutDiag-001`）**:
  - 聚焦「**对比两份 si.out，结构化诊断内存/时间/电路规模差异 + OOM 检测**」——最可复现、最硬核的子技能。自包含合成 si.out（格式忠于真实 PrimeSim，数字从真实 13PM/14PM/Designer043 派生但缩放），无 foundry-model 依赖，可在 .75 复现。
  - 候选提交 `siout_diag.py`：读 `ref.out` + `prob.out` → 解析（elapsed/cpu/total-mem/virtual/resident/subckt0 parts+nets/largest partition dev+nodes/.NODESET/probed signals/power-block m/r/c by net/OOM/swap/completed）→ 写 JSON（含 ref/prob/comparison）。
  - 关键判分点：工程后缀无关（si.out 用 plain MB/sec）；Total memory(peak=) vs Peak Virtual/Resident 三字段不可混淆；self/total CPU/elapsed 取专用行（Total CPU time / Total elapsed time）；OOM 检测需抓 "Out of Physical Memory" + "Free swap ratio '0.0%'"；completed 由 "Total elapsed time" 行存在性判定；cross-input B（双对 hidden：B1 完成-更重 vs B2 OOM-崩溃 + 数字/power-block 全异）杀 A 硬编码与 print-expected stub。
- **pitfalls（合成时需规避）**:
  1. si.out 行段读取须容忍行号前缀 `  N | ...`（read_files 工具加的）——但本 case 给候选的是**裸 si.out 文件**（无行号前缀），候选直接 open() 读。check.py 的 GT 解析器也对裸文件。
  2. OOM 文件**不含** "Total elapsed time" 行（崩溃前未打印）——候选必须用该行缺失判定 completed=False，不能默认 True。
  3. power-block net 名含 `!`（全局网），候选须 strip 或保留原样一致即可；m/r/c 三个计数须全抓（部分 power block 只有 r 或 r+c）。
  4. cross-input guard：hidden 含 B1(ref 完成 / prob 完成但更重) + B2(ref 完成 / prob OOM 崩溃)，两对数字完全不同；check.py 跑候选于两对，要求输出均正确且互异——杀硬编码与 print-expected。
