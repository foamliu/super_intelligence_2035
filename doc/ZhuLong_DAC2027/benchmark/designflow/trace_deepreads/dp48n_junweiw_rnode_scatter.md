# deepread: dp48n — junweiw RNODE scatter layout script

## trace 溯源
- session: `1794967961276_dp48n` (junweiw @ hfeg0pkn001, ip 10.129.2.10)
- mc=132, domain=layout_aether, status=idle (interactive, 99 msgs)
- cwd: `/ai_sandbox/drcpa/V0/agentdir/junweiw`
- model: deepseek-v4-flash, provider cxmt
- 关键词: pyaether:547 / drc:358 / aether:181 / cellview:114 / dbget:61 / dbshape:52 / lvs:36 / rtl:133
- session 文件: `/home/junweiw/.cline/data/sessions/1794967961276_dp48n/1794967961276_dp48n.messages.json` (618KB, 99 msgs)
- 真实路径: `/home/junweiw/script/rnode_scatter.py` (405 行) + README.md (67 行)

## 用户真实意图（2 条 user_input）
1. **U#0 (主任务)**：「帮我写一下用在 layout 中的脚本，脚本放在 /home/junweiw/script。
   功能：在每个 m1/CT 孔的位置打上 M1 RNODE 这个层次，启动脚本调出 GUI 界面（类似 auto via tool），
   填写需要给哪些 power nets 上撒 RNODE，将生成的每种 power RNODE 做成一个 cell，
   要是存在多个，将每个 power RNODE 汇总成一个 top cell，放置 cell lib 库可以自定义」
2. **U#62 (refinement)**：「修改一下，用 label 代替 pin，pin 占用不会比较大，label 比较小」

→ 真实任务 = 产出一个 pyAether layout 自动化脚本，在 power net 的 M1/CT 孔位撒 "M1 RNODE"
   标记（label 默认），每 net 一个 cell，多 net 汇总成 top cell，带 GUI。供 Rscalc 做电源网络电阻提取。

## agent 工具链
- skills(eda_agent) → read_skills(PyAether SKILL.md, layout_optimization scenario)
- RAG search_apis: aeCreateRect / dbNewCellView / dbCrtInst / emyShapeGetNetName / aeCreateFormButton / aeCreateStringField / aeCreateAppForm
- RAG get_api_details: aeCreateStringField / aeCreateFormButton / aeCreateAppForm / dbCrtInst / dbNewCellView / dbCrtRect3X / dbGetTrueOverlapsEx / emyShapeGetNetName
- run_approved_command(shell-runner): grep CAD 源码找 RNODE 真实用法
  → 关键发现: IMCutRscalcFlow.py / IMClePGnet.py 中 RNODE 层 = ["M1","RNODE"]，dbCrtLabel 用法参照 IMClePGnet.py:1315
- editor: 写 rnode_scatter.py / README.md / _check_syntax.py / _check_logic.py
- run_approved_command(python-runner): py_compile + mock pyAether stub 逻辑自检
  → pyAether sandbox (10.129.8.105:45955) Connection refused，故仅静态+mock 验证

## 交付物 rnode_scatter.py 结构（405 行）
- 纯函数: `_bbox_box` / `_shape_lpp` / `_lpp_equals` / `_shape_net_name` / `_net_matches`
  / `_parse_lpp` / `_parse_nets` / `_safe_cell_part` / `_unique_cell` / `_label_height`
- 核心: `_collect_rnode_points(cv, net, m1_layer, m1_purpose, ct_layer, ct_purpose)`
  → 遍历 cv.shapes，过滤目标 net 的 M1 图形，dbGetTrueOverlapsEx 查 CT 孔，返回 [(cx,cy,cts)]
- `_make_net_cell(lib, cell, points, rlayer, rpurpose, net, box_size, mark_mode)`
  → dbNewCellView 建 cell，每个 point 用 dbCrtLabel(label 模式) 或 dbCrtRect3X(rect 模式)
