#!/usr/bin/env python3
"""baize_posttrain_r125_rollout_simulator.py — CPU-Based Multi-Turn Rollout Simulator.

R125 (2026-11-10 wake172): Full end-to-end pipeline validation for verl GRPO
multi-turn tool-calling RL.  Exercises the complete flow:

  1. Load real EDA-Eval-PyAether tasks (158 available)
  2. Simulate model responses at 5 quality levels (excellent/good/mediocre/bad/cheating)
  3. Execute actual v3 EDA tools (search_apis -> get_api_details -> run_code)
  4. Calculate R0++ reward on final responses
  5. Validate multi-turn conversation structure matches verl expectations
  6. Test reward hacking / cheat resistance
  7. Produce reward distribution analysis (variance -> GRPO learnability)

All CPU, zero GPU.  Validates that the entire R1-R124 tooling stack is
integration-correct before GPU becomes available.

Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import json, os, sys, time, re, logging, random
from typing import Any, Dict, List, Optional, Tuple
from collections import defaultdict

logger = logging.getLogger(__name__)
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

DATASET_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/pyAether-eval/original_dataset/EDA-Eval-PyAether-v20260311.jsonl")
API_DB_PATH = os.path.expanduser(
    "~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json")


# =============================================================================
#  1. Task Loader
# =============================================================================
class TaskLoader:
    """Load EDA-Eval-PyAether tasks from JSONL."""

    def __init__(self, path: str = DATASET_PATH):
        self.path = path
        self.tasks: List[Dict[str, Any]] = []
        if not os.path.exists(path):
            logger.warning("Dataset not found: %s", path)
            return
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    self.tasks.append(json.loads(line))
        logger.info("Loaded %d tasks from %s", len(self.tasks), path)

    def get_task(self, idx: int) -> Optional[Dict[str, Any]]:
        if 0 <= idx < len(self.tasks):
            return self.tasks[idx]
        return None

    def sample(self, n: int, seed: int = 42) -> List[Dict[str, Any]]:
        rng = random.Random(seed)
        indices = rng.sample(range(len(self.tasks)), min(n, len(self.tasks)))
        return [self.tasks[i] for i in sorted(indices)]


# =============================================================================
#  2. Mock Model — simulates model responses at different quality levels
# =============================================================================
class MockModel:
    """Generate simulated model responses at 5 quality levels.

    Since we cannot run MiniCPM5-2B without GPU, we simulate the *structure*
    of multi-turn tool-calling trajectories that a model would produce.
    Each quality level produces a different response pattern that exercises
    different parts of the R0++ reward function.
    """

    LEVELS = ["excellent", "good", "mediocre", "bad", "cheating"]

    def __init__(self, api_db_path: str = API_DB_PATH):
        self.api_db_path = api_db_path
        self._api_names: Optional[List[str]] = None

    @property
    def api_names(self) -> List[str]:
        if self._api_names is None:
            with open(self.api_db_path, "r") as f:
                data = json.load(f)
            if isinstance(data, dict):
                self._api_names = list(data.keys())
            elif isinstance(data, list):
                self._api_names = [a["api_name"] for a in data
                                   if isinstance(a, dict) and "api_name" in a]
            else:
                self._api_names = []
        return self._api_names

    def _pick_random_api(self, rng: random.Random) -> str:
        return rng.choice(self.api_names)

    def _extract_sig(self, prompt: str, entry_point: str) -> str:
        """Extract parameter list from prompt's function signature."""
        sig_match = re.search(
            r'def\s+' + re.escape(entry_point) + r'\s*\(([^)]*)\)', prompt)
        if sig_match:
            return sig_match.group(1)
        return ""

    def generate_response(self, task: Dict[str, Any], level: str,
                          rng: random.Random) -> Dict[str, Any]:
        """Simulate a multi-turn tool-calling trajectory."""
        meta = task.get("metadata", {})
        apis_used = meta.get("apis_used", [])
        entry_point = task.get("entry_point", "solve")
        canonical = task.get("canonical_solution", "")
        prompt = task.get("prompt", "")
        apis_short = [a.replace("pyAether.", "") if a.startswith("pyAether.") else a
                      for a in apis_used]

        turns: List[Tuple[str, str]] = []
        tool_calls: List[Dict[str, Any]] = []
        final_code = ""

        if level == "excellent":
            # Full tool-calling: search -> get_details -> code
            if apis_short:
                sq = apis_short[0].split(".")[0] if "." in apis_short[0] else apis_short[0]
                turns.append(("assistant", f"I'll search for the relevant API first."))
                tool_calls.append({"name": "search_apis", "args": {"query": sq}, "result": "found"})
                turns.append(("tool", json.dumps({"results": [{"api_name": apis_short[0]}]})))
                turns.append(("assistant", f"Let me get details for {apis_short[0]}."))
                tool_calls.append({"name": "get_api_details", "args": {"api_names": apis_short[:2]}, "result": "found"})
                turns.append(("tool", json.dumps({"results": [{"api_name": apis_short[0]}]})))
            final_code = f"```python\nimport pyAether as pyScript\n\ndef {entry_point}({self._extract_sig(prompt, entry_point)}):\n"
            final_code += (canonical if canonical else "    return None\n") + "```"

        elif level == "good":
            # Correct APIs but no import, minor issues
            final_code = f"```python\ndef {entry_point}({self._extract_sig(prompt, entry_point)}):\n"
            final_code += (canonical if canonical else "    return None\n") + "```"
            if apis_short:
                tool_calls.append({"name": "search_apis", "args": {"query": apis_short[0]}, "result": "found"})

        elif level == "mediocre":
            # Some correct APIs + wrong API, missing entry_point
            final_code = f"```python\nimport pyAether as pyScript\n\ndef {entry_point}():\n"
            if apis_short:
                wrong_api = self._pick_random_api(rng)
                final_code += f"    result = pyScript.{apis_short[0]}()\n    pyScript.{wrong_api}()\n    return result\n```"
            else:
                final_code += "    return None\n```"
            tool_calls.append({"name": "search_apis", "args": {"query": "completely unrelated"}, "result": "empty"})

        elif level == "bad":
            # Syntax errors, no API usage, no tool calls
            final_code = "```python\ndef solve(\n    return None\n```"

        elif level == "cheating":
            # Reward hacking: embed test assertions, copy canonical
            final_code = f"```python\nimport pyAether as pyScript\n\ndef {entry_point}():\n    # Embedded test to game reward\n    assert True\n"
            final_code += (canonical if canonical else "    return None\n") + "```"
            tool_calls.append({"name": "search_apis", "args": {"query": "test answer"}, "result": "found"})

        turns.append(("assistant", final_code))
        return {"turns": turns, "final_code": final_code,
                "tool_calls": tool_calls, "solution_str": final_code}


