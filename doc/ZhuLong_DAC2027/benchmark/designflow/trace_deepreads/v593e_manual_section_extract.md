# Deepread: v593e (t0002614 @ hfeg0pkn004, mc52, spice_sim)

**Session**: 1794208159902_v593e.messages.json (subdir, 208KB, 48 msgs)
**User**: t0002614 on hfeg0pkn004
**Agent**: lead (cline)
**Match count**: 52 (keyword: hspice/siliconsmart/spectre/ngspice/simulator/spice/custom_sim)
**Pool**: revival-pool #34 (r652), parked→case

## User intent (verbatim)

Two consultation questions:

1. **[msg 0, ts 1794208160331]** 「我想从DRAM的design中抽取一个BLSA和BL上的loading出来做仿真，怎样抽取网表最方便」
   - DRAM BLSA + BL loading extraction for simulation, how to extract netlist most conveniently

2. **[msg 32, ts 1794275215895]** 「Aether中在DM界面查看view，其中config view的作用是什么」
   - In Aether DM interface, what's the role of config view

## Assistant workflow

- Loaded `aether-tool-qa` skill (Aether EDA tool Q&A knowledge base)
- Wrote `search_kb.py` to grep aether_tool_qa.md (5189 lines, 52 hits on netlist/局部/部分提取/hspice/仿真)
- `read_files` on:
  - `part_I_Design_Manager.md` L605-700 (section 2.7.6 Export Netlist)
  - `part_II_Schematic_Editor.md` L170-230 (Export Netlist cross-ref)
  - `part_VIII_Mixed-signal_Design_Environment.md` (MDE)
- Grep found "Figure 2.6 Create Config View" at L71 of part_I_Design_Manager.md (section 2.2 New Cell/View)
- Produced structured Chinese answer: 方案一 (tb cell + 等效 BL loading Cbl/Rbl), 方案二 (Export Netlist, Stop View List, Top Only), 方案三 (hierarchical extract); Config View = mixed-mode simulation setup (Library List / View List / Stop List, MMSIM/RCE templates, SimView Editor)

## Artifacts identified

- **Manual section 2.2 New Cell/View** (L54-94): Menu/ToolBar/BindKey/Tcl Command header, 16 view types (bullet list), 5 Examples (2.3-2.7), 17 Figures (2.4-2.16), 0 Tables, 8 pages (264-271), Note×1
- **Manual section 2.7.6 Netlist/Export Netlist** (L611-679): Menu/ToolBar/BindKey/Tcl Command header, 0 view types, 5 form tabs (General/Format/HDL/CDL/SPICE), 1 Table (2.20 Simulation Type), 4 Examples (2.25-2.28), 15 Figures (2.97-2.111), 13 pages (359-371), Note×4

## A-tier vs B-tier

- **A-tier infeasible**: No /proj artifacts involved — this is a pure consultation/Q&A session. The "artifacts" are Aether manual markdown sections on hfeg0pkn004 under t0002614's ~/.cline/skills/. The manual IS world-readable (scp'd successfully), but the session itself produced no project files.
- **B-tier synthesized**: Converted the consultation into a deterministic structured-extraction task. A = real manual section 2.2 (verbatim from part_I_Design_Manager.md, with OCR ligatures preserved). Hidden B = real manual section 2.7.6 (also verbatim, structurally different). Both are real manual content the assistant actually read during the trace.

## Case design

- **Case ID**: EDA-Eval-DesignFlow-ManualSectionExtract-001
- **Task**: Parse Aether DM manual section markdown → structured JSON (28 top-level keys)
- **A**: section 2.2 New Cell/View (create, 16 view_types, 0 tables, 5 examples, 0 form_tabs)
- **B**: section 2.7.6 Netlist (export, 0 view_types, 1 table, 4 examples, 5 form_tabs)
- **Cross-input guard**: 21 of 28 fields differ (section_number, title, menu_path, purpose_verb, examples, figures, tables, pages, view_types, form_tabs, counts)
- **A-leak guard**: New Cell/View, ChargePump, cp_amp, SimView, MMSIM, PhysConfig, Platform
- **Assertions**: 35 (a-ii), k_rationale==k_check==35
- **4 negatives**: empty_shell (no output), print_only (invalid JSON), naive_hardcode_a (A values on B), core_deleted (null fields)
- **Ligature normalization**: ﬁ→fi, ﬂ→fl (needed for Config/PhysConfig view type matching)

## Self-test results

- check.py SELF-TEST: PASS (reference 35/35)
- negative_selftest: ref PASS + 4 negs all FAIL distinctly
