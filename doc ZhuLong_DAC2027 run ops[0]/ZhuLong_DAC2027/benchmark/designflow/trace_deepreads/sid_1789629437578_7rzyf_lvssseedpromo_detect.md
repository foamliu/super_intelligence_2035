# Trace deepread — sid 1789629437578_7rzyf (ziyuny @ hfeg0pnd002, mc=831)

- **Domain**: physical_verify (Calibre LVS). session = `/home/ziyuny/.cline/data/sessions/1789629437578_7rzyf/1789629437578_7rzyf.messages.json` (2.8 MB, 580 msgs, 296 user turns, 264 tool_uses: 154 editor / 93 read_files).
- **Tool histogram**: editor 154, read_files 93, list_allowed_files 8, run_approved_command 4, skills 2.
- **Real task**: User debugs a Calibre LVS **FAIL** for hierarchy `Ary_1BK_2piece_WLx448` at `/rundata/ieda_agent_test/pv/lvs/Ary_1BK_2piece_WLx448_add_device_layer`. Files touched (via read_files, excerpts captured in session tool_results): `*.lvs.rep` (HCELL SUMMARY, OBJECT STATISTICS, LVS RULE PARAMETERS), `*.spi` (.SEEDPROM sections), `hcells`, `calibreLVS.rule`, `lvs.log`, `*.attwarn`.
- **Root cause (user-identified)**: device-layer **seed promotion** — `lvs_expand_hcell ( device_promotion no )` in the rule deck lets a sub-cell device be promoted across the hcell boundary, so the lower cell reports layout-missing / source-extra and the upper cell reports layout-extra / source-missing (complementary). `.SEEDPROM` markers in the spi netlist are the necessary signal.
- **User intent turns**:
  - U#0 continuation note (gives root cause → hint, not A-档 prompt)
  - U#35 「总结这类问题的分析方案，找共性」→ methodology doc
  - U#169 「如果不知道是否存在这个问题，方案要调整」→ **detection** intent (clean, no root cause given) — basis for this case
  - U#448/476/572/576/578 → rewrite skill-lvs-debug report for layout/PDK engineers; skill introduction with problem categories + specialized checks
- **Delivered artifact in trace**: `methodology.md` + skill-report rewrites (markdown documentation). Not directly judgeable.
- **Case extraction (this round, B-档 synthesized)**: extract the *detect seed promotion from a fresh LVS run* sub-task → `lvs_seedpromo_diag.py` CLI that parses `*.lvs.rep` + `*.spi` + `calibreLVS.rule` and emits structured JSON (top_cell, hcell_summary, rule_device_promotion, object_statistics, seedprom_markers, no_similar_instance_paths, complementary, flags, is_seed_promotion, confidence). 5 共性标志 + complementary pattern.
- **Assets**: A = synthesized Ary-style seed-promo run (real cell names from trace: Ary_1BK_2piece_WLx448, 10 leaf PASS / 5 FAIL, switch_close 39719/74961, .SEEDPROM, device_promotion no). Hidden B = synthesized MemCol_256x64 seed-promo run (different cells, explicit complementary SubArray -512 / GlobalBL +512).
- **Permission note**: `/rundata/ieda_agent_test/...` on hfeg0pnd002 is owned by ziyuny and **not readable** by e0031982 via ssh from .75 (Permission denied). Real LVS files reconstructed from session tool_result excerpts (138 read blocks, 1 MB) — used only to mirror realistic Calibre LVS report structure (HCELL SUMMARY table, LVS RULE PARAMETERS, OBJECT STATISTICS `Instances:` rows, `** no similar instance **` paths). No raw real file shipped; assets are synthesized.
- **Case id**: EDA-Eval-DesignFlow-LvsSeedPromoDetect-001 (physical_verify, L1-boundary, B-档 synthesized). 15 conditions (a–o), ref PASS 15/15, 5 negatives FAIL, §4.9 三假 FAIL. Gate k=15==15>=8 PASS.
