# Deepread r655 — jzeng 00p77 (hfhds201/10.129.32.75, mc416)

## trace_source
- user: jzeng, host: 10.129.32.75 (hfhds201), session: 1794734620660_00p77
- match_count: 416, keywords: drc:1663;gds:1075;rtl:853;pyaether:467;calibre:183;dbget:160;dbopencv:126;cellview:100
- trace: /home/jzeng/.cline/data/sessions/1794734620660_00p77/1794734620660_00p77.messages.json
- 621 msgs / 313 user turns / 2,801,712 bytes (2.8MB)
- tool calls: read_files=100, editor=94, run_approved_command=94, RAG_search=6, list_allowed_files=3

## 真实用户意图（user turns, 逐字原文, 去标签后 >10 字符的）

- **U#0**: `/home/jzeng/Desktop/IMCleAutoVia.py优化该脚本，使其在0.55um宽的M4及0.55um宽的M5交点处生成2x2的M4 M5，再生成V4`
- **U#74**: `还是无法生成M4 M5和V4，建议分成两个脚本，先给我一个脚本，在M4 M5交点生成M4 M5导入某个自定义库`
- **U#90**: `第四步不是生成2x2的V4，是生成2um x 2um的M4和M5`  (澄清: 不是 2x2 V4 阵列, 而是 2um×2um 尺寸的 M4/M5 pad)
- **U#110**: `没法生成，实际layout中M4和M5是一段宽度0.55um，长度较长到线，不是0.55um宽度的方块`  (M4/M5 是长走线, 非方块)
- **U#133**: `M4 M5可能是path pathseg rect等等`  (支持多种几何对象类型)
- **U#141**: `按照上述要求优化一下/home/jzeng/Desktop/IMCleAutoVia.py，使其能在0.55um宽度的M4 M5交叠处生成2um x 2um的M4 M5，然后再生成V4`  (最终完整意图陈述)
- **U#198**: `优化一下，把生成到M4 M5和V4放到一个cell里面`  (全部生成到独立 cell)
- **U#261**: `现在M4 M5还是生成在目标cell，没有生成在auto via cell里面`  (bug: 生成位置错误)
- **U#280**: `只生成了M4 M5到cell，没有V4`  (bug: V4 缺失)
- **U#288**: `只生成了M4 M5的cell，而且是直接就生成在目标layout,我需要生成在auto via库的cell里面，生成完之后再自己调进目标layout`  (最终要求: auto_via 库独立 cell, 不自动 instance)
- **U#303**: `Traceback ... SyntaxError: name 'techdb' is used prior to global declaration解决一下`  (最终 bug: Python 作用域错误)

## 用户意图演进总结

用户要求优化 IMCleAutoVia.py 的 V4 pre-GDS 区域，使其：
1. 扫描当前 layout 中 **0.55um 宽**的 M4/M5 走线（支持 Rect/Path/pathSeg，含层次化子实例）
2. 在 M4-M5 交叠处生成 **2um×2um** 的 M4 pad 和 M5 pad（不是 0.55um 方块，不是 2x2 阵列）
3. 生成 **V4 通孔**（via）
4. 全部生成到 **auto_via 库的独立 cell** 中（`<cellName>_V4_CELL`），**不自动 instance 到目标 layout**
5. 用户手动将独立 cell instance 到目标 layout

## 关键文件

- **`/home/jzeng/Desktop/IMCleAutoVia.py`**: 117,228 bytes / 2,149 lines — pyAether layout 自动化脚本（GUI + Flow class + V4 pre-GDS 逻辑）
  - V4 调用入口: line 635 `self.IMCleGenV4Pads()` (在主 flow 的 genViaCellList check 之后)
  - DRC deck 分发: lines 680-750 (按 process 复制对应 .drc deck)
  - techdb 初始化: 在 pwrnet 循环内部 (~line 942 区域有 `global techdb`)
- **`/home/jzeng/Desktop/V4_gen_M4M5.py`**: 中间独立脚本（agent 分步交付的第一步），最终 126 行/5,398 bytes

## Assistant 的方法与发现

### 分析阶段 (A#7-A#22)
- 完整读取 IMCleAutoVia.py，理解 GUI/Flow class/V4 pre-GDS 结构
- 识别 V4 pre-GDS 区域（原 lines 634-701）的 4 个问题：
  1. **没有按宽度过滤** — 选取所有 M4/M5 矩形，不论宽度
  2. **创建固定 2×2um 方块** — 未根据过孔阵列尺寸对齐
  3. **没有创建 y6.drawing 标记层** — DRC 转换流程（`cxmt_layout_convertYlayerToPcell`）无法生成 V4 via
  4. **via 创建时机不对** — 直接调用 `IMCleCrtViaAndSetDefOverrideEx` 但 `techdb` 尚未初始化

### 修复迭代 (A#28-A#601, 约 15+ 轮)
1. **宽度过滤**: 0.55um ±0.02um tolerance，`min(w,h)` for Rect（正确识别长走线线宽），`emyPathGetWidth()` for Path/pathSeg
2. **对象类型支持**: Rect + Path + pathSeg
3. **层次遍历**: 顶层 + 1 层子实例 (`_collect_wires` 遍历 `cv.instances`)
4. **y6 marks + labels**: 供 DRC pipeline 生成 V4
5. **独立 cell**: M4/M5 pads + y6 marks + V4 vias 全部画到 `ocv`（auto_via/<cell>_V4_CELL），不画到 `self.cv`
6. **不自动 instance**: 删除 `ae.dbCrtInst` 调用，用户手动 instance
7. **ASCII sanitization**: pyAether `load()` 以 ASCII 解码，所有非 ASCII 字符（em dash ≈ × → 等）替换为 ASCII
8. **GDS 导出精度**: `aeExportStream` 精度 1000 (1nm/DBU) vs DRC deck 需要 10000 (0.1nm/DBU) → 改用 `asOut`
9. **直接 V4 via 创建**: 在 V4 段提前初始化 techdb，用 `IMCleCrtViaAndSetDefOverrideEx` 直接创建

