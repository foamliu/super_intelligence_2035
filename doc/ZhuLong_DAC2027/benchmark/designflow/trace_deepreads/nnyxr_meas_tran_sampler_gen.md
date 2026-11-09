# trace_deepread: nnyxr — HSPICE .measure tran 采样测量生成器

- **sid**: 1793754060632_nnyxr
- **user/host**: curryxu @ hfeg0pkn001 (10.129.2.10)
- **mc**: 12 (spice markers) · 281 msgs · ~1MB
- **tools**: editor×44 / read_files×41 / run_approved_command×38 / list_allowed_files×2 / run_commands×2 / SandBox_MCP×2 / ask_question×1

## 用户轮（全 produce-task，无根因 → A-faithful 合格 ✓）

- **U#1 (msg0)**「写一个测量脚本，测量dnner从6.3175ns开始为高电平还是低电平，如果结果大于0.5v则输出为1，如果小于0.5v输出为0，从6.3175ns时刻开始，每1tck测量一次并输出结果」= 提需求，未给根因 ✓
- **U#2 (msg4)**「tck的周期是166.6666ps，测量40个点」= 参数补充（提需求）✓
- **U#3 (msg34)**「再加上dnnor，dnnef，dnnof三个的测量脚本，与dnner相同即可」= 扩展需求 ✓
- **U#4 (msg64)**「测量D<0>分别在6.2222ns，以及后面每隔999.96ps的高低电平，测量8次，格式与DNNER类似，并应用到D<1>-D<23>」= 扩展需求 ✓
- **U#5 (msg82)**「.measure tran DNNER_S0_v FIND v(DNNER) AT=6.317500n / .measure tran DNNER_S0 PARAM='if(DNNER_S0_v>0.5, 1, 0)' 这里第二行的语法可能有些问题，结果会报error」= **给根因（语法错误）** → 不进 prompt（A-faithful 选轮规则）。但金标准含此修复：PARAM='if(...)' → PARAM='(...)'。
- **U#6-U#11 (msg106+)** = 后续 parse_mt0 / format_dnn_compact / make_table 等解析排版需求（与本 case 的「生成 .measure 语句」核心交付无关，本 case 聚焦 U#1-U#4 的生成器）。

## 金标准（on-disk /home/curryxu/gen_meas.py，完整闭环）

读 measure.sp 保留前 22 行原始测量，按 group/signal/point 生成：
- `.measure tran <sanitized_sig>_S<i>_v FIND v(<orig_sig>) AT=<t,6dp>n`
- `.measure tran <sanitized_sig>_S<i>  PARAM='(<meas_name>_v > <threshold>)'`
- `D<k>` 测量名转义为 `Dk_S<i>`（去尖括号），FIND v() 仍用原始 `D<k>`
- Block1: DNNER/DNNOR/DNNEF/DNNOF × 40pts @ 6.3175ns + 166.6666ps
- Block2: D<0>..D<23> × 8pts @ 6.2222ns + 999.96ps
- 关键修复（U#5）：`PARAM='if(X>0.5,1,0)'` → `PARAM='(X > 0.5)'`（HSPICE PARAM 表达式不接受 if() 三元，但接受布尔比较式，结果 1/0）

## 资产获取
- on-disk `gen_meas.py` 完整（.75 ssh 10.129.2.10 cat，8454B → 同金标准）
- on-disk `measure.sp` 前 4000B（含样例注释 + DNNER 块起始）→ 重建前 22 行样例 deck 作 A 资产 `measure_template.sp`
- `/rundata` / `/proj/m2701/...` 仿真结果权限拒（非 owner），从 trace read_files tool_results 重建 a_config.json

## case
- **id**: EDA-Eval-DesignFlow-MeasTranSamplerGen-001
- **domain/track/level**: spice_sim / A-faithful / L1
- **k=14**：check.py 14 独立断言 (a-n)，3 hidden B configs (b1/b2/b3 结构差异)
- 自验：ref PASS 14/14 + 3neg FAIL (stub/nochange/wrongthr) + §4.9 三假 FAIL (empty/print-expected/core-deleted)
- byte-sync sha: 2d736057588edb23aa4830204066731cde82638cded53a4b4682ae7005307302
