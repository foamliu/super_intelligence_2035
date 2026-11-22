# Deepread: 1794918791243_xgund (e0046686 @ hfeg0plg68, mc=201, physical_verify)

## Session
- 265 msgs, lead agent, AutoSimUni SPF weakcell workflow
- User e0046686 builds/modifies AutoSimUni (PyQt GUI `autosim` + Python scripts) to add
  **weakcell** support to the SPF (parasitic) hack flow for bitcell memory characterization.
- Real hostname in prompts: hfeg0plg68 (workspace /home/e0046686/project/autosim_uni/).

## Real task (TASK_SPF_INT.md driven)
- Add WeakCell checkbox to autosim GUI; when checked, use solido weakcell params
  instead of strong cell; hack SPF generation; submit sim.
- Iterates: UI alignment (Qt layouts), weakcell run logic, solido PVT matching bug,
  config/cfg refactor for hack modes.

## Key Python artifacts (on hfeg0plg68)
- `/home/e0046686/project/autosim_uni/spf/parm_hack_for_large_spf.py` (1029 lines)
  — stream SPF bitcell param-name hack; V2 no corner matching; "process g 后缀剥离" builtin.
- `/home/e0046686/project/autosim_uni/spf/solido.txt` (393 lines, 48 PVT blocks)
  — solido weakcell param library.

## solido.txt format (the clean offline-Python subproblem)
- Block header: `*<mode>_<process>g_<voltage>_<temp>_<sig>`
  - mode ∈ {icell, rsnm, wm}
  - process ∈ {ff, sf, ss, fs}  → token = process + "g" (ffg, sfg, ssg, fsg)
  - voltage ∈ {0.6, 1.02}
  - temp ∈ {-40, 125}
  - sig = 6sigma
- Each block: 6 `.param` lines = 6 groups (pd_t, pd_b, pu_t, pu_b, pg_t, pg_b);
  each line has 9 params `<grp>_<i> = <float>` for i in 0..8.
- 16 icell + 16 rsnm + 16 wm = 48 blocks total.

## The bug (user msg idx 218)
> pvt在solido中没有匹配上... solido中的工况是这样组合的:
> `<mode>_<process>g_<voltage>_<temp>_<sig>`，即在process后面会固定拼一个g...
> 根据传入的pvt去solido中匹配参数块的逻辑需要再修改一下

=> The PVT→solido-block matcher built the lookup key with the raw process corner
(eg `ff`) instead of `ffg`, so queries never matched. Fix: append `g` to process
when constructing the solido block key.

## Synthesized case
- ID: EDA-Eval-DesignFlow-SolidoPvtBlockMatchFix-001
- Subpattern: solido_pvt_block_matcher_g_suffix_fix
- Domain: physical_verify
- Script: `solido_pvt_match.py <solido_txt> <pvt_query.json> <out_json>`
  parses solido.txt into PVT-keyed blocks; for each query {mode,process,voltage,temp,sig}
  builds key `<mode>_<process>g_<voltage>_<temp>_<sig>` and returns matched block's
  6 groups + per-group param count + values + match verdict. Stdlib only.
- A = sample_a/solido_a.txt (subset of blocks) + sample_a/pvt_query_a.json + task_brief.md
- hidden B = hidden/solido_b.txt (different mode/process/voltage/temp combos) +
  hidden/pvt_query_b.json (mix of match / no-match / g-suffix-trap queries)
- anti-hardcode: re-run on A yields A's oracle (≠ B).
