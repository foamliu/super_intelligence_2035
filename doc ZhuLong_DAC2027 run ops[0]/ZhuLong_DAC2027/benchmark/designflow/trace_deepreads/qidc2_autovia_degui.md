# Deepread: 1783324072633_qidc2 — AutoVia GUI 脚本去 GUI 化

- **session**: 1783324072633_qidc2 (e0014566 @ hfeg0pkn005, mc=82)
- **size**: 179 msgs / 546KB
- **domain**: layout_virtuoso
- **keywords**: drc:732;virtuoso:80;cellview:80;.gds:46;calibre:42;netlist:31;dbopencellviewbytype:25;ddgetobj:15
- **case**: EDA-Eval-DesignFlow-AutoViaDeGui-001 (r195, A-档 faithful, L1-boundary, k=15/15)

## 用户意图 (msg#61, 逐字原文)
> IMCleAutoVia.il 这个工具本身就是GUI的，比较不太适合整理成agent skill的形式。请你将这个脚本去GUI化，把其中需要通过GUI输入的参数，改成配置文件输入的方式。整个的流程就是先读取配置文件，得到重要的配置信息。然后将这个配置信息，写入到去GUI化的il脚本里，然后通过run_code工具，调用这个去GUI化的脚本执行。

**意图判定**: 纯 intent（去 GUI 化 + 配置文件输入 + run_code 调用），未指出根因或给修复方案 → 合格 A-档 seed。

## 对话流 (user 轮)
- msg#0: 「请尝试连接virtuoso中打开的layout.」(连版图)
- msg#23: 「让你打开并且读取已经打开的layout.」(读版图)
- msg#57: 「请你执行读取当前已打开的layout.」(执行读)
- msg#61: **核心 intent** — 去 GUI 化 IMCleAutoVia.il
- msg#77: continue
- msg#85: 「请问你事情干完了吗？没干完的化，继续啊」(催促)

## assistant 工具链
1. read_open_layout.il: geGetEditCellView 连版图, 读 shapes/instances/terminals/nets
2. run_autovia_config.il: 62 参数 + 27 via flag (process/projName/libName/cellName/viewType/pwrnets/strminLib/runDir/gdsFile/topCellName/suffixValue/genTopCellValue/debugMode/coreNum + viaCT/V1.../VIA9/Vy1.../V1andV2)
3. run_autovia_nogui.il (600+ 行): IMCleGetTimeString 抽取 + RunAutoViaNoGui 入口 + case(process) 14 deck 选择 + via 选择串 strcat + strmout GDS → calibre -drc → sed INSERT_V → stream in → dbCreateInst → FastXOR 校验
4. run_autovia_agent.il: load nogui + 调 RunAutoViaNoGui 的编排器

## 关键产物 (金标准)
- IMCleAutoVia.il: 2035 行原始 GUI 脚本 (Leozhao, v1.1a-v1.9a, CXMT 10G1-10G6/HB/22 等工艺, hiCreateAppForm 表单)
- run_autovia_nogui.il: 600+ 行去 GUI 版, 无 hiCreateAppForm/hiFormCreate/hiDisplayForm, load config + unless 校验 5 必填 + case(process) + strcat via 选择串 + calibre/strmout/dbCreateInst/dbSave 核心流
- run_autovia_config.il: 1995 字节配置 (cxmt10G4plus/train/austin/layout_austin6/vss!, viaCT/V1-V4=t 余 nil)
- read_open_layout.il: 6287 字节连版图辅助 (geGetEditCellView + 读 shapes/instances/terminals/nets)
- run_autovia_agent.il: 1150 字节编排器

## 执行结果
- msg#131: run_autovia_nogui.il 加载成功
- msg#133: load IMCleAutoVia.il 取 helper, 报 "cannot create RUN directory - /proj/DDJOC/v0/ver/autovia/austin/layout_austin6" (runDir 路径权限)
- msg#141-179: sandbox "Unknown SKILL error" 环境问题, assistant 转为本地校验括号平衡/转义, msg#178 总结"脚本编译运行正确, 配置读取, via 选择串 _V5..."

## 案例设计
- **A (可见)**: IMCleAutoVia.il + run_autovia_config.il + task_brief.md
- **B (隐藏)**: run_autovia_config_B.il (process=hl22_uniqB/lib=libB_uniq/cell=cellB_uniq/projName=projB_uniq/pwrnets="vddB! vssB!"/viaV2+V4+V5+RDV+V1A+T2V1+T8V3+RV+VIA3+Vy2+Vr2=t 余 nil, suffixValue=Yes/genTopCell=Yes/debugMode=No/coreNum=8)
- **deliverable**: submit.zip 含去 GUI 脚本 .il + 配置 .il
- **check.py 15 条 a-o**: zip 合法 / 无 GUI 调用 / 无参入口 / load 配置 / 校验 5 必填 / via 选择串 strcat / 抽取日期 helper / 核心 db+calibre 操作 / B 字段全异 / 括号平衡(subprocess) / runDir 处理 / pwrnets 解析 / 入口无 form 参数 / 反硬编码(subprocess) / 反 stub >=3 核心操作
- **negatives**: empty_shell(a) / hardcode_a_gui(b) / naive_print_stub(d) — 三假(a/a/h)
- **自验**: ref PASS, 3 neg FAIL(distinct), 3 fake FAIL → 全通过
