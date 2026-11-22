# r11v3 — willz @ hfeahpc501 — vvdd2c .sp stimulus rewrite + finesim runner optimize + latch tpd deck gen

**trace**: 1795065278472_r11v3 / willz / hfeahpc501 / mc=19 / 79 msgs / 312KB
**keywords**: cmos:70;netlist:67;hspice:44;schematic:22;analog:7;binary:3;virtuoso:1
**domain**: spice_sim (B shard) — FineSim/HSPICE testbench stimulus + batch runner + latch sampler tpd sweep
**scan**: ssh_eda_search_20261122_172249/summary.tsv (fresh B-spice pool, cross-4-shard-ledger 全 NONE ✓, r1065 规范化 diff 30 fresh 之一)

## 真实工作场景
sim_result_261112 目录下多个 FineSim 测试台子目录（23_Sense_V / 00_latCAsamp0New_tb_pst 等），每个子目录含多 corner 子文件夹（ff130_rcx / ss1m85_rcx / tt_rcx ...），每个 corner 一个 `.sp` 测试台 + `.spf` 子电路。

## 3 个 user 任务

### Task 1 (U0, msg 0) — vvdd2c stimulus 批量替换 ✅ 选作 reframe
**U0 原话**：「/proj/ddgot/V0/workdir/willz/simulation/sim_result_261112/23_Sense_V 将所有sp中的 vvdd2c vdd2c! 0 pvcc 更换成 vvdd2c vdd2c! 0 1」
- 真实路径映射：23_Sense_V → /rundata/ddgot/V0/simdir/finesim/workdir/willz/simulation/sim_result_261112/23_Sense_V
- 含 2 个 top 子目录 f6P4G / f7P2G，各 6 个 corner 子目录（ff130_rcx/ff1m130_rcx/ff1m85_rcx/ss130_rcx/ss1m130_rcx/ss1m85_rcx/tt_rcx/tt130_rcx），每个 corner 一个 rcv_ca_top_sim.sp（共 12 个 .sp）
- assistant: list_allowed_files 探目录 → 读一个 .sp 确认第 67 行 = `vvdd2c vdd2c! 0 pvcc` → 写 replace_vvdd2c.py 递归 find *.sp 精确行替换 → run: 12 files each 1 occurrence REPLACED → verify_vvdd2c.py 复核 old=0 new=1 全 12 → 确认 .spf(CaRcvCoreM6.spf ×2) 不含该模式无需改 → cleanup 临时脚本
- **reframe**: `vvdd2c_rewrite.py <spec.json>`，spec={root_dir, file_glob, old_pattern, new_pattern, report_path}，递归 walk root_dir 按 glob 过滤文件、逐文件精确行替换 old→new、回写、emit JSON report{spec, files_scanned, files_modified, replacements_per_file, total_replacements, unmodified_files}。L1 纯 Python。

### Task 2 (U27, msg 27) — run_all_finesim.csh 输出目录扁平化
「f7P2G/run_all_finesim.csh 这个脚本优化下，只需要在sp文件夹的路径下生成新的文件保存仿真结果，不要多层文件夹」
- 旧：每个 .sp 输出到 `$dir/re_$name/`（镜像子目录多层）；新：`$dir/re_$base/`（sp 所在文件夹下单层）
- assistant: read csh → 用 python-runner 重写循环（editor 对 /rundata 写受限）→ `${rel//\//_}` 斜杠转下划线 → bash -n + per-.sp 输出目录模拟验证 → cleanup

### Task 3 (U52-U63, msg 52-63) — latch sampler tpd sweep deck 生成
U52 给参考 .sp 片段（`vclk xisamp0.clkri 0 pulse 0 pvintcore 'td+tpd' ...` + `.tran 10p 'td+2*UI' sweep tpd` + meas 定 `'td+20*UI'`）；U63 精炼：「现在只需要一个hold0的sp，但是要用参考的代码代替原先的代码，记住保留原先的net名字，先生成一个参考的」
- 00_latCAsamp0New_tb_pst 下 14 个 LatSamp_hold{0,1}_{ff1,ff2,ss1,ss2,ssm1,ssm2,裸}.sp，旧扫描 td，参考扫描 tpd
- assistant: 读 14 文件摸角件差异（pvcc/寄生电容 cthin/cthick/cgatein/capo/.temp/sweep 范围）→ 分析旧vs参考扫描差异 → U63 收窄到只生成 1 个 hold0 → 写 gen_hold0.py 读原 LatSamp_hold0.sp，仅替换「刺激/扫描/测量」三处，保留 netlist include/电源/pin/.probe/.OP/.temp，net 名映射（xisamp0.clkri→ClkRi, pvintcore→pvcc）→ 输出到新文件夹 00_latCAsamp0New_tb_pst_tpd/LatSamp_hold0.sp → 验证三处替换正确 → cleanup

## 选 Task 1 理由
- 自含、闭环、交付物清晰（脚本+报告）、可参数化 anti-hardcode
- Task 2 是 csh 改写（check 难以真跑 finesim 验证输出目录，退化到文本断言 → 失牙风险）
- Task 3 需保复杂 netlist + 3 处替换，spec 复杂易错且 check 易退化到子串匹配
- Task 1 是真跑候选（subprocess 跑脚本改文件 + 复核磁盘状态 = 结构化断言非文本相似），符合 §4.2

## case 设计（k=12 a-l）
- **A**: willz 真实结构采样：23_Sense_V/{f6P4G,f7P2G}/<6 corner>/rcv_ca_top_sim.sp = 12 .sp 全含 `vvdd2c vdd2c! 0 pvcc`；2 .spf 不含模式；spec_A old=vvdd2c...pvcc new=vvdd2c...0 1
- **hidden B**（五重 anti-hardcode）：①树结构 3 top × 4 corner = 12 .sp（异于 A 2×6）②corner 名 DDR PVT 风格 tt25/tt98/ss25/ss98 ③supply net 换 vddq 系 `vvddq vddq! 0 pvddq`→`vvddq vddq! 0 1.2` ④fixed 值 1.2（异 A 的 1）⑤3 .spf 其中 1 个**含** old_pattern（测 glob `*.sp` 严格过滤，即便 .spf 含模式也不改）+ 1 .sp **不含**模式（测 0-replacement 上报）
- **check 12 条**: a(zip+compile+size) b(exit0+report非空) c(顶层键⊇6) d(scanned==12) e(modified==11) f(total==11) g(改后.sp new在场old缺席) h(未改.sp 两者均缺席原样) i(.spf 全未改含含模式那个仍含模式 — 核心齿反 no-glob-filter) j(anti-hardcode report.spec==B spec) k(per-file==1) l(3-seed sha256一致)
