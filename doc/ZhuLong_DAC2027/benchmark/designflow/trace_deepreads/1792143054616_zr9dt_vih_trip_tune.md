# Trace Deepread — 1792143054616_zr9dt (jasminej / hfeahpc505, mc=180)

- **session**: `/home/jasminej/.cline/data/sessions/1792143054616_zr9dt/1792143054616_zr9dt.messages.json` (762 KB / 183 msgs)
- **user**: jasminej (NEW for shard B; spice_sim 域)
- **tools** (summary.tsv): 764 hspice + 779 netlist + 402 schematic + 18 calibre（真跑 HSPICE tran/DC VIH 扫频调优）
- **target case_id**: `EDA-Eval-DesignFlow-VihTripTune-001` (spice_sim, B档 synthesized, L2/L3, track faithful)
- **status**: ⚠️ IN-PROGRESS（合成未完成）— 便携电路 90% 就绪，需 1 处极性/measure 修正后即可建 case。**下轮第一件事：继续本条交付，不要 next 新 trace。**

## T0 (idx 0) — 用户首条逐字原文（A-档候选）

```
<user_input mode="act">这是我的testbench,帮我修改网表中DfeTop6M6V2网表中MP28/23/10/3的尺寸（在现有尺寸附近微调），使得输出的csv文件中从0到1（>0.8）的翻转点在vih=170上，并且使得=1/2/3的翻转点结果尽可能接近
--- Attached: 05_VIH_ttnvnt_LP6_0.sp ---</user_input>
```

**A-档合规判定**: 纯需求轮（调 4 个 PMOS 尺寸 → CSV 翻转点落到 vih=170 + 3 个 alter 翻转点尽量接近），🚫 无根因、🚫 无修复方案 → 合格 A-档。verbal "=1/2/3 的翻转点" = 3 个 .alter 条件（DFE 抽头/状态）各自的 0→1 翻转点。

## 真实流（trace 内）

1. 用户给 testbench `05_VIH_ttnvnt_LP6_0.sp`（VIH 扫频 0.165–0.176V，12 点/alter，3 个 .alter），目标翻转点 vih=0.170V。
2. agent 读 DfeTopM6V2.net / .inst（`/rundata/dscqa/V0_LP6/.../netlist/amap/`），定位 MP28/23/10/3，设 work 目录，写 apply_widths.py（按 `XMMP28=<w>` 改 netlist 宽度）。
3. 真跑 HSPICE V-2023.12-SP1-1（先试 finesim V-2023.12-1，LD_PRELOAD libstdc++ 冲突 → 切 hspice）。baseline `hspice_out.mt0.csv` 格式：
   ```
   $DATA1 SOURCE='PrimeSim HSPICE' ...
   vih,result,temper,alter#
    1.650e-01,-3.323e-04, 4.500e+01,1
    ...
    1.740e-01, 1.000e+00, 4.500e+01,1   ← alter1 翻转 @ 0.174
    1.730e-01, 1.163e+00, ... ,2         ← alter2 翻转 @ 0.173
    1.740e-01, 0.880e+00, ... ,3         ← alter3 翻转 @ 0.174
   ```
4. `analyze.py`：按 alter 分组，逐点判 `result>0.8` 为 1，找 0→1 跳变点 vih。baseline：alter1=174mV, alter2=173mV, alter3=174mV（目标 170mV，偏高 ~4mV；3 alter 已接近 1mV 内）。
5. agent 写 launch_edit.run.sh（apply 4 宽度 → hspice 后台 → poll）跑 exp1（MP28/23/10/3 各 +20%），但环境反复卡（LD_PRELOAD/libstdc++/后台进程被中止）。用户 "中止把" → agent 给总结。**trace 未达调优终态**（没拿到 tuned widths 的最终 CSV），但任务定义+方法链完整可复现。

## 便携化设计（B档 synthesized，自包含 level-1 MOS，.75 HSPICE 可跑）

**核心子技能** = VIH DC 扫频 → 解析 mt0.csv → 每 alter 找 0→1 翻转点 → 调 4 个宽度使翻转点落目标 + 3 alter 翻转点尽量接近（DFE-state spread 最小化）。

