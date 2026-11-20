# trace_deepread — 1793006622937_6kot7 (weizhao @ hfeg0pkn004, mc=43)

- **session**: 49 msgs / 368KB, agent `cline lead` (glm-5.2), 10/26 17:23–17:25 (~2min).
- **tools scan**: calibre:1790, virtuoso:18, innovus:18, icc2:18, synopsys:8, skipper:2, hspice:2, cadence:2. (innovus/icc2/synopsys = env/toolchain context, not the task.)
- **real user intent** (USER#0, 唯一真实轮, 逐字):
  > `please study /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/docs/pdfdocs/calbr_mp_useref.pdf , and feedback a sdudy note to me`
  - = 学 Calibre **SVRF (Standard Verification Rule Format) usage reference** 手册 (`calbr_mp_useref.pdf`, 7.3MB) 并产出一份 study note。
- **agent flow** (全 22 assistant turn):
  1. `list_allowed_files` 找 PDF — 用户给的路径 `/apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/docs/pdfdocs/` 是 symlink，实际落点 `/apps/mentor/MRB/calibre/2020.1_36/docs_cal_2020.1_17.9/docs/pdfdocs/`。
  2. `run_commands` 被禁（"Raw shell tool run_commands is disabled; use run_approved_command"）→ 改用 `run_approved_command` profile=python-runner。
  3. 反复 `list_allowed_files`（7+ 次）解 symlink 链；发现 `calbr_mp_useref.pdf` 确在 MRB 路径（7305KB）。
  4. 写 `find_pdf.py`（搜索 mp-related PDF）、`check_pdf_libs.py`（探测 → `pdftotext` 可用，`mutool` 无）、`extract_mp_pdf.py`（`pdftotext` 抽全文）。
  5. 多次撞 `filePath is not a regular file`（editor 写文件后 run_approved_command 立刻跑，文件还没落盘 —— 工具状态竞争）。
  6. **session 在 `extract_mp_pdf.py` 执行处截断（msg 48），从未产出 study note**；用户未表达接受/拒绝。
- **failure mode**: 整轮耗在 **工具/路径基础设施**（symlink 解析 + PDF 抽取 tooling + run_approved_command 状态竞争），没碰到任务核心（理解 SVRF deck 内容）。teaching point：用户要的是对 SVRF deck **内容**的理解与结构化，不是翻 PDF 的工具流。
- **A-档可行性**: 不可行 —— session 无 gold study note（截断于抽取途中），用户未接受结果。
- **B-档 synthesized (本轮交付)**: seed=USER#0 逐字意图（study SVRF useref → 结构化构造目录）。交付 `svrf_construct_catalog.py`：解析 SVRF deck → JSON 构造目录（globals / layers / layer_maps / includes / variables / properties / virtual_ops / drc_checks / lvs_directives / errors / counts）。资产 A=`svrf_deck_A.svrf`（cxmt7L/drcoa/weizhao, 6 层 METAL1/METAL2/VIA1/VIA2/POLY/CT, GDSII, 6 DRC, 5 LVS, 3 errors），hidden B=`svrf_deck_B.svrf`（qtech5L/bandgap/e02141, 7 层 PO/M1/CO/M2/NW/DIFF/VI1, OASIS, 7 DRC, 7 LVS, 4 errors, 3 includes vs 2, 2 CONNECT vs 1）→ 工艺/层名/层号/路径/系统/数值/结构全异 → 杀硬编码 A。12 条断言 (a–l), k=12。
- **正交性**: shard C 首个「SVRF deck **comprehension/parsing** → construct taxonomy」子主题，正交于现有 via-fill SVRF **generation** 案例（生成 SVRF vs 解析/分类 SVRF）；首次把 agent「卡在工具流、没产出 study note」的失败模式转成「对 deck 内容结构化」的判分要点。
- **选料注**: r125 候选池 mc≥30 shard-C tools 过滤后，fresh-user 排除饱和(xinqiaoz/e0014566/miccao/haoyut/yohannw...)。逐个 scp+解析 fresh 候选首条 user turn 验域：ve67l(mike)=cosim/VCS/spike RISC-V build(wrong)、v59v8(e0047695)=cdslck 文件删除 UI 脚本(wrong)、d810y(jackjia)=DDR5 sim/Verdi 波形(wrong)、f6x1i(e02141)=Sentaurus TCAD GAA_FET deck(wrong)、314mt(sophiaw)=hspice 仿真(wrong)、aq0vc(tongni)=netlist/hspice 仿真(wrong)。6kot7(weizhao)=唯一 fresh-user physical_verify-domain trace（calibre SVRF useref study）。fresh-user real-L2 PV 稀缺，本轮以 6kot7 为锚做 L1-boundary。
