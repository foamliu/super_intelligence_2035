#!/usr/bin/env python3
"""R300: Scene-Weighted Reward Design for RL R4 arm (data-driven from R297 API gap).

R297 found SFT v11-v36 caused catastrophic forgetting in Layout (-18.7pp)
and Design Mgmt (-15.5pp), while improving Schematic (+16.6pp).  R297
recommended scene-sensitive RL rewards to prevent RL "laziness".

This script generates a scene-weight config (JSON) from the empirical R297
gap data, plus a both_missed API bonus set (322 APIs both models failed to
use = RL core target) and an anti-forgetting API set (164 base_only APIs).

Surrogate declaration: MiniCPM5-2B is a BaiZe surrogate; gains do not transfer.
"""

import json
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
GAP_FILE = os.path.join(SCRIPT_DIR, "api_gap_analysis_r297.json")
OUT_CONFIG = os.path.join(SCRIPT_DIR, "rl_scene_weight_config_r300.json")
OUT_SUMMARY = os.path.join(SCRIPT_DIR, "r300_scene_weight_summary.json")

FORGETTING_PENALTY_COEF = 2.0
GAP_BONUS_COEF = 0.5
MAX_WEIGHT = 1.5
BOTH_MISSED_BONUS = 0.03
ANTI_FORGET_PENALTY = 0.02
TOP_N_BOTH_MISSED = 50

SCENARIO_CANON = {
    "Schematic": "schematic",
    "Layout": "layout",
    "Design Management": "design_mgmt",
    "Others": "others",
}


def compute_scene_weights(scenario_summary):
    """Compute per-scenario reward multipliers from R297 gap data.

    weight = 1.0 + max(0, -delta)*2.0 + (1 - recall)*0.5
    Then normalized so the best scenario = 1.0 baseline; capped at 1.5.
    """
    raw = {}
    for scenario, stats in scenario_summary.items():
        canon = SCENARIO_CANON.get(scenario, scenario.lower().replace(" ", "_"))
        sft_recall = stats.get("sft_recall", 0.0)
        delta = stats.get("sft_recall_delta", 0.0)
        forgetting = max(0.0, -delta) * FORGETTING_PENALTY_COEF
        gap = (1.0 - sft_recall) * GAP_BONUS_COEF
        raw[canon] = 1.0 + forgetting + gap
    max_raw = max(raw.values()) if raw else 1.0
    weights = {}
    for canon, w in raw.items():
        norm = w / max_raw if max_raw > 0 else 1.0
        weights[canon] = round(min(norm, MAX_WEIGHT), 4)
    return weights, raw


def extract_both_missed_apis(top_both_missed, n=TOP_N_BOTH_MISSED):
    """Extract top-N both_missed API names for the curriculum bonus set."""
    apis = []
    for entry in top_both_missed[:n]:
        api = entry.get("api", "")
        if api:
            apis.append(api)
    return apis


def extract_anti_forget_apis(api_matrix, n=50):
    """Extract top-N base_only APIs (forgotten by SFT) for anti-forgetting."""
    if not isinstance(api_matrix, list):
        return []
    result = []
    for row in api_matrix:
        if not isinstance(row, dict):
            continue
        if row.get("category") == "base_only":
            api = row.get("api", "")
            if api:
                result.append(api)
    return result[:n]


def main():
    with open(GAP_FILE, "r") as f:
        gap = json.load(f)

    scenario_summary = gap["scenario_summary"]
    top_both_missed = gap.get("top_both_missed_apis", [])
    api_matrix = gap.get("api_matrix", [])
    cat_counts = gap.get("api_category_counts", {})

    weights, raw_weights = compute_scene_weights(scenario_summary)
    both_missed_set = extract_both_missed_apis(top_both_missed)
    anti_forget_set = extract_anti_forget_apis(api_matrix)

    config = {
        "meta": {
            "version": "r300",
            "source": "api_gap_analysis_r297.json",
            "design": "scene-weighted R4 enhancement (R297 empirical gap)",
            "surrogate_declaration": "MiniCPM5-2B surrogate; gains do not transfer to BaiZe",
            "date": "2026-11-12",
        },
        "scene_weights": weights,
        "scene_weight_raw": {k: round(v, 4) for k, v in raw_weights.items()},
        "both_missed_api_bonus_set": both_missed_set,
        "both_missed_bonus_per_api": BOTH_MISSED_BONUS,
        "anti_forget_api_set": anti_forget_set,
        "anti_forget_penalty_per_api": ANTI_FORGET_PENALTY,
        "design_constants": {
            "forgetting_penalty_coef": FORGETTING_PENALTY_COEF,
            "gap_bonus_coef": GAP_BONUS_COEF,
            "max_weight": MAX_WEIGHT,
            "top_n_both_missed": TOP_N_BOTH_MISSED,
        },
        "scenario_summary_input": scenario_summary,
        "api_category_counts": cat_counts,
    }

    with open(OUT_CONFIG, "w") as f:
        json.dump(config, f, ensure_ascii=False, indent=2)

    summary = {
        "scene_weights": weights,
        "scene_weight_raw": {k: round(v, 4) for k, v in raw_weights.items()},
        "both_missed_count": len(both_missed_set),
        "anti_forget_count": len(anti_forget_set),
        "formula": "weight = (1.0 + max(0,-delta)*2.0 + (1-recall)*0.5) / max_raw, capped 1.5",
        "bonus": BOTH_MISSED_BONUS,
        "penalty": ANTI_FORGET_PENALTY,
    }
    with open(OUT_SUMMARY, "w") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)

    print("=" * 64)
    print("R300 Scene-Weighted Reward Design (from R297 API gap)")
    print("=" * 64)
    print()
    print("Scene weights (normalized, best=1.0 baseline):")
    print(f"  {'Scenario':<16} {'SFT recall':>10} {'Delta':>8} {'Raw':>6} {'Weight':>8}")
    for scenario, stats in scenario_summary.items():
        canon = SCENARIO_CANON.get(scenario, scenario)
        print(f"  {canon:<16} {stats['sft_recall']:>10.3f} "
              f"{stats['sft_recall_delta']:>+8.3f} {raw_weights[canon]:>6.3f} "
              f"{weights[canon]:>8.3f}")
    print()
    print(f"Both-missed API bonus set: {len(both_missed_set)} APIs "
          f"(bonus +{BOTH_MISSED_BONUS}/correct API)")
    print(f"  Top 10: {', '.join(both_missed_set[:10])}")
    print()
    print(f"Anti-forgetting API set: {len(anti_forget_set)} APIs "
          f"(penalty -{ANTI_FORGET_PENALTY}/dropped API)")
    print(f"  Top 10: {', '.join(anti_forget_set[:10])}")
    print()
    print(f"Config saved: {OUT_CONFIG}")
    print(f"Summary saved: {OUT_SUMMARY}")


if __name__ == "__main__":
    main()
