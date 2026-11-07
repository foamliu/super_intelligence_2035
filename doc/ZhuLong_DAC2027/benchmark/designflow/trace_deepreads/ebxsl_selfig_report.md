# 深读笔记 — 1793855278198_ebxsl (t0002038 @ hfeg0pkn004, mc379)

## Trace 概况
- session: `/home/t0002038/.cline/data/sessions/1793855278198_ebxsl/1793855278198_ebxsl.messages.json`
- 349 msgs / 23 user turns / 213 tool_use（editor=57 read_files=52 RAG search_apis=16 search_codebase=15 run_approved_command=15 list_allowed_files=8 get_api_details=3 skills=2）
- 工具命中：pyAether 529 / schematic 441 / netlist 400 / dbGet 130 / cellview 65 / virtuoso 53 / hspice 3（注：schematic/netlist 计数来自 RAG search 的 query 词，非真跑 netlist；实际是 Aether Layout Editor + pyAether skill 集成）

## 用户意图流（关键轮）
- **U#0**「我想要把文件里面到程序配置到我到aether里面使用可以实现吗」+ 附件 1212（xyCreateAutoVia.py 脚本）= **CLEAN PRODUCE**：把外部脚本配置进 Aether
- U#1「你目前能帮我什么」/ U#2「能帮我配置吗」/ U#3「使用方案一帮我转换出来并帮我配置吧」
- U#5 报错 `NameError: name 'xyCreateAutoVia' is not defined` + `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2`（Python Console 编码问题）
- **U#6**「我选中了两端但是运行后没有反应显示 Please partial-select at least one horizontal AND one vertical path/pathSeg end.」= 选区诊断需求
- **U#7**「这是三次输出的结果=== DIAGNOSE: Selected Objects === cv = db: 0x... / cv type = <class 'pyAether.pyaedb.emyDesign'> / selected = (db: 0x...) / fig.objType = ArrayInst / ...」= 用户贴出诊断输出，确认 figure 属性读取逻辑
- U#9-U#13 反复调试 xyCreateAutoVia 选中端点（path/pathSeg endpoint，horizontal AND vertical）
- **U#10** 贴出 Path 调试输出：`objType = Path / points = [(54.46, 1.03), (55.45, 1.03)] / width = 0.05 / layerName = M2 / selFigPoint = [False, True]`
- U#14「成功了，接下来配置快捷键吧」= 用户接受结果

## 助手工具链
- RAG search_apis/get_api_details 探 pyAether API → editor 改 skill 脚本 → run_approved_command 在 Aether Python Console 跑 → 写 DIAGNOSE 诊断代码（`cv = aeGetCurrentDesign(); selected = cv.getSelectedFigs(); for fig in selected: print(fig.objType, fig.points, fig.width, fig.layerName, fig.selFigPoint)`）

## 金标准（用户实际接受的结果）
- DIAGNOSE 诊断代码：取当前 cellview（emyDesign）+ 选中 figure 列表，逐个打印 objType/points/width/layerName/selFigPoint，让用户看清选中了什么（ArrayInst / Path / Rect 等）

## A-faithful 判定
- **不可行**：真实 xyCreateAutoVia 集成 + Aether GUI 选区交互不可附加（live Aether GUI selection 不可在沙箱复现）+ 真实 /home/t0002038 项目私有不可移植 → **B 档 synthesized**

## 合成（本 case = SelFigReport-001）
- 取 trace 的「诊断当前选中图形属性」子意图（DIAGNOSE helper），合成可复用命令行工具 `sel_fig_report.py`
- `import pyAether as ae` → `ae.aeGetCurDesign()` 取 cv → `cv.getSelectedFigs()` 取选中 figure 列表 → 逐个读 `objType/points/width/layerName/selFigPoint`（缺失属性兜底）→ 写 4 键报告 JSON（cv_type/n_selected/figures/timestamp）
- **mock-pyAether 行为可验范式**（同 #370 CstViewPrecheck）：check.py 运行时生成 mock pyAether.py（读 MOCK_FIGS_JSON/MOCK_CV_TYPE 环境变量构造 figure 对象 + 动态类名），候选 import pyAether 拿到 mock，行为完全离线可验
- A=spec_A.json（cv_type=emyDesign，2 个 Path：M2 width0.05 selFigPoint[false,true] + M3 width0.08）
- hidden B=ArrayInst 单个（无 points/width 属性 → n_points=0, width=null）
- hidden B2=Rect+Polygon 混合 2 个（不同 objType/points/layerName）
- hidden B3=空选中（n_selected=0, figures=[]）
- 反硬编码七轴：cv_type(emyDesign) + objType(Path/ArrayInst/Rect/Polygon) + layerName(M2/M3) + width(0.05) + selFigPoint + 选中数(0/1/2) + 缺属性兜底

