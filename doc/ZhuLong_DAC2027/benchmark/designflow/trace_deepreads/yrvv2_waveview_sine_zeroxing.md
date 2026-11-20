# Deepread · yrvv2 · WaveView tcl 正弦/余弦波 + 过零点/频率/峰值分析

> session: `1793841389903_yrvv2` · user: `e0023936` · host: `10.129.32.75` · mc=25
> domain: **waveform** (WaveView ACE `sx_*` Tcl API)
> ledger: claimed 2026-11-11 11:09 (shard D)
> 深读轮次: r510（P-001 讨论占用预算 → 本轮 deepread，合成留 r511，DEBT:1）

## 1. 用户原话（逐字，仅掩码 key/token）

8 轮 user turn 中仅 4 轮有 text content（其余为 tool_result 空 carrier）：

- **U#0 / U#31**（重复）：`使用tcl代码，帮我画一个正弦波并计算过零点、估算频率与峰值。`
- **U#32**：`使用tcl代码，帮我画一个余弦波并计算过零点、估算频率与峰值。`
- **U#34**：`查询   sx_jump_to_x tcl语言的使用情况`

**主任务（A 档候选）= U#0**：用 Tcl 画正弦波 + 算过零点 + 估频率 + 峰值。
**变体任务 = U#32**：余弦波版本（同结构，sin→cos）。
**旁支 = U#34**：sx_jump_to_x 用法查询（Q&A，非产，不进 case）。

## 2. assistant 工具链（27 条 assistant msg）

RAG 检索 WaveView ACE API → 沙盒（SandBox_MCP_Server__run_code）逐个实测 sx_* 签名 →
编写 proc → run_commands 实跑验证 → 清理临时文件 → 交付。

关键 API 实测确认：
- `sx_open_sim_file_write` / `sx_open_sim_file_read` — 建/读 WDF 文件
- `sx_create_signal` + `sx_append_data` — 逐点写入 `A·sin(2πf·t)` / `A·cos(2πf·t)`
- `sx_save_signal $file $sig` — 落盘
- `sx_find_wave_in_file` / `sx_wave_to_list` — 读回全部 y 值（均匀采样 x）
- `sx_new_wv` + `sx_display_wave $win $wv` — 新建窗口并绘制
- `sx_scan_data_points` + `sx_scan_next` + `sx_x_value`/`sx_y_value` — 数据点扫描（cursor 遍历不理想，改用 wave_to_list）
- `sx_jump_to_x $scan $x` — 跳到指定 x（线性插值），`sx_x_value`/`sx_y_value` 取值

## 3. 金标准（用户实际接受的结果）

assistant 在沙盒中**实测验证**后交付 proc，正弦波（amp=1, freq=1Hz, 2s, 1001 点）：

```
peak=1  peak_x=0.25  num_zero_crossings=4  rising_crossings={0.0 1.0}  period=1.0  est_freq=1.0
```

余弦波（同参数，sin→cos）：
```
peak=1  peak_x=0.0  num_zero_crossings=4  rising_crossings={0.75 1.75}  period=1.0  est_freq=1.0
```

**机制**（可独立 oracle 复算）：
- 信号：`y(t) = A·trig(2πf·t + φ)`，trig∈{sin,cos}，t∈[0,dur]，N 点均匀采样
- peak = max|y| = A；peak_x = 满足 trig(2πf·t)=±1 的首个 t（sin→t=1/(4f)，cos→t=0）
- 过零点：y 符号变化点；rising = 负→正穿越；num_zero_crossings = 总数（含 rising+falling）
- period = 相邻 rising 过零间距 = 1/f
- est_freq = 1/period = f

## 4. 合成设计（B-grade synthesized，下一轮 r511 合成）

**case_id**：`EDA-Eval-DesignFlow-WaveSineZeroXing-001`（waveform 域，B-grade synthesized，L2，k=8–10）

**A（可见输入）**：sine，amp=1，freq=1Hz，dur=2s，N=1001，phase=0
- `inputs_A/params.json` + `example_output/report_A.json`（上面的金标准）
- `task_brief.md`：交付接口 ≤3 行（`wave_analyze.py --amp --freq --dur --phase --kind --out report.json` + `wave_analyze.tcl`）

