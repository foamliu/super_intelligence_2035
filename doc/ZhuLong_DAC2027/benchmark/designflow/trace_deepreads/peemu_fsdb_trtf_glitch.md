# Deepread — 1795079429231_peemu (gallopc @ hfeg0plg86, mc=86)

> shard D · domain=waveform · claimed r1624 · session 108 msgs (66 user / 42 assistant)
> 真实任务：从 FineSim FSDB 波形批量提取信号 tr/tf + glitch，写出可复用 Python 脚本。

## 1. 用户意图（原话脉络）

- **msg0 (act)**：「写一个脚本，可以从一个 fsdb 中提取所有可能获取到信号的 tr 和 tf，后续还可筛选其中比较差的（超过了规定的阈值），并且获得 glitch。具体可以先将 fsdb 文件转换为 txt 或 vcd 方便提取，然后对于 tr 和 tf，需要先判断信号所在的电压域，可以通过截取信号 1ns 内浮动不超过百分之 0.1 的区间，然后判断区间平均值的最大值这种方法，请你进行更好到完善。**不要直接读取 fsdb 文件**，我只需要你写一个脚本，然后我运行提取…用你的经验写脚本」
  - 参考 fsdb 路径：`/proj/ddgoa/V0/simdir/finesim/workdir/gallopc/simulation/sim_xdecg_driver_test/sweep_x20_size_op/out_adjsecgr_swp_ff_1.2_xo16_xi16/swp_secgr__ff_1.2_xo16_xi16.fsdb`
- **msg19/26**：继续生成 / 交给你的工作（脚本分块续写）
- **msg37**：「`/home/gallopc/fsdb_trtf_glith/wv_tmp_trtf/` 这个路径下是我跑了的结果，好像报错了？帮我看一下为什么」→ 调试 wv 导出/解析 bug
- **msg71**：「直接把怎么跑的 terminal 指令给我，然后删掉需要删掉的」→ 给一键命令 + 清理临时 helper
- **msg81**：「有没有办法不需要我自己手动加入信号名改动什么，直接一步命令到位，生成统计结果」→ 加 `--auto` 模式（自动发现全部信号名 + 筛电压信号 + 分批 200 导出 + 分析 + 出统计）
- **msg96**：「这些 csv 的横向的数据都代表什么」→ 详释 4 个 CSV 列含义
- **msg98**：「违例边沿表（超 --tr-max/--tf-max，按最差排序）存放在哪」→ 补 `trtf_violations.csv`（按 tran 差到好排序）
- **msg107**：「存在一个严重的问题，比如 `cm0_ro_eqoffsec4` 这个信号，这个信号虽然可能在 1ns 内波动不大，但是它的**高点平电压其实非常小**，我们可以认为至少 100mV」→ 加 `--min-swing`（默认 100mV），swing 或 high rail < min_swing 标 `low_swing` 跳过不测

## 2. 助手工具链 / 产物

- 工具：`editor`（30 次，文件写改）+ `run_approved_command`（10 次，跑 wv/自测）+ `read_files`（9）+ `list_allowed_files`（6）+ `skills`（1）。
- 主产物：`/home/gallopc/fsdb_trtf_glitch.py`（1743 行）+ `fsdb_trtf_selftest.py`（317 行，56 用例全 PASS）。
- 辅助：`grep_ace_doc.py` / `extract_ace_sections.py` / `cleanup_tmp_helpers.py`（临时 helper，后清理）。

## 3. 脚本核心算法（fsdb_trtf_glitch.py）

Pipeline：EXPORT → PARSE → LEVELS → EDGES → FILTER → GLITCH → REPORT。

1. **EXPORT**：生成 Tcl（`sx_open_sim_file_read` / `sx_signal` / `sx_export_range` / `sx_export_data` [+ `sx_export_vcd`]）+ clean-env sh wrapper（unset LD_LIBRARY_PATH），跑 `wv -ace_no_gui`（~16x 快于 fscript）；默认 `bsub -q wv_queue -env none -K`，失败回退直跑 wv（`--direct` 强制本地）。**FSDB 二进制绝不直读**，只导出 `.tbl` 文本。
2. **PARSE**：读 `.tbl`，WaveView 改写头名 `a.b.v(c)→v(a.b.c)` 反归一化，client-side 时间窗过滤。
3. **LEVELS（稳定窗法）**：滑窗（自适应试 10n/5n/2n/1n，取最大稳定窗），窗内波动 ≤ `max(0.1%·|mean|, 0.1%·swing, v_floor)` 视为稳定；聚类稳定窗均值为轨；`v_domain`=最高轨均值；LOW/HIGH=驻留最久的两轨；无稳定窗则退化 5%/95% 分位数（`level_source=percentile-fallback`）。
4. **EDGES**：按 LOW/HIGH band 分段成 dwell run + transition zone；每个 LOW→HIGH/HIGH→LOW dwell 对 = 一条边；`tr/tf = t(90%) − t(10%)`（可配置 `--rise-lo/--rise-hi`，默认 10%/90%），线性插值求穿越时刻；非单调边沿（回勾 >2% swing）标记。
5. **FILTER**：`tr/tf > --tr-max/--tf-max` 标 `VIOLATION`，`trtf_violations.csv` 按 tran 差到好排序。
6. **GLITCH**：短脉冲（穿 50% 中值且宽 < `--glitch-width`，默认 200p）/ runt（离开本轨未到对面轨就回来）/ 非单调边沿 / 卡死信号尖峰。
7. **低摆幅跳过**：`swing < --min-swing`（默认 100mV）或 `v_high < --min-swing` → `mode=low_swing`，不测 tr/tf（mV 级内部偏置/eq 节点只产噪声）。
8. **REPORT**：console summary + 4 CSV（edges / violations / glitches / summary）+ `--json`。退出码 0=无违例 / 3=有违例。

