# Deepread: f1fik (chengleiy @ hfeg0pkn005=10.129.2.14, mc=594)

**trace**: `/home/chengleiy/.cline/data/sessions/1791958525711_f1fik/1791958525711_f1fik.messages.json` (4.57MB / 543 msgs / 325 user turns)
**kw profile** (summary.tsv ssh_eda_search_20261119_172105): `lvs:3385;pdk:2717;virtuoso:843;techfile:512;pex:445;netlist:358;.cdl:156;calibre:116` — strong physical_verify (LVS+PEX+PDK techfile verification) C-dominant.
**prior state**: parked (legacy, empty note); also in shard B ledger parked. 2026-11-15 reaudit: analysis/Q&A/code-comprehension 合法 → revival r840 via `mark --force` (domain=physical_verify C-shard；B parked 无 case 产出).

## 真实任务（trace 原文）

U#0（用户首条，逐字）：
> 这个路径下是我的全部脚本  请你阅读所有的脚本，理解每个脚本的功能，以及每个脚本之间的关系，路径如下   /home/chengleiy/scripts

**任务形态** = 代码理解 / 脚本库结构化分析。用户要求 agent 阅读其整个 PDK QA / LVS / DRC / PEX 脚本库，理解 (a) 每个脚本的功能 (b) 脚本之间的关系。

## 真实脚本库（.75 实证，e0031982 可读）

`/home/chengleiy/scripts` = 89 .py 文件 / 800K / 16535 行（不含 __pycache__/test_data）。结构：
- `buildLibAll.py` — 顶层入口
- `Functions/` — drc_run.py / lvs_run.py / lvs_run_reduce.py / lpe_run.py / fractureLvsCompare.py / pdkRe.py / csvToMap.py / excelHandle.py / FileIO.py / FolderHandle.py / terminal_process.py / build_common.py / compare_lde_by_device.py
- `utils/` — createLvsComd.py / createLvsComd_reduce.py / createLpeComd.py / createSpFile_reduce.py / NetlistExtract.py / createTable.py / logger.py / python2skill.py
- `application/pcell/` — buildLib.py / buildLib_lvs.py / buildLib_lde.py / buildLib_test.py / buildLib_back.py
- `application/vttf/` — checkTF.py / checkLayerMap.py / diffLayer.py / + vttf4,vttf5 子目录
- `application/specVsNetlist.py`
- `pdk_qa_tools/` — PDK QA 工具包（modules/ + PDKUtils/ + pdk_compare.py / pdk_qa.py）
- `skill/` — SKILL 源码

用户后续 324 条 user turn 多为 agent-policy-engine 状态注入 / list_files 工具结果回灌（read_files content stripped），少量真实追问。核心可造意图 = U#0。

## 金标准（trace 末尾用户接受的结果）

assistant 对脚本库产 markdown 结构化分析报告（free-text prose：每脚本功能 + 跨脚本调用关系）。trace read_files 结果 content 被 strip，故从助手 markdown 解读重建。

## 档 B reframe（为何不全 A 档）

A 档 gold = free-text markdown 分析报告，依赖真实 /home/chengleiy/scripts 沙盒无（800K/89 文件进 SUT workdir 过重且难写 ≥8 独立硬断言牙：prose 难结构化对账）。reframe 为**离线纯 stdlib Python 脚本库调用关系分析器** `script_callgraph_analyzer.py`：
- CLI `<library_dir> <output_json>`
- AST 遍历 .py 文件，提取 per-file: module docstring / top-level functions(name+n_args) / top-level classes(name+methods) / imports
- 跨文件关系: import_edges（file A import module B → edge）+ call_edges（file A 调用 file B 中定义的 top-level function）
- 输出结构化 JSON（files[] / import_edges[] / call_edges[] / 计数）

资产 = 忠实重建的紧凑脚本库（镜像真实文件名 + LVS/DRC/PEX domain），A 档可见、B 档隐藏变体（不同文件数/函数/import 边）。check() 跑 SUT 分析器于 B，对账结构事实（文件数/函数名/类方法/import 边/call 边/计数）≥8 独立断言，退化提交（空壳/print-only/硬编码）全 FAIL。

**子型**: `python-script-library-callgraph-analyzer`（与 r838 单脚本静态剖析 / r839 脚本库检索分类 形成三连多样化：r838=单脚本结构，r839=库检索分类，r840=库调用关系图）。
