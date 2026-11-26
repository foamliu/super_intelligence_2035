# deepread · h8hlb · hier-path occurrence callback 解析

> session: `1794540105944_h8hlb.messages.json` · user `lizwen` @ `hfeg0pkn003` · mc=18
> domain: layout_aether (pyAether + dbGet + cellview) · 19 msgs (2 user / 2 assistant text + tool calls)
> snapshot: `/home/lizwen/.cline/data/sessions/1794540105944_h8hlb/` (live + 2026-11-16 hourly snapshot)

## 用户意图（逐字）

- **U#1**：粘贴一段遍历 `data.hierPath.refs` 拼 `inst_name`（带 `(row x col)` 阵列后缀）+ `ae.dbConcatTransformF` 累乘变换的代码片段，问：
  > 「怎么会有row col」
- **U#2**：粘贴**完整** `funcCb(self, data)` 回调，问：
  > 「解析这段」

`funcCb` 语义：对每个 occurrence 收集三样东西——
1. **instName**：沿 `hierPath.refs` 逐级 `"/"+name`，`row>0 or col>0` 时加 `(row x col)`；
2. **trans**：`dbConcatTransformF(ref.transform, transform)` 累乘；若该级是阵列单元（row/col>0），按 `transform.orient()`（R90/R180/R270/MY/MX/MYR90/MXR90 七种，R0 不修正）对 `(deltaX,deltaY)` 与 `(row,col)` 做朝向修正后 `x+=col*dx, y+=row*dy`，orient 不变；
3. **box**：`data.getBBox(box)` → `emyDbu2UU(cv, box, boxF)` DBU→UU。

## agent 行为
- 全程 `RAG_MCP_Server__search_apis` / `get_api_details` 检索 pyAether API 文档（emyHierPath / pushLevel / getLevel / dbConcatTransformF / emyTransformF / emyDbu2UU）。
- A#12 回答 U#1：「row/col 是阵列实例(ArrayInst/mosaic)的行列索引，hierPath 每级是 (ref,row,col) 三元组唯一定位 occurrence」。
- A#18 回答 U#2：分 6 段解析 funcCb（整体流程 → 前置过滤 → 名字拼接 → 变换累乘 + 阵列偏移修正 → bbox 收集 → 追加 self.hier_path_info）。
- **纯 Q&A / analysis 任务，无脚本交付**（agent 全程只检索 + prose，无 run_code / write）。

## 11-15 task 初心判定
- 旧规则：analysis/explain 类判 weak → parked。
- 新标准：「explain 类」「analysis-Q&A」**全部恢复为可造**（11-15 令 §一/二）。
- 本 session 有真实 trace（trace_source 齐全）+ 能写出有牙 check()（reframe 为 compute 累加器）→ **可造 ✓**。

## reframe（mock-behavioral · B 档 synthesized）
- 真实任务 path-dependent（需真 Aether hierPath 遍历 + pyAether SWIG），reframe 为**纯 stdlib 层次路径 occurrence 信息累加器**。
- 新子型 `hier-path-occurrence-transform-accumulate`：(a) source-to-source family 的 geometry-compute 变体（承 r705 ViaFeasWidenPlan）。
- fixture = hierPath 规格 JSON（各级 name/transform{orient,px,py}/row/col/deltaX/deltaY + leaf_bbox_dbu + dbu_per_uu）；candidate = 实现 accumulate → {instName, trans{orient,px,py}, box{xl,yb,xr,yt}}。
- **teeth 锚点**：8-orient 阵列偏移修正（R90 互换+dx取反 / R180 双取反 / R270 互换+dy取反 / MY dx取反 / MX dy取反 / MYR90 互换+双取反 / MXR90 互换）+ D4 群串联 compose 表 + instName 阵列后缀 + bbox DBU→UU 旋转平移。每朝向各可独立 FAIL。
- distinct vs r705（via feasibility+widening 矩形几何）= 本例层次变换累乘 + 阵列偏移 + bbox 变换。

## 交付（DoD）
- case_id: `EDA-Eval-DesignFlow-HierPathOccurInfo-001`（layout_aether, L1, B 档, k=21）
- assets: hierpath_A.json (visible) + hidden/hierpath_B.json + hidden/hierpath_B2.json + prompt.txt + task_brief.md
- reference: check.py (21-cond) + reference_solution.py + negative/{stub_empty,stub_print_expected,stub_delete_core}.py + negative_selftest.py
- 自验：reference 21/21 PASS；3 negatives 全 FAIL（empty 7/21 / print-expected 7/21 / delete-core 15/21）
- EDA-Eval-DesignFlow_C.jsonl 438→439

## collision audit
- 4-shard jsonl grep `h8hlb|1794540105944` → 0 hit（无跨 shard 收割）。
- 与 r706 CadToolCliRefactorAudit-001（steveny/test_layout_rscalc_flow_19）不同 user、不同 session、不同域（r706=physical_verify 文档关联+CLI 审计；本例=layout_aether hierPath 变换累乘）。
