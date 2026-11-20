#!/usr/bin/env python3
"""R176: Expanded SFT Qualitative Eval (16-prompt) + Error Taxonomy + RL Reward-Arm Mapping.

Extends R175 (8-prompt) to 16 prompts (8 R175 replication + 8 new) across 4 EDA
categories (Layout/Schematic/DesignMgmt/Others, 4 each). Queries base (8098) and
SFT (8096) vLLM endpoints, applies an automated error taxonomy, and maps each SFT
failure to RL reward arms R1-R4 to quantify Phase-3 RL headroom.

Protocol (frozen from R175): temperature=0.0, max_tokens=400, /v1/chat/completions.
No sandbox needed -- direct vLLM API calls only.
"""
import argparse
import json
import re
import sys
import time
import urllib.request
import urllib.error

BASE_URL_DEFAULT = "http://localhost:8098"
SFT_URL_DEFAULT = "http://localhost:8096"
TEMP = 0.0
MAX_TOKENS = 400
TIMEOUT = 60

PROMPTS = [
    {"id": "L1", "category": "Layout", "replication": True,
     "prompt": "Write a Python function get_cell_area(name) that uses dbfunc.dbGetCell to get a cell by name and returns its area as a float.",
     "expected_api": "dbGetCell", "rubric": "def get_cell_area + dbGetCell + .area + float()",
     "correct_key": ["def get_cell_area", "dbGetCell", ".area"]},
    {"id": "L2", "category": "Layout", "replication": True,
     "prompt": "Write a Python function list_all_cells() that uses dbfunc.dbGetCells to return a list of all cell names in the database.",
     "expected_api": "dbGetCells", "rubric": "def list_all_cells + dbGetCells + return",
     "correct_key": ["def list_all_cells", "dbGetCells", "return"]},
    {"id": "L3", "category": "Layout", "replication": False,
     "prompt": "Write a Python function create_cell(cell_name) that uses dbfunc.dbCreateCell to create a new cell and returns it.",
     "expected_api": "dbCreateCell", "rubric": "def create_cell + dbCreateCell + return",
     "correct_key": ["def create_cell", "dbCreateCell", "return"]},
    {"id": "L4", "category": "Layout", "replication": False,
     "prompt": "Write a Python function get_cell_bbox(name) that uses dbfunc.dbGetCell to get a cell and returns its bounding box as a tuple (x0, y0, x1, y1).",
     "expected_api": "dbGetCell", "rubric": "def get_cell_bbox + dbGetCell + bbox",
     "correct_key": ["def get_cell_bbox", "dbGetCell"]},
    {"id": "S1", "category": "Schematic", "replication": True,
     "prompt": "Write a Python function get_inst_net(inst_name) that uses the PyAether schematic API to return the net name connected to an instance.",
     "expected_api": None, "rubric": "def get_inst_net + return net name",
     "correct_key": ["def get_inst_net", "return"]},
    {"id": "S2", "category": "Schematic", "replication": True,
     "prompt": "Write a Python function count_instances(cell_name) that uses dbfunc.dbGetInsts to count the number of instances in a cell.",
     "expected_api": "dbGetInsts", "rubric": "def count_instances + dbGetInsts + len()",
     "correct_key": ["def count_instances", "dbGetInsts", "len("]},
    {"id": "S3", "category": "Schematic", "replication": False,
     "prompt": "Write a Python function create_wire(net_name, points) that uses schCreateWire to create a schematic wire on the given net with the given points.",
     "expected_api": "schCreateWire", "rubric": "def create_wire + schCreateWire",
     "correct_key": ["def create_wire", "schCreateWire"]},
    {"id": "S4", "category": "Schematic", "replication": False,
     "prompt": "Write a Python function get_pin_name(pin_id) that uses leGetPin to get a pin object and return its name.",
     "expected_api": "leGetPin", "rubric": "def get_pin_name + leGetPin + return",
     "correct_key": ["def get_pin_name", "leGetPin", "return"]},
    {"id": "D1", "category": "DesignMgmt", "replication": True,
     "prompt": "Write a Python function save_design(path) that uses dbfunc.dbSaveDesign to save the current design to a file path.",
     "expected_api": "dbSaveDesign", "rubric": "def save_design + dbSaveDesign",
     "correct_key": ["def save_design", "dbSaveDesign"]},
    {"id": "D2", "category": "DesignMgmt", "replication": True,
     "prompt": "Write a Python function open_library(lib_path) that uses dbfunc.dbOpenLibrary to open a design library.",
     "expected_api": "dbOpenLibrary", "rubric": "def open_library + dbOpenLibrary",
     "correct_key": ["def open_library", "dbOpenLibrary"]},
    {"id": "D3", "category": "DesignMgmt", "replication": False,
     "prompt": "Write a Python function open_cellview(lib, cell, view) that uses dmOpenCellView to open a cell view and return it.",
     "expected_api": "dmOpenCellView", "rubric": "def open_cellview + dmOpenCellView + return",
     "correct_key": ["def open_cellview", "dmOpenCellView", "return"]},
    {"id": "D4", "category": "DesignMgmt", "replication": False,
     "prompt": "Write a Python function list_libraries() that uses dmGetLibs to return a list of all library names.",
     "expected_api": "dmGetLibs", "rubric": "def list_libraries + dmGetLibs + return",
     "correct_key": ["def list_libraries", "dmGetLibs", "return"]},
    {"id": "O1", "category": "Others", "replication": True,
     "prompt": "Write a Python function find_max(lst) that returns the maximum value in a list using functools.reduce.",
     "expected_api": None, "rubric": "def find_max + reduce + max (NOT operator.max)",
     "correct_key": ["def find_max", "reduce"], "known_trap": "operator.max"},
    {"id": "O2", "category": "Others", "replication": True,
     "prompt": "Write a Python function reverse_string(s) that returns the reversed version of string s.",
     "expected_api": None, "rubric": "def reverse_string + s[::-1] or reversed()",
     "correct_key": ["def reverse_string"]},
    {"id": "O3", "category": "Others", "replication": False,
     "prompt": "Write a Python function flatten_list(nested) that flattens a nested list into a single list.",
     "expected_api": None, "rubric": "def flatten_list + iter/extend or comprehension",
     "correct_key": ["def flatten_list"]},
    {"id": "O4", "category": "Others", "replication": False,
     "prompt": "Write a Python function count_words(text) that returns the number of words in a text string.",
     "expected_api": None, "rubric": "def count_words + split + len",
     "correct_key": ["def count_words", "len("]},
]


