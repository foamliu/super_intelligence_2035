# Deep-read: 1792720528359_2tuxj — CTLE transient eye-diagram characterization

- **trace**: `1792720528359_2tuxj` (kaixuanx @ hfeg0pkn001, mc=91, deepseek-v4-flash, 186 msgs)
- **case shipped**: `EDA-Eval-DesignFlow-CTLEtranChar-001` (spice_sim, B档 synthesized, L2, k=16) — EDA-Eval-DesignFlow_B.jsonl line 34
- **user T0**: 「我设计了一个CTLE电路，仿真激励和网表都在这个文件夹里，我已经仿真了CTLE的AC性能ctle_act_ind.sp，现在我想仿真相关的瞬态性能ctle_act_ind_tran.sp，我需要你帮我总结一下需要仿真的各项性能指标，并帮我重新写一个仿真脚本」

## Real task

kaixuanx 设计了 CTLE_active_ind（DDR RX 均衡器，NMOS 差分对 + R||C 源简并实现"有源电感"式高频 peaking）。AC 表征已跑完（`ctle_act_ind.sp`，TT/25C，VDD=0.8V，5Gbps，peak_gain=+2.51dB @ 2.5GHz）。现要做**瞬态表征**。要求：总结需仿真的瞬态性能指标 + 重写仿真脚本。

## Real agent tool chain (186 msgs)

1. `list_allowed_files` / `read_files` — 读 ctle.sp / ctle_act_ind.sp / ctle_act_ind_tran.sp（旧瞬态网表）
2. `editor` — 写 ctle_act_ind_tran_v2.sp（重写瞬态 deck）
3. `run_approved_command` — 真跑 HSPICE V-2023.12-SP1-1
4. 反复踩坑 → 修正 → 重跑

## Key insight (核心陷阱，烤进 check.py 条件 [p])

**HSPICE 伪随机源是 `LFSR(...)` 不是 `PRBS(...)`。** kaixuanx 第一版用 `PRBS(...)` 激励，HSPICE 报：
```
**error** ... Undefined parameter or function definition 'prbs'
***** job aborted
```
改用 `LFSR(amp_low amp_high 0 trin trin data_rate prbs_seed [15,14])` 后跑通。

LFSR 语法要点：
- `LFSR(vlow vhigh tdelay trise tfall rate seed [taps])`
- taps 必须**内联字面**（如 `[15,14]`），不能作为 `.param` 字符串传入（HSPICE 不展开）
- 差分两路用互补电平：`VINP ... LFSR(amp_low amp_high ...)` / `VINN ... LFSR(amp_high amp_low ...)`

## Final deliverable (trace)

`ctle_act_ind_tran_v2.sp`（7803 bytes，从 hfeg0pkn001 fetch）—— 差分 LFSR PRBS 激励 + `.MEAS TRAN` 眼图/共模/时序/过冲/功耗。

## Portable synthesis (B档)

foundry PDK 不可移植 .75 → 取可复现子技能：
- 便携 level-1 CTLE 子电路（NMOS diff pair M1/M2 + R||C 源简并 Rs/Cs + PMOS 负载 RL + Itail 尾管，**无 foundry 依赖**，corner.lib = level-1 NMOS `.MODEL LEVEL=1 KP=120u VTO=0.45 LAMBDA=0.05`）
- 差分 LFSR PRBS 激励 + `.MEAS TRAN` 全套瞬态度量 + HSPICE 真跑 + `.mt0` `$DATA1` 文本解析 + `tran_report.json`

## .75 HSPICE 排雷

1. CTLE subckt 用 GLOBAL `.param W/L/RL/Rs/Cs/CL/Itail`，**不能** `PARAMS:` 上 X1 行：
   - `.SUBCKT CTLE INP INN OUTP OUTN VDD VSS`（无 PARAMS:）
   - `X1 INP INN OUTP OUTN VDD VSS CTLE`（无 PARAMS:）
   - 否则 HSPICE 报 `Definition of model/subckt 'params:' is not found`
2. LFSR taps inline 字面 `[15,14]`，不能 `.param` 字符串
3. level-1 NMOS corner.lib：`.LIB tt / .MODEL nmos NMOS LEVEL=1 KP=120u VTO=0.45 LAMBDA=0.05 GAMMA=0.4 PHI=0.6 NSUB=1e16 / .ENDL tt`，`.lib 'corner.lib' tt` 加载
4. .mt0 `$DATA1` 解析：header 行后列名行（4 名/行）+ 数据行（4/行，科学计数法），`temper`/`alter#` 是尾列需跳过

