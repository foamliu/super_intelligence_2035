# trace deepread — sid 1792490325235_wvhcg (johnl @ hfeg0pfn119)

- mc=198, 293 msgs (159 user / 134 asst), 154 tool calls, 1.0MB messages.json
- session: 2026-10-20 09:58 → 10-21 02:12 (~16h), status=failed exit 1, model=deepseek-v4-flash, cwd=/home/johnl
- tools: editor×59, run_approved_command×38, read_files×22, RAG_MCP_Server__search_apis×16, RAG_MCP_Server__get_api_details×8, list_allowed_files×6, SandBox_MCP_Server__run_code×1, run_commands×1
- summary.tsv keywords: schematic:185 pyAether:151 dbGet:127 netlist:66 innovus:48 hspice:19 calibre:17 cellview:14 synthesis:3 → **pg_layout seed** (Innovus + pyAether db-access + stdcell OA audit)

## 真实任务（USER#0 原文逐字，纯意图，未给根因/修复 — A-档合格 seed）
> 先执行以下只读命令，定位现有 Aether 库、视图和技术库入口，不进行任何实现。… 1. 读取找到的库映射，确定真实库名、路径和技术库引用；2. 查阅目标机已安装的 Aether/PyAether 接口，用只读方式检查网表实际使用的单元：视图、放置边界、引脚及图形、阻挡、site、层和过孔；3. 输出对象清单及缺项，注明查询方法和证据；4. 目前只确认 OA 数据内容。不要放置、CTS、布线或修改库；不要把 OA 可读直接写成 Innovus 兼容。

USER#2-5 = "加油"/"继续"/"加油加油"/"继续继续"（鼓励/续做，非新意图）。

## agent 工具链（read-only OA 就绪性审计）
1. probe_env.sh / probe_libs.sh / probe_tech.sh — hostname/pwd/command -v、ls /proj/drcoa/V0/libs/drcoa_stdcell、readlink、find lib.defs/cds.lib/tech.db/*.tf/abstract/layout/*.oa
2. read_files /proj/drcoa/V0/lib.defs + cds.lib → 真实库映射（drcoa_stdcell → stdcells_ac，TECHLIB 引用）
3. RAG search_apis ×16 (pyAether): dbOpenCV / libOpenLib / dbGetAllCells / dbAllCellViews / prBoundary / site / obstruction / pin term layer / via / viaParam
4. SandBox_MCP_Server__run_code + probe_py.py (pythone) — 验 pyAether 加载、emyInitAether/emyInitDb/emyLibDefList.openLibs/dbOpenCV
5. inspect1-20.py (pyAether `mode='r'`) — emyInitAether('-adv')+emyInitDb()+openLibs('/proj/drcoa/V0/cds.lib')+dbOpenCV(stdcells_ac, cell, 'layout','r')，逐 18 单元提取 views/bbox/prBoundary/terms/shapes/byLayer/rows/instances/blockages/vias/layerHeaders；pins_all2_clean.csv（173 引脚图形 cell,term,dir,pinN,layer,purp,x0,y0,x1,y1）；oa_vianames.txt（PCU_N/PCU_L/LICONGC_101X194 + stacks MT2-M0U / PG-MT2）；oa_via_bbox.txt（drawn bbox 实测）；oa_pins_tech.txt（金属层 width/spacing/direction）

## 真实产物（gold）
- oa_report.txt（27KB）— 18 单元逐项：views=[layout(maskLayout)/schematic/symbol/verilog]、prBoundary=((0,0),(w,6.71))、terms n=6-9、shapes n=30-70、byLayer、rows n=0 全部、instances、blockages n=0 全部、vias n=4-25、viaDefs、layerHeaders
- pins_all2_clean.csv（173 行）— 9 term：A/B/C/D/Y(logic, M0U:pin, y=2.596-2.944 h=0.348)、vss!(MT2:pin 底轨 + M1:pin)、vcc!(MT2:pin 顶轨 + M1:pin)、vbp!(NW:pin)、vbn!(PW:pin)
- oa_vianames.txt — PCU_N(MT2→M0U 主)、PCU_L(MT2→M0U 次)、LICONGC_101X194(PG→MT2, 仅 aoi22LVSx2)
- oa_pins_tech.txt — TECHLIB 金属规则：M1(0.195/0.195)、M0U(0.272/0.176)、MT2(0.272/0.192)、PG(0.162/0.234)；techGetPrRoutingDirection 全空 → 无 PR 布线方向

## 18 单元清单（prBoundary w × 6.71）
aoi21LVSx1(2.81,8t,50sh,13v) aoi22LVSx1(2.78,9t,53sh,16v) aoi22LVSx2(4.98,9t,65sh,25v,含LICONGC)
invLVSx1(1.13,6t,30sh,4v) invLVSx2(1.13,6t,30sh,6v) invLVSx4(1.68,6t,34sh,10v) invLVSx6(2.23,6t,38sh,12v)
nand2LVSx1(1.68,7t,39sh,7v) nand2LVSx2(2.78,7t,48sh,13v) nand3LVSx1(3.88,8t,61sh,11v) nand3LVSx2(5.53,8t,66sh,20v)
nor2LVSx1(1.68,7t,39sh,7v) nor2LVSx2(2.78,7t,46sh,13v) nor2LVSx3(3.88,7t,58sh,15v)
oai211LVSx1(4.98,9t,70sh,17v) oai21LVSx1(2.81,8t,48sh,14v) oai21LVSx2(3.88,8t,52sh,19v) or2LVSx1(2.81,7t,48sh,12v)
全部：rows n=0、blockages n=0、无 abstract view

## 结论（agent 给出，用户未追问=接受方向）
OA 单元（stdcells_ac）引脚/层/过孔/金属规则**齐全且可读**，但**无 abstract、无 site/row、无 placement obstruction、TECHLIB 无 PR 布线层/方向** → **不能直接视为 Innovus 可放置数字库**。全程只读（mode='r'），未放置/CTS/布线/改库。

## 合成口径
A-faithful 需 SUT 连真实 Aether + /proj/drcoa/V0 drcoa_stdcell 库读 OA，SUT 沙盒只配 eda_flow MCP（无 RAG_MCP_Server/无该库/无 pythone Aether 授权）→ 不可复现 → **B-档 faithful-seed-B-synthesized L1-boundary**（与 r144/r145 同口径）：把 OA 调查结果（18 单元 inventory + 173 引脚 + 3 via + 4 金属规则 + 4 gaps + verdict）放进 bundle_A.json，SUT 渲染结构化《OA Library Readiness Audit》markdown 报告 + stdout 聚合。泛化为 `oa_lib_readiness_report_gen.py`。
