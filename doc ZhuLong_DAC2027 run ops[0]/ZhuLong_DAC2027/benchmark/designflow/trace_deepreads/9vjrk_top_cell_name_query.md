# deepread: 9vjrk — top cell name query (trace-faithful A-grade)

- session: `1792031877409_9vjrk`
- user: e0014566 @ hfeg0pkn001 (10.129.2.10)
- mc=17, keywords: cellview:120;ddgetobj:25;virtuoso:9;schematic:3;dbget:2;pyaether:1
- 12 msgs, 38KB messages.json, single-turn closed-loop
- domain: schematic_netlist (D-pure, D-confirm per pool_domain_audit)

## User verbatim (U#0)
```
请返回当前top cell的名称，使用virtuoso skill的API接口，使用run code工具执行
```
意图：用 Virtuoso SKILL API（经 run code 工具执行）返回**当前 top cell** 的名称。
注意：这是「当前 top cell」——用户在顶层，不在 in-place 编辑子 cell。
所以 top == displayed == edit cellview，三者相同。
（对比 r866 TopCellNameResolver-001：那个 trace 有 in-place 编辑场景，
top ≠ edit ≠ displayed；本 trace 无此 nuance，是更纯粹的「取顶层 cell 名」任务。）

## Assistant tool chain
1. `RAG_MCP_Server__search_apis` × 2 — queries: "get current top cell name", "get current design library cell"
   - 候选: hdbGetTopCellName(sim 0.66, 需 configId → 不适用), geGetTopLevelCellView(sim 0.64, 正确), cpfGetReferenceLibCells(噪声), ddsGetCurrentLib(噪声), cpfFindReferenceLibs(噪声)
2. `RAG_MCP_Server__get_api_details` — [geGetTopLevelCellView, geGetWindowCellView, ddGetObj]
   - geGetTopLevelCellView([w_windowId]) => d_cellview/nil, 顶层 cellview, 例 `geGetTopLevelCellView(hiGetCurrentWindow())`
3. `RAG_MCP_Server__search_apis` — "cellView of current window libName cellName"
   - 候选: geGetWindowCellView(sim 0.77, 返回 displayed 不是 top → 干扰项), geGetWindowRep(alias), geGetCellViewWindow(reverse lookup), lmSimView, deOpenCellView
4. `SandBox_MCP_Server__run_code` (lang=skill) — 首次 FAIL:
   ```skill
   cv = geGetTopLevelCellView(hiGetCurrentWindow())
   if cv then            ;; *Error* if: empty then clause - if(cv then)
     printf("Top cell name: %s\n" cv->cellName)
     ...
   ```
   error: `*Error* if: empty then clause - if(cv then)` — SKILL 多行 if/then 解析失败
5. `SandBox_MCP_Server__run_code` (retry, lang=skill) — SUCCESS:
   ```skill
   cv = geGetTopLevelCellView(hiGetCurrentWindow())
   when( cv
     printf("Top cell name: %s\n" cv->cellName)
     printf("Full path -> lib: %s, cell: %s, view: %s\n" cv->libName cv->cellName cv->viewName)
   )
   unless( cv
     printf("No top-level cellview found (current window empty or undefined)\n")
   )
   ```
   output:
   ```
   Top cell name: TrimDelay
   Full path -> lib: drjqa_stdcells, cell: TrimDelay, view: schematic
   ```

## Gold standard (用户实际接受的结果)
- top cell name: **TrimDelay**
- lib: **drjqa_stdcells**, view: **schematic**
- core API: `geGetTopLevelCellView(hiGetCurrentWindow())` + `~>cellName`/`~>libName`/`~>viewName`
- 关键教训：SKILL 多行 `if(cv then ...)` 解析失败 → 改用 `when(cv ...)` 成功
  （这是 A-grade trace-faithful 的真实 debugging 信号，纳入 check 断言）

## Distinction from r866 TopCellNameResolver-001 (B-grade)
| 维度 | r866 (B-grade) | 9vjrk (A-grade, 本 case) |
|---|---|---|
| prompt | synthesized w/ in-place editing scenario | verbatim 用户原话 |
| scenario | top ≠ edit ≠ displayed (3 cellview 区分) | top == displayed (无 in-place, 纯取顶层) |
| 干扰项 | edit/displayed cellview (geGetWindow/EditCellView) | hdbGetTopCellName(需 configId) + geGetWindowCellView(返回 displayed) |
| SKILL 教训 | — | `when()` guard (if/then 解析失败) 纳入断言 |
| grade | B | A (trace-faithful) |

## Reframe (L1, Python on JSON spec)
SUT 写 `top_cell_name_query.py`，读 window_spec.json + rag_results.json，
产 `top_cell_report.json`：top_cell + window_info + skill_api_guide(top_cell_apis + example_skill_script with when() guard)。
Hidden B 换 cellview (TopAmp/primitivesLib) + B2 null-top 边界。
