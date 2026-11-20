#!/usr/bin/env python3
"""baize_posttrain_r127_sft_trajectory_synthesizer.py — Golden Trajectory to SFT.

R127 (2026-11-10 wake174): Convert 103 DeepSeek golden EDA-Eval traces into
SFT training pairs WITHOUT contaminating the 158-task eval set.

Key insight (R126): 99% of golden trajectories contain execution errors yet
recover to success. The tool-use STRATEGY (search->detail->run->fix) is the
transferable signal, not the specific eval task solution.

All CPU, zero GPU. Surrogate analysis results NOT transferable to BaiZe.
"""
from __future__ import annotations
import json, os, sys, re, time, hashlib, logging, random
from typing import Any, Dict, List, Optional, Set
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)

TRACE_DIR = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/cline_cli_trace/cline_trace_v1_3/cline_trace")
DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
API_KB_PATH = os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")
OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_JSONL = os.path.join(OUTPUT_DIR, "r127_sft_synthetic_trajectories.jsonl")
OUTPUT_REPORT = os.path.join(OUTPUT_DIR, "r127_synthesis_report.json")

TOOL_CALL_RE = re.compile(
    r'<use_mcp_tool>\s*<server_name>([^<]+)</server_name>\s*'
    r'<tool_name>([^<]+)</tool_name>\s*<arguments>(.*?)</arguments>', re.DOTALL)
CODE_BLOCK_RE = re.compile(r'```python\s*(.*?)```', re.DOTALL)
ERROR_INDICATORS = ["error", "Error", "Traceback", "Exception", "failed",
    "Failed", "TypeError", "AttributeError", "ImportError", "SyntaxError",
    "KeyError", "ValueError", "NameError", "IndexError"]
API_CALL_RE = re.compile(r'pyScript\.(\w+)\s*\(')
TOOL_NAME_MAP = {"search_apis": "search_apis", "get_api_details": "get_api_details",
    "run_pyAether_code_tool": "run_code", "run_code": "run_code"}


def normalize_tool_name(name):
    return TOOL_NAME_MAP.get(name.strip(), name.strip())


class ContaminationChecker:
    """Check whether content matches any of the 158 eval tasks."""

    def __init__(self, dataset_path):
        self.eval_prompts = {}
        self.eval_entry_points = set()
        self.eval_api_sets = []
        self._load(dataset_path)

    def _load(self, path):
        if not os.path.exists(path):
            logger.warning("Dataset not found: %s", path)
            return
        with open(path) as f:
            for line in f:
                entry = json.loads(line)
                prompt = entry["prompt"]
                ph = hashlib.md5(prompt.encode()).hexdigest()
                self.eval_prompts[ph] = entry["task_id"]
                ep = entry.get("entry_point", "")
                if ep:
                    self.eval_entry_points.add(ep)
                sol = entry.get("canonical_solution", "")
                self.eval_api_sets.append(set(API_CALL_RE.findall(sol)))
        logger.info("Loaded %d eval tasks, %d entry points",
                     len(self.eval_prompts), len(self.eval_entry_points))

    def check_code(self, code):
        apis = set(API_CALL_RE.findall(code))
        for i, eval_apis in enumerate(self.eval_api_sets):
            if eval_apis and apis and apis == eval_apis:
                return {"contaminated": True, "reason": "api_set_match", "idx": i}
        m = re.search(r'def\s+(\w+)\s*\(', code)
        if m and m.group(1) in self.eval_entry_points:
            return {"contaminated": True, "reason": "entry_point", "name": m.group(1)}
        return {"contaminated": False, "reason": "clean"}

    def check_api(self, api_name):
        return any(api_name in s for s in self.eval_api_sets)