### 最终 bug (U#303, A#603-A#617)
- **SyntaxError**: `name 'techdb' is used prior to global declaration`
- 根因: V4 段（line ~702）加了 `global techdb` + `techdb = ae.techGetTechFile(...)`，但原方法后面（line ~942）也有 `global techdb`
- Python 规则: 同一作用域中 `global` 声明必须在变量的**任何使用之前**。V4 段先用了 `techdb`（line 720 `ae.techFindViaDefByName(techdb, ...)`），后面才 `global techdb`（line 942）→ 编译器报错
- agent 修复方案: V4 段不用 `global techdb`，改用本地变量名 `_v4_techdb`

## 三个核心根因 (for synthesis)

### RC1: M4/M5 生成在目标 cell 而非 auto_via cell
- **现象** (U#261, U#288): M4/M5 方块直接画在 `self.cv`（目标 layout）中
- **根因**: V4 pre-GDS 段的 `ae.dbCrtRect(self.cv, ...)` 使用了 `self.cv` 而非独立 cell 引用 `ocv`
- **修复**: 创建 `ocv = ae.dbCrtCV(self.autoViaLib, cellName+'_V4_CELL', 'layout')`，所有 shape 创建改用 `ocv`

### RC2: V4 未生成
- **现象** (U#280): 只生成了 M4/M5，没有 V4
- **根因 (双重)**:
  1. 没有 y6.drawing 标记层 → DRC pipeline (`cxmt_layout_convertYlayerToPcell`) 无法将 y-layer marks 转换为 V4 via pcell
  2. 直接 via 创建 (`IMCleCrtViaAndSetDefOverrideEx`) 依赖 `techdb`，但 `techdb` 在 V4 段执行时尚未初始化（它在后面 pwrnet 循环中才初始化）
- **修复**: (1) 添加 y6 marks + labels; (2) 在 V4 段提前初始化 techdb 或用本地变量

### RC3: SyntaxError — techdb global declaration
- **现象** (U#303): `SyntaxError: name 'techdb' is used prior to global declaration` at line 942
- **根因**: V4 段（line ~702）引入 `global techdb` + 使用 `techdb`，但原方法 line 942 也有 `global techdb`。Python 要求 `global` 声明必须在同一作用域中变量的任何使用之前。V4 段先使用 techdb（line 720），后面才 global 声明（line 942）→ 违反规则
- **修复**: V4 段改用本地变量 `_v4_techdb`，不声明 `global techdb`

## 合成计划 (DEBT — next round)

**case_id**: `AutoViaV4Diagnose-001` (C-A debug-Q&A/analysis-only)
**domain**: eda_other (pyAether layout automation)
**source-type**: pyAether script code-comprehension + bug diagnosis

### A files (trace-embedded, from IMCleAutoVia.py)
- A1: V4 pre-GDS 区域 (IMCleGenV4Pads method, 含 ocv 创建 + shape 生成 + techdb 使用 + global 声明)
- A2: techdb 初始化区域 (pwrnet 循环内 line ~942, 含 global techdb)
- A3: DRC pipeline 入口 (cxmt_layout_convertYlayerToPcell 调用, line ~1022)

### B (hidden, variant)
- B1: 同结构但变量名不同 (`_v4_techdb` vs `techdb`)，cell 名后缀不同 (`_VIA4_CELL` vs `_V4_CELL`)，宽度参数不同 (0.45um vs 0.55um)

### check() (≥14 条独立断言)
- RC1 诊断: 指出 `self.cv` vs `ocv` 错误 (a-c)
- RC2 诊断: 指出 y6 marks 缺失 + techdb 未初始化 (d-g)
- RC3 诊断: 指出 global declaration 顺序错误 + Python 作用域规则 (h-j)
- evidence verification: 引用具体行号/变量名 (k-l)
- B judge self-check: 隐藏 B 变体独立解析 (m)
- 3-seed randomization (n)

### 交付物
`autovia_v4_diagnosis_report.json` (结构化诊断报告)

### 自验
- ref 解 PASS (≥14/14)
- ≥5 negative FAIL (naive stub, always-pass, wrong-RC, partial, print-only)
- §4.9 三假提交全 FAIL

## trace_avail
EXISTS on .75: /home/jzeng/Desktop/IMCleAutoVia.py (117KB, 2149 lines, readable as e0031982)
EXISTS: /home/jzeng/.cline/data/sessions/1794734620660_00p77/1794734620660_00p77.messages.json (2.8MB)

## 备注
- 本轮 DEBT: deepread 完成, 合成未完成 (2.8MB trace + 2149-line script 需仔细提取 A files)
- 下轮优先: 提取 IMCleGenV4Pads method 完整代码 → 合成 AutoViaV4Diagnose-001
- infra 确认: eda_flow run_commands 可读 .75 本机文件 (whoami=e0031982, hostname=hfhds201)