**电路**（NMOS-input diff pair + PMOS current-mirror load，4 个可调宽度 = 2 NMOS 输入 + 2 PMOS 镜像负载；trace 的 MP28/23/10/3 映射为 4 个 sizing knobs）：
```
MN28 neta vih nett 0  nmod W=wn28   $ 输入(vih侧)  — 可调
MN23 netb vref nett 0 nmod W=wn23   $ 输入(vref侧) — 可调
MP10 netb netb vdd vdd pmod W=wp10  $ PMOS diode 负载 — 可调
MP3  neta netb vdd vdd pmod W=wp3   $ PMOS mirror 负载 — 可调
MNb  nett vbias 0 0  nmod W=wnb     $ 尾电流（fixed）
idfe neta 0 idfe                    $ DFE 反馈电流（per-alter，spread 驱动）
out = netB → 2 CMOS inverter        $ 取 netB 使 out 随 vih↑ 而 0→1（升）
.model nmod nmos level=1 kp=120u vto=0.5 lambda=0.05 gamma=0.4 phi=0.6 nsub=1e16
.model pmod pmos level=1 kp=50u  vto=-0.5 lambda=0.05 gamma=0.4 phi=0.6 nsub=1e16
.dc vih 0.45 0.65 0.002 ; 3 .alter: idfe=-10u/0/+10u
.measure dc vtrip cross v(out)=0.8  $ 用 cross（非 rise）捕双向
```

**.75 真跑验证（本轮）**：
- ✅ 收敛（vbias=0.70，尾电流≈0.27mA；vbias=0.30 时 MNb 截止→死锁，已修）。
- ✅ sharp 翻转：alter1(idfe=0) out 在 vih≈0.525 处 high→low 跃变（netA 路径，**falling**）。
- ⚠️ **待修 2 处**（已定位，~10min 工作量）：
  1. **极性**：当前 out 取自 netA→2inv，随 vih↑ 是 **high→low（falling）**；trace 要 0→1（rising）。→ 改取 **netB→2inv**（netB 随 vih↑ 而升）即得 rising。或 netA→3inv（奇数级）。
  2. **measure**：`when v(out)=0.8 rise=1` → 改 `cross=1`（或极性修后 rise=1 即可）。
  3. neta 在高 vih 时被 idfe 拉到 -95mV（越界）→ idfe 改注入 netB 或限幅；或在 netB 取输出规避。
- ✅ 物理符合预期：trip≈vref(0.5) 附近，随 idfe 平移；spread = idfe_range/gm，gm∝√(Itail·W/L) → 调 wn28/wn23 改 spread，调 wp10/wp3+wnb 改绝对 trip。**4 宽度耦合优化结构成立**（center vs spread 可独立调控）。

## case 计划（下轮直接执行）

