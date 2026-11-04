# deepread: lj2gw (e0014566 / hfeg0plg58 / mc393)

**session**: `/home/e0014566/.cline/data/sessions/1786535933950_lj2gw/1786535933950_lj2gw.messages.json` (1.4MB / 377 msgs)

## 用户意图（A-faithful 提需求轮 = U#0 / MSG0，逐字原文）
> 请你帮忙看下  Library : auto_austin_case1 , Cell : Array16G_B, View : layout, 这个版图。我现在要用rscalc计算电阻，看看其powernet 上的RTEXT，以及RNODE有没有打齐，没有的话，帮忙打上。既然不能修改原本的layout, 请先原封不动拷贝一份这个layout, 然后分析，然后打上RTEXT RNODE，RNODE的量控制在30个左右。

U#1（MSG1）是流程修复轮（"拷贝下来不能再编辑了，想别的方案：拷贝先不保存，把 RTEXT/RNODE 一并写入再保存"）——按 A 档规则**不取作任务说明**（属给出修复方案）。U#2（MSG2）"projname:train, version:V0_Austin" 是环境补全。后续轮均为调试/重试。

## agent 工具链
1. RAG search_apis/get_api_details 大量检索 pyAether API：dbCopyCellView / leGuiMeasureResistance / aeGetCurDesign / dbOpenCV(=dbOpenCellViewByType) / aeCreateText / emyShapeGetNetName / emyNetGetBBox / emyDesignSave / getBBox / emyNet / emyBlock 等。
2. run_commands / read_files 读 `/home/e0014566/test_layout_rscalc_flow_11/` 下既有流程文件：prompt_flow.md、rscalc.config、rscalc_work/add_rtext_rnode_sampled.il、check_rtext_rnode.il、virtuoso-rscalc-runner/assets/run_rscalc_nogui.il、verify_result.il、rscalc_work_ai/test_edit.log。
3. editor 写 `add_rtext_rnode.il`（先因 old_text 冲突失败）→ 改写 `add_labels_batch.il`（两次 editor：part1 创建 + part2 在 line 70 insert）+ `add_labels_batch.cmd`。
4. run_commands 启动 Virtuoso 批处理：`env -u ARGUS_HOME _CXMT_SH_PROJ_WRITE_CHECK=1 OA_UNSUPPORTED_PLAT=linux_rhel50_gcc48x LD_PRELOAD=/usr/lib64/libstdc++.so.6 virtuoso -nograph -replay add_labels_batch.cmd -log ...`。
5. SandBox_MCP_Server__run_code(lang=skill) 在沙箱里 `foreach(cv dbGetOpenCellViews() dbClose(cv))` 清句柄；最终写 `all_in_one.il`（拷贝+加标签+保存+验证一进程）重跑。

## 关键产物（金标来源 = add_labels_batch.il / all_in_one.il，editor new_text 全量提取）
核心算法（SKILL `procedure(AddRtextRnode)`）：
- `dbOpenCellViewByType(libName cellName viewName "" "a")`
- 遍历 `cvId~>terminals`，过滤 `member(termName powerNets)`（vcc!/vss!/viso!），去尾 `!` → netNameNoBang
- 收集 pin figs：`foreach(pin term~>pins foreach(fig pin~>figs ...)`，取 bbox 中心 (cx,cy) + `car(fig~>lpp)` figLay，cons 成 pinList
- `sort(pinList '(lambda (a b) car(a) < car(b)))` 按 X 升序
- **RTEXT**：每网 1 个（按 `netNameNoBang_pinLay` 去重），`dbCreateLabel(cvId list(pinLay "RTEXT") list(minX pinY) netNameNoBang "centerCenter" "R0" "stick" 1.0)`，落最左 pin
- **RNODE**：`nextSampleX = minX`；遍历排序后 pin：`isEdge = |pinX-minX|<0.01 || |pinX-maxX|<0.01`，`isSample = pinX >= nextSampleX`；命中则 `dbCreateLabel(cvId list(pinLay "RNODE") list(pinX pinY) netNameNoBang ...)` 且 `nextSampleX = pinX + sampleStep`（sampleStep=3500.0）
- `dbSave(cvId)` + `dbClose(cvId)`

`all_in_one.il` 同算法但加 `dbCopyCellView(srcCv libName destCell viewName t)` 前置拷贝。

## 真实运行结局
trace 末尾 agent 反复受 **CXMT 写权限系统**阻塞：`dbOpenCellViewByType "a"` 模式 `isEditable: nil`，`test_edit.log` 报 "Can't find corrent username projname nil vername nil - Warning: Please contact CAD to get permission."。批处理日志声称 `Created: RTEXT=3 RNODE=31 / dbSave returned t`，但**全新 Virtuoso 进程验证显示 `Total labels: 0 / RTEXT=0 / RNODE=0`**——标签未真正持久化。trace 在 MSG165 仍重跑 all_in_one 未结，**无用户接受的运行产物**。金标因此取**脚本逻辑结构**（add_labels_batch.il / all_in_one.il），降级为 L1-boundary 确定性生成器。

## 合成决策
- **A 档 trace-faithful**：任务说明 = U#0 逐字。金标 = SKILL 逻辑（RTEXT 每网 1 + RNODE edge+step 采样），重建为 config-driven 生成器 `gen_rtext_rnode.py`，输出 `add_labels.il`（baked dbCreateLabel）+ `rtext_rnode_plan.json`。
- **A**（可见）：auto_austin_case1/Array16G_B_rscalc/RDL/step=3500/vcc!+vss!+viso!（11/11/9 pin）→ RTEXT=3 RNODE=31（与 trace 报告一致）。
- **B**（hidden）：pwr_grid_eval_b/PwrMeshB_rscalc/M1+M2/step=4200/vdd!+gnd!+vbb!+vref!（14/14/8/5 pin）→ RTEXT=4 RNODE=29（~30，贴合用户"30 个左右"目标）。结构与 A 显著不同（lib/cell/层数/层名/步长/pin 几何）。
- check.py 15 条件 a-o，subprocess 真跑生成器于 B，断言 SKILL 结构 + plan 数值 + 跨输入护栏 + 确定性 + 步进采样证明。
- 6... 实为 3 negatives（empty/print_fixed_A/core_deleted）distinct c/e/f。
