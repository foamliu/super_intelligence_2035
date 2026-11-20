# trace deepread — 1795059093484_svju2 (clarawu@hfeg0pkn005, mc172)

**src**: `.75` ssh → 10.129.2.14 `/home/clarawu/.cline/data/sessions/1795059093484_svju2/1795059093484_svju2.messages.json` (694208B, 144 msgs, single file no archive). NMSGS=144.
**kw**: netlist:508;hspice:475;schematic:434;analog:5 → spice-dominant. **tool counts**: editor:46, run_approved_command:14, read_files:13, list_allowed_files:9, ask_question:1.
**domain**: spice_sim (DDR4 FinalDrv VOH sensitivity metric stimulus + extraction). shard B.

## 用户真实意图（trace-faithful，按 msg 顺序，5 轮 act 模式）

用户 clarawu 在 `/proj/m2701/V0_DDR4/workdir/clarawu/simulation/sim_FinalDrv_Ron_cio_leakage_versionD/hspiceD/schematic/netlist/stimulus_file_for_metrics/` 下有一组「dVOH/dX 灵敏度」metric 目录，每个目录应包含一套 HSPICE stimulus deck + 提取脚本 + run 脚本。多个目录被「copy-paste 错配」（装着别的 metric 的文件）。用户 5 轮要求 agent 修正/改这些目录：

### 段1 (msg 0) — 修正 `dVOHdV2` 目录（核心意图：组合两个参考构建新 metric 目录）
- user: 「参考 dVOHdT 和 dRONdV2，帮我修改 dVOHdV2」
- `dVOHdV2` 目录错装了 `dRONdT` 的文件（dRONdT.csv / extract_dRONdT.py / stimulus_dVOHdT_25C.sp / wv_dVOHdT/）。
- agent 分析两个参考：
  - **dVOHdT** = VOH 测量方法参考：`.dc temp POI 3 'Tref-1' 'Tref' 'Tref+1'`，`find v(DQ_VOH) at=...` → 3 点中心差分算 dVOH/dT。
  - **dRONdV2** = V2(VVDD) 参数化参考：`VDD2CS` 中心 param，`VVDD='VDD2CS'`，3 个电压文件 0P82V/0P85V/0P88V，corner `ZQCODE_FF/TT/SS_25C_<V2>V_0P5V`。
  - **dVOHdV2** = 组合：VOH 测量方法 + V2 扫描 → `stimulus_dVOHdV2_0P82V/0P85V/0P88V.sp`，每文件 `.dc VVDD POI 3 'VDD2CS-0.001' 'VDD2CS' 'VDD2CS+0.001'`，`VVDDQ=0.5` fixed，measure `v(DQ_VOH)` → `extract_dVOHdV2.py` 算 dVOH/dV2 + `run` bsub 脚本 + 清理 stale dRONdT 文件。
- 交付物：`dVOHdV2/` 目录 = 3 个 stimulus .sp + extract_dVOHdV2.py + run + wv_dVOHdV2/。

### 段2 (msg 52) — 类似地修正 `dVOHdVQ` 目录
- user: 「类似地，参考 dRONdVQ，帮我修改 dVOHdVQ」
- `dVOHdVQ` 错装了刚生成的 `dVOHdV2` 文件。参考 `dRONdVQ`：扫描变量换成 **VVDDQ**（DQ IO supply），中心 param `VQ`，`VVDDQ='VQ'`，VVDD fixed 0.85，2 个电压文件 0P5V/0P6V，corner `ZQCODE_*_25C_0P85V_<VQ>V`。
- agent 先验证 `DQ_VOH` 节点确实依赖 VVDDQ（读 netlist_delvto + pwr.sp 确认 `vddq!` 由 VVDDQ 驱动）→ dVOHdVQ metric 物理有效。然后生成 `stimulus_dVOHdVQ_0P5V/0P6V.sp` + `extract_dVOHdVQ.py` + `run` + 清理 stale dVOHdV2 文件。

### 段3 (msg 87) — 改 `extract_dVOHdV2.py` 输出列：去掉 `VOH@V2(V)` 和 `dVOH/dV2(V/V)`
- 输出只保留 `dVOH/dV2(mV/V)` 和 `dVOH/dV2(%/V)`。

### 段4 (msg 103) — `dVOH/dV2(mV/V)` 列保留到小数点后两位
- `fmt_mv` 与 MAX 行 `%.6f` → `%.2f`。

### 段5 (msg 114) — 改 `extract_dVOHdVQ.py` 输出列：去掉 `VOH@VQ(V)` 和 `dVOH/dVQ(V/V)`，`mV/V`→`mV/mV`，`%/V`→`%/mV`，数字 2 位小数
- 关键物理换算决策：agent ask_question，user 选「按 per-mV 物理量级换算」：`mV/mV` 列 = dVOH/dVQ(V/V) 原始比值（如 0.35），`%/mV` 列 = (%/V)/1000（如 0.14%）。即数值按 1000 倍换算（不是只改表头文字）。

