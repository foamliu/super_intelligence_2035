# 深读笔记 — fa3cd (waveform 域, mc=73, waveview:195 主导)

**trace**: `1792371248997_fa3cd` · user `e0039602` · host `hfeg0plg85/...` · 2026-10-19 00:54→02:20 · model deepseek-v4-flash · cwd `/home/e0039602/.cline/skills/waveview-fsdb-readerV2-2` · 44 msgs(24 user/20 assistant) / 20 tool_use(read_files 7 / run_approved_command 6 / editor 4 / list_allowed_files 1 / get_agent_policy_status 1 / run_commands 1) · terminal_marker `failed_external_process_exit`(用户首条命令 FSDB not found 报错退出)。

## 项目背景
用户在调试/理解自建 skill **waveview-fsdb-readerV2-2**：用 Synopsys WaveView ACE Tcl 后端（`wv -ace_no_gui`，比 fscript 快 ~16x）从 finesim FSDB 波形里读层次信号 → 导出 `.tbl` → Python 解析 → 自动判数字/模拟 → 数字做边沿/脉冲/电平持续/上升下降沿时间，模拟做过零+统计。两文件：
- `waveview-fsdb-readerV2-2.py`（670 行，分析器 + CLI + 总线展开）
- `waveview_fsdb_reader.py`（434 行，读 FSDB + 生成 Tcl/sh + 解析 .tbl）

## 4 个 user 问题（真实意图）
1. **msg0**：跑 `waveview-fsdb-readerV2-2.py <fsdb> "xi_peri0.xi_bcenter.net01818<15:0>" 1p 0.9u 1.5u` 报 `FileNotFoundError: FSDB not found: /proj/drcpa/V0/.../Mrs004_TT0.94V25C_X16.fsdb` —— "我这样运行这个项目，为什么会报错"
2. **msg28**："请你阅读这个项目中的代码，他会如何判定数字和模拟信号，如何判断出没有有效性好之后他会不仅行输出吗"（数字/模拟判定 + 无数据是否输出）
3. **msg37**："nodata的意思是没有读到任何信号？而不是说有信号但是信号里没有包含数据？"（澄清 found=False 的两种含义）
4. **msg39**："代码是会将读出的文件存在wv——tmp文件里是吗"（读出数据落盘位置）

## agent 流程
- msg1-27（问题1）：list_allowed_files → read_files 读两源 + `run_approved_command`(python-runner) 跑自写 `_check_fsdb.py` 逐级 `os.path.exists/access` → 定位 `/proj/drcpa` 存在但 access=False，`/proj/drcpa/V0` 不存在 → 结论"不是 bug，是 FSDB 路径在本机不存在（FSDB 在生成它的 farm 节点上）"→ 清理临时文件。
- msg29-38（问题2-3）：read_files 完整读两源 → 解释 `detect_signal_type()` + `found` 字段两种 no-data 含义被同一个 `if not pts` 折叠。
- msg40-43（问题4）：read_files `_run_waveview()` + 实读 `wv_tmp/wv_o_26488.tbl`/`wv_s_26488.tcl` → 确认 5 类中间文件落 wv_tmp，真数据在 `wv_o_<ts>.tbl`。

## 关键代码逻辑（verbatim 已读，下轮 case 直接复用）

### .tbl 格式（WaveView 导出，真文件 `wv_o_26488.tbl` 426 行）
```
#format table ## [Custom WaveView] saved 10:45:31 Mon Sep 21 2026
XVAL xi_peri0.xi_bcenter.v(net01818<15>) xi_peri0.xi_bcenter.v(net01818<13>)
 0.000000000E+00  9.399999380E-01  9.399999380E-01
 9.535040000E-07  9.381002784E-01  9.381185174E-01
 ...
```
- 头关键字 `XVAL`（不是 fscript 的 `TIME`）。每行 = 时间 + 各信号该时刻值，科学计数法无后缀。
- WaveView 会把请求的 `v(scope.net)` 在表头**重写**成 `scope.v(net)`；`normalize_sig_name()` 反转：找最后一个 `.v(`，scope=其前，net=括号内，重组 `v(scope.net)`。`v(dq0<0>)` 顶层无点前缀则不变。

