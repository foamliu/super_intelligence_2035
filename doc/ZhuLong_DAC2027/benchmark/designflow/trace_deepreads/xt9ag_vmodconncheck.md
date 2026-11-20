# Deepread: 1793683605769_xt9ag (e0045144 @ hfeg0pkn002, mc=301, digital)

**Session**: 443 msgs (225 user / 218 asst), agent=lead, tools: editor96/read_files63/run_approved_command44/list_allowed_files8/run_commands2/SandBox_MCP_Server__run_code3/search_codebase3.
**Scan keywords**: verilog:790, rtl:86, pyaether:8, netlist:6, synthesis:2, systemverilog:1, pdk:1 (digital-dominant).
**User**: e0045144 — same user as o0c8y (AHB master Verilog, r162). Working under `/home/e0045144/ACC/script/` + `/home/e0045144/cpu/`.

## User turns (verbatim, A-faithful eligible marked ★)

- ★ **USER#0 (idx0)**: `可以帮我产生一个check 模块之间连线是否一致的脚本吗\n输入两份verilog，check这两份文件相同模块之间的连线是否一致` — **clean build requirement, no root cause / no fix given** → A-faithful eligible. Selected as task prompt.
- USER#231 (idx231): `脚本有完整生成吗` — status check (not a requirement).
- ★ USER#256 (idx256): `帮我检查下下面两个verilog中对应module以及内部instance模块interface是否一致，以及 内部连线是否一致` + 2 real paths (`pa_cpu_merged_top.v` vs `pa_cpu_merged_top_hack_sram_dbc.v`) — clean refinement with real inputs (refines USER#0's intent; not used as prompt to keep A-faithful = original need, but informs gold semantics).
- USER#332 (idx332): `我修改了文件在对比下呢` — status (re-run).
- USER#338 (idx338): `为什么用下面的脚本执行完log显示乱码` + script + log paths — **gives root cause (encoding)** → disqualified for A.
- USER#363 (idx363): `帮我把UTF-8显示改成ASIC码，并且效果一样` — fix request (different task: encoding rework).

## Agent trajectory & gold standard

Agent iterated through several script names (incremental editor writes):
1. `check_verilog_conn.pl` (msg#13-49, Perl, first attempt — full-file writes)
2. `gen_check_script.py` (msg#67-135, Python generator variant)
3. `cvc.pl` (msg#145-320, **Perl — primary deliverable**, "Check Verilog Connections")
4. `vconn_check.pl` (msg#193-207, alt Perl)
5. `syncheck.py` (msg#217-250, Python synthesis-check variant)
6. `run_cvc_check.sh` (msg#266-302, bash wrapper invoking cvc.pl on the two real pa_cpu files)

**Gold = cvc.pl logic** (msg#145 first creation, 5217c; refined through msg#320):
- CLI: `perl cvc.pl <f1.v> <f2.v>` / `--dir <d1> <d2>` / `-f <fl1> <fl2>`
- Parse: strip /* */ and // comments → split on `module <name>` / `endmodule` → per module body, split statements on `;` → skip assign/always/initial/input/output/.../keyword statements → try match `<Type> <inst_name> ( <ports> )` (strip `#(params)` first) → parse ports: named `.port(sig)` (regex `\.(\w+)\s*\(([^()]*(?:\([^()]*\)[^()]*)*)\s*\)`) or positional (comma-split at depth 0, `__O<i>`)
- Group instances by `type` across all files; common module types = types in both groups
- Compare: for each common module type, for each instance pair, compare port→signal maps; emit diffs; write `cvc.log` + `cvc_diff.csv` (Module,Port,Sig1,Sig2,DiffType,Detail); print `[PASS] All consistent!` or `[FAIL] N diff(s)`; exit 1 on diffs else 0.
- Helpers: `comma()` (depth-aware comma split), `nrm()` (whitespace-normalize signal names), `instcnt()`, `grp()`.

User accepted at USER#332 ("我修改了文件在对比下呢" — re-running after edits → cvc.pl was the working tool).

## Benchmark case design (VmodConnCheck-001)

- **Domain**: digital (verilog structural check, L1-static — offline Python, no EDA binary; VCS not needed for static parse+compare).
- **A-faithful**: prompt = USER#0 verbatim. task_brief ≤3 lines fixes only the deliverable interface (Python3 CLI + JSON report schema + exit codes), not the intent.
- **Deliverable**: `check_vconn.py` (Python3, CLI `<f1.v> <f2.v>`) — Python chosen for judge portability (agent itself also produced Python variants gen_check_script.py/syncheck.py, so Python is within the solution space; interface constraint ≠ intent change per §3 ①).
- **Reference**: Python port of cvc.pl logic — parse modules (strip comments, split module...endmodule, ANSI + non-ANSI header port extraction), extract instances (named .port(sig) + positional), group by module type, compare port→signal maps for matched instance names, plus module-level port-interface diff. JSON report: {modules_compared, instances_compared, diffs:[{module,instance,port,sig1,sig2,type}], n_diffs, verdict}; exit 0=PASS/1=FAIL.
- **Hidden B** (inline in check.py, names disjoint from A: dsp_core/dsp_mul/dsp_acc/u_mul/u_acc/rst_n vs A pa_cpu_top/pa_alu/pa_regfile/u_alu/u_rf):
  - B1: identical pair → expect PASS (0 diffs)
  - B2: u_mul .b rewired (b→a) → expect port_signal_mismatch
  - B3: u_acc instance added in F2 only → expect instance_missing
  - B4: dsp_acc module header rst_n port removed → expect port_missing
- **check.py 16 conds (a-p)**: (a)zip含check_vconn.py (b)compile通过 (c)B1 PASS n_diffs0 (d)B2 FAIL+u_mul port_signal_mismatch (e)B3 FAIL+u_acc instance_missing (f)B4 FAIL+rst_n port_missing (g)JSON五键 (h)反硬编码B名不泄漏A名 (i)3-seed一致 (j)modules_compared==3 (k)instances_compared==2 (l)极简verilog不崩 (m)含解析逻辑非stub (n)内容敏感 (o)diff六键schema (p)无reference泄漏
- **Self-verify**: reference_submit.zip PASS 16/16; 3 negatives (naive_noop/always_fail/gutted) all FAIL; §4.9 (a)empty-shell FAIL cond(a) (b)print-only=neg1 FAIL (c)ref-delete-core=neg3 FAIL. Assertion gate k_rationale=16=k_check≥8 PASS. jsonl test==disk check.py sha sync.

## Notable

- **BLOCKER ③ note**: this session is a rare genuine digital session (verilog:790 dominant, e0045144 = digital user) in the .75 cline cluster which is structurally analog-heavy. Static verilog parse+compare is the viable L1 path (VCS not required). Same user as o0c8y (r162 AHB master) — e0045144 has now produced 2 shard-A digital cases.
- Files cvc.pl/check_verilog_conn.pl/syncheck.py no longer on disk (not in .snapshot either — only acc_auto_connect*.pl retained); gold reconstructed from trace editor new_text blocks.