### 段6 (msg 134) — 改 `extract_dVOHdT.py`：`dVOH/dT(mV/C)` 列保留 2 位小数
- `fmt_mv` + MAX 行 `%.6f` → `%.2f`。

## reframe 判定（portability-reframe + harness-for-teeth · 11-15 重审令 doc-Q&A/script-build 恢复可造）

**原 trace 交付物** = 写在 `/proj/m2701/.../stimulus_file_for_metrics/<metric>/` 的一套 HSPICE stimulus deck + Python 提取脚本 + bsub run 脚本，引用 `/proj/m2701/.../encode_file/*.sp` + `zqcode_75pvt.sp` PDK corner 库 + FineSim/HSPICE 实跑 → **不可便携**（r890 YieldSimAgentPlanGen / r889 SimScanSkillGen 同类 portability-reframe 已立）。
**reframe** → produce 参数化生成器 `gen_dvoh_sens_metric.py`：输入 spec.json（metric 名 / measure_node / 扫描变量 sweep_var / 中心 param / sweep_half / fixed_params / point_files[suffix,center,corners] / x_label / slope_unit / 输出列 drop_columns / column_renames / per_unit_rescale / decimal_places）→ 输出一套 `stimulus_<metric>_<suffix>.sp` + `extract_<metric>.py` + `run`。把 trace 5 轮意图（VOH 3 点中心差分测量方法 + 任意扫描变量参数化 + 输出列裁剪/重命名/per-mV 物理换算/小数精度）全部固化为 spec 驱动。
**check 牙**：B spec（dVOHdVQ + msg114 换算，与 A 结构性反向：sweep_var=VVDDQ vs VVDD / center_param=VQ vs VDD2CS / fixed VVDD=0.85 vs VVDDQ=0.5 / 2 点 vs 3 点 / corner 0P85V_<VQ>V vs <V2>V_0P5V / 输出列 mV/mV+%/mV 重命名 + per-mV 1000× 换算 vs mV/V+%/V）→ check 独立跑 SUT 生成器于 B，断言生成 stimulus 结构（.dc sweep_var POI 3 / find v(DQ_VOH) / center_param / fixed_param / B corners / 文件名 suffix）+ extract.py 输出列配置（重命名 mV/mV+%/mV、drop VOH@/V/V、反硬编码 A 的 mV/V+%/V+VOH@V2）+ 在合成 B md0 fixture 上真跑 extract 算 per-mV 换算数值（mV/mV=slope V/V、%/mV=(%/V)/1000，非 A 的 *1000 值）+ 2 位小数 + MAX 行 + py_compile + 确定性 3 run + anti-stub（空壳/硬编码 A/always-print-B 在 B2 不同数值 fixture 上 FAIL）。layer L1（无 EDA 二进制）。

## A/B spec 对照（造题用）

| 维度 | A (dVOHdV2, trace-faithful 段1+段3+段4) | B (hidden, dVOHdVQ 段5 msg114, 结构性反向) |
|---|---|---|
| metric | dVOHdV2 | dVOHdVQ |
| x_label / slope_unit | V2 / V | VQ / V |
| sweep_var | VVDD | VVDDQ |
| center_param | VDD2CS | VQ |
| sweep_half | 0.001 (V) | 0.001 (V) |
| fixed_params | {VVDDQ: 0.5} | {VVDD: 0.85} |
| point_files | 3: 0P82V/0.85, 0P85V/0.85→0.85, 0P88V/0.88 | 2: 0P5V/0.5, 0P6V/0.6 |
| corners | ZQCODE_FF/TT/SS_25C_<V2>V_0P5V | ZQCODE_FF/TT/SS_25C_0P85V_<VQ>V |
| drop_columns | [VOH@V2(V), dVOH/dV2(V/V)] | [VOH@VQ(V), dVOH/dVQ(V/V)] |
| column_renames | {} | {dVOH/dVQ(mV/V)→dVOH/dVQ(mV/mV), dVOH/dVQ(%/V)→dVOH/dVQ(%/mV)} |
| per_unit_rescale | false (mV/V=slope*1000, %/V=slope*100) | true (mV/mV=slope, %/mV=(slope*100)/1000) |
| decimal_places | 2 | 2 |

## 造题 ETA / DEBT
deepread 完成 r891。合成 case EDA-Eval-DesignFlow-DvohSensMetricGen-001 同轮（k~16, 5 neg, L1 produce-generator portability-reframe）。
