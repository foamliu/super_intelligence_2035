# trace_deepread: ijgow (layout_virtuoso) — LayerShapeDeleteCount-001

**Session**: `1782819860572_ijgow` (user `e03179` @ `hfeg0plg15` / 172.16.8.191, mc=23)
**Date**: 2026-04-09
**Domain**: layout_virtuoso (版图 = layout, explicit)
**Selected**: r715 round (2026-11-17), first viable fresh C-domain candidate with real editor/write_file/sandbox_run activity

## Selection rationale (r715)

r714 报「可达 fresh 池 mc≥10 对 C-domain produce-deliverable 任务本轮实质耗尽」（14 deepread 全 false-positive: PDK-release-note / GUI 启动 / 快捷键 Q&A / doc 索引 / skill 元任务 / analysis-only / run-existing）。

r715 改选料策略：**按 tool_total 排序**（真实工具调用数，非纯 mc keyword 计数），优先有 `editor/write_file/SandBox_run_code` 落盘真实脚本内容的 session。

从 248 fresh C-domain 候选中按 tool_total 排序，前 25 多为 PDK-release-note（xinqiaoz）/ netlist extraction（D 域）/ GUI 启动（miccao yavow）/ run-existing（e0014566 djvnv）/ steveny cluster（已 r706 避让）。

**ijgow (e03179, mc23, 85 cellview + 18 skill + 10 dbGet + 8 dbGet_tools)** 进入候选：keyword profile `cellview:244 dbget:37 schematic:21` 看似 schematic 域（D），但 **U#0 原文「删除当前版图在所有M1的图形」** 明确"版图"（layout），且 agent 实际调 `geGetTopLevelCellView` + `dbStartGenLPToShape(cv list("M1" "drawing"))` + `dbDeleteObject` —— **真实 layout 按层批量删除图形操作**，属 C-shard layout_virtuoso。

并行深读的 4 个候选 deepread 结论：
- **dm280** (ellawu mc38 225 calibre): U#0 粘贴代码片段 + U#12 pinyin「duishuyu cxmtG4C xiangmude drgqx rangtadexunxing follow drvsa」(给 cxmtG4C 项目的 drgqx 让其 follow drvsa 模式) — agent 搜不到 drgqx/drvsa，ask_question 超时，**意图模糊不可交付**，parked
- **u2kcz** (minjiex mc29 61 cellview): U#0「怎么能快速的将大量gds导入virtuoso中」— **Q&A/prose 回答无落盘**，11-15 B类可造但 check 牙弱，parked 备选
- **k3qx4** (e0014566 mc34 155 cellview): U#0「在Schematic中,帮我高亮当前打开的设计图中所有名称以\"net开头的线」— **明确 Schematic 域**（非 layout），属 D-shard，parked
- **pcb1x** (e03179 mc31 113 cellview): U#0「抓取当前打开的电路中所有的Pin List」— agent 用 schSchemToPinList/schSymbolToPinList/schGetPinOrder **schematic 域 API**，属 D-shard，parked
- **1r058** (e0014566 mc23 90 cellview): U#0「请返回高亮当前的mos管」— schHiHiliteLabel（schematic-only）+ e0014566 已饱和，parked
- **ijgow** (e03179 mc23): **VIABLE ✓** U#0「删除当前版图在所有M1的图形...使用skill语言生成代码并执行」— 真实 layout 批量删除 + 计数 + 写文件

## Trace 解析（ijgow, 42 msgs, 1 user text turn）

### User 原话（U#0，逐字）
> 删除当前版图在所有M1的图形。统计删除图形的数目，并保存到本地的当前目录下的一个文件中。使用skill语言生成代码并执行。

### Agent 工具链（42 msgs）
1. **RAG search_apis** ×8: `delete all shapes in layer` / `get current design cellview` / `count number of shapes` / `get all shapes on layer M1 in cellview` / `dbGetq layer purpose shapes list` / `dbDeleteObject delete shape` / `setof fi...`
   - 返回：abeClearLayer / pcDeleteParamLayer / leEditDesignProperties / leComputeAreaDensity / **dbStartGenLPToShape** / leHiQuery / **dbDeleteObject** / pteGetLayerSetMembers / **geGetTopLevelCellView**
2. **RAG get_api_details**: geGetTopLevelCellView, dbStartGenLPToShape, dbDeleteObject, dbGetq
3. **run_commands**: `pwd` → `/home/e0025768/devops/bundle`
4. **SandBox_MCP_Server__run_code (lang=skill)** ×7:
   - **[13] 主删除脚本**（成功）:
     ```skill
     cv = geGetTopLevelCellView()
     if(cv then
         lpp = list("M1" "drawing")
         gen = dbStartGenLPToShape(cv lpp)
         count = 0
         ; Collect all shapes first (to avoid issues with deletion while iterating)
         shapes = nil
         while(shape = gen~>next
             shapes = cons(shape shapes)
         )
         dbStopGen(gen)
         shapes = reverse(shapes)
         foreach(shape shapes
             dbDeleteObject(shape)
             count = count + 1
         )
         outfile = outfile("./deleted_m1_shapes.txt" "w")
         fprintf(outport "Deleted %d M1 shapes.\n" count)
         close(outport)
         printf("Successfully deleted %d M1 shapes. Result saved to ./deleted_m1_shapes.txt\n" count)
     )
     ```
   - **[14] 输出**: `Successfully deleted 1 M1 shapes. Result saved to ./deleted_m1_shapes.txt`（沙盒里当前 cellview 只 1 个 M1 图形）
   - [15-32] 验证文件存在的多次 SandBox 调用全失败：`infile` 参数错误、`Unknown SKILL error`、`Connection refused by sandbox [pyAether] at 10.129.32.75:55209` —— **沙盒服务后续不可用**
   - [35] 改 pyAether 也失败（同 connection refused）
