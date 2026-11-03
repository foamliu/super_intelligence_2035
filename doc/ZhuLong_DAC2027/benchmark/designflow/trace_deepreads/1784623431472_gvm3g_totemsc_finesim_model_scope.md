# Trace deep-read: 1784623431472_gvm3g — Totem-SC/FineSim `.model ./` scope fix

- **session**: 1784623431472_gvm3g.messages.json (e0014566 @ hfeg0plg58, mc=554, 272 msgs, 639KB)
- **agent**: lead (cline)
- **domain**: spice_sim (FineSim SPICE engine, Ansys Totem-SC reliability wrapper)
- **shard**: B (spice_char) → case `EDA-Eval-DesignFlow-FineSimModelScopeFix-001`

## 用户意图（逐字原话，仅掩码 key/token）
- T0 [act]: `hello`
- T2 [act]: `运行  runme`
- T53 [act]: `需要的，辛苦进一步帮忙排查好，并且修复.`
- T239 [act]: `continue`
- T260 [act]: `你把代码改好，现在可以完全跑通了吗？`
- T268 [act]: `Thanks`
- T270 [act]: `你内置了 skill-creator 吗？`

用户轮均为 terse 指令（运行/排查修复/确认跑通），无规格化需求 → **B 档 synthesized**（用户原话太 terse，A 档 faithful 不合规——无"提出需求/表达目标"的实质轮，只有"运行 runme"+"排查修复"）。子技能来自真实排障修复流程。

## 真实工具链
- **Ansys Totem-SC** 2025_R1.6.ENG（电源/EM/IR 可靠性仿真，FineSim 为底层 SPICE 引擎）
- 工作目录 `/proj/train/AI_Virtuoso/workdir/e0014566/20260715_ddjob_totem_sc_case/PowerIREM/`
- `runme` 脚本 → `totem_sc run.py` → FineSim 仿真 → NLV/ELMV/NV/PHMV/.../PEM_peak 16 个 view 生成 + EM/IR/Pad Data Mining 报告
- FineSim V-2023.12-1（与 .75 同版本，便携可行）
- foundry G4B-CIP 模型（不可移植 .75）

## 根因（cline 诊断）
模型文件 `data/packsim_0313134807/inc/incFile_G4B_CIP` 与 `incFile_lp` 用 HSPICE 专有本地模型作用域语法 `.model ./ntn. nmos`（`./` 前缀），FineSim 不支持 `./` 前缀 → 找不到模型定义 → `ERROR! can't find model for mosfet 'mn1'/'mp1' / diode 'd1'`（共 9 错）→ FineSim fail → ELMV 段错误。

对比可工作的 `incFile_G4B_HK2d0`: `.MODEL ntn. nmos`（无 `./` 前缀）→ FineSim 可识别。

## 修复（cline 执行）
1. `sed -i 's/\.model \.\//.model /g'` incFile_G4B_CIP + incFile_lp（共 53 处 `.model ./` → `.model `，去 `./` 前缀，保留模型名含末尾点）
2. `aplmmx.config`: `CHECK_MODEL_CORNER 1` → `0`（避免 FineSim 流程 APLMMX 段错误，配置已有 TODO 注释）
3. `incFile_G4B_HK2d0`: CRLF → LF 行尾
4. 重跑 runme → FineSim 成功：MOS 模型加载 + DC converged + Transient 完成 + `FineSim Successfully Completed` → 16 个 view 全生成 + EM 报告完整

## 可移植子技能（本 case 取的内核）
**FineSim "can't find model" 诊断 + `.model ./` HSPICE 本地作用域语法 → `.model ` name-agnostic 修复 + FineSim 真跑闭环验证**。

便携化：foundry G4B-CIP + Totem-SC 不可移植 .75，取 level-1 Shichman-Hodges MOS（kp/vto/lambda）+ FineSim V-2023.12-1 `.tran` + `.measure tran tpd/vswing`。

## distinct vs 已有 B case
- BistOscRccReorder-001 = FineSim "cannot open include"（RCC 路径缺失）+ var_osc 扫描顺序重排
- 本条 = FineSim "can't find model"（模型定义语法 `.model ./` 不兼容）+ name-agnostic 去 `./` 前缀修复
- 不同失败模式、不同修复动作 → distinct 子技能 ✓

## A/B 设计（便携 .75）
- A（可见）：2 级 CMOS 反相器链 + ESD 钳位二极管（vdd=3.3V, 4 MOS + 1 diode, 50fF 负载），broken `models_A.sp` 用 `.model ./nch. nmos / .model ./pch. pmos / .model ./dclamp. d` → FineSim 10 错。修复后 GT: tpd=2.1447e-09, vswing=3.3, "FineSim Successfully Completed"。
- B（隐藏）：3 级反相器链 + 中间节点二极管钳位（vdd=2.5V, 6 MOS + 1 diode, 100fF, 不同模型名 nmos_hv./pmos_hv./desd.），broken `models_B.sp` 用 `.model ./` → FineSim 14 错。修复后 GT: tpd=5.8225e-11, vswing=2.5。跨输入 diff ~36x。

## 关键陷阱（烤进 check.py 16 条 a-p）
- (d) 修复后 models.sp 含 0 个 `.model ./`
- (h) A dut.log 无 "can't find model"
- (j) 判分器独立重跑 FineSim 防假 .mt0
- (k)(l)(m) 隐藏 B 跨输入：naive_hardcode_a 只按 A 模型名(nch/pch/dclamp)字面替换 → B 的 nmos_hv/pmos_hv/desd 仍 `.model ./` → B FineSim 失败 → (k) 击穿
- (n) fixer.py name-agnostic：不含 A tpd 数值 + 不含 A/B 模型名硬编字面量 → naive_hardcode_a (含 nch/pch/dclamp) + naive_print_expected (含 2.1447e-09) 击穿
- (o) B diagnosis.missing_models == B 真实名（防硬编 A 诊断）
- naive_strip_trailing_dot: 去 `./` 且去末尾点 → 实例引用 `nch.` ≠ 模型 `nch` → FineSim 仍 "can't find model" → (h) 击穿（(d) 通过，distinct signature）

## .75 端到端自验
- ref fixer on A: verdict=true, tpd=2.1447e-09 ✓
- ref fixer on B (cross-input): verdict=true, tpd=5.8225e-11, B 模型名保留 ✓
- negative_selftest on .75 (~29s): ref PASS 16/16 + 5 neg 全 FAIL 互异(NEG_RC=0)
  - naive_empty → (a), naive_print_expected → (d), naive_hardcode_a → (n), naive_strip_trailing_dot → (a missing mt0), naive_no_rerun → (a missing mt0/log)
- §4.9 三假（空壳/print-expected/删核心=no_rerun）全 FAIL ✓
- test field == disk check.py (md5 22c8306496b52376fcdc13f33b7ffeab) ✓
- 断言闸门 k_rationale=k_check=16≥8 ✓
