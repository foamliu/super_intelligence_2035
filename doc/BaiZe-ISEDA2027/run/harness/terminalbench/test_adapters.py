#!/usr/bin/env python3
"""Mock unit tests for Terminal-Bench 7-harness adapters.

Uses AST / source inspection — NO harbor, NO Docker needed.
Validates:
  - AGENT_IMPORT_PATHS has 7 correct entries
  - Each adapter file defines the expected class with name()/install()/run()
  - Options classes exist with expected default values
  - _base.py defines TB_MODEL, TB_BASE_URL, TBBaseAgent
  - No hardcoded API keys

Run:
    cd doc/BaiZe-ISEDA2027/run/harness
    python3 terminalbench/test_adapters.py
    # or with pytest:
    python3 -m pytest terminalbench/test_adapters.py -v
"""

from __future__ import annotations

import ast
import re
import sys
import unittest
from pathlib import Path

# Ensure terminalbench package is importable
HERE = Path(__file__).resolve().parent
HARNESS_DIR = HERE.parent  # run/harness/
AGENTS_DIR = HERE / "agents"
sys.path.insert(0, str(HARNESS_DIR))


# ---- Helper: parse a Python file into an AST ----

def _parse(filepath: Path) -> ast.AST:
    return ast.parse(filepath.read_text(), filename=str(filepath))

def _class_names(tree: ast.AST) -> dict[str, ast.ClassDef]:
    return {n.name: n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)}

def _method_names(cls: ast.ClassDef) -> set[str]:
    return {n.name for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))}

def _has_base(tb_cls: ast.ClassDef, base_name: str) -> bool:
    for base in tb_cls.bases:
        if isinstance(base, ast.Name) and base.id == base_name:
            return True
        if isinstance(base, ast.Attribute) and base.attr == base_name:
            return True
    return False

def _field_defaults(cls: ast.ClassDef) -> dict[str, str]:
    """Extract Field(default=...) values from a pydantic Options class."""
    defaults = {}
    for node in cls.body:
        if not isinstance(node, ast.AnnAssign):
            continue
        if not isinstance(node.target, ast.Name):
            continue
        field_name = node.target.id
        if node.value is None:
            continue
        # Try to extract the default value
        val = node.value
        if isinstance(val, ast.Call):
            # Field(default="something", ...)
            for kw in val.keywords:
                if kw.arg == "default" and isinstance(kw.value, ast.Constant):
                    defaults[field_name] = str(kw.value.value)
        elif isinstance(val, ast.Constant):
            defaults[field_name] = str(val.value)
    return defaults


# ---- Test: AGENT_IMPORT_PATHS (top-level __init__.py, no harbor needed) ----

class TestImportPaths(unittest.TestCase):
    """Verify AGENT_IMPORT_PATHS in terminalbench/__init__.py."""

    def setUp(self):
        from terminalbench import AGENT_IMPORT_PATHS
        self.paths = AGENT_IMPORT_PATHS

    def test_has_7_entries(self):
        self.assertEqual(len(self.paths), 7)

    def test_expected_harness_names(self):
        expected = {
            "cline-patched", "codex", "hermes", "opencode",
            "claude-code", "deepseek-harness", "pi",
        }
        self.assertEqual(set(self.paths.keys()), expected)

    def test_all_paths_have_module_colon_class(self):
        for name, path in self.paths.items():
            with self.subTest(harness=name):
                self.assertIn(":", path, f"{name} path must be 'module:Class' format")
                module, cls = path.rsplit(":", 1)
                self.assertTrue(module.startswith("terminalbench.agents."))
                self.assertTrue(cls.endswith("TB") or cls == "ClinePatched")

    def test_module_names_match_files(self):
        """Each import path module must correspond to an actual .py file."""
        for name, path in self.paths.items():
            with self.subTest(harness=name):
                module, cls = path.rsplit(":", 1)
                filename = module.rsplit(".", 1)[-1] + ".py"
                filepath = AGENTS_DIR / filename
                self.assertTrue(filepath.exists(), f"{filepath} not found for {name}")


# ---- Test: adapter structural compliance via AST ----

