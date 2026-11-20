# trace_deepread — sid 1794471129064_qdpsc · SpiceMeasInject

- **session**: 1794471129064_qdpsc.messages.json
- **user**: jiangbaol @ hfeg0pkn004 / 10.129.2.13
- **mc**: 146 (kw: netlist/schematic/analog dominant, d_ratio 0.88)
- **nmsg**: 233 / nturns: 8 user turns
- **domain**: schematic_netlist
- **trace source**: ssh_eda_search_20261113_131349/summary.tsv

## 用户意图（U3 = clean produce-task，本轮采用）

U0-U2 = error debug / option how-to / probe fix Q&A（不进 case）。

**U3 原话**：
> /proj/m2701/.../004_onlySlicer_delay_m2701.sp
> 在该.sp中添加measure语句，实现如下功能：
> 1.测量XI7整体电源功耗,采样时间与.sp内其他功耗时间一致;
> 2.测量1.53后，ldfedata第一个下降沿达到vvdd-0.36的时刻；
> 3.测量2.时刻时outn_stg1与outp_stg1的电压
> 生成的.sp放在原.sp路径下...

U4-U7 = 后续 sizing sweep（需 live Finesim 迭代，不可 portable，不进 case）。

## 助手真实工具链（U3 段）

1. `run_approved_command` python-runner grep 现有 `.meas`/`.probe`/power 行 → 定位 213-222 行既有 `Cur_slicer_latch_avg AVG ... From='5n-32*UI' TO='5n'`（采样窗口来源）
2. `read_files` 210-285 + 155-210 → 确认 `.tran 1p 5n`、`vcc!` 由 `vvcc` 源、XI7 supply pin = `inh_vcc`、`LDFEDataEr` 是顶层 net、`outn_stg1/outp_stg1` 在 `XI7.XI_DqIbSAHFM6IP.` 下
3. `editor` 写 `cp_sp.sh` → `run_approved_command` 复制 .sp 到 `/home/jiangbaol/004_onlySlicer_delay_m2701.sp`（281 行，沙箱 /proj 只读）
4. `editor` 在 AVG measure 行后插入 measure block（marker 注释 `* ZL-added measure block`）
5. `read_files` 复核 → 二次 `editor` 把 power measure 改成 probe-alias→AVG 习惯（`XI7_vcc_cur = 'isub(XI7.inh_vcc)'` + `.meas I_XI7_vcc_avg AVG XI7_vcc_cur ...` + `.meas P_XI7_vcc_avg AVG 'VVDD*XI7_vcc_cur' ...`）
6. 最终 304 行，给出 cp 命令

## 真实产物（measure block，最终态）

```spice
* ============================================================================
* ZL-added measure block
* [1] XI7 overall power-supply consumption (from vcc! / XI7.inh_vcc)
*     sampling window identical to the other power/current avg measures above
.probe XI7_vcc_cur = 'isub(XI7.inh_vcc)'
.meas tran I_XI7_vcc_avg  AVG  XI7_vcc_cur           From='5n-32*UI'  TO='5n'
.meas tran P_XI7_vcc_avg  AVG  'VVDD*XI7_vcc_cur'    From='5n-32*UI'  TO='5n'
*
* [2] time when ldfedata (=LDFEDataEr) first falling edge reaches vvdd-0.36, after 1.53ns
.meas tran t_ldfe_first_fall  WHEN  v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
*
* [3] outn_stg1 / outp_stg1 voltage at the [2] instant
.meas tran V_outn_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outn_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
.meas tran V_outp_stg1_at  FIND  v(XI7.XI_DqIbSAHFM6IP.outp_stg1)  WHEN v(LDFEDataEr)='vvdd-0.36'  FALL=1  FROM=1.53n
* ============================================================================
```

## SPICE .measure 语法要点（HSPICE/Finesim）

- 功耗：先 `.probe <alias> = 'isub(<inst>.<supply_pin>)'` 再 `.meas tran <I_avg> AVG <alias> From='<F>' TO='<T>'` + `.meas tran <P_avg> AVG '<vdd>*<alias>' From='<F>' TO='<T>'`
- 边沿时刻：`.meas tran <name> WHEN v(<signal>)='<threshold>' FALL=1 FROM=<after>`（FALL=1=第一个下降沿）
- 边沿时刻电压：`.meas tran V_<sig>_at FIND v(<sig>) WHEN v(<signal>)='<threshold>' FALL=1 FROM=<after>`（复用 [2] 的 WHEN 条件 = "在 [2] 时刻"）
- 采样窗口来源：从既有 `.meas ... AVG ... From='...' TO='...'` 提取，**不可硬编码**

