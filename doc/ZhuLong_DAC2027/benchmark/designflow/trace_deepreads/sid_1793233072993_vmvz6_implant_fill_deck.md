# trace_deepread: 1793233072993_vmvz6 — Calibre DRC implant-fill deck generation (physical_verify)

- **trace**: `1793233072993_vmvz6` · ellawu @ hfeg0pkn005 · mc=285 · 136 msgs · 1.5MB
- **tool mix**: pyAether 94 + dbGet 127 + calibre 17 + schematic 4 (low sim: hspice/spectre 0)
- **domain**: physical_verify (Calibre DRC rule-deck generation)
- **case**: EDA-Eval-DesignFlow-ImplantFillDeckGen-001 (A-faithful, L1-boundary, k=14/14)

## 用户原话逐字 (A-档 seed, 纯需求/报错 — 未指根因未给修复)
- U[0]: `ERROR: Error VAR2 on line 496 of /proj/decqa/V0/ver/drc/ellawu/auto_implant/ella_train/ella3/runFillImplant.rule - no variable value, or invalid variable value, specified for this variable name: SPACE_VALUE_cell. --- Attached files --- [Attached file: IMCleFillImplantDrc1.py → .../uploads/IMCleFillImplantDrc1.py]`
- 后续轮 (U[77..134]) 是迭代修复（说中文/修复后脚本/布尔值传参/IMCleAddPropertyForImplantFill/FLATTEN 条件），**含根因/方案**，不进 prompt，仅作金标准反推参考。

## 真实产物 (gold)
附件 `IMCleFillImplantDrc1.py` (179KB, pyAether) 中的 `IMCleImplantFillMainDeckGenerate(file_path, layerDict, layerFile)`：
读 `runFillImplant.rule` 模板 →
1. `LAYER OPERATION` 行后写 `INCLUDE "<layerFile>"`
2. `//VARIABLE SPACE_VALUE` 标记处：layerDict 每个 key 替换/插入 `VARIABLE SPACE_VALUE_<key> <val>`
3. 过滤掉 layerDict 之外的 `VARIABLE SPACE_VALUE_*` 行（**消除 VAR2 SPACE_VALUE_cell 错误源**）
4. `//CMACRO` 标记处：对 layerDict 中有 DMACRO 的 key 插入 `CMACRO FILL_IMPLANT_<key>`（DMACRO 头 D→C，`SPACE_VALUE`→`SPACE_VALUE_<key>`）
5. 过滤 layerDict 之外的 `CMACRO FILL_IMPLANT_*`
6. 删除原始 `= FLATTEN` 赋值行
7. `//FLATTEN` 标记处：对 CMACRO 末 token 含 gap/hole 的，插入派生 `<begin> = FLATTEN <gap_or_hole>`（U[134] 加并列条件：**fill in cell 没勾选时才执行**）
8. `//DFM` 标记处：插入 `FILL_DFM_RDB { DFM RDB GDS implantFill_flatten.gds }`

## L1-boundary 抽象
L2（live pyAether + Calibre + OA）沙盒不可复现 → L1-boundary：
候选得 deck 模板（文本，含 LAYER OPERATION/DMACRO/VARIABLE/CMACRO/= FLATTEN//FLATTEN//DFM 标记）+ layer 定义文件 + JSON 配置（layerDict/layerFile/fill_in_cell），纯 stdlib 产 `runFillImplant.rule`。
- A(可见)=cell/nch + stale 干扰键 + fill_in_cell=false
- 隐藏 B=pch1/nch2 + old 干扰键 + fill_in_cell=false（主判分）
- 隐藏 B2=avn/dgx + legacy 干扰键 + fill_in_cell=true（条件分支守卫，杀硬编码 + 验条件）

## 判分 14 条 (a–n, check.py 自包含, A/B/B2 内联)
a zip+py(≥200B)+py_compile+stdlib 禁 pyAether/socket/urllib + 源码无 B 字面量
b B exit0 + 输出 deck 非空
c LAYER OPERATION 紧随 INCLUDE "layers_B.def"
d VARIABLE SPACE_VALUE_pch1 0.18
e VARIABLE SPACE_VALUE_nch2 0.22
f 无 VARIABLE SPACE_VALUE_old（杀 VAR2 错误源）
g CMACRO FILL_IMPLANT_pch1 含 SPACE_VALUE_pch1
h CMACRO FILL_IMPLANT_nch2 含 SPACE_VALUE_nch2
i 无 CMACRO FILL_IMPLANT_old
j //FLATTEN 之前无原始 = FLATTEN 行
k //FLATTEN 之后派生 pch1gap/nch2hole = FLATTEN，无 oldgap
l //DFM 之后 FILL_DFM_RDB 块 + DFM RDB GDS implantFill_flatten.gds
m B2 fill_in_cell=true → 无派生 FLATTEN，但 VARIABLE/INCLUDE 仍正确
n A 无 B 值污染 + 含 SPACE_VALUE_cell 0.16 + B 3 次重跑 sha256 一致

## 自验
- ref PASS 14/14 on B+B2+A
- 独立 temp 提取 jsonl test 字段复跑 PASS
- 5 negative（empty/print_expected/hardcode_b/naive_include_only/core_deleted）NEG_ALL_FAIL=true
- §4.9 三假（empty/print-expected/core-deleted）全 FAIL
- jsonl test 字段 sha == disk check.py sha
- 断言对账 k_rationale=k_check=14≥8 GATE PASS
