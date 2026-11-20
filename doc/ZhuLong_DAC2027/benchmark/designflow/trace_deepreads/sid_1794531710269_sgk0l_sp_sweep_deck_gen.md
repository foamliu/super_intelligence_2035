# deepread — sid 1794531710269_sgk0l · vincentz @ hfeg0plg98 (mc=56)

**session**: hspice-dominant (hspice:1466; virtuoso:1453; netlist:168; aether:82; schematic:39; skipper:30)
**size**: 1,061,552 bytes / 83 msgs / 3 user turns
**source path on target**: `/rundata/train/V0_NCG_HF_Virtuoso/simdir/hspice/vincentz/H-spice/SM_V2B_TF/FBCC_VS_CBCC/01_V1_FBCC_Vcm/` (permission-denied to e0031982 ⇒ 全合成)

## 用户意图（逐字）

**U#0 (produce-task, 第一步)**:
> mixbest_V1_RBL_95_no_probe_I.sp 帮我以这个.sp文件为基础，里面的 Sanadj1=1 Sanadj2=1 Sanadj3=1 Sanadj4=1 Sapadj1=1 Sapadj2=1 Sapadj3=1 Sapadj4=1 R_BL=95，一共9个变量，其中 Sanadjx 需要和 Sapadjx 相等，值只能为 0 or 1，R_BL 从 0,5,15, step 10, 95, 105, 115, 125, 135，分别生成对应的 .sp 文件，放在 NxPx_RBL 文件夹里，文件以 mixbest_V1_RBL_X_NxPx.sp 命名，X 为 RBL 数值，x = Sanadj1*4 + Sanadj2*2 + Sanadj3*1 + Sanadj4*8。

**U#1 (produce-task, 第二步)**:
> 请帮我根据 runsim 文件生成一个 runsim_RBL_NxPx 文件用于跑 NxPx_RBL 下所有的 .sp 文件

**U#2 (Q&A，非 produce)**:
> vtarget.pl 这个代码是什么意思？  ⇒ assistant 解释 primesim bisection 结果提取脚本，与本 case 无关

## 关键澄清（MSG 38-39）
agent ask_question 问 R_BL 取值列表，用户确认 = **0,5,15,25,35,45,55,65,75,85,95,105,115,125,135（15 个值，15 到 95 步长 10）**

## 金标准（agent 实际产物，MSG 47/50/78）
- 模板 `mixbest_V1_RBL_95_no_probe_I.sp` 含 9 条 `.param`（Sanadj1-4/Sapadj1-4/R_BL），2347 chars
- 16 种 (Sanadj,Sapadj) 组合（SanadjN==SapadjN，0/1），x = Sanadj1*4+Sanadj2*2+Sanadj3*1+Sanadj4*8 ∈ 0..15
- 输出 16 个 `N{x}P{x}_RBL/` 目录 × 15 个 `.sp` = **240 文件**
- 文件名 `mixbest_V1_RBL_{RBL}_N{x}P{x}.sp`
- 每个 .sp：仅替换 9 条 `.param` 取值，deck 其余逐字保留
- `runsim_RBL_NxPx`：`#!/bin/bash`，按 x=0→8→1→9...→7→15 顺序、每 x 内 R_BL 升序，每条
  `bsub -q fqueue3 primesim -i NxPx_RBL/mixbest_V1_RBL_{RBL}_N{x}P{x}.sp -o ./result/NxPx_RBL/.../SM -np 6`，相邻间 `sleep 1.5s`，共 240 条

## x-编码验证表（MSG 50）
| Sanadj1,2,3,4 | Sapadj1,2,3,4 | x | 文件夹 |
|---|---|---|---|
| 0,0,0,0 | 0,0,0,0 | 0 | N0P0_RBL |
| 0,0,0,1 | 0,0,0,1 | 8 | N8P8_RBL |
| 0,0,1,0 | 0,0,1,0 | 1 | N1P1_RBL |
| ... | ... | ... | ... |
| 1,1,1,1 | 1,1,1,1 | 15 | N15P15_RBL |

bit 分解：x = 4·S1 + 2·S2 + 1·S3 + 8·S4 ⇒ S4=(x>>3)&1, S1=(x>>2)&1, S2=(x>>1)&1, S3=x&1

## 合成计划（B-grade L1，纯 stdlib SUT）
- **domain**: analog_context（HSPICE corner 扫描 deck 生成）
- **A 可见**: mixbest_V1_RBL_95_no_probe_I.sp（V1 FBCC_Vcm deck，合成）+ runsim 模板
- **隐藏 B**: mixbest_V2_RBL_50_no_probe_II.sp（V2 CBCC_Vddq deck，disjoint 节点/subckt/measure），R_BL=[10,30,50,70,90,110,130]（7 值，16×7=112），prefix=mixbest_V2，runsim_V2_NxPx
- **隐藏 C**: mixbest_V3_RBL_20_no_probe_III.sp（V3 SenseAmp deck，disjoint），R_BL=[20,60,100]（3 值，16×3=48），prefix=mixbest_V3，runsim_V3_NxPx — 交叉反硬编码
- **SUT**: `sp_sweep_gen.py <base_sp> <out_root> --rbl csv --prefix p --runsim-name n [--sleep s]`，纯 stdlib
- **check.py**: 18 条 a-r，subprocess 跑 SUT 于 B/C/A，断言 16 目录、文件数、命名、9 条 .param 替换、Sanadj==Sapadj、x-formula、deck body 逐字一致(反硬编码)、runsim 结构、确定性、--help
- **k_rationale == k_check == 18 ≥ 8 ✓**

## 自验结果
- ref check.py: **PASS 18/18 (a-r)** exit 0
- negative_selftest: 3 neg (empty_shell/print_only/hardcode_a) **ALL FAIL** NEG_RC=0
- §4.9 三假: empty→cond d, print→cond d, core_removed(clean)→cond f, distinct {d,f}=2 ✓
- 确定性 cond q: B 重跑 sha256 一致 ✓
