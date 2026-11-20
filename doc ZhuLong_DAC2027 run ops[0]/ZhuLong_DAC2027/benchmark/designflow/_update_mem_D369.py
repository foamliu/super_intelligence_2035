#!/usr/bin/env python3
"""Update MEMORY_DESIGNFLOW_D.md for round #369 (LvsRptAnalyze-001).
- Archive #368 流水 to MEMORY_D_archive.md (归档批次 2063)
- Update DEBT/PHASE/coverage/体积/断言 lines
- Add #369 流水 line
"""
import re, os, datetime

MEM = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_DESIGNFLOW_D.md"
ARCH = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/MEMORY_D_archive.md"

text = open(MEM).read()
lines = text.split("\n")

# Find the #368 流水 line (starts with "- 流水 #368")
liu368_idx = None
for i, ln in enumerate(lines):
    if ln.startswith("- 流水 #368"):
        liu368_idx = i; break
assert liu368_idx is not None, "流水 #368 line not found"

liu368 = lines[liu368_idx]

# Append #368 to archive with header
arch = open(ARCH).read()
arch += "\n\n## 归档批次 2063 (2026-11-07 #369 轮归档)\n"
arch += liu368 + "\n"
open(ARCH, "w").write(arch)
print("archived #368 流水 to MEMORY_D_archive.md (归档批次 2063)")

