# oebdw — 256_topo_predict_system coupling tool path-portability

- session: 1795403490348_oebdw.messages.json
- user: feng1z @ hfeg0pkn002 (10.129.2.11), mc24, domain = pnr_signoff/eda_other (post-route coupling analysis)
- 23 msgs / 107KB (active messages.json; also 2MB .messages.archive.json not pulled)

## User real intent (trace-faithful)
feng1z has a coupling-analysis tool suite under `/home/feng1z/256_topo_predict_system/`:
- `gen_coupling_summary_en.py` (305 lines) — parses `All_SignalCouplingDetail_forsilicon_normal.rpt`
  into a per-HB-group coupling summary Excel. 8 sub-groups, 3-level column layout, same-line-type
  negation rule (eBLb/oBLa=type2 → negate), column sums, round(sum/1e-18,1) row. 3 modes: -g group /
  -b range / multi -i merge.
- `gen_ccap_sorting_table.py`, `run_coupling_all.sh` (5 perl perspectives), .ods template, BLNetMapping.

**Problem**: scripts hardcode `/home/feng1z/256_topo_predict_system/` paths → break for any other user.
**Want**: make all scripts path-relative (SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))),
so the project dir can be copied and run by anyone.

## Trace flow
- U#0 context summary: lists 7 deliverable files, explains the hardcode-path bug, says "已改为相对脚本位置(SCRIPT_DIR)".
- U#1/U#4/U#7 "搞定了吗/run 的命令发我/改好了吗" — agent's editor tool repeatedly rejected
  ("Invalid input for tool editor: Type validation failed", "丢参数"). Agent tried editor ~6x, then
  run_approved_command sed (/usr/bin/sed outside dynamicFileRoots → rejected), then a bash patch script
  via editor (also rejected).
- U#18: agent gave up on tools, handed user **3 sed commands + 1 cp (step-0 template)** to run manually:
  ① gen_coupling_summary_en.py DEFAULT_RPT → SCRIPT_DIR; ② gen_ccap_sorting_table.py BASE → SCRIPT_DIR;
  ③ run_coupling_all.sh paths; ④ cp .ods → fixed template name.
- U#19 "我指纹几个问题，你可要别跑代码了，太吃token了" → agent stops running code.
- U#21 "修复命令我只跑一次就行吗？第0 步 我只跑一次就行吗" → U#22 agent: yes, each once permanently
  (sed rewrites file content; cp template once). Only re-run step-0 if template edited.

## Verified on .75 (r1106)
- ssh 10.129.2.11: current `gen_coupling_summary_en.py` already has `DEFAULT_RPT = os.path.dirname(os.path.abspath(__file__)) + "/" + ...`
  ⇒ the sed fix WAS applied (user ran it). Portable state confirmed.
- rpt format (514 lines): blocks of
  `<s1> <s2> <s1> <s2> <val>` then `<s1> <s2> totalCoupling=<val>`. Parser regex:
  `([\w<>\[\]]+)\s+([\w<>\[\]]+)\s+totalCoupling=([\d.eE+-]+)`, symmetric couple_map.
- line_type: prefix eBLb/oBLa → 2, else 1; val negated when target_type == col_type.
- HB_BASE={20:240,21:252,22:264}; groupN → start=HB_BASE[hb]+(N-1)*4, 4 BL indices, 6 sigs/idx.

## Case design (B档 synthesized — real /home/feng1z tree not sandbox-reachable)
task_id: CouplingToolPortabilityProduce-001, domain pnr_signoff, k≥10.
- A (SUT-visible): coupling_tool_A/ with hardcoded `/home/feng1z/256_topo_predict_system/` paths +
  rpt/coupling_detail_A.rpt (A-specific BL indices/values) + SPEC.md.
- hidden-B: coupling_tool_B/ hardcoded `/home/verif_eng/coupling_analysis/` + rpt/coupling_detail_B.rpt
  (different BL indices/values). A/B token-zero-intersect.
- Deliverable: submit.zip = make_portable.py (+ patched script). check runs make_portable.py on B,
  then patched B script on B rpt → CSV; verifies no /home/ hardcode, SCRIPT_DIR present, totalCoupling
  pairs parsed = oracle, negation rule, col sums, anti-hardcode A absent, determinism 3x, §4.9 三假 FAIL.
