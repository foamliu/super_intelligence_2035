# deepread — 1791958525711_f1fik (chengleiy@hfeg0pkn001=10.129.2.10, mc12, schematic_netlist)

**revival-from-parked (r935)**：原 2026-11-05 以「PDK/LVS-QA infra，非 D design-flow（infra/scripts not a design-flow task）」parked。2026-11-15 候选重审令 §II 将 script-comprehension / explain / Q&A / teaching 全部恢复为可造。承 r933/r934 「skill-explain produce-reframe」范式（candidate = 通用解析器而非自然语言报告）可造：用户请求「阅读全部脚本 + 理解每个脚本功能与脚本间关系」reframe 为 produce 一个通用 script-dir-comprehend 解析器（静态分析，可客观判分）。本 case 是该范式从「单文件 skill 手册」扩展到「整目录多语言脚本库」的首例（directory-walk + Python ast + SKILL/Perl 正则 + import 依赖解析）。

## trace 概览

- 用户 chengleiy 在 hfeg0pkn001(10.129.2.10) 上有自建脚本目录 `/home/chengleiy/scripts`（PDK / LVS / techfile / pcell build / Cadence SKILL 自动化工具库）。
- 543 msgs，跨 2026-11-01~11-15 多日长会话（ts 1791958527114 → 1793513936816）。U#0 在 11-01 06:22，其后用户在同一会话转入实际 VTTF 工具链优化（多轮 fix/check），超出本问范畴。
- domain 复核：keywords 命中 netlist/lvs/drc/virtuoso/aether/schematic/pcell（mc12 是 D-正向词累计），属 D 域 schematic_netlist（PDK/LVS/netlist/pcell 自动化上下文）。原 ledger note「PDK/LVS-QA infra」是旧规则 infra 排除，新规则下 script-comprehension 可造。

## 用户轮原文（A 档合规判定）

| 轮 | ts | 原文 | A档合规 |
|----|----|------|---------|
| U#0 | 1791958527114 | 这个路径下是我的全部脚本  请你阅读所有的脚本，理解每个脚本的功能，以及每个脚本之间的关系，路径如下 /home/chengleiy/scripts | ✅ 提出需求（理解全部脚本功能+关系）✓ 未给根因/修复✗ → **选用** |

**主意图 = U#0**：阅读并理解整个脚本目录（每个脚本的功能 + 脚本间关系）。这是纯 comprehension/explain 请求，A-faithful seed。会话后续的 VTTF 优化工作是用户在理解后的实际开发，不属于本问范畴（本问只锚定 U#0 的 comprehension 意图）。

## assistant 工具链（U#0 后的 comprehension 阶段，MSG 1-31）

- A#1: `get_agent_policy_status` + `list_allowed_files /home/chengleiy/scripts depth=3 limit=1000` — 列全树（输出截断）
- A#5: 分目录 `list_allowed_files` ×4（application/utils/Functions/skill）— 拿到完整文件清单
- A#9: thinking 整理出脚本清单（root buildLibAll.py+tttt；application specVsNetlist.py + pcell/ 6 文件 + vttf/ 10 文件；Functions/ 13 .py；utils/ 9 .py；skill/ utils 12 .il + src_code libInit+procedure+callback+layout_lib + src_code_lde + src_code_lde_back）→ `read_files` 批 1（root + application/pcell 9 文件）
- A#11-A#21: 分批 `read_files` 全部 Python（Functions 13 + utils 9 + vttf 10）+ SKILL（procedure 7 + skill/utils 12 + callback mosdejoaCB + layout_lib createMos 样本）
- A#28: 确认 `buildLibAll.py` TASK_MAP 引用的 `buildLib_lpe.py` 不存在（重要 finding）+ 识别外部 import（Functions.result_message / PDKUtils.excelIO）
- 其后（MSG 31+）用户转入 VTTF 优化开发（本问不锚定）

## GOLD 关键内容（assistant 实际理解 + 脚本库结构签名）

脚本库是 **IC 设计自动化工具库**（Python + Cadence SKILL + Perl），围绕 PDK techfile 三件套（layer.map / tech.tf / display.drf）+ LVS/LPE/DRC + pcell build：