### parse_wv_table(text) → {sig: [(t,v),...]}
- 跳过 `#`/空行；首个 `XVAL`/`TIME` 行 → sig_names = `normalize_sig_name(p)` 各列；其后每行 split，`float(parts[0])` 为 t，逐列 `float` append。列不足/非数字跳过。

### read_signals() 客户端时间窗过滤（问题3 的根因）
- `t_lo=parse_time_str(time_start)`、`t_hi=parse_time_str(time_end)`；`parse_time_str` 后缀表 `ms/p/n/u/m` → 秒。
- 对每个 raw 信号点过滤 `t>=t_lo` 且 `t<=t_hi` → **可能把有点的信号滤成空 `[]`**（情况B）。WaveView 找不到的信号名静默返回空 handle，根本不进 data 字典（情况A）。**两种情况 `get_points` 都返回 `[]`，都判 `found=False`，输出同一句 `[!] Signal ... not found`** —— 代码分不开。

### detect_signal_type(points, digital_thresh=0.25, level_frac=0.05, min_dwell=0.05)
1. 空 points → `"analog"`
2. `swing=v_max-v_min < digital_thresh` → `"digital"`（恒定/亚阈值）
3. 否则 `tol=level_frac*swing`；`f_low`=落在 `|v-v_min|<=tol` 的样本占比；`f_high`=落在 `|v-v_max|<=tol` 的占比；`f_low>=min_dwell 且 f_high>=min_dwell` → `"digital"`，否则 `"analog"`（如只在低电平停留+一个尖峰的电流信号正确判模拟）

### 数字分析（analyze_signal type=="digital"）
- `detect_edges(points, thresh=0.25)`：相邻样本 `v_prev<thresh<=v_curr`→rise，`v_prev>=thresh>v_curr`→fall；返回 `[(t,"rise"/"fall")]`。
- `detect_pulses(points, thresh)`：`v>=thresh` 高脉冲 `[(start,end,width)]`，结尾在脉冲内补到 points[-1]。
- `reference_levels(points, edge_frac=0.10)`：`vals` 升序，`k=max(1,round(n*0.10))`；`v_low=_median(s[:k])`、`v_high=_median(s[-k:])`（用最低/最高 10% 的中位数抗毛刺）；退化（v_high<=v_low）回退 (0,1)。
- `mid=v_low+0.5*swing`、`v25=v_low+0.25*swing`、`v75=v_low+0.75*swing`。
- `level_durations(points, level=mid)`：`crossing_times(points,level,up=True/False)` 线性插值过零时刻；events 合并排序；从 points[0] 状态推 high/low 区间；返回 `(high_pulses, low_pulses)` 各 `(start,stop,dur)`。
- `transition_times(points,v_low,v_high)`：rise=25%→75% up-crossings 配对（`t75-t25`），fall=75%→25% down-crossings 配对（`t25-t75`）。
- `_trim_stats`/`_tran_stats`：`{n,min,max,avg,sum}`。

### 模拟分析（type=="analog"）
- `analog_stats`：`n_points/t_start/t_end/duration/v_min/v_max/v_mean/v_min_at/v_max_at/first/last`。
- `zero_crossings(points)`：相邻样本跨 0（`v_prev<0<=v_curr` 或 `v_prev>=0>v_curr`）线性插值 `t_cross`，direction rising/falling。

### found 字段（问题3 核心）
`analyze_signal`：`pts=get_points(data,sig_name)`；`if not pts: return {"signal":sig_name,"found":False}`。`found=True` 时 report 含 `type/n_points/t_start/t_end` + 数字或模拟分支字段。

### _run_waveview() 落盘 5 文件到 wv_tmp（问题4）
`wv_s_<ts>.tcl`（Tcl 输入）/`wv_r_<ts>.sh`（清 env 包装）/`wv_o_<ts>.tbl`（**真导出波形数据**）/`wv_b_<ts>.out`/`wv_e_<ts>.err`。`ts=int(time.time()*1000)%100000+rand(0,999)`。真分析在内存 `data` 字典做，.tbl 只是 WaveView 中间产物，**最终报告只打印不写文件**。

### 真实 .tbl 数据特征（asset A 候选）
`wv_o_26488.tbl`：2 信号 `xi_peri0.xi_bcenter.v(net01818<15>)`/`<13>`，~0.94V 量级，时间 0→1.9e-6s，含下降沿（0.94→0→0.94）和上升沿 —— **模拟/弱数字混合**（swing≈0.94>0.25 但驻留判定偏向一边）。是真实 finesim DRAM 仿真导出。

