# trace_deepreads/1792461218411_hojhc_simspeedup.md

**session**: `1792461218411_hojhc` · user `aocao` @ `hfhds224` (10.129.32.108) · mc=258
**model**: deepseek-v4-flash (cxmt-deepseek-flash) · agent `lead` · 311 msgs · 22.5M input tokens / 296K output
**status**: cancelled (exit_code 0) · 2026-10-20 01:53 → 10-21 07:14 (≈29h)
**cwd**: `/home/aocao` · workspace_root `/home/aocao`
**domain**: verification (DRAM row-hammer sim performance) — shard A
**keywords** (col6): `verilog:409;systemverilog:401;netlist:131;synopsys:61;aether:59;analog:56;transistor:25;cmos:17`

## 用户原话轮（A-faithful 候选）
- **USER#0** (clean 提出需求): `/rundata/decqa/V0/simdir/verilog/aocao/decqa/wave_mirror/cyclic_xyz/RM/200ms_debugwave/.../sim_time=2000/`「在该路径下 我的仿真速度增大了非常非常多，当我sim_time=2000时，几天都跑不完，帮我找出原因并给出解决方案，尽可能极限到缩短时间」
- **USER#37** (指出新增慢代码): 「我并没有dump波形，我新加了下面这部分相关内容才变慢的」+ 贴 `map_addr` / `calc_victim` 代码
- **USER#39**: 「需要实施这些修改，但是先别覆盖原来的代码」← 关键约束：保留原函数
- **USER#204**: 修改后 net_hammer_count_per_ms.rpt 307ms 后最大地址变 10020 持续增大 → 修改有 bug
- **USER#248**: 「不要换成原来到循环版本，这样仿真时间预计又会大幅增加」
- **USER#296**: 修后 159ms 起 17ffb/19ffb 交替为最大 → 仍未收敛

## 根因诊断（assistant A#36 / A#38）
1. **总 ACT 命令 ≈ 3300 万次**：sim_time=2000ms / tREFI=31.2μs → 64102 周期 × 519 ACT/周期。
2. **analog netlist 巨大开销**：rhr_netlist.sv 122,543 primitive / 220,602 reg，每次 ACT 触发整个 chip 事件评估（不可软件绕过）。
3. **🥇 foreach(visited_queue) O(n²)**：饱和后 224 比较 × 33M ≈ 7.4B 比较。
4. **🥈 calc_victim 跨模块层次化引用**（本 case 焦点）：
   - `calc_victim` 在 `for (int i=0;i<7;i++)` 循环内读 `top.RWLbase_addrs[i]`（7 次）+ 1 次 `top.RM`
   - `hammer_update` 一次连调 4 次 calc_victim（plus1/plus2/minus1/minus2）
   - → 每次 ACT ~28 跨模块层次化读 × 33M ACT
   - 事件驱动仿真器对层次化引用无法缓存，每次强制重新求值 → 主因
5. `map_addr` 在 calc_victim 头尾各调一次。

## 修复实现（assistant A#78 / A#99 / A#123）
1. **新增 `calc_victim_fast`**：把 `top.RM` / `top.RWLbase_addrs` 改成函数 input 参数 `local_RM` / `local_RWLbase_addrs[7]`，函数体内**无任何 `top.` 层次化引用**。
2. **`hammer_update` 缓存**：进入时 `local_RM = top.RM; for(ci<7) local_RWLbase_addrs[ci] = top.RWLbase_addrs[ci];`，4 次 `calc_victim_fast(..., local_RM, local_RWLbase_addrs)` → 跨模块读 28→8。
3. **原 `calc_victim` 改 wrapper**：`return calc_victim_fast(log_add, step, is_minus, top.RM, top.RWLbase_addrs);`（向后兼容，外部调用不断 — 响应 USER#39）。
4. **region-index 快路径**：`phys_agg[15:13]` 直接定位 region，跳过 >99% 地址的全 7 轮循环。
5. （另议：visited_queue→visited_set O(1)；降 $display 频率 #1ms→#10ms；多线程 — 在 simulation.pat / rhr_parameter.pkg，本 case 不含。）

## 后段 bug（未纳入本 case 金标准）
- USER#204：calc_victim_fast 首版缺 Part C（RWL2Normal edge, !is_minus）→ 307ms 后 max addr 发散到 10020。
- USER#296：补 Part C 后 159ms 起 17ffb/19ffb 交替为最大 — session 在此 cancelled，未收敛。
- 本 case 取 trace 的**优化诊断 + 实现核心**（calc_victim_fast + 缓存 + wrapper）作为金标准，B 档 synthesized（金标准非 trace 末尾用户接受结果，因 session cancelled）。

## 真实文件
- 原始 monitor: `/rundata/decqa/V0/simdir/verilog/aocao/decqa/wave_mirror/cyclic_xyz/RM/200ms_debugwave/cyclic_xyz_prac_mirror_SLT128_RWL_decqa_burty_num=1_x_num=1_y_num=1_z_num=1031_sim_time=2000/rhr_monitor.sv`
- 改后路径: `.../200ms_debugwave/improve_simspeed/cyclic_xyz_prac_mirror_SLT128_RWL_modify_decqa_..._sim_time=2000/`
- 优化产物（agent 工作副本）: `/home/aocao/opt_rhr_final.sv` / `opt_rhr_fast_fixed.sv` / `build3.py` / `do_fix.py` / `gen_f1.py`

## 合成 case
- **case_id**: `EDA-Eval-DesignFlow-SimSpeedupMonitor-001`
- **track**: B (synthesized) · **level**: L2-static · **domain**: verification
- **交付**: `optimize_monitor.py <in_sv> <out_sv> <report.json>`（结构识别慢 victim-calc 反模式 → 产 *_fast + 缓存 + wrapper + 报告）
- **hidden B**: `rhr_monitor_B.sv`（module rowhammer_watch / compute_target / refresh_push / scramble_addr / chip.RM_en / chip.RWLbases / remap_tab / 18-bit / 8 regions / 5 calls / step {3,4,5} / ignore 18'h3FFFF — 全不同反硬编 A）
- **check**: 16 条断言 a-p · subprocess 真跑 §4.2 · 3 随机 B 变体 §4.5 · 4 negative 全 FAIL · §4.9 三假全 FAIL
- **自验**: ref PASS 16/16 · negative_selftest 4/4 FAIL · jsonl test sha == disk check.py sha