# =============================================================================
#  3. Reward Calculator — wraps the real R0++ reward function
# =============================================================================
class RewardCalculator:
    """Compute R0++ reward using the real reward_functions.py."""

    def __init__(self, api_db_path: str = API_DB_PATH):
        self.api_db_path = api_db_path
        from baize_posttrain_reward_functions import compute_score, reward_r0_skeleton
        self.compute_score = compute_score
        self.reward_r0_skeleton = reward_r0_skeleton

    def compute(self, task: Dict[str, Any], solution_str: str,
                arm: str = "R0") -> Tuple[float, Dict[str, Any]]:
        """Compute reward for a task/response pair."""
        meta = task.get("metadata", {})
        extra_info = {
            "test_code": task.get("test", ""),
            "canonical_solution": task.get("canonical_solution", ""),
            "entry_point": task.get("entry_point", ""),
            "metadata": json.dumps(meta),
        }
        try:
            score = self.compute_score(
                data_source="pyaether_synth_v2",
                solution_str=solution_str,
                ground_truth=task.get("test", ""),
                extra_info=extra_info, arm=arm,
                api_database=self.api_db_path, auto_fallback=True)
        except Exception as e:
            logger.error("Reward computation failed: %s", e)
            score = 0.0
        try:
            r0_score = self.reward_r0_skeleton(
                solution_str=solution_str, extra_info=extra_info,
                api_db_path=self.api_db_path)
        except Exception:
            r0_score = score
        return float(score), {"compute_score": float(score),
                              "r0_skeleton": float(r0_score), "arm": arm}


