# trace_deepread: zloqs (1795237965362_zloqs) · chengk@hfeg0plg96 · mc=428 · layout_aether

> r910 deepread-only round (40-min budget exhausted by candidate triage). Case synthesis deferred to r911.

## trace_source
- session_file: `1795237965362_zloqs.messages.json`
- user: chengk · host: hfeg0plg96 (10.129.8.228) · IP alternatives: 10.129.2.12/10.129.8.224/10.129.8.234/10.129.33.229/10.129.40.209/172.16.8.162/172.16.8.163
- mc=428 · keywords: aether:1480;pyaether:301;drc:193;lvs:54;schematic:48;calibre:44;techfile:33;floorplan:19;cellview:15
- ledger: claimed r910 (shard C, layout_aether)
- NUM_MSGS=303, USER_TURNS=12, file size TBD (~1.5MB-class)

## user intent (verbatim, 12 user turns)
- **U[0]**: `[brainstorming] 希望详细了解目录/home/chengk/work/ZL_work/aether_ui_code/pylib/下所有代码的逻辑和具体用法，写清楚详细的说明文档和示例，便于快速了解代码用法，对于出现的陌生api，需要调用skill [eda_agent] [ask-eda] 详细了解所有知识，为了完美的完成这个任务，给出详细计划`
- **U[22]**: brainstorming skill system-prompt injection (long meta-prompt — NOT task content)
- **U[24]**: `需要修改部分内容，只解释目录AppForm和目录AsyncTool下的内容，输出文件写到目录/home/chengk/work/ZL_work/aether_ui_code/pylib/`
- **U[26]**: `ok` (approve design)
- **U[32]**: `按照spec开始开始产出 PyLib_使用指南.md`
- **U[43]**: `详略粒度：每字段都有一条映射行（偏全），给出详细说明和示例，示例需要达到如下要求：在aether中load这个函数代码可以直接运行无报错，代码必须参照/apps/imctf/cad/init/settings_aether/python_ae/，并描述预期的运行结果，示例需要较为复杂`
- **U[91]**: `以上内容基本满足，文档最后追加一部分内容，首先参照已有的代码，/apps/imctf/cad/init/settings_aether/python_ae/，总结出十个最常用的ui设计代码模板，要求复用的时候简单修改即可，此外，按照软件开发中最常用的ui组合设计，用aethe的api实现一下示例模板代码，补充前面没有的`
- **U[132]**: `文档中示例代码中全改成英文，第三部分 AsyncTool 详解按照同样的思路写到目录下一个新的文件中`
- **U[213]/U[222]**: more brainstorming skill injections (meta, not task)

## real_task_summary
Generate a **pylib usage guide** markdown doc covering `AppForm/` and `AsyncTool/` subdirs of `/home/chengk/work/ZL_work/aether_ui_code/pylib/`, with: (1) per-module architecture + class/method/field enumeration, (2) **per-field mapping rows** (field name → type/description/example), (3) runnable aether examples (referencing `/apps/imctf/cad/init/settings_aether/python_ae/`), (4) **10 reusable UI design code templates**, (5) AsyncTool detailed doc in a **separate file**. Examples must `load` in aether without error. Final deliverable: `PyLib_AppForm.md` + `PyLib_AsyncTool_详解.md` written to the pylib/ dir.

## artifacts (all fetchable from 10.129.8.228, e0031982 has read access)
| path | lines | role |
|---|--:|---|
| `/home/chengk/work/ZL_work/aether_ui_code/pylib/AppForm/AppForm.py` | 2459 | A source (real) — ~90 hi* APIs + AppField/AppForm/AppLayout/AppLayoutForm/AppWin/AppListBox/AppMsg classes; header v5.8 2026-09-20 |
| `/home/chengk/work/ZL_work/aether_ui_code/pylib/AsyncTool/AsyncTool.py` | 251 | A source (real) — AsyncTool class (asyncio+ThreadPoolExecutor) + gAsync singleton; funcExec/shellExec/setSize/getSize |
| `/home/chengk/work/ZL_work/aether_ui_code/pylib/PyLib_AppForm.md` | 1040 | GOLD doc (user-accepted) — covers AppForm architecture + per-field mapping + 10 UI templates |
| `/home/chengk/work/ZL_work/aether_ui_code/pylib/PyLib_AsyncTool_详解.md` | 229 | GOLD doc (user-accepted) — AsyncTool detailed doc |
| `/apps/imctf/cad/init/settings_aether/python_ae/` | — | reference style dir (formRegisiter.py, common_set.py, bindkeyBasic.py, layout/, hi/, se/, le/, tc/, ut/, veri/, db/, image/, mentor/, genabs/) |
| `/home/chengk/work/ZL_work/aether_ui_code/pylib/{APT,docs}` | — | out-of-scope (APT = Auto Placement Tool, not covered) |

