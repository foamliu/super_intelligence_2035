# 深读笔记 — 1791862539977_nwwkg (taodu @ hfeg0plg55/10.129.35.74)

- session: 1791862539977_nwwkg.messages.json, user taodu, host hfeg0plg55 (10.129.35.74), mc=271
  (keywords: schematic:288 / dbGet:260 / pyAether:163 / netlist:35 / hspice:20 / cellview:16 / calibre:13 / pyAether-lang:8 / virtuoso:4)
- meta: model deepseek-v4-flash, cwd /home/taodu/sos/settings_cdns, 177 msgs / 1.22MB, status completed exit 0
  inputTokens 12.56M / outputTokens 87K（读了大量 python_ae 源码）
- tools: list_allowed_files×18 / read_files×23 / editor×38 / run_commands×4 / run_approved_command×2 /
  SandBox_MCP_Server__run_code×4 / RAG_MCP_Server__search_apis×4 / skills×2 / get_agent_policy_status×2

## 真实意图（USER 原话逐字）
- USER#1 (idx0, 唯一用户指令, A-档 seed 提出目标未给根因):
  「分析下面到目录，总结出aether常用到API和常用到DB处理方式，输出一个PDF文件
   /apps/imctf/cad/init/settings_aether/python_ae」
- 全程只有 1 条用户文本指令（其余 97 条 user 消息都是 tool_result）。单轮闭环任务。

## 真实 agent 行为（cline）
- list_allowed_files 探 /apps/imctf/cad/init/settings_aether/python_ae 目录树（depth 4, limit 500），
  发现子目录：le / db / hi / se / layout / tc / ut / veri / wave / genabs / image / IAPR / mentor /
  PG_DUMMY / py_cck_code / AUTO_PC（16 个子目录）。
- read_files 读各子目录下的 .py 源码（CXMTleBasicFuncs / CXMTdbCommonFunc / IMCutHierarchyTraverser /
  cxmt_AIAPR_getPinInfo / ep_* / common_set / bindkeyBasic 等）。
- editor 写 generate_aether_api_pdf.py（初版，自带极简 PDF 生成）→ 改写为 gen_report.py
  （analyze_codebase() 扫描代码库 + gen_pdf() 输出；reportlab 不可用时回退 .txt）。
- SandBox_MCP_Server__run_code 探 reportlab 可用性 → 不可用 → 回退文本报告。
- 最终交付：Aether_pyAether_API_and_DB_Guide.txt（结构化文本手册）。

## 真实 gold（人工复核 idx170 editor new_text，最终 Guide.txt 3013B 节选）
报告结构（中文手册）：
- 四、设计模式与技术要点：4.1 异常处理(try/except 包裹) / 4.2 Config 类配置管理(CXMTutBaseFuncs.py,
  leGlobalVariables=Config({...})) / 4.3 Lisp 风格辅助函数(car/cadr/caddr/cddr/cons/append1/assoc/
  nthelem/parseString/buildString/makeTable/rexCompile/rexExecute/rexSubstitute/rexReplace/mapc/mapcar/
  mapcan/maplist) / 4.4 GOA Geometry Operation API(goaInit/goaLayerFromCellView/goaNewLayer/
  goaLayerFromShapes/goaLayerOrPtArray, 见 cxmt_AIAPR_getPinInfo.py) / 4.5 AI APR 流程(getTech→
  getInstsInfo→getPinInfo→getNetInfo→getSchInfo→getPreRoutingInfo→drawRouting→doBatch, JSON 输出)
- 五、注意事项与最佳实践：资源释放(dbOpenCV 后必调 dbCloseCV) / 异常安全(try/except) / 只读模式(mode="r") /
  SDL 检测(aeIsInSDL) / 层次遍历(visited set 缓存) / Form(aeRegisterCallback) / 环境变量(PROJ_NAME/Ver/
  CXMT_SCRIPTS_ROOT) / 数据库事务(ae.dbUndoEnable/ae.dbUndoDisable)
