# Deepread: 1795154631427_u6dpn — FineSim IDDQ Lib/Netlist Device-Name Mismatch Diagnosis+Fix

## Trace metadata
- **session**: 1795154631427_u6dpn
- **user**: jeoteanl @ hfeg0plg57 (10.129.35.77) — NEW user (4-shard ledger 未出现过)
- **mc**: 86 (hspice + netlist + pdk dominant)
- **date**: 2026-11-20
- **msgs**: 205, 1.0MB
- **scan snapshot**: summary_1120_reconstructed.tsv
- **domain**: spice_sim (B shard) — std-cell characterization simulator-deck repair

## User intent (msg25, 原话)
jeoteanl 在 hfeg0plg57 上跑 m2701 V0_DDR3 FineSim std-cell characterization (AI_FOR_STD 流程)。
step1 = IDDQ 仿真，75 个 case 全部失败。用户报告失败并要求诊断修复。

## 根因诊断（agent 推理链）
agent 读 step1 IDDQ 的 deck（duty.sp 形态，msg62）+ .lib 加载语句，定位到**模型库与网表器件名不匹配**：

| 层 | 实际内容 | 器件/subckt 名 |
|---|---|---|
| 网表实例化 | subckt 调用 | `nrvt_ckt` / `prvt_ckt`（HL22 22nm PDK 4 端子 subckt）|
| 激活的 .lib | V1_HKMG 库 | `ntn` / `ptn` / `ntk` / `ptk`（根本无 `nrvt_ckt` / `prvt_ckt`）|

→ FineSim 在 V1_HKMG 库里找不到 `nrvt_ckt`/`prvt_ckt` 的 subckt 定义，75 个 case 全部 instantiation 失败。

### duty.sp 形态（msg62，broken form — 本 case 的 visible A）
- V1_HKMG 库 **active**，HL22 库 **commented**
- 器件 = `nrvt_ckt` / `prvt_ckt`
- corner = `tt_25C_0.80V`
- DEFAULT_LIB 拼接：`dir + file`（丢斜杠 bug，见下）

## 修复（agent 操作）
1. **激活 HL22 topusage 库**（section `top_tt` / `pre_simu`）—— 该库含 `nrvt_ckt`/`prvt_ckt` subckt 定义
2. **注释 V1_HKMG 库**（错配库，移除）
3. **DEFAULT_LIB 全路径拼接** —— 踩坑 msg83: 原写法 `DEFAULT_LIB = dir + file` 丢斜杠，生成 `hspicetopusage...`（dir 末尾无 `/` + file 头部无 `/` → 两段直接 concat）。正确写法 = `dir.rstrip("/") + "/" + file.lstrip("/")`，单斜杠分隔。

### fixed form（agent 输出）
- HL22 topusage 库 **active**（`top_tt` / `pre_simu` section）
- V1_HKMG 库 **commented**
- DEFAULT_LIB 单斜杠拼接
- 器件 `nrvt_ckt`/`prvt_ckt` 现可解析

## 本 case 聚焦范围
A 档 trace-faithful，聚焦该**诊断 + 修复子任务**（lib/netlist device-name mismatch）。
不涵盖 m2701 characterization 全流程的其余步骤（step2/step3 等）。

## 交付物（A 档 LibMismatchFix-001）
纯 Python `lib_mismatch_fix.py <deck.sp> <lib_spec.json> <out_dir>`：
- 读 deck.sp，识别实例化的 device 名
- 读 lib_spec.json（含各 lib 的 subckt 名清单 + section + corner）
- 诊断：device → lib 归属（哪个 lib 含该 device 的 subckt 定义）
- 激活正确 lib（含 spec 指定 section），注释错配 lib
- DEFAULT_LIB 单斜杠拼接（规避 trace 的 hspicetopusage concat bug）
- 输出修正后的 deck.sp + manifest.json 到 out_dir

### visible A（trace-faithful）
- 库：HL22 PDK（含 `nrvt_ckt`/`prvt_ckt`）vs V1_HKMG（含 `ntn`/`ptn`/`ntk`/`ptk`）
- corner: `tt_25C_0.80V`
- sections: `top_tt` / `pre_simu`

### hidden B（anti-hardcode-A，全异）
- 库：`PDK_B_HP` / `Legacy_B`
- 器件：`nch_hp` / `pch_hp`
- corner: `typ`
- sections: 全异于 A
→ 防 SUT 硬编码 A 的库名/器件名/section

## 判分（check.py, k=12 a-l）
- ref PASS 12/12
- NEG 4/4 FAIL: neg_empty→a, neg_print→a, neg_core_removed→b, neg_hardcode_a→b
- §4.9 三假（empty/print/core-removed）+ hardcode-A 全 FAIL
- 3-seed 字节 sha256 一致

## dup 检查
4-shard ledger（A/B/C/D）cross-shard 去重：u6dpn 仅 B 未动（fresh），NEW user jeoteanl，无近重既有 case。

## 落库记账
- cases/B 471→472
- B.jsonl 470（auto-regen by merge 脚本，LibMismatch@174；merge jsonl 勿手改）
- ledger_B case 631→632（row 1646）
