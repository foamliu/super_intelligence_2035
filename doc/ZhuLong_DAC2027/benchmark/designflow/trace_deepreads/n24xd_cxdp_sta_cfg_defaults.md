# Deep-read: n24xd — CXDP STA flow config defaults + `$(CXDP_DESIGN_NAME)` resolution

- **session**: `1795488475556_n24xd.messages.json` (1.3 MB, 170 msgs: 98 user / 72 assistant)
- **trace_source**: user=`e0046913`, host=`hfeg0pkn001` (also indexed on hfeg0plg90/plg46/plg24 — same NFS home), `match_count=126`
- **keywords**: netlist:659; pt_shell:270; rtl:215; primetime:80; synopsys:35; verilog:12; pdk:4; techfile:3
- **domain**: pnr_signoff (STA / PrimeTime) — A-shard
- **session path (resolved r1490)**: `/home/e0046913/.cline/data/sessions/1795488475556_n24xd/1795488475556_n24xd.messages.json` — **depth-2 subdirectory** (r1489 only checked depth-1, hence the locate-DEBT; the scanner uses `find /home/*/.cline/data/sessions -maxdepth 3` so it found it)
- **claimed**: r1489 (ledger A, status=claimed), deep-read done r1490

## User intent flow (8 distinct intents across 19 user turns)

| # | msg | Intent | Type |
|---|---|---|---|
| 1 | U#1–U#5 | Debug: `make common` (LSF queue) fails vs `make common CXDP_STA_RUN_MODE=direct` (local) works; root cause = `/proj/lacaa`↔`/rundata/lacaa` path mapping; rewrite Makefile LSF submit to FM-style "whole command to remote" (`bsub -K -Is`) | debug + script edit |
| 2 | U#6–U#9 | Evaluate STA results at `…/sta/all_out/v1.0_Latest` | assessment Q&A |
| 3 | U#10–U#11 | Create `create_cxdp_sta.py` (mimic `create_cxdp_dir.py` for lint) to one-shot generate a CXDP STA flow run-tree | script generation |
| 4 | U#12–U#13 | Restructure `src_pre` from `<root>/sta/run/src_pre` to `<root>/src_pre` (sibling of sta); identify which scripts need editing + give before/after | analysis + script edits |
| 5 | U#14–U#15 | `read_sdc` shows 4 warnings but no detail; how to see them; better to print error/warning to log? why not shown? | Q&A + script-improve suggestion |
| 6 | U#16 | Evaluate STA; if script-level OK, modify `create_cxdp_sta.py` to replace script source | assessment + script edit |
| 7 | **U#17–U#18** | **Modify `CXDP_DESIGN_CFG` defaults + resolve `$(CXDP_DESIGN_NAME)`; check `CXDP_STA_CFG` similarly** | **config transformation** ← CHOSEN |
| 8 | U#19 | Evaluate STA results at check_for_accept_1124 | assessment Q&A |

## Chosen intent for case synthesis: U#17 (config-file normalization)