# Build #369 流水 line
liu369 = (
    "- 流水 #369 (LvsRptAnalyze-001, schematic_netlist, B-grade synthesized L1, 16 条件 a-p) — "
    "erhym/fhwang/10.129.2.14/mc50；trace=DRAM 物理验证组 LVS 排障(134 msgs/5 user turns/70 tool_use; "
    "U#1「帮我分析一下这个结果路径下LVS的结果文件错误类型，并附带解决方案方向 /proj/drcpa/V0/ver/lvs/YDEC_Power_Rscalc/Array3G_TOP_L」"
    "+U#2「把上述你的分析方案生成文本文件放到这个路径下」= CLEAN PRODUCE; "
    "U#4 给根因假设→A-grade rule#2 排除; assistant read_files .lvs.report/.ext/.erc.summary + run_approved_command grep/head/tail/sed/wc 提取关键段 + editor 写 analyze_lvs.py/analyze_lvs.sh/write_report.py 增量构建 + 产 LVS_ANALYSIS_REPORT.md 到目标路径). "
    "金标准=结构化 Markdown 分析报告(基本信息+Rule设置+总体错误摘要+错误类型分类[Connectivity/Property W 2.717u vs 1.476u/提取警告]+根因分析[4根因]+解决方案方向[Open circuit/Unattached/Virtually connected/Stamping/Property/Connectivity 各给修复建议]). "
    "**A-faithful 不可行**: 真实 LVS 报告 260MB 不可附加 + /rundata/drcpa 私有路径不可移植 + live Calibre RVE/svdb 不可移植 → B 档 synthesized. "
    "**合成**: analyze_lvs.py --report --ext --erc --outdir → error_summary.json + lvs_analysis_report.md. "
    "_parse_header(top_cell/tool_version/layout/source/report_lines/cpu/elapsed) + _parse_rule_settings(recognize_gates/filter_unused/virtual_connect_colon/execute_erc) + "
    "_parse_overall(lvs_result/connectivity/property/missing_smashed_mosfet/short/open/correct_cells/incorrect_cells) + "
    "_parse_property_errors(Disc#/layout_w/source_w/diff_pct重算/device) + _parse_ext(open_circuit/unattached_label/unattached_port/virtually_connected/stamping_conflict 计数+信号名) + "
    "_parse_erc(erc_errors/erc_warnings/detail) + _root_causes + _solutions + _build_report(6 章节 Markdown). "
    "A=Array3G_TOP_L INCORRECT Calibre v2020.1, 1224 smashed, W 2.717u/1.476u, SecEnGapN/vap2!/viso!/VncsgnEn, open2/unatt_label5/unatt_port6/virt4/stamp1; "
    "hidden B=DDR5_PHY_TOP INCORRECT Calibre v2022.4, RECOGNIZE GATES=ALL/VIRTUAL CONNECT COLON=YES, 856 smashed, W 0.840u/0.420u, vcore!/vref!/vbias!/vddq!/vssx!, open7/unatt_label12/unatt_port3/virt5/stamp2; "
    "hidden B2=AES_CORE **CORRECT** 通过 case(0 errors 0 ext warnings)—测候选能否处理通过报告(不能总报 INCORRECT). "
    "反硬编码六轴: design Array3G/DDR5_PHY/AES 全不同; Calibre 版本 v2020.1 vs v2022.4; W 值 2.717/1.476 vs 0.840/0.420; smashed 1224/856/0; 信号名 SecEnGapN/vap2! vs vcore!/vref! 全不相交; B2 CORRECT case 杀总报 INCORRECT. "
    "check 16 条件 a-p: a(防泄漏+py_compile) b(B-run exit0+2文件) c(error_summary.json 7顶层键) d(B lvs_result==INCORRECT) e(report含基本信息+top_cell+tool_version) f(report含Rule设置3关键词) g(B ext_warnings open7/unatt_label12/stamp2) h(B property_errors 3元素+W值+diff_pct≥50) i(report含错误分类Connectivity+Property) j(B missing_smashed==856) k(report含根因节) l(report含解决方案节+可操作建议label/svdb/RVE) m(B2跨输入守卫CORRECT+0errors+0ext) n(反硬编码无A标记+A-run top_cell≠B) o(确定性3x sha256) p(error_counts dict+三键+smashed==856). "
    "自验: ref PASS 16/16 + 6 neg FAIL 2 distinct first_fail(b,e: empty_shell→b.B-2files, print_expected→e.report-topcell, core_deleted→e.report-tool, naive_hardcode_a→e.report-topcell, naive_no_correct→e.report-tool, naive_wrong_smashed→e.report-tool) + §4.9 三假 FAIL + 断言闸门 k=16 + 确定性 3x sha256 一致. "
    "**教训**: (1) **LVS 报告分析是 schematic_netlist L1 可验好范式**: 三类输入(.lvs.report/.ext/.erc.summary)结构化文本解析, 错误计数+Property W 提取+diff_pct 重算+根因+解决方案 → 16 条件天然丰富(结构/计数/数值/跨输入/确定性); "
    "(2) **B2 CORRECT 通过 case 是强反硬编码轴**: 候选必须区分 CORRECT/INCORRECT, naive_no_correct 总报 INCORRECT → B2 上 (m) FAIL; "
    "(3) **真实 260MB 报告不可附加 → 合成小型片段保留真实结构**: 头部 # Calibre/# Cell/# Layout + Rule 设置行 + LVS COMPARISON RESULTS + Property Error #N: Layout W=..u Source W=..u diff=..% Device:.. + missing smashed mosfet: N occurrences + .ext 五类警告段 + erc.summary, 完全离线可验; "
    "(4) **erhym U#1+U#2 是干净 produce 但 U#4 给根因假设 → A-grade rule#2 排除 U#4**: A-grade 任务说明只用提出需求的轮(U#1+U#2), 用户给根因/修复方案的轮不得用作 A 档; "
    "(5) **diff_pct 必须重算不能抄报告**: 报告里 diff=84.1% 是 |lw-sw|/sw, 候选硬抄字符串会错(0.84/0.42 → 100.0% 不是报告的 diff 值), check (h) 验 diff_pct≥50 容忍重算口径差异; "
    "(6) **L1/L2 比例债 23→24 轮**: 本轮又 L1(纯文本解析无 EDA 依赖), 选料优先 waveform/analog_context 低覆盖域但 fresh 池 top 候选(paosw mc31 waveview260/m3k7v mc38 waveview124)是 Q&A 非 produce → 降级选 erhym(schematic_netlist mc50 干净 produce), fresh D-domain clean produce 池结构性稀缺不变. "
    "台账 mark erhym→case；case-mark 197→198；schematic_netlist 110→111；D.jsonl 199→200。"
)

