#!/usr/bin/env python3
"""baize_posttrain_eda_tool_v3.py — Unified EDA Tool Suite for verl 0.4.0.

R123 (2026-11-10): Integrates R122 LocalAPISearch into the EDA tool pipeline.
Provides 4 tool classes matching the real EDA harness MCP tools:

  1. EDASearchAPIsTool       — search_apis (BM25 keyword search over 8463 APIs)
  2. EDAGetAPIDetailsTool    — get_api_details (direct lookup by API name)
  3. EDASearchByKeywordTool  — search_apis_by_keyword (camelCase + BM25 hybrid)
  4. EDARunCodeTool          — run_code (static analysis; sandbox when available)

All 4 classes match verl 0.4.0 BaseTool API contract:
  __init__(config, tool_schema) -> create() -> execute() -> calc_reward() -> release()

A singleton LocalAPISearch instance is shared across search tools (loaded once,
~0.8s for 8463 APIs / 17.3MB).  run_code uses tier-3 static analysis (no sandbox
required, suitable for zero-GPU dry-run and R0++ reward computation).

Surrogate RL results are NOT transferable to BaiZe.
"""
from __future__ import annotations
import asyncio, json, logging, time, os, sys
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

logger = logging.getLogger(__name__)

# -- verl import (with stub fallback for standalone dry-run) --
try:
    from verl.tools.base_tool import BaseTool
    from verl.tools.schemas import OpenAIFunctionToolSchema
    HAS_VERL = True
except ImportError:
    HAS_VERL = False
    class OpenAIFunctionToolSchema:
        @classmethod
        def model_validate(cls, d):
            return d
    class BaseTool:
        def __init__(self, config, tool_schema):
            self.config = config
            self.name = "stub"
            self.tool_schema = tool_schema

# -- LocalAPISearch import (R122) --
_SEARCHER: Optional[Any] = None  # singleton

def _get_searcher() -> Any:
    """Lazily load singleton LocalAPISearch instance."""
    global _SEARCHER
    if _SEARCHER is not None:
        return _SEARCHER
    _here = os.path.dirname(os.path.abspath(__file__))
    if _here not in sys.path:
        sys.path.insert(0, _here)
    from baize_posttrain_r122_local_api_search import LocalAPISearch
    api_info_path = os.environ.get(
        "BAIZE_API_INFO_PATH",
        os.path.expanduser("~/code/eda_fastmcp/docs/API_INFO_MERGED_V3.json"))
    _SEARCHER = LocalAPISearch(api_info_path=api_info_path)
    logger.info("LocalAPISearch singleton loaded: %s APIs from %s",
                _SEARCHER.stats().get("total_apis", "?"), api_info_path)
    return _SEARCHER


# =============================================================================
#  1. EDASearchAPIsTool -- search_apis
# =============================================================================
class EDASearchAPIsTool(BaseTool):
    """Search EDA APIs by natural-language query (BM25 keyword search).

    Replaces MCP search_apis. Returns top-k matching APIs with similarity
    scores, api_name, short description, and category.
    """

    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self.default_top_k = config.get("search_top_k", 5)
        self.default_threshold = config.get("search_similarity_threshold", 0.1)
        self._instance_dict: Dict[str, Dict[str, Any]] = {}

    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "call_count": 0, "last_query": "", "last_results": []}
        return instance_id

    async def execute(self, instance_id: str, parameters: dict[str, Any],
                      **kwargs) -> Tuple[str, float, dict]:
        query = parameters.get("query", "")
        top_k = parameters.get("top_k", self.default_top_k)
        threshold = parameters.get("similarity_threshold", self.default_threshold)
        lang = parameters.get("lang", "pyAether")

        if not query:
            return (json.dumps({"error": "query is required"}), 0.0,
                    {"error": "missing_query"})

        if instance_id in self._instance_dict:
            self._instance_dict[instance_id]["call_count"] += 1
            self._instance_dict[instance_id]["last_query"] = query

        start = time.time()
        try:
            searcher = _get_searcher()
            results = searcher.search_apis(
                query, top_k=top_k, similarity_threshold=threshold, lang=lang)
            elapsed = round(time.time() - start, 4)
            if instance_id in self._instance_dict:
                self._instance_dict[instance_id]["last_results"] = results
            return (json.dumps({"results": results, "count": len(results)},
                               ensure_ascii=False), 0.0,
                    {"elapsed_s": elapsed, "query": query, "tool": "search_apis"})
        except Exception as e:
            return (json.dumps({"error": str(e)}), 0.0, {"error": str(e)})

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        return 0.0  # search tools are informational, no direct reward

    async def release(self, instance_id: str, **kwargs) -> None:
        self._instance_dict.pop(instance_id, None)


