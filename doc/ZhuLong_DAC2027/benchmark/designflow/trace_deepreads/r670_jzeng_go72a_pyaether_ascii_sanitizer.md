# Deepread: jzeng go72a — PyaetherAsciiSanitizer (layout_aether)

**Session**: 1794641637039_go72a.messages.json
**User**: jzeng @ 10.129.2.12 (hfeg0plg22)
**Match count**: 24 (keywords: drc:136; .gds:66; pyaether:39; aether:26; netlist:10; calibre:8)
**Domain**: layout_aether (pyAether auto-via script encoding fix)
**Date**: 2026-11-16 r670

## Trace flow (38 msgs, 4 user turns)

### U#1 (msg#0): SyntaxError — ae.load() without quotes
User pastes a traceback: `ae.load(/home/jzeng/Desktop/IMCleAutoVia.py)` → `SyntaxError: invalid syntax`. The file path is not quoted.
**Assistant** (msg#1): Explains the path needs quotes: `ae.load("/home/jzeng/Desktop/IMCleAutoVia.py")`.

### U#2 (msg#2): UnicodeDecodeError — ascii codec can't decode byte 0xe2
After adding quotes, user gets: `UnicodeDecodeError: 'ascii' codec can't decode byte 0xe2 in position 69390: ordinal not in range(128)`. The error is in `ae_load_utils.py:59` where `exec(fh.read() + "\n", cur_frame_gv)` reads the file with ASCII encoding.
**Assistant** (msg#3): Diagnoses non-ASCII chars in the file. Suggests `# -*- coding: utf-8 -*-` header (Method 1) or removing non-ASCII chars (Method 2).

### U#3 (msg#4): "帮我修改/home/jzeng/Desktop/IMCleAutoVia.py，解决这个错误"
**Core produce-task**: Fix the file to resolve the UnicodeDecodeError.
**Assistant** (msg#5-19):
1. Reads the file (1847 lines, 101930 bytes)
2. Adds `# -*- coding: utf-8 -*-` at line 1 (editor insert)
3. Verifies first 10 lines

### U#4 (msg#20): Same UnicodeDecodeError persists (position 69390)
The `# -*- coding: utf-8 -*-` declaration doesn't help because `ae.load()` opens the file with ASCII encoding internally (`fh.read()` uses ASCII), not the Python interpreter's encoding.
**Assistant** (msg#21-37):
1. Realizes the encoding declaration is ineffective for `ae.load()`
2. Writes `find_non_ascii.py` helper script at `/ai_sandbox/drcpa/V0/agentdir/jzeng/find_non_ascii.py`
3. Runs it via `python-runner` profile → finds em dash `—` (U+2014, UTF-8 0xe2 0x80 0x94) at byte offset 69390, line 1240
4. Context: `# botEncX/botEncY default to 0 — no layer1 override, technology default applies.`
5. Edits line 1240: replaces `—` (em dash) with `--` (two hyphens)
6. Re-runs `find_non_ascii.py` → 0 non-ASCII bytes remaining (file is now pure ASCII, 101929 bytes)
7. User implicitly accepts (no further messages)

## Gold deliverable
The fixed IMCleAutoVia.py with all non-ASCII characters replaced with ASCII equivalents. The actual fix was replacing one em dash `—` → `--` on line 1240. The `# -*- coding: utf-8 -*-` header added by the assistant is harmless but unnecessary.

## File structure (IMCleAutoVia.py, 2149 lines after fix)
- Lines 1-15: imports (os, re, time, traceback, pyAether, PyQt5)
- Lines 17-30: header comments (IMCleAutoVia.il, Author: Leozhao, revision history)
- Lines 261-440: class IMCleAutoViaFormDef (UI form definition)
- Lines 441-1142: class IMCleAutoViaFlow (QWidget, GUI + flow logic)
  - IMCleGenV4Pads (line 995): generate M4/M5 pads at intersections
  - IMCleAutoViaGUICB (line 556): main GUI callback
- Lines 1143-1592: standalone functions
  - IMCleAutoVia_MarkChk (line 1143): mark-layer label check
  - IMCleGetRectProp (line 1161): rectangle properties (the function with the em dash comment at line 1421)
  - IMCleCrtViaAndSetDefOverrideEx (line 1445): create via with enclosure overrides
- Lines 1593-1779: IMCleAutoVia (main entry point)
- Lines 1783-2149: gen_via_from_y, utility functions, GUI launcher

## B-dang reframe
Reframe as pure stdlib `pyaether_ascii_sanitizer.py`:
- Read Python script (UTF-8) → find non-ASCII chars → replace per table (em dash→--, curly quotes→straight, arrow→->, etc.) → write pure ASCII output
- The output must be: pure ASCII (0 bytes > 127), valid Python (py_compile passes), AST structure preserved (same imports/defs/classes)
- Hidden B (ViaEnclosureChecker.py): different structure, different non-ASCII chars (Chinese, curly quotes, arrows, ellipsis, copyright), reversed functional content
- Hidden B2: minimal 5-line script with 1 em dash

## Why this is C-domain (layout_aether)
- IMCleAutoVia.py = "IM Cle Auto Via" = automatic via generation for aether layout
- Depends on pyAether (ae.load, aeCreateVia, aeSetViaEnclosure, aeGetCurDesign)
- Contains DRC enclosure rules, via generation logic, layout cell manipulation
- Keywords: pyaether:39 (real), drc:136/.gds:66 (path-substring from DRC/enclosure code in the script)
- The task (fix encoding so the layout script can load) is directly in the layout_aether workflow

## Sub-type distinction
Distinct from r667 RoutingTrackFinder (routing track channel finder) and r665 AntennaQaPatternReuse (calibre deck diff): this is `pyaether-ascii-sanitizer` (encoding fix for pyAether scripts), a debug-fix produce-task.