**B（隐藏输入，植入 hidden/）**：cosine，amp=2，freq=3Hz，dur=1s，N=1501，phase=π/4
- 与 A 在 kind/amp/freq/dur/N/phase 全部不同（不是换文件名）
- B 的 oracle（独立 python 复算）：
  - peak=2.0；peak_x≈0（cos+phase=π/4 首个峰值偏移）
  - 过零点数 = 2·f·dur = 6（cos 在 1s 内 3Hz → 6 个过零）
  - rising_crossings ≈ {周期内 cos 上升过零点}
  - period=1/3≈0.3333；est_freq=3.0

**SUT 交付**：`submit.zip` 含
1. `wave_analyze.py`（参数化：--amp/--freq/--dur/--phase/--kind sine|cosine/--N/--out，纯 stdlib 禁 numpy/scipy/subprocess/socket，输出 JSON{kind,amp,freq,dur,phase,N,peak,peak_x,num_zero_crossings,rising_crossings,falling_crossings,period,est_freq}）
2. `wave_analyze.tcl`（WaveView ACE sx_* proc，参数化 $amp/$freq/$dur/$N/$kind，结构正确：sx_open_sim_file_write→sx_create_signal→sx_append_data→sx_save_signal→sx_open_sim_file_read→sx_wave_to_list→计算）
3. `report_B.json`（B 参数跑出的结果）

**check.py 8 条件草案**（a–h，每条独立可 FAIL）：
- a: zip 含 3 文件齐全 + 无禁 import（numpy/scipy/subprocess/socket/urllib/eval/exec）+ 无 ref/hidden/B 字面量（amp=2/freq=3/cosine/phase=0.7854）
- b: wave_analyze.py py_compile 通过
- c: 子进程真跑 SUT 的 `wave_analyze.py --amp 2 --freq 3 --dur 1 --phase 0.7853981633974483 --kind cosine --N 1501 --out /tmp/rB.json` 退出 0 + JSON parse + 顶层 keys 齐全
- d: peak == oracle（2.0，容差 1e-9）
- e: peak_x == oracle（cos(2π·3·t+π/4) 首个 |y|=2 的 t，容差 1e-6）
- f: num_zero_crossings == oracle（6，符号变化计数）
- g: rising_crossings 集合 == oracle（容差 1e-6，个数 + 值）
- h: period == oracle（1/3，容差 1e-9）+ est_freq == oracle（3.0，容差 1e-9）
- （可选 i: 反硬编码——跑 A 参数得 A 的 oracle，A/B 结果不同；j: tcl 结构 regex 命中 sx_create_signal/sx_append_data/sx_save_signal/sx_wave_to_list；k: 3-seed sha256 稳定——若取 k=10 则补 i/j/k）

**k_check 目标 = 8（硬闸门下限）**；`test_rationale` 写 `8 条断言：①zip…②py_compile…③B 真跑退出0+JSON…④peak…⑤peak_x…⑥num_zero_crossings…⑦rising_crossings…⑧period+est_freq…`，k_rationale=k_check=8。

**negative/**：empty_shell（→ a/c 全 FAIL）、print_only（report.json 写死 B 期望串 → a/d/e/h FAIL，反硬编码 i 若有则 FAIL）、core_removed（peak 恒返回 0 → d/e FAIL）。`negative_selftest.py` 一次跑完全 FAIL。

**§4.9 三假**：(a) 空 zip (b) 只 print 期望串 (c) ref 删 peak 计算 → 全 FAIL/REJECTED。

## 5. 维度正交（vs 既有 D waveform case）

既有 waveform case（待查 jsonl_D）：本 case = WaveView tcl 合成波形 + 过零点/频率/峰值分析，
机制是「参数化波形生成 + 符号变化过零检测 + 周期估计」，与既有（若涉及真实 .fsm/.wdb
波形文件读取/测量）产物/机制不同。r511 合成前先 `grep waveform EDA-Eval-DesignFlow_D.jsonl`
确认非重复。

## 6. 下一轮（r511）计划

1. 复用本深读笔记 → 合成 WaveSineZeroXing-001（无需重读 trace）
2. 写 assets/inputs_A + hidden/inputs_B + reference/{wave_analyze.py,check.py} + negative/
3. 自验：ref PASS 8/8 + negative_selftest 全 FAIL + §4.9 三假全 FAIL
4. 过断言闸门（k_rationale=k_check=8）→ 追加 EDA-Eval-DesignFlow_D.jsonl
5. `mark --status case --case-id EDA-Eval-DesignFlow-WaveSineZeroXing-001`
6. 日报 + MEMORY（DEBT 1→0）