def chat_completion(base_url, model_name, user_prompt):
    payload = {
        "model": model_name,
        "messages": [{"role": "user", "content": user_prompt}],
        "temperature": TEMP,
        "max_tokens": MAX_TOKENS,
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        base_url.rstrip("/") + "/v1/chat/completions",
        data=data, headers={"Content-Type": "application/json"}, method="POST")
    t0 = time.time()
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            body = json.loads(resp.read().decode("utf-8"))
        elapsed = round(time.time() - t0, 2)
        choice = body["choices"][0]
        return choice["message"]["content"], choice["finish_reason"], \
            body.get("usage", {}).get("completion_tokens", 0), elapsed
    except Exception as e:
        return "ERROR: " + str(e), "error", 0, round(time.time() - t0, 2)


def analyze_output(content, spec):
    text = content or ""
    has_function_def = bool(re.search(r"def\s+\w+\s*\(", text))
    has_code_block = "```" in text
    has_return = "return " in text
    is_pure_prose = (not has_function_def) and (not has_code_block)
    expected_api = spec.get("expected_api")
    has_expected_api = (expected_api is None) or (expected_api in text)
    correct_keys = spec.get("correct_key", [])
    keys_found = [k for k in correct_keys if k in text]
    keys_missing = [k for k in correct_keys if k not in text]
    known_trap = spec.get("known_trap")
    hits_trap = (known_trap is not None) and (known_trap in text)
    return {
        "len_chars": len(text), "has_function_def": has_function_def,
        "has_code_block": has_code_block, "has_return": has_return,
        "is_pure_prose": is_pure_prose, "has_expected_api": has_expected_api,
        "keys_found": keys_found, "keys_missing": keys_missing, "hits_trap": hits_trap,
    }


