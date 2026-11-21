# Deepread: 6rsot — NanoSpice log format support for cmp_log toolkit

- **Session**: `1794967669776_6rsot.messages.json`
- **User**: e0044979 @ hfeg0pkn034 (10.129.32.75)
- **mc**: 71 · **Domain**: characterization · **Round**: r987 (shard B)
- **Case ID**: `EDA-Eval-DesignFlow-NanoSpiceLogFormatSupport-001`

## Real task (trace-faithful)
用户 e0044979 自研一套 Python 仿真日志对比工具包 `cmp_log/`（4 个文件：
`simlog_parsers.py` / `meas_parsers.py` / `compare_report.py` /
`sim_log_compare.py`），用于跨仿真器（PrimeSim / FineSim / XA / FX / Spectre）
比对仿真 log 与 measure 结果、生成 HTML 报告。近期切到 **NanoSpice**
（Primarius 并行 SPICE）做 SRAM 时序/表征仿真后发现工具包不认识 NanoSpice 格式：

1. `detect_sim` 返回 `unknown`（无 NanoSpice 关键字识别）
2. `parse_sim_log` 解析不出版本/模式/运行阶段/资源统计
3. `find_measure_source` 找不到 `.mt0`（NanoSpice 把 measure 结果写在
   `<logname>.output/<logname>.mt0` 子目录里，而非 log 同级）
4. `sniff_meas_format` 把 NanoSpice 的 `.mt0`（带 `$DATA1` 头但数据是逐行
   `name = value` 的 kv 格式）误判为 columnar 列式格式 → measure 全丢
5. `compare_report._STAGE_MAP` 无 `nanospice` 条目 → DC/Tran 阶段归桶失败

## Agent's fix (4 处改动)
1. **`simlog_parsers.py`**：
   - `detect_sim` 增加 `if "NanoSpice" in head_text: return "nanospice"`
     （头部截断兜底还加了 `Final Statistics` + `Total Simulation CPU Time` 特征行）
   - 新增 `_parse_nanospice(info, lines)` 解析器，用一组正则：
     - `_RE_NS_VERSION` / `_RE_NS_START_TIME` / `_RE_NS_PWD` / `_RE_NS_CMDLINE`
       （命令行里的 `+simmode=<mode>` 取模式）
     - `_RE_NS_AFTER` 解析 `Memory: XXM Peak memory: XXM Elapsed Time: X (s)
       CPU Time: X (s) After <stage>` 行（4 个 After 阶段：Matrix Loading /
       parsing / Elaboration / Kernel setup，各含 cpu/wall/mem）
     - `_RE_NS_TOTAL_CPU` / `_RE_NS_TOTAL_ELAPSED` / `_RE_NS_PEAK_MEM`
       （Final Statistics 汇总）
     - `_RE_NS_DC_TIME` / `_RE_NS_TRAN_TIME`（Final Statistics 细分 DC/Tran 时间，
       记为 `DC-Analysis` / `Tran-Analysis` stage）
   - `parse_sim_log` 分发到 `_parse_nanospice`

2. **`meas_parsers.py`**：
   - `sniff_meas_format` 改为：`$`/`.TITLE` 头之后**继续扫描数据行**，
     若出现 ≥2 条 kv 行则判 `kv`（覆盖 NanoSpice 式 `$DATA1`+kv 混合格式，
     原来遇到 `$` 头就 break 误判 columnar）
   - `find_measure_source` 在同目录 `<stem>.mt0` 之外再查
     `<log_dir>/<stem>.output/<stem>.mt0`（NanoSpice 的 measure 输出子目录约定）

3. **`compare_report.py`**：`_STAGE_MAP` 增加
   `"nanospice": ("DC-Analysis", "Tran-Analysis")`

4. **`sim_log_compare.py`**：输出目录不存在时 `os.makedirs(out, exist_ok=True)`