## 4. CSV 列含义（msg97 详释）

- `trtf_edges.csv`：signal, dir(rise/fall), t_ref1_s(10%/90%), t_ref2_s(90%/10%), t_mid_s(50%), tran_s(=t_ref2−t_ref1), limit_s, status(OK/VIOLATION/incomplete), non_monotonic, prev_dwell_s, next_dwell_s
- `trtf_violations.csv`：signal, dir, tran_s(排序键), limit_s, t_ref1_s, t_ref2_s, t_mid_s, non_monotonic
- `trtf_glitches.csv`：signal, type(pulse_high/low/runt_up/down/spike_up/down), t_start_s, t_end_s, width_s, amplitude_v, amp_pct_swing
- `trtf_summary.csv`：signal, mode(digital/single_level/constant/skip/low_swing), domain_v, v_low_v, v_high_v, n_points, n_rise, n_fall, tr/tf min/max/avg, n_tr_bad, n_tf_bad, n_incomplete, n_non_monotonic, n_glitch, v_min/max, overshoot/undershoot, level_source

## 5. case 合成（r1624 → FsdbTrTfGlitchExtract-001）

- **task_id**：`FsdbTrTfGlitchExtract-001`，domain=waveform，LIVE-NA，judge_layers=[L0,L1]，无 check_live（deliverable=Python 脚本，纯结构化 JSON 判分，无真实 EDA 二进制依赖）。
- **synthesized-reframe**：spec-JSON 驱动的 `fsdb_trtf_glitch.py(spec.json)->report.json`（把 CLI 参数包成 spec JSON，输出汇总 report JSON），hidden-B 反硬编码。
- **A**(visible) `spec_A.json` + `waveform_A.tbl`（合成 4 信号）：clk 干净 digital(tr=80ps/tf=96ps/0违例)、bad 超阈慢边沿(tr=800ps>500p VIOLATION)、lowsw 50mV 低摆幅(<100m 跳过)、glch 50ps 窄脉冲 glitch(width<200p)。
- **hidden B**(token-structurally 不同) `spec_B.json` + `waveform_B.tbl`：1.5V 轨(异于 1.2V)、tr_max 800p(异于 500p)、glitch_width 300p(异于 200p)、min_swing 200m(异于 100m)、含 constant(d2_const) + runt_up(d2_runt) 信号(A 无)、d2_low2 150mV 低摆幅(在 B 200m 下跳过)。
- **reference**：`fsdb_trtf_glitch.py`(~380 行 slim 重实现，镜像真实算法语义)。
- **check.py 13 conds(a-m)**：a zip 含 py ②b py_compile ③c A 运行 exit0 写 report_A ④d A clk digital+1rise+1fall+0bad+v_high≈1.2 ⑤e A bad rise VIOLATION tran≈800ps>500p+n_tr_bad==1 ⑥f A lowsw low_swing+n_rise=n_fall=0+tr=null ⑦g A glch pulse_high glitch width<200p ⑧h A n_viol=1+n_glitch=1+violations 排序 ⑨i A clk/lowsw level_source=stable-windows(非 fallback) ⑩j A clk tr≈80ps/tf≈96ps(确认 10%→90% 非 0-100% 全斜坡) ⑪k B 运行 exit0 写 report_B ⑫l B d2_const constant+d2_runt runt_up+d2_slow limit==800p+d2_low2 low_swing ⑬m 反硬编码源码无 A 专属 token(lowsw/glch/waveform_A)。
- **自验全绿**：ref PASS(13/13) + negative_selftest 6neg ALL-FAIL distinct first-fail{a,b,f,e,l,g} + §4.9 trio(no_lowswing→f/full_ramp→e/no_glitch→g) + SKIP_RUN=1 workdir leak 自检通过 + 3-way sha sync(f28cb3c4…, size 11613) + k_check=13=k_rationale=13。
- 台账 mark：1795079429231_peemu → case(EDA-Eval-DesignFlow-FsdbTrTfGlitchExtract-001)。
