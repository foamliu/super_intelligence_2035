# Deepread: 1789960601663_3pcjt (lorikx@hfeg0pkn001, mc32, verification)

**Trace**: /home/lorikx/.cline/data/sessions/1789960601663_3pcjt/1789960601663_3pcjt.messages.json (1.3MB, 60 msgs)
**Scan kw**: synopsys:40;systemverilog:31;verilog:17;synthesis:6;aether:5;pyaether:3;rtl:2
**digi:ana = 56:5** (clean digital-dominant, verification)

## Real user turns (rule2 check for A-faithful)
- **U#1 (CLEAN need, A-faithful rule2 OK)**: `/home/lorikx/2prfbv_refer/verification/2prf_vector_generate_v6/ top.sv和Makefile 需要怎么修改可以变成生成fsdb`
- U#19: `make DATA_WIDTH=72 DEPTH=1024 build_teston TIMING_VALIDATION TIMING_DEBUG all 这个命令怎么用` (usage Q&A, not main task)
- U#20: `请帮我检查 timing.fsdb 的15000ps左右...寻找一下Q没有恢复输出的原因` (NEW debug task, asks to find cause — rule2 borderline, user describes symptom not fix)
- U#26: `请整理目前的内容，从问题到原因到解决方案` (meta summary)
- **U#27 (rule2 VIOLATE)**: `deselect 周期也在擦全阵列...问题出在哪 同事的逻辑成立的前提是...但模型实际是...` (user GIVES root-cause + mechanism → cannot be A-faithful task statement)
- U#30: `如果这段时间都写进去了，为什么后面没有时序违例的阶段还读不出来数据` (debug follow-up)

→ A-faithful task statement = **U#1 only**. U#20+ is a separate Q-recovery debug phase (not used).

## Phase 1 task (U#1): make FSDB generation togglable
**Input (as agent read it, msg[5]/msg[8])**:
- `Makefile` (orig, 101 lines): VCS Makefile, VERDI_HOME=/apps/synopsys/verdi/R-2020.12, **unconditional** novas PLI linkage (`VCS_OPTS += -P .../novas.tab .../pli.a` + `-kdb -lca`), defines USER_CLOCK_CYCLE/USER_DATA_WIDTH/USER_DEPTH/USER_MUX/USER_OUTPUT_NAME, BUILD_TARGETS filter for build_%/timing_validation/timing_debug.
- `src/top.sv` (orig, 289 lines): SRAM 2-port verification top_tb. Has `USER_FILENAME` macro (default "timing"). **VCD dump block commented out** (lines 244-255). **Unconditional `initial begin $fsdbDumpfile($sformatf("%s.fsdb",`USER_FILENAME)); $fsdbDumpvars(0, top_tb); $display(...); end`** (lines 256-262) — NOT gated on any macro.
- `file.list`: 7 bytes (just `src/top.sv` likely).

**Gold (agent wrote to /home/lorikx/.cline/scripts/data/, msg[16]/[17], re-read msg[27])**:
1. `Makefile.fsdb` (109 lines): wraps PLI linkage in `ifeq ($(FSDB),1)` block, adds `FSDB ?= 1` default, adds `+define+DUMP_FSDB` inside block, renames `USER_OUTPUT_NAME` define → `USER_FILENAME`. → FSDB togglable: `make FSDB=1` (default) links PLI + defines DUMP_FSDB; `make FSDB=0` skips PLI + no DUMP_FSDB (fast regression).
2. `top_fsdb_snippet.sv` (21 lines): wraps the `initial begin $fsdbDumpfile...end` block in `` `ifdef DUMP_FSDB `` / `` `else $display("DUMP_FSDB not defined...") `endif ``. → $fsdb tasks only called when DUMP_FSDB defined (FSDB=1); FSDB=0 prints notice instead.

**Key transformation** (unconditional → conditional/togglable):
- Makefile: PLI `ifeq($(FSDB),1)` gate + `DUMP_FSDB` macro define
- top.sv: `$fsdbDump*` `` `ifdef DUMP_FSDB `` gate + `` `else `` fallback

**Why this is distinct from jzlbn FsdbVerdiInteg-001 / 6yrpu SimMakefileVCS-001**: those convert iverilog→VCS+FSDB (different starting point). 3pcjt starts from a VCS Makefile that ALREADY links PLI unconditionally + top.sv ALREADY calls $fsdbDumpfile unconditionally; the task is to make FSDB **togglable** (gate PLI + macro + $fsdb calls on a make flag). Different sub-task.

## Asset availability
- uploads/: none (user pointed at /home/lorikx/2prfbv_refer/.../ path, agent read via read_files policy)
- Real files fetched via ssh cat from hfeg0pkn001:
  - orig Makefile (from trace msg[5] tool_result) → /tmp/3pcjt_assets/orig_mkf.txt (2791 bytes)
  - orig top.sv (from trace msg[8] tool_result) → /tmp/3pcjt_assets/orig_top.txt (7197 bytes)
  - gold Makefile.fsdb (from trace msg[27]) → /tmp/3pcjt_assets/gold_mkf.txt (3070 bytes)
  - gold top_fsdb_snippet.sv (from trace msg[27]) → /tmp/3pcjt_assets/gold_top.txt (781 bytes)
  - on-disk Makefile (current, post-session, has FSDB) — NOT used as original (already modified)

## Case plan
- **task_id**: EDA-Eval-DesignFlow-FsdbTogglePatch-001
- **domain**: verification; **track**: A (faithful); **level**: L2-static (真跑 candidate + `make -n` dry-run on hidden B)
- **prompt**: U#1 verbatim
- **assets A**: orig Makefile + src/top.sv + file.list + prompt.txt + task_brief.md
- **hidden B**: synthesized Makefile + top.sv with same unconditional-FSDB pattern but DIFFERENT identifiers (VERDI_HOME=U-2023.03-SP1-1, top=tb_counter, macro=WAVE_NAME, different PLI subpath variant, minimal counter TB). Zero identifier overlap with A.
- **candidate**: `enable_fsdb_toggle.py` — general patcher: wraps PLI in `ifeq($(FSDB),1)` + adds DUMP_FSDB define + wraps $fsdbDump* in `ifdef DUMP_FSDB`/`else`.
- **check.py**: ~14 conds (a-n): a no-forbidden-calls b py_compile c [B]exit0+outputs d [B]FSDB toggle var e [B]PLI gated in ifeq f [B]DUMP_FSDB define g [B]top.sv $fsdb ifdef DUMP_FSDB h [B]`else` branch i [B]make -n FSDB=1 parses j [B]make -n FSDB=0 no novas.tab k [B]make -n FSDB=1 has novas.tab+DUMP_FSDB l [A]reverse-hardcode guard (candidate on A yields same transform) m [B']determinism n [B]no ungated $fsdb call remains.
- **negatives**: empty_shell, print_expected, core_deleted (all must FAIL).
- **真跑**: candidate via subprocess on B; `make -n FSDB=1`/`FSDB=0` dry-run via subprocess (validates Makefile parse + expansion). vcs/verdi PLI available on .75 (R-2020.12 + novas.tab) if真跑 vcs needed, but `make -n` suffices for L2-static.

## Tool availability on .75
- vcs: /apps/synopsys/SRB/vcs/R-2020.12/bin/vcs (R-2020.12) ✓
- verdi PLI: /apps/synopsys/verdi/R-2020.12/share/PLI/VCS/LINUX64/{novas.tab, pli.a} ✓
- make: available
