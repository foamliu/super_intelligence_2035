# Deepread: 131n4 — zhiguo1w Calibre SVRF mask-block TCL 脚本族解析

**Session**: 1793175276412_131n4 (zhiguo1w@hfeg0pjn200, mc=46, physical_verify)
**Trace**: 47 msgs / 24 real user turns / 23 assistant turns / 340KB (via .75 scp from 10.129.40.209)
**Date**: 2026-11-16 (r633)

## 用户意图（逐字原文，真实用户轮）

zhiguo1w 是一位版图/DRC 工程师，正在研读一组 **Calibre TVF/SVRF mask-block 定义 TCL 脚本**（DRC 验证 deck 的 mask阻挡块定义工具链）。用户逐个上传 TCL 脚本，要求 agent 解析函数功能、算法原理、脚本间关系。

核心用户轮序列：
- UI#0/#1: "解析该脚本的各个函数功能及算法原理" + defineMaskBLK.tcl
- UI#2: "解析函数，并分析与上述maskBLK的区别" + defineMainBLK.tcl
- UI#3: "解析该脚本所有函数，并和上面的函数进行链接" + defineEmpty.tcl
- UI#4: "分析该脚本函数，并与上述三个脚本的关系" + defineRunOut.tcl
- UI#5: "angleBLK是什么输出结果"
- UI#6: "分析里面的函数，以及seligattern和origin的作用" + GenLine.tcl
- UI#7: "分析两个脚本各自函数的作用和相互之间的区别联系" + FILL_Dum.tcl + FILL_Dum_LR.tcl
- UI#8: "分析脚本中的函数" + SelectBigArea.tcl + SelectBigLength.tcl
- UI#9: "所以是先生成出垂直和水平方向的所有可以添加的dummy，在进行判断选择哪种？垂直和水平的dummy能共存吗"
- UI#10: "判断选择方向本质是比的什么参数"
- UI#11: "这里加dummy的逻辑是什么，为什么多次加dummy" + GenLine.tcl
- UI#12: "解析函数" + CutMaxLen.tcl
- UI#13: "MergeAndCutLine" + MergeAndCutLine.tcl
- UI#14: "该脚本的作用" + GenCMP_LINE.tcl
- UI#15: "解析Enlargeineidth函数" + EnlargeEdgeToGen.tcl + EnLargeLineWidth.tcl
- UI#16: "继续分析" + EnlargeEdgeToBLK.tcl + EnlargeRectEdgeToBLK.tcl
- UI#17: "继续" + EnlargeRectEdgeToBLK_oneOrient.tcl + SplitEdgeOrient.tcl
- UI#18: "解析" + drcForbidSpace.tcl
- UI#19: "分析" + outDRC.tcl
- UI#20: 贴 defineMainBLK_info proc 代码片段
- **UI#21**: "分析该脚本如何将BLK的信息写入SVRF，共写入了那些信息" + defineMaskBLK.tcl ← **核心 produce-task（本 case 选题）**
- UI#22: "defineMaskBLK_Info函数的作用"
- UI#23: "不同的bol会带来什么不同的定义语句，分别在版图上如何表现"

## 本 case 选题：UI#21

UI#21 是一个具体的 **grounded extraction** 任务：分析 defineMaskBLK.tcl 如何把 BLK（mask 阻挡块）信息写入 SVRF，写入了哪些信息。用户接受的 gold answer（ASST#0, msg 42）给出了结构化分析：

### SVRF 写入的两种调用
| 调用 | 写入的 SVRF 内容 |
|---|---|
| `tvf::SETLAYER` | 层派生语句（赋值/布尔/几何变换） |
| `DefineLayer` | LAYER 声明 → `<lpp> <层名>` 映射 |