**User original request (U#17, verbatim core)**:
> `CXDP_PRE_SDC_MODES = NORM` / `CXDP_PRE_SDC_NORM = pa_cpu_merged_top.out.sdc` / `CXDP_PRE_SDC_SCAN_SHIFT =` / `CXDP_PRE_SDC_SCAN_CAPTURE =`
> 改进建议：1. `CXDP_PRE_SDC_NORM` 改默认 `<Design>.norm.sdc`; 2. `CXDP_PRE_SDC_SCAN_SHIFT` 默认 `<Design>.scan_shift.sdc`; 3. `CXDP_PRE_SDC_SCAN_CAPTURE` 默认 `<Design>.scan_capture.sdc`; 4. CFG 中带 `$(CXDP_DESIGN_NAME)` 都改为实际设计名（`$` 无法被解析）; 并检查 `CXDP_STA_CFG` 是否有类似问题，若存在则优化。

**Why this intent**: self-contained (input = 2 CFG files + design name; output = 2 normalized CFG files), checkable with ≥8 independent structural assertions, supports hidden-B (different design name + different golden-hardcoded name), supports negatives (stub/empty/no-op/only-partial). L1 produce-task (offline CFG transform, no real EDA run needed) → `judge_layers=[L0,L1]`. Faithful to a real user pain (`$` not expanded by `read_cfg_var.py` ⇒ CMD-013 crash root cause).

**Assistant resolution (msg162, verbatim rules)**:
1. `CXDP_PRE_SDC_NORM`: default `.out.sdc` → `<design>.norm.sdc`
2. `CXDP_PRE_SDC_SCAN_SHIFT`: empty → `<design>.scan_shift.sdc`
3. `CXDP_PRE_SDC_SCAN_CAPTURE`: empty → `<design>.scan_capture.sdc`
4. Replace **all** `$(CXDP_DESIGN_NAME)` / `$(DESIGN_NAME)` in DESIGN_CFG with actual design name (because `read_cfg_var.py` does not do make-style `$()` expansion ⇒ unresolved `$` crashes the flow).
5. `CXDP_STA_CFG`: same `$(CXDP_DESIGN_NAME)` replacement AND replace golden-hardcoded design name (e.g. `pa_cpu_merged_top`, `cla_top`) with the new module name (e.g. `CXDP_STA_NETLIST_LIST`, `CXDP_STA_PRE_SDC_NORM`).
6. `$(...)` **inside comments** (`# … $(CXDP_DESIGN_ROOT) …`) is harmless (not parsed) → leave as-is. Only **effective assignment values** must be `$`-free.
7. `Makefile` / `sta.tcl` / `proc/*.tcl` keep their `$()` (they ARE make/PT-expanded at runtime) → do NOT touch.

## Asset A (input, from session msg104 read_files) — `CXDP_DESIGN_CFG`

Design name = `pa_cpu_merged_top`. Key effective lines (full file 6469 B saved below in appendix):
```
CXDP_DESIGN_NAME = pa_cpu_merged_top
CXDP_DESIGN_HIERARCHY = module
CXDP_RTL_SRC_DIR = src_rtl
CXDP_PRE_SRC_DIR = src_pre
CXDP_POST_SRC_DIR = src_post
CXDP_POST_PHY_DIR = src_phy
CXDP_DESIGN_INCLUDE_DIR = $(CXDP_DESIGN_ROOT)/include/src
CXDP_PROJ_INCLUDE_DIR = ../../include/src
CXDP_DESIGN_ROOT = ../../..
CXDP_RTL_FILE_LIST = designlist
CXDP_MEM_LIB_DIR       = $(CXDP_DESIGN_ROOT)/include/memory/lib
CXDP_MEM_VLOG_DIR      = $(CXDP_DESIGN_ROOT)/include/memory/vlog
CXDP_MEM_RTL_DIR       = $(CXDP_DESIGN_ROOT)/include/memory/rtl
CXDP_MEM_MBIST_DIR     = $(CXDP_DESIGN_ROOT)/include/memory/mbist
CXDP_PRE_SDC_MODES = NORM
CXDP_PRE_SDC_NORM = $(CXDP_DESIGN_NAME).out.sdc
CXDP_PRE_SDC_SCAN_SHIFT =
CXDP_PRE_SDC_SCAN_CAPTURE =
CXDP_PRE_SDC_OCC_SCAN_CAPTURE =
CXDP_POST_SDC_MODES =
CXDP_POST_SDC_NORM =
CXDP_POST_SDC_SCAN_SHIFT =
CXDP_POST_SDC_SCAN_CAPTURE =
CXDP_POST_SDC_OCC_SCAN_CAPTURE =
CXDP_PRE_UPF_FILE        = $(CXDP_DESIGN_NAME).upf
CXDP_POST_UPF_FILE       = $(CXDP_DESIGN_NAME).upf
```
Note: in the *golden* (`check_for_accept_1124`) the `CXDP_PRE_SDC_NORM` was already manually set to `pa_cpu_merged_top.out.sdc` (literal, not `$(...)`). The **template** uses `$(CXDP_DESIGN_NAME).out.sdc`. The case should hand the agent the **template-style** file (with `$(CXDP_DESIGN_NAME)`) so the transform is non-trivial.

## Asset A — `CXDP_STA_CFG` (3193 B, msg104)

Golden design = `cla_top` (hardcoded; inconsistent with DESIGN_CFG's `pa_cpu_merged_top` — this is the real-world messiness the user wants fixed). Key effective lines:
```
CXDP_STA_DB_VER          = Latest
CXDP_STA_TYPE            = pre
CXDP_STA_PARAMETER_TYPE  = WL
CXDP_STA_NETLIST_LIST      = cla_top.netlist.f
CXDP_STA_NETLIST_LIST_DIR  = ../data
CXDP_STA_LIB_CORNER   = WCL
CXDP_STA_RC_CORNER    = RCWORST
CXDP_STA_CORNER       = ssgnp_v0p675_0c
CXDP_STA_CORNERS      = ssgnp_v0p675_0c
CXDP_STA_LIB_TYPE     = db
CXDP_STA_LIB_VT_TYPES = LVT SVT ULVT
CXDP_STA_TOOL_NAME    = PrimeTime
CXDP_STA_TOOL_VERSION = 2022.12-SP5
CXDP_STA_JOB_QUEUE_EN = 1
CXDP_STA_JOB_QUEUE    = fqueue2h
CXDP_STA_PBA_MODE     = none
CXDP_STA_POCV_EN      = 0
CXDP_STA_PRE_SDC_NORM  = cla_top.norm.sdc
CXDP_STA_POST_SDC_NORM =
CXDP_STA_SDC  =
CXDP_STA_SDF  =
CXDP_STA_SDF_DIR =
CXDP_STA_SPEF =
CXDP_STA_SDC_MODES = NORM
CXDP_OUTPUT_TAG   = v1.0_Latest
CXDP_OUTPUT_LOCAL = 0
CXDP_STA_QA_EN          = 1
CXDP_STA_QA_TNS_WARN    = -5.0
CXDP_STA_QA_WNS_WARN    = -1.0
CXDP_STA_GEN_TIMING_REPORT = 1
CXDP_STA_WRITE_SDF_EN   = 0
CXDP_STA_WRITE_SPEF_EN  = 0
CXDP_STA_SI_EN          = 0
CXDP_STA_GLITCH_RPT_EN  = 0
CXDP_STA_IRDROP_EN      = 0
CXDP_STA_IRDROP_FILE    =
CXDP_STA_MVDD_EN        = 0
CXDP_STA_MVTC_FILE      =
```
STA_CFG has NO `$(CXDP_DESIGN_NAME)` (it uses literal `cla_top`), so rule 5 = replace the **golden-hardcoded design name** `cla_top` with the target module name.

## Synthesis plan (next round)

- **task_id**: `EDA-Eval-DesignFlow-CfgDefaultsResolve-001` (A-shard, pnr_signoff, L1)
- **prompt**: faithful scenario — user has a CXDP STA flow; their `CXDP_DESIGN_CFG` uses `$(CXDP_DESIGN_NAME)` which `read_cfg_var.py` cannot expand (crashes), `CXDP_PRE_SDC_NORM` defaults to `.out.sdc`, SCAN_SHIFT/CAPTURE empty; `CXDP_STA_CFG` hardcodes the golden design name. Ask: produce normalized `CXDP_DESIGN_CFG` + `CXDP_STA_CFG` for a **given target module name** applying the 5 rules; deliverable = `submit.zip` with the two normalized files.
- **hidden B**: different target module name (e.g. `new_mod_abc`) + a STA_CFG golden name different from `cla_top` (e.g. `cpu_core`) + a DESIGN_CFG template variant where `$(CXDP_DESIGN_NAME)` also appears in a 2nd SDC mode line. B must differ in value/structure, not just filename.
- **check() assertions (≥8, independent, each FAIL-able)** — target k≈12:
  1. zip contains exactly `CXDP_DESIGN_CFG` + `CXDP_STA_CFG`
  2. `CXDP_DESIGN_NAME = <target>` in DESIGN_CFG
  3. `CXDP_PRE_SDC_NORM = <target>.norm.sdc` (not `.out.sdc`, not `$(...)`)
  4. `CXDP_PRE_SDC_SCAN_SHIFT = <target>.scan_shift.sdc` (non-empty)
  5. `CXDP_PRE_SDC_SCAN_CAPTURE = <target>.scan_capture.sdc` (non-empty)
  6. no `$(CXDP_DESIGN_NAME)` / `$(DESIGN_NAME)` in any **effective** (non-comment) DESIGN_CFG line
  7. `CXDP_PRE_UPF_FILE` / `CXDP_POST_UPF_FILE` resolved to `<target>.upf`
  8. `CXDP_STA_NETLIST_LIST = <target>.netlist.f` in STA_CFG (golden name replaced)
  9. `CXDP_STA_PRE_SDC_NORM = <target>.norm.sdc` (golden name replaced, not the old golden name)
  10. no occurrence of the **old golden design name** in any effective STA_CFG line
  11. non-targeted keys unchanged (regression: e.g. `CXDP_STA_CORNER`, `CXDP_STA_TOOL_VERSION`, `CXDP_DESIGN_ROOT`, `CXDP_RTL_FILE_LIST` identical to input) — guards against over-replacement
  12. comment lines containing `$(CXDP_DESIGN_ROOT)` / `$(DESIGN_ROOT)` are **preserved** (not stripped) — guards against naive `replace all '$('`
  13. same design name used consistently across NORM/SCAN_SHIFT/SCAN_CAPTURE (no mix-up)
- **negatives (≥2 + 3 fake-submit)**: (a) empty-shell (zip with empty files) FAIL; (b) only-print-expected (echoes the rule text, no transform) FAIL; (c) delete-core (copies input unchanged) FAIL on assertions 3/4/5/6/8/9; (d) naive `sed s/$(CXDP_DESIGN_NAME)/<target>/g` without handling STA_CFG golden-name ⇒ FAIL on 8/9/10; (e) over-replace (strips comment `$()` too) ⇒ FAIL on 12.
- **randomization**: 3 seeds picking different target module names; transform must be deterministic given (input, target).
- **test_rationale**: `12 条断言：①zip 2 文件齐全 ②DESIGN_NAME=target ③PRE_SDC_NORM=target.norm.sdc ④SCAN_SHIFT=target.scan_shift.sdc ⑤SCAN_CAPTURE=target.scan_capture.sdc ⑥DESIGN_CFG 有效行无 $(CXDP_DESIGN_NAME) ⑦UPF 解析为 target.upf ⑧STA_NETLIST_LIST=target.netlist.f ⑨STA_PRE_SDC_NORM=target.norm.sdc ⑩STA_CFG 有效行无旧 golden 名 ⑪非目标 key 不变 ⑫注释行 $(...) 保留`

## DEBT

- **r1489 locate-DEBT**: ✅ RESOLVED r1490 (session file is at depth-2 subdir `1795488475556_n24xd/`, not depth-1).
- **synthesis DEBT (new, r1490)**: deep-read complete; full case synthesis (assets + hidden B + negative + check.py ≥8 + self-verify + pi + double-commit) deferred to next round — 40-min round budget insufficient for quality synthesis after locate+deepread. Next round: build `cases/A/EDA-Eval-DesignFlow-CfgDefaultsResolve-001.json` + `reference/` + `assets/` + `hidden/` + `negative/` per plan above; then `mark --session 1795488475556_n24xd.messages.json --status case --case-id …`.

## Appendix: full CXDP_DESIGN_CFG (6469 B, msg104)

See `CXDP_DESIGN_CFG.txt` extracted to .75 session workdir; re-extractable from session msg104 if needed. Effective (non-comment) lines enumerated above are sufficient for asset construction.

## Appendix: full CXDP_STA_CFG (3193 B, msg104)

Effective lines enumerated above (file ends at `CXDP_STA_MVTC_FILE =`). Sufficient for asset construction.