# Replace #368 流水 line with a 1-line pointer + #369 流水
lines[liu368_idx] = "- (归档批次 2063) 流水 #368 (WaveCmpWrap-001, waveform, B-grade synthesized L1, 16 条件 a-p) 已搬 MEMORY_D_archive.md"
# Insert #369 流水 right after the pointer
lines.insert(liu368_idx + 1, liu369)

# Update DEBT line (line index 3, 0-based)
for i, ln in enumerate(lines):
    if ln.startswith("DEBT: 0"):
        lines[i] = "DEBT: 0（#369 已合成 LvsRptAnalyze-001（schematic_netlist B-grade synthesized L1，Calibre LVS 报告分析器，解析 .lvs.report/.ext/.erc.summary 生成 error_summary.json+lvs_analysis_report.md，16 条件 a-p）；⚠️ L1/L2 比例债 23→24 轮（#365 降到的 20 已被 #366-#369 连续 4 轮 L1 顶到 24；fresh mc>=30 D-domain 池 candidates_mc30.tsv 重建得 342 fresh 候选，waveform/analog_context top 候选多为 Q&A 非 produce → 选料降级到 schematic_netlist；L2 需 live binary 不可移植 + 40min 预算风险高 → 继续 L1 produce）。下轮继续优先 L2/L3 produce，挑 hspice/spectre/calibre/wv 真跑类 trace；waveform(44)/analog_context(45) 仍为最低覆盖域，继续优先补；可降 mc 阈值到 ≥5 重建 fresh 池或跨 shard 共享 L2 trace）。"
        break

# Update PHASE line — prepend #369, demote #368 to archived reference
for i, ln in enumerate(lines):
    if ln.startswith("- **PHASE**"):
        new_phase = (
            "- **PHASE**: shard D 运行中。已交付 200 条 case（D.jsonl 200 行：analog_context:45/schematic_netlist:111/waveform:44）；台账 case-mark 198 + 1037 parked = 1235 已动过。"
            "**本轮 #369 = 交付 EDA-Eval-DesignFlow-LvsRptAnalyze-001**（schematic_netlist B-grade synthesized **L1**，Calibre LVS 报告分析器，解析 .lvs.report/.ext/.erc.summary 生成 error_summary.json+lvs_analysis_report.md，16 条件 a-p）。"
            "**#368**(归档批次 2063)：3qe6x→WaveCmpWrap-001（waveform B-grade synthesized L1，WaveCompare 波形对比 CLI 封装，边沿序列+四判决，16 条件 a-p）。"
            "**#367**(归档批次 2061)：d810y→WvDispCfg-001（waveform L1）。**#366**(归档批次 2060)：pspw5→WrCornerCmp-001（waveform L1）。"
            "**#365**(归档批次 2060)：p5x6n→CosWaveWdf-001（waveform **L2 真跑 WaveView ACE**，A-faithful，14 条件 a-n）。"
            "**#364**(归档批次 2060)：f86ll→DelayChainCmp-001（schematic_netlist L1）。**#363**(归档批次 2058)：dhgxy→NetlistSubstPlan-001（schematic_netlist L1）。"
            "**#369**：erhym/fhwang/10.129.2.14/mc50, **B-grade synthesized** **L1**(离线文本解析无 EDA 依赖), 16 条件 a-p；"
            "Calibre LVS 报告分析器 analyze_lvs.py --report --ext --erc --outdir → error_summary.json+lvs_analysis_report.md；"
            "_parse_header(Cell/Calibre版本/Layout/Source/行数) + _parse_rule_settings(RECOGNIZE GATES/FILTER UNUSED/VIRTUAL CONNECT COLON/EXECUTE ERC) + "
            "_parse_overall(lvs_result/Connectivity/Property/missing_smashed_mosfet/Short/Open/correct_cells/incorrect_cells) + "
            "_parse_property_errors(Disc#/layout_w/source_w/diff_pct重算/device) + _parse_ext(5类警告计数+信号名) + _parse_erc + _root_causes(4根因) + _solutions(6修复建议) + _build_report(6章节Markdown). "
            "**A-faithful 不可行**：U#1+U#2 是干净 produce(分析 LVS 错误类型+生成报告文件)但真实 260MB 报告不可附加 + /rundata/drcpa 私有路径不可移植 + live Calibre RVE/svdb 不可移植 → B 档 synthesized. "
            "A=Array3G_TOP_L INCORRECT v2020.1, 1224 smashed, W 2.717u/1.476u, SecEnGapN/vap2!/viso!; "
            "hidden B=DDR5_PHY_TOP INCORRECT v2022.4, 856 smashed, W 0.840u/0.420u, vcore!/vref!/vbias!, open7/unatt_label12/stamp2; "
            "hidden B2=AES_CORE **CORRECT** 通过 case(0 errors 0 ext)—杀总报 INCORRECT. "
            "反硬编码六轴: design/版本/W值/smashed数/信号名/B2 CORRECT case 全不同. "
            "自验 ref PASS 16/16 + 6 neg FAIL 2 distinct first_fail(b,e) + §4.9 三假 FAIL + 断言 k=16 + 确定性 3x sha256 一致."
        )
        lines[i] = new_phase
        break