### defineMaskBLK.tcl 的 6 个 proc
1. `defineMaskBLK` (4 params: name mask pList maskBLK) — 主入口：读 maskInfo（GRID BORD BLK_OR BLK_AND BLK_AND2 BLK_IGNORE cmpLay Lwidth Width Height），处理 BLK_OR/BLK_AND/BLK_AND2，计算 Wmin，输出 DefMaskBlk via SETLAYER OR/SIZE/COPY
2. `FixValueSizeGrid` (3 params: value grid outValue) — 值对齐到 grid
3. `defineMaskBLK_AND` (5 params: name BORD blockList layNum outLay) — AND 链迭代
4. `defineMaskBLK_info` (4 params: name BLK_TYPE pList blockList1) — 参数→几何层翻译器，逐条解包 BLK 配置（type/pname/lpp/bol/space），注册层 + 忽略扣除 + 几何变换
5. `defineMaskBLK_ignore` (4 params: name layGen pList outGen) — BLK_IGNORE 处理，NOT 扣除
6. `defineMaskBLK_infoType` (8 params: name layGen BORD bordSpace Mspace bol space outLay) — **核心 bol 调度器**，9 种 bol 分支

### 9 种 bol 分支（defineMaskBLK_infoType）
| # | bol 取值 | 匹配方式 | 核心 SVRF 操作 |
|---|---|---|---|
| 1 | `""` (空串) | exact `==` | SIZE |
| 2 | `BORD NOT` | exact `==` | NOT (+SIZE) |
| 3 | `BORD NOT OR` | exact `==` | NOT + OR (+SIZE) |
| 4 | `BORD NOT_ignore m` | regexp | NOT + NOT (+SIZE) |
| 5 | `BORD NOT_ignore m1 m2` | regexp | NOT + OR + NOT (+SIZE) |
| 6 | `OR HOLE` | exact `==` | OR + HOLES (+SIZE) |
| 7 | `edge*` | string match | NOT + SIZE + OR |
| 8 | `ignore*` | string match | NOT (+SIZE) |
| 9 | `BORD NOT WxH` | regexp | SIZE + RECTANGLE + NOT |

### SVRF 操作类型清单
tvf::SETLAYER 中出现的 SVRF 几何操作：OR, SIZE, COPY, AND, NOT, HOLES, RECTANGLE
DefineLayer：LAYER 声明

### BLK 类型变量
BLK_OR, BLK_AND, BLK_AND2, BLK_IGNORE（在 maskInfo 中读取）

### 输出层名模板
DefMaskBlk_$name, DefMaskBlk_preDRC_$name, defineMaskBlk_OR_$name, blk_and_$block, size_$name, BORD_NOT_$name 等

## Case 设计（B档 grounded-extraction-tool reframe）

- **case_id**: MaskBlkSvrfWriteExtract-001
- **domain**: physical_verify
- **tier**: L1-boundary
- **档位**: B (synthesized, mock-behavioral grounded-extraction-tool)
- **deliverable**: `maskblk_svrf_analyzer.py <script.tcl> <output.json>` — 解析 Calibre TVF/SVRF TCL 脚本，提取结构化 JSON（proc 清单 / tvf::SETLAYER 调用清单与操作计数 / DefineLayer 计数 / BLK 类型变量 / bol 调度分支 / 输出层名模板）
- **asset A**: defineMaskBLK_a.tcl（真实 defineMaskBLK.tcl 逐字原文）
- **hidden B**: defineMaskBLK_b.tcl（合成变体：proc 名加 B 后缀 / BLK_AND3 替 BLK_AND2 / 删 OR HOLE+ignore* 加 BORD AND / 层名模板 DefMaskBlkB_）
- **hidden B2**: defineMaskBLK_b2.tcl（另一变体反硬编交叉校验）

承 r630 LvsHcellFailReportExtract + r631 LvsDeckErcStatusCheck grounded-extraction-tool 模式。

## 真实性归属
- trace_source: zhiguo1w@hfeg0pjn200, session 1793175276412_131n4, mc=46
- real_task_summary: 解析 Calibre SVRF mask-block 定义 TCL 脚本族（defineMaskBLK/defineMainBLK/defineEmpty/defineRunOut/GenLine/FILL_Dum/SelectBigArea/CutMaxLen/MergeAndCutLine/EnlargeEdge/drcForbidSpace/outDRC），逐个分析函数功能、算法原理、脚本间关系；核心问 defineMaskBLK.tcl 如何将 BLK 信息写入 SVRF（tvf::SETLAYER + DefineLayer + 9 种 bol 分支）
- 用户接受的 gold = ASST#0 msg42 结构化分析（2 种调用 / 5 大类信息 / 9 种 bol 分支表）