- **assets/可见 A**：`slice_A.sp`（baseline 宽度 wp10=1.5u/wp3=1.5u/wn28=2u/wn23=2u，trip 偏高 ~0.525 vs 目标 0.500）+ `baseline.mt0.csv`（A 的 GT）+ `task_brief.md`（≤3 行：交付接口 + 文件位置，不写"做什么"）+ `analyze_spec.md`（mt0.csv 格式 + 翻转点定义 result>0.8 + 3 alter + 目标 vih=0.500 + closeness 容差）。
- **assets/hidden/B**：`slice_B.sp`（不同库参数：kp_n=90u/kp_p=40u/vto±0.45/vbias=0.68，baseline trip≈0.540，目标仍 0.500，spread 不同）+ `baseline_B.mt0.csv` + hidden_manifest.json。B 的 best-tune 与 A 全异（跨输入守卫）。
- **reference/**：`vih_tune_ref.py`（解析 mt0.csv → 找 trip → DOE/网格搜 4 宽度（每设计真跑 HSPICE 子进程）→ 选 trip@target + min spread 的 best → 输出 widths.json + tuned.mt0.csv + analysis.json）+ `reference_submit.zip`。
- **check.py（≥12 条断言 a-?）**：
  - (a) zip 含 3 文件 (widths.json/tuned.mt0.csv/analysis.json)
  - (b) widths.json 4 键 wn28/wn23/wp10/wp3 且为正数
  - (c) 4 宽度与 baseline 不同（非平凡）
  - (d) tuned.mt0.csv ≥3 alter 块且每块≥10 vih 点
  - (e) analysis.json 含 trips[3]/target/spread/best_widths
  - (f) subprocess 独立重跑候选 vih_tune.py on 隐藏 B deck → 真 HSPICE 出 .mt0.csv（防 print-expected）
  - (g) B 的 tuned trip 与 B target 偏差 ≤3mV
  - (h) B 的 3 alter trip spread ≤2mV
  - (i) 候选 widths 应用于 B deck 后重跑 trip 与候选报告的 tuned trip 一致（防造假数据）
  - (j) 跨输入守卫：B best_widths ≠ A best_widths（硬编 A 答案在 B 上 trip 偏差 >5mV 必败）
  - (k) ref 参考解 on A：trip@0.500±2mV + spread≤2mV（ref 真 PASS）
  - (l) trip 单调性：每 alter 的 result 随 vih 单调 0→1（防乱序/造假）
  - (m) measure 用 cross/正确极性（候选 deck 含可解析 trip）
  - (n) ≥3 个随机种子重跑结论一致（随机化）
- **negative/（≥5）**：naive_empty→(a) · naive_hardcode_A→(j)(g) 跨输入 · naive_no_rerun(print expected trip)→(f)(i) · naive_baseline_unchanged→(c)(g) · naive_wrong_polarity(rise on falling)→(m)(h) · + §4.9 三假 (a)(b)(c)。
- **k 条断言** = check.py 标签数（≥12），test_rationale 写 `12 条断言：①zip3文件 ②4宽度正数 ③非平凡 ④mt0结构 ⑤analysis字段 ⑥子进程真跑 ⑦B trip命中 ⑧B spread小 ⑨widths复现一致 ⑩跨输入守卫 ⑪ref-on-A PASS ⑫trip单调 ⑬极性正确 ⑭随机化一致`（k=14，对账 k_rationale=k_check≥8）。
- **自验**：.75 negative_selftest.py 一把过（ref PASS + 6 neg FAIL + §4.9 三假 FAIL）。

## distinct vs 已有 B case

Sram6tDcChar=SRAM 6T DC 表征(被动测) · InvOptSpec=单反相器 W/L 网格 · TaperBufOpt=多级 buffer DOE+PDP · OtaAcReport=WaveView AC 度量提取 · PFDdeadZone=PFD dead-zone sweep · CTLESpec/OpampACSpec=AC spec 合规 · Vcc2sc=regulator tran/PVT · VwlpRefDeckSet=多分析 deck-set · **本条独特点=VIH DC 扫频翻转点 + 4 宽度调优到目标 + DFE-state spread 最小化（center-vs-spread 耦合优化）** —— shard B 此前无 optimization-to-target-with-closeness-constraint 子技能。

## 教训（本轮）

1. `.75` HSPICE level-1 model 必须给 `nsub=1e16 phi=0.6 gamma=0.4`（缺 nsub → "nsub <= ni" abort）。
2. `.param x=2.0u` 在 V/I source value 用 `{x}` 会 "syntax error at {x}" → 用裸参数名 `W=wp28 L=lp`、`idfe neta 0 idfe`；V 源直接写常量 `vdd 0 1.0`。
3. NMOS tail current source `MNb gate=vbias` 需 vbias > Vto(0.5) 才导通；vbias=0.30 → 尾电流截止 → diff pair 死锁（netA/netB 常值、out 钉死）。
4. PMOS-input diff pair 在 vih≈VDD/2 区不在好工作点（PMOS 需 gate<源-0.5）；NMOS-input diff pair 在 vih≈0.5 区正常 → 选 NMOS-input。
5. diff amp 输出极性：netA 随 vih↑ 而 ↓（falling），netB 随 vih↑ 而 ↑（rising）→ 取 netB→偶数 inv 得 rising 0→1。
6. `rm -f slice_A.*` 会连同 .sp 一起删 → hspice "No valid input file"。只 rm out_* 。

## 2026-11-03 09:5x 补充：电路验证结果 + 近完成 recipe（parked，下轮可直接交付）

**状态**：parked（idfe-spread 机制不洁净，需简化为 single-alter；电路核心已验证可用）。

### 已验证可用的电路（.75 HSPICE V-2023.12-SP1-1 真跑确认）
- **偏置必须用 MNb NMOS 尾管（vbias=0.7, wnb=2u），🚫 不能用理想 Itail 源**（Itail 把 neta/netb 拖到负值，diff pair 死锁）。
- **分析必须用 .dc Vvih 扫源（🚫 .dc vih——会扫不存在的 param variable；🚫 .tran ramp——init 态乱，measure 2/3 failed）**。
- **输出取 neta→1inv（neta 随 vih↑而↓，1 inv → out 上升 = rising 0→1，measure when v(out)=0.8 rise=1 成功）**。
- baseline(wn28=wn23=2u, wp10=wp3=1.5u, wnb=2u, vbias=0.7, vref=0.5, vdd=1.2) → **vtrip=0.5007（已命中 target 0.500！）**
- 增大输入对 wn28/wn23 → trip 不变（仍 0.5003），说明 trip 由 vref + PMOS 负载 + 尾流决定，wn28/wn23 改 gm/灵敏度。
- level-1 model 必须给 nsub=1e16 phi=0.6 gamma=0.4。
- .measure 输出落在 .ms0/.ms1/.ms2（不是 .mt0），格式 $DATA1 ... vtrip temper alter#。

### ❌ idfe-spread 机制不可用（已穷举验证）
- idfe 注入 **neta**：正 idfe（sink neta）即使 0.1uA 也把 trip 压到 <0.30（out 起始就 high，measure failed）；负 idfe 仅 +10~40mV。极端不对称。
- idfe 注入 **netb**：正 idfe +41mV，负 idfe ≈0（netb 被 MP10 diode 钳位）。仍不对称。
- 根因：diff pair gm 小（尾流~10uA），idfe 与支路电流可比，单边拉拽主导；netb 被 diode-PMOS 钳位。spread = idfe_range/gm 公式在此拓扑不成立。

### ✅ 下轮 recipe（简化为 single-alter VIH trip 调优，仍是 faithful L2 子技能）
**case 核心**："调 4 宽度（wn28/wn23/wp10/wp3）使 VIH DC 翻转点命中 target，且在隐藏 B（异库参数）上同样命中"——丢掉 3-alter/spread（trace 的 "=1/2/3 接近" 不可移植），保留 trace 核心 "改 4 PMOS 尺寸使翻转点落 vih=X"。

1. **4 宽度独立性验证**（下轮先跑 ~5min）：固定 wn28=wn23=2u，扫 wp10=wp3∈{1,1.5,2,3}u，看 trip 是否随之移动（若不动，4 宽度非独立可调→换 trace）。
2. **check.py 重写**（基于已验证 deck）：gen_deck 用 MNb 尾 + .dc Vvih + neta→1inv + .measure when v(out)=0.8 rise=1；parse .ms0；条件 ≥8：(a)zip 含 vih_tune.py (b)py_compile (c)cand on A 出 widths 4 正键 (d)cand on B 出 widths 4 正键 (e)widths_B≠baseline_B (f)独立重跑 B trip 命中 target±6mV [KEY] (g)cand tuned.csv 与独立重跑一致±2mV (h)widths_A≠widths_B (i)独立重跑 A trip 命中 (j)cand_B ≥10 .sp (k)analysis.json n_designs≥10 (l)trip 单调 (m)deck 用 .dc Vvih 扫源 (n)≥3 种子一致。
3. **params_A.json**：vdd=1.2/vref=0.5/vbias=0.7/kp_n=120u/kp_p=50u/vto±0.5/LL=0.5u/wnb=2u/baseline{wn28=wn23=2u,wp10=wp3=1.5u}/sweep[0.35,0.65]/step=0.001/target=0.500。
4. **params_B.json（异库跨输入）**：vdd=1.1/vref=0.48/kp_n=90u/kp_p=40u/vto±0.45/LL=0.6u/vbias=0.68/baseline{wn28=wn23=3u,wp10=wp3=2u}/sweep[0.33,0.63]/target=0.500。B best_widths≠A。
5. **vih_tune_ref.py**：grid 搜 wp10=wp3∈{1,1.5,2,2.5,3}u × wn28=wn23∈{1.5,2,2.5,3,4}u = 25 设计，每设计 .dc Vvih 跑 trip，选 |trip-target| 最小 → widths.json + tuned.ms0.csv + analysis.json。
6. **negative ≥5**：naive_empty→(a) · naive_hardcode_A→(f)(h) · naive_no_rerun→(g) · naive_baseline_unchanged→(e)(f) · naive_no_search→(j)(k) · + §4.9 三假。
7. **自验**：.75 negative_selftest.py（ref PASS + 5 neg FAIL + §4.9 三假 FAIL）。

### 教训
- 理想电流源 Itail 在 diff pair 里拖负节点；用 NMOS 尾管 MNb 自限。
- .dc 必须扫源（.dc Vvih），扫节点名（.dc vih）创建 phantom param variable。
- .tran ramp 测 DC trip 受 init 态影响（2/3 alter failed）；.dc sweep 才稳。
- idfe 单边注入 diff pair 输出节点 → 极不对称；spread-minimization 需对称结构或舍弃。
- 4 宽度独立性需先验证（wp 改 trip、wn 改灵敏度），否则 case 不成立。