# =============================================================================
#  4. Verl Conversation Structure Validator
# =============================================================================
class ConversationValidator:
    """Validate that simulated conversation matches verl multi-turn format."""

    @staticmethod
    def validate_verl_format(rollout: Dict[str, Any]) -> Dict[str, Any]:
        turns = rollout.get("turns", [])
        checks = {}
        checks["has_turns"] = len(turns) > 0
        checks["has_assistant_turn"] = any(r == "assistant" for r, _ in turns)
        sol = rollout.get("solution_str", "")
        checks["solution_str_nonempty"] = bool(sol) and isinstance(sol, str)
        checks["has_code_block"] = "```" in sol
        checks["final_turn_is_assistant"] = turns[-1][0] == "assistant" if turns else False
        tool_calls = rollout.get("tool_calls", [])
        checks["tool_calls_is_list"] = isinstance(tool_calls, list)
        checks["tool_calls_valid"] = all(isinstance(tc, dict) and "name" in tc
                                          for tc in tool_calls) if tool_calls else True
        checks["no_empty_content"] = all(bool(c.strip()) for _, c in turns) if turns else False
        return {"all_pass": all(checks.values()), "checks": checks}


# =============================================================================
#  5. Reward Distribution Analyzer
# =============================================================================
class RewardDistributionAnalyzer:
    """Analyze reward distribution across quality levels.

    Key question: Does R0++ produce enough variance for GRPO to learn?
    GRPO needs within-group variance (advantage != 0) to produce gradients.
    """

    @staticmethod
    def analyze(rewards_by_level: Dict[str, List[float]]) -> Dict[str, Any]:
        results = {}
        for level, scores in rewards_by_level.items():
            if not scores:
                results[level] = {"count": 0}
                continue
            n = len(scores)
            mean = sum(scores) / n
            std = (sum((s - mean) ** 2 for s in scores) / n) ** 0.5 if n > 1 else 0.0
            results[level] = {"count": n, "mean": round(mean, 4),
                              "min": round(min(scores), 4),
                              "max": round(max(scores), 4), "std": round(std, 4)}

        # GRPO learnability: simulate groups of 8 (G=8)
        grpo_check = RewardDistributionAnalyzer._grpo_variance_check(rewards_by_level)
        results["grpo_learnability"] = grpo_check

        # Separation: can reward distinguish quality levels?
        levels_order = ["excellent", "good", "mediocre", "bad", "cheating"]
        means = [(lv, results[lv]["mean"]) for lv in levels_order
                 if lv in results and "mean" in results[lv]]
        separation = all(means[i][1] > means[i + 1][1] for i in range(len(means) - 1))
        results["quality_separation"] = {"monotonic_decreasing": separation, "ordered_means": means}
        return results

    @staticmethod
    def _grpo_variance_check(rewards_by_level: Dict[str, List[float]]) -> Dict[str, Any]:
        all_scores = []
        for scores in rewards_by_level.values():
            all_scores.extend(scores)
        if len(all_scores) < 8:
            return {"error": "Not enough samples for G=8"}
        rng = random.Random(42)
        group_variances = []
        groups_with_signal = 0
        n_groups = 20
        for _ in range(n_groups):
            group = rng.sample(all_scores, min(8, len(all_scores)))
            g_mean = sum(group) / len(group)
            advantages = [s - g_mean for s in group]
            var = sum(a ** 2 for a in advantages) / len(advantages)
            group_variances.append(var)
            if var > 0.01:
                groups_with_signal += 1
        return {
            "n_groups_simulated": n_groups, "groups_with_signal": groups_with_signal,
            "signal_rate": round(groups_with_signal / n_groups, 4),
            "mean_group_variance": round(sum(group_variances) / len(group_variances), 6),
            "min_group_variance": round(min(group_variances), 6),
            "max_group_variance": round(max(group_variances), 6),
            "verdict": "LEARNABLE" if groups_with_signal / n_groups > 0.5 else "INSUFFICIENT_VARIANCE",
        }