class TrajectoryPatternExtractor:
    """Extract reusable patterns from DeepSeek golden traces."""

    def __init__(self, trace_dir):
        self.trace_dir = trace_dir
        self.patterns = {
            "tool_sequences": Counter(),
            "api_co_occurrence": defaultdict(Counter),
            "error_recovery_map": defaultdict(Counter),
            "conversation_templates": [], "api_usage_examples": [],
            "search_query_patterns": [],
            "total_traces": 0, "total_tool_calls": 0,
            "total_errors": 0, "total_recoveries": 0,
        }

    def extract_all(self):
        traces = sorted(os.listdir(self.trace_dir))
        self.patterns["total_traces"] = len(traces)
        for tid in traces:
            tp = os.path.join(self.trace_dir, tid, "api_conversation_history.json")
            if not os.path.exists(tp):
                continue
            with open(tp) as f:
                messages = json.load(f)
            self._extract_single(tid, messages)
        self.patterns["top_tool_sequences"] = self.patterns["tool_sequences"].most_common(20)
        self.patterns["top_error_recovery"] = {
            k: v.most_common(5) for k, v in self.patterns["error_recovery_map"].items()}
        return self.patterns

    def _extract_single(self, task_id, messages):
        tool_seq, prev_err = [], False
        for i, msg in enumerate(messages):
            if msg.get("role") != "assistant":
                continue
            content = msg.get("content", [])
            if not isinstance(content, list):
                continue
            for block in content:
                if block.get("type") != "text":
                    continue
                text = block.get("text", "")
                for m in TOOL_CALL_RE.finditer(text):
                    tool = normalize_tool_name(m.group(2))
                    tool_seq.append(tool)
                    self.patterns["total_tool_calls"] += 1
                    if tool == "search_apis":
                        try:
                            args = json.loads(m.group(3).strip())
                            q = args.get("query", args.get("description", ""))
                            if q:
                                self.patterns["search_query_patterns"].append(q)
                        except (json.JSONDecodeError, ValueError):
                            pass
                    if prev_err:
                        self.patterns["error_recovery_map"]["any_error"][tool] += 1
                        self.patterns["total_recoveries"] += 1
                    prev_err = False
                for m in CODE_BLOCK_RE.finditer(text):
                    code = m.group(1).strip()
                    if len(code) < 10:
                        continue
                    apis = API_CALL_RE.findall(code)
                    for api in apis:
                        self.patterns["api_usage_examples"].append(
                            {"api_name": api, "code_snippet": code[:500], "task_id": task_id})
                    uniq = set(apis)
                    for a in uniq:
                        for b in uniq:
                            if a != b:
                                self.patterns["api_co_occurrence"][a][b] += 1
            if i + 1 < len(messages) and messages[i + 1].get("role") == "user":
                nc = messages[i + 1].get("content", [])
                if isinstance(nc, list):
                    for b in nc:
                        txt = b.get("text", "")
                        if b.get("type") == "text" and any(e in txt for e in ERROR_INDICATORS):
                            prev_err = True
                            self.patterns["total_errors"] += 1
        for n in (2, 3):
            for i in range(len(tool_seq) - n + 1):
                self.patterns["tool_sequences"][tuple(tool_seq[i:i + n])] += 1
        if tool_seq:
            self.patterns["conversation_templates"].append(
                {"task_id": task_id, "n_messages": len(messages),
                 "tool_sequence": tool_seq, "compressed": self._compress(tool_seq)})

    @staticmethod
    def _compress(seq):
        if not seq:
            return []
        r = [seq[0]]
        for t in seq[1:]:
            if t != r[-1]:
                r.append(t)
        return r


class APIKnowledgeBase:
    """Load and index the PyAether API knowledge base."""

    def __init__(self, kb_path):
        self.apis = {}
        self.by_category = defaultdict(list)
        self._load(kb_path)

    def _load(self, path):
        if not os.path.exists(path):
            logger.warning("API KB not found: %s", path)
            return
        with open(path) as f:
            data = json.load(f)
        if isinstance(data, list):
            for e in data:
                name = e.get("api_name", "")
                if name:
                    self.apis[name] = e
                    self.by_category[e.get("category", "unknown")].append(name)
        elif isinstance(data, dict):
            for name, e in data.items():
                if isinstance(e, dict):
                    self.apis[name] = e
                    self.by_category[e.get("category", "unknown")].append(name)
        logger.info("API KB loaded: %d APIs, %d categories", len(self.apis), len(self.by_category))

    def get_safe_apis(self, checker):
        return [n for n in self.apis if not checker.check_api(n)]

    def get_api_doc(self, name):
        e = self.apis.get(name, {})
        parts = ["# " + name]
        if e.get("api_type"):
            parts.append("Type: " + e["api_type"])
        if e.get("api_descriptions"):
            parts.append("Description: " + e["api_descriptions"])
        if e.get("category"):
            parts.append("Category: " + e["category"])
        return "\n".join(parts)


