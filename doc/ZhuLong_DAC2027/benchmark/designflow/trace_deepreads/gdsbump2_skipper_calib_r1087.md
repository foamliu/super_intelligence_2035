# GDSBump2 skipper dbLibLayers calibration — r1087 (2026-11-25)

> Resolves the r1086 open blocker: "skipper-semantic=36 vs GT=34, 差 2 lpp 未对上".
> **结论：GT=34 正确；r1086 的 36 是误算（假设 TEXT 全为 texttype=0）。**
> 本轮用 .75 真实 skipper 2020.06.sp3 实测确认语义，mock 路径已完全明确。

## 1. 核心发现（skipper 2020.06.sp3 实测）

在 .75 sandbox 用真实 skipper 跑合成 GDSII 探针（`skipper probe.tcl <gds> -noterm`）确认：

1. **TEXT 元素的 purpose = COLROW 记录的值**（record type 0x16），**不是** TEXTTYPE (0x0F)。
   - 探针：TEXT on layer 99 + COLROW=5 → skipper dbLibLayers 报 `99.5`。
   - 探针：TEXT on layer 100 + COLROW=0 → 报 `100.0`。
2. **skipper 拒绝 TEXT 里的 TEXTTYPE (0x0F) 记录**：报错
   `Purpose type is not expected: 15, 22 (expected)`（15=0x0F=TEXTTYPE，22=0x16=COLROW）。
   → 这正是 A.gds 的 TEXT 元素用 COLROW 而非 TEXTTYPE 的原因（Cadence 导出时按 skipper 方言写）。
3. **BOUNDARY/PATH 的 purpose = DATATYPE (0x0E)**（标准语义，实测确认）。
4. **dbLibLayers = BOUNDARY/PATH (layer,datatype) ∪ TEXT (layer,colrow)**，跨全库所有 cell 去重。

## 2. A.gds 真实 lpp 计数（本地 stdlib 解析 + 实测语义）

A.gds (`A1_CA2_connection_check_A1.gds`, 12288B, 24 cells, 149 elements)：
- BOUNDARY distinct (layer,datatype): **33**
- TEXT 元素 21 个，COLROW 值分布 `{0:17, 7:1, 10:1, 3:1, 2:1}`，
  distinct (layer,colrow) = 20；其中 **只有 (230,0) 不在 BP 集**（(78,7)/(160,10) 等都与 BP 撞）。
- skipper-faithful union = 33 + 1 = **34** == check.py GT nlpp=34 ✓
- totalfig = 149 (BOUNDARY 83 + SREF 45 + TEXT 21) == GT totalfig=149 ✓

**GT=34 正确，无需改 check.py 的 GT。** r1086 的 "36" 来自把所有 TEXT 当 texttype=0，
误把 (78,0)/(160,0)/(230,0) 都算新 lpp；实际 (78,7)/(160,10) 因 COLROW=7/10 与 BP 撞，只有 (230,0) 新。

## 3. hidden_B / hidden_B2（无 TEXT，纯 BOUNDARY）

- hidden_B: 1 cell B_TOP, 11 BOUNDARY, lpps {5.0:3,15.0:2,25.0:2,35.0:2,100.1:1,200.2:1} == GT ✓
- hidden_B2: 1 cell B2_TOP, 5 BOUNDARY, lpps {8.0:2,16.0:2,24.0:1} == GT ✓
（B/B2 已在 r1086 确认；本轮再确认结构。）

## 4. mock 设计（skipper_mock.py，下轮建）

`skipper_mock.py`（放 `reference/EDA-Eval-DesignFlow-GDSBump2-001/`）：
- 入口：`python3 skipper_mock.py <tcl> <args...> -noterm`，仿 DummyMeas skipper_mock 模式。
- 解析 GDSII（stdlib only）为内存模型：cells[]，每 cell 含 elements[]；
  element 带 (type, layer, purpose, raw_records)。
  - BOUNDARY/PATH: purpose = DATATYPE 值
  - TEXT: purpose = COLROW 值（**关键**，不是 TEXTTYPE）
  - SREF/AREF: sname（用于 hierarchy）
- 生成 tcl wrapper（tclsh8.6，eval 机已有）定义 db* procs，set argv，source 候选 tcl：
  - `dbImport <gds>` → 返回 handle（mock 预解析模型注入）
  - `dbLibGetId`/`dbLibGetName`
  - `dbLibLayers -libId` → 返回 "layer.purpose" 列表（BP∪TEXT 去重）
  - `dbLibTopCell`/`dbLibGetAllCells`/`dbCellGetByName`/`dbCellGetBBox`/`dbFigQuery`/`dbFigGet`
  - `dbLayerMove -libId -cellName -lpp1 -lpp2 -depth` → 遍历 cell 树，把 (layer,purpose)==lpp1 的 figure 的 layer 改为 lpp2.layer（purpose 改为 lpp2.purpose，bump 场景下 purpose 不变）
  - `dbLibExport <lib> <out.gds>` → 把（被候选 dbLayerMove 改过的）模型写回 GDSII binary（LAYER 记录值更新；DATATYPE/COLROW 不变）
- 忠实性：候选必须真调 dbLayerMove 才会改模型；空壳/只 print/删核心 → dbLibExport 写出原 GDS → check.py 断言 (c)(e)(k)(l) FAIL。✓
- check.py 的 REPORT_TCL 也走同一 mock（read-only 路径），保证 nlpp/lpps/totalfig 与 GT 一致。
- check.py 已 `SKIPPER = os.environ.get("SKIPPER_BIN", "/apps/.../skipper")`；
  评测机 36.15 无 skipper → 需让 check.py 在 mock 模式下跑。
  方案：check.py 检测 skipper 二进制不存在时 fallback 到 `python3 skipper_mock.py`（同 DummyMeas/PowerFill 模式）。
  **注意**：check.py 当前 `_run_skipper` 直接 `subprocess.run([SKIPPER, tcl, ...])`；
  改为：若 SKIPPER 不可执行，则 `subprocess.run([sys.executable, skipper_mock_py, tcl, ...])`。
  （只改运行入口，不改断言逻辑/条数/严格度——符合 LITE_FIX_ORDER §4。）

## 5. 下轮计划

1. 建 `skipper_mock.py`（按 §4）。
2. 改 check.py `_run_skipper` 加 mock fallback（SKIPPER 不可用时走 mock）。
3. 自验 L2（ref gds_bump2.tcl 跑 mock → 15/15 PASS）+ L3（4 neg 全 FAIL distinct）。
4. 真跑 `eval/run_one.sh EDA-Eval-DesignFlow-GDSBump2-001 --shard C`（非 SKIP_RUN）确认 L4。
5. PGLayout 仍 defer（更复杂：dbCreateInst/Rect/Label + geometry overlap）。

## 6. 本轮产出

- 0 case（calibration 轮，同 r1086 性质）。
- 关键解锁：GDSBump2 的 L4 skipper 语义已实测确定，mock 可直接建。
- green 135 不变 / 余 P0 仍 2（PGLayout+GDSBump2，GDSBump2 下轮可转 green）。
