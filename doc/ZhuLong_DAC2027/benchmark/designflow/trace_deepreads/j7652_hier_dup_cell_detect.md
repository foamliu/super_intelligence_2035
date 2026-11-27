# j7652 — laryu 跨库重复 cell 检测（design-review Q&A → 合成 case）

## trace
- `1795412906029_j7652.messages.json` · laryu @ hfeg0pkn001 · mc=317 · domain=schematic_netlist · FRESH
- 281 msgs (145 user / 136 assistant)。trace 获取：.75 ssh→hfeg0pkn001，per-session subdir 直读 682KB。
- 真实任务：用户(laryu)让 agent 解读自研 Aether py3 设计审查脚本族
  (`IMCutDesignReviewItems.py` / `IMCutHierarchyTraverser.py`) 中的若干函数与 API，
  核心围绕「跨库重复 cell 检测」：
  - `CXMTleSearchDupInstance_GetLibrary(cellView, cellTable)`：递归遍历 instHeaders，
    建 `cellName → libName` 映射（first-wins），经 `dbOpenCV` 进入子 cellView。
  - `IMCdbCheckBadDuplicateCB(cv, hierPath, comp)`：回调；用 `etMakeTable('cellTbl', False)`
    维护 `cellName.lower() → [lib1, lib2, ...]`；若 cellName 已出现在不同 lib，append 该 lib
    并报告 `"hierPath,lib,cell,view,libs joined by _VS_"`。
  - `IMCdbCheckBadDuplicate()`：主入口；开 `{cellName}_DuplicateCell_{_sch|_layout}.csv` 日志，
    调 `InnoutHierarchyTraverser` 跑该回调。
  - `InnoutHierarchyTraverser`：层次遍历引擎，维护全局 `IMCutHierarchyTraverserResultTable`。
  - 其余 Q&A：`etMakeTable` API 作用、`member` 用法、`global` 变量来源、`pullPin.py` 环境检查、
    SVRF 语法解释——分散，不合成。

## case 合成（synthesized-reframe）
- task_id=`HierDupCellDetect-001` · domain=schematic_netlist · LIVE-NA · judge_layers=[L0,L1] · 无 check_live
- reframe：把用户的「跨库重复 cell 检测」抽象为通用 spec-JSON 驱动
  `find_dup_cells.py(spec)->report.json` + hidden-B 反硬编码。
- spec schema：`{top, view, cells:{name:{lib, instances:[{inst,lib,cell}]}}}`；
  实例的 `lib` = 实例绑定库（非 cell 定义库），同一 cellName 可在不同位置被不同 lib 例化。
- 行为：递归展开实例树，记录每个 cellName 的 lib 集合 + 每次 occurrence 的 hierPath；
  ≥2 不同 lib ⇒ 重复；同 lib 多次不算重复；路径防环（(cellName,lib) 沿当前路径重复=环）；
  实例引用 cells 中不存在的 cell ⇒ error + valid=false。

## A / hidden B 设计
- **A**(visible) `spec_A.json`：ChipTop@TOP；dups = Amp(3 libs: AnaLib/IoLib/PwrLib)、
  BiasGen(2: AnaLib/AnaLib2)、Buf(2: AnaLib/PwrLib，**嵌套深层**——经 ClkDiv/u2/c1 与 Tree/u9/t3)；
  非重复：Inv(同 lib 2 次)、Leaf(同 lib 2 次)、ClkDiv、Tree、ChipTop。total_occurrences=14。
- **hidden B**(token-structurally 不同) `spec_B.json`：SysRoot@CORE；dups = VrefBuf(2)、
  Decoder(3)、Cap(2 libs，**嵌套深层**——Decoder×3 各带 Cap@Vlib + Branch 带 Cap@AnaCore，
  全展开 4 occurrence)；非重复：FF、Nand(同 lib 2 次)、Wire(同 lib 2 次)、Branch、SysRoot。
  total_occurrences=16。A 硬编码器在 B 全错。

## check.py 17 conds(a-q)
a zip 含 find_dup_cells.py ②b py_compile ③c A 运行 exit0 valid==True ④d A dup_count==3
⑤e A dup 集合=={Amp,BiasGen,Buf} ⑥f A Amp libs[AnaLib,IoLib,PwrLib] ⑦g A BiasGen libs[AnaLib,AnaLib2]
⑧h A Buf libs[AnaLib,PwrLib] ⑨i A Inv 不判重复 ⑩j A Leaf 不判重复 ⑪k A Buf 2 occ hierPath{ChipTop/u2/c1,ChipTop/u9/t3}
⑫l A total_occurrences==14 ⑬m A libs 去重+排序+lib_count==len ⑭n B 运行 exit0 valid==True
⑮o B 反硬编码{VrefBuf,Decoder,Cap}+libs+Cap 4 occ 路径+FF/Nand/Wire 不判重复 ⑯p 源码无 A/B token
⑰q malformed spec(引用不存在 cell)→valid==False+errors 非空。

## negatives(5)
empty→a / print_only→c / core_deleted→d（§4.9 trio distinct）+ hardcode_a→o + shallow_traverse→d（非递归漏 Buf）。

## 自验（全绿）
- ref check.py on reference_submit.zip → PASS 17/17
- negative_selftest 5 neg ALL-FAIL（trio all fail）
- SKIP_RUN=1 eval/run_one.sh workdir leak 自检通过（无 check.py/reference/hidden 泄漏）
- 3-way sha sync: disk==JSON test==metadata.check_sha256=c879de99c04da2c37c776c1e17e8a8fb4f6c12f55a1f7f36285f1505ed3a4d39 size=8883
- k_check=17=k_rationale=17
- 框架 auto-build D jsonl 595 case 含本条