# =============================================================================
#  2. EDAGetAPIDetailsTool -- get_api_details
# =============================================================================
class EDAGetAPIDetailsTool(BaseTool):
    """Get full API documentation by API name(s).

    Replaces MCP get_api_details. Returns full api_info entries for the
    requested API names, including parameters, return type, description.
    """

    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self._instance_dict: Dict[str, Dict[str, Any]] = {}

    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {"call_count": 0}
        return instance_id

    async def execute(self, instance_id: str, parameters: dict[str, Any],
                      **kwargs) -> Tuple[str, float, dict]:
        api_list = parameters.get("api_list", parameters.get("api_names", []))
        lang = parameters.get("lang", "pyAether")

        if not api_list:
            return (json.dumps({"error": "api_list is required"}), 0.0,
                    {"error": "missing_api_list"})
        if isinstance(api_list, str):
            api_list = [api_list]

        if instance_id in self._instance_dict:
            self._instance_dict[instance_id]["call_count"] += 1

        start = time.time()
        try:
            searcher = _get_searcher()
            results = searcher.get_api_details(api_list, lang=lang)
            elapsed = round(time.time() - start, 4)
            found = sum(1 for r in results if r.get("found", False))
            return (json.dumps({"results": results, "count": len(results),
                                "found": found}, ensure_ascii=False), 0.0,
                    {"elapsed_s": elapsed, "tool": "get_api_details"})
        except Exception as e:
            return (json.dumps({"error": str(e)}), 0.0, {"error": str(e)})

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        return 0.0

    async def release(self, instance_id: str, **kwargs) -> None:
        self._instance_dict.pop(instance_id, None)


# =============================================================================
#  3. EDASearchByKeywordTool -- search_apis_by_keyword
# =============================================================================
class EDASearchByKeywordTool(BaseTool):
    """Search EDA APIs by keyword (camelCase token + BM25 hybrid).

    Replaces MCP search_apis_by_keyword. Better for partial name matching
    (e.g. "CV" -> APIs containing "CV" in their name).
    """

    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self.default_top_k = config.get("keyword_top_k", 5)
        self._instance_dict: Dict[str, Dict[str, Any]] = {}

    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {"call_count": 0}
        return instance_id

    async def execute(self, instance_id: str, parameters: dict[str, Any],
                      **kwargs) -> Tuple[str, float, dict]:
        query = parameters.get("query", parameters.get("keyword", ""))
        top_k = parameters.get("top_k", self.default_top_k)
        lang = parameters.get("lang", "pyAether")

        if not query:
            return (json.dumps({"error": "query is required"}), 0.0,
                    {"error": "missing_query"})

        if instance_id in self._instance_dict:
            self._instance_dict[instance_id]["call_count"] += 1

        start = time.time()
        try:
            searcher = _get_searcher()
            results = searcher.search_apis_by_keyword(
                query, top_k=top_k, lang=lang)
            elapsed = round(time.time() - start, 4)
            return (json.dumps({"results": results, "count": len(results)},
                               ensure_ascii=False), 0.0,
                    {"elapsed_s": elapsed, "tool": "search_apis_by_keyword"})
        except Exception as e:
            return (json.dumps({"error": str(e)}), 0.0, {"error": str(e)})

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        return 0.0

    async def release(self, instance_id: str, **kwargs) -> None:
        self._instance_dict.pop(instance_id, None)