- 附录速查表：A 文件分类(版图编辑 le/*.py: aeGetCurDesign,dbOpenCV,dbGetTrueOverlapsEx / 电路编辑 se/*.py:
  dbGetAnyInstSwitchMaster,dbFindNetByName / DB基础 db/CXMTdbCommonFunc.py: CXMTleStreamOut,CXMTleStreamIn /
  层次遍历 ut/IMCutHierarchyTraverser.py: InnoutHierarchyTraverser / 快捷键 common_set.py,bindkeyBasic.py:
  aeSetBindKey,aeRegisterCallback / 菜单注册 aeDMMenu / AI APR IAPR/cxmt_AIAPR_*.py: goaInit,goaLayerFromCellView /
  CCK py_cck_code/ep_*.py: aeCrtAppForm,aeAddNetProbe)；
  B 常用对象属性(CellView: libName,cellName,viewName,cellViewType,instances,shapes,signals /
  Instance: name,libName,cellName,master,origin,orient,bbox,cdfParameter / Shape: objType,layerName,
  purposeName,bbox,net,pin,lpName,text / Net: name,figs,terms / Terminal: name,net / HierQueryResult:
  object,hierPath,hierPath.refs,getDepth())

## gold 依赖
- 依赖 live /apps/imctf/cad/init/settings_aether/python_ae 源码树（16 子目录，数百 .py）+ live reportlab
  → A-档 faithful 不可行（内网源码树不可整体 fixture 化 + PDF 二进制不可判分）→ B-档 synthesized L1-boundary
  （离线 fixture python_ae 代码库 → 结构化报告生成器, stdlib-only, 确定性）。

## 合成方向
- 候选脚本 aether_api_summary.py：--codebase <dir> --out <report.md>，扫描 fixture 代码库 →
  按子目录分类(le=版图编辑/se=电路编辑/db=DB基础/ut=层次遍历/IAPR=AI APR/py_cck_code=CCK/common=快捷键菜单/
  mentor=calibre wrap) → 提取 API 调用(ae*/db*/goa*/calibre*/CXMT*/IMC*/Innout* 前缀)按类计数 →
  识别 DB 处理模式(dbOpenCV/dbCloseCV 配对计数/dbGet*/dbUndoEnable/只读 mode="r") →
  解析对象属性(@attrs 注解) → 识别设计模式(try/except 计数/Config 类/Lisp helpers/GOA API) →
  emit report.md(中文手册) + summary.json(结构化, 供判分)。
- 资产 A 忠实：mock python_ae_A 子目录 le/se/db/ut/IAPR/py_cck_code/common, 每子目录 2-3 个 .py,
  含真实 API 名(aeGetCurDesign/dbOpenCV/dbGetTrueOverlapsEx/dbCloseCV/aeSetBindKey/goaInit/
  goaLayerFromCellView/CXMTleStreamOut/InnoutHierarchyTraverser/aeCrtAppForm/aeAddNetProbe) +
  @attrs 注解(CellView/Instance/Shape/Net) + try/except + Config 类 + Lisp helpers(car/cadr/mapcar)。
- 隐藏 B：子目录 le/se/db/ut/IAPR/mentor/common（**无 py_cck_code, 新增 mentor** = B 独有子目录,
  mentor 含 calibreDrc/calibreLvs = B 独有 API）, 不同 API 计数, **无 Config 类, 无 Lisp helpers**
  (config_class_used=False, lisp_helpers_used=False), 不同 dbOpenCV/try_except 计数, 不同 @attrs。
  → 杀硬编码 A 的子目录集合/API 列表/计数值/Config/Lisp。
- 16 条断言：见 check.py (a-p), 每条对 B fixture 独立重推导后与候选 summary.json/report.md 对账。

## 正交性
- 现有 layout_aether case 全是"具体版图操作"（GdsRectGen 矩形生成 / ABMatchPlacementCheck AB 匹配 /
  CTLEAether CTLE 自动化 / ScmosStructId SCMOS 族结构判别 / AddCellPin 加 pin / ListInstCV 列实例 /
  PinFloatAether pin float / WheelZoom / SkillMenuRoute / CTLESchGenAudit / SchPinPlanAudit /
  SchWireRebuildGen）。本案 = aether/pyAether **代码库静态分析 → API 参考手册生成**（按子目录分类 +
  API 计数 + DB 模式识别 + 对象属性提取 + 设计模式归纳），首次覆盖"代码库分析→文档生成"子主题，
  taodu 首个 nwwkg trace。