# Update coverage line
for i, ln in enumerate(lines):
    if ln.startswith("- 📊 trace 覆盖率"):
        lines[i] = "- 📊 trace 覆盖率：198 / 1511 = 13.1%（mc>=30 候选池；D.tsv 现 198 case-mark + 1037 parked · 已动过 1235；快照 2026-11-07 21:4x sessions=2912 mc300=252 mc500=281 mc1000=8）。已覆盖 domain（D.jsonl 200 行）：analog_context:45 · schematic_netlist:111 · waveform:44。**#369**：erhym→EDA-Eval-DesignFlow-LvsRptAnalyze-001（已交付，schematic_netlist B-grade synthesized L1，Calibre LVS 报告分析器，16 条件 a-p）。**#368**：3qe6x→WaveCmpWrap-001（已归档，waveform L1）。**#367**：d810y→WvDispCfg-001（已归档，waveform L1）。**#366**：pspw5→WrCornerCmp-001（已归档，waveform L1）。**#365**：p5x6n→CosWaveWdf-001（已归档，waveform L2 真跑 WaveView ACE）。**#364**：f86ll→DelayChainCmp-001（已归档，schematic_netlist L1）。**#363**：dhgxy→NetlistSubstPlan-001（已归档）。**#362**：l5r0u→IOBufTune-001（已归档）。**#361**：0oeb7→DelApiProbePlan-001（并行）。**#360**：oh3te→AutocellPlaceGen-001（已归档）。**#359**：4qpyk→ShiftIntervalReport-001（已归档）。**#358**：5hbdw→SaTransistorExtract-001（已归档）。**#357**：tx5s5→TestModeExtract-001（已归档）。**#356**：aw9d7→SpiceClosureExtract-001（已归档）。**#355**(并行)：8orer→SchHierCopyPlan-001（已归档）。"
        break

# Update 体积 line
for i, ln in enumerate(lines):
    if ln.startswith("- 📦 体积"):
        lines[i] = "- 📦 体积：TASK_D≈25KB / MEMORY_D≈31KB（#369 顶替 #368 PHASE/coverage/debt/断言 行 + 归档 #368 流水→archive 批次 2063 + 新增 #369 流水；低于 32KB 红线）"
        break

# Update 断言 line
for i, ln in enumerate(lines):
    if ln.startswith("- 🧾 断言"):
        lines[i] = "- 🧾 断言: k_rationale=k_check=16 ✓（#369 LvsRptAnalyze-001，16 条件 a-p 全对账；日报三列 k(断言)=16/k(check)=16/一致=✓ 自证）。存量 200 条 test_rationale 全部以 `k 条断言：①…` 开头已核验达标。rewrite_queue.tsv 全部 done（无待修）。今日 152/200 达标（#369 新增 1 条达标）。"
        break

open(MEM, "w").write("\n".join(lines))
sz = os.path.getsize(MEM)
print("MEMORY_D updated: %d bytes (%.1f KB)" % (sz, sz/1024))
