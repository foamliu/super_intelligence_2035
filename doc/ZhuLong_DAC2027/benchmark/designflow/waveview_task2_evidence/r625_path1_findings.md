# r625 · WAVEVIEW task2 Tier 2a · path 1 decisive test findings

**Date**: 2026-11-16 09:0x (shard A r625)
**Test**: r624 "ready-to-run decisive test" — does removing `"images"` from `capabilities` in `models.json` make cline `read_file` on a PNG throw `"Current model does not support image input"` (tool error) instead of returning image bytes (→ gateway hard-error)?

## Setup (fully isolated, zero blast radius)

- cline invoked with `--config /nasdata/app.e0031982/.cache/cline-tier2a-test` (isolated config dir, **NOT** the shared `~/.cline`). Shared `~/.cline` verified untouched before & after (providers.json = 2B SFT `minicpm5-2b-sft-v39-final`; models.json `deepseek-v4-flash.capabilities` still includes `"images"`).
- Isolated providers.json: `openai-compatible` → `deepseek-v4-flash` @ `http://agi-gateway.cxmt.com/v1`, key `...c43c1f4a-...` (verified HTTP 200 on `/chat/completions` beforehand).
- Isolated models.json: `deepseek-v4-flash.capabilities = ["streaming","tools"]` — **`"images"` removed** (the test variable).
- Workspace: `assets/thresh_char_A.png` (β10 TempThreshChar-001 A asset). Prompt: "read assets/thresh_char_A.png, report peak voltage of v(temp)".
- `cline --config <isolated> -c <ws> -P openai-compatible -m deepseek-v4-flash -k <key> --auto-approve true --json --thinking low "<prompt>"`, timeout 90s.

## Result (definitive)

- **cline exit=1**, `finishReason=error`, `recoverable:false`, duration 1164ms, 2 iterations.
- Session event [13]: model called `read_files` on `thresh_char_A.png`.
- Session event [15]: `read_files` **returned image bytes** —
  `output:[{"type":"text","text":"Successfully read image"},{"type":"image","data":"iVBORw0KGgo..."}]`.
  ⇒ `modelSupportsImages` was **true** despite `"images"` removed from isolated `models.json.capabilities`.
- Session event [19]: cline sent image content to gateway in next LLM call →
  `Error: deepseek-v4-flash is not a multimodal model` (hard error).
- stderr: `{"type":"error","message":"deepseek-v4-flash is not a multimodal model"}`.

## Conclusion

**Path 1 (capabilities toggle via `--config models.json`) is INFEASIBLE.** cline's bundled
catalog / knownModels merge **overrides** the user-provided `capabilities` array for known model
IDs like `deepseek-v4-flash`. Removing `"images"` there has **no effect** on `modelSupportsImages`
(`c?.capabilities?.includes("images") ?? true` resolves to true via the bundled entry).

Therefore the baseline arm failure mode **cannot** be improved to "read_file tool error → model
gives up" via the capabilities toggle. It stays **hard-gateway-reject** (read_file returns bytes →
gateway "not a multimodal model" → exit=1).

Note on `?? true` default: an *unknown* custom model ID (no bundled catalog entry) with no
user-provided capabilities would also default to `modelSupportsImages=true` → same gateway error.
So a custom-ID variant of path 1 does not help either. (A custom ID with explicit
`capabilities=["streaming","tools"]` AND no bundled override is a narrow untested refinement, but
the gateway must still route the custom ID — uncertain, not pursued this round.)

## Implication for vision's decision (sharpened)

vision must now choose between:
- **(A) Accept hard-gateway-reject baseline failure mode** — verdict FAIL correct, failure mode =
  hard error on image read (not graceful engaged-but-image-blind). Fastest; no further infra work.
- **(B) Pivot to path 2** — PNG moved OUT of cline workspace + absolute path fed to `vqa` tool
  (model told "image at /abs/path, use vqa tool"; read_file never touches PNG). Cleanest design:
  baseline (VQA_MCP=0) = engaged-but-image-blind FAIL; +VQA = model uses vqa → PASS. Requires
  (b1) qwen35_vqa SSH bridge can read eval-machine abs path, (b2) prompt restructure with vision
  confirmation that check.py unchanged (口径约束 4).
- **(C) Path 3** — switch to a text-only endpoint that silently accepts multimodal content (e.g.
  local vLLM deployment), avoiding the gateway strict check. Needs GPU / deployment.

## Evidence

- `r625_path1_decisive_test_session.jsonl` (21 events, 94KB) — full cline session.
- `r625_path1_decisive_test_stderr.log` — stderr incl. the multimodal hard-error line.
