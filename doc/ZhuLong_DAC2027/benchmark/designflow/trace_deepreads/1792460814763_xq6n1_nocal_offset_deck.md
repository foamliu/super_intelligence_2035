# Deepread: 1792460814763_xq6n1 — comparator offset calibration → no-cal control deck

- **trace**: `1792460814763_xq6n1.messages.json` (yanghao @ hfeg0pkn002, mc=58, 36 msgs, ~ SpiceSim/characterization)
- **keywords**: hspice:113; transistor:46; netlist:69; schematic:44; waveview:9
- **A档选轮合规**: U0 = 纯需求轮（"参照 cal_only.sp 写一个不校准都测量 offset 的 sp 文件，作为对照。即 init 一直为1，开关一直断开，DFF6～0 始终没有时钟触发"）—— 用户未给根因/修复方向 ✓。但 DUT 依赖 foundry PDK（.inc TsCoreComp netlist）+ 100 点 MC bsub → 不可移植 .75 → **B档 synthesized**（子技能忠实，.75 level-1 标定金标准）。

## 真实流（逐轮）
- **U0**: 参照 `cal_only.sp`（TsCoreComp input-offset CALIBRATION，7-bit cap array + post-cal offset measurement via input ramp method）写一个**不校准但测量 offset** 的对照 sp：init 一直为1、开关一直断开、DFF6~0 始终没有时钟触发。
- agent 读 `cal_only.sp`（calibration testbench：comparator core + DFF 控制 7-bit 开关电容阵列 + pass gates + init 复位 + Vip ramp + .measure offset），理解 DUT 结构，创建 `nocal_only.sp`（194 行）：init=1 常置、开关常开、DFF 不时钟 → 直接测 raw comparator offset。editor 写工程目录被 policy 拦 → 经 python-runner 复制到 /proj/ddgoa/.../00_tscomp/nocal_only.sp（9319 bytes）+ runsim 追加注释行。未跑 sim（bsub 100 点 MC，未授权）。
- **U28**（follow-up，不作 A 档任务说明——用户给出修复方向"在触发器输出加复位管子，init=1 时 DFF6~0 先阶跃一次复位到0，之后依次触发校准"）：agent patch_cal_only.py 改 cal_only.sp（226 行）补复位序列。**可另存 hint，不进 prompt**。

## distinct（vs 已有 B characterization case）
GmidLut/NmosAgeChar/CTLEtranChar/VihTripTune/ButterflyCurve/DffSetupHoldChar/ThoxVthExtract/OtaAutoTune/TxRonSize/PVTvarSpecJudge/RcurrDirClassify/SizingSensDiag/Tr0JitterRemeas/CpIcpChar/SlicerSizingOpt/ReadsigAddrTbl —— 全为指标表征 / spec 合规 / 灵敏度 / 波形 forensics / netlist 解析 —— 本条 = **comparator offset calibration testbench → no-calibration control-run deck 改写**（control-signal stimulus rewrite：init/switch/DFF-clock 常置化，保留 .measure offset 方法论 + DUT netlist），shard B 首个「calibration control-stimulus rewrite」case，distinct ✓。

## 便携 reframe（关键）
trace 原走 foundry PDK TsCoreComp + 7-bit cap SAR + bsub MC → 不可移植。保留「校准→不校准对照 testbench 改写」子技能，DUT 用 level-1 Shichman-Hodges **3-inverter comparator**（inv1 sizing 不对称→raw offset，inv2 gain，inv3 buffer）+ 1-bit cal cap（Mcal pass gate，cal_en 控制）+ 3 控制信号（init/cal_clk/cal_en）。.75 HSPICE V-2023.12-SP1-1 标定。

候选 `nocal_deck_gen.py`（CLI <cal_only.sp> <spec.json> <out_dir>：name-agnostic 按 spec 的 net 名定位 Vinit/Vclk/Ven 独立源 → 改写为常量 [init=vdd, clk=0, en=0]，保留 .subckt/Mcal/.measure/Vip ramp → 写 nocal_only.sp + nocal_manifest.json）。

## .75 实测 GT（确定性，已验证）
- **A**（vdda=1.2, vhalf=0.6, inv1 Mp W=2u/Mn W=4u, L=180n, Ccal=10f, ramp 10n）：
  - cal_A.sp offset（含 cal）= **142.36mV**（vtrip_at=742.36mV）
  - nocal_A.sp offset（raw, cal 断开）= **144.71mV**（vtrip_at=744.71mV）