- `_make_top_cell(lib, top_cell, subcells)` → dbNewCellView + dbCrtInst 汇总
- `rnode_scatter_run(lib, nets, rndLayer='M1', rndPurpose='RNODE', ctLayer='CT',
                    ctPurpose='drawing', boxSize=0.0, cellPrefix='RNODE_',
                    topCell='', alwaysTop=False, markMode='label')`
  → 主流程: aeGetCurDesign → 每 net 收点→建 cell → >1 net 建 top cell
- GUI: `_ListNetsCB` / `_RNodeFormCB` / `_build_form` / `rnode_scatter_gui()`
  → aeCreateStringField ×9 (lib/net/rndLayer/ctLayer/markMode/size/cellPrefix/topCell/alwaysTop)
  + aeCreateFormButton(列出 power net) + aeCreateAppForm + aeDisplayForm

## case 设计（EDA-Eval-DesignFlow-RnodeScatterScript-001, layout_aether, k=14）
- **交付**: submit.zip 含 rnode_scatter.py（单文件 pyAether 脚本）
- **判分**: pyAether 不可用 → check 用 mock pyAether + AST 结构 + 运行 rnode_scatter_run 录制调用
- **公开 A**: task_brief.md（规格 + 函数签名契约 + 示例 config_a.json: 2 nets/4 vias）
- **隐藏 B**: config_b.json（3 nets VDD!/VSS!/AVDD!, 6 vias, 不同 lib/cell）不进 SUT 沙箱
- **mock**: check 内建 pyAether stub，按 config B 构造 mock cv（shapes/nets/CT overlaps），
  import 候选 rnode_scatter.py，调 rnode_scatter_run(lib_B, nets_B, 'M1','RNODE','CT','drawing',0.0,'RNODE_','',False,'label')，
  录制 dbNewCellView/dbCrtLabel/dbCrtInst/dbCrtRect3X 调用
- **14 条断言**: ①zip合法含rnode_scatter.py ②py_compile通过 ③AST定义rnode_scatter_run ④AST定义rnode_scatter_gui
  ⑤AST引用dbCrtLabel(label模式,用户refinement) ⑥AST引用dbNewCellView ⑦AST引用dbCrtInst(top汇总)
  ⑧AST引用RNODE purpose ⑨AST引用aeCreateAppForm(GUI界面) ⑩mock下import成功 ⑪mock B运行rnode_scatter_run返回True且建3个net cell ⑫dbCrtLabel调用6次且textName覆盖3个net ⑬dbCrtInst调用3次(top汇总3 instance) ⑭跨输入守卫:mock A(2 nets)运行建2 net cell+4 label+2 inst, 硬编B(3 net)在A上失败
- **4 neg**: empty(缺rnode_scatter.py→cond1) / print_only(只print无函数→cond3/10) / hardcode_b(硬编B结构→cond14) / delete_core(无dbCrtLabel→cond5)
- **§4.9 三假**: (a)空壳→cond1 (b)只print→cond3 (c)删核心dbCrtLabel→cond5 全FAIL
- **反硬编 cond14**: mock A 跑候选，hardcode_b 脚本硬编 3 net/6 label/3 inst → 在 A(2 net)上 label 数≠4 FAIL

## 与既有 case 区别（防 intent-dup）
- WidthLengthQaPatternGen / EncloseShort3DPatternGen: 产 .qap 文本 manifest（DRC pattern 生成器，离线 CLI）
- 本 case: 产 pyAether layout 脚本（带 GUI form + cell 创建 + instance 汇总），判分用 mock pyAether 录制 API 调用
- 域不同: 本 case = layout_aether（pyAether 自动化），非 physical_verify DRC pattern
- 断言不同: mock API 调用录制（dbNewCellView/dbCrtLabel/dbCrtInst 计数+参数） vs .qap 几何复算