## check.py 16 条件 a-p
a(zip+无泄漏+py_compile+has sel_fig_report.py) b(A exit0+report) c(4顶层键) d(cv_type==emyDesign 从 type 读) e(n_selected==2+figures len2) f(fig0 objType==Path) g(fig0 n_points==2) h(fig0 width==0.05) i(fig0 layerName==M2) j(fig0 selFigPoint==[false,true]) k(fig1 objType==Path+n_points==2) l(B ArrayInst: nsel1+objType+npts0+width-null) m(B2 Rect+Polygon: nsel2+objType+npts3) n(反硬编码源码无 Path/M2/M3/ArrayInst/Rect/Polygon/emyDesign 字面量) o(B3 空选中: nsel0+figures[]) p(确定性 3x figures 块 sha256)

## 自验
- ref PASS 16/16 + 6 neg FAIL 6 distinct first_fail(b.A-report / f.A-fig0-objType / e.A-nsel-2 / l.B-nsel-1 / l.B-fig0-objType / l.B-nsel-1) + §4.9 三假 FAIL + 断言闸门 k=16 + test 字段与 check.py 字节同步
- 注意：print_expected 与 naive_static_figs 同首fail(l.B-nsel-1)，但失败原因不同（一个硬编报告一个忽略 mock），均有效 FAIL

## 教训
1. **mc>=30 fresh D-domain clean produce 池结构性枯竭**：本轮 peek 7 条高 mc 候选(4dd1i/z9yjw/llns7/5e6p2/evxj6/ebxsl/fieju/6rvi0)全为 layout/digital/physical_verify/powerfill，无一干净 shard D produce。印证 #317/#332/#365 长期结论。下轮需降 mc>=5 或跨 shard 共享。
2. **同 trace 不同意图第七例**：ebxsl 整体是 Aether layout autovia 集成（layout 域），但取其「DIAGNOSE 选中图形属性」子意图=analog_context（cellview figure 属性读取+报告），domain+intent+check 与原 trace 主意图不重叠。parked note「wrong-domain」保留作历史，case 行加 case_id（继 #331/#332/#365/u78sz 模式）。
3. **mock-pyAether 行为可验范式第二例**（继 #370）：真实 pyAether figure 属性（objType/points/width/layerName/selFigPoint）来自 trace 实际诊断输出，API 契约清晰 → check 运行时注入 mock（动态类名 type(cv).__name__ + figure 属性构造）记录可控返回，候选的 import pyAether 调用形状/属性读取/缺属性兜底/报告/跨输入全可验，16 条件天然丰富（cv_type/objType/points/width/layerName/selFigPoint/选中数/缺属性/空选中/反硬编码/确定性）。
4. **缺属性兜底是强反硬编码轴**：B(ArrayInst 无 points/width)测 getattr 兜底，core_deleted 不读属性→(f) FAIL；B3(空选中)测 len(figs)==0 兜底，naive_static_figs 总报 2→(l) FAIL。
5. **type(cv).__name__ 防 cv_type 硬编**：naive_hardcode_a 硬编 "emyDesign"→(n) 反硬编码 FAIL（虽先在 (l) 因 objType 硬编 FAIL）；ref 用 type(cv).__name__ 从 mock 动态类读，(d) 通过。
6. **analog_context 46→47**（仍最低覆盖域之一，与 waveform 44 并列）；L1/L2 比例债 25→26 轮（mock-pyAether 无 live binary，fresh D-domain L2 真跑不可移植 + 40min 预算）。
