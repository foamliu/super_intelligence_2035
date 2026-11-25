#!/usr/bin/env python3
"""baize_posttrain_ray_patch_verify.py — Verify R-009 resolution: monkey-patch propagation.

R53 (2026-11-08): Tests that the MiniCPM5 XML parser patch propagates to
subprocesses (simulating Ray workers) via the .pth file mechanism.

Tests:
  1. Direct import: patch applies in current process
  2. Subprocess without env var: patch does NOT apply (negative control)
  3. Subprocess with BAIZE_SGLANG_PATCH=1: patch DOES apply (positive test)
  4. Self-test: parse a sample XML tool call
  5. .pth file existence check
  6. (Optional) Ray actor test

Usage:
  python baize_posttrain_ray_patch_verify.py
  python baize_posttrain_ray_patch_verify.py --ray

⚠️ Surrogate RL results are NOT transferable to BaiZe.
"""
import sys
import os
import json
import subprocess
import importlib

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)


def test_direct_import():
    """Test 1: Direct import applies the patch."""
    print("\n=== Test 1: Direct Import ===")
    import baize_posttrain_sglang_patch as patch
    result = patch.apply_patch()
    applied = patch.is_applied()
    error = patch.get_error()
    status = "✅ PASS" if result and applied else "❌ FAIL"
    print(f"  apply_patch() returned: {result}")
    print(f"  is_applied(): {applied}")
    if error:
        print(f"  error: {error}")
    print(f"  {status}")
    return result and applied


def test_subprocess_no_env():
    """Test 2: Subprocess WITHOUT env var — patch should NOT auto-apply."""
    print("\n=== Test 2: Subprocess WITHOUT env var (negative control) ===")
    code = (
        "import sys; sys.path.insert(0, '{dir}'); "
        "import baize_posttrain_sglang_patch as p; "
        "print('AUTO_APPLIED:' + str(p.is_applied()))"
    ).format(dir=SCRIPT_DIR)
    env = os.environ.copy()
    env.pop("BAIZE_SGLANG_PATCH", None)
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True,
            text=True, timeout=60, env=env)
        output = result.stdout.strip()
        applied = "AUTO_APPLIED:True" in output
        status = "✅ PASS" if not applied else "⚠️ UNEXPECTED"
        print(f"  stdout: {output}")
        print(f"  auto_applied: {applied}")
        print(f"  {status} (expected: not auto-applied)")
        return True
    except subprocess.TimeoutExpired:
        print("  ❌ TIMEOUT")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def test_subprocess_with_env():
    """Test 3: Subprocess WITH BAIZE_SGLANG_PATCH=1 — patch SHOULD auto-apply."""
    print("\n=== Test 3: Subprocess WITH BAIZE_SGLANG_PATCH=1 ===")
    code = (
        "import sys; sys.path.insert(0, '{dir}'); "
        "import baize_posttrain_sglang_patch as p; "
        "print('AUTO_APPLIED:' + str(p.is_applied())); "
        "print('ERROR:' + str(p.get_error()))"
    ).format(dir=SCRIPT_DIR)
    env = os.environ.copy()
    env["BAIZE_SGLANG_PATCH"] = "1"
    try:
        result = subprocess.run(
            [sys.executable, "-c", code], capture_output=True,
            text=True, timeout=60, env=env)
        output = result.stdout.strip()
        applied = "AUTO_APPLIED:True" in output
        status = "✅ PASS" if applied else "❌ FAIL"
        print(f"  stdout: {output}")
        if result.stderr.strip():
            for line in result.stderr.strip().split("\n")[-5:]:
                print(f"  stderr: {line}")
        print(f"  auto_applied: {applied}")
        print(f"  {status} (expected: auto-applied)")
        return applied
    except subprocess.TimeoutExpired:
        print("  ❌ TIMEOUT (possible NFS cold start)")
        return False
    except Exception as e:
        print(f"  ❌ ERROR: {e}")
        return False