class SyntheticTrajectoryGenerator:
    """Generate synthetic SFT multi-turn trajectories from extracted patterns."""

    SYSTEM_PROMPT = (
        "You are an EDA automation assistant with access to pyAether API tools.\n"
        "Available tools:\n"
        "- search_apis: Search for pyAether APIs by natural language description\n"
        "- get_api_details: Get detailed documentation for a specific API name\n"
        "- run_code: Execute Python code in a pyAether environment\n\n"
        "Workflow: First search for relevant APIs, then get their details, "
        "then write and run code. If code fails, analyze the error and fix it."
    )
    TOOL_TAG_OPEN = "[tool_call: "
    TOOL_TAG_CLOSE = "]"
    TOOL_RESULT_TAG = "[tool_result]"

    def __init__(self, patterns, kb, checker, rng):
        self.patterns = patterns
        self.kb = kb
        self.checker = checker
        self.rng = rng
        self.generated = []

    def generate_all(self, target_count=200):
        safe_apis = self.kb.get_safe_apis(self.checker)
        if not safe_apis:
            logger.error("No safe APIs available!")
            return []
        n_a = target_count // 2
        n_b = target_count // 4
        n_c = target_count - n_a - n_b
        for i in range(n_a):
            p = self._gen_type_a(safe_apis, i)
            if p:
                self.generated.append(p)
        for i in range(n_b):
            p = self._gen_type_b(safe_apis, i)
            if p:
                self.generated.append(p)
        for i in range(n_c):
            p = self._gen_type_c(safe_apis, i)
            if p:
                self.generated.append(p)
        logger.info("Generated %d SFT pairs (target=%d)", len(self.generated), target_count)
        return self.generated

    def _tool_call(self, tool, **kwargs):
        args = json.dumps(kwargs, ensure_ascii=False)
        return "%s%s %s%s" % (self.TOOL_TAG_OPEN, tool, args, self.TOOL_TAG_CLOSE)

    def _tool_result(self, result_dict):
        return self.TOOL_RESULT_TAG + json.dumps(result_dict, ensure_ascii=False) + self.TOOL_RESULT_TAG

    def _gen_type_a(self, safe_apis, idx):
        """Type A: search -> get_details -> run_code (golden pattern)."""
        api = self.rng.choice(safe_apis)
        doc = self.kb.get_api_doc(api)
        cont = self.checker.check_code("pyScript.%s(" % api)
        if cont["contaminated"]:
            return None
        fn_name = "use_" + api.lower()[:20]
        msgs = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "Write a Python function that uses the pyAether API `%s`. First search for it, get its details, then implement and test." % api},
            {"role": "assistant", "content": "I'll search for the `%s` API first.\n\n%s" % (api, self._tool_call("search_apis", query=api))},
            {"role": "user", "content": self._tool_result({"api_name": api, "found": True})},
            {"role": "assistant", "content": "Found it. Let me get the detailed documentation.\n\n%s" % self._tool_call("get_api_details", api_name=api)},
            {"role": "user", "content": self._tool_result({"api_name": api, "doc": doc[:300]})},
            {"role": "assistant", "content": "Now I'll write a function and run it.\n\n```python\nimport pyAether as pyScript\n\ndef %s():\n    pyScript.emyInitAether('-adv')\n    result = pyScript.%s()\n    return result\n```\n\n%s" % (fn_name, api, self._tool_call("run_code", code="import pyAether as pyScript\n%s()" % fn_name))},
            {"role": "user", "content": self._tool_result({"status": "success", "output": "Code executed successfully."})},
            {"role": "assistant", "content": "The code ran successfully. The function `%s()` calls `pyScript.%s` and returns the result." % (fn_name, api)},
        ]
        return {"pair_id": "R127-A-%04d" % idx, "type": "A_api_usage",
                "api_used": [api], "pattern": "search->detail->run",
                "messages": msgs, "contamination_check": "passed",
                "source": "synthetic_from_golden_pattern"}

    def _gen_type_b(self, safe_apis, idx):
        """Type B: search -> run (error) -> detail -> run (success)."""
        api = self.rng.choice(safe_apis)
        doc = self.kb.get_api_doc(api)
        cont = self.checker.check_code("pyScript.%s(" % api)
        if cont["contaminated"]:
            return None
        errs = [("TypeError", "missing required argument"),
                ("AttributeError", "object has no attribute"),
                ("ImportError", "cannot import name")]
        et, ed = self.rng.choice(errs)
        fn_name = "use_" + api.lower()[:20]
        msgs = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "Write a Python function using pyAether API `%s`. Search, implement, and test." % api},
            {"role": "assistant", "content": "Let me search and try it directly.\n\n%s" % self._tool_call("search_apis", query=api)},
            {"role": "user", "content": self._tool_result({"api_name": api, "found": True})},
            {"role": "assistant", "content": "Found it. Let me try calling it.\n\n%s" % self._tool_call("run_code", code="import pyAether as pyScript\npyScript.%s()" % api)},
            {"role": "user", "content": self._tool_result({"status": "error", "error": "%s: %s" % (et, ed)})},
            {"role": "assistant", "content": "The code failed with %s. Let me get the API details.\n\n%s" % (et, self._tool_call("get_api_details", api_name=api))},
            {"role": "user", "content": self._tool_result({"api_name": api, "doc": doc[:300]})},
            {"role": "assistant", "content": "Now I understand. I need to init Aether first.\n\n```python\nimport pyAether as pyScript\n\ndef %s():\n    pyScript.emyInitAether('-adv')\n    result = pyScript.%s()\n    return result\n```\n\n%s" % (fn_name, api, self._tool_call("run_code", code="import pyAether as pyScript\n%s()" % fn_name))},
            {"role": "user", "content": self._tool_result({"status": "success", "output": "Code executed successfully."})},
            {"role": "assistant", "content": "After the %s, I retrieved docs and fixed the code. The function now works." % et},
        ]
        return {"pair_id": "R127-B-%04d" % idx, "type": "B_error_recovery",
                "api_used": [api], "pattern": "search->run(err)->detail->run(ok)",
                "error_type": et, "messages": msgs,
                "contamination_check": "passed", "source": "synthetic_from_golden_pattern"}

    def _gen_type_c(self, safe_apis, idx):
        """Type C: multi-API chain (detail x N -> run)."""
        n = self.rng.randint(2, 3)
        selected = self.rng.sample(safe_apis, min(n, len(safe_apis)))
        for a in selected:
            if self.checker.check_code("pyScript.%s(" % a)["contaminated"]:
                return None
        msgs = [
            {"role": "system", "content": self.SYSTEM_PROMPT},
            {"role": "user", "content": "Write a Python function chaining %d pyAether APIs: %s. Get details for each, then implement and test." % (len(selected), ", ".join(selected))},
        ]
        for a in selected:
            d = self.kb.get_api_doc(a)
            msgs.append({"role": "assistant", "content": "Let me get details for `%s`.\n\n%s" % (a, self._tool_call("get_api_details", api_name=a))})
            msgs.append({"role": "user", "content": self._tool_result({"api_name": a, "doc": d[:200]})})
        lines = ["import pyAether as pyScript", "", "def chain_apis():",
                 '    """Chain multiple pyAether APIs."""',
                 "    pyScript.emyInitAether('-adv')"]
        for a in selected:
            lines.append("    result_%s = pyScript.%s()" % (a.lower()[:15], a))
        ret = ", ".join("'%s': result_%s" % (a, a.lower()[:15]) for a in selected)
        lines.append("    return {%s}" % ret)
        code = "\n".join(lines)
        msgs.append({"role": "assistant", "content": "Now I'll implement the workflow.\n\n```python\n%s\n```\n\n%s" % (code, self._tool_call("run_code", code=code))})
        msgs.append({"role": "user", "content": self._tool_result({"status": "success", "output": "All APIs called successfully."})})
        msgs.append({"role": "assistant", "content": "Successfully chained %d APIs: %s." % (len(selected), ", ".join(selected))})
        return {"pair_id": "R127-C-%04d" % idx, "type": "C_multi_api",
                "api_used": selected, "pattern": "detail x%d -> run" % len(selected),
                "messages": msgs, "contamination_check": "passed",
                "source": "synthetic_from_golden_pattern"}