AppForm.py header confirms: `import pyAether as ae` + PyQt5; type-in fields (hiCreateStringField/IntField/FloatField/ListField/PointField/BBoxField/PointListField), enumerated choice fields (hiCreateToggleField/RadioField/CyclicField/ButtonBoxField/SpinBox), combination (hiCreateComboField), display (hiCreateReportField), misc (hiCreateButton/FormButton/Label/LayerCyclicField/BooleanButton), tree (hiCreateTree/TreeItem/GetTree/...), scroll region. __init__.py has `from .AppForm import *` with `__all__` ~90 hi* APIs.

## A档 feasibility
**A档 NOT feasible**: trace has 12 user turns with iterative refinement (U[0]→U[132]); "gold" is the final accepted `PyLib_AppForm.md` + `PyLib_AsyncTool_详解.md` which the assistant produced autonomously across many turns. No single clean "user asks → gold" pair. → **B档 reframe**.

## B档 reframe plan (for r911 synthesis)
**Case id candidate**: `EDA-Eval-DesignFlow-PyLibApiDocGen-001` (layout_aether, B档 reframe)

**Reframe**: Build an offline **pylib API documentation generator** `pylib_api_doc_gen.py` that parses AppForm.py + AsyncTool.py source (AST-based) and emits a structured usage guide JSON with: per-module entries, per-class entries (with methods), per-field mapping rows (field name → type/description/example-call), runnable example code blocks (validated as syntactically-correct Python + referencing aether/pyAether APIs), and a templates section.

**A fixture (visible to SUT)**: real `AppForm.py` (2459 lines) + `AsyncTool.py` (251 lines), fetched via eda_flow run_commands ssh+cat from 10.129.8.228 to .75 workdir then embedded in `assets/<id>/A/`. Real gold docs (`PyLib_AppForm.md`/`PyLib_AsyncTool_详解.md`) kept as reference-only (NOT in SUT sandbox) for judge-side cross-check.

**B fixture (hidden, in `assets/<id>/hidden/`)**: synthetic small `AppForm_mini.py` (~150 lines, 1 class AppFormMini with 4 fields: string/int/toggle/combo + 3 methods: create/show/get_value) + `AsyncTool_mini.py` (~80 lines, AsyncToolMini with 3 methods: funcExec/shellExec/setSize). Known ground-truth structure for judge. Different names/structure from A (anti-hardcode).

**check.py (B-embedded, ≥8 assertions)** — judge parses SUT's generated doc JSON against B ground truth:
1. zip structure: submit.zip contains `pylib_api_doc.json` (+ optional md)
2. JSON top-level keys: `modules` / `classes` / `fields` / `methods` / `examples` / `templates`
3. `modules` contains exactly AppForm_mini + AsyncTool_mini (set-match)
4. `classes` enumerates AppFormMini + AsyncToolMini with correct base-class info
5. `fields` has 4 entries (string/int/toggle/combo) with correct name→type mapping per B ground truth
6. `methods` has 3+3 entries with correct names + signatures
7. `examples` ≥3 code blocks, each is syntactically valid Python (ast.parse) + contains `import pyAether as ae` or `ae.` reference
8. `templates` has exactly 10 entries (per U[91] requirement) each with name + code block
9. per-field mapping row format: each field entry has {name, type, description, example} all non-empty
10. no hardcoded A values (B uses different class/field names; assert B names appear, A names absent)
11. anti-stub: assert doc JSON is not empty / not just-print-expected / references B's actual structure

**test_rationale (k=11 条断言)**: `11 条断言：① zip 内含 pylib_api_doc.json ② JSON top-level keys 齐全 (modules/classes/fields/methods/examples/templates) ③ modules 集合 == {AppForm_mini, AsyncTool_mini} ④ classes 枚举 AppFormMini+AsyncToolMini 含 base-class ⑤ fields 4 条 (string/int/toggle/combo) name→type 正确 ⑥ methods 3+3 条 name+signature 正确 ⑦ examples ≥3 且 ast.parse 通过 + 含 pyAether/ae 引用 ⑧ templates 恰 10 条 ⑨ 每条 field mapping row {name,type,description,example} 非空 ⑩ 不硬编码 A (B 名称出现, A 名称缺席) ⑪ anti-stub (非空/非 print 期望/引用 B 实际结构)`