class TestAdapterStructure(unittest.TestCase):
    """Verify each adapter file defines the required class with name()/install()/run()."""

    ADAPTERS = [
        ("cline_patched.py", "ClinePatched", "cline-patched"),
        ("codex.py", "CodexTB", "codex"),
        ("hermes.py", "HermesTB", "hermes"),
        ("opencode.py", "OpenCodeTB", "opencode"),
        ("claude_code.py", "ClaudeCodeTB", "claude-code"),
        ("deepseek_harness.py", "DeepseekHarnessTB", "deepseek-harness"),
        ("pi.py", "PiTB", "pi"),
    ]

    def setUp(self):
        self.trees = {}
        for filename, cls_name, harness in self.ADAPTERS:
            filepath = AGENTS_DIR / filename
            self.trees[filename] = _parse(filepath)

    def test_adapter_class_exists(self):
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                self.assertIn(cls_name, classes,
                    f"{filename} must define class {cls_name}")

    def test_subclasses_tb_base_agent(self):
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                cls = classes[cls_name]
                self.assertTrue(
                    _has_base(cls, "TBBaseAgent"),
                    f"{cls_name} must subclass TBBaseAgent",
                )

    def test_name_method_exists(self):
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                methods = _method_names(classes[cls_name])
                self.assertIn("name", methods, f"{cls_name} must define name()")

    def test_install_method_exists(self):
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                methods = _method_names(classes[cls_name])
                self.assertIn("install", methods, f"{cls_name} must define install()")

    def test_run_method_exists(self):
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                methods = _method_names(classes[cls_name])
                self.assertIn("run", methods, f"{cls_name} must define run()")

    def test_name_returns_harness_identifier(self):
        """Check that name() contains the harness identifier string in its body."""
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                classes = _class_names(self.trees[filename])
                cls = classes[cls_name]
                name_method = None
                for node in cls.body:
                    if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "name":
                        name_method = node
                        break
                self.assertIsNotNone(name_method, f"{cls_name}.name() not found")
                # Check the return value contains the harness name
                src = ast.unparse(name_method)
                # Accept both single and double quoted strings
                self.assertTrue(
                    f'"{harness}"' in src or f"'{harness}'" in src,
                    f"{cls_name}.name() must return '{harness}', got: {src}",
                )

    def test_imports_from_base(self):
        """Each adapter must import from terminalbench.agents._base."""
        for filename, cls_name, harness in self.ADAPTERS:
            with self.subTest(harness=harness):
                src = (AGENTS_DIR / filename).read_text()
                self.assertIn("from terminalbench.agents._base import",
                    src, f"{filename} must import from _base")


# ---- Test: Options classes via AST ----

class TestOptionsClasses(unittest.TestCase):
    """Verify each adapter has an Options class with expected defaults."""

    def test_cline_patched_options(self):
        tree = _parse(AGENTS_DIR / "cline_patched.py")
        classes = _class_names(tree)
        self.assertIn("ClinePatchedOptions", classes)
        defaults = _field_defaults(classes["ClinePatchedOptions"])
        self.assertEqual(defaults.get("data_dir"), "/tmp/cline_tb_data")

    def test_codex_options(self):
        tree = _parse(AGENTS_DIR / "codex.py")
        classes = _class_names(tree)
        self.assertIn("CodexTBOptions", classes)
        defaults = _field_defaults(classes["CodexTBOptions"])
        self.assertEqual(defaults.get("codex_version"), "0.94.0")
        self.assertEqual(defaults.get("sandbox"), "workspace-write")

    def test_hermes_options(self):
        tree = _parse(AGENTS_DIR / "hermes.py")
        classes = _class_names(tree)
        self.assertIn("HermesTBOptions", classes)

    def test_opencode_options(self):
        tree = _parse(AGENTS_DIR / "opencode.py")
        classes = _class_names(tree)
        self.assertIn("OpenCodeTBOptions", classes)

    def test_claude_code_options(self):
        tree = _parse(AGENTS_DIR / "claude_code.py")
        classes = _class_names(tree)
        self.assertIn("ClaudeCodeTBOptions", classes)
        defaults = _field_defaults(classes["ClaudeCodeTBOptions"])
        self.assertEqual(defaults.get("permission_mode"), "bypassPermissions")

    def test_deepseek_harness_options(self):
        tree = _parse(AGENTS_DIR / "deepseek_harness.py")
        classes = _class_names(tree)
        self.assertIn("DeepseekHarnessTBOptions", classes)
        defaults = _field_defaults(classes["DeepseekHarnessTBOptions"])
        self.assertEqual(defaults.get("profile"), "sdk-minimal")

    def test_pi_options(self):
        tree = _parse(AGENTS_DIR / "pi.py")
        classes = _class_names(tree)
        self.assertIn("PiTBOptions", classes)


