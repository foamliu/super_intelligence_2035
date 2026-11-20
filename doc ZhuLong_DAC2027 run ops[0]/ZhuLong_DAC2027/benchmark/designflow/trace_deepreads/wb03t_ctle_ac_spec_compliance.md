# wb03t — cwei SpiceAgent CTLE AC spec 合规自检 (spice_sim 域)

## trace 元数据
- session: `1790487462826_wb03t.messages.json` (cwei / hfeg0plg93, mc=691)
- size: 971KB, 400 msgs (sparse 9 substantive user msgs / 252 tool_use: 220 run_commands / 22 editor / 8 read_files)
- 关键字：spice/sim/ctle/.meas/finesim/ncr/peaking；pyAether OA 原理图段（末段 GUI 阻塞，不稳定）
- model deepseek-v4-flash；session 末段 pyAether 卡死（GUI 阻塞），但 Spice 仿真子流完整
- trace-keyword 域 = spice_sim，**实产 case 域 = spice_sim**（CTLE AC spec 合规自检子流）
- 选择理由：spice_sim 域当时最稀（仅 1 case CTLEAC-001），mc=691 中等，trace 含完整 FineSim AC + .meas 解析 + spec 表，可抽“failed-measure→not_met 处理”这一独立可复用子流，与 CTLEAC-001（.op idd 解析）形成互补而非重复。

## 主线（从 9 条 substantive user msg 提炼）
SpiceAgent 入口 → cwei 给 CTLE 设计任务（LPDDR5 DQ RX @6.4Gbps，cl028hkn 28nm）→ 写 `dut_ctle.sp`（source-degenerated 差分对，nlvt_ckt + R‖C degeneration + R load + ideal tail）→ 写 `tb_ctle_ac.sp` / `tb_ctle_tran.sp` → **FineSim AC 仿真** → 解析 `.meas`（dc_g/hf_g/peaking/fpeak/bw/vcm_out/idd）→ 给 spec.md（13 行 spec 表，AC 可测 7 行）→ pyAether 生成 OA schematic（末段 GUI 阻塞，未完成）。

## 关键真实 artifacts
- `dut_ctle.sp` — ctle_a subckt（nlvt_ckt diff pair, w=2.5e-6 l=100e-9 nf=4, rs=200 cs=200f rl=2k itail=1m）
- `tb_ctle_ac.sp` — AC testbench（FineSim, .ac dec 100 1k-10g, .meas dc_g/hf_g/peaking/vcm_out/g_at_1g/bw/idd）
- spec 表 7 行：dc_g[0,6]/hf_g[8,14]/peaking[6,12]/fpeak[2,4.5]/bw[5,—]/vcm_out[0.45,0.65]/idd[—,2.5]

## .75 EDA 栈（实测探明）
- **FineSim**: V-2023.12-1，`finesim -spice -np 4 <deck>`（必须 `-spice` 模式，默认 PRO 模式拒绝 `.ac`，检出 CKTSIMSPICE license）
- **PDK**: `/proj/shdc/models/cl028hkn/cl028hkn_1d05_1d8_v1d1a/hspice/model.sp` lib `TOP_TT_TYP`；wrapper `nlvt_ckt`/`plvt_ckt` 在 `cl028hkn_1d05_1d8_logic_v1d1.l`
- 产物在 `<deck>.log`（不是 `.lis`）；finesim -spice 跑小 CTLE AC ~6s

## .meas 解析要点（本 case 核心契约）
- `<deck>.log` 行形如 `       dc_g= 1.0631e-01` / `         bw=     failed` / WARNING `can't compute 'i(vdd)', measure failed`
- **`.meas ac bw WHEN vdb(...)=dc_g-3 FALL=1`** 在频带内增益未降到 dc_g-3 时返回 `failed`
- **`.meas ac idd AVG i(vdd)`** 在 .ac 下返回 `failed`（AC 分析不给出可信直流电流）
- **失败的 measure 必须报 `not_met`（不是 fail/0/crash）** —— 这是本 case 与 CTLEAC-001 的关键差异点（CTLEAC-001 测 .op idd 解析；本 case 测 failed-measure 语义归类）
- `peaking` 是派生量 = `hf_g - dc_g`（`.meas ac peaking PARAM='hf_g - dc_g'` 直接给值，harness 须能兜底派生）

