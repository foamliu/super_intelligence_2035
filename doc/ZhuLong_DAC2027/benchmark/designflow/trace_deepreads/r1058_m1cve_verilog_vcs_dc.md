# r1058 deepread — m1cve (johnl @ hfeg0pfn120 / 10.129.33.246)

**Session**: `1789882246438_m1cve.messages.json` (416 msgs, 1.4MB, 2026-09-20)
**Scan**: mc=95, keywords `verilog:263;rtl:180;synthesis:64;synopsys:57;netlist:40;dc_shell:34;aether:23;pyaether:17` → A-domain (digital/synthesis) on keyword face.
**Ledger prior note (parked)**: "User turn 6 'verilog+VCS+DC' is clean A-track need. But deliverable=cnt16 fixed design+cnt16-specific scripts ... NOT a reusable flow driver ... Vague prompt (no spec) => weak <8-cond check or L1-structural, violates §5 new-case L2/L3 + §4.3."

## Re-peek trigger
Parked under **§5 L2/L3 gate** which 11-15 令 declared OBSOLETE (§5 is now observation-only). 11-15 令 B-class 误杀 revival criterion: re-judge parked entries whose exclusion rested on旧 §5. This is exactly r1057's wcio5 pattern (keyword-inference parked → deep-read → A-domain viable). Check if m1cve is a parallel revival.

## Trace reality (full 416-msg walk)
Two distinct intents, NOT one:

**(A) verilog+VCS+DC task** — I6 only, abandoned by ~I40.
- I6 verbatim: 「请编写一个verilog 脚本 并用本地的vcs验证 然后yongdc综合」
- Agent could NOT execute shell (no run permission in this old session policy). Wrote cnt16.v + tb_cnt16.v + cnt16_synth.tcl + run scripts via editor only.
- User frustrated the agent couldn't run: 「我执行了结果我懒得看」「我才懒得保存 我只会帮你跑下命令」「你自己监控 我跑完了懒得跟你说」
- User asked agent to dump all commands into ONE file (`/home/johnl/.cline/scripts/data/run.sh`) so user could run manually. Agent obliged.
- **No accepted gold result** — agent never saw sim/synth output; user never confirmed correctness.
- Abandoned by I136 when user pivoted.

**(B) tokenplan API token testing** — I136–I414 (the dominant ~280-msg task), eventually succeeded.
- I136: user wants a script to test their tokenplan token (`11_44952_...`, Base URL `http://10.129.8.86:8899/token/v1`).
- Long debug: 403/timeout from wrong model names → fix → I414 success (glm-5.3-flash HTTP 200).
- This is **agent-platform API testing**, not EDA design flow. Internal endpoint unreachable by check().

## Re-judgment under new (11-15) standard
Only two legitimate exclusions remain: (1) no real trace, (2) no checkable deliverable with teeth.

- **Intent (B) tokenplan**: not EDA design flow + internal endpoint unreachable by check → legitimately excluded (not a §5 call).
- **Intent (A) verilog+VCS+DC**: real A-domain intent ✓. But:
  - No accepted gold in trace (agent never ran it, user never confirmed) → A档 trace-faithful has no gold to anchor check.
  - A B档 reframe (synthesize a clear cnt16 spec + deliver RTL+tb+synth flow) is conceivable, BUT the judge host has no VCS/iverilog (confirmed: `which vcs/iverilog` empty on app.e0031982 box). An L1-static-only check (structural invariants, no subprocess run) risks the "weak <8-cond check" the parked note flagged — i.e. §4.3 teeth concern is NOT a旧-rule artifact, it's a real §4.2/§4.3 gate.

## ⭐ Key capability discovery — VCS + dc_shell ARE on .75
`tools.eda_flow.run_commands` on .75 sandbox found:
- `/apps/synopsys/SRB/vcs/R-2020.12/bin/vcs`
- `/apps/synopsys/SRB/designcompiler/O-2018.06-SP5-5/bin/dc_shell`
- (no iverilog/yosys)

**Implication**: design_flow check() can run VCS sim + DC synth ON .75 when the eval is configured with `--upstream http://10.129.32.75:8664/v1/run_code` (per `docs/design_flow_session_backend.md` §4: `session.run_code(test+wrapper)` executes on the backend). For agent self-verify, `tools.eda_flow.run_code(lang="pyAether", host="aether", workdir=...)` runs Python on .75 where VCS/DC are on PATH → **L2 digital cases with real VCS/DC in check() are now buildable + self-verifiable**.

This unblocks a whole class of L2/L3 digital cases (verilog sim + synthesis flow) that were previously L1-static-only (e.g. AsyncFifoSim-001 explicitly notes "No simulator is invoked (the local judge host has no vcs/iverilog)"). Once 11-24 scan returns fresh A-domain candidates, prefer building L2 VCS/DC cases with this path.

## Verdict
m1cve **re-confirmed parked**, but for a CORRECTED reason:
- ❌旧 §5 L2/L3 gate (obsolete, do not cite)
- ✅ §4.2/§4.3 teeth: no gold in trace + judge host sim-less → only L1-static check possible → weak teeth. Legitimate exclusion under new standard.
- Intent (B) tokenplan: not EDA, legitimately excluded.

**Not a revival** (unlike wcio5). The旧 §5 citation in the original note should be corrected to §4.2/§4.3.

## Forward action
- 11-24 scan quota resets → run full 698-host scan → POOL_SWITCH → mc≥5 selection.
- For new A-domain verilog/sim/synth candidates: build **L2 cases** using .75 VCS/DC via `run_code` self-verify (this deepread's capability discovery). Prefer over L1-static.
- m1cve ledger note: append re-peek result + corrected exclusion reason.