5. **run_commands**: `ls -la /home/e0025768/devops/bundle/deleted_m1_shapes.txt` → `File not found on local filesystem`（沙盒文件不在本地 FS）
6. **editor**: 保存最终 SKILL 代码到 `/home/e0025768/devops/bundle/delete_m1_shapes.il`
7. **最终 prose 总结**: 共删除 1 个 M1 图形 + 写入 `./deleted_m1_shapes.txt` 内容 `Deleted 1 M1 shapes.`

### 真实交付（gold）
- SKILL 脚本 `delete_m1_shapes.il`：geGetTopLevelCellView + dbStartGenLPToShape(cv list("M1" "drawing")) + 遍历收集（避免迭代中删除问题）+ dbDeleteObject + fprintf 写文件
- 输出文件 `./deleted_m1_shapes.txt`：内容 `Deleted 1 M1 shapes.\n`
- 执行结果：删除 1 个 M1 图形

## Reframe（mock-behavioral · 新子型 `layout-layer-shape-delete-count`）

真实 Virtuoso + SandBox_MCP_Server__run_code path-dependent（需 OA 环境、cellview 依赖 GUI 状态、沙盒服务后段故障）→ **纯 stdlib Python** 操作 **JSON mock cellview**：

| 真实 | mock-behavioral |
|---|---|
| geGetTopLevelCellView() | json.load(mock_cv.json) → cv["shapes"] |
| dbStartGenLPToShape(cv list("M1" "drawing")) | filter shapes by lpp[0]=="M1" |
| dbDeleteObject(shape) | remove shape from list |
| fprintf(outport "Deleted %d M1 shapes." count) | write to argv[3] path |
| printf(...) | print(json.dumps(result, sort_keys=True)) |

**distinct vs r711 SkillPatternDecoordinate**: r711 = SKILL 图案 .il 去坐标参数化推断 + 几何一致性校验；本例 = **layout 按层批量删除图形 + 计数文件 + JSON 摘要**（无参数化推断、无几何校验，是删除操作 + 计数 + 写文件）

**11-15 B 类复活**：U#0 是"删除 + 统计 + 写文件"的**实际操作任务**（非 analysis-only），但旧规则可能因 mock 化判为 weak，新标准合法。

## Fixture 设计

| Fixture | 层 | 总 shape | 删除数 | 总后 | 输出内容 |
|---|---|---|---|---|---|
| A (visible) | M1 | 12 | 4 | 8 | `Deleted 4 M1/drawing shapes.` |
| B (reverse A) | M2 | 15 | 8 | 7 | `Deleted 8 M2/drawing shapes.` |
| B2 (edge) | M3 | 6 | 0 | 6 | `Deleted 0 M3/drawing shapes.` |

A∩B∩B2: layer (M1/M2/M3) / total (12/15/6) / deleted (4/8/0) / shape_ids 全异 / bBox 全异 / process (cxmt10G4plus/cxmtG4C/cxmtV3) 全异 → **抗硬编码** ✓

## check() 21 条件 (a-u)

a. zip valid + .py present
b. py_compile passes
c. B run exit 0 + valid JSON + 10 top-level keys
d. B layer==M2, purpose==drawing (early check, catches hardcoded-A stub)
e. B deleted_count==8 (oracle)
f. B total_before==15, total_after==7 (oracle)
g. B remaining_layer_counts has no M2 key + sum==7
h. B remaining_layer_counts == oracle exactly
i. B deleted_shape_ids == oracle (8 ids, ascending)
j. B remaining_shapes_preserved == True
k. B output_file created at specified path
l. B output_content matches "Deleted 8 M2/drawing shapes.\n" (JSON + disk)
m. B2 run exit 0 + valid JSON + keys
n. B2 deleted_count==0, total_before==total_after==6
o. B2 remaining_shapes_preserved==True, deleted_shape_ids==[]
p. B2 output_content == "Deleted 0 M3/drawing shapes.\n"
q. determinism: B rerun (same args) byte-identical sorted JSON
r. anti-hardcode: B values match oracle AND differ from A (M1/4/12)
s. anti-hardcode B2: 0 deletes differs from A(4) and B(8)
t. degenerate guard: empty→c / print-A→d / no-delete→e (3 distinct first_fails)
u. B output_file path echoed correctly in JSON

## 自验结果（r715）

- reference_submit.zip: **PASS 21/21** ✓
- neg_stub_empty.zip: **FAIL**, first_fail = `c_run_B_json` (json) — 空壳无 stdout
- neg_stub_print_expected.zip: **FAIL**, first_fail = `d_B_layer_purpose` (layer_purpose) — 硬编 A 的 layer=M1
- neg_stub_delete_core.zip: **FAIL**, first_fail = `e_B_deleted_count` (deleted_count) — 不删除只打印 deleted_count=0
- **3 negatives distinct first_fails** ✓ (json / layer_purpose / deleted_count)
- k_rationale == k_check == 21 ≥ 8 GATE PASS ✓
- jsonl test 字段 round-trip PASS ✓ (extract→check.py→run reference_submit.zip→CHECK PASS 21/21)
- A/B/B2 三 fixture 解析正确 ✓ (手算: A 删 4 M1 / B 删 8 M2 / B2 删 0 M3)
- 确定性 2x ✓ (相同 args 重跑字节一致)
- 抗硬编码 A∩B∩B2 全异 ✓
