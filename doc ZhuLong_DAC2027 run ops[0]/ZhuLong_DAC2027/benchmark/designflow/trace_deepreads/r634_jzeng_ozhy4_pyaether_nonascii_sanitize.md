# r634 deepread: ozhy4 — pyAether non-ASCII sanitize (jzeng@hfeg0pkn003 mc39)

**session**: 1794642749970_ozhy4 @ 10.129.2.12 (hfeg0pkn003)
**user**: jzeng | **mc**: 39 | **domain**: layout_aether (pyAether script fix)
**trace**: 33 msgs / 3 real user turns / via .75 ssh cat subdir `<sid>/<sid>.messages.json`

## User intent (verbatim)

- **USER#0**: Pasted pyAether traceback:
  ```
  File "/apps/empyrean/.../pyAether/pydef/ae_load_utils.py", line 59, in load
      exec(fh.read() + "\n", cur_frame_gv)
  UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 73034: ordinal not in range(128)
  ```
- **USER#8**: "帮我修复这个错误" (Help me fix this error)
- **USER#22**: Pasted NEW traceback (position 69699 — file regenerated with new non-ASCII) + "解决这个问题" (Solve this problem)

## What happened

1. Agent loaded aether-tool-qa skill, read FAQ docs
2. Listed `/ai_sandbox/drcpa/V0/agentdir/jzeng` → found `find_non_ascii.py`
3. Ran `find_non_ascii.py` → located non-ASCII bytes in `/home/jzeng/Desktop/IMCleAutoVia.py`
4. Read IMCleAutoVia.py around non-ASCII lines; used editor to replace:
   - `→` (U+2192, 0xE2 0x86 0x92) → `->` (ASCII arrow)
   - `上下走向` (Chinese "vertical direction") → removed (kept "vertical")
5. USER#22: file was regenerated with NEW non-ASCII at different positions → agent re-ran find_non_ascii, found `→` at pos 69699 + `上下走向` at lines 1245, 1707 → fixed all 3
6. **ASST#32 final**: file 106061→106030 bytes, 0 non-ASCII, all UTF-8 replaced with ASCII equivalents. File now loads via `ae_load_utils.load()` without UnicodeDecodeError.

## Root cause

pyAether's `ae_load_utils.load()` does `exec(fh.read())` in Python 3.9 with ASCII encoding. The .py file (`IMCleAutoVia.py`, ~106KB pyAether auto-via layout generation script) contained:
- `→` (U+2192) UTF-8 arrows in comments (3-byte: 0xE2 0x86 0x92)
- `上下走向` Chinese comments (3-byte per char: 0xE4 0xB8 0x8A...)

These trigger `UnicodeDecodeError` because the file is opened in ASCII mode.

## Gold (real artifact → fix)

The agent's fix = byte-level non-ASCII detection + targeted replacement:
- `→` → `->` (semantic-preserving)
- Chinese `上下走向` → removed (kept English "vertical")
- Result: ASCII-only file, valid Python, loads without error

## Case reframe (B档 mock-behavioral)

Real `IMCleAutoVia.py` (106KB) and `find_non_ascii.py` are not retrievable (file regenerated post-session, sandbox cleaned). **Synthesize** a realistic pyAether layout script excerpt with non-ASCII (arrows + Chinese comments) as asset.

**Deliverable**: `sanitize_nonascii.py <input.py> <output.py> <report.json>`
- Scan input.py for non-ASCII bytes (byte position, line number, hex, decoded char, context)
- Replace each with ASCII equivalent per mapping: `→`→`->`, `×`→`*`, `°`→`deg`, `–`→`-`, `±`→+/-`, Chinese→removed
- Write clean output.py (ASCII-only, py_compile valid)
- Write report.json {file, original_size, output_size, nonascii_count, replacements[], line_count_preserved}

**Asset A**: `script_a.py` — pyAether layout excerpt ~130 lines with `→` arrows + `上下走向` Chinese (~10 non-ASCII byte positions)
**Hidden B**: `script_b.py` — different pyAether excerpt with `×`, `°`, `水平方向` Chinese (different positions/lines)
**Hidden B2**: `script_b2.py` — variant with `–`, `±`, `阈值` Chinese (anti-hardcode)

## Why this is a good case

- **Real user intent**: fix a concrete load error (UnicodeDecodeError) — not contrived
- **Artifact-grounded**: the .py file is the artifact, output is verifiable (ASCII-only + valid Python + loads)
- **Check has teeth**: anti-hardcode (B/B2 different non-ASCII), determinism, no-false-positives, structure preservation
- **Domain**: layout_aether (pyAether script), C-shard legitimate