# =============================================================================
#  4. EDARunCodeTool -- run_code (static analysis / sandbox)
# =============================================================================
class EDARunCodeTool(BaseTool):
    """Execute Python code in the EDA environment.

    Tier 3 (no sandbox): static analysis only (syntax check + AST-based
    API call extraction for R0++ reward computation).
    Tier 1/2 (with sandbox): would forward to remote sandbox -- not available
    on .17 (R121 finding: all sandbox ports FILTERED).
    """

    def __init__(self, config: dict, tool_schema: OpenAIFunctionToolSchema):
        super().__init__(config, tool_schema)
        self.tier = config.get("tier", 3)
        self.max_code_length = config.get("max_code_length", 5000)
        self.timeout = config.get("timeout", 60)
        self.sandbox_endpoint = config.get("sandbox_endpoint", "tier3_static")
        self._instance_dict: Dict[str, Dict[str, Any]] = {}

    async def create(self, instance_id: Optional[str] = None, **kwargs) -> str:
        if instance_id is None:
            instance_id = str(uuid4())
        self._instance_dict[instance_id] = {
            "response": "", "reward": 0.0, "tool_call_count": 0,
            "syntax_ok": False, "apis_called": []}
        return instance_id

    async def execute(self, instance_id: str, parameters: dict[str, Any],
                      **kwargs) -> Tuple[str, float, dict]:
        code = parameters.get("code", "")
        if not code:
            return (json.dumps({"error": "code is required"}), 0.0,
                    {"error": "missing_code"})
        if len(code) > self.max_code_length:
            return (json.dumps({"error": "Code too long"}), 0.0,
                    {"error": "code_too_long"})

        if instance_id in self._instance_dict:
            self._instance_dict[instance_id]["tool_call_count"] += 1

        start = time.time()
        try:
            if self.tier == 3:
                result = self._static_analysis(code)
            elif self.tier in (1, 2):
                result = {"response": "[sandbox not available]",
                          "error_log": "Sandbox ports FILTERED (R121)",
                          "print_log": "", "result": None}
            else:
                result = {"error": f"Unknown tier: {self.tier}"}

            elapsed = round(time.time() - start, 4)
            if instance_id in self._instance_dict:
                self._instance_dict[instance_id]["syntax_ok"] = result.get(
                    "syntax_ok", False)
                self._instance_dict[instance_id]["apis_called"] = result.get(
                    "apis_called", [])
            return (json.dumps(result, ensure_ascii=False), 0.0,
                    {"elapsed_s": elapsed, "tier": self.tier,
                     "tool": "run_code"})
        except Exception as e:
            return (json.dumps({"error": str(e)}), 0.0, {"error": str(e)})

    @staticmethod
    def _extract_dotted_path(node: Any) -> str:
        """R124 FIX: Reconstruct full dotted path from AST call node.

        For ``pyScript.emyDesign.setCp()`` the AST is:
            Call(func=Attribute(attr='setCp',
                 value=Attribute(attr='emyDesign',
                 value=Name(id='pyScript'))))

        This method walks the chain and returns ``emyDesign.setCp`` (stripping
        the pyScript / pyAether root).  For a bare ``print()`` call it returns
        ``print``.  For ``pyScript.aeGetCurDesign()`` it returns
        ``aeGetCurDesign``.
        """
        import ast as _ast
        parts: List[str] = []
        cur = node
        while isinstance(cur, _ast.Attribute):
            parts.append(cur.attr)
            cur = cur.value
        if isinstance(cur, _ast.Name):
            parts.append(cur.id)
        parts.reverse()
        # Strip the pyScript / pyAether root (first element)
        if len(parts) >= 2 and parts[0] in ("pyScript", "pyAether", "py"):
            parts = parts[1:]
        return ".".join(parts)

    def _static_analysis(self, code: str) -> dict:
        """Tier-3 static analysis: syntax check + AST API call extraction.

        This is the R0++ reward input: extracts function calls that look like
        pyAether API calls (camelCase names matching KB entries).

        R124 FIX: Now reconstructs dotted paths (``emyDesign.setCp``) so that
        ``api_legality`` is computed correctly against the KB which stores
        names as ``class.method``.
        """
        result = {"response": "", "error_log": "", "print_log": "",
                  "result": None, "syntax_ok": False, "apis_called": []}
        try:
            compile(code, "<sandbox>", "exec")
            result["syntax_ok"] = True
            result["response"] = "[static] Syntax OK"
        except SyntaxError as e:
            result["error_log"] = f"SyntaxError: {e}"
            result["response"] = f"[static] SyntaxError at line {e.lineno}: {e.msg}"
            return result

        # AST-based API call extraction (for R0++ call_verified dimension)
        try:
            import ast
            tree = ast.parse(code)
            api_names: List[str] = []
            api_short_names: List[str] = []  # short (last-segment) names
            for node in ast.walk(tree):
                if isinstance(node, ast.Call):
                    func = node.func
                    if isinstance(func, ast.Name):
                        # Bare function call: print(), len(), etc.
                        api_names.append(func.id)
                        api_short_names.append(func.id)
                    elif isinstance(func, ast.Attribute):
                        dotted = self._extract_dotted_path(func)
                        api_names.append(dotted)
                        api_short_names.append(func.attr)
            # Verify against API KB if available
            # R124 FIX: try both the dotted name AND the short name
            verified_apis: List[str] = []
            try:
                searcher = _get_searcher()
                for dotted, short in zip(api_names, api_short_names):
                    found = False
                    # Try dotted name first (e.g. "emyDesign.setCp")
                    details = searcher.get_api_details([dotted])
                    if details and details[0].get("api_type", "unknown") != "unknown":
                        verified_apis.append(dotted)
                        found = True
                    if not found and dotted != short:
                        # Fall back to short name (e.g. "aeGetCurDesign")
                        details = searcher.get_api_details([short])
                        if details and details[0].get("api_type", "unknown") != "unknown":
                            verified_apis.append(short)
                            found = True
            except Exception:
                pass  # KB not available, just return raw names
            result["apis_called"] = api_names
            result["apis_verified"] = verified_apis
            result["api_legality"] = (
                len(verified_apis) / len(api_names) if api_names else 1.0)
        except Exception as e:
            result["error_log"] = f"AST analysis error: {e}"

        return result

    async def calc_reward(self, instance_id: str, **kwargs) -> float:
        return self._instance_dict.get(instance_id, {}).get("reward", 0.0)

    async def release(self, instance_id: str, **kwargs) -> None:
        self._instance_dict.pop(instance_id, None)