## 实测 ground truth（独立 FineSim 跑 on .75）
| input | dc_g | hf_g | peaking | vcm_out | g_at_1g | fpeak | bw | idd | overall |
|:--|--:|--:|--:|--:|--:|:--|:--|:--|:--|
| A = tb_a.sp (ctle_a: w=2.5u nf=4 rs=200 cs=200f rl=2k itail=1m vin_cm=0.525 C_load=25f) | 0.10631 | -0.008282 | -0.11459 | 0.50616 | 0.14455 | failed | failed | failed | — |
| B = tb_b.sp (ctle_b: w=5u nf=8 rs=50 cs=100f rl=5k itail=0.5m vin_cm=0.55 C_load=40f) | -25.4331 | -25.1759 | 0.25691 | 0.026751 | -25.4053 | failed | failed | failed | True (loose spec) |

A 的 dc_g=0.10631（≈-19.5dB，弱增益，spec_a 的 [0,6]dB 判 fail）；B 的 vcm_out 塌到 0.027V（高 rl×itail 压降）→ 全部增益 ≈-25dB，但 spec_b 极宽松 [-30,-20]dB → 全 pass，overall=True。A/B 数值/结构/verdict 模式全不同（非文件名互换）。

## 抽取的 case
- `EDA-Eval-DesignFlow-CTLESpec-001`（spice_sim 域扩量#2，L2 真跑 FineSim -spice）
- 交付件 = `ctle_spec_check.py`：吃 `<tb.sp> <spec.json> <out_report.json>`，真跑 `finesim -spice -np 4`，解析 `<deck>.log` 的 .meas，把 failed measure 归类为 `not_met`，逐条 spec 判 pass/fail/not_met，写 report.json
- 隐藏 B = tb_b.sp（ctle_b inline）+ spec_b.json（loose spec → overall_pass=True，fpeak/bw/idd 仍 not_met）
- check.py 12 条件 a-l（见 jsonl test_rationale），关键 discriminator：
  - (h) fpeak/bw/idd verdict==not_met（击破把 failed 当 fail/0/pass 的错解）
  - (l) 跨输入 guard：候选在 (tb_a, spec_b) 上 dc_g≈A 的 0.10631 且 ≠B 的 -25.4331（击破 print-expected/跳过 sim 的 stub）
- ref 自验（.75）：reference harness 12/12 PASS；5 negatives 全 FAIL：
  - empty_shell→(a)；print_expected→(l)（pass a-k，败在跨输入）；ref_core_deleted→(c) sim_ok=False
  - naive_always_pass→(h)（全 stamp pass）；naive_ignore_failed→(h)+(j)（failed 当 fail → overall_pass=False≠True）
- §4.9 三 fake-submit（empty/print-expected/ref-core-deleted）全 FAIL ✓；≥2 negative 全 FAIL ✓
- pi real-run 待下一轮（budget）

## 与 CTLEAC-001 的区别（非重复）
| 维度 | CTLEAC-001 (n91pk/alenxu) | CTLESpec-001 (wb03t/cwei) |
|:--|:--|:--|
| PDK | G6 V1_HKMG_D5 | cl028hkn 28nm |
| 核心解析 | .meas + **.op vvdd amps**（idd 必走 .op） | .meas only（idd 在 .ac 下 failed→not_met） |
| failed 处理 | bw_3db failed→null | **fpeak/bw/idd failed→not_met 语义** |
| spec 形态 | target_op(>=/<) + unit 换算 | min/max + verdict{pass,fail,not_met} |
| overall | AND(spec.pass) | AND(verdict!=fail)（not_met 不算 fail） |
| 关键 guard | idd 走 .op | 跨输入 dc_g 区分 + failed→not_met |