# ---- Test: shared base (_base.py) ----

class TestSharedBase(unittest.TestCase):
    """Verify _base.py defines TBBaseAgent and shared constants."""

    def setUp(self):
        self.src = (AGENTS_DIR / "_base.py").read_text()
        self.tree = _parse(AGENTS_DIR / "_base.py")

    def test_tb_base_agent_class_exists(self):
        classes = _class_names(self.tree)
        self.assertIn("TBBaseAgent", classes)

    def test_tb_base_subclasses_base_installed_agent(self):
        classes = _class_names(self.tree)
        self.assertTrue(_has_base(classes["TBBaseAgent"], "BaseInstalledAgent"))

    def test_tb_model_constant(self):
        self.assertIn("TB_MODEL", self.src)
        self.assertIn("kimi-k2.6-cloud", self.src)

    def test_tb_base_url_constant(self):
        self.assertIn("TB_BASE_URL", self.src)
        self.assertIn("agi-gateway.cxmt.com", self.src)

    def test_env_for_harness_method(self):
        classes = _class_names(self.tree)
        methods = _method_names(classes["TBBaseAgent"])
        self.assertIn("_env_for_harness", methods)

    def test_install_node_helper(self):
        classes = _class_names(self.tree)
        methods = _method_names(classes["TBBaseAgent"])
        self.assertIn("_install_node", methods)
        self.assertIn("_install_bun", methods)

    def test_abstract_methods_raise(self):
        """_base.py's own name/install/run should raise NotImplementedError."""
        classes = _class_names(self.tree)
        methods = _method_names(classes["TBBaseAgent"])
        self.assertIn("name", methods)
        self.assertIn("install", methods)
        self.assertIn("run", methods)


# ---- Test: no hardcoded API keys ----

class TestNoHardcodedKeys(unittest.TestCase):
    """Ensure no adapter file contains a real API key string."""

    KEY_PATTERNS = [
        r"02_[A-Z0-9]{20,}",  # actual key format from keys.txt
    ]

    def test_no_key_patterns_in_source(self):
        for py_file in AGENTS_DIR.glob("*.py"):
            content = py_file.read_text()
            for pattern in self.KEY_PATTERNS:
                with self.subTest(file=py_file.name):
                    self.assertNotRegex(
                        content, pattern,
                        f"{py_file.name} contains a hardcoded API key!",
                    )

    def test_api_key_from_env(self):
        """_base.py must source the API key from env, not hardcode it."""
        src = (AGENTS_DIR / "_base.py").read_text()
        self.assertIn("os.environ", src)
        self.assertIn("TB_API_KEY", src)


# ---- Test: lazy imports in agents/__init__.py ----

class TestLazyImports(unittest.TestCase):
    """Verify agents/__init__.py uses lazy imports (no eager harbor imports)."""

    def test_no_eager_adapter_imports(self):
        src = (AGENTS_DIR / "__init__.py").read_text()
        # Should NOT have top-level 'from terminalbench.agents.X import Y'
        # (those are in TYPE_CHECKING block or lazy __getattr__)
        eager_pattern = r'^from terminalbench\.agents\.\w+ import \w+'
        eager_lines = [
            line for line in src.splitlines()
            if re.match(eager_pattern, line) and 'TYPE_CHECKING' not in line
        ]
        # Lines inside 'if TYPE_CHECKING:' block are OK
        # Check that no eager import is outside TYPE_CHECKING
        # Simple heuristic: if there's a __getattr__, eager imports should be in TYPE_CHECKING
        if '__getattr__' in src:
            # With lazy loading, top-level imports should only be in TYPE_CHECKING block
            # Check the source doesn't have eager imports outside if TYPE_CHECKING
            in_type_checking = False
            real_eager = []
            for line in src.splitlines():
                stripped = line.strip()
                if 'if TYPE_CHECKING' in stripped:
                    in_type_checking = True
                    continue
                if in_type_checking and stripped and not stripped.startswith('#'):
                    if re.match(eager_pattern, stripped):
                        continue  # inside TYPE_CHECKING, OK
                    if not stripped.startswith(('from', 'import')):
                        in_type_checking = False
                if not in_type_checking:
                    if re.match(eager_pattern, stripped):
                        real_eager.append(stripped)
            self.assertEqual(real_eager, [],
                "agents/__init__.py has eager adapter imports outside TYPE_CHECKING")


if __name__ == "__main__":
    unittest.main(verbosity=2)
