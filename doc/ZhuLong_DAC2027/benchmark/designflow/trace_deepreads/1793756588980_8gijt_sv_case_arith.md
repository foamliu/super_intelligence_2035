# Deepread: 1793756588980_8gijt (stevenh @ hfeg0pgn145, mc35, digital)

**Session**: 80 msgs, dir format `/home/stevenh/.cline/data/sessions/1793756588980_8gijt/`
**Keywords**: verilog:74;analog:41;pex:1;drc:1
**Project**: DDR5 DRGQX loopback timing testbench (ddr5_test.sv / ddr5_tasks.sv under /rundata/drgqx/)

## User turns
- U#0: paste `case(modereg.loopback_outsel)` DML/DMU branch with `timing.tLBDLY_lbdq = 1860-78-471+389+136+221;` style arithmetic
- U#10: paste similar with extra `+166`/`+155` terms (correction)
- U#16: "你可以直接帮我修改吗？路径/.../ddr5_test.sv 对应行" (directly modify the file)
- U#36: "/.../A_Summary.rpt 阅读一下看看failed行中有哪些存在LBDQ_Err或者LBDQS_Err非零值" (scan report for non-zero LBDQ errs → agent found 0/69)
- **U#44 (lead)**: "/rundata/drgqx/.../ddr5_tasks.sv 解析一下该文件中含有类似case语句赋值给同名称变量的行，并计算最终值" (parse the file for case-statement assignments to same-name variables, compute final values)
- **U#60**: "变成可执行脚本，我要快速修改" (make it an executable script for quick modification)

## Agent tool chain (U#44→U#79)
1. search_codebase → grep `case(.*loopback`, `timing\.tLBDLY`, `loopback_outsel`
2. editor `find_timing_assign.sh` (grep -n timing.tLBDLY + loopback_outsel) → run → found 16 branches × 2 vars (tLBDLY_lbdq/tLBDLY_lbdqs) lines 1752-1841
3. read_files ddr5_tasks.sv lines 1746-1841
4. editor `calc_tasks_timing.py` — **hardcoded** expressions dict {DML/DMU/DQL0-7/DQU0-7: {tLBDLY_lbdq: "1367+498-96-455+385+110", tLBDLY_lbdqs: "1337+570+20-101-463+369+217", ...}} → eval each → print table
5. editor `replace_timing.sh` — **hardcoded** sed substitutions (36 exprs for ddr5_test.sv + 32 for ddr5_tasks.sv), with backup `cp $FILE $FILE.bak.$(date)`, `sed -i -e 's/expr/value/'`
6. chmod +x → verified executable

## A-faithful analysis
- User gave **spec** ("parse case statements assigning to same-name variables, compute final values" + "make executable script for quick modify") + **file path**, did NOT give root cause or implementation method.
- Agent had to: locate case block → extract arithmetic expressions → compute → build replacement script.
- **A-faithful: QUALIFIED** (user spec + path, not implementation).
- **Deliverable**: `replace_timing.sh` + `calc_tasks_timing.py` at private `/home/stevenh/` → INFEASIBLE for sandbox (private /rundata/drgqx/ SV files, private output path) → **B档 synthesized**.

## B档 case design: SvCaseArithFold-001
**Archetype**: sv-case-arith-constant-folder (general parser, NOT hardcoded dict like agent)
**Deliverable**: `sv_case_arith_fold.py` stdlib CLI — parse `case(SELECTOR)...endcase` blocks in .sv, extract `LHS = ARITH_EXPR;` assignments where LHS appears in ≥2 branches ("same-name variable"), compute integer arithmetic (+,-,*,paren), JSON report + --rewrite mode.
**A** (visible): timing_A.sv — `case(modereg.loopback_outsel)` 8 branches, vars timing.tLBDLY_lbdq/tLBDLY_lbdqs, line-comment decoy.
**B** (hidden): timing_B.sv — `case(cfg.rd_mode)` 4 branches + default, vars cfg.tRDLY/tWRLY/tCSH, multiplication+parentheses, block-comment trap, single-branch-LHS trap (cfg.tDummy).
**Trap vs agent**: agent hardcoded exprs in dict; SUT must produce general parser. Cross-input guard: B uses different var names → hardcoded-A fails.
