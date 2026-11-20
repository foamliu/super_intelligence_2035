# Trace deepread: uiqz1 — CXDP design-list generator (perl)

- **session**: `1792843726821_uiqz1.messages.json`
- **user/host**: e0043890 @ hfeg0pnd002 (also visible on hfeg0pkn00{1..5} via NFS home)
- **mc**: 212 (rtl:1742 verilog:93 netlist:40 synthesis:24 drc:14 synopsys:12) — clean digital/RTL lean (digi=1899 ana=27)
- **size**: 2.31 MB, 857 msgs, 405 tool calls (run_approved_command 146 / editor 138 / read_files 79 / list_allowed_files 37)
- **agent**: zhulong "lead" profile, 2026-10-31, NFS home `/home/e0043890`
- **shard**: A (digital — lint/RTL front-end flow)

## User intent (verbatim, clean need turn — A-faithful rule2 OK: no root-cause/fix given)

USER#7 (idx 22), verbatim:

> 你可以访问/proj/lacaa/V0/workdir/ypleng/CXDP吗，这是SoC团队和CAD团队联合打造的前端流程设计环境，目的是通过/proj/lacaa/V0/workdir/ypleng/CXDP/v1.0/flow/utility/create_cxdp_dir/create_cxdp_dir.py来创建一个目录，在该目录下可以放置自己的设计文件后，进到各个流程下去跑流程。
> 例如使用命令create_cxdp_dir.py -name cla_top -proj_cfg /proj/lacaa/V0/workdir/ypleng/demo/SOC_MPW/config/CXDP_PROJ_VARS 创建一个cla_top模块的目录，然后将cla_top的模块设计手动copy到cla_top/src_rtl下，
> 对应的RTL list文件是CXDP_DESIGN_CFG里变量CXDP_RTL_FILE_LIST指定的文件，例如CXDP_RTL_FILE_LIST = designlist，那么就从CXDP_RTL_SRC_DIR指定的目录开始去找CXDP_RTL_FILE_LIST指定的文件
> 写一个perl脚本，叫gen_design_list.pl，执行脚本时，可以读取该目录下的CXDP_DESIGN_CFG, CXDP_PROJ_CFG文件，从两个CFG文件的变量去生成run SG-lint要用的RTL designlist.f
> 以/proj/lacaa/V0/workdir/ypleng/demo/cla_top为例，写一个gen_design_list.pl脚本在/proj/lacaa/V0/workdir/ypleng/demo/cla_top/lint/run下，执行gen_design_list.pl时，生成designlist，里面要包含定义的RTL的绝对路径

Earlier turns (hello / chinese-input Q&A / "你可以访问...demod/lint/run吗" / pasting CLA Verilog stubs) are preamble; later turns are Makefile/lint-run iterations (beyond the clean need). USER#7 is the focused "提出需求" turn.

## CXDP environment structure (reconstructed from trace)

```
/proj/lacaa/V0/workdir/ypleng/demo/cla_top/
├── config/
│   ├── CXDP_DESIGN_CFG   (113 lines, module-level: CXDP_DESIGN_NAME=cla_top, CXDP_RTL_SRC_DIR=src_rtl, CXDP_RTL_FILE_LIST=designlist, CXDP_DESIGN_ROOT=../../..)
│   └── CXDP_PROJ_CFG     (313 lines, project-level: lib paths, corners, $(CXDP_*) var refs)
├── src_rtl/
│   ├── designlist        (1 line: `*.v`  — glob pattern)
│   ├── full_adder.v      (1-bit FA)
│   ├── cla2.v            (2-bit CLA)
│   ├── cla4.v            (4-bit CLA)
│   ├── cla_recursive.v   (param WIDTH=16 recursive CLA)
│   └── adder_pow2.v      (top wrapper)
└── lint/run/
    ├── CXDP_DESIGN_CFG -> ../../config/CXDP_DESIGN_CFG   (symlink)
    ├── CXDP_PROJ_CFG   -> ../../config/CXDP_PROJ_CFG     (symlink)
    ├── CXDP_LINT_CFG   (91 lines, lint-tool cfg)
    ├── Makefile         (symlink to CXDP flow Makefile)
    └── gen_design_list.pl  (the gold script, 93 lines)
```

