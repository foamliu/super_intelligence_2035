#!/usr/bin/env python3
"""baize_posttrain_sglang_preflight.py — R50 SGLang + MiniCPM5-2B pre-flight static checks.

Zero-GPU checks runnable on 11/9 before launching training.
Usage: python3 baize_posttrain_sglang_preflight.py [--html] [--json]
"""
import sys, os, json, re, argparse

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = "/tmp/models/MiniCPM5-2B"
CONFIG_V2 = os.path.join(SCRIPT_DIR, "baize_posttrain_rl_verl_config_v2.yaml")
results = []

def check(name, status, detail=""):
    results.append((name, status, detail))
    print(f"  [{status}] {name}: {detail}")

def run_all():
    print("=" * 70)
    print("R50 SGLang + MiniCPM5-2B Pre-flight Static Checks")
    print("=" * 70)
    # 1. Model files
    print("\n[1] Model files")
    if not os.path.isdir(MODEL_PATH):
        check("model_dir", "FAIL", f"NOT FOUND: {MODEL_PATH}")
        return False
    check("model_dir", "PASS")
    for f in ["config.json", "model-00000-of-00001.safetensors", "tokenizer.json",
               "tokenizer_config.json", "chat_template.jinja"]:
        fp = os.path.join(MODEL_PATH, f)
        check(f"file_{f}", "PASS" if os.path.isfile(fp) else "FAIL",
              f"{os.path.getsize(fp)/1024/1024:.1f}MB" if os.path.isfile(fp) else "MISSING")
    # 2. Architecture
    print("\n[2] Architecture")
    try:
        with open(os.path.join(MODEL_PATH, "config.json")) as f:
            cfg = json.load(f)
        arch = cfg.get("architectures", [])
        check("arch_llama", "PASS" if "LlamaForCausalLM" in arch else "FAIL", str(arch))
        check("model_type", "PASS" if cfg.get("model_type") == "llama" else "FAIL",
              cfg.get("model_type", ""))
    except Exception as e:
        check("config_load", "FAIL", str(e))
    # 3. Tokenizer vocab
    print("\n[3] Tokenizer vocab")
    vocab_check = None
    import subprocess
    for venv_py in ["/home/app.e0031982/code/vllm_venv/bin/python3", sys.executable]:
        code = (
            f"from transformers import AutoTokenizer; "
            f"t=AutoTokenizer.from_pretrained('{MODEL_PATH}',trust_remote_code=True); "
            f"v=t.get_vocab(); import json; "
            f"tks=['<function','</function>','<|im_start|>','<|im_end|>',"
            f"'<param','</param>','<tools>','</tools>',"
            f"'<|python_tag|>','[TOOL_CALLS]','<|action_start|>']; "
            f"print(json.dumps({{t:t in v for t in tks}}))")
        r = subprocess.run([venv_py, "-c", code], capture_output=True, text=True, timeout=60)
        if r.returncode == 0:
            vocab_check = json.loads(r.stdout.strip().split("\n")[-1])
            check("tokenizer_load", "PASS")
            break
    if vocab_check is None:
        check("tokenizer_load", "FAIL", "No venv with transformers")
    else:
        for tok in ["<function", "</function>", "<|im_start|>", "<|im_end|>"]:
            check(f"vocab_{tok}", "PASS" if vocab_check.get(tok) else "FAIL", str(vocab_check.get(tok)))
        for tok in ["<|python_tag|>", "[TOOL_CALLS]", "<|action_start|>"]:
            check(f"vocab_NOT_{tok}", "PASS" if not vocab_check.get(tok) else "WARN", str(vocab_check.get(tok)))
    return True

def run_all_part2():
    # 4. SGLang function_call_parser
    print("\n[4] SGLang function_call_parser")
    try:
        from sglang.srt.function_call_parser import (
            FunctionCallParser, BaseFormatDetector,
            StreamingParseResult, ToolCallItem, StructureInfo,
        )
        check("sglang_import", "PASS")
        fields = list(ToolCallItem.model_fields.keys())
        check("tci_has_parameters", "PASS" if "parameters" in fields else "FAIL", str(fields))
        check("tci_no_arguments", "PASS" if "arguments" not in fields else "WARN", str(fields))
        enum_keys = list(FunctionCallParser.ToolCallParserEnum.keys())
        check("enum_builtins", "PASS", str(enum_keys))
    except Exception as e:
        check("sglang_import", "FAIL", str(e))
        return False
    # 5. Monkey-patch test
    print("\n[5] Monkey-patch test")
    try:
        class TestDetector(BaseFormatDetector):
            def __init__(self):
                super().__init__()
                self.bot_token = "<function"
                self.eot_token = "</function>"
            def has_tool_call(self, text):
                return "<function name=" in text
            def detect_and_parse(self, text, tools):
                return StreamingParseResult(normal_text=text, calls=[])
            def structure_info(self):
                return lambda name: StructureInfo(
                    begin=f'<function name="{name}">', end="</function>", trigger="<function")
        FunctionCallParser.ToolCallParserEnum["minicpm5"] = TestDetector
        check("patch_register", "PASS", "minicpm5 registered")
        tci = ToolCallItem(tool_index=0, name="test", parameters='{"k":"v"}')
        check("tci_construct_ok", "PASS", str(tci.parameters))
    except Exception as e:
        check("patch_register", "FAIL", str(e))
    # 6. verl import
    print("\n[6] verl import")
    try:
        from verl.trainer.main_ppo import main
        check("verl_import", "PASS")
    except Exception as e:
        check("verl_import", "FAIL", str(e))
    # 7. v2 config
    print("\n[7] v2 config YAML")
    try:
        import yaml
        with open(CONFIG_V2) as f:
            yc = yaml.safe_load(f)
        check("yaml_load", "PASS")
        r = yc.get("actor_rollout_ref", {}).get("rollout", {})
        for nm, ok in [
            ("custom_reward_top", "custom_reward_function" in yc),
            ("sglang", r.get("name") == "sglang"),
            ("grpo", yc.get("algorithm", {}).get("adv_estimator") == "grpo"),
            ("multi_turn_off", r.get("multi_turn", {}).get("enable") == False),
            ("n=8", r.get("n") == 8),
            ("4gpu", yc.get("trainer", {}).get("n_gpus_per_node") == 4),
        ]:
            check(f"cfg_{nm}", "PASS" if ok else "FAIL")
    except Exception as e:
        check("yaml_load", "FAIL", str(e))
    # Summary
    n_p = sum(1 for _, s, _ in results if s == "PASS")
    n_f = sum(1 for _, s, _ in results if s == "FAIL")
    n_w = sum(1 for _, s, _ in results if s == "WARN")
    print(f"\n{'='*70}")
    print(f"SUMMARY: {n_p} PASS / {n_f} FAIL / {n_w} WARN")
    print(f"OVERALL: {'GO' if n_f == 0 else 'NO-GO'}")
    print("=" * 70)
    return n_f == 0

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="R50 SGLang+MiniCPM5-2B pre-flight")
    parser.add_argument("--html", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    ok1 = run_all()
    ok2 = run_all_part2() if ok1 else False
    ok = ok1 and ok2
    if args.json:
        print(json.dumps([{"check": n, "status": s, "detail": d} for n, s, d in results],
                         ensure_ascii=False, indent=2))
    sys.exit(0 if ok else 1)