## A/B ground truth (.75 真跑)

| | vdd | W | L | RL | Rs | Cs | CL | Itail | rate | swing | eye_amp | pwr_avg | outcm_avg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A | 0.8V | 2u | 0.18u | 2k | 2k | 80f | 10f | 100u | 5Gbps | 0.2 | 0.4214V | 160uW | 0.6123V |
| B | 1.0V | 3u | 0.15u | 1.5k | 3k | 50f | 15f | 150u | 8Gbps | 0.25 | 0.571V | 300uW | 0.787V |

A/B 全异 >25%（eye_amp 差 35%，pwr 差 87%）→ 跨输入守卫成立。

## check.py 16 条断言 (a-p)

a zip含ctle_tran.py+tran_report_A · b py_compile · c 提交vs fresh A一致(防造假>8%发散) · d 14必需键非NaN · e A eye_amp±5%ref · f A差分眼双极打开(vmax>0,vmin<0) · g A eye_mid≈0(<5mV) · h A眼对称(|vmax|-|vmin|<5mV) · i A outcm_avg±5%+合理范围(0.25..0.95)*VDD · j A pwr_avg±5%+>0 · k 候选B exit0出报告 · l B eye_amp±5%ref(跨输入) · m B pwr_avg±5%ref · n B eye_amp与A差>5%(防硬编A) · o B pwr_avg与A差>5%(防硬编A) · p deck用LFSR非PRBS源(核心陷阱)

## .75 negative_selftest（~3min 一把过）

ref **PASS 16/16** + 5 neg 全 FAIL(NEG_RC=1，互异条件集)：
- naive_empty → b,c,d,e,f,i,j,k,l,m,p（空壳/None 度量）
- naive_hardcode_a → l,m,n,o,p（硬编 A，跨输入守卫 + LFSR 缺失击穿）
- naive_print_expected → e,i,l,n,p（伪造 A 值不匹配 ref + 无 LFSR）
- naive_prbs → c,d,e,f,i,j,l,m,p（真跑但 PRBS() 源 → sim abort，全 None，[p] 直接命中 `PRBS(`）
- naive_fabricate → c（真跑但谎报 tran_report_A 与 fresh 不一致）

§4.9 三假（空壳/print-expected/真跑谎报）全 FAIL。

## 本轮踩到并修复（重要）

1. **ref solver `ctle_tran_ref._resolve` 只查 cwd/script-dir**，找不到 `assets/ctle.sp` → check.py `ref_metrics` 必须显式从 ASSETS copy ctle.sp+corner.lib 进 `_ref_A`/`_ref_B` dir。否则真实 eval 在 `reference/CASE` 布局下 ref 全 None → 全 crash。**这是 check.py 与 ref solver 解耦的关键**。
2. `pct()` 加 None 守卫（返回 9e9）；f/h/i/j 加 None 守卫防 crash；main() 包 try/except 把 crash 转成 `fail("?")` —— grader 永不裸 crash。
3. .75 selftest 布局须镜像 repo：check.py 在 `selftest/reference/CASE/`，assets 在 `selftest/assets/CASE/`，则 `HERE/../../assets/CASE` 解析对（flat 布局 `selftest/check.py` 会解析到 `<wd>/../assets` 错位）。

## Distinct vs 已有 shard B cases

NmosAgeChar=NMOS Vtlin/Idlin/Idsat · VihTripTune=VIH DC trip 调优 · OtaAcReport=WaveView AC · TaperBufOpt=buffer DOE PDP · CTLEAC/CTLESpec=CTLE AC · SubcktExtract=网表解析 · Tr0TrTfMeas=.tr0 tr/tf · PVTalterChar=多 alter PVT · Sram6tDcChar=SRAM DC · InvOptSpec=反相器优化 · Vcc2scTranGen=regulator tran · VwlpRefDeckSet=多分析 deck-set · AlterDeckSplit=.alter 拆分 · PFDdeadZone=dead-zone sweep · DummyMeas=.measure 提取 · PowerFill=功耗填充 · SimLibIdx=仿真库索引 —— **本条 = CTLE 瞬态眼图（LFSR PRBS 差分激励 + .MEAS TRAN eye/CM/timing/slew/overshoot/power + .mt0 解析），shard B 首个瞬态眼图 case**。