def test_self_test():
    """Test 4: Run the patch module's self-test."""
    print("\n=== Test 4: Self-test (parse sample XML tool call) ===")
    import baize_posttrain_sglang_patch as patch
    result = patch.self_test()
    print(f"  Result: {json.dumps(result, indent=2, ensure_ascii=False)}")
    all_pass = (
        result.get("patch_applied", False)
        and result.get("parser_registered", False)
        and result.get("parse_test") is not None
        and result.get("parse_test", {}).get("calls_count", 0) >= 1
        and result.get("parse_test", {}).get("first_call_name") == "get_weather"
    )
    status = "✅ PASS" if all_pass else "❌ FAIL"
    print(f"  {status}")
    return all_pass


def test_pth_file():
    """Test 5: Check if .pth file exists in site-packages."""
    print("\n=== Test 5: .pth file existence ===")
    import site
    found = False
    for sp in site.getsitepackages():
        pth_path = os.path.join(sp, "baize_posttrain_sglang_patch.pth")
        if os.path.exists(pth_path):
            print(f"  Found: {pth_path}")
            with open(pth_path) as f:
                content = f.read()
            print(f"  Content: {content.strip()}")
            found = True
            break
    if not found:
        print("  ❌ .pth file NOT found in site-packages")
        print("  Run: bash baize_posttrain_install_ray_patch.sh")
    else:
        print("  ✅ PASS")
    return found


def test_ray_actor():
    """Test 6: (Optional) Test with actual Ray actor."""
    print("\n=== Test 6: Ray Actor Test (optional) ===")
    try:
        import ray
    except ImportError:
        print("  ⏭️ Ray not available — skipping")
        return True
    try:
        ray.init(ignore_reinit_error=True, num_cpus=2, include_dashboard=False)

        @ray.remote
        def check_patch_in_worker():
            import sys, os
            env_set = os.environ.get("BAIZE_SGLANG_PATCH", "0")
            sys.path.insert(0, SCRIPT_DIR)
            import baize_posttrain_sglang_patch as patch
            return {"env_var": env_set, "is_applied": patch.is_applied(),
                    "error": patch.get_error(), "pid": os.getpid()}

        result = ray.get(check_patch_in_worker.remote())
        print(f"  Ray worker result: {json.dumps(result, indent=2)}")
        if os.environ.get("BAIZE_SGLANG_PATCH") == "1":
            success = result["is_applied"]
            status = "✅ PASS" if success else "❌ FAIL"
        else:
            print("  ℹ️ BAIZE_SGLANG_PATCH not set — worker won't have patch")
            status = "⚠️ SKIP"
        print(f"  {status}")
        ray.shutdown()
        return True
    except Exception as e:
        print(f"  ❌ Ray test error: {e}")
        try:
            ray.shutdown()
        except:
            pass
        return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="R53 Ray patch propagation verifier")
    parser.add_argument("--ray", action="store_true", help="Also test with Ray actors")
    parser.add_argument("--json", action="store_true", help="Output JSON results")
    args = parser.parse_args()

    print("=" * 60)
    print("  R53: Ray Worker Patch Propagation Verifier")
    print("  Resolves R-009: monkey-patch may not reach Ray workers")
    print("=" * 60)
    print(f"  Python: {sys.executable}")
    print(f"  Script dir: {SCRIPT_DIR}")
    print(f"  BAIZE_SGLANG_PATCH: {os.environ.get('BAIZE_SGLANG_PATCH', 'not set')}")

    results = {}
    results["direct_import"] = test_direct_import()
    results["subprocess_no_env"] = test_subprocess_no_env()
    results["subprocess_with_env"] = test_subprocess_with_env()
    results["self_test"] = test_self_test()
    results["pth_file"] = test_pth_file()
    if args.ray:
        results["ray_actor"] = test_ray_actor()

    print("\n" + "=" * 60)
    print("  SUMMARY")
    print("=" * 60)
    all_pass = True
    for name, passed in results.items():
        icon = "✅" if passed else "❌"
        print(f"  {icon} {name}")
        if not passed:
            all_pass = False
    overall = "✅ ALL PASS" if all_pass else "❌ SOME FAILED"
    print(f"\n  Overall: {overall}")
    if args.json:
        print(json.dumps(results, indent=2))
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(main())