HALLUCINATION_PATTERNS = [
    "Microsoft Access", "DBF file", "spreadsheet", "Excel",
    "database management system", "SQL", "MySQL", "PostgreSQL",
]


def detect_hallucination(content):
    text = (content or "").lower()
    return [p for p in HALLUCINATION_PATTERNS if p.lower() in text]


def classify_error(analysis, finish_reason, spec):
    if finish_reason == "error":
        return "error"
    if finish_reason == "length":
        return "protocol_failure"
    if analysis["is_pure_prose"] and not analysis["has_function_def"]:
        return "protocol_failure"
    if analysis["hits_trap"]:
        return "api_misuse"
    if not analysis["has_expected_api"] and spec.get("expected_api"):
        return "api_misuse"
    if analysis["has_function_def"] and analysis["has_return"]:
        # Check semantically-critical missing keys (exclude function name)
        fn_name_key = spec["correct_key"][0] if spec["correct_key"] else None
        critical_missing = [k for k in analysis["keys_missing"] if k != fn_name_key and k != "return"]
        if critical_missing:
            return "semantic_error"
        return "correct"
    if analysis["has_function_def"] and not analysis["has_return"]:
        return "incomplete"
    return "protocol_failure"


def map_to_reward_arm(error_class):
    table = {
        "correct": {"arm": "all_pass", "r1": 1, "r2": 1.0, "r3": 1.0, "r4": 1.0,
                    "note": "Correct -- all arms give full reward"},
        "protocol_failure": {"arm": "R1 catches", "r1": 0, "r2": 0.0, "r3": 0.0, "r4": 0.0,
                              "note": "No code produced -- R1 binary=0; R2 partial=0"},
        "api_misuse": {"arm": "R4 catches", "r1": 0, "r2": 0.3, "r3": 0.3, "r4": 0.0,
                        "note": "API misuse -- R4 API-legality=0; R2 partial for format"},
        "semantic_error": {"arm": "R2 gradient", "r1": 0, "r2": 0.5, "r3": 0.5, "r4": 0.5,
                            "note": "Right API wrong logic -- R2 partial captures gradient; R1 binary misses"},
        "incomplete": {"arm": "R1 catches", "r1": 0, "r2": 0.2, "r3": 0.2, "r4": 0.2,
                        "note": "Incomplete -- R1=0; R2 small partial"},
        "error": {"arm": "infra_error", "r1": 0, "r2": 0, "r3": 0, "r4": 0,
                   "note": "Infrastructure error"},
    }
    return table.get(error_class, {"arm": "unknown", "r1": 0, "r2": 0, "r3": 0, "r4": 0,
                                     "note": "Unclassified"})