**Negatives**: (a) empty zip, (b) doc.json with only `{"modules":[]}`, (c) doc.json with A's class names copy-pasted (fails B-name assertion), (d) doc.json with 5 templates not 10, (e) examples with syntax errors. All must FAIL.

**§4.9 三假**: (a) empty shell → FAIL ②③; (b) print-only `{"status":"ok"}` → FAIL ②⑪; (c) ref-solve-with-core-deleted (no ast.parse validation) → FAIL ⑦.

**3-seed**: randomize B field/method name suffixes across 3 seeds; doc structure assertions must hold for all.

**Roundtrip sha256**: build_jsonl → extract → disk check.py byte-identical.

## why deferred (not lazy 0-case)
1. **Pool top-mc exhausted**: r910 triage of mc≥30 drc/calibre-dominant candidates (positions 1-250) found **near-total coverage** — all top fresh-looking candidates already C-cased or parked-with-reason (agzjb=DrcCwdRaceEvidence, m14th=parked-meta, cp5wk=DRCDeckWinClean, 5e6p2=DRCDeckSyncPlan, f7hpy=DRCSpecGen, 0c5yk=DRCSFCompare/DrcDeckValueCompare, 1xhgy=AutoCellTclFlow, ipbrb=LayoutElementAttribution, 8du7m=RsCalcFlowCompare, uml8e=ERCBootPlan, n1k2a/90vlt=token-burn-parked, zqelb=GUI-cleanup-parked, jr97m=parked). zloqs is the **only genuinely fresh** C-domain candidate in mc 30-2000 drc/calibre-dominant batch (verified: zero ledger rows across all 4 shards).
2. **zloqs needs external source fetch** (AppForm.py 2459 lines + AsyncTool.py 251 lines + 2 gold md files) — fetchable but requires 4 scp/cat operations + embedding as A fixture.
3. **B fixture + check.py (11 assertions) + negatives + 3-seed + roundtrip** is a full case build (~30 min) — cannot fit in remaining ~2 min of r910 40-min budget after triage.
4. **§3 allows**: "单条 trace 过大时可以本轮只深读，心跳记 DEBT: 1 deepread 未合成" — zloqs 303 msgs + 2459-line source fetch qualifies.

## next-round (r911) execution plan
1. `python3 designflow/trace_ledger.py --shard C claim` already done (r910). Verify still claimed.
2. Fetch 4 files via eda_flow run_commands ssh+cat from 10.129.8.228 → .75 workdir:
   `ssh 10.129.8.228 'cat /home/chengk/work/ZL_work/aether_ui_code/pylib/AppForm/AppForm.py'` (2459 lines → A source)
   `ssh 10.129.8.228 'cat /home/chengk/work/ZL_work/aether_ui_code/pylib/AsyncTool/AsyncTool.py'` (251 lines → A source)
   `ssh 10.129.8.228 'cat /home/chengk/work/ZL_work/aether_ui_code/pylib/PyLib_AppForm.md'` (1040 lines → reference-only gold)
   `ssh 10.129.8.228 'cat /home/chengk/work/ZL_work/aether_ui_code/pylib/PyLib_AsyncTool_详解.md'` (229 lines → reference-only gold)
3. Embed AppForm.py + AsyncTool.py as `assets/EDA-Eval-DesignFlow-PyLibApiDocGen-001/A/` (SUT-visible).
4. Synthesize B: `AppForm_mini.py` (~150 lines) + `AsyncTool_mini.py` (~80 lines) → `assets/<id>/hidden/` + `hidden_manifest.json`.
5. Write `reference/EDA-Eval-DesignFlow-PyLibApiDocGen-001/check.py` (B-embedded, 11 assertions).
6. Write `reference/.../solve.py` (ref doc generator using ast.parse on B source).
7. Self-verify: ref PASS 11/11 + 5 negatives FAIL distinct + §4.9(a)(b)(c) FAIL + 3-seed stable.
8. Build jsonl entry via `build_jsonl.py --shard C` + roundtrip sha256 check.
9. Append to `EDA-Eval-DesignFlow_C.jsonl` + mark ledger `--status case --case-id EDA-Eval-DesignFlow-PyLibApiDocGen-001`.
10. Commit both repos + update MEMORY_C.
