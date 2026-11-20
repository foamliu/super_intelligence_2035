# 2c126 — gracew DDR5 ATPG testmode→pattern 验证 (r426 深读)

- **trace**: gracew / hfeg0pkn004 / `1793771746058_2c126` / mc70 / kw `verilog:1085;analog:115;rtl:56;aether:13;netlist:12;cmos:12;systemverilog:5` (refined-A: a_tot=1146, c=13, b=0, n=127, top_tool=verilog, clean A-dominant digital)
- **session 位置坑**: session 是**目录**非文件（autofs）—— `/home/gracew/.cline/data/sessions/1793771746058_2c126/1793771746058_2c126.messages.json` (1.21MB, 188 msgs)。需 `ls /home/gracew/` 触发挂载后再 cat（同 lilaj r424 模式）。
- **agent**: deepseek-lead。tool use: editor×34, run_approved_command×27, read_files×14, list_allowed_files×13, search_codebase×2, run_commands×2.
- **5 user turns**（5/5 全 find/Q&A，未给根因 → A-faithful produce-task INFEASIBLE → B 档合成）:
  - U#1「我想检查这 cm1_io_Wr4phF1<2:0> 个 testmode 是否符合期望该跑那个 pattern 或者这个 pattern 应该怎么写」
  - U#2「/rundata/.../cmds_testmode/cmds_fuse/ 这个路径下有什么可以验证这些 testmode 的 pattern 吗 [cm1_io_Wr4phF1/Hi/R0/R1Hi/T + cm1_ro_AdjAllRefNewOp/AdjSrefOsc500ns 等 10+ 个]」
  - U#3「针对上面那几个可以通过 fuse 验证的 tm，要怎么写 pattern，请给个例子」
  - U#4「波形显示 DQ0/DQ8 分别输出 BANKA 和 BANKB 的值，我希望只有 DQ0 输出」
  - U#5「请找到 cm1_ro_Maxcnt<1:0>/cm1_ro_NCSPCStrim<5:0>/cm1_ro_NewDisOn/cm1_ro_AllRefPump2Stg/cm1_ro_AllRef1pump8Stg 相关的验证 pattern」
- **agent 实际产出**: ~30 个 throwaway search/probe 脚本（`search_wr4ph.py`/`search_rtl.py`/`search2.py`/`search3.py`/`read_opt.py`/`find_consumer.py`/`find_cons2-5.py`/`coverage.py`/`coverage2-3.py`/`rtl_probe.py`/`wide.py`/`blow_probe.py`/`blown_probe.py`/`pat_probe.py`/`mb_probe.py`/`mb2.py`/`find_ro.py`/`find_ro2-5.py`），反复 grep pattern 文件中 testmode 引用，回答"哪些 pattern 验证这些 testmode"。无可复用单一工具产出 → B 档合成。
- **沉淀需求** (B 档合成 TmPatternXref-001): testmode→pattern 交叉引用工具。5 维度全可追溯 (TFC 5/5=100%):
  1. testmode 名解析 (cm1_<io|ro>_<core>[<hi:lo>]) ← U#2/U#5 testmode list + find_ro.py
  2. pattern `# TM:` 指令解析 ← U#2 + pat_probe.py
  3. prefix io/ro 区分 ← U#2 list 含 cm1_io_ 与 cm1_ro_ 两类
  4. bus range 覆盖 ← U#2 + U#4 波形 DQ bit 诊断
  5. orphan 检测 ← agent 反复 grep 找不到的 testmode
- **合成 case**: EDA-Eval-DesignFlow-TmPatternXref-001 (digital L1 spec-driven cross-check, k=14 B档). deliverable=tm_pattern_xref.py 纯 stdlib. A=6pat/8tm, B=hidden 10pat/10tm (prefix 撞/base 词边界/部分 bus/multi-TM/注释 TM/无 TM orphan). 自验 ref PASS 14/14, 4neg FAIL, §4.9(a)(b)(c) FAIL.
- **同 user**: gracew 第 4 case (r411 PatternTaskXref / r414 SignalRunXref / r423 Bl6CompcodeMerge / r426 TmPatternXref)，同 DDR5 drgqx 项目不同 session 不同子任务，deliverable 零重叠（4 种不同 cross-check archetype）。
