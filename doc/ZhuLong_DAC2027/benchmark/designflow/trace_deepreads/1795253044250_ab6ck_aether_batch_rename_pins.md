# Deepread — 1795253044250_ab6ck (joeyli / hfeg0pkn004)

- session: `1795253044250_ab6ck`  user: `joeyli` (E0034352 LiJoey, PDC/DE-DDR/Layout-DT)
- host: `hfeg0pkn004` (10.129.2.13)  model: `deepseek-v4-flash` (cxmt-deepseek-flash)
- cwd: `/ai_sandbox/drvqa/V0/agentdir/joeyli`  scene: `aether assistant` engine=aether
- mc=301  keywords: aether:917; schematic:508; pyaether:364; dbget:92; cellview:86; netlist:35; mixed-signal:15; floorplan:12
- 274 msgs (153 user / 121 assistant), 4 real user inputs, inputTok 18M / outTok 127K
- domain: layout_aether (schematic pin/term rename via pyAether)  → shard C

## Real task (user prompts, verbatim)
1. `帮我写一个ather脚本 py3版本：对于前缀一致到一组pin 可以实现批量累加前缀后缀不变 例如s01xx-s08xx 变为s09xx-s16xx`
2. `帮我把它设置为快捷键 F`
3. `帮我把它设置为快捷键 F7`
4. `我希望你直接提供一个脚本 load 后我打开layout 按F7实现功能`

## Task essence
Write a **pyAether (Python 3) script** that batch-renames a group of schematic **terminals (pins)** whose names share a prefix+suffix, by **incrementing the numeric part of the prefix** while keeping the suffix unchanged. Example: `s01xx … s08xx` → `s09xx … s16xx` (delta=+8, num_digits=2, suffix `xx` preserved). Then **bind the function to the F7 hotkey** so that after `load`-ing the script and opening a layout/schematic, pressing F7 runs the rename.

## Agent workflow (what it actually did)
- ~30 `RAG_MCP_Server__search_apis` + `get_api_details` calls researching pin/term APIs:
  `emyFigGroupGetAllPinNets`, `emyFigGetPinName`, `emyTermGetPinFigs`, `emyPinGetTermName`,
  `emyTermGetBaseNameString`, `emyTermSetNewName`, `emyTerm`, `emyBlock`, `emyDesign`,
  `aeGetCurDesign`, `emyCdbaNS`, `emyString`, `emyName`, `aeSaveDesign`, `aeCheckAndSaveDesign`.
- 3 `SandBox_MCP_Server__run_code` (pyAether) attempts → all failed with **"Connection refused"** (sandbox unreachable). API existence confirmed only via RAG, never executed.
- Wrote `batch_rename_pins.py` via `editor` tool — but `editor`'s `new_text`/`insert_line` **kept appending duplicate copies**, corrupting the file (≥3 full copies, ~900 lines). Spent ~30 turns trying to clean it (rm, cp /dev/null, editor old_text replace) — never fully succeeded. Final deliverable given **inline in chat text** instead.
- For F7 binding: read Aether skill refs (`part_XI_Script.md`, `part_XIV_Appendix.md`, `快捷键速查.md`) for `aeSetBindKey` / `proc.menu` / `aether_v2.key` / `aether_interface.xml`. Proposed a **Tcl bridge** (`batch_rename_pins.tcl` with `proc batchRenamePins` calling embedded `python {…}`) + `aether_interface.xml` registering an Interface bound to F7 via Options→Settings→Shortcut.

## Final deliverable (the working code the agent produced)
`batch_rename_pins.py` core:
```python
import re, pyAether as pa
def build_pattern(prefix, num_digits, suffix):
    return re.compile('^'+re.escape(prefix)+r'(\d{'+str(num_digits)+r'})'+re.escape(suffix)+r'$')
def batch_increment_terms(design, ns, prefix, delta, suffix='', num_digits=2):
    pattern = build_pattern(prefix, num_digits, suffix)
    terms = design.terminals
    matched = [(t, get_term_name(t,ns), int(m.group(1))) for t in terms if (m:=pattern.match(get_term_name(t,ns)))]
    for term, old_name, old_num in matched:
        new_num = old_num + delta
        if new_num < 0: skip
        new_name = f'{prefix}{str(new_num).zfill(num_digits)}{suffix}'
        pa.emyTermSetNewName(ns, term, pa.emyString(new_name), pa.emyString())  # rename
    pa.aeCheckAndSaveDesign()  # save
def run(prefix='s', delta=8, suffix='', num_digits=2, do_save=True):
    design = pa.aeGetCurDesign(); ns = pa.emyCdbaNS()
    batch_increment_terms(design, ns, prefix, delta, suffix, num_digits)
```
F7 binding: `~/.empyrean/batch_rename_pins.tcl` (proc batchRenamePins → `python { import batch_rename_pins as brp; brp.run(...) }`) + `aether_interface.xml` (<Interface><name>Batch Rename Pins</name><viewtype>schematic</viewtype><program>tcl</program>…) bound to F7.

## Confirmed-real pyAether APIs (verified via get_api_details on aether host)
- `aeGetCurDesign() -> emyDesign` — current cellview
- `emyCdbaNS()` — CDBA namespace
- `emyTermGetBaseNameString(pTerm, ns, basename)` — get term base name into emyString
- `emyTermSetNewName(ns, oldTerm, netName, msg) -> emyTerm` — rename term; returns emyTerm on success, NULL on fail
- `aeCheckAndSaveDesign()` / `aeSaveDesign() -> bool` / `emyDesignSave(pDesign, msg=None) -> emyBoolean`
- `emyString()`, `emyName`, `emyTerm`, `emyBlock` — all real

## Trace weaknesses / bugs (exploitable for discriminating negatives)
1. `_emy_str_to_python` uses `emy_str.replace('', '')` — **nonsensical** (no-op); real conversion needs `str(emy_str)` or `.getLength()`+buffer read. Never validated (sandbox down).
2. `design.terminals` property access — never confirmed; alternative is `emyBlock.getTerms()` / `emyDesignGetBlock`.
3. `emyTermSetNewName` success check `if result is not None: return True` — doc says returns emyTerm or NULL, so None-check is plausible but unchecked.
4. `editor` tool misuse corrupted the file; final answer was chat-inline only — SUT that relies on editor may hit same trap.
5. No handling of name **collisions** (e.g. s08xx→s16xx when s16xx already exists) — not requested by user, optional.

## Why this makes a good shard-C case
- Real user, fresh (joeyli not in C.jsonl 163 users), real Aether schematic/layout workflow.
- Pure C-domain: pyAether + schematic + cellview + terminal rename.
- Self-contained: deliverable is a static .py + .tcl; check.py can do **static AST/regex inspection** (no live Aether needed).
- Clean correctness signal: prefix-increment + suffix-preserve + zero-pad + real rename API + save + F7 binding → k≥8 checkable assertions.
- Good negative/fake material: suffix-instead-of-prefix increment, no-zero-pad, hallucinated API, README-only, print-only, hardcoded output names.
- Hidden env_B: different prefix/suffix/delta (e.g. d00a→d08a, delta=8) generalization gate.

## trace_source metadata
host=hfeg0pkn004, user=joeyli, session_file=1795253044250_ab6ck.messages.json, session_msgs=274,
real_task_summary="pyAether py3 脚本：批量累加一组 schematic pin/terminal 名称的数字前缀、后缀不变 (s01xx-s08xx→s09xx-s16xx)，并绑定 F7 快捷键在打开 layout 后一键执行"
