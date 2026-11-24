# 6c0ct — FarMeg coupling comparison (waveform / produce)

- trace: `1795398722406_6c0ct.messages.json`, user dsgao @ 10.129.2.10, mc=123, 187 msgs / 2 MB
- domain: waveform (FSDB .tbl parse + coupling glitch metrics)
- deliverables (scp'd from .75 → eda_flow workdir): `gen_csv.py` (5835B, `from analyze import parse_table`), `coupling_comparison.csv` (3326B, 4 sections), `coupling_report.txt` (3319B), `out_old.tbl` / `out_new.tbl`
- case: `EDA-Eval-DesignFlow-FarMegCouplingCompare-001` (shard D, k_check=14)

## real task
对比两份 FSDB 仿真 (old=full_testbench_far_spicehd_1111_103938 vs new=full_testbench_far_spicehd_1119_190152, 修改电路后)，分析 aggressor `ra543_far<6>` / `ra210_far<7>` 翻转时对其他 quiet 信号的耦合串扰影响。交付 CSV + report + `gen_csv.py`。

## kernel (offline-ified)
纯解析 + 数值层，无 EDA 工具依赖：
1. `.tbl` 解析：首行 `TIME v(s0) v(s1) ...`，信号名从 `v(...)` 提取；数据行 `<time> <v0> <v1> ...`，工程后缀 m/u/n/p/f/k/meg/g → 浮点；`nan`/空 → None。
2. aggressor 边沿：threshold 穿越 → [(t, level)]，取第一条 rise / 第一条 fall。
3. 10→90% slew：首次到达 slew_lo 的 t_lo 与首次到达 slew_hi 的 t_hi，slew = t_hi - t_lo（需 t_hi>t_lo）。
4. per-victim 峰值：max(peak pos) / min(peak neg)，None 跳过。
5. 4-section CSV：SECTION1 sim info / SECTION2 aggressor timing(ns) / SECTION3 per-victim glitch peaks(mV) / SECTION4 digitized levels(V)。

## A / B 设计（结构性不相交）
- A (可见, 5 sigs): aggressor `aggr_a` + victims `vic_a0..vic_a2` / `ref_a`；t_rise=12ns / t_fall=30ns；时间 0..60ns。
- B (隐藏, 6 sigs): aggressor `drv_x` + victims `rcv_y0..rcv_y3` / `sense_z`；t_rise=18.6ns / t_fall=45.7ns (old) vs 16.44/43.1 (new)；slew 1.0/0.96 ns；NEW 串扰峰值较 OLD 降 ~22%。
- 信号名、数量、时间范围、翻转时刻、串扰幅度全部不同；B 不是 A 的改名。
- 精细时间网格（aggressor 翻转附近 0.2ns 步长，其余 2ns 粗步）是 slew10-90 非零测量的关键——均匀粗网格会让 10%/90% crossing 落在同一 step 内 → slew=0。

## manifest_B.json
`{aggressor:"drv_x", threshold:1.7, slew_lo:0.5, slew_hi:3.0, victims:[[rcv_y0..3,sense_z,"quiet victim"]], expected:{old/new:{rise_first,fall_first,slew1090,glitches{sig:[pos,neg]}}}, signals:[...]}`

## check.py (14 断言)
A0 zip 存在可解压 / A1 gen_csv.py 在根 / A2 py_compile(自包含) / A3 在 B 上运行 exit0 + 产出 out.csv / A4 SECTION1 aggressor+threshold 来自 B / A5 SECTION2 rise+fall+slew OLD+NEW 匹配独立重算(6 sub) / A6 SECTION3 per-victim pos+neg peaks 匹配 / A7 SECTION4 V_min/max 匹配 / A8 victim 集合 == B manifest / A9 3-seed 随机抽 B 90% 行子集解析自洽。

## negative
- `print_only.py`：只 print 不写 CSV → A3 FAIL
- `core_deleted.py`：parse_table 返回空，CSV 结构对但全 0 → A5/A6/A7 FAIL

## selftest
ref solution PASS / 2 negative FAIL / selftest OK

## 备注
- 原 trace `gen_csv.py` 依赖 `from analyze import parse_table`（外部模块）；reference solution 内联 parse_table 自包含，SUT 必须同样自包含。
- check.py SECTION4 列索引修正：solution 输出 6 列 `[name,"V",OLD_min,OLD_max,NEW_min,NEW_max]`，check 初版误用 r[3..6]，已改 r[2..5]。
