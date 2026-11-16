# r627 · WAVEVIEW task2 path 2 · 9-case batch — honest negative findings + recipe regression identified

**Date**: 2026-11-16 10:0x-10:3x (shard A r627)
**SUT**: deepseek-v4-flash @ agi-gateway (SUT 变更声明: deepseek-v4-pro→flash, 口径约束 3).
**Config**: isolated `--config` (cfg_base / cfg_vqa separate dirs, zero blast radius; shared `~/.cline` untouched).
**Cases**: 9 remaining (alpha1/β9/α4/β8/β11/α3/β6/α2/β7) × 2 arms = 18 runs. β10 already proven r626.
**Results**: `designflow/waveview_baseline_results.A.json` → `task2_r627`.

## ⭐ Headline: this batch does NOT measure multimodal gain — but produced 3 actionable findings

**vqa engagement = 0/8 vqa arms.** The model skipped vqa entirely on every vqa arm and guessed → the vqa arm data is not a real vqa measurement. **0 FAIL→PASS flips** is therefore not evidence of "no multimodal gain"; it's an artifact of the vqa arm not using vqa.

Root cause identified (recipe regression vs r626): **permissive prompt**. r626 (β10, real flip) used the directive "你**必须**用 vqa 工具读图" + 9 specific questions → 14 vqa calls. r627 used the permissive "你**可以**...可以多次调用" → the model opted to guess instead. **Directive prompt is the correct recipe** (now fixed in `run_batch_r627.py` for next round's rerun).

## Finding 1 — recipe regression (permissive vs directive prompt) [FIXED for next round]

| | r626 β10 (real flip) | r627 batch (no measurement) |
|:-:|:-|:-|
| prompt | "你**必须**用 vqa...建议依次问 ①…②…⑨" | "你**可以**...可以多次调用" |
| vqa calls | 14 | **0** (all 8 vqa arms) |
| flip | FAIL→PASS ✅ | n/a (vqa arm didn't use vqa) |

**Fix**: `run_batch_r627.py` vqa hint rewritten to directive ("你**必须**用 vqa...**必须**依次调用 vqa 问出每个所需数值"). Verified the directive phrasing matches r626's working β10 prompt. Next round reruns vqa arms with the fixed prompt.

## Finding 2 — baseline difficulty: 5/8 valid base arms PASS while image-blind (ceiling effect)

Valid base arms (image-blind, 0 vqa): **5 PASS / 2 FAIL / 1 missing (ERROR)**. The 5 blind-PASS cases **cannot show a FAIL→PASS flip** (ceiling effect — baseline already passes without vision):

| case | base verdict | base vqa | blind-pass mechanism |
|:-|:-:|:-:|:-|
| TempSelWaveform-001 | PASS | 0 | educated guess within check.py tolerance |
| DqReadPathWaveDebug-001 | PASS | 0 | educated guess within tolerance |
| WaveCmpWrap-001 | PASS | 0 | educated guess within tolerance |
| **RiseEdgeMarginMeas-001** | PASS | 0 | **task_brief leaks oracle** (see Finding 3) |
| FsdbWrDqMeas-001 | PASS | 0 | educated guess within tolerance |
| WaveView-002 | FAIL | 0 | timeout 360s (no submit) — genuinely hard blind |
| SimFailFsdbProbe-001 | FAIL | 0 | no submit — genuinely hard blind |

**Implication for vision**: only the 2 (–3 with EyeApertureSelect, which ERRORed) genuinely-hard-blind cases can show a real flip. The 5 blind-pass cases need either tighter check.py tolerance (to make blind guessing fail) or are simply not vision-discriminative at this SUT level. **vision may want to recalibrate baseline difficulty** (tighten tolerances or pick cases where blind guessing genuinely fails).

## Finding 3 — alpha2 (RiseEdgeMarginMeas-001) task_brief leaks the oracle

`assets/EDA-Eval-DesignFlow-RiseEdgeMarginMeas-001/task_brief.md` lines 28-36 contain the **exact A-oracle values** in its JSON schema example:
```json
{ "ref_edge_time": 5.17, "target_edge_time": 7.37, "margin_ns": 2.20, ... }
```
A blind model copies them verbatim → check.py (TOL_EDGE=0.40ns) accepts → PASS with no image. **This case has no vision dependency by construction.**

**Fix for vision**: replace the concrete numbers in the task_brief example with placeholders (`<float: ...>`), matching β10's placeholder style. check.py / hidden-B / oracle unchanged (口径约束 4 satisfied). Flag for vision to approve/apply (designflow discipline: don't modify check.py/assets without vision sign-off on task_brief content).

## Finding 4 — script bug: NFS rmtree race (3 ERROR runs) [FIXED]

3 runs (EyeApertureSelect base+vqa, WaveMaxFind base) ERRORed with `[Errno 39] Directory not empty` from `shutil.rmtree` on NFS. **Fixed**: added 3-retry loop with 1s sleep in `build_workspace()`. These 3 runs did NOT execute cline (no data); next round's rerun will cover them.

## Per-case result table (valid runs only)

| case | base | vqa | vqa arm engaged? | flip | note |
|:-|:-:|:-:|:-:|:-:|:-|
| EyeApertureSelect-001 | ERROR | ERROR | — | incomplete | rmtree race; rerun |
| WaveMaxFind-001 | ERROR | PASS | NO (0 vqa) | incomplete | base rmtree race; vqa guessed |
| TempSelWaveform-001 | PASS | PASS | NO (0 vqa) | both PASS | blind-pass (ceiling) |
| WaveView-002 | FAIL | FAIL | NO (0 vqa) | both FAIL | timeout both arms; genuinely hard |
| SimFailFsdbProbe-001 | FAIL | FAIL | NO (0 vqa) | both FAIL | no submit both; genuinely hard |
| DqReadPathWaveDebug-001 | PASS | FAIL | NO (0 vqa) | PASS→FAIL | vqa arm timeout; base blind-pass |
| WaveCmpWrap-001 | PASS | PASS | NO (0 vqa) | both PASS | blind-pass (ceiling) |
| RiseEdgeMarginMeas-001 | PASS | FAIL | NO (0 vqa) | PASS→FAIL | **task_brief leaks oracle** (Finding 3) |
| FsdbWrDqMeas-001 | PASS | PASS | NO (0 vqa) | both PASS | blind-pass (ceiling) |

## Next round plan (r628)

1. **Rerun vqa arms with directive prompt** (now fixed) on all 9 cases — get real vqa-engagement data.
2. **Rerun the 3 ERROR runs** (EyeApertureSelect base+vqa, WaveMaxFind base) with rmtree-retry fix.
3. **Escalate to vision**: (a) alpha2 task_brief oracle-leak fix (Finding 3); (b) baseline-difficulty recalibration for the 5 blind-pass cases (Finding 2) — tighten tolerance or accept they're not vision-discriminative at this SUT level.
4. β10 (r626) remains the one proven flip. The 9-case batch's real value is the recipe + difficulty findings above, which unblock a clean rerun.

## Evidence

- `waveview_baseline_results.A.json` → `task2_r627` (18 runs, corrected summary with ERROR accounting + vqa-engagement flag).
- `run_batch_r627.py` (directive prompt + rmtree-retry fixes applied for next round).
- session logs / outputs in `.cache/cline-tier2a-path2/probe_r627/` (scratch, not committed).
