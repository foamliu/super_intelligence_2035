# Deepread — 1795518550460_3uze0 (PWL 波形时序参数提取: 50% crossing / tr-tf / dr-df)

- **session**: 1795518550460_3uze0
- **user/host**: guangmingz / hfeg0pkn004
- **mc=176**, schematic/netlist/verilog/analog/synopsys/waveview (D-domain, FRESH, NEW user)
- **size**: 1,304,464 bytes (1.3MB), 343 msgs (185 user / 158 assistant)
- **tools**: run_approved_command 82, editor 39, read_files 26, list_allowed_files 5, ask_question 5
- **key files** (final versions fetched from hfeg0pkn004):
  - `/home/guangmingz/.cline/skills/vam-agent-demo/scripts/extract_pwl_drdf.py` (337 lines, 26 reads) — 50% crossing delay extractor (ref vs ideal)
  - `/home/guangmingz/.cline/skills/vam-agent-demo/scripts/extract_pwl_trtf.py` (323 lines, 7 reads) — tr/tf (10%-90%) extractor
  - `agent_generated_scripts/cosim_IO_DqIbSADoubleTail_model.va` (8 edits) — Verilog-A behavioral model of DQ sense-amp (double-tail)
  - `agent_generated_scripts/check_state.py` / `update_timing.py` / `analyze_ldata*.py` / `validate_ldata_edges.py` — analysis helpers

## 用户真实意图（逐条，从 `<user_input>` 块）

用户(guangmingz)使用自研 "vam-agent" skill（Verilog-AMS 建模智能体）对 IO cell `IO_DqIbSADoubleTail`（DQ sense-amp double-tail）做行为建模。核心流程：

1. 提供 fullchip 仿真路径 + cell DSIM block cosim 仿真环境路径
2. 从 cosim 仿真输出抽取 PWL 波形（FSDB→PWL 经 WaveView/wv + bsub LSF 队列）
3. 分析输入 PWL 与输出 PWL 的时序/逻辑关系
4. 构建/精化 Verilog-A 行为模型 `.va` + 时序参数 + 跑 cosim 验证

关键用户捕获的** latch/采样逻辑**（编码为断言的牙）：
- DqIb > Vref → Ldata=1；DqIb < Vref → LdataN=0
- DqSamp 上升沿采样
- SampEnN=0 → LDFEdata = ¬LdataN，LDFEdataN = ¬Ldata

## 两个核心脚本的精确语义（判分要点来源）

### extract_pwl_drdf.py（ref vs ideal 50% crossing 延时）
- `load_pwl(file, signal)`: 解析 PWL 块。头行 `v<sig> <sig> 0 pwl(`（大小写不敏感，末 token 去 `()`/`（）` 后 == `pwl`）。数据行 `+` 续行（剥 `+`），`)`/`）` 终止。返回 (t[], v[]) np.array；找不到返回 (None,None)。
- `estimate_levels_hist(v, bins=200)`: 直方图取峰值电平。**关键**：bin 中心数组从中点 `mid=len//2` 切两半，lo=前半 argmax 中心，hi=后半 argmax 中心（**非**全局 min/max，抗过冲）。
- `find_edges(v, vmin, vmax, hyst_frac=0.15)`: 滞回状态机找边沿。amp=vmax−vmin；v_lo=vmin+hyst*amp（靠近低电平）；v_hi=vmax−hyst*amp（靠近高电平）；vmid=中点。初始 state = v[0]>=vmid ? 'high':'low'。low→高穿 v_hi=rise 边沿(start,end)；high→低穿 v_lo=fall 边沿。**滞回带防半山腰噪声误判**。
- `cross_in_segment(t,v,vth,i0,i1,rising)`: 线性插值找首次穿越 vth 时刻。rising: tv[k-1]<vth<=tv[k]；falling: tv[k-1]>vth>=tv[k]。t0+(vth−v0)/(v1−v0)*(t1−t0)。
- `extract_50_times`: 对每个边沿，向前回退到稳定电平、向后扩展到过 v50，调 cross_in_segment 求 50% 穿越时刻。返回 rise_50[], fall_50[]。
- `local_tolerance(times, idx, period_frac, default_tol)`: 取 idx 前后 ±3 点的 diff 中位 * period_frac（局部周期自适应容差）。
- `pair_by_time_window(t_ref, t_meas, ...)`: **贪心配对**——所有 |tm−tr|<=tol_i 的 (dt,i,j) 候选，按 dt 升序排序，依次取未用的 ref/meas 配对（**非**先到先配）。delay = t_ref[i] − t_meas[j]（正值=实测滞后=传输延时）。返回 delays + 未匹配 ref 数 + 未匹配 meas 数。
- `report`: n/median/mean/std/min/max，**一致性警告**：med>0 且 (mean/med>1.1 或 std/med>0.2)。
- 可选过滤：`--skip_first N`（跳前 N 边沿）、`--t_start`/`--t_end`（时间窗）、`--diag`（打印 dr/df 最大最小各 1 个配对详情）。

### extract_pwl_trtf.py（单波形 tr/tf 10%-90%）
- `load_pwl` 同上。
- `estimate_levels(v, mode, pct)`: 三模式。extremum=min/max；robust=分位(pct, 100−pct)；hist=同上直方图峰值。
- `find_edges` 同上（含 debug）。
- `edge_time(t,v,kind,i_start,i_end,v10,v90)`: **过冲感知**段扩展。rise: i_start 回退到 v<=v10；j 从 i_end 扩到 v>=v90，**但 j>i_end 且 v[j+1]<v[j]（过峰）即停**。t10/t90 = cross_in_segment。tr=|t90−t10|。fall 对称。
- v10=vmin+0.1*amp, v90=vmin+0.9*amp。
- `report` 同上 + `--diag`（tr/tf 最小最大各 3 个边沿详情）。

