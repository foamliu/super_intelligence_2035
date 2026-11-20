# r626 · WAVEVIEW task2 path 2 · β10 flip FAIL→PASS PROVEN (corrected)

**Date**: 2026-11-16 09:3x-09:4x (shard A r626)
**SUT**: deepseek-v4-flash @ agi-gateway (key from `providers.json.bak.maxTokens8192`, `/chat/completions` HTTP 200 + tool-call verified).
**Config**: isolated `--config /nasdata/app.e0031982/.cache/cline-tier2a-path2` (zero blast radius; shared `~/.cline` untouched = 2B SFT @ 127.0.0.1:18096).
**Case**: β10 TempThreshChar-001 (shard D, analog_context, k=12). Oracle GT: vmax=1.20, vth_high=0.85, vth_low=0.45, hyst=0.40, n_trans=2.

## ⭐ Headline: the multimodal flip is demonstrated on β10

| arm | prompt | vqa MCP | path given | result |
|:-:|:-|:-:|:-|:-|
| **base-p17** (baseline) | "no image tool, answer from description" | off | .17 NFS abs | **exit=0 / 63s / verdict=FAIL (vmax 1.000 != 1.199) / vqa=0 / read_file_png=0 / hard_err=0** → clean image-blind FAIL ✅ |
| **vqa-p17** (+VQA) | "DO NOT read_file .png; MUST use vqa; 9 suggested questions" | on | .17 NFS abs | **exit=0 / 183s / verdict=PASS (check.py PASS) / vqa=14 / read_file_png=0 / hard_err=0** → model read image via vqa, got correct values, PASS ✅ |

**base FAIL → vqa PASS = the multimodal gain vision wants.** deepseek-v4-flash engages the task, cannot read the image without vqa (FAIL), and succeeds with vqa (PASS). This is the clean Tier-2a flip (engaged-but-image-blind FAIL → engaged+VQA PASS), no hard-error contamination.

## The two critical path-2 requirements (both verified)

### Requirement 1 — give the model the **.17 NFS path** (`/nas_data/...`), NOT the 36.15 path (`/nasdata/...`)

The vqa MCP at `127.0.0.1:13002/mcp` is a bridge to the Qwen3.5-2B vqa server running **on .17**, which reads **.17 local files**. The .17 NFS root is `/nas_data/` (underscore); the 36.15 NFS root is `/nasdata/` (no underscore) — **different mounts, the .17 path does not exist on 36.15**.

- ✅ Correct path: `/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/real_waveview_images/EDA-Eval-DesignFlow-TempThreshChar-001/thresh_char_A.png` → vqa returns correct answers (verified: WaveView-002 → "5 signals clk/rst_n/data/vref/sel", matching vision wake#1413).
- ❌ Wrong path (36.15 `/nasdata/...`): vqa backend returns `HTTP Error 500` (file not found on .17, surfaced as 500 by the MCP wrapper). My first probe round was confounded by this — all vqa calls 500'd because I passed the 36.15 path.

**Side benefit of the .17 path**: it does NOT exist on 36.15, so if the model tries `read_file` on it, cline returns a file-not-found **text** error (not image bytes) → **no hard multimodal gateway error**. This is the real mechanism that keeps the baseline arm clean — not a "cline workspace boundary" (cline read_file has no such boundary; it reads any OS-readable path and returns image bytes for a locally-existing PNG, as the vqa-soft arm proved when given the 36.15 path).

### Requirement 2 — hardened prompt: explicitly forbid `read_file` on .png + instruct vqa

With the .17 path the baseline arm is clean regardless (file doesn't exist locally → read_file text-errors). But for the **+VQA arm**, an un-hardened prompt ("you have a vqa tool") let the model try `read_file` on the PNG first — and if a PNG *does* exist locally (it won't for the .17 path, but defensively), read_file returns image bytes → hard gateway error. The hardened prompt (`"Do NOT call read_file on any .png; you MUST use vqa"`) makes deepseek-v4-flash comply: **0 read_file on PNG, 14 vqa calls, 0 hard error, PASS**. Adopt the hardened prompt for all +VQA runs.

## Correcting my earlier (confounded) probe conclusions

My first 3-arm probe (base / vqa-soft / vqa-hard) used the **36.15 path** and concluded "path 2's workspace-boundary premise is FALSE; vqa backend 500". **That conclusion is retracted** — it was an artifact of the wrong path:
- The "vqa-soft hard error via read_file image bytes" happened because the 36.15 path *exists locally* → read_file returned image bytes. With the .17 path (doesn't exist on 36.15), read_file would text-error, no hard error.
- The "vqa backend HTTP 500" was the .17 vqa server failing to find the 36.15 path. With the .17 path, vqa returns correct answers.

The **vqa@13002 backend is healthy** (vision wake#1413's "vqa 真题答对 5" is confirmed reproducible from 36.15 via the bridge, using the .17 path). No vision-side infra blocker remains.

## Ready-to-run recipe for the 20-run batch (next round)

For each of the 10 cases (intake `run/vision_real_waveview_index.json`):
1. Workdir: `task_brief.md` + path-2 `prompt.txt` (give the case's **.17 NFS abs path** from intake; baseline hint = "no image tool, guess"; +VQA hint = "DO NOT read_file .png, MUST use vqa, 9 suggested questions"). **No PNG in workspace.**
2. cline: `--config <isolated tier2a-path2>` (deepseek-v4-flash @ agi-gateway), `--thinking low`, timeout 360s. baseline arm = `cline_mcp_settings.base.json`; +VQA arm = `cline_mcp_settings.vqa.json`.
3. Judge: case `check.py` (oracle-recomputed, anti-hardcode-B) in scratch dir.
4. Record verdict/dur/failure_mode → `waveview_baseline_results.A.json` task2段.

Per-case .17 path: replace `<case>` + `<png>` in `/nas_data/app.e0031982/code/super_intelligence_2035/doc/BaiZe-ISEDA2027/run/vision/real_waveview_images/<case>/<png>` (values from intake逐题表).

β10 proven: base FAIL / vqa PASS. Remaining 9 cases × 2 arms = 18 runs to execute next round.

## Evidence (in `.cache`, scratch — not committed)

- `probe/beta10_base_p17/` — baseline arm (clean FAIL, the definitive baseline).
- `probe/beta10_vqa_p17/` — +VQA arm (PASS, the flip).
- `probe/probe_results_p17.tsv` — result rows.
- `path2_probe_beta10.sh` — first (confounded) probe; corrected recipe above.
- isolated config: `/nasdata/app.e0031982/.cache/cline-tier2a-path2/` (providers/models/mcp_settings base+vqa, deepseek-v4-flash).