## Gold: gen_design_list.pl (deployed in lint/run, 93 lines)

Key logic:
1. `parse_cfg($f)`: read CFG, strip `#` comments + whitespace, match `KEY = VALUE` into `%v`.
2. `resolve_vars($v,$proj,$des)`: iteratively substitute `$(VAR)` (up to 20 rounds) — VAR looked up in design-cfg first, then proj-cfg.
3. `expand_list($lf,$sd)`: read list file, strip comments/blanks, for each entry: if absolute use as-is else `catfile($sd,$entry)`, `bsd_glob` expand, keep `abs_path($f)` for `-f $f`. Returns sorted unique keys.
4. MAIN: `abs_path('CXDP_DESIGN_CFG')` resolves the symlink → real config dir → `dirname` twice = design root. Read both CFGs, resolve vars. `CXDP_RTL_SRC_DIR` (default `src_rtl`) + `CXDP_RTL_FILE_LIST` (default `designlist`). `rtl_abs = design_root/rtl_src_dir`. `list_file = rtl_abs/file_list`. `expand_list`. Write `designlist.f` in cwd with header `# RTL file list for SG-Lint (gen_design_list.pl)`, `# Design: <name>`, `##TOP_MODULE <name>`, then sorted absolute paths.

## Verified gold output on A (cla_top)

```
# RTL file list for SG-Lint (gen_design_list.pl)
# Design: cla_top
##TOP_MODULE cla_top
/.../test_cla_top/src_rtl/adder_pow2.v
/.../test_cla_top/src_rtl/cla2.v
/.../test_cla_top/src_rtl/cla4.v
/.../test_cla_top/src_rtl/cla_recursive.v
/.../test_cla_top/src_rtl/full_adder.v
```
exit 0, 5 files. ✅

## Case plan (A-faithful, digital, L1-static + subprocess真跑候选于 hidden-B)

- **A (SUT sees)**: prompt = USER#7 verbatim; assets = cla_top example (config/ + src_rtl/ + designlist + 5 .v files + lint/run/README explaining symlink structure).
- **hidden-B** (`uart_top`): different module name, different `CXDP_RTL_SRC_DIR=rtl_src`, different file-list name `filelist` containing `*.v`, 4 .v files (uart.v/uart_rx.v/uart_tx.v/uart_top.v), config has `$(CXDP_DESIGN_ROOT)` include-dir refs to exercise var resolution.
- **hidden-C** (anti-hardcode guard, `mem_top`): CXDP_RTL_SRC_DIR=`src`, file-list=`rtl.lst` with explicit list `mem.v\nmem_top.v` (no glob), 2 .v files. Different count + different paths than B → script must re-read config, not hardcode.
- **check (≥14 conds a-n)**: unzip submit → `perl -c` syntax → subprocess run on hidden-B → assert designlist.f: exists, N absolute paths, all start `/`, all `-f`, all end `.v`, sorted, no dup, no glob remnants, count==#vfiles-in-B, header has design name, ##TOP_MODULE present → anti-hardcode: re-run on hidden-C, assert count==2 + paths differ from B → anti-stub (empty/print/core-deleted FAIL).
- **k = 14** (a-n), k_rationale == k_check == 14 ≥ 8.

## Notes

- /proj/lacaa denied from e0031982 on .75 — all real assets reconstructed from trace read_files tool_results (CXDP_DESIGN_CFG 113 lines, CXDP_PROJ_CFG 313 lines, designlist `*.v`, 5 .v files from editor new_text). Verified byte-faithful by re-running gold on reconstructed cla_top.
- The 249-line `/home/e0043890/gen_design_list.pl` (dev version) was superseded by the 93-line deployed version in `lint/run/` — gold = 93-line version (what user actually used).
- Trace has later Makefile/lint-run iterations (idx 100+) — out of scope for A-faithful USER#7 case (those are follow-on tasks, not the clean need).
