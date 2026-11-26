#!/usr/bin/env python3
"""Update summary_stats.json: add scansync.r315 entry, refresh note + updated_at."""
import json

HERE = "/nasdata/app.e0031982/code/super_intelligence_2035/doc/ZhuLong_DAC2027/benchmark/designflow"
s = json.load(open(HERE + "/summary_stats.json"))

s["scansync"]["r315"] = {
    "ts": "2026-11-10T13:55:00+08:00",
    "date": "2026-11-10",
    "round_type": "case (cleared r314 DEBT:1 build — RhrQueueBoundsDiag-001, A-faithful diagnosis-generator)",
    "scan_dir": "ssh_eda_search_20261109_224902",
    "scan_confirmed": "no new scan since r292 full rescan (mc30=2247, dedup=5999, users=512, hosts=696 unchanged); daily log 20261110 healthy 2981 lines (per r314 scansync)",
    "case_delivered": "EDA-Eval-DesignFlow-RhrQueueBoundsDiag-001",
    "case_k": 15,
    "case_domain": "verification",
    "case_track": "faithful",
    "case_level": "L1-static",
    "shard_A_new_this_round": 1,
    "shard_A_jsonl": 199,
    "trace": "1792053769843_7huyr (aocao@hfeg0plg227, mc129) -> case",
    "finding": (
        "r315 cleared the r314 DEBT:1 (7huyr diagnosis-generator case build). "
        "REFRAME (matching acaey/SvHierRefDiag-001 spec-driven diagnosis-generator pattern): "
        "deliverable=gen_rhr_diag.py (stdlib generator) + spec_a.json; generator emits "
        "diag_rhr_bounds.py which reads spec.json + structured codebase (queues/address_spaces/"
        "indexing_points/init_loops/log_warnings/user_constraints) and statically DERIVES the "
        "root cause: queue decl (by name), address-space max (2^bits-1), max index value "
        "(max index_var_max), out-of-bounds judgment + OOB-point filtering (in-bounds distractor "
        "filtered), root-cause classification (queue_index_out_of_bounds_undersized_push_back_init), "
        "fix strategy (separate_preinit_full_address_space_plus_keep_aci_loop_direct_index) + "
        "target (the push_back init loop) + why_simple_extend_rejected (from no_extend_i_to_full_"
        "space constraint). A=spec_a faithful (aocao/decqa/cyclic_xyz/addr_q/ROW_COUNT=65760/RTSVQI/"
        "simulation.pat:106/17-bit/114712/131072/RWL); hidden B=spec_b isomorphic (q_addr/tb_top.sv/"
        "rhr_drv.sv/18-bit/decl_size=32768/max_index=258999/RTSVQI @ sim_pattern.pat:88/MAIN+REDIST/"
        "redist_map). check.py 15 conds a-o (independent recompute). Self-verify: ref PASS 15/15, "
        "8 negatives (fake_empty/fake_print_a/fake_core_deleted/naive_no_filter/fake_core_max/"
        "naive_hardcode_a/fake_print_only/fake_fix_no_constr) ALL FAIL NEG_RC=0, §4.9 (a)(b)(c) "
        "covered. Assertion gate k_rationale=k_check=15>=8 PASS. test_sha8=d1114efa test==disk. "
        "A.jsonl 198->199. ledger 7huyr->case (verification 45->46). Leak-isolation OK (assets have "
        "no check.py/reference/jsonl/test). No new scan (still r292 rescan). Paper: PAPER_SKIP(no "
        "latexmk); \\Ntasks synced 997->1007 (A:199 B:235 C:284 D:289), App A breakdown updated. "
        "10th clean A-faithful produce scarcity context (analysis-only trace made viable via "
        "diagnosis-generator reframe, 2nd such reframe after SvHierRefDiag-001)."
    ),
    "mc30": 2247,
    "hosts": 696,
    "updated_at": "2026-11-10T13:55:00+08:00",
}

s["note"] = (
    "11/10 r315: case delivered RhrQueueBoundsDiag-001 (7huyr/aocao, verification, A-faithful "
    "diagnosis-generator, k=15, A.jsonl 198->199). PIVOT: 7huyr r314-claimed analysis-only trace "
    "(USER#1 'check code logic, wave looks ok' -> addr_q queue 65760 vs addr_phys 114719 RTSVQI "
    "out-of-bounds) reframed to spec-driven diagnosis-generator (gen_rhr_diag.py -> diag_rhr_bounds.py "
    "derives queue-bounds root cause: decl/max-index/OOB-filter/classification/fix+constraint). "
    "10th produce-scarcity context; analysis-only traces viable via diagnosis-generator reframe "
    "(2nd after SvHierRefDiag-001). Latest scan 11/09 r292 (no new), daily log 11/10 healthy 2981 lines."
)
s["updated_at"] = "2026-11-10T13:55:00+08:00"

with open(HERE + "/summary_stats.json", "w") as f:
    json.dump(s, f, ensure_ascii=False, indent=2)
    f.write("\n")
print("summary_stats.json updated: scansync.r315 added, note + updated_at refreshed")
