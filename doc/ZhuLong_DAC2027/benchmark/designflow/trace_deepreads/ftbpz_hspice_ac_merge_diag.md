# ftbpz deepread — HSpice AC merge diagnosis Q&A

**session**: 1792543801789_ftbpz | **user**: ruminji | **host**: hfeg0pkn004 | **mc**: 14 | **domain**: spice_sim
**trace**: 15 msgs / agent=lead / 0 tool_calls (pure conversation Q&A) / 7 substantive user turns

## User question chain (verbatim)

1. "仿真一个level shifter小模块的后仿真，是否需要加上LDE效应" → LDE (LOD/WPE/PSE/Mx) explanation
2. "hspice语句会区分大小写吗" → HSpice case-insensitive, except string literals
3. **"hspice仿真ac特性，多个模块放在一起仿真结果不正确，但是单独的每一个模块仿真结果都是正确的，是什么原因？"** → rich root cause analysis (SELECTED)
4. "revision ID 如果改版的时候没改的话，会导致什么问题" → revision ID in LVS/tapeout
5. "revision id在哪里改？会涉及金属层次的改动吗？" → 3 scenarios, only 1 involves metal
6. "half density 是什么意思？" → DRC rule, metal density halved
7. "DRAM half density 设计是什么意思" → DRAM architecture, cells per bitline halved
8. "/proj/drcpa/V0/workdir/ruminji/drcpa_levelshifter.csv 这个csv文件里面matched cell一列，一共有多少种level shifter" → (no response, trace ends)

## Selected: Q3 — HSpice AC merge diagnosis

**User intent**: Debug why HSpice AC simulation gives wrong results when multiple modules are combined, but each module individually is correct.

**Agent answer structure** (msg 5, verbatim preserved):
- Section 一: 7 root causes ranked by probability:
  1. DC工作点被破坏 (DC operating point disruption) — .OP / .PRINT DC
  2. 节点名冲突 / 全局电源地短路 (Node name conflicts / global PG shorts) — .SUBCKT isolation
  3. 负载效应 / 输入阻抗不匹配 (Load effect / impedance mismatch) — .PRINT AC ZIN
  4. AC激励源放置错误 (AC stimulus placement) — only one AC source
  5. 反馈回路被意外闭合 (Unexpected feedback loop) — substrate/well coupling
  6. 仿真参数冲突 (Simulation parameter conflicts) — duplicate .AC/.OPTION
  7. 模型声明冲突 (Model declaration conflicts) — duplicate .MODEL
- Section 二: Diagnostic steps (ordered flowchart)
- Section 三: Debug techniques (逐级断点法, AC+DC联合分析, 观察每级波形)
- Section 四: Typical cases (LNA+Mixer, OTA+Buffer)
- Section 五: Summary table (suspicion → verification → fix)

## Case design

**form**: explain-Q&A → 产「结构化诊断指南生成器」
**case_id**: EDA-Eval-DesignFlow-HspiceAcMergeDiag-001
**A**: verbatim user Q3 + verbatim agent answer as knowledge_base.md
**hidden B**: HSpice transient simulation merge scenario with different root causes (IC冲突/上电顺序/反馈振荡/时间步长/去耦不足/衬底噪声/数模混合)
**deliverable**: hspice_merge_diag_guide.py(workdir, out_dir) → parses knowledge_base.md + scenario.txt → hspice_merge_diag_report.json
**check**: ≥8 assertions on JSON structure + B semantic content + A-leak guard + B-grounding + determinism + 4 negatives
