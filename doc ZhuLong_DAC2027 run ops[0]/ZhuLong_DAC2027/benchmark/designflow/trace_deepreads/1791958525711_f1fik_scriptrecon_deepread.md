# Deepread: 1791958525711_f1fik (chengleiy @ 10.129.2.14 / hfeg0pkn005)

- **mc** 594, keywords: lvs:3385 / pdk:2717 / virtuoso:843 / techfile:512 / pex:445 / netlist:358 / .cdl:156 / calibre:116
- **trace size** 4.5MB / 543 msgs (325 user / 218 assistant)
- **domain** physical_verify (PDK techfile / LVS / PEX toolchain)
- **prior ledger state** parked 2026-11-10 (r313 peek): "请阅读/home/chengleiy/scripts所有脚本理解功能与关系 = recon/explain doc task NOT produce-task; status=failed" → pre-11-15 误判，按 11-15 §二 revival (analysis-Q&A / explain / doc-search 全部复活) → r737 reclaim 为 case

## 真实用户意图（U#0 逐字原文）

> 这个路径下是我的全部脚本  请你阅读所有的脚本，理解每个脚本的功能，以及每个脚本之间的关系，路径如下   /home/chengleiy/scripts

- 单一明确意图：读 `/home/chengleiy/scripts` 下全部脚本，理解每个脚本的功能 + 脚本之间的关系。
- 用户**没有**给出根因或修复方案（符合 A 档选轮规则，可作任务说明）。
- 后续 542 条消息是用户不断追加的新任务（能力建设 3/4、TSI/ALS、genTechVariants.py 等），与 U#0 的原始意图分离；本 case 只取 U#0。

## assistant 工具链（前 ~30 msgs）

- list_allowed_files / read_files 探索 `/home/chengleiy/scripts` 树
- 逐个 read .py 脚本，提取 docstring + 顶层函数 + import 关系
- 产出结构化文字说明：每个脚本功能 + 脚本间调用/导入关系
- 用户接受（U#36 引申到 a_lvs_pattern 案例，进一步验证脚本目的）

## reframe（mock-behavioral `script-recon-analysis-Q&A`）

真实任务 path-dependent on `/home/chengleiy/scripts` 的 .py 脚本内容（docstring + import + 顶层函数 + 调用关系）→ mock-stdlib：
- A = 9 个 mock PDK techfile 工具链脚本（gen_layermap / gen_tech_from_layermap / gen_display / check_tf / diff_layer / upda_tf=orchestrator / gen_tech_variants / tsi_verify / gen_symbolic_from_csv），真实工具链拓扑保留
- B = 7 个 mock schematic/netlist/LVS 工具链脚本（gen_netlist / extract_devices / check_lvs / run_lvs=orchestrator / compare_schematic / gen_spice_deck / pin_remap），跨域反硬编码
- B2 = 3 个 mock foo 工具链脚本（gen_foo / check_foo / run_foo=orchestrator），最小跨输入 guard
- 三 fixture 脚本数 9/7/3、关系数 5/4/2、叶数 7/5/2 全不同
- solve.py 纯 stdlib（ast/json/os/sys）解析 .py：模块 docstring → purpose 分类；顶层 FunctionDef/ClassDef → defines；Import/ImportFrom → imports / local_imports；`from <sibling> import <name>` 且 <name> 在本脚本中被 Call → caller→callee 边（**双确认**：import + call，未调用 import 不计边）
- 牙齿：20 断言 a-t，真值表 B_EXPECTED / B2_EXPECTED 人工独立推得；含 evidence 可溯源性 (r)、反硬编码 A (s)、跨输入 B2 guard (o)、空目录防崩 (p)、确定性 (q)、退化提交全 FAIL

## distinct vs 近期 family

- r736 LayoutElementAttribution = 枚举+归属 Q&A（layout element → AutoVia/PowerFill 分类）
- r735 AutoviaAgentScriptGen = 生成式变换（产新 .il 文件）
- r734 DrcSvrfSetlayerExplain = 单 SVRF rule 文件结构化解析
- r733 DrcRuleVarPrefixCollision = DRC 报告+LDR+deck 三文件交叉诊断
- **本例 = 脚本目录静态分析（AST-based recon）+ 关系图构建**，C 域首例 script-recon-analysis-Q&A revival

## 牙齿验证

- reference solve.py self-test: PASS 20/20 ✓
- 3 negatives FAIL distinct: solve_empty→(c), solve_print_gold→(e), solve_import_only→(k) ✓
- §4.9 退化提交（空壳/print-only/exit-1）全 FAIL ✓
- k_rationale == k_check == 20 ≥ 8 GATE PASS ✓

## 纪律

- SUT 沙箱只含 sample_input/scripts + prompt.txt + task_brief.md；hidden/ + reference/ 不进 SUT ✓
- 不脱敏：user=chengleiy / host=10.129.2.14 / session_file=1791958525711_f1fik 真值 ✓
- 只动 C shard 文件 ✓
