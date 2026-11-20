# Deepread: 6ajm4 (e0023936 @ hfhds201) — wv-dataeye-measure skill

**Session**: `1794201834116_6ajm4.messages.json` (74 msgs, 569KB, 2026-11-09)
**User**: e0023936 (hfeg0plg06=10.129.32.75=hfhds201 本机)
**Domain**: eda_other (WaveView eye-diagram measurement batch pipeline / skill automation)
**Markers**: 21 VERDI/verdi, tcl=205, syn=15, hspice, 1 virtuoso
**Trace source**: real cline session, USER#8 = A-faithful spec (提出需求未给根因)

## Conversation flow
- USER#0 (ts=1794201835148): 「当前打开的waveview波形图，如何理解？」= 分析问答 (非 produce)
- USER#8 (ts=1794202130463): **A-faithful 任务说明（逐字）**：
  > 「对已加载的 sslvht_10667.fsdb 中信号 v(dq) 以 10667M 速率做眼图 VREF 扫描（0.030~0.160V、步长 1mV、vdc=vac=0.040V），逐行输出 Vref/aperture(ps)/skew(ps)，再用 dual jitter gate（保留 skew≤3×最小skew 且≤15ps 的点）加邻域支持（±0.010V 内有效邻居数）过滤边缘假峰，选出眼宽最大的点，报告最佳眼宽、VREF 和 skew。」
  = 提出需求未给根因（A-faithful ✓）；明确给出方法学参数（VREF 范围/步长/vdc/vac/dual gate 阈值/support 窗口）。
- USER#17/22/26/36: 「打开 eye 图」「打开最大矩形区域」「以 vref 为中心线的最大矩形」「打开 aperture」= WaveView GUI 操作（辅助，非交付核心）
- USER#38 (ts=1794204247853): `<skill_instructions name="wv-dataeye-measure">` = **assistant 交付的完整 skill**（金标准），含 8 文件 file-roles 表：
  - `measEyeMaxWidth.tcl` — 核心 TCL: sx_open_sim_file_read / sx_create_eye / sx_measure_eye / sx_query_eye, VREF sweep, 写 .rep (Vref/Width/Skew 表 + Max Width/Min Skew 摘要)
  - `eye_width.cfg` — 手动测量配置模板
  - `wv_batch_cfggen.py` — Step1: 按 fsdb 生成 .cfg (auto rate detection by a<NN> tag 或文件名数字)
  - `wv_batch_run.sh` — Step2: 循环调 wv CLI 跑 TCL, 产 .rep
  - `wv_batch_collect.py` — Step3: 解析 .rep, dual jitter gate (SKEW_MULT=3, MAX_SKEW_PS=15) + 邻域支持 (SUPPORT_WIN=0.010V) 选最佳 VREF/眼宽, 写 wv_summary.csv
  - `wv_batch_all.sh` — 一键: cfggen→run→collect
  - `wv_run_job.sh` — **端到端 runner**: 设 py310_env PATH, unset LD_LIBRARY_PATH, 烘 Synopsys license vars, 调 wv_batch_all.sh (bsub 入口)
  - `wv_csv_pipeline.py` — 等价纯 numpy 管线 (--no-dump/--no-run 分阶段)

## Golden deliverable (on-disk, e0031982 可读)
`/home/e0023936/devops/wv-dataeye-measure/`:
- SKILL.md (17115B, v2 queue-ready)
- measEyeMaxWidth.tcl (3719B) — TCL 测量脚本
- wv_batch_collect.py (8367B) — .rep 解析 + dual gate 选最佳
- wv_run_job.sh (2661B) — 端到端 runner
- wv_batch_cfggen.py (11529B), wv_batch_run.sh (4800B), wv_batch_all.sh (2525B), wv_csv_pipeline.py (14542B)
- eye_width.cfg (604B), wv_summary.csv (81B = `name,corner,aperture_ps,vref_mV,skew_ps\nsslvht_10667,sslvht_10667,64.25,109,3.89`)
- sslvht_10667.fsdb (19.7MB, 不入 case)

## 关键算法（check.py 验证核心）
1. **measEyeMaxWidth.tcl**: VREF 循环 `for {set vref $vref_start} {$vref-$vref_stop<1e-9} {set vref [expr $vref+$vref_step]}`；vref_bit 精度 (step>=0.001→3, >=0.0001→4, >=0.00001→5)；end_time="end"→`sx_equation xmax($signal_name)`；aper/skew `format %.2f [expr $aper*1E12]` (ps)；写 .rep 含 `* Max Width : Vref=... Width=...p Skew=...p` + `* Min Skew : ...` + 表头 `Vref Width Skew`。
2. **wv_batch_collect.py**: dual jitter gate = `SKEW_MULT(3.0)*min_skew` AND `MAX_SKEW_PS(15.0)` (取严格者)；support/density = `SUPPORT_WIN(0.010V)` 内有效邻居数；选 `max width` 且 support 高的点；ui_ps = `1000/(rate/1000)`；corner_of = `re.search(r"a(\d+)", name)`。
3. **wv_run_job.sh**: `unset LD_LIBRARY_PATH`；`export SNPSLMD_LICENSE_FILE="12000@hl04:...:12000@hfrdap201"`；`export LM_LICENSE_FILE="59001@hl01:..."`；`export PATH=/home/e0023936/miniforge3/envs/py310_env/bin:$PATH`；`set -e`；调 `wv_batch_all.sh`。

## Case 设计（B-档 synthesized）
- **deliverable**: `gen_wv_eye_pipeline.py` (argv: spec.json outdir) — spec-driven 生成器，产 3 核心文件 (measEyeMaxWidth.tcl + wv_batch_collect.py + wv_run_job.sh)，参数化 signal/rate/vref_range/vdc/vac/gate_consts/license/python_path。
- **A**: spec_a.json (faithful golden: sslvht_10667, v(dq), 10667M, vref 0.030-0.160 step 0.001, vdc=vac=0.040, SKEW_MULT=3, MAX_SKEW_PS=15, SUPPORT_WIN=0.010, license=12000@hl04..., py=/home/e0023936/miniforge3/envs/py310_env/bin) + prompt(USER#8 逐字) + task_brief(≤3行 CLI 契约)。
- **hidden B**: spec_b.json (异构: signal v(dqs), rate 8400M, vref 0.050-0.180 step 0.002, vdc=0.050 vac=0.035, SKEW_MULT=2.5, MAX_SKEW_PS=12.0, SUPPORT_WIN=0.008, 不同 license servers 12000@sl04:..., 不同 py path /opt/miniforge3/envs/py311/bin, 不同 fsdb 命名) + hidden_manifest。
- **check.py**: 16 条断言 a-p（zip/生成器 subprocess 跑 B exit0 产 3 文件/TCL 结构 sx_*/VREF loop/B 参数/vref_bit/end_time 处理/collect subprocess 跑合成 B .rep 产 CSV/dual gate 拒边缘假峰/support 选持续峰/run.sh unset LD_LIBRARY_PATH+license+py path+set -e/bash -n valid/python -c compile/反硬编码 A 字面量/3-seed 确定性）。
- **subprocess 可验**: collect.py 在合成 .rep 上跑（核心算法）；bash -n / python -c compile（语法）；生成器 3-seed 确定性。

## 限制
- 真实 fsdb (19.7MB) + wv license 不可在判分环境跑 → check.py 用合成 .rep（结构忠实于 TCL 输出格式）验 collect.py 算法。
- TCL/shell 静态结构验（反硬编码 B 字面量）。