- **B**（vddbx=1.0, vhalfbx=0.5, inv1 Mp W=1.5u/Mn W=5u, L=150n, Ccal=15f, ramp 8n, 全不同 net 名 initb/cal_clkb/cal_enb/ipb/inb/outb/cal_nb/vddb/vssb, subckt cmp_dut_b, model nchb/pchb）：
  - cal_B.sp offset = **234.23mV**（vtrip_at_b=734.23mV）
  - nocal_B.sp offset（待 next round 验证，预计 ~相近 raw 值）
- 跨输入：offset 142 vs 234 = 65% diff ✓；vdd/vhalf/sizing/L/cap/net/model 名全不同 ✓

## 候选 .75 端到端验证（已通过）
1. `nocal_deck_gen_ref.py cal_A.sp spec_A.json nocalA_out` → 写 nocalA_out/nocal_only.sp
2. nocal deck control 行：`Vinit init 0 vdda` / `Vclk cal_clk 0 0` / `Ven cal_en 0 0`（常量，无 pulse/pwl）✓
3. `.subckt cmp_dut` / `Mcal` / `.measure tran vtrip_at ... cross=1` / `.measure tran offset param=...` 保留 ✓
4. `hspice -i nocal_only.sp -o nocalA` → **job concluded**，vtrip_at=744.71mV, offset=144.71mV（not failed）✓

## check.py ≥14 条 a-n（设计，next round 实现）
(a) submit.zip 含 nocal_only.sp + nocal_deck_gen.py
(b) py_compile nocal_deck_gen.py
(c) subprocess 跑 nocal_deck_gen.py B → 产 nocal_only.sp（反 naive_empty/print_expected）
(d) nocal_only.sp 跑 HSPICE → job concluded（judge 独立 rerun，反 fake_core_deleted/no_rerun）
(e) init net 常量（nocal deck 无 `pulse`/`pwl` on Vinit 行）
(f) cal_clk net 常量 0（无 pulse on Vclk 行）
(g) cal_en net 常量 0（无 pwl on Ven 行）
(h) `.measure` offset 语句保留（nocal deck 含 `measure tran` + `offset`）
(i) cmp_dut .subckt 保留（nocal deck 含 `.subckt cmp_dut`，反 naive_delete_dut）
(j) HSPICE 产数值 offset（.lis 含 `offset=` 非 `failed`）on B
(k) offset_B 在合理范围（|offset| < vddbx）+ 匹配 GT ±20%（反 naive_fake_numbers）
(l) 跨输入守卫：judge 重跑 candidate on A → nocalA 产 + A net 名（init/cal_clk/cal_en）出现 + A offset 数值
(m) name-agnostic：B deck 含 B net 名（initb/cal_clkb/cal_enb）无 A net 名泄漏（反 naive_hardcode_a）
(n) 确定性：重跑 B 两次 offset 一致 1% 内

## negatives（≥2 + 3 fakes）
naive_empty / naive_print_expected / naive_no_rewrite（cp cal_B.sp 原样→control 仍 pulse，击穿 e/f/g）/ naive_hardcode_a（硬编 A net 名→击穿 m）/ naive_delete_meas（删 .measure→击穿 h/j）/ fake_core_deleted（删 subckt→击穿 i/d）

## 进度与 DEBT
- **已落盘** `designflow/_wip_nocal_deck/`：cal_A.sp, cal_B.sp, spec_A.json, spec_B.json, nocal_deck_gen_ref.py（bug-fixed：移除 Vin/Vip/Vb 前缀守卫，按 net 名匹配）
- **已 .75 验证**：DUT A/B 跑通 + 候选 A 端到端跑通（rewrite + HSPICE + offset 数值）
- **未完成（DEBT:1，next round 第一件事）**：check.py 14 条 + 6 neg + negative_selftest.py + reference_submit.zip + assets/reference 落 EDA-Flow-Bench repo + 追加 EDA-Eval-DesignFlow_B.jsonl + mark dckp0→no, mark xq6n1 case + 日报 + 清 DEBT:1
- **预算超支原因**：候选 trace 选料耗 ~22min（多台 ssh peek + 排除已评/rejected）+ DUT 调试 3 轮（.model 缺 type → Vinit 被 Vin 前缀守卫误杀 → diff-pair 增益不足改 3-inverter）→ 合成正赛时已超 40min 硬预算 → 诚实记 DEBT:1，WIP 全落盘便于 next round 快速收尾

ledger xq6n1 claimed→deepread（covered 维持 67，deepread 不增 covered），已动 111→112，in-progress 1→2（claim 新增）。
