# Deepread — iacrk · BWZ dummy 填充逻辑解析

**session**: `1793152046824_iacrk.messages.json`
**user**: `zhiguo1w` @ `hfeg0pjn200` (10.129.40.209)
**mc**: 117 · **domain**: physical_verify (Calibre DFM TVF dummy)
**date**: 2026-11-15 ~ 11-16
**msgs**: 44 (user=22 / assistant=22)
**附件**: `calibreDummy_chip.rule` (2.19MB TVF 脚本), `debug.oas` (U#2)

## 用户意图（逐字）

- **U#0**: 「解析该文当中BWZ加入dummy的逻辑」（附件 calibreDummy_chip.rule）
- U#1: 「如果使用15_7 layer来进行QA，如何画QA Pattern 能正确输出dummy」
- U#2: 「输出并没有dummy，且输出到blk layer后不再继续输出BWZ相关debug layer」（附件 debug.oas）
- U#3: 「可是我画的是10*1的矩形」
- U#4: 「如果在QA Pattern中同时存在Vertical和Horizontal方向，也会造成同时触发双向区域吧」
- U#5: 「这个脚本中，如果只有BWZ存在，其他layer 比如PCZ是否也直接输出其对应的dummy」

**真实意图**: 解析 Calibre DFM TVF dummy 生成脚本中 BWZ（Buried Wordline）加入 dummy 的完整流程逻辑。

## Agent 工具链

search_codebase（超时）→ run_commands（disabled）→ run_approved_command（profile/shell-runner）→ read_files（读 deck 段）→ 最终 prose 解析说明。Agent 在受限 shell 环境下反复尝试 grep/读 deck，最终完成结构化解析。

## BWZ dummy 流水线（真实 deck 关键结构，fixture 忠实复刻）

1. **参数定义** `set BWZ_cmp [list 15_9 0.449 0.449 0.400 "" "" 150 5.5 0.400 BORD_BWZ_H BORD_BWZ_V 0.449 0]`（12 字段：cmpLay/LWidth/LSpace/Mspace/Amin/Hmin/MaxLen/MinLen/bordSpace/HBord/VBord/LineEndSpace）
2. **全局变量**: `BWZ_SPACE=0.449`, `min_longEdge_BWZ=1`, `exclude_bord_BWZ=311_41`, `BWZ_Info_Extent=[15_7 15_101 15_103]`
3. **层声明**: `LAYER BWZarray 10002`, `LAYER exBWZ 10003`, `LAYER Prohibit_BWZ:prohibit_cmp 10004`
4. **方向判定**: `BWZarraySel = BWZarray NOT exBWZ` → `BORD_BWZ_H_pre = BORD INTERACT (BWZarraySel WITH EDGE (LENGTH (ANGLE==0) >= 1))` → `BORD_BWZ_V_pre = ... ANGLE==90 ...` → `BORD_BWZ_H = H_pre NOT INTERACT V_pre`（互斥）
5. **DefMaskBlk**: `defineMaskBlk_OR_...BWZ.H = OR empty <Prohibit> <BORD_BORD> <Frame_FRMCP>` → `DefMaskBlk = SIZE ... BY 0.449/2.0-GRID OVERUNDER`
6. **MainBlk 保护**: `maskBlk_sizeIn = SIZE DefMaskBlk BY -0.400` → `mainPattern_Extent = EXTENTS ...` → `... ENCLOSE RECTANGLE 0.449 5.5`（Lwidth × MinLen）
7. **输出**: `DFM RDB OASIS debug.oas ... 15 0/1`
8. **H/V 双分支**: BWZ.H 与 BWZ.V 镜像执行

## 旧规则判定与 11-15 复活

- **2026-11-03 parked**，note: `解析 calibreDummy.rule BWZ dummy 逻辑=prose 解释非 script`
- **11-15 task初衷 B类复活**: analysis/explain/Q&A 域全部恢复为可造；唯一排除标准=无真实 trace / 写不出有牙 check
- **r707 revival**: reframe 为 mock-behavioral `tvf-deck-dummy-flow-extract`（纯 stdlib TVF deck 静态解析器），check 20 条独立断言（参数/全局/层/方向/Mask Block/Main Block/输出/H-V 分支），hidden B 反 A 硬编码，B2 边角 H-only

## case

- **case_id**: `EDA-Eval-DesignFlow-BwzDummyFlowExtract-001`
- **C.jsonl**: 438 行（437→438）
- **check**: 20 条断言 a-t（k_rationale=k_check=20 ≥8 ✓）
- **自验**: reference PASS ✓ · 3 negatives (empty/print_only/hardcode_a) 全 FAIL ✓
