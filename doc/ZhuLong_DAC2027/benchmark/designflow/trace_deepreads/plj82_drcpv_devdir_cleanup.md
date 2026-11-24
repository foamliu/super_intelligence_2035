# Deep-read: plj82 — drcpv dev-dir cleanup after v0.7 bump

**trace**: `xxchen@hfeg0pkn003`, session `1795403976977_plj82`, mc=89
(drc:4583;calibre:144;.gds:88;.def:12;pdk:8;techfile:6;gdsii:1 — keywords
from the drcpv tool name + GDS/calibre artefacts, not from a DRC run itself).
34 msgs (20 user / 14 assistant), 588KB messages.json.

## Real user intent

> 「drcpv 开发版本进版到 v0.7 … 整理下当前目录下的文件和记录，删除掉零时性的无用的文件。」

Housekeeping: after bumping the DRC pattern tool dev version v0.6→v0.7,
clean up the dev directory by deleting temporary / regenerable files.
This is a recurring intent for xxchen — the earlier session `yh7cy`
(mc=160, v0.6) is the same task ("先清理一下当前的运行路径没有用的临时文件"),
so this is a stable, real, repeated user need, not a one-off.

## What the agent did (tool chain)

1. `list_allowed_files` (depth 3) on
   `/home/xxchen/workspace/DRC_pattern_tool/0.7/drcpv_develop` + `proj/` +
   `temp_script_run/` + `drcpv/` to map the tree.
2. `read_files` PROJECT.md / checkList.md / LDR_issue.md /
   maintain_pattern_types.md / drcpv/gui/__init__.py / requirements.txt /
   `log` / `run` / `gui` to learn conventions.
3. Wrote `temp_cleanup/inspect.py` (python-runner) — top-level entries +
   __pycache__/.pyc/.swp scan. Output showed:
   - keep: PROJECT.md(30KB), QA.gds(366KB), QA_skill_convert.gds(384KB),
     layer.map(95KB), qa_config_device*.txt(330KB each), docs/(15),
     drcpv/(1312), manual/(42), proj/(5), tasks/(5), gen_ldr_rule_checkid_map.py,
     read_gds.py, requirements.txt, run, gui(launcher)
   - remove: temp_script_run/(288 debug scripts), temp_qt_gdsView/(114),
     temp_qt_gui/(40), temp_manual_gds/(1), drcpv/gui/tmp_generate/(27
     _refresh_*.cfg/gds/log), all __pycache__ (root + drcpv/script + many
     function/.../good_pattern|bad_pattern/N), manual/*.md.swp(2 vim swap),
     root `log`(645KB CLI run log)
4. `temp_cleanup/inspect2.py` — confirmed tmp_generate triples + root
   qa_config_*.txt are TOOL config (output_gds QA.gds / layerMap layer.map)
   → keep.
5. `temp_cleanup/cleanup.py` — rmtree the 8 remove classes; freed ~23.7MB.
6. `temp_cleanup/verify.py` — top-level after cleanup (drcpv 1312→664
   files), residual scan (only temp_cleanup itself), `py_compile` all 586
   .py under drcpv/ → 0 failures.
7. `temp_cleanup/remove_self.py` — self-delete temp_cleanup/ + stray
   drcpv/script/__pycache__.

## Classification rules extracted (the case's spec)

| entry | action | reason |
|---|---|---|
| dir `__pycache__` | remove | bytecode cache |
| dir basename startswith `temp_` | remove | temporary dev / prototype dir |
| dir `tmp_generate` | remove | GUI-refresh generated cfg/gds/log |
| file `*.swp` | remove | vim swap residue |
| root-level file `log` | remove | regenerable CLI run log |
| else (source .py, layer.map, *.gds, qa_config_*.txt, docs/, proj/, run, gui) | keep | project file/dir |

Remove-dirs are NOT descended (whole dir = one remove entry).

## Case synthesis (DrcToolDevDirCleanupAudit-001)

Offline-Python (L1, pure stdlib) deliverable `cleanup_audit.py`:
- `python3 cleanup_audit.py <root> <mode=audit|apply> <out.json>`
- recursive walk, classify per rules above, emit JSON manifest
  {entries[{path,type,action,reason,size_bytes}], stats, applied,
  deleted_paths, compile_check{...}}
- audit: non-destructive (applied=false, tree byte-unchanged); apply:
  delete remove-files then rmtree remove-dirs deepest-first
- compile_check via builtin compile() (no .pyc written — critical so
  audit mode doesn't mutate the tree)

**判分设计**: hidden B (v0.8 tree, 10 remove: 2 __pycache__ + 4 temp_* +
1 tmp_generate + 2 .swp + log; 21 must-keep incl .py/config/gds/docs/proj)
+ hidden B2 (v0.9, 5 remove, B-unique `temp_proto_v9` for anti-hardcode).
check.py embeds HIDDEN_B/B2 as path→content dicts, builds in tempdir,
subprocess-runs candidate, 15 independent conditions (audit non-destructive,
each remove class, .py/config keep, stats consistency, apply deletion +
compile, B2 anti-hardcode, idempotent re-apply).

**k=15 全闸门通过**: ref PASS; 4 neg (noop→cond3, print_only→cond2,
delete_everything→cond8, hardcode_b→cond11) 全FAIL distinct; §4.9 三假
(empty→"script not found", print_only→cond2, delete-core no temp_ rule→cond4)
全FAIL; §4.6 k==15==test_rationale ①-⑮; §4.2 subprocess 真跑; §4.1 hidden
B/B2 不进 SUT 沙箱(attachments 只 sample_a+task_brief); §4.5 B2 反硬编
(temp_proto_v9 + count≠B); §4.7 tempfile.mkdtemp; §4.8 SUT 沙箱不含
reference/check.py/negatives/hidden.

**区别**: C 域 physical_verify 子型 drcpv-dev-dir-cleanup-audit 首例。
与 DrcDeckStructureAudit-001(deck 结构解析)/DrcResultsItemCollect-001(
per-cell results 解析)/VddVssStripeAudit-001(GDS PG label 几何审计)
产物/断言/trace 全不同 —— 本例聚焦「EDA 工具开发目录的规则化清理审计
+ 可选删除 + 源码可编译回归」，是 flow-driving/env-hygiene 类真实意图
(用户两次进版都做同样清理) 的可复用工具化。

**deepread note**: designflow/trace_deepreads/plj82_drcpv_devdir_cleanup.md (本文件)