## 合成计划（case_id: EDA-Eval-DesignFlow-SpiceMeasInject-001）

**子类**：netlist-text-transform（SPICE deck measure 注入），与 r622 ulvt / r624 capfit / r626 spf-coupling 同族但新增「measure 语句语法生成 + 窗口继承」维度。

**SUT**：`spice_meas_inject.py`（纯 stdlib CLI `python3 spice_meas_inject.py <in.sp> <out.sp> <spec.json>`）

**spec.json 格式**：
```json
{
  "power": {"instance":"XI7","supply_pin":"inh_vcc","vdd":"VVDD","alias":"xi7_vcc_cur"},
  "edge_time": {"signal":"LDFEDataEr","threshold":"vvdd-0.36","after":"1.53n","name":"t_ldfe_first_fall","edge":"falling"},
  "voltage_at_edge": {"signals":["XI7.XI_DqIbSAHFM6IP.outn_stg1","XI7.XI_DqIbSAHFM6IP.outp_stg1"]}
}
```

**visible A** = sample_A.sp（采真实结构：.tran/.param/.probe/.meas AVG From='5n-32*UI' TO='5n'/XI7.inh_vcc/LDFEDataEr/outn_stg1/outp_stg1）+ spec_A.json
**hidden B** = sample_B.sp（XTOP.vdd_pin/VDD/DataPulse/vdd-0.5/2.5n/XTOP.XSA.sub.outp,outn/window From='10n-64*UI' TO='10n'/falling）+ spec_B.json
**hidden C** = sample_C.sp（XSENSE.vcc_supp/VCC/SenseIn/vcc-0.25/0.8n/XSENSE.XAMP.diff_outp,diff_outn/window From='8n-16*UI' TO='8n'/**rising**→RISE=1 反硬编码 FALL）+ spec_C.json

**gotcha**：① 窗口继承（不可硬编码 5n-32*UI）② probe-alias→AVG 习惯 ③ WHEN...FALL/RISE=1 FROM=after 语法 ④ FIND...WHEN 复用 [2] 条件（"在[2]时刻"= 同 WHEN）⑤ 边沿方向 falling/rising 映射 FALL/RISE=1（C 用 rising 反硬编码 FALL）⑥ 插入位置 = AVG measure 行后

**check.py 16 cond a-p**（内嵌独立 oracle：自解析 B/C .sp 提取窗口 + 自构造期望 measure 行集合，非文本相似）：
a zip合法仅1.py / b py_compile / c 源码不硬编码 A 字面量(XI7/inh_vcc/LDFEDataEr/5n-32*UI/1.53n/vvdd-0.36) / d B exit0+out.sp 创建 / e B 原 .sp 行保留(非插入行 verbatim) / f B power: .probe alias='isub(XTOP.vdd_pin)' / g B power: .meas I_avg AVG alias From=B_window TO=B_window / h B power: .meas P_avg AVG 'VDD*alias' From=B_window / i B window 匹配 B 既有 AVG 窗口(10n-64*UI/10n) / j B edge: .meas name WHEN v(DataPulse)='vdd-0.5' FALL=1 FROM=2.5n / k B volt-at-edge: 每 sig .meas V_<base>_at FIND v(sig) WHEN v(DataPulse)='vdd-0.5' FALL=1 FROM=2.5n / l B 插入位置 = AVG measure 行后 / m C 跨输入: C power 用 XSENSE.vcc_supp/VCC 非 B/A / n C 反硬编码: C out.sp 不含 XI7/inh_vcc/LDFEDataEr / o C 边沿方向: .meas ... RISE=1（rising→RISE 非 FALL） / p 鲁棒: spec 缺 power 段 → 非零退出或跳过

**4 neg**：empty_shell→d / print_only(硬编码 A block)→c+n / hardcode_a(总输出 XI7 block)→f(B 无 XTOP alias) / core_removed(读 spec 但不插入)→e(无新 measure 行) 或 g

**§4.9 三假**：empty/print/core 全 FAIL

**k_rationale = k_check = 16 ≥ 8 ✓**

## 备注

- g860c（jiangbaol 同 user/host，U0-U6 与 qdpsc 完全相同，仅 U7 目标不同）= near-dup，不取（避免 D-as-sink overcount，呼应 discuss r626 ① user+task-signature key）
- U4-U7 sizing sweep 需 live Finesim 迭代（/apps/synopsys/SRB/finesim），不可 portable，不进 case
- 本 case 是 D 域 netlist-text-transform 子类第 8 轮（r620-r630 + r631），新维度 = SPICE .measure 语法生成（前 7 轮为文本筛选/层次/续行/不规则映射/双格式/off-by-one/前缀冲突，本轮 = 测量语句构造 + 窗口继承）