def main():
    parser = argparse.ArgumentParser(description="R176 expanded SFT qualitative eval")
    parser.add_argument("--base", default=BASE_URL_DEFAULT)
    parser.add_argument("--sft", default=SFT_URL_DEFAULT)
    parser.add_argument("--base-model", default="minicpm5-2b")
    parser.add_argument("--sft-model", default="minicpm5-sft")
    parser.add_argument("--out", default="sft_qual_eval_r176_results.json")
    args = parser.parse_args()
    print("R176 Expanded SFT Qualitative Eval (16 prompts)")
    print("  base: {} ({})".format(args.base, args.base_model))
    print("  sft:  {} ({})".format(args.sft, args.sft_model))
    print("  temp={}, max_tokens={}".format(TEMP, MAX_TOKENS))
    print()
    results = []
    for idx, spec in enumerate(PROMPTS):
        pid = spec["id"]
        repl = "R175-repl" if spec["replication"] else "NEW"
        print("[{}/16] {} ({}, {}) ...".format(idx + 1, pid, spec["category"], repl), end=" ", flush=True)
        b_content, b_finish, b_tokens, b_elapsed = chat_completion(args.base, args.base_model, spec["prompt"])
        s_content, s_finish, s_tokens, s_elapsed = chat_completion(args.sft, args.sft_model, spec["prompt"])
        b_analysis = analyze_output(b_content, spec)
        s_analysis = analyze_output(s_content, spec)
        b_error = classify_error(b_analysis, b_finish, spec)
        s_error = classify_error(s_analysis, s_finish, spec)
        b_hallu = detect_hallucination(b_content)
        s_hallu = detect_hallucination(s_content)
        s_reward = map_to_reward_arm(s_error)
        print("base={} sft={} arm={}".format(b_error, s_error, s_reward["arm"]))
        results.append({
            "id": pid, "category": spec["category"], "replication": spec["replication"],
            "prompt": spec["prompt"], "expected_api": spec["expected_api"], "rubric": spec["rubric"],
            "base": {"content": b_content, "finish": b_finish, "completion_tokens": b_tokens,
                      "elapsed": b_elapsed, "analysis": b_analysis, "error_class": b_error,
                      "hallucination": b_hallu},
            "sft": {"content": s_content, "finish": s_finish, "completion_tokens": s_tokens,
                     "elapsed": s_elapsed, "analysis": s_analysis, "error_class": s_error,
                     "hallucination": s_hallu, "reward_arm_mapping": s_reward},
        })
    n = len(results)
    base_finish_length = sum(1 for r in results if r["base"]["finish"] == "length")
    sft_finish_stop = sum(1 for r in results if r["sft"]["finish"] == "stop")
    base_func_def = sum(1 for r in results if r["base"]["analysis"]["has_function_def"])
    sft_func_def = sum(1 for r in results if r["sft"]["analysis"]["has_function_def"])
    base_pure_prose = sum(1 for r in results if r["base"]["analysis"]["is_pure_prose"])
    sft_pure_prose = sum(1 for r in results if r["sft"]["analysis"]["is_pure_prose"])
    base_hallu = sum(1 for r in results if r["base"]["hallucination"])
    sft_hallu = sum(1 for r in results if r["sft"]["hallucination"])
    base_avg_chars = sum(r["base"]["analysis"]["len_chars"] for r in results) / n
    sft_avg_chars = sum(r["sft"]["analysis"]["len_chars"] for r in results) / n
    base_avg_tok = sum(r["base"]["completion_tokens"] for r in results) / n
    sft_avg_tok = sum(r["sft"]["completion_tokens"] for r in results) / n
    sft_correct = sum(1 for r in results if r["sft"]["error_class"] == "correct")
    sft_semantic = sum(1 for r in results if r["sft"]["error_class"] == "semantic_error")
    sft_api_misuse = sum(1 for r in results if r["sft"]["error_class"] == "api_misuse")
    sft_protocol = sum(1 for r in results if r["sft"]["error_class"] == "protocol_failure")
    sft_incomplete = sum(1 for r in results if r["sft"]["error_class"] == "incomplete")
    repl_results = [r for r in results if r["replication"]]
    new_results = [r for r in results if not r["replication"]]
    repl_correct = sum(1 for r in repl_results if r["sft"]["error_class"] == "correct")
    new_correct = sum(1 for r in new_results if r["sft"]["error_class"] == "correct")
    r1_scores = [r["sft"]["reward_arm_mapping"]["r1"] for r in results]
    r2_scores = [r["sft"]["reward_arm_mapping"]["r2"] for r in results]
    r4_scores = [r["sft"]["reward_arm_mapping"]["r4"] for r in results]
    summary = {
        "total_prompts": n, "replication_prompts": len(repl_results), "new_prompts": len(new_results),
        "base": {"finish_length": "{}/{}".format(base_finish_length, n),
                  "function_def": "{}/{}".format(base_func_def, n),
                  "pure_prose": "{}/{}".format(base_pure_prose, n),
                  "avg_len_chars": round(base_avg_chars, 1),
                  "avg_completion_tokens": round(base_avg_tok, 1),
                  "hallucination": "{}/{}".format(base_hallu, n)},
        "sft": {"finish_stop": "{}/{}".format(sft_finish_stop, n),
                 "function_def": "{}/{}".format(sft_func_def, n),
                 "pure_prose": "{}/{}".format(sft_pure_prose, n),
                 "avg_len_chars": round(sft_avg_chars, 1),
                 "avg_completion_tokens": round(sft_avg_tok, 1),
                 "hallucination": "{}/{}".format(sft_hallu, n),
                 "correct": "{}/{}".format(sft_correct, n),
                 "semantic_error": "{}/{}".format(sft_semantic, n),
                 "api_misuse": "{}/{}".format(sft_api_misuse, n),
                 "protocol_failure": "{}/{}".format(sft_protocol, n),
                 "incomplete": "{}/{}".format(sft_incomplete, n),
                 "correctness_rate": round(sft_correct / n * 100, 1),
                 "replication_correct": "{}/{}".format(repl_correct, len(repl_results)),
                 "new_correct": "{}/{}".format(new_correct, len(new_results))},
        "compression_ratio": round(base_avg_chars / sft_avg_chars, 1) if sft_avg_chars > 0 else 0,
        "token_efficiency": round(base_avg_tok / sft_avg_tok, 1) if sft_avg_tok > 0 else 0,
        "reward_arm_projection": {
            "R1_binary_mean": round(sum(r1_scores) / n, 3),
            "R2_partial_mean": round(sum(r2_scores) / n, 3),
            "R4_api_legality_mean": round(sum(r4_scores) / n, 3),
            "R2_vs_R1_gradient": round((sum(r2_scores) - sum(r1_scores)) / n, 3),
            "note": "R2 captures gradient R1 misses; R4 catches API misuse"},
    }
    output = {"timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
              "protocol": {"temperature": TEMP, "max_tokens": MAX_TOKENS,
                            "base_endpoint": args.base, "sft_endpoint": args.sft},
              "summary": summary, "results": results}
    with open(args.out, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)
    print()
    print("=" * 70)
    print("SUMMARY (16 prompts)")
    print("=" * 70)
    print("Base:  finish=length {}/{}, func_def {}/{}, pure_prose {}/{}, hallu {}/{}".format(
        base_finish_length, n, base_func_def, n, base_pure_prose, n, base_hallu, n))
    print("       avg {} chars, {} tokens".format(round(base_avg_chars, 1), round(base_avg_tok, 1)))
    print("SFT:   finish=stop  {}/{}, func_def {}/{}, pure_prose {}/{}, hallu {}/{}".format(
        sft_finish_stop, n, sft_func_def, n, sft_pure_prose, n, sft_hallu, n))
    print("       avg {} chars, {} tokens".format(round(sft_avg_chars, 1), round(sft_avg_tok, 1)))
    print("       correctness: {}/{} ({}%)".format(sft_correct, n, round(sft_correct / n * 100, 1)))
    print("         replication: {}/{}, new: {}/{}".format(
        repl_correct, len(repl_results), new_correct, len(new_results)))
    print("       errors: correct={} semantic={} api_misuse={} protocol={} incomplete={}".format(
        sft_correct, sft_semantic, sft_api_misuse, sft_protocol, sft_incomplete))
    print("Compression: {}x (chars), {}x (tokens)".format(
        summary["compression_ratio"], summary["token_efficiency"]))
    print("Reward arm projection:")
    print("  R1 binary mean  = {} (all-or-nothing)".format(summary["reward_arm_projection"]["R1_binary_mean"]))
    print("  R2 partial mean = {} (gradient)".format(summary["reward_arm_projection"]["R2_partial_mean"]))
    print("  R4 api-legality  = {} (catches API misuse)".format(summary["reward_arm_projection"]["R4_api_legality_mean"]))
    print("  R2-R1 gradient   = {} (RL signal R1 misses)".format(summary["reward_arm_projection"]["R2_vs_R1_gradient"]))
    print()
    print("Results saved to: {}".format(args.out))
    return 0


if __name__ == "__main__":
    sys.exit(main())