## case 合成 plan（task_id = PwlTimingExtractProduce-001，LIVE-NA judge=[L0,L1]）

**reframe**：cosim/FSDB/WaveView/wv/bsub 工具链不在 eval 沙盒 ⇒ reframe 为 spec-JSON 驱动纯 Python **PWL 波形时序参数提取器** `pwl_timing_extract.py(spec)->report.json`，纯文本/数值判分，无真实 EDA 二进制依赖，判 LIVE-NA。

**spec schema**（A visible / B hidden token-structurally 不相交）：
```
{
  "mode": "drdf" | "trtf",
  "ref_pwl": "<多行 PWL 文本>",          # drdf 模式：实测波形
  "ideal_pwl": "<多行 PWL 文本>",         # drdf 模式：理想方波
  "pwl": "<多行 PWL 文本>",               # trtf 模式：单波形
  "ref_signal": "...", "ideal_signal": "...", "signal": "...",
  "ref_vmin/vmax": null|float, "ideal_vmin/vmax": null|float, "vmin/vmax": null|float,
  "hyst": 0.15, "period_frac": 0.5,
  "skip_first": 0, "t_start": null, "t_end": null,
  "level_mode": "hist"|"extremum"|"robust"
}
```
PWL 文本格式（模拟真实 wv dump）：
```
vDqIb DqIb 0 pwl(
+ 0.000e-12 0.0
+ 1.000e-09 0.0
+ 1.050e-09 1.2
...
)
vLdata Ldata 0 pwl(
...
)
```

**report.json 结构**：
- drdf 模式：`{ref:{n_points,vmin,vmax,n_rise,n_fall,rise_50[],fall_50[]}, ideal:{...}, pairs:{dr{n,median,mean,std,min,max,values[]}, df{...}, unmatched_ref_rise, unmatched_ref_fall, unmatched_ideal_rise, unmatched_ideal_fall}, warnings[]}`
- trtf 模式：`{signal,n_points,level_src,vmin,vmax,v10,v90,n_rise,n_fall,tr{n,median,mean,std,min,max,values[]}, tf{...}, skipped_rise, skipped_fall, warnings[]}`

**reference `pwl_timing_extract_ref.py`**：spec 驱动通用实现（独立代码路径：load_pwl + estimate_levels_hist + find_edges + cross_in_segment + extract_50/edge_time + greedy pair + report）。**与 check.py 的 gold 复算用不同实现路径**（如 gold 用简单阈值穿越无滞回、或 gold 用 scipy-free 直接遍历）。

**check.py ~16-18 conds（a-?，k_check=k_rationale）**：
1. a: zip 含 pwl_timing_extract.py
2. b: py_compile
3. c: A 运行 valid=True errors 空
4. d: A drdf 模式 ref vmin/vmax 匹配（hist 峰值估计，**非**全局 min/max，因有过冲点）
5. e: A ref n_rise/n_fall 匹配（滞回带过滤半山腰噪声）
6. f: A ref rise_50/fall_50 首末时刻匹配（线性插值 50% 穿越）
7. g: A dr 配对数 + unmatched 计数匹配（贪心最小 dt，**非**先到先配）
8. h: A dr/df median/mean 匹配（delay = ref−ideal）
9. i: A trtf 模式 vmin/vmax 匹配（指定 level_mode）
10. j: A tr/tf values 匹配（10-90 线性插值，**过冲感知**段扩展 stop at peak）
11. k: A warnings 触发（构造 mean/med>1.1 的不一致波形）
12. l: A skip_first/t_window 过滤生效
13. m: malformed spec（缺 signal / 找不到 PWL 块）→ valid=False errors 非空
14. n: hidden-B 运行（不同 signal/波形/参数）结果与独立 gold 匹配（**反硬编码**：A-only token 不出现在候选）
15. o: anti-hardcode tokenize 剥注释/字符串/docstring 源码扫描无 A-only 字面 token（信号名/数值）
16. p: 确定性 3-run report.json md5 一致
17. q: hidden-B token-structurally 不相交（不同信号名 DqIb/Ldata vs ClkIn/Qout，不同电压/时间值）
18. r: level_mode robust/extremus 与 hist 结果差异（证明非硬编码单模式）

**negatives（6，全 FAIL distinct first-fails）**：
- empty → c
- print_only（打印固定 report.json 串）→ d/e（数值不匹配）
- core_deleted（只解析 header 不算边沿/延时）→ e/f
- hardcode_a（A 的数值硬编码）→ n（B 全错）
- global_minmax（用全局 min/max 代 hist 峰值）→ d（过冲点致 vmin/vmax 偏）
- first_come_pair（先到先配代贪心最小 dt）→ g（配对数/延时错）

**§4.9 trio** {empty, print_only, core_deleted} = {c, d/e, e/f} 3-distinct

**check() 返回 {'pass':bool,'detail':str} 严格契约**（非 tuple，避 r1661 隐患）

**自验**：REF PASS 16-18/18；negative_selftest 6-distinct；SKIP_RUN=1 eval/run_one.sh 框架接受；test sha 3-way sync (disk==JSON test==metadata)；judge_layers=[L0,L1] k_check only-add。

**trace_source**: user=guangmingz, host=hfeg0pkn004, session_file=1795518550460_3uze0.messages.json, match_count=176, real_task_summary="从 cosim 仿真 PWL 波形提取 50% crossing 延时(dr/df)与 tr/tf(10-90) 时序参数用于 IO cell Verilog-A 行为建模"

下轮 r1668 按 plan 合成 PwlTimingExtractProduce-001。