# =============================================================================
#  6. Cheat Resistance Tester
# =============================================================================
class CheatResistanceTester:
    """Test that the R0++ reward is resistant to reward hacking."""

    @staticmethod
    def run_tests(reward_calc: 'RewardCalculator',
                  task: Dict[str, Any]) -> Dict[str, Any]:
        results = {}
        meta = task.get("metadata", {})
        apis_used = meta.get("apis_used", ["pyAether.test"])
        entry_point = task.get("entry_point", "solve")
        canonical = task.get("canonical_solution", "    return None")
        test_code = task.get("test", "")
        extra_info = {"test_code": test_code, "canonical_solution": canonical,
                      "entry_point": entry_point, "metadata": json.dumps(meta)}

        def _score(sol):
            return reward_calc.compute_score(
                "pyaether_synth_v2", sol, test_code, extra_info,
                arm="R0", api_database=reward_calc.api_db_path, auto_fallback=True)

        # Scenario 1: Embedded test assertions
        results["embedded_test"] = _score(
            "```python\nassert True\nassert candidate() is not None\n```")
        # Scenario 2: API-name stuffing (no structure)
        api_list = " ".join(apis_used[:10])
        results["api_stuffing"] = _score(
            f"```python\nimport pyAether as pyScript\n# {api_list}\n```\n")
        # Scenario 3: Canonical solution copy
        results["canonical_copy"] = _score(
            f"```python\nimport pyAether as pyScript\n\ndef {entry_point}():\n{canonical}\n```")
        # Scenario 4: Empty code block
        results["empty_code"] = _score("```\n```")
        # Scenario 5: Gibberish with code markers
        results["gibberish"] = _score("```python\nasdfjkl pyScript.emyDesign asdf\n```")
        # Scenario 6: Format-only (no code)
        results["format_only"] = _score("**Solution:** Use the API correctly.")
        # Legitimate good response
        results["legitimate_good"] = _score(
            f"```python\nimport pyAether as pyScript\n\ndef {entry_point}():\n{canonical}\n```")
        # Anti-gaming cap: all syntax errors -> cap 0.3
        results["syntax_err_cap"] = _score("```python\ndef broken(\n    return\n```")

        cheat_scores = [results["embedded_test"], results["api_stuffing"],
                        results["empty_code"], results["gibberish"], results["format_only"]]
        good_score = results["legitimate_good"]
        max_cheat = max(cheat_scores)
        results["verdict"] = {
            "max_cheat_score": round(max_cheat, 4),
            "legitimate_good_score": round(good_score, 4),
            "cheat_below_good": max_cheat < good_score,
            "anti_gaming_cap_works": results["syntax_err_cap"] <= 0.3,
            "overall": "RESISTANT" if (max_cheat < good_score and
                                       results["syntax_err_cap"] <= 0.3) else "VULNERABLE",
        }
        return results


