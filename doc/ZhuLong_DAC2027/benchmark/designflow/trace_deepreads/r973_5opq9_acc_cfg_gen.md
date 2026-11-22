# r973 Deepread: AccCfgGenProduce-001 (5opq9)

## Trace Source
- **sid**: 5opq9
- **user**: e0045144
- **host**: hfeg0pkn004 (10.129.2.13)
- **mc**: 51
- **keywords**: rtl:270;verilog:31;binary:1;analog:1
- **session_file**: 1795079277820_5opq9.messages.json
- **size**: 450KB / 88 msgs / 10 user msgs
- **scp**: from /home/e0045144/.cline/data/sessions/1795079277820_5opq9/1795079277820_5opq9.messages.json

## User Intent (U#0/U#1, verbatim)
> 根据下面的makefile和lint cfg file写个acc cfg file，acc 配置变量如下：
> CXDP_ACC_EMPTY_FLIST，CXDP_ACC_CONN_FLIST，CXDP_ACC_HIER_FLIST，CXDP_ACC_GEN_INIT_FLIST
> makefile path: /home/e0045144/CXDP/ACC_Release/Makefile
> lint cfg path: /proj/lacaa/V0/workdir/xuwang/CXDP/v1.0/flow/acc/config/CXDP_LINT_CFG

## Session Flow
- U#0/U#1: config-gen request (this case's focus)
- U#2: parse Makefile (analysis)
- U#3: how Makefile calls cfg params (Q&A)
- U#4: Perl script syntax question
- U#8: generate acc cases from create_cxdp_dir.py script

## Trace Gold (msg#2–msg#20)
1. Assistant reads Makefile → extracts CXDP_ACC_*_FLIST, FILELIST_DIR, PERL, GEN_INIT_CON_CSV, ACC_AUTO_CONNECT
2. Assistant reads LINT CFG (CXDP_LINT_CFG) → format template (header + 3 sections + comment tables)
3. Assistant reads existing CXDP_ACC_CFG (leftover copy of LINT template, still has CXDP_LINT_* vars)
4. Assistant creates new CXDP_ACC_CFG following LINT format but with ACC-specific variables:
   - Section 1 Setup: CXDP_ACC_FILELIST_DIR, 4 FLIST vars, ROOT_DIR, ENV_INIT_EN
   - Section 2 Tool: CXDP_ACC_PERL, GEN_INIT_CON_CSV, AUTO_CONNECT, GEN_EMPTY_SCRIPT, GEN_EMPTY_ASSIGN
   - Section 3 Output: GEN_CSV_EN, RUN_ACC_EN, OUTPUT_DIR, CSV_OUT_DIR, RTL_OUT_DIR, OUTPUT_TAG, QA_EMPTY_EN

## Case Design
- **Script**: `gen_acc_cfg.py <makefile> <lint_cfg> <output>`
- **A fixture** (visible): Makefile_A (apb_bus filelists, FILELIST_DIR=../filelist, PERL=perl) + CXDP_LINT_CFG_A (author=Yuping Leng, v0.1, 2026-10-16)
- **Hidden B**: Makefile_B (axi_bus filelists, FILELIST_DIR=../flist, PERL=/usr/bin/perl, different script paths) + CXDP_LINT_CFG_B (author=Min Zhao, v1.2, 2026-11-01)
- **check.py**: 21 assertions (a-u) including §4.9 anti-degenerate
- **Ref**: PASS 21/21, 3 negatives FAIL

## Key Transformation Rules
- Makefile `KEY = VALUE` or `KEY ?= VALUE` → parsed into dict
- LINT CFG header (AUTHOR/VERSION/DATE) → adapted for ACC CFG
- 4 FLIST vars from Makefile → direct copy to ACC CFG
- FILELIST_DIR from Makefile → CXDP_ACC_FILELIST_DIR in ACC CFG
- PERL/GEN_INIT_CON_CSV/ACC_AUTO_CONNECT from Makefile → ACC CFG Section 2
- Standard ACC vars (ROOT_DIR=ACC, ENV_INIT_EN=1, GEN_EMPTY_SCRIPT, etc.) → fixed defaults

## Selection Notes
- mc≥10 pool (shard_mc.A=10), _a_dom_cands_r963.tsv 420 A-domain candidates
- 4-shard ledger (4047 unique sids) cross-exclusion → 47 fresh A-domain candidates
- A-pure filtering (exclude C/B/D-dominant): top candidates include 5q6uq(mc112), 4i95w(mc70), s509i(mc61), 5opq9(mc51)
- 5opq9 selected: U#0/U#1 is cleanest config-gen produce-task (clear I/O + deterministic transformation + easy hidden-B)
- No intent-dup with prior A cases (no prior ACC config-gen case)