## .75 沙盒 wv 可用性（已实测，下轮 L2 升级备选）
- `wv` 二进制在 `/apps/synopsys/SRB/wv/T-2022.06-SP1/bin/wv`。
- `wv -ace_no_gui <tcl>` 在 eda_flow 沙盒**可执行**（rc=0，加载 FSDB 成功，跑 Tcl 成功，CPU 0.16s）。
- license 串 `12000@hl04:12000@hfds4:12000@hl05:12000@hl06:12000@hl07:12000@hl08`；须 `unset LD_LIBRARY_PATH` + `PATH` 设 wv bindir。
- demo FSDB：`/apps/synopsys/verdi/Verdi_M-2017.03-SP2-9/demo/{mixed/mixed.fsdb, dumper/modelsim_link_third_party/sample.fsdb, hwsw_debug/multi_core/design.fsdb}`。
- **未解决**：demo FSDB 的 `sx_signal` 路径未探明（`v(clock)`/`v(system.clock)` 均 "signal not found"；mixed.vcd 顶层 scope=`system`，信号 clock/reset/data[7:0]/vma/...，但 FSDB 内部命名规则与 VCD 不同，可能 VHDL 混合用 `:` 或无 `v()` 包装）。**下轮 L2 升级路径**：探明 demo FSDB 信号路径 → 把 case 改成"候选须调 wv 读 FSDB→分析"，check 在 .75 上对隐藏 FSDB B 真跑 wv。

## 下轮 case 设计（本轮合成）
**ID**: EDA-Eval-DesignFlow-Waveform-001 · **域**: waveform（11 类最后空白域）· **层**: L1（离线 .tbl 分析复刻；trace 4 问中 3 问是分析器逻辑，非驱动 wv）。
- **deliverable**: `outputs/submit.zip` 含 `tbl_analyzer.py`（纯标准库）—— 解析 WaveView `.tbl`（XVAL 头 + normalize_sig_name 反重写）→ detect_signal_type 数字/模拟 → 数字 edges/pulses/reference_levels(median 极端 10%)/level_durations(mid)/transition_times(25↔75%) → 模拟 zero_crossings + analog_stats → 处理 found=False（含"信号名不在 .tbl"和"时间窗滤空"两种 no-data）→ 输出 JSON 报告。
- **asset A**（SUT 看）：真实 `wv_o_26488.tbl` 切片（真 finesim 导出，2 信号 ~0.94V）+ analyzer_spec.md（算法逐条）+ task_brief.md（真实场景：e0039602 的 skill，FSDB 路径错机→改用已导出的 .tbl 做离线分析）。
- **hidden B**（check only，§4.1 不同规模/取值/结构）：`hidden_waveform.tbl` 含 ① 干净数字方波 `v(tb.clk)` 0↔1.8V 多周期 ② 双极模拟 `v(tb.sense)` 正弦/ramp ③ 缺失信号（请求但不在 XVAL 头 → found=False）—— 与 A 的 2 信号 0.94V 完全不同。
- **check 11 条件**（§4.3 ≥8，§4.2 subprocess 真跑，§4.5 3-seed 随机化）：见 reference/check.py。
- **负样本**（§4.4 ≥2 + §4.9 三假）：naive_always_digital / naive_always_analog / naive_skip_missing / naive_fixed_levels + fake_empty_shell / fake_print_expected / fake_ref_core_deleted —— 全 FAIL。

## 牙齿识别（7 类，逐条可独立 FAIL）
1. XVAL 表头解析 + normalize_sig_name 反重写（`scope.v(net)`→`v(scope.net)`）
2. detect_signal_type 三分支（空→analog / swing<thresh→digital / 双电平驻留 f_low&f_high≥min_dwell）
3. 数字 edges 计数（rise/fall 用 thresh 跨越，非简单过零）
4. reference_levels 用最低/最高 10% 中位数（非 min/max，抗毛刺）
5. transition_times 25%↔75% 线性插值（rise=t75-t25，fall=t25-t75）
6. analog zero_crossings 双向 + 线性插值 t_cross
7. found=False 两种 no-data（不在表 / 时间窗滤空）统一处理不崩

close_session keep=false cleaned=true。
