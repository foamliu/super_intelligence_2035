# Deepread — q1dv2 (ziyuny @ hfeg0pnd001, mc=147, physical_verify)

**session**: `1794969260918_q1dv2/1794969260918_q1dv2.messages.json` (475KB, 102 msgs, 8 real user text turns)
**host**: 10.129.32.189 (hfeg0pnd001) — same host as 7rzyf (ziyuny, built LvsSeedPromoDetect) + pvl8c (steveny, built EdaAgentSkillRouteRewrite)
**domain**: physical_verify (DRC + calibre dominant; drc:899 + calibre:695 + lvs:38)
**fresh**: NOT in any of 4 shard ledgers prior to claim (in_ledger=0 across A/B/C/D) → genuine fresh unbuilt high-mc C-dominant candidate from 11-19 scan.

## User turns (verbatim)
- U#0 / U#9: `运行/home/ziyuny/zl/wl_adjcent/test.sh`
- U#23: `好的`
- U#33: `运行/home/ziyuny/zl/wl_adjcent/rundrc.sh`  ← DRC submission
- U#37 / U#40: `这个job已经exit了，排查一下是什么原因呢？`  ← **core produce-task (diagnosis)**
- U#74: `注意 这里的drc python 代码等文件，跑得shell命令和脚本中，都要写全路径，这一点将来要计入skill中去`  ← skill/note
- U#100: `现在回顾一下前情，整个flow，我们梳理到哪里了？`  ← review

## Real task & gold (assistant chain on U#37→U#73)
ziyuny submitted a Calibre DRC job via `rundrc.sh`:
```
bsub -q pv -env "USE_CALIBRE_VCO=aoi" -o drc.log /apps/mentor/calibre/2020.1_36/aoi_cal_2020.1_36.18/bin/calibre -hier -drc wl_adjacent.drc
```
Job exited. Assistant diagnosed:
1. `bhist -l 3063498` → **exit code 4**, **Execution CWD `</home/ziyuny>`** (NOT the project dir `/home/ziyuny/zl/wl_adjcent`).
2. Because `-o drc.log` is a **relative** path, the log was written to `/home/ziyuny/drc.log` (followed the wrong CWD).
3. `drc.log` shows: `--- RULE FILE = wl_adjacent.drc` + `ERROR: Error OPEN1 - problem with access, file type, or file open of file: wl_adjacent.drc` → Calibre could not find the rule file because CWD was the home dir, not the project dir.
4. **Root cause**: `rundrc.sh` did NOT `cd` to the project dir before `bsub`, so the LSF job inherited CWD=`/home/ziyuny`; the relative rule-file path `wl_adjacent.drc` failed to resolve → OPEN1.
5. **Fix**: edit `rundrc.sh` to `cd /home/ziyuny/zl/wl_adjcent` before bsub + use full paths. Re-submitted job 3064887 → succeeded.
6. U#74: user generalises — "all DRC python code / shell commands / scripts must use full paths, record this into skill."

## Reframe (档 B) — `EDA-Eval-DesignFlow-DrcJobExitCwdDiag-001`
A-档 gold = assistant's free-text root-cause diagnosis prose (depends on live LSF/Calibre env, not reproducible, no ≥8 independent hard-assertion teeth) → reframe to offline pure-stdlib **DRC job exit root-cause diagnosis script** `drc_job_exit_diag.py <rundrc_sh> <bhist_log> <drc_log> <project_listing> [-o out.json]`:
- parse rundrc.sh: `cd` detection (cwd_set), `-o` path type (relative/absolute), calibre binary, `-drc` rule file path type
- parse bhist: job_id, exit_code, Execution CWD
- parse drc.log: RULE FILE, ERROR lines → error_type (open1_file / license / timeout / other)
- parse project listing: project_dir, rule_file_present
- derive cwd_correct (job_cwd == project_dir)
- classify root_cause priority: license_failure > cwd_mismatch > rule_file_missing > timeout > unknown
- output 17-key structured JSON (job_id/exit_code/job_cwd/project_dir/cwd_correct/cwd_set/output_path/output_path_type/rule_file/rule_path_type/rule_file_present/error_type/error_msg/root_cause/severity/recommended_fix/diagnosis_summary)

**Visible A** (faithful to trace): no cd + relative `-o drc.log` + relative rule `wl_adjacent.drc` + exit 4 + CWD=`/home/ziyuny` (wrong) + OPEN1 + rule file present → root_cause=**cwd_mismatch**, fix=cd+full paths.
**Hidden B** (fully inverted, license_failure): `cd /home/ziyuny/zl/wl_test2` + absolute `-o` + absolute rule + exit 255 + CWD=project dir (correct) + license/checkout/flexlm ERROR + rule present → root_cause=**license_failure**, fix=license server/LM_LICENSE_FILE/admin.

7 axes differ (cwd_set / output_path_type / rule_path_type / exit_code / cwd_correct / error_type / root_cause) — prevents hardcoding A.

## Distinct from existing C cases
- DrcCwdRaceEvidence-001 (xinqiaoz): CWD **race** between parallel calibre runs (os.chdir process-global) — different CWD failure mode (race, not submission-dir).
- DrcRunStatusAnalyze-001 (ziyuny, ics15): **status report** from 13MB log (progress %, violations) — not root-cause diagnosis of a job exit.
- DrcQaRunDiag-001 / BridgeConnDiag-001 / PexGxrcDiag-001 / AlpsOutMissingDiag / ErcReconLicDiag / LVSDiag: all different sub-types.
→ This case = **LSF-submitted Calibre DRC job exit (code 4) root-cause diagnosis — CWD-mismatch vs license-failure differential**. New sub-type (drc-job-exit-cwd-diagnosis).