# =============================================================================
#  End-to-end dry-run validation
# =============================================================================
async def _e2e_dry_run():
    """Simulate a full RL rollout tool-call sequence:
    search_apis -> get_api_details -> run_code (static) -> search_apis_by_keyword
    """
    print("=" * 70)
    print("R123 EDA Tool V3 -- End-to-End Dry-Run Validation")
    print("=" * 70)

    # -- 1. Initialize all 4 tools --
    print("\n[1] Initializing 4 EDA tools...")
    schemas = {
        "search_apis": {"type": "function", "function": {
            "name": "search_apis",
            "description": "Search EDA APIs by natural-language query",
            "parameters": {"type": "object", "properties": {
                "query": {"type": "string"},
                "top_k": {"type": "integer", "default": 5}},
                "required": ["query"]}}},
        "get_api_details": {"type": "function", "function": {
            "name": "get_api_details",
            "description": "Get full API documentation by name(s)",
            "parameters": {"type": "object", "properties": {
                "api_list": {"type": "array", "items": {"type": "string"}}},
                "required": ["api_list"]}}},
        "search_apis_by_keyword": {"type": "function", "function": {
            "name": "search_apis_by_keyword",
            "description": "Search APIs by keyword (camelCase + BM25)",
            "parameters": {"type": "object", "properties": {
                "query": {"type": "string"}},
                "required": ["query"]}}},
        "run_code": {"type": "function", "function": {
            "name": "run_code",
            "description": "Execute Python code in EDA environment",
            "parameters": {"type": "object", "properties": {
                "code": {"type": "string"}},
                "required": ["code"]}}},
    }
    tool_classes = {
        "search_apis": EDASearchAPIsTool,
        "get_api_details": EDAGetAPIDetailsTool,
        "search_apis_by_keyword": EDASearchByKeywordTool,
        "run_code": EDARunCodeTool,
    }
    tools = {}
    for name, cls in tool_classes.items():
        schema = (OpenAIFunctionToolSchema.model_validate(schemas[name])
                  if HAS_VERL else schemas[name])
        tools[name] = cls({"tier": 3, "timeout": 30}, schema)
        print(f"  OK {name}: {cls.__name__}")

    # -- 2. Step 1: search_apis --
    print("\n[2] Step 1: search_apis('get current design')")
    iid1 = await tools["search_apis"].create(instance_id="rollout-001")
    resp1, rew1, meta1 = await tools["search_apis"].execute(
        iid1, {"query": "get current design", "top_k": 3})
    data1 = json.loads(resp1)
    print(f"  create() -> {iid1} (type={type(iid1).__name__})")
    print(f"  execute() -> {data1['count']} results, elapsed={meta1['elapsed_s']}s")
    for r in data1.get("results", [])[:3]:
        print(f"    - {r.get('api_name', '?')}: {r.get('short_desc', '')[:60]}")

    # -- 3. Step 2: get_api_details --
    top_api = data1["results"][0]["api_name"] if data1["results"] else "aeGetCurDesign"
    print(f"\n[3] Step 2: get_api_details(['{top_api}'])")
    iid2 = await tools["get_api_details"].create(instance_id="rollout-002")
    resp2, rew2, meta2 = await tools["get_api_details"].execute(
        iid2, {"api_list": [top_api]})
    data2 = json.loads(resp2)
    print(f"  found={data2.get('found', 0)}/{data2.get('count', 0)}, "
          f"elapsed={meta2['elapsed_s']}s")
    if data2["results"]:
        d = data2["results"][0]
        print(f"    name: {d.get('api_name', '?')}")
        print(f"    type: {d.get('api_type', '?')}")
        print(f"    desc: {str(d.get('api_description', ''))[:80]}")

    # -- 4. Step 3: run_code (static analysis) --
    print(f"\n[4] Step 3: run_code(static analysis of code using {top_api})")
    test_code = (
        f"import pyAether as pyScript\n"
        f"design = pyScript.{top_api}()\n"
        f"print(f'Current design: {{design}}')\n")
    iid3 = await tools["run_code"].create(instance_id="rollout-003")
    resp3, rew3, meta3 = await tools["run_code"].execute(iid3, {"code": test_code})
    data3 = json.loads(resp3)
    print(f"  syntax_ok={data3.get('syntax_ok', False)}, "
          f"elapsed={meta3['elapsed_s']}s")
    print(f"  apis_called={data3.get('apis_called', [])}")
    print(f"  apis_verified={data3.get('apis_verified', [])}")
    print(f"  api_legality={data3.get('api_legality', 0):.2f}")

    # -- 5. Step 4: search_apis_by_keyword --
    print(f"\n[5] Step 4: search_apis_by_keyword('CV')")
    iid4 = await tools["search_apis_by_keyword"].create(instance_id="rollout-004")
    resp4, rew4, meta4 = await tools["search_apis_by_keyword"].execute(
        iid4, {"query": "CV"})
    data4 = json.loads(resp4)
    print(f"  {data4['count']} results, elapsed={meta4['elapsed_s']}s")
    for r in data4.get("results", [])[:3]:
        print(f"    - {r.get('api_name', '?')}: {r.get('short_desc', '')[:60]}")

    # -- 6. Step 5: run_code with syntax error --
    print(f"\n[6] Step 5: run_code(syntax error test)")
    bad_code = "def foo(\n  # missing close paren"
    iid5 = await tools["run_code"].create(instance_id="rollout-005")
    resp5, rew5, meta5 = await tools["run_code"].execute(iid5, {"code": bad_code})
    data5 = json.loads(resp5)
    print(f"  syntax_ok={data5.get('syntax_ok', False)}")
    print(f"  error_log={data5.get('error_log', '')[:80]}")

    # -- 7. Release all --
    print(f"\n[7] Releasing all tool instances...")
    for name, tool in tools.items():
        for iid in [iid1, iid2, iid3, iid4, iid5]:
            try:
                await tool.release(iid)
            except Exception:
                pass
    print("  OK All released")

    # -- Summary --
    print("\n" + "=" * 70)
    print("DRY-RUN SUMMARY")
    print("=" * 70)
    checks = [
        ("search_apis returned results", data1["count"] > 0),
        ("get_api_details returned results", data2.get("count", 0) > 0),
        ("run_code syntax check passed", data3.get("syntax_ok", False)),
        ("run_code API extraction worked", len(data3.get("apis_called", [])) > 0),
        ("search_apis_by_keyword returned results", data4["count"] > 0),
        ("run_code syntax error detected", not data5.get("syntax_ok", True)),
        ("All execute() return type=str", all(
            isinstance(r, str) for r in [resp1, resp2, resp3, resp4, resp5])),
        ("All create() return type=str", all(
            isinstance(r, str) for r in [iid1, iid2, iid3, iid4, iid5])),
    ]
    passed = sum(1 for _, ok in checks if ok)
    for label, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'} {label}")
    print(f"\n  {passed}/{len(checks)} checks passed")
    if passed == len(checks):
        print("  ALL CHECKS PASSED -- EDA Tool V3 ready for verl integration")
    else:
        print("  WARNING: Some checks failed -- review above")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(_e2e_dry_run())