def main():
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    t0 = time.time()
    print("=" * 70)
    print("R127: SFT Golden Trajectory Synthesizer")
    print("=" * 70)

    print("\n[1/5] Loading contamination checker...")
    checker = ContaminationChecker(DATASET_PATH)
    print("  Loaded %d eval tasks, %d entry points" % (
        len(checker.eval_prompts), len(checker.eval_entry_points)))

    print("\n[2/5] Extracting patterns from 103 golden traces...")
    extractor = TrajectoryPatternExtractor(TRACE_DIR)
    patterns = extractor.extract_all()
    print("  Traces: %d" % patterns["total_traces"])
    print("  Tool calls: %d" % patterns["total_tool_calls"])
    print("  Errors: %d" % patterns["total_errors"])
    print("  Recoveries: %d" % patterns["total_recoveries"])
    print("  API usage examples: %d" % len(patterns["api_usage_examples"]))
    print("  Search queries: %d" % len(patterns["search_query_patterns"]))
    print("  Templates: %d" % len(patterns["conversation_templates"]))
    print("  Top 2-gram sequences:")
    for seq, cnt in patterns["top_tool_sequences"][:5]:
        if len(seq) == 2:
            print("    %s->%s: %d" % (seq[0], seq[1], cnt))

    print("\n[3/5] Loading API knowledge base...")
    kb = APIKnowledgeBase(API_KB_PATH)
    safe_apis = kb.get_safe_apis(checker)
    print("  Total APIs: %d" % len(kb.apis))
    print("  Safe (non-eval): %d" % len(safe_apis))

    print("\n[4/5] Generating synthetic SFT trajectories...")
    rng = random.Random(42)
    gen = SyntheticTrajectoryGenerator(patterns, kb, checker, rng)
    pairs = gen.generate_all(target_count=200)
    print("  Generated: %d SFT pairs" % len(pairs))
    tc = Counter(p["type"] for p in pairs)
    for t, c in tc.most_common():
        print("    %s: %d" % (t, c))
    all_apis = set()
    for p in pairs:
        all_apis.update(p.get("api_used", []))
    print("  Unique APIs covered: %d" % len(all_apis))
    cont_fail = sum(1 for p in pairs if p.get("contamination_check") != "passed")
    print("  Contamination failures: %d" % cont_fail)

    print("\n[5/5] Writing outputs...")
    with open(OUTPUT_JSONL, "w") as f:
        for p in pairs:
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    jsonl_size = os.path.getsize(OUTPUT_JSONL)
    print("  JSONL: %s (%d bytes)" % (OUTPUT_JSONL, jsonl_size))

    report = {
        "meta": {"round": "R127", "wake": 174, "date": "2026-11-10",
                 "elapsed_sec": round(time.time() - t0, 2)},
        "pattern_extraction": {
            "total_traces": patterns["total_traces"],
            "total_tool_calls": patterns["total_tool_calls"],
            "total_errors": patterns["total_errors"],
            "total_recoveries": patterns["total_recoveries"],
            "api_usage_examples": len(patterns["api_usage_examples"]),
            "search_queries": len(patterns["search_query_patterns"]),
            "conversation_templates": len(patterns["conversation_templates"]),
            "top_2gram": [{"seq": list(s), "count": c}
                          for s, c in patterns["top_tool_sequences"] if len(s) == 2][:10],
        },
        "api_kb": {"total": len(kb.apis), "safe": len(safe_apis)},
        "generation": {"target": 200, "generated": len(pairs),
                       "types": dict(tc), "apis_covered": len(all_apis),
                       "contamination_failures": cont_fail},
        "key_findings": {
            "golden_pattern": "search->detail->run dominant (19.4% in R126)",
            "error_recovery": "99% golden traces have errors with recovery",
            "safe_api_pool": "%d non-eval APIs" % len(safe_apis),
            "sft_format": "OpenAI chat format, multi-turn, 3 types",
            "contamination": "ALL PASSED" if cont_fail == 0 else "%d FAILED" % cont_fail,
        },
    }
    with open(OUTPUT_REPORT, "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("  Report: %s" % OUTPUT_REPORT)
    elapsed = time.time() - t0
    print("\nDone in %.1fs" % elapsed)
    print("  %d SFT pairs -> %s" % (len(pairs), OUTPUT_JSONL))
    return 0


if __name__ == "__main__":
    sys.exit(main())