- **顶层编排**：`buildLibAll.py`（TASK_MAP dispatch lvs/lpe/drc/all，引用 application/pcell/buildLib_*.py，注意 buildLib_lpe.py 缺失）
- **Functions/**（13 .py，功能层）：lvs_run/lvs_run_reduce/lpe_run/drc_run（run wrapper）、fractureLvsCompare/compare_lde_by_device（对比）、csvToMap/excelHandle（数据 IO）、FileIO/FolderHandle（文件工具）、pdkRe（PDK regex）、terminal_process、build_common
- **utils/**（9 .py，工具层）：createLvsComd/createLpeComd/createLvsComd_reduce/createSpFile_reduce（命令生成）、createTable、logger（get_logger）、NetlistExtract、python2skill
- **application/specVsNetlist.py**：spec vs netlist 对比（import Functions.result_message + PDKUtils.excelIO 树外）
- **application/pcell/**（buildLib.py + buildLib_lde/lvs/back/test + buildLib.pl）：pcell 库构建
- **application/vttf/vttf2/**（13 .py，techfile 流水线）：updaTf（总控 STEP1-7）→ genLayermap_definition → diffLayer → genTechFromLayerMap → genDisplayFromTech → checkTF/displayTfCross/diffVttfOutputs（校验）+ checkLayerMap/genLayerMap/layerManage/virtuosoLoadCheck/checkTfSyntax
- **skill/utils/**（12 .il）：createCdl/createCdl_label/createLibCell/csvToMap/dumpPcell/exportLibCdf/getLibName/pdk_createTap/proc/proc_ycl/streamOutGDS
- **skill/src_code/** + **skill/src_code_lde/**（变体）：libInit.il/libInitCustomExit.il + procedure/（common/proc/createCdl/csvToMap/getLibName/streamOutGDS/t1）+ callback/mosdejoaCB + layout_lib/createMos + lvsqa_config.ini

**关系网**：buildLibAll.py → application/pcell/buildLib_*.py；Functions/* 被 application/* 与 buildLibAll import（from Functions.FileIO import * 等）；utils/* 被 Functions/* 与 application/* import（from utils.logger import get_logger）；树外依赖 Functions.result_message / PDKUtils.excelIO（不存在于本目录）；skill .il 由 libInit.il 装载、procedure/ 定义公共函数、layout_lib/ 按器件生成 pcell。

## 造题（r935）

- **case_id**：EDA-Eval-DesignFlow-ScriptDirComprehendQA-001
- **domain**：schematic_netlist
- **grade**：A（U#0 verbatim，未改写口语）
- **asset_fidelity**：synthesized-reframe（A=真实脚本目录精简快照，deliverable=通用解析器 reframe）
- **l1_subgrade**：L1-realrun-python
- **A 资产**：`scripts_A/`（78 脚本，5 语言 python/skill/perl/ini/text，从 /home/chengleiy/scripts 真实精简：root + Functions + utils + application/{specVsNetlist,pcell,vttf/vttf2} + skill/{utils,src_code,src_code_lde}，排除 __pycache__/ref_lib/reduceFile/binary）
- **B hidden**：`scripts_B/`（合成平行场景：library-characterization 工具链，15 文件，DISJOINT 标识符 charRunAll/cornerSweep/measureExtract/timingReport/arcClassify/deckBuilder/libcore(libStat/tableRender/logHub)/skill_ilib(measureDevice/dumpArc/libBoot)/char_config/buildDeck/charUtils，反硬编码 A-only token 50 个 identifier-boundary 正则）
- **candidate**：`script_dir_comprehend_parser.py`（通用目录解析器：walk 树 → Python ast 抽 module_doc/functions/classes/imports/__main__ + SKILL `procedure(NAME(` 正则 + Perl `sub` 正则 + ini section → import 依赖解析到树内文件(relationship)或树外(cited_files) → 输出 JSON{question,scripts,functions,relationships,entry_points,cited_files,overall}+report.txt+stdout）
- **check.py**：12 断言 a-l（a zip+py+out_A / b py_compile / c A JSON 7 键非空 / d B stdout JSON 7 键 / e B scripts 覆盖期望集⊆scripts[]⊆B实际(反泄露) / f B functions≥5 / g B entry_points==grep __main__ 集(正确性) / h B relationships≥1 树内 import 边 / i B cited_files 非空(树外依赖) / j B overall+report.txt 含 script/function/relationship/entry / k 反硬编码 B stdout 0 个 A-only token / l 3-seed md5 一致）
- **self-verify**：reference 12/12 PASS + 3 neg（empty→d / print_only→e / core_deleted→e）全 FAIL ALL_NEG_FAIL=True + §4.9 (a)(b)(c) 三退化覆盖 ✓ + 3-seed idempotent ✓
- **reference_submit.zip**：130073B（parser 16669B + out_A.json 113404B）
- **jsonl test sha256**：ae016523f2f9c51ec2e85ba44e91a812cabdf95449233ff5a3b417d0f55d16dd == disk check.py sha256 MATCH ✓
- **D.jsonl**：504→505
- **ledger**：mark f1fik --status case --force（r935 revival-from-parked 单轮 peek→synth→mark case）
- **范式扩展**：skill-explain produce-reframe 从「单文件 skill 手册解析」扩展到「整目录多语言脚本库 comprehension」D 域首例（directory-walk + per-file ast/regex + import-graph），承 r933/r934
- **identifier-boundary 正则反硬编码**：D 域续标（buildLibAll/lvs_run/updaTf/csvToMap 等 50 个 A-only token 不误匹配 B 的 charRunAll/cornerSweep/libcore 等不相交标识符）