## Reframe
trace 原是一次性给 cmp_log 工具包加 NanoSpice 支持（用户切到 NanoSpice 做 SRAM
仿真发现工具不认识，agent 改 4 个 .py）。reframe 成 `submit.zip`（4 修改后 .py），
把 4 个真实行为转成 check 齿：
- `detect_sim` 识别 NanoSpice（U0 unknown→nanospice）→ 齿 ③
- `parse_sim_log` 解析版本/模式/资源/阶段（U40）→ 齿 ④⑤⑥⑦
- `find_measure_source` 查 `.output` 子目录（U12）→ 齿 ⑧
- `sniff_meas_format` 识别 `$DATA1`+kv 混合格式（U23）→ 齿 ⑨

A/B 仅版本/模式/host/pwd/数值/measure 名异（anti-hardcode-A），3-seed 确定性禁时间戳。
layer L1（纯 Python log/.mt0 文本解析无 EDA 二进制）。

## Asset fidelity
### A (visible, SRAM 时序)
- `nano_log_A.log`：VERSION 4.26.2.8, MACHINE hfeg0pkn042, PWD sram_a/TV1,
  +simmode=prox1, 4 After 阶段, Final Statistics (cpu 26173.8 / wall 3749.84 /
  mem 21065.6, DC 32.173s, Tran 2862.14s)
- `nano_mt0_A.mt0`：`$DATA1 SOURCE='NanoSpice' VERSION...` + `$OPTION MEASFORM=2`
  + `.TITLE` + 31 条 kv measure（clk_h_dd_yf_w0 / t_tcs_f_cg / clk2wl_max /
  wl2sae_max / sae2q_max ...）
- `fsim_mt0_A.mt0`：FineSimPro kv+targ/trig 同 measure 名

### B (hidden, SRAM bitcell 双端口表征)
- `nano_log_B.log`：VERSION 4.30.1.0, host hfeg0pkn077, PWD srambb/TV2_NS,
  +simmode=gigahd, cpu 38294.5 / wall 5559.21 / mem 28451.3, DC 48.902s, Tran 4356.77s
- `nano_mt0_B.mt0`：`$DATA1`+kv 36 条 measure（vdd_wl_hi / i_leak_bl_standby /
  t_w_access / v_sae_peak / v_snm_read ...）
- `fsim_mt0_B.mt0`：FineSimPro kv 同 36 名

## check.py — 13 条 a..m
- (a) submit.zip 有效 + 含 4 个 .py
- (b) 4 脚本可编译
- (c) detect_sim(B log) = "nanospice"
- (d) parse_sim_log: version=4.30.1.0 + mode=gigahd + date 含 "Wed Jan 20"
- (e) total_cpu=38294.5 + total_wall=5559.21 + peak_mem=28451.3
- (f) 4 After 阶段 + 至少一个有 cpu+wall+mem 全设
- (g) DC-Analysis + Tran-Analysis 阶段
- (h) find_measure_source → ("mt0", path 含 ".output")
- (i) load_measures ≥30 + B 名在 + A 名不泄漏
- (j) sim_log_compare.py 跑 B exit 0 + HTML >500B
- (k) HTML 含 NanoSpice + gigahd + srambb/TV2_NS + B 前 3 measure 名
- (l) anti-hardcode-A: HTML 无 A version/mode/host/pwd/measure 名
- (m) 3-seed 确定性: 同一 B 目录重跑 3 次 HTML 逐字节一致

## Negative samples (4)
- `neg_empty.zip`：4 .py 全是 stub（无 detect_sim 等）→ ③ AttributeError
- `neg_print.zip`：fake return（detect_sim 假返 nanospice 但 parse_sim_log 无 stage）→ ⑥
- `neg_core_removed.zip`：裸原始 4 .py（未加 NanoSpice 支持）→ ③ detect_sim=finesim
- `neg_hardcode_a.zip`：版本/模式硬编码 A 的 4.26.2.8/prox1 → ④ mode=gigahd catch

## INFRA notes
- 6rsot live session 可直读 `/home/e0044979/.cline/data/sessions/`
- .75 eda_flow sandbox 建 14 文件 case_assets + 4 neg zip，自检 ref PASS 13/13 + 4 neg FAIL
- 二进制传输：eda_flow `read_file` text 直返 content string；base64 经 write tool
  会 CRC 损坏（大文件 mid-stream），改用 `execute` 返 dict 存 tool-output JSON 再
  `python3 json.load` 解
