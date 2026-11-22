# Deepread — 1794550428633_s4vkc

- **slug**: `1794550428633_s4vkc`
- **user**: `yinyus`
- **host**: `hfeg0plg58` / `10.129.35.82`
- **match_count**: 495 (aether:1179 + drc:740 + calibre:81 + lvs:41)
- **domain**: layout_aether (Aether schematic construction)
- **lib**: `/proj/drcpa/V0/workdir/yinyus/yinyus_nicap_block`
- **cells created**: `AG_CapYdecneartest`, `AG_CapYdecneartest2` (empty schematic views, confirmed by `master.tag` + `sch.oa`)
- **messages**: 306

## Real task summary

User `yinyus` asked the agent to build a schematic circuit in Aether
(pyAether) inside library `yinyus_nicap_block`. The session had three phases:

1. **Create empty cell** `AG_CapYdecneartest` (schematic view) in
   `yinyus_nicap_block`.  Agent hit a `libstdc++.so` GLIBCXX_3.4.26
   conflict (system lib too old vs Aether's `libemy2netlist.so`) and
   solved it with `LD_PRELOAD` of Aether's bundled
   `/apps/empyrean/tools/aether_new/tools/platform/linux26-x86_64/lib/libstdc++.so`.
   Cell created successfully; save API corrected from `dbSave`/`dbClose`
   to `daSave()` + `dbCloseCV(cv)` (later `emyDesignSave(cv)`).

2. **Create a second empty cell** `AG_CapYdecneartest2` — succeeded
   immediately using the warmed-up script template.

3. **Build the circuit** in `AG_CapYdecneartest` with topology
   (top → bottom):
   ```
   vad2o!  (top)
     │
     ├─ AG_CXcap1S511x503 <1>   (from drcpa_analog)
     └─ AG_CXcap1S511x503 <0>   (from drcpa_analog)
     │
   vss!  (bottom)
   ```
   - 2× capacitor instance `AG_CXcap1S511x503` sourced from library
     `drcpa_analog`, with instance-name bit suffix `<1:0>`.
   - **Key user correction**: `vad2o!` and `vss!` are **TECHLIB
     power/ground instances** (created with `dbCrtInst` from lib
     `TECHLIB`, cells `vad2o` / `vss`, view `symbol`), **NOT schematic
     pins** (`dbCrtSchPin`).  The agent first built them as pins and the
     user corrected: "vad2o!/vss! 是 TECHLIB 的电源/地 cell，要用
     dbCrtInst 创建 instance 而不是 dbCrtSchPin".

## Assistant tool chain (key pyAether APIs used)

- `ae.emyInitAether("-adv")` — initialise Aether bridge
- `ae.dbOpenCV(lib, cell, view, mode)` — open existing cell view
- `ae.dbNewCellView(...)` — create a new schematic cell view
- `ae.dbDeleteCellView(cv)` — delete existing cell view (before recreate)
- `ae.dbCrtInst(cv, point, lib, cell, view, inst, ...)` — create instance
- `ae.dbCrtSchPin(cv, name, point, direction, orient)` — create pin
  (used incorrectly for power/ground in first attempt)
- `ae.dbCrtSchWire(cv, ...)` — draw schematic wire
- `ae.emyDesignSave(cv)` / `ae.daSave()` — save cell view
- `ae.dbCloseCV(cv)` — close cell view
- `ae.RAG_MCP_Server__search_apis` — API discovery
  (queries: "create new cell schematic library", "dbCrtInst create
  instance", "dbCrtSchWire draw wire", "save cell view database")

## Outcome

- Empty cells `AG_CapYdecneartest` and `AG_CapYdecneartest2` were
  **successfully created** (OA `master.tag` + `sch.oa` present).
- The circuit with **pins** (vad2o!/vss! as dbCrtSchPin) was built once
  in `AG_CapYdecneartest` and reported SUCCESS (msg 140), but was
  **wrong per user correction**.
- The corrected build with **TECHLIB instances** never cleanly
  completed: the agent got stuck in an editor/file-duplication loop and
  OA metadata (`data.dm`) caching issues after externally `rm`-ing the
  cell directory.  Final run (msg 305) was SIGKILLed (aborted).

## Verifiable deliverable for a benchmark case

A **written, followable operations specification**
(`ag_capydecneartest_schematic_build_spec.md`) that a pyAether script
can implement to build the corrected schematic: TECHLIB `vad2o` power
instance at top → 2× `drcpa_analog/AG_CXcap1S511x503` instances
(`<1:0>`) → TECHLIB `vss` ground instance at bottom, wired top-to-bottom
with `dbCrtSchWire`, saved with `emyDesignSave`/`dbCloseCV`.

Key correction the spec must encode: **vad2o/vss are `dbCrtInst` from
`TECHLIB`, not `dbCrtSchPin`** — this is the trap the real agent fell
into and the user explicitly corrected.