# =============================================================================
#  7. Pipeline Runner — orchestrates the full simulation
# =============================================================================
class PipelineRunner:
    """Run the full end-to-end pipeline simulation."""

    def __init__(self, n_tasks: int = 20, seed: int = 42):
        self.n_tasks = n_tasks
        self.seed = seed
        self.task_loader = TaskLoader()
        self.mock_model = MockModel()
        self.reward_calc = RewardCalculator()
        self.validator = ConversationValidator()
        self.dist_analyzer = RewardDistributionAnalyzer()
        self.cheat_tester = CheatResistanceTester()

    def run(self) -> Dict[str, Any]:
        t0 = time.time()
        results: Dict[str, Any] = {
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "n_tasks": self.n_tasks, "seed": self.seed}
        tasks = self.task_loader.sample(self.n_tasks, seed=self.seed)
        if not tasks:
            results["error"] = "No tasks loaded"
            return results
        results["tasks_loaded"] = len(tasks)

        # Phase 1: Reward distribution across quality levels
        rng = random.Random(self.seed)
        rewards_by_level: Dict[str, List[float]] = {lv: [] for lv in MockModel.LEVELS}
        validation_results = {"pass": 0, "fail": 0, "details": []}
        for task in tasks:
            for level in MockModel.LEVELS:
                rollout = self.mock_model.generate_response(task, level, rng)
                score, _ = self.reward_calc.compute(task, rollout["solution_str"])
                rewards_by_level[level].append(score)
                v = self.validator.validate_verl_format(rollout)
                if v["all_pass"]:
                    validation_results["pass"] += 1
                else:
                    validation_results["fail"] += 1
                    validation_results["details"].append({
                        "task_id": task.get("task_id", "?"), "level": level,
                        "failed_checks": [k for k, v2 in v["checks"].items() if not v2]})
        results["reward_distribution"] = self.dist_analyzer.analyze(rewards_by_level)
        results["validation"] = validation_results

        # Phase 2: Cheat resistance (first 5 tasks)
        cheat_results = []
        for task in tasks[:5]:
            cr = self.cheat_tester.run_tests(self.reward_calc, task)
            cheat_results.append({
                "task_id": task.get("task_id", "?"),
                "scenario": task.get("metadata", {}).get("scenario", "?"),
                "results": cr})
        results["cheat_resistance"] = cheat_results

        # Phase 3: Per-scenario reward breakdown
        rng2 = random.Random(self.seed + 1)
        scenario_rewards: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: defaultdict(list))
        for task in tasks:
            scenario = task.get("metadata", {}).get("scenario", "Unknown")
            for level in MockModel.LEVELS:
                rollout = self.mock_model.generate_response(task, level, rng2)
                score, _ = self.reward_calc.compute(task, rollout["solution_str"])
                scenario_rewards[scenario][level].append(score)
        scenario_summary = {}
        for sc, lv_scores in scenario_rewards.items():
            scenario_summary[sc] = {
                lv: {"mean": round(sum(s) / len(s), 4) if s else 0, "count": len(s)}
                for lv, s in lv_scores.items()}
        results["per_scenario"] = scenario_summary

        # Phase 4: Tool execution validation
        results["tool_execution"] = self._validate_tool_execution(tasks[0])

        # Summary
        results["elapsed_seconds"] = round(time.time() - t0, 2)
        results["summary"] = self._generate_summary(results)
        return results

    def _validate_tool_execution(self, task: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate that v3 tools actually execute correctly on a real task."""
        if not task:
            return {"error": "No task provided"}
        results = {}
        meta = task.get("metadata", {})
        apis_used = meta.get("apis_used", [])
        apis_short = [a.replace("pyAether.", "") for a in apis_used]
        try:
            from baize_posttrain_r122_local_api_search import LocalAPISearch
            searcher = LocalAPISearch(api_info_path=API_DB_PATH)
            query = apis_short[0].split(".")[0] if apis_short and "." in apis_short[0] else (
                apis_short[0] if apis_short else "design")
            t1 = time.time()
            sr = searcher.search_apis(query, top_k=5)
            results["search_apis"] = {"query": query, "n_results": len(sr),
                "elapsed_ms": round((time.time() - t1) * 1000, 2),
                "first_result": sr[0]["api_name"] if sr else None}
            if apis_short:
                t2 = time.time()
                details_list = searcher.get_api_details([apis_short[0]])
                details = details_list[0] if details_list else {}
                results["get_api_details"] = {"api_name": apis_short[0],
                    "found": details.get("api_type", "unknown") != "unknown",
                    "api_type": details.get("api_type", "unknown"),
                    "elapsed_ms": round((time.time() - t2) * 1000, 2)}
            kw = apis_short[0] if apis_short else "emyDesign"
            t3 = time.time()
            kr = searcher.search_apis_by_keyword(kw, top_k=3)
            results["search_by_keyword"] = {"keyword": kw, "n_results": len(kr),
                "elapsed_ms": round((time.time() - t3) * 1000, 2)}
            try:
                import yaml
                with open(os.path.join(HERE, "baize_posttrain_tool_config_v3.yaml")) as f:
                    tc = yaml.safe_load(f)
                from baize_posttrain_eda_tool_v3 import EDARunCodeTool
                rc_schema = next((t for t in tc.get("tools", []) if t.get("name") == "run_code"), None)
                if rc_schema:
                    tool = EDARunCodeTool(config={"sandbox_tier": 3}, tool_schema=rc_schema)
                    test_code = "import pyAether as pyScript\n"
                    if apis_short:
                        test_code += f"result = pyScript.{apis_short[0]}()\n"
                    test_code += "print(result)"
                    inst_id = tool.create({"code": test_code})
                    resp, reward, meta_out = tool.execute(inst_id, {"code": test_code})
                    results["run_code_static"] = {
                        "syntax_ok": meta_out.get("syntax_ok", False),
                        "apis_called": meta_out.get("apis_called", []),
                        "apis_verified": meta_out.get("apis_verified", []),
                        "api_legality": meta_out.get("api_legality", 0.0),
                        "response_length": len(resp)}
                    tool.release(inst_id)
            except Exception as e:
                results["run_code_static"] = {"error": str(e)}
        except Exception as e:
            results["error"] = str(e)
        results["all_tools_valid"] = all(
            "error" not in v for v in results.values() if isinstance(v, dict))
        return results

    def _generate_summary(self, results: Dict[str, Any]) -> Dict[str, Any]:
        rd = results.get("reward_distribution", {})
        grpo = rd.get("grpo_learnability", {})
        sep = rd.get("quality_separation", {})
        val = results.get("validation", {})
        cheat = results.get("cheat_resistance", [])
        cheat_ok = sum(1 for c in cheat
                       if c.get("results", {}).get("verdict", {}).get("overall") == "RESISTANT")
        total_val = val.get("pass", 0) + val.get("fail", 0)
        checks = [
            grpo.get("verdict") == "LEARNABLE",
            sep.get("monotonic_decreasing", False),
            val.get("pass", 0) > val.get("fail", 0),
            cheat_ok >= len(cheat) * 0.8 if cheat else True]
        n_pass = sum(checks)
        verdict = ("READY_FOR_GPU" if n_pass == 4 else "MOSTLY_READY" if n_pass >= 3
                   else "NEEDS_FIXES" if n_pass >= 2 else "NOT_READY")
        return {
            "tasks_tested": results.get("tasks_loaded", 0),
            "quality_levels": MockModel.LEVELS,
            "grpo_learnable": grpo.get("verdict", "UNKNOWN"),
            "grpo_signal_rate": grpo.get("signal_rate", 0),
            "quality_separation_monotonic": sep.get("monotonic_decreasing", False),
            "validation_pass_rate": round(val.get("pass", 0) / max(1, total_val), 4),
            "cheat_resistance_rate": round(cheat_ok / max(1, len(cheat)), 4),
            "tool_execution_valid": results.get("tool_execution", {}).get("all_tools_valid", False),
            "elapsed_seconds": results.get("elapsed_seconds", 0),
            "overall_verdict": verdict}


# =============================================================================
#  Main
# =============================================================================
def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="R125: CPU-Based Multi-Turn Rollout Simulator")
    parser.add_argument("--n-tasks", type=int, default=20,
                        help="Number of tasks to simulate (default 20)")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="", help="Output JSON path (default stdout)")
    parser.add_argument("--verbose", "-v", action="store_true")
    args = parser.parse_args()
    level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=level, format="%(levelname)s: %(message)s")
    runner = PipelineRunner(n_tasks=args.n_tasks, seed=args.seed)
    results = runner.run()
    output = json.dumps(results, indent=2, ensure_ascii=False, default=str)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Results written to {args.output}")
    else:
        print(output)
    summary = results.get("summary", {})
    print("\n" + "=" * 60)
    print("R125 ROLLOUT SIMULATOR SUMMARY")
    print("=" * 60)
    for k, v in summary.items():
        print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
